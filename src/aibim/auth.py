"""AIBIM SDK authentication client.

Handles login, registration, token refresh, and validation
against the AIBIM SaaS auth endpoints.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from aibim.client import AibimClient


class AuthClient:
    """Authentication operations against the AIBIM API."""

    def __init__(self, client: AibimClient) -> None:
        self._client = client

    # ── Async methods ───────────────────────────────────────────────

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate and obtain access/refresh tokens.

        Args:
            email: User email address.
            password: User password.

        Returns:
            Dict containing access_token, refresh_token, and user info.
        """
        return await self._client._post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )

    async def register(self, email: str, password: str, tenant_name: str) -> dict[str, Any]:
        """Register a new user and tenant.

        Args:
            email: User email address.
            password: User password.
            tenant_name: Name for the new tenant organization.

        Returns:
            Dict containing the created user and tenant info.
        """
        return await self._client._post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "tenant_name": tenant_name},
        )

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token from a previous login.

        Returns:
            Dict containing a new access_token and refresh_token.
        """
        return await self._client._post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

    async def me(self) -> dict[str, Any]:
        """Get current authenticated user information.

        Returns:
            Dict containing user profile and tenant info.
        """
        return await self._client._get("/api/v1/auth/me")

    async def validate(self) -> dict[str, Any]:
        """Validate the current authentication token.

        Returns:
            Dict containing user info if the token is valid.
        """
        return await self._client._get("/api/v1/auth/validate")

    # ── Sync methods ────────────────────────────────────────────────

    def login_sync(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate and obtain access/refresh tokens (sync).

        Args:
            email: User email address.
            password: User password.

        Returns:
            Dict containing access_token, refresh_token, and user info.
        """
        return self._client._post_sync(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )

    def register_sync(self, email: str, password: str, tenant_name: str) -> dict[str, Any]:
        """Register a new user and tenant (sync).

        Args:
            email: User email address.
            password: User password.
            tenant_name: Name for the new tenant organization.

        Returns:
            Dict containing the created user and tenant info.
        """
        return self._client._post_sync(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "tenant_name": tenant_name},
        )

    def refresh_sync(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token (sync).

        Args:
            refresh_token: The refresh token from a previous login.

        Returns:
            Dict containing a new access_token and refresh_token.
        """
        return self._client._post_sync(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

    def me_sync(self) -> dict[str, Any]:
        """Get current authenticated user information (sync).

        Returns:
            Dict containing user profile and tenant info.
        """
        return self._client._get_sync("/api/v1/auth/me")

    def validate_sync(self) -> dict[str, Any]:
        """Validate the current authentication token (sync).

        Returns:
            Dict containing user info if the token is valid.
        """
        return self._client._get_sync("/api/v1/auth/validate")
