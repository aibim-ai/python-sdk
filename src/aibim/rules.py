"""AIBIM SDK detection rules client.

Manage custom detection rules through the AIBIM API.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aibim.client import AibimClient


class RulesClient:
    """Detection rules management."""

    def __init__(self, client: AibimClient) -> None:
        self._client = client

    # ── Async methods ───────────────────────────────────────────────

    async def list(self) -> list[dict[str, Any]]:
        """List all detection rules.

        Returns:
            List of detection rule dictionaries.
        """
        return await self._client._get("/api/v1/rules")

    async def create(self, rule: dict[str, Any]) -> dict[str, Any]:
        """Create a new detection rule.

        Args:
            rule: Rule definition dict with keys like name, pattern,
                  severity, action, etc.

        Returns:
            The created rule dictionary.
        """
        return await self._client._post("/api/v1/rules", json=rule)

    async def delete(self, rule_id: str) -> None:
        """Delete a detection rule.

        Args:
            rule_id: UUID of the rule to delete.
        """
        await self._client._delete(f"/api/v1/rules/{rule_id}")

    # ── Sync methods ────────────────────────────────────────────────

    def list_sync(self) -> list[dict[str, Any]]:
        """List all detection rules (sync).

        Returns:
            List of detection rule dictionaries.
        """
        return self._client._get_sync("/api/v1/rules")

    def create_sync(self, rule: dict[str, Any]) -> dict[str, Any]:
        """Create a new detection rule (sync).

        Args:
            rule: Rule definition dict.

        Returns:
            The created rule dictionary.
        """
        return self._client._post_sync("/api/v1/rules", json=rule)

    def delete_sync(self, rule_id: str) -> None:
        """Delete a detection rule (sync).

        Args:
            rule_id: UUID of the rule to delete.
        """
        self._client._delete_sync(f"/api/v1/rules/{rule_id}")
