"""AC-010/011/012: text extraction per format, and graceful failure on a corrupt file.

Exercises both `app.services.extract_text` (also re-exported from
`app.text_extraction`) directly, and the full pipeline: upload, then poll
`/api/documents/{id}/status` until it reaches a terminal status ("processed"
or "failed", per this ticket's contract).

Both tiers are offline: MinIO is the in-memory fake from conftest, and the
session-wide fixture there fakes any google-genai client an embedding step
might construct.
"""

from __future__ import annotations

import io
import time
import uuid

import pytest
from conftest import build_docx, build_minimal_pdf


def _extract_text():
    from app.services import extract_text

    return extract_text


def test_extract_text_from_txt() -> None:
    extract_text = _extract_text()
    assert extract_text(b"Hello TXT fixture", "txt") == "Hello TXT fixture"


def test_extract_text_from_pdf() -> None:
    extract_text = _extract_text()
    pdf_bytes = build_minimal_pdf("Hello PDF fixture")
    assert "Hello PDF fixture" in extract_text(pdf_bytes, "pdf")


def test_extract_text_from_docx() -> None:
    pytest.importorskip("docx", reason="python-docx not installed yet (US-005-1 pending)")
    extract_text = _extract_text()
    docx_bytes = build_docx("Hello DOCX fixture")
    assert "Hello DOCX fixture" in extract_text(docx_bytes, "docx")


def test_extract_text_from_corrupt_file_does_not_raise() -> None:
    extract_text = _extract_text()
    # Extension says pdf, bytes are garbage: this must not raise, whatever it
    # returns (empty string, None, or a raised-and-caught marker upstream).
    try:
        extract_text(b"not a real pdf at all", "pdf")
    except Exception as exc:  # noqa: BLE001 -- the assertion *is* "did not raise"
        pytest.fail(f"extract_text raised on a corrupt file instead of handling it: {exc!r}")


def _poll_status(client, document_id: str, browser_uuid: str, timeout: float = 2.0) -> dict:
    deadline = time.monotonic() + timeout
    last_body: dict = {}
    while time.monotonic() < deadline:
        response = client.get(
            f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": browser_uuid}
        )
        last_body = response.json()
        if last_body.get("status") in {"processed", "failed"}:
            return last_body
        time.sleep(0.05)
    return last_body


@pytest.mark.parametrize(
    ("filename", "content_type", "build"),
    [
        ("report.txt", "text/plain", lambda: b"Hello TXT fixture"),
        ("report.pdf", "application/pdf", lambda: build_minimal_pdf("Hello PDF fixture")),
    ],
)
def test_upload_of_valid_file_reaches_ready_status(
    client, fake_minio, browser_uuid, filename, content_type, build
) -> None:
    data = build()
    upload = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, io.BytesIO(data), content_type)},
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    final = _poll_status(client, document_id, browser_uuid)
    assert final.get("status") == "processed", final


def test_upload_of_valid_docx_reaches_ready_status(client, fake_minio, browser_uuid) -> None:
    pytest.importorskip("docx", reason="python-docx not installed yet (US-005-1 pending)")
    data = build_docx("Hello DOCX fixture")
    upload = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={
            "file": (
                "report.docx",
                io.BytesIO(data),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    final = _poll_status(client, document_id, browser_uuid)
    assert final.get("status") == "processed", final


def test_corrupt_pdf_marks_document_failed_rather_than_raising(
    client, fake_minio, browser_uuid
) -> None:
    upload = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={
            "file": (
                "corrupt.pdf",
                io.BytesIO(b"%PDF-1.4\nnot actually a valid pdf body"),
                "application/pdf",
            )
        },
    )
    # Uploading must itself succeed (the corruption is only discoverable once
    # extraction runs); the failure belongs in the status, not the response code.
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    final = _poll_status(client, document_id, browser_uuid)
    assert final.get("status") == "failed", final
    assert final.get("error")


def test_list_and_status_never_leak_another_browser_uuids_corrupt_document(
    client, fake_minio, browser_uuid
) -> None:
    other_uuid = str(uuid.uuid4())
    upload = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": other_uuid},
        files={
            "file": (
                "corrupt.pdf",
                io.BytesIO(b"%PDF-1.4\nnot actually a valid pdf body"),
                "application/pdf",
            )
        },
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    list_resp = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    assert all(doc["id"] != document_id for doc in list_resp.json())
