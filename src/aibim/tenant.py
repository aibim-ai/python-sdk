"""AIBIM SDK tenant management client.

Manage tenant configuration, API keys, endpoints, and usage.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from aibim.client import AibimClient


class TenantClient:
    """Tenant management operations."""

    def __init__(self, client: AibimClient) -> None:
        self._client = client

    # ── Async methods ───────────────────────────────────────────────

    async def me(self) -> dict[str, Any]:
        """Get current tenant information.

        Returns:
            Tenant details dictionary.
        """
        return await self._client._get("/api/v1/tenant/me")

    async def get_config(self) -> dict[str, Any]:
        """Get tenant configuration.

        Returns:
            Tenant configuration dictionary.
        """
        return await self._client._get("/api/v1/tenant/config")

    async def update_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Update tenant configuration.

        Args:
            config: Configuration key-value pairs to update.

        Returns:
            Updated configuration dictionary.
        """
        return await self._client._put("/api/v1/tenant/config", json=config)

    async def get_detection_mode(self) -> dict[str, Any]:
        """Get current detection mode setting.

        Returns:
            Dict with mode field (e.g. 'monitor', 'enforce', 'learning').
        """
        return await self._client._get("/api/v1/tenant/detection-mode")

    async def set_detection_mode(self, mode: str) -> dict[str, Any]:
        """Set detection mode.

        Args:
            mode: Detection mode ('monitor', 'enforce', or 'learning').

        Returns:
            Updated detection mode dictionary.
        """
        return await self._client._put(
            "/api/v1/tenant/detection-mode",
            json={"mode": mode},
        )

    async def list_api_keys(self) -> list[dict[str, Any]]:
        """List all API keys for the tenant.

        Returns:
            List of API key dictionaries.
        """
        return await self._client._get("/api/v1/tenant/keys")

    async def create_api_key(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Create a new API key.

        Args:
            name: Human-readable name for the key.
            **kwargs: Additional options (scopes, expires_at, etc.).

        Returns:
            The created API key dictionary (includes the key value).
        """
        payload: dict[str, Any] = {"name": name, **kwargs}
        return await self._client._post("/api/v1/tenant/keys", json=payload)

    async def delete_api_key(self, key_id: str) -> None:
        """Delete an API key.

        Args:
            key_id: UUID of the API key to delete.
        """
        await self._client._delete(f"/api/v1/tenant/keys/{key_id}")

    async def get_usage(self) -> dict[str, Any]:
        """Get usage statistics for the tenant.

        Returns:
            Usage statistics dictionary.
        """
        return await self._client._get("/api/v1/tenant/usage")

    async def list_endpoints(self) -> list[dict[str, Any]]:
        """List all proxy endpoints for the tenant.

        Returns:
            List of endpoint dictionaries.
        """
        return await self._client._get("/api/v1/tenant/endpoints")

    async def create_endpoint(self, endpoint: dict[str, Any]) -> dict[str, Any]:
        """Create a new proxy endpoint.

        Args:
            endpoint: Endpoint definition dict with slug, name,
                      upstream_url, upstream_type, etc.

        Returns:
            The created endpoint dictionary.
        """
        return await self._client._post("/api/v1/tenant/endpoints", json=endpoint)

    # ── Sync methods ────────────────────────────────────────────────

    def me_sync(self) -> dict[str, Any]:
        """Get current tenant information (sync).

        Returns:
            Tenant details dictionary.
        """
        return self._client._get_sync("/api/v1/tenant/me")

    def get_config_sync(self) -> dict[str, Any]:
        """Get tenant configuration (sync).

        Returns:
            Tenant configuration dictionary.
        """
        return self._client._get_sync("/api/v1/tenant/config")

    def update_config_sync(self, config: dict[str, Any]) -> dict[str, Any]:
        """Update tenant configuration (sync).

        Args:
            config: Configuration key-value pairs to update.

        Returns:
            Updated configuration dictionary.
        """
        return self._client._put_sync("/api/v1/tenant/config", json=config)

    def get_detection_mode_sync(self) -> dict[str, Any]:
        """Get current detection mode setting (sync).

        Returns:
            Dict with mode field.
        """
        return self._client._get_sync("/api/v1/tenant/detection-mode")

    def set_detection_mode_sync(self, mode: str) -> dict[str, Any]:
        """Set detection mode (sync).

        Args:
            mode: Detection mode ('monitor', 'enforce', or 'learning').

        Returns:
            Updated detection mode dictionary.
        """
        return self._client._put_sync(
            "/api/v1/tenant/detection-mode",
            json={"mode": mode},
        )

    def list_api_keys_sync(self) -> list[dict[str, Any]]:
        """List all API keys for the tenant (sync).

        Returns:
            List of API key dictionaries.
        """
        return self._client._get_sync("/api/v1/tenant/keys")

    def create_api_key_sync(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Create a new API key (sync).

        Args:
            name: Human-readable name for the key.
            **kwargs: Additional options.

        Returns:
            The created API key dictionary.
        """
        payload: dict[str, Any] = {"name": name, **kwargs}
        return self._client._post_sync("/api/v1/tenant/keys", json=payload)

    def delete_api_key_sync(self, key_id: str) -> None:
        """Delete an API key (sync).

        Args:
            key_id: UUID of the API key to delete.
        """
        self._client._delete_sync(f"/api/v1/tenant/keys/{key_id}")

    def get_usage_sync(self) -> dict[str, Any]:
        """Get usage statistics for the tenant (sync).

        Returns:
            Usage statistics dictionary.
        """
        return self._client._get_sync("/api/v1/tenant/usage")

    def list_endpoints_sync(self) -> list[dict[str, Any]]:
        """List all proxy endpoints for the tenant (sync).

        Returns:
            List of endpoint dictionaries.
        """
        return self._client._get_sync("/api/v1/tenant/endpoints")

    def create_endpoint_sync(self, endpoint: dict[str, Any]) -> dict[str, Any]:
        """Create a new proxy endpoint (sync).

        Args:
            endpoint: Endpoint definition dict.

        Returns:
            The created endpoint dictionary.
        """
        return self._client._post_sync("/api/v1/tenant/endpoints", json=endpoint)
