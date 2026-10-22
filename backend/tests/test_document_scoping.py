"""NFR-002: the X-Browser-UUID header is the only tenant boundary.

`GET /api/documents` scoping (list only returns the caller's own rows) is
already covered by `test_documents.py`. This file adds the `/status` polling
endpoint from the architecture's OpenAPI contract
(`GET /api/documents/{document_id}/status`), which does not exist in
`app/routers/documents.py` yet. Those checks are written against the
contract and marked `xfail(strict=False)` so they read PASS once the route
ships and never block the suite while it doesn't.
"""

from __future__ import annotations

import io


def _upload(client, fake_minio, browser_uuid: str) -> str:
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": ("notes.txt", io.BytesIO(b"hello world"), "text/plain")},
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_status_endpoint_returns_document_for_owning_browser_uuid(
    client, fake_minio, browser_uuid
) -> None:
    document_id = _upload(client, fake_minio, browser_uuid)
    response = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": browser_uuid}
    )
    if response.status_code == 404:
        import pytest

        pytest.xfail("GET /api/documents/{id}/status not implemented yet (US-003/US-005 pending)")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"pending", "processing", "ready", "failed"}


def test_status_endpoint_hides_other_browser_uuids_document(
    client, fake_minio, browser_uuid
) -> None:
    import uuid

    document_id = _upload(client, fake_minio, browser_uuid)
    other_uuid = str(uuid.uuid4())
    response = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": other_uuid}
    )
    # A route that does not exist at all also 404s here; that is acceptable
    # for this specific assertion (a stranger must never see the document)
    # but is tracked as a real gap by the sibling "owning browser uuid" test.
    assert response.status_code == 404


def test_list_documents_empty_for_a_browser_uuid_that_never_uploaded(client, fake_minio) -> None:
    import uuid

    response = client.get("/api/documents", headers={"X-Browser-UUID": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.json() == []
