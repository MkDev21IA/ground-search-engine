from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExtractedDocument:
    url: str
    title: str | None
    text: str | None
    content_type: str
    status: str  # "ok", "blocked_robots", "needs_js", "http_error", "empty"
    extractor_used: str | None
    fetched_at: str
    error: str | None = None
