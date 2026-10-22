"""Tests for POST /api/documents and GET /api/documents.

The MinIO client is overridden with an in-memory fake so these tests never
need a running object store, matching how `get_db` is already a FastAPI
dependency rather than a module-level singleton. Browser UUIDs are generated
fresh per test because the app's sqlite file persists across test runs.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.services import minio_client

client = TestClient(app)


class _FakeMinio:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self._buckets: set[str] = set()

    def bucket_exists(self, bucket: str) -> bool:
        return bucket in self._buckets

    def make_bucket(self, bucket: str) -> None:
        self._buckets.add(bucket)

    def put_object(self, bucket, key, data, length, content_type=None):  # noqa: ANN001
        self.objects[f"{bucket}/{key}"] = data.read()


def _override_minio() -> _FakeMinio:
    fake = _FakeMinio()
    app.dependency_overrides[minio_client] = lambda: fake
    return fake


def _clear_override() -> None:
    app.dependency_overrides.pop(minio_client, None)


def test_upload_requires_browser_uuid_header() -> None:
    fake = _override_minio()
    try:
        response = client.post(
            "/api/documents",
            files={"file": ("a.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 400
        assert fake.objects == {}
    finally:
        _clear_override()


def test_upload_accepts_txt_and_lists_only_for_matching_browser_uuid() -> None:
    fake = _override_minio()
    browser_uuid = str(uuid.uuid4())
    other_uuid = str(uuid.uuid4())
    try:
        response = client.post(
            "/api/documents",
            headers={"X-Browser-UUID": browser_uuid},
            files={"file": ("notes.txt", b"hello world", "text/plain")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "notes.txt"
        assert body["status"] == "pending"
        assert "id" in body
        assert len(fake.objects) == 1

        other_resp = client.post(
            "/api/documents",
            headers={"X-Browser-UUID": other_uuid},
            files={"file": ("other.txt", b"bye", "text/plain")},
        )
        assert other_resp.status_code == 200

        list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert len(docs) == 1
        assert docs[0]["filename"] == "notes.txt"
        assert docs[0]["browser_uuid"] == browser_uuid
    finally:
        _clear_override()


def test_upload_rejects_unsupported_format() -> None:
    fake = _override_minio()
    browser_uuid = str(uuid.uuid4())
    try:
        response = client.post(
            "/api/documents",
            headers={"X-Browser-UUID": browser_uuid},
            files={"file": ("virus.exe", b"MZ...", "application/x-msdownload")},
        )
        assert response.status_code == 400
        body = response.json()
        assert "PDF, TXT and DOCX" in body["detail"]
        assert fake.objects == {}

        list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
        assert list_resp.json() == []
    finally:
        _clear_override()


def test_renamed_exe_with_allowed_extension_but_wrong_content_type_is_rejected() -> None:
    fake = _override_minio()
    browser_uuid = str(uuid.uuid4())
    try:
        response = client.post(
            "/api/documents",
            headers={"X-Browser-UUID": browser_uuid},
            files={"file": ("malware.pdf", b"MZ...", "application/x-msdownload")},
        )
        assert response.status_code == 400
        assert fake.objects == {}
    finally:
        _clear_override()


def test_documents_endpoints_appear_in_openapi() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/documents" in response.json()["paths"]


def test_health_still_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
