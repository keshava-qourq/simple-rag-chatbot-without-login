"""Pydantic request and response models.

One pair per entity in the approved data model, plus the placeholder every
generated route returns until it has been implemented.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StubResponse(BaseModel):
    """What a generated route returns until someone implements it.

    A stub that returns a typed body rather than raising keeps the service
    startable and its OpenAPI document complete, so the frontend can be built
    against the agreed shape while the handlers are still being written.
    """

    endpoint: str
    status: str = "not_implemented"
    detail: str = "Scaffolded from the approved API spec; no behaviour yet."


class DocumentUploadResponse(BaseModel):
    """What POST /api/documents returns once the file has been stored."""

    id: str
    filename: str
    status: str


class DocumentOut(BaseModel):
    """A document row as returned by GET /api/documents."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    browser_uuid: str
    filename: str
    file_type: str
    file_size_bytes: int
    minio_object_key: str
    status: str
    chunk_count: int | None = None
    created_at: datetime
    last_activity_at: datetime


class DocumentStatusOut(BaseModel):
    """What GET /api/documents/{document_id}/status returns."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    error: str | None = None
