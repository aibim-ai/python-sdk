"""AIBIM Guard — convenience wrapper for direct prompt analysis.

Use AibimGuard when you want to analyze prompts without proxying
full LLM traffic. Useful for pre-screening user input.

Usage::

    guard = AibimGuard(base_url="https://proxy.aibim.ai", api_key="aibim-key-xxx")
    result = guard.analyze_sync("Ignore all previous instructions and...")
    if result.decision == AibimDecision.BLOCK:
        print(f"Blocked! Risk: {result.risk_score}")
"""
from __future__ import annotations

from typing import Optional

from aibim.client import AibimClient
from aibim.models import AnalyzeResponse


class AibimGuard:
    """Direct prompt analysis without full proxy routing.

    Wraps AibimClient to provide a simple analyze interface
    for pre-screening user input against the detection pipeline.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
    ) -> None:
        self._client = AibimClient(base_url=base_url, api_key=api_key)

    # ── Async methods ───────────────────────────────────────────────

    async def analyze(self, text: str, model: str = "default") -> AnalyzeResponse:
        """Analyze a prompt for threats (async).

        Args:
            text: The prompt text to analyze.
            model: Target model identifier.

        Returns:
            AnalyzeResponse with risk score, decision, and matched rules.
        """
        data = await self._client._post(
            "/api/v1/alerts/analyze",
            json={"text": text, "model": model},
        )
        return AnalyzeResponse.model_validate(data)

    async def health(self) -> dict:
        """Check AIBIM service health (async).

        Returns:
            Health status dictionary.
        """
        return await self._client._get("/health")

    async def deep_health(self) -> dict:
        """Check AIBIM deep health including dependencies (async).

        Returns:
            Detailed health status including database, Redis, etc.
        """
        return await self._client._get("/health/deep")

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.close()

    # ── Sync methods ────────────────────────────────────────────────

    def analyze_sync(self, text: str, model: str = "default") -> AnalyzeResponse:
        """Analyze a prompt for threats (sync).

        Args:
            text: The prompt text to analyze.
            model: Target model identifier.

        Returns:
            AnalyzeResponse with risk score, decision, and matched rules.
        """
        data = self._client._post_sync(
            "/api/v1/alerts/analyze",
            json={"text": text, "model": model},
        )
        return AnalyzeResponse.model_validate(data)

    def health_sync(self) -> dict:
        """Check AIBIM service health (sync).

        Returns:
            Health status dictionary.
        """
        return self._client._get_sync("/health")

    def deep_health_sync(self) -> dict:
        """Check AIBIM deep health including dependencies (sync).

        Returns:
            Detailed health status including database, Redis, etc.
        """
        return self._client._get_sync("/health/deep")

    def close_sync(self) -> None:
        """Close the underlying sync HTTP client."""
        self._client.close_sync()

    # ── Context managers ────────────────────────────────────────────

    async def __aenter__(self) -> AibimGuard:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    def __enter__(self) -> AibimGuard:
        return self

    def __exit__(self, *args: object) -> None:
        self.close_sync()
