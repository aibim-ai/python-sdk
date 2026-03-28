"""AIBIM SDK error types.

All AIBIM-specific errors inherit from AibimError, making it easy
to catch any SDK error with a single except clause.
"""
from __future__ import annotations


class AibimError(Exception):
    """Base AIBIM error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AibimBlockedError(AibimError):
    """Request blocked by AIBIM detection pipeline."""

    def __init__(
        self,
        message: str,
        risk_score: float,
        matched_rules: list[str],
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(message, status_code=403)
        self.risk_score = risk_score
        self.matched_rules = matched_rules
        self.correlation_id = correlation_id

    def __repr__(self) -> str:
        return (
            f"AibimBlockedError(risk_score={self.risk_score}, "
            f"matched_rules={self.matched_rules!r}, "
            f"correlation_id={self.correlation_id!r})"
        )


class AibimAuthError(AibimError):
    """Authentication or authorization error."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class AibimRateLimitError(AibimError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return f"AibimRateLimitError(retry_after={self.retry_after})"
