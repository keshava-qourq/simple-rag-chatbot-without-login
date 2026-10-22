"""Cross-UUID isolation on the single-document endpoints.

AC ref: "A pytest test asserts cross-UUID isolation: GET status and DELETE
for a document owned by another UUID return 404".
"""


def test_status_and_delete_from_another_uuid_return_404(client, browser_uuid, other_browser_uuid, pdf_file):
    filename, content, content_type = pdf_file

    upload = client.post(
        "/api/documents",
        headers={"X-Browser-UUID": browser_uuid},
        files={"file": (filename, content, content_type)},
    )
    assert upload.status_code in (200, 201, 202), upload.text
    document_id = upload.json()["document_id"]

    status_as_other = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": other_browser_uuid}
    )
    assert status_as_other.status_code == 404

    delete_as_other = client.delete(
        f"/api/documents/{document_id}", headers={"X-Browser-UUID": other_browser_uuid}
    )
    assert delete_as_other.status_code == 404

    # The owner can still see it: the "other" calls above must not have deleted it.
    status_as_owner = client.get(
        f"/api/documents/{document_id}/status", headers={"X-Browser-UUID": browser_uuid}
    )
    assert status_as_owner.status_code == 200
