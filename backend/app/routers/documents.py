"""Document upload, listing, status and deletion.

Scoped entirely by the `X-Browser-UUID` request header -- there is no login,
so that header is the only tenant identity the API has. It is never read
from the request body.
"""

import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentListItem, DocumentStatusResponse, DocumentUploadResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Maps a lower-cased file extension to its short type code and the set of
# content types the browser is allowed to declare for it. Both must agree:
# neither the extension nor the declared content type is trusted alone.
_ALLOWED_TYPES: dict[str, tuple[str, set[str]]] = {
    ".pdf": ("pdf", {"application/pdf"}),
    ".txt": ("txt", {"text/plain"}),
    ".docx": (
        "docx",
        {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ),
}

_UNSUPPORTED_TYPE_DETAIL = "Only PDF, TXT, and DOCX files are supported."


def _require_browser_uuid(x_browser_uuid: str | None = Header(default=None)) -> str:
    """Every route here is scoped by this header; reject anything without one."""
    if not x_browser_uuid or not x_browser_uuid.strip():
        raise HTTPException(status_code=400, detail="X-Browser-UUID header is required.")
    return x_browser_uuid.strip()


_minio_client = None


def get_minio_client():
    """Lazily built MinIO client, cached across requests.

    A module-level function rather than a constant so tests can monkeypatch
    it with a fake and never touch a real object store or its credentials.
    """
    global _minio_client
    if _minio_client is None:
        from minio import Minio

        _minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )
    return _minio_client


def _bucket_name() -> str:
    return os.getenv("MINIO_BUCKET", "documents")


def _ensure_bucket(client) -> None:
    bucket = _bucket_name()
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def _validate_file_type(filename: str, content_type: str | None) -> str:
    """Returns the short type code, or raises 400 for any unsupported file."""
    _, ext = os.path.splitext(filename or "")
    ext = ext.lower()
    match = _ALLOWED_TYPES.get(ext)
    if match is None:
        raise HTTPException(status_code=400, detail=_UNSUPPORTED_TYPE_DETAIL)
    file_type, allowed_content_types = match
    if content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail=_UNSUPPORTED_TYPE_DETAIL)
    return file_type


def _get_owned_document(db: Session, document_id: str, browser_uuid: str) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.browser_uuid != browser_uuid:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),  # noqa: B008
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentUploadResponse:
    file_type = _validate_file_type(file.filename or "", file.content_type)
    contents = await file.read()

    document_id = str(uuid.uuid4())
    object_key = f"{browser_uuid}/{document_id}.{file_type}"

    client = get_minio_client()
    _ensure_bucket(client)
    client.put_object(
        _bucket_name(),
        object_key,
        BytesIO(contents),
        length=len(contents),
        content_type=file.content_type,
    )

    document = Document(
        id=document_id,
        browser_uuid=browser_uuid,
        filename=file.filename or "",
        file_type=file_type,
        file_size_bytes=len(contents),
        minio_object_key=object_key,
        status="pending",
    )
    db.add(document)
    db.commit()

    return DocumentUploadResponse(document_id=document.id, status=document.status)


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[DocumentListItem]:
    documents = db.scalars(
        select(Document)
        .where(Document.browser_uuid == browser_uuid)
        .order_by(Document.created_at.desc())
    ).all()
    return [
        DocumentListItem(
            document_id=d.id,
            filename=d.filename,
            status=d.status,
            created_at=d.created_at,
        )
        for d in documents
    ]


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentStatusResponse:
    document = _get_owned_document(db, document_id, browser_uuid)
    return DocumentStatusResponse(
        document_id=document.id,
        status=document.status,
        chunk_count=document.chunk_count,
    )


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    document = _get_owned_document(db, document_id, browser_uuid)

    client = get_minio_client()
    try:
        client.remove_object(_bucket_name(), document.minio_object_key)
    except Exception:
        # The DB row is the source of truth for the API; a storage object
        # that is already gone (or a store that is briefly unreachable)
        # should not stop the user from clearing it out of their list.
        pass

    db.delete(document)
    db.commit()
    return None
