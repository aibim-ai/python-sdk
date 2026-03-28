"""AIBIM SDK alerts client.

Manage alerts, alert rules, and retrieve alert statistics.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aibim.client import AibimClient


class AlertsClient:
    """Alert management operations."""

    def __init__(self, client: AibimClient) -> None:
        self._client = client

    # ── Async methods ───────────────────────────────────────────────

    async def list(self, **params: Any) -> list[dict[str, Any]]:
        """List alerts.

        Args:
            **params: Query parameters (limit, offset, severity,
                      status, start_date, end_date, etc.).

        Returns:
            List of alert dictionaries.
        """
        return await self._client._get("/api/v1/alerts", params=params or None)

    async def list_rules(self) -> list[dict[str, Any]]:
        """List alert rules.

        Returns:
            List of alert rule dictionaries.
        """
        return await self._client._get("/api/v1/alerts/rules")

    async def create_rule(self, rule: dict[str, Any]) -> dict[str, Any]:
        """Create a new alert rule.

        Args:
            rule: Alert rule definition dict with keys like name,
                  condition, severity, action, etc.

        Returns:
            The created alert rule dictionary.
        """
        return await self._client._post("/api/v1/alerts/rules", json=rule)

    async def stats(self) -> dict[str, Any]:
        """Get alert statistics.

        Returns:
            Dict with alert counts by severity, status, etc.
        """
        return await self._client._get("/api/v1/alerts/stats")

    # ── Sync methods ────────────────────────────────────────────────

    def list_sync(self, **params: Any) -> list[dict[str, Any]]:
        """List alerts (sync).

        Args:
            **params: Query parameters.

        Returns:
            List of alert dictionaries.
        """
        return self._client._get_sync("/api/v1/alerts", params=params or None)

    def list_rules_sync(self) -> list[dict[str, Any]]:
        """List alert rules (sync).

        Returns:
            List of alert rule dictionaries.
        """
        return self._client._get_sync("/api/v1/alerts/rules")

    def create_rule_sync(self, rule: dict[str, Any]) -> dict[str, Any]:
        """Create a new alert rule (sync).

        Args:
            rule: Alert rule definition dict.

        Returns:
            The created alert rule dictionary.
        """
        return self._client._post_sync("/api/v1/alerts/rules", json=rule)

    def stats_sync(self) -> dict[str, Any]:
        """Get alert statistics (sync).

        Returns:
            Dict with alert counts by severity, status, etc.
        """
        return self._client._get_sync("/api/v1/alerts/stats")
