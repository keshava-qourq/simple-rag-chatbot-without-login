"""Shared fixtures for the document-upload test suite.

Runs with no live MinIO and no live Gemini key: the `minio.Minio` class and
the `google.genai.Client` class are replaced with in-memory fakes *before*
`app.main` (and whatever router/service modules it imports) get a chance to
construct a real client from them. This has to happen at import time, not
inside a fixture function, because pytest loads conftest.py before it
collects test modules in the same directory -- any `from minio import Minio`
or `from google import genai` done later by application code will see the
patched attribute.
"""

import io
import os
import sys
import uuid
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")
os.environ.setdefault("MINIO_ENDPOINT", "fake-minio:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "fake-access-key")
os.environ.setdefault("MINIO_SECRET_KEY", "fake-secret-key")
os.environ.setdefault("MINIO_BUCKET", "test-bucket")
os.environ.setdefault("GEMINI_API_KEY", "fake-gemini-key")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class _FakeMinioObjectStat:
    def __init__(self, size: int) -> None:
        self.size = size


class FakeMinioClient:
    """In-memory stand-in for `minio.Minio` -- no network, no container."""

    _store: dict[tuple[str, str], bytes] = {}

    def __init__(self, *args, **kwargs) -> None:
        pass

    def bucket_exists(self, bucket_name: str) -> bool:
        return True

    def make_bucket(self, bucket_name: str) -> None:
        return None

    def put_object(self, bucket_name, object_name, data, length, *args, **kwargs):
        payload = data.read() if hasattr(data, "read") else bytes(data)
        FakeMinioClient._store[(bucket_name, object_name)] = payload
        return None

    def get_object(self, bucket_name, object_name, *args, **kwargs):
        payload = FakeMinioClient._store.get((bucket_name, object_name), b"")
        return io.BytesIO(payload)

    def stat_object(self, bucket_name, object_name, *args, **kwargs):
        payload = FakeMinioClient._store.get((bucket_name, object_name), b"")
        return _FakeMinioObjectStat(size=len(payload))

    def remove_object(self, bucket_name, object_name, *args, **kwargs):
        FakeMinioClient._store.pop((bucket_name, object_name), None)
        return None


try:
    import minio  # noqa: E402

    minio.Minio = FakeMinioClient  # patch the attribute every later import sees
except ImportError:
    pass


class _FakeEmbedding:
    def __init__(self, values):
        self.values = values


class _FakeEmbedResponse:
    def __init__(self, n: int):
        self.embeddings = [_FakeEmbedding([0.01] * 768) for _ in range(n)]


class _FakeGenerateResponse:
    text = "This is a stubbed Gemini answer for tests."


class _FakeModels:
    def embed_content(self, *args, **kwargs):
        contents = kwargs.get("contents", args[1] if len(args) > 1 else [""])
        n = len(contents) if isinstance(contents, list) else 1
        return _FakeEmbedResponse(n)

    def generate_content(self, *args, **kwargs):
        return _FakeGenerateResponse()


class FakeGenaiClient:
    """In-memory stand-in for `google.genai.Client` -- no network call made."""

    def __init__(self, *args, **kwargs) -> None:
        self.models = _FakeModels()


try:
    from google import genai  # noqa: E402

    genai.Client = FakeGenaiClient
except ImportError:
    pass


# ---------------------------------------------------------------------------
# App fixtures
# ---------------------------------------------------------------------------

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client():
    """A fresh TestClient per test; the app's SQLite tables persist across the
    run (create_all is additive), so tests must not assume table isolation --
    they isolate instead via distinct random browser UUIDs per test."""
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def browser_uuid() -> str:
    return str(uuid.uuid4())


@pytest.fixture()
def other_browser_uuid() -> str:
    return str(uuid.uuid4())


def _read(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()


@pytest.fixture()
def pdf_file():
    return ("tiny.pdf", _read("tiny.pdf"), "application/pdf")


@pytest.fixture()
def txt_file():
    return ("tiny.txt", _read("tiny.txt"), "text/plain")


@pytest.fixture()
def docx_file():
    return (
        "tiny.docx",
        _read("tiny.docx"),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture()
def corrupt_pdf_file():
    """Has a .pdf extension and the PDF content-type, but is not parseable."""
    return ("corrupt.pdf", _read("corrupt.pdf"), "application/pdf")


@pytest.fixture()
def unsupported_exe_file():
    return ("unsupported.exe", _read("unsupported.exe"), "application/octet-stream")


@pytest.fixture()
def unsupported_png_file():
    return ("unsupported.png", _read("unsupported.png"), "image/png")
