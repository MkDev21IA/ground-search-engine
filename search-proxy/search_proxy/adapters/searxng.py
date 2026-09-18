from __future__ import annotations

import os
from datetime import UTC, datetime

import httpx

from ..base import SearchAdapter, error_result
from ..models import Query, Result


class SearxngAdapter(SearchAdapter):
    """Adapter for a self-hosted SearXNG instance (see README, 'Getting Started').

    Requires `json` enabled under `search.formats` in SearXNG's settings.yml
    (JSON format is disabled by default in upstream SearXNG).
    """

    name = "searxng"

    def __init__(self, base_url: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = (
            base_url or os.environ.get("SEARXNG_BASE_URL", "http://localhost:8080")
        ).rstrip("/")
        self.timeout = timeout

    def search(self, query: Query) -> list[Result]:
        fetched_at = datetime.now(UTC).isoformat()
        params = {
            "q": query.text,
            "format": "json",
            "language": query.lang,
        }
        try:
            response = httpx.get(
                f"{self.base_url}/search", params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            return [error_result(self.name, fetched_at, exc)]

        results: list[Result] = []
        for rank, item in enumerate(data.get("results", [])[: query.max_results], start=1):
            results.append(
                Result(
                    engine=self.name,
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("content", ""),
                    rank=rank,
                    fetched_at=fetched_at,
                )
            )
        return results
