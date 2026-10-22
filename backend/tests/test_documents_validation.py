"""Unsupported file types: rejected with a 400 naming the accepted formats,
and no row left behind.

AC ref: "A pytest test asserts an unsupported file type (e.g. .exe or .png)
returns HTTP 400 with a message naming PDF, TXT and DOCX, and that no
document row is created".
"""

import pytest


@pytest.mark.parametrize("fixture_name", ["unsupported_exe_file", "unsupported_png_file"])
def test_unsupported_file_type_rejected_with_400_and_no_row_created(
    client, browser_uuid, fixture_name, request
):
    filename, content, content_type = request.getfixturevalue(fixture_name)

    before = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    before_count = len(before.json()) if before.status_code == 200 else 0

    response = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 400
    message = response.text.lower()
    assert "pdf" in message
    assert "txt" in message
    assert "docx" in message

    after = client.get("/api/documents", headers={"X-Browser-UUID": browser_uuid})
    after_count = len(after.json()) if after.status_code == 200 else 0
    assert after_count == before_count
