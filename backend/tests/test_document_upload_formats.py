"""AC-005 / AC-006: accepted and rejected upload formats.

`test_documents.py` already covers the TXT happy path and a renamed-.exe
case; this file adds PDF, DOCX, and the full rejected-format list so every
format named in the acceptance criteria has its own assertion.
"""

from __future__ import annotations

import io

import pytest

from conftest import build_docx, build_minimal_pdf


def test_upload_pdf_creates_document_and_object(client, fake_minio, browser_uuid) -> None:
    pdf_bytes = build_minimal_pdf("Hello PDF fixture")
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": ("report.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filename"] == "report.pdf"
    assert body["status"] == "pending"
    assert len(fake_minio.objects) == 1
    stored_key = next(iter(fake_minio.objects))
    assert browser_uuid in stored_key

    list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    assert list_resp.status_code == 200
    docs = list_resp.json()
    assert len(docs) == 1
    assert docs[0]["filename"] == "report.pdf"
    assert docs[0]["browser_uuid"] == browser_uuid


def test_upload_docx_creates_document_and_object(client, fake_minio, browser_uuid) -> None:
    pytest.importorskip("docx", reason="python-docx not installed yet (US-005-1 pending)")
    docx_bytes = build_docx("Hello DOCX fixture")
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={
            "file": (
                "notes.docx",
                io.BytesIO(docx_bytes),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filename"] == "notes.docx"
    assert body["status"] == "pending"
    assert len(fake_minio.objects) == 1

    list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    docs = list_resp.json()
    assert len(docs) == 1
    assert docs[0]["filename"] == "notes.docx"


def test_upload_txt_creates_document_and_object(client, fake_minio, browser_uuid) -> None:
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": ("plain.txt", io.BytesIO(b"Hello TXT fixture"), "text/plain")},
    )
    assert response.status_code == 200, response.text
    assert len(fake_minio.objects) == 1
    list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    assert len(list_resp.json()) == 1


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("malware.exe", "application/x-msdownload"),
        ("data.csv", "text/csv"),
        ("photo.png", "image/png"),
    ],
)
def test_upload_rejects_unsupported_formats_with_clear_message(
    client, fake_minio, browser_uuid, filename, content_type
) -> None:
    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, io.BytesIO(b"not a real payload"), content_type)},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "PDF" in detail
    assert "TXT" in detail
    assert "DOCX" in detail
    assert fake_minio.objects == {}

    list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    assert list_resp.json() == []


def test_upload_without_browser_uuid_header_returns_400(client, fake_minio) -> None:
    response = client.post(
        "/api/documents",
        files={"file": ("plain.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
    assert fake_minio.objects == {}
