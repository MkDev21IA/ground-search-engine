from __future__ import annotations

import re
import lxml.html
from readability import Document
import trafilatura


def _is_spa(html: str) -> bool:
    """Detects typical signatures indicating a client-side JavaScript SPA."""
    lower = html.lower()
    spa_patterns = [
        r'id=["\']root["\']',
        r'id=["\']app["\']',
        r'id=["\']__next["\']',
        r'<noscript>.*javascript.*</noscript>',
    ]
    for pattern in spa_patterns:
        if re.search(pattern, lower, re.DOTALL):
            return True
    return False


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    # Collapse consecutive whitespace while preserving paragraph lines
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def extract_html_content(
    html: str,
    url: str | None = None,
    min_content_length: int = 100,
) -> tuple[str | None, str | None, str | None, str]:
    """Extracts title, clean text, extractor engine used, and status from HTML.

    Returns: (title, text, extractor_used, status)
    status can be: 'ok', 'needs_js', 'empty'
    """
    title: str | None = None
    text: str | None = None
    extractor_used: str | None = None

    # 1. Primary extraction with trafilatura
    try:
        extracted = trafilatura.extract(
            html,
            url=url,
            include_links=False,
            include_comments=False,
            output_format="txt",
        )
        if extracted:
            text = _clean_text(extracted)
            extractor_used = "trafilatura"

        metadata = trafilatura.extract_metadata(html)
        if metadata and metadata.title:
            title = metadata.title
    except Exception:
        text = None

    # 2. Fallback to readability-lxml if trafilatura fails or yields insufficient content
    if not text or len(text) < min_content_length:
        try:
            doc = Document(html)
            if not title:
                title = doc.title()
            summary_html = doc.summary()
            if summary_html:
                tree = lxml.html.fromstring(summary_html)
                readability_text = _clean_text(tree.text_content())
                if len(readability_text) > (len(text) if text else 0):
                    text = readability_text
                    extractor_used = "readability"
        except Exception:
            pass

    # 3. Fallback extraction of <title> tag
    if not title:
        try:
            tree = lxml.html.fromstring(html)
            title_tag = tree.find(".//title")
            if title_tag is not None and title_tag.text:
                title = title_tag.text.strip()
        except Exception:
            pass

    # 4. Evaluate extraction status
    if text and len(text) >= min_content_length:
        return title, text, extractor_used, "ok"

    if _is_spa(html):
        return title, text or None, extractor_used, "needs_js"

    return title, text or None, extractor_used, "empty"
