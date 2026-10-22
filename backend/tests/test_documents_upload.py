"""POST /api/documents and GET /api/documents: supported formats, persistence
against the browser UUID, and the missing-header case.

AC refs: "A pytest test asserts a PDF, a TXT and a DOCX upload each return
success, are persisted against the X-Browser-UUID from the request header,
and appear in GET /api/documents for that UUID only" and "A pytest test
asserts a request without the X-Browser-UUID header returns 400".
"""

import pytest


def _upload(client, browser_uuid, file_tuple):
    filename, content, content_type = file_tuple
    return client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, content, content_type)},
    )


@pytest.mark.parametrize("fixture_name", ["pdf_file", "txt_file", "docx_file"])
def test_supported_upload_succeeds_and_is_persisted_for_its_uuid(
    client, browser_uuid, other_browser_uuid, fixture_name, request
):
    file_tuple = request.getfixturevalue(fixture_name)

    response = _upload(client, browser_uuid, file_tuple)

    assert response.status_code in (200, 201, 202), response.text
    body = response.json()
    assert "document_id" in body
    document_id = body["document_id"]

    owner_list = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    assert owner_list.status_code == 200
    owner_ids = [d["document_id"] for d in owner_list.json()]
    assert document_id in owner_ids

    other_list = client.get("/api/documents", headers={"X-Browser-UUID": other_browser_uuid})
    assert other_list.status_code == 200
    other_ids = [d["document_id"] for d in other_list.json()]
    assert document_id not in other_ids


def test_upload_without_browser_uuid_header_returns_400(client, pdf_file):
    filename, content, content_type = pdf_file

    response = client.post(
        "/api/documents",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 400


def test_list_without_browser_uuid_header_returns_400(client):
    response = client.get("/api/documents")

    assert response.status_code == 400
