"""Pydantic request and response models.

One pair per entity in the approved data model, plus the placeholder every
generated route returns until it has been implemented.
"""

from datetime import datetime

from pydantic import BaseModel


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

    document_id: str
    status: str


class DocumentListItem(BaseModel):
    """One row of GET /api/documents."""

    document_id: str
    filename: str
    status: str
    created_at: datetime


class DocumentStatusResponse(BaseModel):
    """What GET /api/documents/{document_id}/status returns."""

    document_id: str
    status: str
    chunk_count: int | None = None
