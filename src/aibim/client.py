"""AIBIM SDK core HTTP client.

Provides both async and sync interfaces to all AIBIM API endpoints.
Sub-clients (auth, rules, data, tenant, alerts) are lazily instantiated.
"""
from __future__ import annotations

from typing import Any, Optional

import httpx

from aibim.errors import AibimAuthError, AibimBlockedError, AibimError, AibimRateLimitError
from aibim.retry import RetryPolicy


def _parse_error_response(response: httpx.Response) -> None:
    """Parse an error response and raise the appropriate AibimError."""
    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = {}

    message = body.get("error", body.get("message", response.text or f"HTTP {status}"))

    if status == 401:
        raise AibimAuthError(message=message)

    if status == 403:
        raise AibimBlockedError(
            message=message,
            risk_score=body.get("risk_score", 0.0),
            matched_rules=body.get("matched_rules", []),
            correlation_id=body.get("correlation_id"),
        )

    if status == 429:
        retry_after_raw = response.headers.get("retry-after")
        retry_after: float | None = None
        if retry_after_raw is not None:
            try:
                retry_after = float(retry_after_raw)
            except (ValueError, TypeError):
                pass
        raise AibimRateLimitError(message=message, retry_after=retry_after)

    if status >= 400:
        raise AibimError(message=message, status_code=status)


class AibimClient:
    """Core AIBIM HTTP client with async and sync support.

    Usage::

        async with AibimClient(base_url="https://proxy.aibim.ai", api_key="aibim-key-xxx") as client:
            events = await client.data.events()

        # Or sync:
        client = AibimClient(base_url="https://proxy.aibim.ai", api_key="aibim-key-xxx")
        events = client.data.events_sync()
        client.close_sync()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._retry = RetryPolicy(max_retries=max_retries)
        self._http: Optional[httpx.AsyncClient] = None
        self._http_sync: Optional[httpx.Client] = None

        # Lazy sub-client instances
        self._auth: Optional[Any] = None
        self._rules: Optional[Any] = None
        self._data: Optional[Any] = None
        self._tenant: Optional[Any] = None
        self._alerts: Optional[Any] = None

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._http

    def _get_sync_client(self) -> httpx.Client:
        if self._http_sync is None or self._http_sync.is_closed:
            self._http_sync = httpx.Client(base_url=self._base_url, timeout=self._timeout)
        return self._http_sync

    def _headers(self) -> dict[str, str]:
        """Build common request headers."""
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    # ── Async request helpers ───────────────────────────────────────

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an HTTP request with retry and error handling (async)."""
        headers = {**self._headers(), **kwargs.pop("headers", {})}

        async def _do() -> httpx.Response:
            client = self._get_async_client()
            response = await client.request(method, path, headers=headers, **kwargs)
            if response.status_code >= 400:
                # For retryable statuses, raise HTTPStatusError so retry policy catches them
                if response.status_code in (429, 500, 502, 503, 504):
                    response.raise_for_status()
                # For non-retryable errors, raise AIBIM-specific errors immediately
                _parse_error_response(response)
            return response

        return await self._retry.execute(_do)

    async def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """GET request, return parsed JSON body."""
        response = await self._request("GET", path, params=params)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    async def _post(self, path: str, json: Optional[Any] = None) -> Any:
        """POST request, return parsed JSON body."""
        response = await self._request("POST", path, json=json)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    async def _put(self, path: str, json: Optional[Any] = None) -> Any:
        """PUT request, return parsed JSON body."""
        response = await self._request("PUT", path, json=json)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    async def _delete(self, path: str) -> None:
        """DELETE request."""
        await self._request("DELETE", path)

    # ── Sync request helpers ────────────────────────────────────────

    def _request_sync(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an HTTP request with retry and error handling (sync)."""
        headers = {**self._headers(), **kwargs.pop("headers", {})}

        def _do() -> httpx.Response:
            client = self._get_sync_client()
            response = client.request(method, path, headers=headers, **kwargs)
            if response.status_code >= 400:
                if response.status_code in (429, 500, 502, 503, 504):
                    response.raise_for_status()
                _parse_error_response(response)
            return response

        return self._retry.execute_sync(_do)

    def _get_sync(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """GET request (sync), return parsed JSON body."""
        response = self._request_sync("GET", path, params=params)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    def _post_sync(self, path: str, json: Optional[Any] = None) -> Any:
        """POST request (sync), return parsed JSON body."""
        response = self._request_sync("POST", path, json=json)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    def _put_sync(self, path: str, json: Optional[Any] = None) -> Any:
        """PUT request (sync), return parsed JSON body."""
        response = self._request_sync("PUT", path, json=json)
        body = response.json()
        return body.get("data", body) if isinstance(body, dict) and "data" in body else body

    def _delete_sync(self, path: str) -> None:
        """DELETE request (sync)."""
        self._request_sync("DELETE", path)

    # ── Sub-clients (lazy) ──────────────────────────────────────────

    @property
    def auth(self) -> Any:
        """Authentication sub-client."""
        if self._auth is None:
            from aibim.auth import AuthClient
            self._auth = AuthClient(self)
        return self._auth

    @property
    def rules(self) -> Any:
        """Detection rules sub-client."""
        if self._rules is None:
            from aibim.rules import RulesClient
            self._rules = RulesClient(self)
        return self._rules

    @property
    def data(self) -> Any:
        """Data/analytics sub-client."""
        if self._data is None:
            from aibim.data import DataClient
            self._data = DataClient(self)
        return self._data

    @property
    def tenant(self) -> Any:
        """Tenant management sub-client."""
        if self._tenant is None:
            from aibim.tenant import TenantClient
            self._tenant = TenantClient(self)
        return self._tenant

    @property
    def alerts(self) -> Any:
        """Alerts sub-client."""
        if self._alerts is None:
            from aibim.alerts import AlertsClient
            self._alerts = AlertsClient(self)
        return self._alerts

    # ── Lifecycle ───────────────────────────────────────────────────

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()

    def close_sync(self) -> None:
        """Close the underlying sync HTTP client."""
        if self._http_sync is not None and not self._http_sync.is_closed:
            self._http_sync.close()

    async def __aenter__(self) -> AibimClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __enter__(self) -> AibimClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close_sync()
