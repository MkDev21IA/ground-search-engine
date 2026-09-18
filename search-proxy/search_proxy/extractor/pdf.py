from __future__ import annotations

import io
from pypdf import PdfReader


def extract_pdf_content(
    pdf_bytes: bytes,
    min_content_length: int = 50,
) -> tuple[str | None, str | None, str | None, str]:
    """Extracts title, clean text, extractor engine used, and status from PDF bytes.

    Returns: (title, text, extractor_used, status)
    status can be: 'ok', 'empty', or 'pdf_error: <details>'
    """
    title: str | None = None
    text: str | None = None
    extractor_used: str | None = "pypdf"

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        if reader.metadata and reader.metadata.title:
            title = str(reader.metadata.title).strip()

        pages_text: list[str] = []
        for page in reader.pages:
            page_content = page.extract_text()
            if page_content:
                pages_text.append(page_content.strip())

        if pages_text:
            text = "\n\n".join(pages_text).strip()
    except Exception as exc:
        return title, None, extractor_used, f"pdf_error: {exc}"

    if text and len(text) >= min_content_length:
        return title, text, extractor_used, "ok"

    return title, text or None, extractor_used, "empty"
