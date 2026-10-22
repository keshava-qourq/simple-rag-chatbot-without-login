"""POST /api/documents and GET /api/documents.

Uploads are scoped by the `X-Browser-UUID` header rather than any login --
this application has no accounts, so that header is the only tenant
boundary (NFR-002). Only PDF, TXT and DOCX are accepted; text extraction,
embeddings, chat and delete are out of scope here.
"""

import io
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from minio import Minio
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentOut, DocumentUploadResponse
from app.services import minio_bucket, minio_client

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Extension -> the single content type we accept for it. Checking both the
# declared content type and the extension means a file renamed to look like
# one of these (e.g. malware.exe -> malware.pdf) is still rejected, because
# its content type will not match.
_ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_UNSUPPORTED_FORMAT_DETAIL = "Only PDF, TXT and DOCX files are supported."


def _require_browser_uuid(
    x_browser_uuid: str | None = Header(default=None, alias="X-Browser-UUID"),
) -> str:
    """400, not FastAPI's default 422, when the tenant header is missing."""
    if not x_browser_uuid:
        raise HTTPException(status_code=400, detail="X-Browser-UUID header is required.")
    return x_browser_uuid


def _ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),  # noqa: B008 -- FastAPI's documented pattern
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    client: Minio = Depends(minio_client),  # noqa: B008
) -> DocumentUploadResponse:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    content_type = file.content_type or ""

    if extension not in _ALLOWED_TYPES or content_type != _ALLOWED_TYPES[extension]:
        raise HTTPException(status_code=400, detail=_UNSUPPORTED_FORMAT_DETAIL)

    data = await file.read()
    size = len(data)
    document_id = str(uuid.uuid4())
    bucket = minio_bucket()
    storage_key = f"{browser_uuid}/{document_id}{extension}"

    _ensure_bucket(client, bucket)
    client.put_object(
        bucket,
        storage_key,
        io.BytesIO(data),
        length=size,
        content_type=content_type,
    )

    now = datetime.now(UTC)
    document = Document(
        id=document_id,
        browser_uuid=browser_uuid,
        filename=filename,
        file_type=extension.lstrip("."),
        file_size_bytes=size,
        minio_object_key=storage_key,
        status="pending",
        chunk_count=None,
        created_at=now,
        last_activity_at=now,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return DocumentUploadResponse(
        id=document.id, filename=document.filename, status=document.status
    )


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    browser_uuid: str = Depends(_require_browser_uuid),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.browser_uuid == browser_uuid)
        .order_by(Document.created_at.desc())
        .all()
    )
