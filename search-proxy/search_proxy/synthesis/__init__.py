from __future__ import annotations

from .builder import build_context, truncate_text
from .client import LLMClient, LLMConfig, extract_citations
from .models import Citation, SourceDocument, SynthesisOutput
from .prompts import SYSTEM_PROMPT, build_synthesis_messages
from .service import SynthesisService

__all__ = [
    "Citation",
    "LLMClient",
    "LLMConfig",
    "SourceDocument",
    "SynthesisOutput",
    "SynthesisService",
    "build_context",
    "build_synthesis_messages",
    "extract_citations",
    "truncate_text",
    "SYSTEM_PROMPT",
]
