from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from search_proxy.extractor.models import ExtractedDocument
from search_proxy.models import Result
from .builder import build_context
from .client import LLMClient, extract_citations
from .models import SynthesisOutput
from .prompts import build_synthesis_messages


class SynthesisService:
    """Orchestrates grounded answer synthesis with inline citations."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def synthesize(
        self,
        query: str,
        results: list[Result],
        extracted_docs: list[ExtractedDocument],
        max_words_per_doc: int = 3000,
        max_total_words: int = 12000,
    ) -> SynthesisOutput:
        """Generates a grounded response based on search results and extracted documents."""
        context_str, sources_used = build_context(
            results=results,
            extracted_docs=extracted_docs,
            max_words_per_doc=max_words_per_doc,
            max_total_words=max_total_words,
        )

        messages = build_synthesis_messages(query=query, context=context_str)
        answer, raw_usage = self.llm_client.generate(messages)
        citations = extract_citations(answer)

        now_iso = datetime.now(timezone.utc).isoformat()

        return SynthesisOutput(
            prompt=query,
            answer=answer,
            citations=citations,
            sources_used=sources_used,
            model=self.llm_client.config.model,
            generated_at=now_iso,
            raw_usage=raw_usage,
        )
