"""AIBIM SDK retry logic with exponential backoff and jitter."""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Callable, TypeVar

import httpx

T = TypeVar("T")

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class RetryPolicy:
    """Retry policy with exponential backoff and jitter.

    Retries on transient HTTP errors (429, 5xx) with exponential
    backoff. Respects the ``Retry-After`` header for 429 responses.
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        max_backoff_secs: float = 30.0,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff_secs = max_backoff_secs

    def _compute_delay(self, attempt: int, response: httpx.Response | None = None) -> float:
        """Compute delay for the next retry attempt.

        If the response contains a ``Retry-After`` header (common for 429),
        that value is used. Otherwise exponential backoff with jitter is applied.
        """
        if response is not None:
            retry_after = response.headers.get("retry-after")
            if retry_after is not None:
                try:
                    return min(float(retry_after), self.max_backoff_secs)
                except (ValueError, TypeError):
                    pass

        delay = self.backoff_factor * (2 ** attempt)
        jitter = random.uniform(0, delay * 0.5)  # noqa: S311
        return min(delay + jitter, self.max_backoff_secs)

    @staticmethod
    def _is_retryable(exc: Exception) -> tuple[bool, httpx.Response | None]:
        """Determine if an exception is retryable."""
        if isinstance(exc, httpx.HTTPStatusError):
            if exc.response.status_code in _RETRYABLE_STATUSES:
                return True, exc.response
        if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout)):
            return True, None
        return False, None

    async def execute(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``fn`` with retry logic (async version).

        Args:
            fn: An async callable to execute.
            *args: Positional arguments forwarded to *fn*.
            **kwargs: Keyword arguments forwarded to *fn*.

        Returns:
            The return value of *fn*.

        Raises:
            The last exception if all retries are exhausted.
        """
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                retryable, response = self._is_retryable(exc)
                if not retryable or attempt >= self.max_retries:
                    raise
                last_exc = exc
                delay = self._compute_delay(attempt, response)
                await asyncio.sleep(delay)

        if last_exc is not None:
            raise last_exc  # pragma: no cover

    def execute_sync(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``fn`` with retry logic (sync version).

        Args:
            fn: A sync callable to execute.
            *args: Positional arguments forwarded to *fn*.
            **kwargs: Keyword arguments forwarded to *fn*.

        Returns:
            The return value of *fn*.

        Raises:
            The last exception if all retries are exhausted.
        """
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                retryable, response = self._is_retryable(exc)
                if not retryable or attempt >= self.max_retries:
                    raise
                last_exc = exc
                delay = self._compute_delay(attempt, response)
                time.sleep(delay)

        if last_exc is not None:
            raise last_exc  # pragma: no cover
