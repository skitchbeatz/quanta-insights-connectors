"""Sourcewhale API client — async httpx client for the Sourcewhale REST API.

PROVISIONAL: Sourcewhale's API documentation is not publicly available.
This client's endpoints, request/response shapes, and authentication method
are INFERRED from common outreach platform patterns (Outreach.io, Salesloft,
Apollo) and Sourcewhale's known feature set.

ALL endpoint paths and payload structures MUST be verified against the real
API once documentation is obtained from the Sourcewhale admin console.

Assumed auth: API key via Authorization header (Bearer token or X-Api-Key).
Assumed base URL: https://api.sourcewhale.com/v1 (unverified).

This client is ready to use once:
1. API documentation is located
2. Endpoint paths are verified/corrected
3. An API key is generated and stored in Vault
"""

from typing import Any

import httpx

from ...logging import get_logger
from ..base import APIError, AuthenticationError

logger = get_logger(__name__)

# PROVISIONAL: Base URL is unverified — update when API docs are obtained
BASE_URL = "https://api.sourcewhale.com/v1"

# Default timeout for API requests (seconds)
DEFAULT_TIMEOUT = 30.0

# Maximum retries for transient failures
MAX_RETRIES = 3


class SourcewhaleAPIClient:
    """Async HTTP client for the Sourcewhale API.

    PROVISIONAL: All endpoint paths and payload structures are inferred
    and must be verified against the real API documentation.

    Usage:
        async with SourcewhaleAPIClient(api_key="...") as client:
            sequences = await client.list_sequences()
            contacts = await client.list_contacts(sequence_id="seq_123")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Sourcewhale API client.

        Args:
            api_key: Sourcewhale API key (from admin console or Vault)
            base_url: API base URL (override for testing or when real URL is confirmed)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "SourcewhaleAPIClient":
        """Create the httpx async client on context manager entry."""
        # PROVISIONAL: Auth header format may differ — verify with real API
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "quanta-insights-connectors/1.0",
            },
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Close the httpx async client on context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the httpx client, raising if not initialized."""
        if self._client is None:
            raise RuntimeError(
                "SourcewhaleAPIClient must be used as an async context manager: "
                "async with SourcewhaleAPIClient(...) as client:"
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request with error handling.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API path (e.g. "/sequences")
            params: Query parameters
            json_body: JSON request body (for POST/PUT)

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If API key is invalid (401/403)
            APIError: If the API returns an error response
        """
        url = path.lstrip("/")

        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_body,
                )

                # Handle error responses
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        "Sourcewhale API key is invalid or expired. "
                        "Check the API key in Vault at "
                        "secret/business/quanta-insights/sourcewhale/"
                    )

                if response.status_code == 429:
                    logger.warning(
                        "Sourcewhale API rate limited",
                        attempt=attempt,
                    )
                    if attempt < MAX_RETRIES:
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise APIError("Sourcewhale API rate limited after max retries")

                if response.status_code >= 500:
                    logger.warning(
                        "Sourcewhale API server error",
                        status_code=response.status_code,
                        attempt=attempt,
                    )
                    if attempt < MAX_RETRIES:
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise APIError(
                        f"Sourcewhale API server error: {response.status_code}"
                    )

                if response.status_code >= 400:
                    error_body = response.text
                    raise APIError(
                        f"Sourcewhale API error {response.status_code}: {error_body}"
                    )

                # Parse and return successful response
                return response.json()  # type: ignore[no-any-return]

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(
                    "Sourcewhale API connection error",
                    error=str(e),
                    attempt=attempt,
                )
                if attempt < MAX_RETRIES:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue

        raise APIError(
            f"Sourcewhale API request failed after {MAX_RETRIES} retries: {last_error}"
        )

    # ── Sequences ─────────────────────────────────────────────────────────
    # PROVISIONAL: Endpoint paths are inferred

    async def list_sequences(
        self,
        status: str | None = None,
        tag: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List outreach sequences/campaigns.

        PROVISIONAL: Endpoint path and params are inferred.

        Args:
            status: Filter by status (active, paused, completed, draft)
            tag: Filter by tag
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Dict with 'sequences' and 'total' keys
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if tag:
            params["tag"] = tag

        logger.info("Fetching Sourcewhale sequences", params=params)
        return await self._request("GET", "/sequences", params=params)

    async def get_sequence(self, sequence_id: str) -> dict[str, Any]:
        """Get a specific sequence with stats.

        PROVISIONAL: Endpoint path is inferred.

        Args:
            sequence_id: The sequence ID

        Returns:
            Sequence dict with steps and stats
        """
        logger.info("Fetching Sourcewhale sequence", sequence_id=sequence_id)
        return await self._request("GET", f"/sequences/{sequence_id}")

    async def get_sequence_stats(self, sequence_id: str) -> dict[str, Any]:
        """Get performance stats for a sequence.

        PROVISIONAL: Endpoint path is inferred. May be part of get_sequence response.

        Args:
            sequence_id: The sequence ID

        Returns:
            Stats dict with reply_rate, open_rate, etc.
        """
        logger.info("Fetching Sourcewhale sequence stats", sequence_id=sequence_id)
        return await self._request("GET", f"/sequences/{sequence_id}/stats")

    # ── Contacts ──────────────────────────────────────────────────────────
    # PROVISIONAL: Endpoint paths are inferred

    async def list_contacts(
        self,
        sequence_id: str | None = None,
        status: str | None = None,
        email: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List contacts with optional filters.

        PROVISIONAL: Endpoint path and params are inferred.

        Args:
            sequence_id: Filter by sequence
            status: Filter by outreach status
            email: Filter by exact email
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Dict with 'contacts' and 'total' keys
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if sequence_id:
            params["sequence_id"] = sequence_id
        if status:
            params["status"] = status
        if email:
            params["email"] = email

        logger.info("Fetching Sourcewhale contacts", params=params)
        return await self._request("GET", "/contacts", params=params)

    async def get_contact_history(self, contact_id: str) -> dict[str, Any]:
        """Get outreach history for a contact.

        PROVISIONAL: Endpoint path is inferred.

        Args:
            contact_id: The contact ID

        Returns:
            Dict with 'events' list and 'total_events'
        """
        logger.info("Fetching Sourcewhale contact history", contact_id=contact_id)
        return await self._request("GET", f"/contacts/{contact_id}/history")

    # ── Analytics ─────────────────────────────────────────────────────────
    # PROVISIONAL: Endpoint path is inferred

    async def get_analytics(
        self,
        period: str = "last_30_days",
    ) -> dict[str, Any]:
        """Get aggregated campaign analytics.

        PROVISIONAL: Endpoint path and params are inferred.

        Args:
            period: Time period (last_7_days, last_30_days, last_90_days, all_time)

        Returns:
            Analytics dict with overall metrics and top sequences
        """
        params: dict[str, Any] = {"period": period}
        logger.info("Fetching Sourcewhale analytics", period=period)
        return await self._request("GET", "/analytics", params=params)

    # ── Health Check ──────────────────────────────────────────────────────

    async def validate_api_key(self) -> bool:
        """Validate the API key by making a lightweight request.

        PROVISIONAL: Uses /sequences as the validation endpoint.

        Returns:
            True if the API key is valid

        Raises:
            AuthenticationError: If the API key is invalid
        """
        try:
            await self.list_sequences(limit=1)
            return True
        except AuthenticationError:
            raise
        except APIError as e:
            logger.error("Sourcewhale API key validation failed", error=str(e))
            raise AuthenticationError(
                f"Failed to validate Sourcewhale API key: {e}"
            ) from e
