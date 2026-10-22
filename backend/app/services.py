"""The backing services this application is configured to reach.

Each entry maps a service to the environment variable that addresses it. The value
comes from docker-compose.yml through .env.example, so the health check reports
what the running deployment can actually reach.
"""

import os
from datetime import UTC, datetime

from minio import Minio
from sqlalchemy.orm import Session

from app.models import Document
from app.text_extraction import extract_text

SERVICES = {
    "minio": "MINIO_ENDPOINT",
}


def configured_services() -> dict[str, bool]:
    """Each service mapped to whether its connection variable is set."""
    return {name: bool(os.getenv(var)) for name, var in SERVICES.items()}


def minio_client() -> Minio:
    """A client for the MinIO deployment named in the environment.

    A FastAPI dependency rather than a module-level singleton, so tests can
    override it with a fake and never touch a real object store.
    """
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", ""),
        secret_key=os.getenv("MINIO_SECRET_KEY", ""),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )


def minio_bucket() -> str:
    """The bucket uploaded documents are stored in."""
    return os.getenv("MINIO_BUCKET", "documents")


def process_document(db: Session, document: Document, data: bytes) -> None:
    """Extracts text from an uploaded file and records the outcome on `document`.

    Moves the row from pending to processing to a terminal status: processed
    with the extracted text persisted, or failed with an error message when
    extraction could not read the file. Runs synchronously, right after a
    successful upload -- there is no background job runner in this service yet.
    """
    document.status = "processing"
    db.commit()

    text = extract_text(data, document.file_type)

    if text is None:
        document.status = "failed"
        document.error_message = "Could not extract text from the uploaded file."
    else:
        document.extracted_text = text
        document.status = "processed"
        document.error_message = None

    document.last_activity_at = datetime.now(UTC)
    db.commit()
    db.refresh(document)
