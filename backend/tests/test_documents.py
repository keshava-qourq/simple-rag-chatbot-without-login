"""Unit and integration tests for the document upload API."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.routers import documents as documents_router

# An isolated in-memory database per test run, independent of whatever is on
# disk at backend/app.db -- a single shared connection so every session (the
# request's and the test's) sees the same tables.
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(bind=_engine)


def _override_get_db() -> Iterator:
    session = _TestSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = _override_get_db


class _FakeMinioClient:
    """Stands in for MinIO so tests never touch a real object store."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.buckets: set[str] = set()

    def bucket_exists(self, bucket: str) -> bool:
        return bucket in self.buckets

    def make_bucket(self, bucket: str) -> None:
        self.buckets.add(bucket)

    def put_object(self, bucket, key, data, length, content_type=None) -> None:
        self.objects[key] = data.read()

    def remove_object(self, bucket, key) -> None:
        self.objects.pop(key, None)


@pytest.fixture(autouse=True)
def fake_minio(monkeypatch: pytest.MonkeyPatch) -> _FakeMinioClient:
    fake = _FakeMinioClient()
    monkeypatch.setattr(documents_router, "_minio_client", None)
    monkeypatch.setattr(documents_router, "get_minio_client", lambda: fake)
    return fake


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


UUID_A = "11111111-1111-1111-1111-111111111111"
UUID_B = "22222222-2222-2222-2222-222222222222"


def _upload(client: TestClient, browser_uuid: str, filename="notes.txt", content=b"hello",
            content_type="text/plain"):
    return client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, content, content_type)},
    )


def test_upload_missing_header_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_blank_header_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": "   "},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_txt_is_stored_in_minio_and_db(
    client: TestClient, fake_minio: _FakeMinioClient
) -> None:
    response = _upload(client, UUID_A)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    document_id = body["document_id"]

    status_response = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": UUID_A}
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "pending"
    assert len(fake_minio.objects) == 1


def test_upload_pdf_and_docx_are_accepted(client: TestClient) -> None:
    pdf = _upload(client, UUID_A, "report.pdf", b"%PDF-1.4", "application/pdf")
    assert pdf.status_code == 201

    docx = _upload(
        client,
        UUID_A,
        "report.docx",
        b"docxbytes",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert docx.status_code == 201


def test_upload_rejects_unsupported_type(
    client: TestClient, fake_minio: _FakeMinioClient
) -> None:
    response = _upload(client, UUID_A, "image.png", b"pngbytes", "image/png")

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]
    assert fake_minio.objects == {}

    documents = client.get("/api/documents", headers={"X-Browser-UUID": UUID_A}).json()
    assert all(d["filename"] != "image.png" for d in documents)


def test_upload_rejects_mismatched_content_type(client: TestClient) -> None:
    response = _upload(client, UUID_A, "notes.txt", b"hello", "application/pdf")
    assert response.status_code == 400


def test_list_documents_is_scoped_by_browser_uuid(client: TestClient) -> None:
    _upload(client, UUID_A, "a.txt")
    _upload(client, UUID_B, "b.txt")

    response = client.get("/api/documents", headers={"X-Browser-UUID": UUID_A})

    assert response.status_code == 200
    filenames = [d["filename"] for d in response.json()]
    assert "a.txt" in filenames
    assert "b.txt" not in filenames


def test_status_returns_404_for_other_browser_uuid(client: TestClient) -> None:
    upload = _upload(client, UUID_A, "secret.txt")
    document_id = upload.json()["document_id"]

    response = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": UUID_B}
    )

    assert response.status_code == 404


def test_delete_removes_document_for_owner(
    client: TestClient, fake_minio: _FakeMinioClient
) -> None:
    upload = _upload(client, UUID_A, "to-delete.txt")
    document_id = upload.json()["document_id"]

    response = client.delete(
        f"/api/documents/{document_id}", headers={"X-Browser-UUID": UUID_A}
    )

    assert response.status_code == 204
    assert fake_minio.objects == {}

    status_after = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": UUID_A}
    )
    assert status_after.status_code == 404


def test_delete_returns_404_for_other_browser_uuid(client: TestClient) -> None:
    upload = _upload(client, UUID_A, "not-yours.txt")
    document_id = upload.json()["document_id"]

    response = client.delete(
        f"/api/documents/{document_id}", headers={"X-Browser-UUID": UUID_B}
    )

    assert response.status_code == 404
