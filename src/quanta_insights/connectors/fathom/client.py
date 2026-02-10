"""Fathom API client — async httpx client for the Fathom REST API.

Base URL: https://api.fathom.ai/external/v1
Auth: X-Api-Key header
Rate limits: RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset headers
Pagination: Cursor-based (next_cursor)

This client is ready to use once an API key is provided. It handles:
- Authentication via X-Api-Key header
- Rate limit tracking from response headers
- Cursor-based pagination
- Structured error handling
- Automatic retries on transient failures

Reference: https://developers.fathom.ai/api-reference
"""

from typing import Any

import httpx

from ...logging import get_logger
from ..base import APIError, AuthenticationError

logger = get_logger(__name__)

# Fathom API base URL
BASE_URL = "https://api.fathom.ai/external/v1"

# Default timeout for API requests (seconds)
DEFAULT_TIMEOUT = 30.0

# Maximum retries for transient failures
MAX_RETRIES = 3


class RateLimitInfo:
    """Tracks rate limit state from Fathom API response headers."""

    def __init__(self) -> None:
        self.limit: int | None = None
        self.remaining: int | None = None
        self.reset: float | None = None

    def update_from_headers(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        if "RateLimit-Limit" in headers:
            self.limit = int(headers["RateLimit-Limit"])
        if "RateLimit-Remaining" in headers:
            self.remaining = int(headers["RateLimit-Remaining"])
        if "RateLimit-Reset" in headers:
            self.reset = float(headers["RateLimit-Reset"])

    @property
    def is_exhausted(self) -> bool:
        """Check if rate limit is exhausted."""
        return self.remaining is not None and self.remaining <= 0

    def __repr__(self) -> str:
        return f"RateLimitInfo(limit={self.limit}, remaining={self.remaining}, reset={self.reset})"


class FathomAPIClient:
    """Async HTTP client for the Fathom API.

    Usage:
        async with FathomAPIClient(api_key="...") as client:
            meetings = await client.list_meetings()
            summary = await client.get_recording_summary("rec_123")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Fathom API client.

        Args:
            api_key: Fathom API key (from settings page or Vault)
            base_url: API base URL (override for testing)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limit = RateLimitInfo()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "FathomAPIClient":
        """Create the httpx async client on context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-Api-Key": self.api_key,
                "Accept": "application/json",
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
                "FathomAPIClient must be used as an async context manager: "
                "async with FathomAPIClient(...) as client:"
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request with error handling and rate limit tracking.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API path (e.g. "/meetings")
            params: Query parameters
            json_body: JSON request body (for POST/PUT)

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If API key is invalid (401)
            APIError: If the API returns an error response
        """
        url = path.lstrip("/")

        # Check rate limit before making request
        if self.rate_limit.is_exhausted:
            logger.warning(
                "Fathom API rate limit exhausted",
                reset=self.rate_limit.reset,
            )
            raise APIError(
                f"Fathom API rate limit exhausted. Resets at: {self.rate_limit.reset}"
            )

        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_body,
                )

                # Update rate limit info from response headers
                self.rate_limit.update_from_headers(response.headers)

                # Handle error responses
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Fathom API key is invalid or expired. "
                        "Check the API key in Vault at secret/business/quanta-insights/fathom/"
                    )

                if response.status_code == 429:
                    logger.warning(
                        "Fathom API rate limited",
                        attempt=attempt,
                        rate_limit=repr(self.rate_limit),
                    )
                    if attempt < MAX_RETRIES:
                        # Retry after a short delay (exponential backoff)
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise APIError("Fathom API rate limited after max retries")

                if response.status_code >= 500:
                    logger.warning(
                        "Fathom API server error",
                        status_code=response.status_code,
                        attempt=attempt,
                    )
                    if attempt < MAX_RETRIES:
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise APIError(
                        f"Fathom API server error: {response.status_code}"
                    )

                if response.status_code >= 400:
                    error_body = response.text
                    raise APIError(
                        f"Fathom API error {response.status_code}: {error_body}"
                    )

                # Parse and return successful response
                return response.json()  # type: ignore[no-any-return]

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(
                    "Fathom API connection error",
                    error=str(e),
                    attempt=attempt,
                )
                if attempt < MAX_RETRIES:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue

        raise APIError(f"Fathom API request failed after {MAX_RETRIES} retries: {last_error}")

    # ── Meetings ──────────────────────────────────────────────────────────

    async def list_meetings(
        self,
        after: str | None = None,
        before: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """List meetings with optional date filters.

        Args:
            after: Filter meetings after this ISO datetime
            before: Filter meetings before this ISO datetime
            cursor: Pagination cursor from previous response
            limit: Maximum number of results (default 50)

        Returns:
            Dict with 'meetings', 'next_cursor', 'has_more' keys
        """
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if cursor:
            params["cursor"] = cursor

        logger.info("Fetching Fathom meetings", params=params)
        return await self._request("GET", "/meetings", params=params)

    async def list_all_meetings(
        self,
        after: str | None = None,
        before: str | None = None,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch all meetings using cursor-based pagination.

        Args:
            after: Filter meetings after this ISO datetime
            before: Filter meetings before this ISO datetime
            max_pages: Safety limit on number of pages to fetch

        Returns:
            List of all meeting dicts
        """
        all_meetings: list[dict[str, Any]] = []
        cursor: str | None = None

        for page in range(max_pages):
            response = await self.list_meetings(
                after=after, before=before, cursor=cursor
            )
            meetings = response.get("meetings", [])
            all_meetings.extend(meetings)

            if not response.get("has_more", False):
                break

            cursor = response.get("next_cursor")
            if not cursor:
                break

            logger.debug(
                "Fetching next page of meetings",
                page=page + 2,
                total_so_far=len(all_meetings),
            )

        return all_meetings

    # ── Recordings ────────────────────────────────────────────────────────

    async def get_recording_summary(self, recording_id: str) -> dict[str, Any]:
        """Get the AI-generated summary for a recording.

        Args:
            recording_id: The recording ID

        Returns:
            Summary dict with 'template_name' and 'markdown_formatted'
        """
        logger.info("Fetching Fathom recording summary", recording_id=recording_id)
        return await self._request("GET", f"/recordings/{recording_id}/summary")

    async def get_recording_transcript(self, recording_id: str) -> dict[str, Any]:
        """Get the full transcript for a recording.

        Args:
            recording_id: The recording ID

        Returns:
            Transcript dict with list of speaker-attributed entries
        """
        logger.info("Fetching Fathom recording transcript", recording_id=recording_id)
        return await self._request("GET", f"/recordings/{recording_id}/transcript")

    async def get_recording(
        self,
        recording_id: str,
        include_summary: bool = False,
        include_transcript: bool = False,
        include_action_items: bool = False,
        include_crm_matches: bool = False,
    ) -> dict[str, Any]:
        """Get a recording with optional included data.

        Args:
            recording_id: The recording ID
            include_summary: Include AI summary in response
            include_transcript: Include full transcript in response
            include_action_items: Include action items in response
            include_crm_matches: Include CRM matches in response

        Returns:
            Recording dict with requested includes
        """
        params: dict[str, Any] = {}
        includes = []
        if include_summary:
            includes.append("summary")
        if include_transcript:
            includes.append("transcript")
        if include_action_items:
            includes.append("action_items")
        if include_crm_matches:
            includes.append("crm_matches")
        if includes:
            params["include"] = ",".join(includes)

        logger.info(
            "Fetching Fathom recording",
            recording_id=recording_id,
            includes=includes,
        )
        return await self._request("GET", f"/recordings/{recording_id}", params=params)

    # ── Teams ─────────────────────────────────────────────────────────────

    async def list_teams(self) -> dict[str, Any]:
        """List all teams in the Fathom workspace.

        Returns:
            Dict with 'teams' key
        """
        logger.info("Fetching Fathom teams")
        return await self._request("GET", "/teams")

    async def list_team_members(self) -> dict[str, Any]:
        """List all team members in the Fathom workspace.

        Returns:
            Dict with 'team_members' key
        """
        logger.info("Fetching Fathom team members")
        return await self._request("GET", "/team-members")

    # ── Webhooks ──────────────────────────────────────────────────────────

    async def register_webhook(
        self,
        url: str,
        include_transcript: bool = True,
        include_summary: bool = True,
        include_action_items: bool = True,
        include_crm_matches: bool = False,
        triggered_for: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register a webhook for real-time meeting data.

        NOTE: This is a WRITE operation. Only available when allow_writes=True.

        Args:
            url: Destination URL for webhook events
            include_transcript: Include transcript in webhook payload
            include_summary: Include summary in webhook payload
            include_action_items: Include action items in webhook payload
            include_crm_matches: Include CRM matches in webhook payload
            triggered_for: List of triggers (e.g. ['my_recordings', 'shared_team_recordings'])

        Returns:
            Webhook registration dict with 'id', 'url', 'secret'
        """
        body: dict[str, Any] = {
            "url": url,
            "include_transcript": include_transcript,
            "include_summary": include_summary,
            "include_action_items": include_action_items,
            "include_crm_matches": include_crm_matches,
        }
        if triggered_for:
            body["triggered_for"] = triggered_for

        logger.info("Registering Fathom webhook", url=url)
        return await self._request("POST", "/webhooks", json_body=body)

    async def delete_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Delete a webhook registration.

        NOTE: This is a WRITE operation. Only available when allow_writes=True.

        Args:
            webhook_id: The webhook ID to delete

        Returns:
            Confirmation dict
        """
        logger.info("Deleting Fathom webhook", webhook_id=webhook_id)
        return await self._request("DELETE", f"/webhooks/{webhook_id}")

    # ── Health Check ──────────────────────────────────────────────────────

    async def validate_api_key(self) -> bool:
        """Validate the API key by making a lightweight request.

        Returns:
            True if the API key is valid

        Raises:
            AuthenticationError: If the API key is invalid
        """
        try:
            await self.list_teams()
            return True
        except AuthenticationError:
            raise
        except APIError as e:
            logger.error("Fathom API key validation failed", error=str(e))
            raise AuthenticationError(f"Failed to validate Fathom API key: {e}") from e
