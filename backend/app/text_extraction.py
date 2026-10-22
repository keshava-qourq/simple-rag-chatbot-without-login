"""Text extraction, dispatched by file type.

AC-010/011/012: PDF via pypdf (page text concatenated in order), TXT decoded
as UTF-8 with a safe fallback for undecodable bytes, DOCX via python-docx
(paragraph text concatenated). Extraction never raises: a corrupt file yields
``None`` rather than an exception, so callers can tell "parsed, no text" (an
empty string) apart from "could not be parsed at all" (``None``) and decide
how to record that in the Document row.
"""

from __future__ import annotations

import io


def _extract_pdf(data: bytes) -> str | None:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:  # noqa: BLE001 -- any pypdf failure means "could not extract"
        return None


def _extract_txt(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        # Safe fallback for undecodable bytes rather than raising (AC-011).
        return data.decode("utf-8", errors="replace")


def _extract_docx(data: bytes) -> str | None:
    try:
        import docx

        document = docx.Document(io.BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception:  # noqa: BLE001 -- any python-docx failure means "could not extract"
        return None


_DISPATCH = {
    "pdf": _extract_pdf,
    "txt": _extract_txt,
    "docx": _extract_docx,
}


def extract_text(data: bytes, file_type: str) -> str | None:
    """Extracted text for a supported file type, or ``None`` if it could not be parsed.

    Never raises: callers that need to distinguish success from failure check
    the return value, not an exception.
    """
    handler = _DISPATCH.get(file_type.lower().lstrip("."))
    if handler is None:
        return None
    return handler(data)
