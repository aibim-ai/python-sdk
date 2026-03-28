"""AIBIM SDK data and analytics client.

Access detection events, real-time stats, benchmarks, compliance,
trust scores, threat intelligence, and DLP events.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from aibim.client import AibimClient


class DataClient:
    """Data and analytics operations."""

    def __init__(self, client: AibimClient) -> None:
        self._client = client

    # ── Async methods ───────────────────────────────────────────────

    async def events(self, **params: Any) -> list[dict[str, Any]]:
        """List detection events.

        Args:
            **params: Query parameters (limit, offset, severity,
                      start_date, end_date, etc.).

        Returns:
            List of detection event dictionaries.
        """
        return await self._client._get("/api/v1/data/events", params=params or None)

    async def realtime_stats(self) -> dict[str, Any]:
        """Get real-time detection statistics.

        Returns:
            Dict with current request rate, block rate, avg latency, etc.
        """
        return await self._client._get("/api/v1/data/stats/realtime")

    async def benchmarks(self) -> list[dict[str, Any]]:
        """List benchmark results by model.

        Returns:
            List of model benchmark score dictionaries.
        """
        return await self._client._get("/api/v1/data/benchmarks/models")

    async def compliance(self) -> list[dict[str, Any]]:
        """List compliance framework status.

        Returns:
            List of compliance framework dictionaries with scores.
        """
        return await self._client._get("/api/v1/data/compliance/frameworks")

    async def trust_agents(self) -> list[dict[str, Any]]:
        """List agent trust scores.

        Returns:
            List of agent trust score dictionaries.
        """
        return await self._client._get("/api/v1/data/trust/agents")

    async def threat_feed(self) -> list[dict[str, Any]]:
        """Get threat intelligence feed.

        Returns:
            List of threat intelligence entries.
        """
        return await self._client._get("/api/v1/data/threat-intel/feed")

    async def dlp_events(self) -> list[dict[str, Any]]:
        """List DLP (Data Loss Prevention) events.

        Returns:
            List of DLP event dictionaries.
        """
        return await self._client._get("/api/v1/data/dlp/events")

    # ── Sync methods ────────────────────────────────────────────────

    def events_sync(self, **params: Any) -> list[dict[str, Any]]:
        """List detection events (sync).

        Args:
            **params: Query parameters.

        Returns:
            List of detection event dictionaries.
        """
        return self._client._get_sync("/api/v1/data/events", params=params or None)

    def realtime_stats_sync(self) -> dict[str, Any]:
        """Get real-time detection statistics (sync).

        Returns:
            Dict with current request rate, block rate, avg latency, etc.
        """
        return self._client._get_sync("/api/v1/data/stats/realtime")

    def benchmarks_sync(self) -> list[dict[str, Any]]:
        """List benchmark results by model (sync).

        Returns:
            List of model benchmark score dictionaries.
        """
        return self._client._get_sync("/api/v1/data/benchmarks/models")

    def compliance_sync(self) -> list[dict[str, Any]]:
        """List compliance framework status (sync).

        Returns:
            List of compliance framework dictionaries with scores.
        """
        return self._client._get_sync("/api/v1/data/compliance/frameworks")

    def trust_agents_sync(self) -> list[dict[str, Any]]:
        """List agent trust scores (sync).

        Returns:
            List of agent trust score dictionaries.
        """
        return self._client._get_sync("/api/v1/data/trust/agents")

    def threat_feed_sync(self) -> list[dict[str, Any]]:
        """Get threat intelligence feed (sync).

        Returns:
            List of threat intelligence entries.
        """
        return self._client._get_sync("/api/v1/data/threat-intel/feed")

    def dlp_events_sync(self) -> list[dict[str, Any]]:
        """List DLP (Data Loss Prevention) events (sync).

        Returns:
            List of DLP event dictionaries.
        """
        return self._client._get_sync("/api/v1/data/dlp/events")
