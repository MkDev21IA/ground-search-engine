from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import re
from typing import Any, Iterator
import httpx

from .models import Citation


MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)")


def extract_citations(text: str) -> list[Citation]:
    """Extracts all inline markdown citations `[Label](URL)` present in the text."""
    citations: list[Citation] = []
    seen: set[tuple[str, str]] = set()

    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        label = match.group(1).strip()
        url = match.group(2).strip()
        if (label, url) not in seen:
            seen.add((label, url))
            citations.append(Citation(url=url, label=label))

    return citations


@dataclass
class LLMConfig:
    """Universal configuration for OpenAI-compatible providers (Gemini, OpenAI, LM Studio, Ollama)."""

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )
    api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL", "gemini-2.5-flash")
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )
    timeout: float = 60.0


class LLMClient:
    """Universal HTTP client implementing the OpenAI Chat Completions specification."""

    def __init__(
        self,
        config: LLMConfig | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = config or LLMConfig()
        self._http_client = http_client
        self._owns_client = http_client is None

    def _get_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = httpx.Client(timeout=self.config.timeout)
        return self._http_client

    def generate(self, messages: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
        """Sends chat messages to /chat/completions and returns response content and usage statistics."""
        client = self._get_client()
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
        }

        response = client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(
                f"LLM API request failed [{response.status_code}] on {url}: {response.text}"
            )

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"LLM response contained no choices: {data}")

        answer = choices[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        return answer, usage

    def stream_generate(
        self, messages: list[dict[str, str]]
    ) -> Iterator[dict[str, Any]]:
        """Sends chat messages with stream=True and yields token chunks and usage.

        Yields dicts with:
        - {"type": "token", "content": delta_text}
        - {"type": "usage", "usage": usage_dict}
        """
        client = self._get_client()
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.status_code >= 400:
                body = response.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"LLM API request failed [{response.status_code}] on {url}: {body}"
                )

            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[len("data: "):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except Exception:
                    continue

                if "usage" in chunk and chunk["usage"]:
                    yield {"type": "usage", "usage": chunk["usage"]}

                choices = chunk.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield {"type": "token", "content": token}

    def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def __enter__(self) -> LLMClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
