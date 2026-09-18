from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Query:
    text: str
    lang: str = "en"
    max_results: int = 10


@dataclass
class Result:
    engine: str
    url: str
    title: str
    snippet: str
    rank: int
    fetched_at: str
    error: str | None = None
