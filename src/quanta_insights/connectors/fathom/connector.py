"""Fathom meeting intelligence connector implementation.

Provides MCP tools for accessing Fathom meeting data:
- List/search meetings
- Get meeting summaries
- Get meeting transcripts
- Search meetings by company domain
- Get action items from meetings

Auth: API key via X-Api-Key header.
API Docs: https://developers.fathom.ai/api-reference
"""

from typing import Any

from ...config import settings
from ...logging import get_logger
from ..base import AuthenticationError, BaseConnector, ToolDefinition
from .client import FathomAPIClient

logger = get_logger(__name__)


class FathomConnector(BaseConnector):
    """Fathom meeting intelligence connector."""

    def __init__(self) -> None:
        super().__init__("Fathom")
        self.mock_mode = settings.is_mock_mode("fathom")
        self._api_client: FathomAPIClient | None = None

    async def authenticate(self) -> None:
        """Authenticate with Fathom API.

        In production, loads API key from Vault and validates it.
        In mock mode, skips authentication.
        """
        if self.mock_mode:
            logger.info("Fathom connector running in mock mode")
            self._set_authenticated(True)
            return

        # Load API key from Vault
        try:
            from ...vault_client import vault_client
            secret = await vault_client.get_secret("business/quanta-insights/fathom")
            api_key = secret.get("api_key")
            if not api_key:
                raise AuthenticationError(
                    "Fathom API key not found in Vault at "
                    "secret/business/quanta-insights/fathom/"
                )
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(
                f"Failed to load Fathom credentials from Vault: {e}"
            ) from e

        # Create and validate the API client
        self._api_client = FathomAPIClient(api_key=api_key)
        await self._api_client.__aenter__()

        try:
            await self._api_client.validate_api_key()
            logger.info("Fathom API key validated successfully")
        except Exception as e:
            await self._api_client.__aexit__(None, None, None)
            self._api_client = None
            raise AuthenticationError(
                f"Fathom API key validation failed: {e}"
            ) from e

        self._set_authenticated(True)

    async def _get_all_tools(self) -> list[ToolDefinition]:
        """Return all Fathom tool definitions."""
        return [
            ToolDefinition(
                name="fathom_list_meetings",
                description=(
                    "List meetings recorded in Fathom with optional filters. "
                    "Returns meeting metadata including title, date, duration, "
                    "and calendar invitees."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "date_from": {
                            "type": "string",
                            "format": "date",
                            "description": "Start date filter (ISO format, e.g. '2024-01-01')",
                        },
                        "date_to": {
                            "type": "string",
                            "format": "date",
                            "description": "End date filter (ISO format, e.g. '2024-12-31')",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Filter by invitee email domain (e.g. 'acme.com')",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 50,
                            "description": "Maximum number of results",
                        },
                    },
                },
            ),
            ToolDefinition(
                name="fathom_get_meeting_summary",
                description=(
                    "Get the AI-generated summary for a specific meeting recording. "
                    "Returns a markdown-formatted summary with key points, decisions, "
                    "and discussion topics."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "recording_id": {
                            "type": "string",
                            "description": "The recording ID to get the summary for",
                        },
                    },
                    "required": ["recording_id"],
                },
            ),
            ToolDefinition(
                name="fathom_get_meeting_transcript",
                description=(
                    "Get the full transcript for a specific meeting recording. "
                    "Returns timestamped speaker-attributed text segments."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "recording_id": {
                            "type": "string",
                            "description": "The recording ID to get the transcript for",
                        },
                    },
                    "required": ["recording_id"],
                },
            ),
            ToolDefinition(
                name="fathom_search_meetings_by_domain",
                description=(
                    "Find all meetings where attendees from a specific company domain "
                    "were present. Useful for reviewing all interactions with a client "
                    "or candidate's company."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Email domain to search for (e.g. 'acme.com')",
                        },
                        "limit": {
                            "type": "integer",
                            "default": 50,
                            "description": "Maximum number of results",
                        },
                    },
                    "required": ["domain"],
                },
            ),
            ToolDefinition(
                name="fathom_get_action_items",
                description=(
                    "Get action items extracted from a specific meeting recording. "
                    "Returns descriptions, assignees, and playback links."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "recording_id": {
                            "type": "string",
                            "description": "The recording ID to get action items for",
                        },
                    },
                    "required": ["recording_id"],
                },
            ),
        ]

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a Fathom tool."""
        if tool_name == "fathom_list_meetings":
            return await self._list_meetings(arguments)
        elif tool_name == "fathom_get_meeting_summary":
            return await self._get_meeting_summary(arguments)
        elif tool_name == "fathom_get_meeting_transcript":
            return await self._get_meeting_transcript(arguments)
        elif tool_name == "fathom_search_meetings_by_domain":
            return await self._search_meetings_by_domain(arguments)
        elif tool_name == "fathom_get_action_items":
            return await self._get_action_items(arguments)
        else:
            from ..base import ToolNotFoundError
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")

    async def _list_meetings(self, args: dict[str, Any]) -> dict[str, Any]:
        """List meetings with optional filters."""
        logger.info("Listing Fathom meetings", args=args)

        if self.mock_mode:
            from .mock import get_mock_meetings
            return get_mock_meetings(
                domain=args.get("domain"),
                date_from=args.get("date_from"),
                date_to=args.get("date_to"),
                limit=args.get("limit", 50),
            )

        # Real API: fetch meetings with date filters
        assert self._api_client is not None
        return await self._api_client.list_meetings(
            after=args.get("date_from"),
            before=args.get("date_to"),
            limit=args.get("limit", 50),
        )

    async def _get_meeting_summary(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get AI summary for a recording."""
        recording_id = args.get("recording_id", "")
        logger.info("Getting Fathom meeting summary", recording_id=recording_id)

        if self.mock_mode:
            from .mock import get_mock_summary
            summary = get_mock_summary(recording_id)
            if summary is None:
                return {"error": f"No summary found for recording '{recording_id}'"}
            return {"recording_id": recording_id, "summary": summary}

        # Real API: fetch recording summary
        assert self._api_client is not None
        summary = await self._api_client.get_recording_summary(recording_id)
        return {"recording_id": recording_id, "summary": summary}

    async def _get_meeting_transcript(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get full transcript for a recording."""
        recording_id = args.get("recording_id", "")
        logger.info("Getting Fathom meeting transcript", recording_id=recording_id)

        if self.mock_mode:
            from .mock import get_mock_transcript
            transcript = get_mock_transcript(recording_id)
            if transcript is None:
                return {"error": f"No transcript found for recording '{recording_id}'"}
            return {
                "recording_id": recording_id,
                "transcript": transcript,
                "entry_count": len(transcript),
            }

        # Real API: fetch recording transcript
        assert self._api_client is not None
        transcript_data = await self._api_client.get_recording_transcript(recording_id)
        entries = transcript_data.get("transcript", [])
        return {
            "recording_id": recording_id,
            "transcript": entries,
            "entry_count": len(entries),
        }

    async def _search_meetings_by_domain(self, args: dict[str, Any]) -> dict[str, Any]:
        """Search meetings by attendee email domain."""
        domain = args.get("domain", "")
        limit = args.get("limit", 50)
        logger.info("Searching Fathom meetings by domain", domain=domain)

        if self.mock_mode:
            from .mock import get_mock_meetings
            result = get_mock_meetings(domain=domain, limit=limit)
            return {
                "domain": domain,
                "meetings": result["meetings"],
                "total": len(result["meetings"]),
            }

        # Real API: Fathom doesn't have a native domain filter, so we
        # fetch all meetings and filter client-side by invitee domain.
        # TODO: Optimize with server-side filtering if Fathom adds support.
        assert self._api_client is not None
        all_meetings = await self._api_client.list_all_meetings()
        filtered = [
            m for m in all_meetings
            if any(
                inv.get("domain", "").lower() == domain.lower()
                for inv in m.get("calendar_invitees", [])
            )
        ][:limit]
        return {
            "domain": domain,
            "meetings": filtered,
            "total": len(filtered),
        }

    async def _get_action_items(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get action items from a recording."""
        recording_id = args.get("recording_id", "")
        logger.info("Getting Fathom action items", recording_id=recording_id)

        if self.mock_mode:
            from .mock import get_mock_action_items
            items = get_mock_action_items(recording_id)
            if items is None:
                return {"error": f"No action items found for recording '{recording_id}'"}
            return {
                "recording_id": recording_id,
                "action_items": items,
                "total": len(items),
            }

        # Real API: fetch recording with action items included
        assert self._api_client is not None
        recording = await self._api_client.get_recording(
            recording_id, include_action_items=True
        )
        items = recording.get("action_items", [])
        return {
            "recording_id": recording_id,
            "action_items": items,
            "total": len(items),
        }
