"""Sourcewhale outreach connector implementation.

Provides MCP tools for accessing Sourcewhale outreach data:
- List outreach sequences
- Get sequence performance stats
- Search contacts by sequence/status
- Get full outreach history for a contact
- Get aggregated campaign analytics

NOTE: API documentation is not publicly available. This connector's tools
and data models are PROVISIONAL — inferred from common outreach platform
patterns (Outreach.io, Salesloft, Apollo) and Sourcewhale's known feature set.
Will be updated once official API docs are obtained from the admin console.

Auth: API key (generation method TBD — expected via admin console).
"""

from typing import Any

from ...config import settings
from ...logging import get_logger
from ..base import AuthenticationError, BaseConnector, ToolDefinition
from .client import SourcewhaleAPIClient

logger = get_logger(__name__)


class SourcewhaleConnector(BaseConnector):
    """Sourcewhale outreach and sequencing connector.

    PROVISIONAL: Data models inferred from common outreach platform patterns.
    """

    def __init__(self) -> None:
        super().__init__("Sourcewhale")
        self.mock_mode = settings.is_mock_mode("sourcewhale")
        self._api_client: SourcewhaleAPIClient | None = None

    async def authenticate(self) -> None:
        """Authenticate with Sourcewhale API.

        In production, loads API key from Vault and validates it.
        In mock mode, skips authentication.
        """
        if self.mock_mode:
            logger.info("Sourcewhale connector running in mock mode")
            self._set_authenticated(True)
            return

        # Load API key from Vault
        try:
            from ...vault_client import vault_client
            secret = await vault_client.get_secret("business/quanta-insights/sourcewhale")
            api_key = secret.get("api_key")
            if not api_key:
                raise AuthenticationError(
                    "Sourcewhale API key not found in Vault at "
                    "secret/business/quanta-insights/sourcewhale/"
                )
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(
                f"Failed to load Sourcewhale credentials from Vault: {e}"
            ) from e

        # Create and validate the API client
        self._api_client = SourcewhaleAPIClient(api_key=api_key)
        await self._api_client.__aenter__()

        try:
            await self._api_client.validate_api_key()
            logger.info("Sourcewhale API key validated successfully")
        except Exception as e:
            await self._api_client.__aexit__(None, None, None)
            self._api_client = None
            raise AuthenticationError(
                f"Sourcewhale API key validation failed: {e}"
            ) from e

        self._set_authenticated(True)

    async def _get_all_tools(self) -> list[ToolDefinition]:
        """Return all Sourcewhale tool definitions."""
        return [
            ToolDefinition(
                name="sourcewhale_list_sequences",
                description=(
                    "List outreach sequences (campaigns) in Sourcewhale. "
                    "Returns sequence metadata, step counts, and aggregate stats. "
                    "Filter by status or tag."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["active", "paused", "completed", "draft", "all"],
                            "default": "active",
                            "description": "Filter by sequence status",
                        },
                        "tag": {
                            "type": "string",
                            "description": "Filter by tag (e.g. 'engineering', 'ml')",
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
                name="sourcewhale_get_sequence_stats",
                description=(
                    "Get detailed performance metrics for a specific outreach sequence. "
                    "Returns reply rate, open rate, bounce rate, and per-step breakdown."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "sequence_id": {
                            "type": "string",
                            "description": "The sequence ID to get stats for",
                        },
                    },
                    "required": ["sequence_id"],
                },
            ),
            ToolDefinition(
                name="sourcewhale_search_contacts",
                description=(
                    "Search for contacts in Sourcewhale by sequence, status, or email. "
                    "Returns contact details and their current outreach status."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "sequence_id": {
                            "type": "string",
                            "description": "Filter by sequence ID",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "replied", "bounced", "opted_out", "completed", "all"],
                            "default": "all",
                            "description": "Filter by outreach status",
                        },
                        "email": {
                            "type": "string",
                            "description": "Search by exact email address",
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
                name="sourcewhale_get_outreach_history",
                description=(
                    "Get the full outreach timeline for a specific contact. "
                    "Returns all events: emails sent, opens, clicks, replies, "
                    "LinkedIn messages, and bounces in chronological order."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "contact_id": {
                            "type": "string",
                            "description": "The contact ID to get outreach history for",
                        },
                    },
                    "required": ["contact_id"],
                },
            ),
            ToolDefinition(
                name="sourcewhale_get_campaign_analytics",
                description=(
                    "Get aggregated outreach analytics across all sequences. "
                    "Returns overall reply rates, open rates, volume metrics, "
                    "and top-performing sequences."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["last_7_days", "last_30_days", "last_90_days", "all_time"],
                            "default": "last_30_days",
                            "description": "Time period for analytics",
                        },
                    },
                },
            ),
        ]

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a Sourcewhale tool."""
        if tool_name == "sourcewhale_list_sequences":
            return await self._list_sequences(arguments)
        elif tool_name == "sourcewhale_get_sequence_stats":
            return await self._get_sequence_stats(arguments)
        elif tool_name == "sourcewhale_search_contacts":
            return await self._search_contacts(arguments)
        elif tool_name == "sourcewhale_get_outreach_history":
            return await self._get_outreach_history(arguments)
        elif tool_name == "sourcewhale_get_campaign_analytics":
            return await self._get_campaign_analytics(arguments)
        else:
            from ..base import ToolNotFoundError
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")

    async def _list_sequences(self, args: dict[str, Any]) -> dict[str, Any]:
        """List outreach sequences."""
        logger.info("Listing Sourcewhale sequences", args=args)

        if self.mock_mode:
            from .mock import get_mock_sequences
            return get_mock_sequences(
                status=args.get("status"),
                tag=args.get("tag"),
                limit=args.get("limit", 50),
            )

        # Real API: fetch sequences with filters
        assert self._api_client is not None
        return await self._api_client.list_sequences(
            status=args.get("status"),
            tag=args.get("tag"),
            limit=args.get("limit", 50),
        )

    async def _get_sequence_stats(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get stats for a specific sequence."""
        sequence_id = args.get("sequence_id", "")
        logger.info("Getting Sourcewhale sequence stats", sequence_id=sequence_id)

        if self.mock_mode:
            from .mock import get_mock_sequence_stats
            stats = get_mock_sequence_stats(sequence_id)
            if stats is None:
                return {"error": f"No sequence found with ID '{sequence_id}'"}
            return stats

        # Real API: fetch sequence stats
        assert self._api_client is not None
        return await self._api_client.get_sequence_stats(sequence_id)

    async def _search_contacts(self, args: dict[str, Any]) -> dict[str, Any]:
        """Search contacts by sequence, status, or email."""
        logger.info("Searching Sourcewhale contacts", args=args)

        if self.mock_mode:
            from .mock import get_mock_contacts
            return get_mock_contacts(
                sequence_id=args.get("sequence_id"),
                status=args.get("status"),
                email=args.get("email"),
                limit=args.get("limit", 50),
            )

        # Real API: search contacts with filters
        assert self._api_client is not None
        return await self._api_client.list_contacts(
            sequence_id=args.get("sequence_id"),
            status=args.get("status"),
            email=args.get("email"),
            limit=args.get("limit", 50),
        )

    async def _get_outreach_history(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get outreach history for a contact."""
        contact_id = args.get("contact_id", "")
        logger.info("Getting Sourcewhale outreach history", contact_id=contact_id)

        if self.mock_mode:
            from .mock import get_mock_outreach_history
            history = get_mock_outreach_history(contact_id)
            if history is None:
                return {"error": f"No outreach history found for contact '{contact_id}'"}
            return history

        # Real API: fetch contact outreach history
        assert self._api_client is not None
        return await self._api_client.get_contact_history(contact_id)

    async def _get_campaign_analytics(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get aggregated campaign analytics."""
        period = args.get("period", "last_30_days")
        logger.info("Getting Sourcewhale campaign analytics", period=period)

        if self.mock_mode:
            from .mock import get_mock_campaign_analytics
            return get_mock_campaign_analytics(period=period)

        # Real API: fetch aggregated analytics
        assert self._api_client is not None
        return await self._api_client.get_analytics(period=period)
