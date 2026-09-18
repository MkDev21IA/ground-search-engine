from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceDocument:
    """Represents a source document formatted for LLM context."""

    index: int
    title: str
    url: str
    source_tier: str  # "full_text" | "snippet"
    content: str


@dataclass
class Citation:
    """Represents an inline citation parsed from the model response."""

    url: str
    label: str


@dataclass
class SynthesisOutput:
    """Consolidated synthesis output containing answer, citations, and sources."""

    prompt: str
    answer: str
    citations: list[Citation]
    sources_used: list[SourceDocument]
    model: str
    generated_at: str
    raw_usage: dict[str, Any] = field(default_factory=dict)
