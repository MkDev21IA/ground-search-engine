from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Query, Result


class SearchAdapter(ABC):
    """Translates a canonical Query into a specific engine call and normalizes
    the engine response back into a list of canonical Result objects.

    A failure (timeout, WAF blocking, rate limit, etc.) must not raise an exception:
    it should yield a Result with `error` populated so that an individual failing
    query does not abort the entire batch (see decisions/0006).
    """

    name: str

    @abstractmethod
    def search(self, query: Query) -> list[Result]: ...


def error_result(engine: str, fetched_at: str, exc: Exception) -> Result:
    """Standard error Result returned when an engine call fails,
    keeping batch execution alive rather than terminating the process."""
    return Result(
        engine=engine,
        url="",
        title="",
        snippet="",
        rank=0,
        fetched_at=fetched_at,
        error=str(exc),
    )
