from __future__ import annotations

from datetime import UTC, datetime
import httpx

from .fetcher import (
    DEFAULT_USER_AGENT,
    RobotsChecker,
    RobotsDisallowedError,
    fetch_resource,
)
from .html import extract_html_content
from .models import ExtractedDocument
from .pdf import extract_pdf_content


class ContentExtractor:
    """Orchestrates polite HTTP fetching and clean main-text extraction."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 10.0,
        robots_checker: RobotsChecker | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.robots_checker = robots_checker or RobotsChecker(user_agent=user_agent)
        self.client = client

    def extract_many(self, urls: list[str]) -> list[ExtractedDocument]:
        """Extracts content from multiple URLs sequentially."""
        return [self.extract_from_url(url) for url in urls]

    def extract_from_url(self, url: str) -> ExtractedDocument:
        fetched_at = datetime.now(UTC).isoformat()
        try:
            status_code, content_type, body_bytes, _ = fetch_resource(
                url=url,
                user_agent=self.user_agent,
                timeout=self.timeout,
                client=self.client,
                robots_checker=self.robots_checker,
            )
        except RobotsDisallowedError as exc:
            return ExtractedDocument(
                url=url,
                title=None,
                text=None,
                content_type="text/html",
                status="blocked_robots",
                extractor_used=None,
                fetched_at=fetched_at,
                error=str(exc),
            )
        except httpx.HTTPError as exc:
            return ExtractedDocument(
                url=url,
                title=None,
                text=None,
                content_type="unknown",
                status="http_error",
                extractor_used=None,
                fetched_at=fetched_at,
                error=str(exc),
            )
        except Exception as exc:
            return ExtractedDocument(
                url=url,
                title=None,
                text=None,
                content_type="unknown",
                status="error",
                extractor_used=None,
                fetched_at=fetched_at,
                error=str(exc),
            )

        if status_code >= 400:
            return ExtractedDocument(
                url=url,
                title=None,
                text=None,
                content_type=content_type,
                status="http_error",
                extractor_used=None,
                fetched_at=fetched_at,
                error=f"HTTP status {status_code}",
            )

        is_pdf = "pdf" in content_type or url.lower().split("?")[0].endswith(".pdf")
        if is_pdf:
            title, text, extractor_used, status = extract_pdf_content(body_bytes)
            return ExtractedDocument(
                url=url,
                title=title,
                text=text,
                content_type="application/pdf",
                status=status,
                extractor_used=extractor_used,
                fetched_at=fetched_at,
            )

        if "html" in content_type:
            html_text = body_bytes.decode("utf-8", errors="replace")
            title, text, extractor_used, status = extract_html_content(
                html_text, url=url
            )
            return ExtractedDocument(
                url=url,
                title=title,
                text=text,
                content_type=content_type,
                status=status,
                extractor_used=extractor_used,
                fetched_at=fetched_at,
            )

        return ExtractedDocument(
            url=url,
            title=None,
            text=None,
            content_type=content_type,
            status="unsupported_content_type",
            extractor_used=None,
            fetched_at=fetched_at,
        )
