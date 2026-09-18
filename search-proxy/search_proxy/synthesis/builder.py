from __future__ import annotations

from search_proxy.extractor.models import ExtractedDocument
from search_proxy.models import Result
from .models import SourceDocument


def truncate_text(text: str, max_words: int) -> str:
    """Truncates text to a maximum word count, appending an indicator if truncated."""
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    return f"{truncated}... [content truncated for context management]"


def build_context(
    results: list[Result],
    extracted_docs: list[ExtractedDocument],
    max_words_per_doc: int = 3000,
    max_total_words: int = 12000,
) -> tuple[str, list[SourceDocument]]:
    """Constructs structured context for the LLM combining search and extraction.

    Applies graceful degradation:
    - If extracted successfully (status == 'ok') with text: uses extracted full text.
    - If extraction fails for any reason: inherits the search snippet.
    """
    docs_by_url: dict[str, ExtractedDocument] = {
        doc.url: doc for doc in extracted_docs if doc.url
    }

    sources: list[SourceDocument] = []
    total_words = 0

    for i, res in enumerate(results, start=1):
        if not res.url:
            continue

        doc = docs_by_url.get(res.url)
        title = (doc.title if doc and doc.title else res.title) or "Untitled"

        if doc and doc.status == "ok" and doc.text and len(doc.text.strip()) > 0:
            tier = "full_text"
            raw_content = doc.text.strip()
        else:
            tier = "snippet"
            raw_content = (
                res.snippet.strip() if res.snippet else "No content available."
            )

        content = truncate_text(raw_content, max_words_per_doc)
        words_in_doc = len(content.split())

        if total_words + words_in_doc > max_total_words and sources:
            # Respect global context word limit
            break

        total_words += words_in_doc
        sources.append(
            SourceDocument(
                index=i,
                title=title,
                url=res.url,
                source_tier=tier,
                content=content,
            )
        )

    blocks: list[str] = []
    for src in sources:
        tier_str = (
            "Extracted Full Text"
            if src.source_tier == "full_text"
            else "Search Snippet"
        )
        block = (
            f"--- [SOURCE {src.index}] ---\n"
            f"Title: {src.title}\n"
            f"URL: {src.url}\n"
            f"Evidence Tier: {tier_str}\n"
            f"Content:\n{src.content}\n"
        )
        blocks.append(block)

    context_str = "\n".join(blocks)
    return context_str, sources
