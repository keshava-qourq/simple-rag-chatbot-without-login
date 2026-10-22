"""Shared fixtures for the document-upload and extraction test suites.

Nothing here talks to a real MinIO or Gemini: the MinIO client is swapped for
an in-memory fake via FastAPI's dependency_overrides, and any google-genai
client that gets constructed is swapped for one that returns canned,
deterministic responses. Both patches are no-ops if the corresponding package
is not installed yet -- the extraction feature these tests target may still be
mid-build, and an ImportError here must not take down the whole suite.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from app.main import app
from app.services import minio_client


class FakeMinio:
    """An in-memory stand-in for the subset of the MinIO client the app uses."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self._buckets: set[str] = set()

    def bucket_exists(self, bucket: str) -> bool:
        return bucket in self._buckets

    def make_bucket(self, bucket: str) -> None:
        self._buckets.add(bucket)

    def put_object(self, bucket, key, data, length, content_type=None):  # noqa: ANN001
        self.objects[f"{bucket}/{key}"] = data.read()

    def get_object(self, bucket, key):  # noqa: ANN001
        class _Resp:
            def __init__(self, payload: bytes) -> None:
                self._payload = payload

            def read(self) -> bytes:
                return self._payload

            def close(self) -> None:
                pass

            def release_conn(self) -> None:
                pass

        return _Resp(self.objects[f"{bucket}/{key}"])


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def fake_minio() -> Iterator[FakeMinio]:
    """Overrides the `minio_client` dependency for the duration of a test."""
    fake = FakeMinio()
    app.dependency_overrides[minio_client] = lambda: fake
    try:
        yield fake
    finally:
        app.dependency_overrides.pop(minio_client, None)


@pytest.fixture()
def browser_uuid() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="session", autouse=True)
def _no_live_gemini_calls() -> Iterator[None]:
    """Replaces google.genai.Client with a fake, if the package is installed.

    AC says extraction/embedding must run offline. If google-genai is not
    installed yet (the extraction feature may still be mid-build), there is
    nothing to patch and nothing that could reach the network either.
    """
    mp = MonkeyPatch()
    try:
        from google import genai  # type: ignore[import-not-found]
    except ImportError:
        yield
        mp.undo()
        return

    class _FakeEmbedding:
        values = [0.0] * 768

    class _FakeEmbedResult:
        embeddings = [_FakeEmbedding()]

    class _FakeGenerateResult:
        text = "This is a fake, offline answer."

    class _FakeModels:
        def embed_content(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
            return _FakeEmbedResult()

        def generate_content(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
            return _FakeGenerateResult()

    class _FakeClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
            self.models = _FakeModels()

    mp.setattr(genai, "Client", _FakeClient)
    yield
    mp.undo()


def build_minimal_pdf(text: str) -> bytes:
    """A tiny, hand-built single-page PDF whose content stream draws `text`.

    Built without pypdf (the reading library, not a writer) so this fixture
    generator has no dependency on the extraction feature under test. Verified
    against pypdf's PdfReader to extract back exactly this text.
    """
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>"
        b"/MediaBox[0 0 612 792]/Contents 5 0 R>>",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    content = f"BT /F1 24 Tf 100 700 Td ({text}) Tj ET".encode()
    objects.append(b"<</Length %d>>\nstream\n" % len(content) + content + b"\nendstream")

    buf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n".encode()
        buf += body
        buf += b"\nendobj\n"
    xref_offset = len(buf)
    count = len(objects) + 1
    buf += f"xref\n0 {count}\n".encode()
    buf += b"0000000000 65535 f \n"
    for off in offsets:
        buf += f"{off:010d} 00000 n \n".encode()
    buf += b"trailer\n"
    buf += f"<</Size {count}/Root 1 0 R>>\n".encode()
    buf += b"startxref\n"
    buf += str(xref_offset).encode()
    buf += b"\n%%EOF"
    return bytes(buf)


def build_docx(text: str) -> bytes:
    """A .docx built via python-docx; callers must `pytest.importorskip("docx")` first."""
    import io

    import docx

    document = docx.Document()
    document.add_paragraph(text)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()
