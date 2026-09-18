from __future__ import annotations

from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import httpx

DEFAULT_USER_AGENT = (
    "LLMSearchBot/0.1 (+https://github.com/MkDev21IA/grounded-search-engine)"
)


class RobotsDisallowedError(Exception):
    """Exception raised when robots.txt disallows crawling of the target URL."""


class RobotsChecker:
    """Manages fetching, parsing, and caching of robots.txt rules per domain."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self.user_agent = user_agent
        self._parsers: dict[str, RobotFileParser] = {}

    def is_allowed(self, url: str, client: httpx.Client | None = None) -> bool:
        parsed = urlsplit(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self._parsers:
            parser = RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            try:
                if client:
                    resp = client.get(
                        robots_url,
                        headers={"User-Agent": self.user_agent},
                        timeout=5.0,
                        follow_redirects=True,
                    )
                    if resp.status_code == 200:
                        parser.parse(resp.text.splitlines())
                    else:
                        parser.allow_all = True
                else:
                    with httpx.Client() as local_client:
                        resp = local_client.get(
                            robots_url,
                            headers={"User-Agent": self.user_agent},
                            timeout=5.0,
                            follow_redirects=True,
                        )
                        if resp.status_code == 200:
                            parser.parse(resp.text.splitlines())
                        else:
                            parser.allow_all = True
            except Exception:
                parser.allow_all = True

            self._parsers[domain] = parser

        parser = self._parsers[domain]
        return parser.can_fetch(self.user_agent, url)


def fetch_resource(
    url: str,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = 10.0,
    client: httpx.Client | None = None,
    robots_checker: RobotsChecker | None = None,
) -> tuple[int, str, bytes, dict[str, str]]:
    """Fetches an HTTP resource respecting robots.txt and an honest User-Agent.

    Returns: (status_code, content_type, body_bytes, headers)
    """
    checker = robots_checker or RobotsChecker(user_agent=user_agent)
    if not checker.is_allowed(url, client=client):
        raise RobotsDisallowedError(f"Access to URL {url} disallowed by robots.txt")

    headers = {"User-Agent": user_agent}

    def _do_get(cli: httpx.Client) -> httpx.Response:
        return cli.get(url, headers=headers, timeout=timeout, follow_redirects=True)

    if client:
        response = _do_get(client)
    else:
        with httpx.Client() as local_client:
            response = _do_get(local_client)

    content_type_header = response.headers.get("content-type", "")
    content_type = content_type_header.split(";")[0].strip().lower()

    return (
        response.status_code,
        content_type,
        response.content,
        dict(response.headers),
    )
