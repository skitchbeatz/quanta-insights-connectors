"""Fathom webhook receiver — HTTP endpoint for real-time meeting data.

Receives POST requests from Fathom when meetings are recorded/processed.
Validates webhook signatures, parses payloads, and stores meeting data
for consumption by MCP tools.

This runs as a separate HTTP server alongside the MCP stdio transport.
In production, Traefik routes webhook traffic to this endpoint at:
  https://quanta-insights.chateaumac.com/webhooks/fathom

Fathom webhook payload includes (configurable at registration time):
- transcript
- summary
- action_items
- crm_matches

Webhook triggers:
- my_recordings
- shared_team_recordings
- shared_external_recordings

Reference: https://developers.fathom.ai/api-reference
"""

import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)


class WebhookStore:
    """In-memory store for received webhook events.

    Stores the most recent meeting data received via webhooks.
    In production, this would be backed by a database or message queue.
    For Phase 1, in-memory storage is sufficient for single-instance deployment.
    """

    def __init__(self, max_events: int = 1000) -> None:
        """Initialize the webhook store.

        Args:
            max_events: Maximum number of events to retain in memory
        """
        self.max_events = max_events
        # Keyed by recording_id for quick lookup
        self._meetings: dict[str, dict[str, Any]] = {}
        # Chronological list of all events
        self._events: list[dict[str, Any]] = []

    def store_event(self, event: dict[str, Any]) -> None:
        """Store a webhook event.

        Args:
            event: Parsed webhook payload
        """
        recording_id = event.get("recording_id", "")
        timestamp = datetime.now(UTC).isoformat()

        enriched_event = {
            **event,
            "received_at": timestamp,
        }

        # Store by recording_id for lookup
        if recording_id:
            self._meetings[recording_id] = enriched_event

        # Append to chronological list, evicting oldest if at capacity
        self._events.append(enriched_event)
        if len(self._events) > self.max_events:
            evicted = self._events.pop(0)
            # Clean up meeting index if the evicted event was the latest for that recording
            evicted_id = evicted.get("recording_id", "")
            if evicted_id and self._meetings.get(evicted_id) == evicted:
                del self._meetings[evicted_id]

        logger.info(
            "Stored webhook event",
            recording_id=recording_id,
            total_events=len(self._events),
        )

    def get_meeting(self, recording_id: str) -> dict[str, Any] | None:
        """Get the latest webhook data for a recording.

        Args:
            recording_id: The recording ID to look up

        Returns:
            The webhook event data, or None if not found
        """
        return self._meetings.get(recording_id)

    def get_recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get the most recent webhook events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent events, newest first
        """
        return list(reversed(self._events[-limit:]))

    @property
    def event_count(self) -> int:
        """Total number of stored events."""
        return len(self._events)

    @property
    def meeting_count(self) -> int:
        """Number of unique meetings stored."""
        return len(self._meetings)


# Global webhook store instance — shared with MCP tools
webhook_store = WebhookStore()


def verify_fathom_signature(
    payload_body: bytes,
    signature_header: str,
    webhook_secret: str,
) -> bool:
    """Verify the HMAC signature from Fathom webhook.

    Fathom signs webhook payloads with the secret provided at registration.
    The signature is sent in the X-Fathom-Signature header.

    Args:
        payload_body: Raw request body bytes
        signature_header: Value of X-Fathom-Signature header
        webhook_secret: The secret from webhook registration

    Returns:
        True if signature is valid
    """
    if not signature_header or not webhook_secret:
        return False

    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature_header)


async def handle_fathom_webhook(request: Request) -> Response:
    """Handle incoming Fathom webhook POST requests.

    Validates the signature, parses the payload, and stores the event.

    Expected payload structure (from Fathom docs):
    {
        "recording_id": "...",
        "title": "...",
        "url": "...",
        "created_at": "...",
        "duration_seconds": ...,
        "calendar_invitees": [...],
        "recorded_by": {...},
        "transcript": [...],       // if include_transcript=true
        "summary": {...},          // if include_summary=true
        "action_items": [...],     // if include_action_items=true
        "crm_matches": {...}       // if include_crm_matches=true
    }
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    signature = request.headers.get("X-Fathom-Signature", "")
    webhook_secret = getattr(settings, "fathom_webhook_secret", "")

    if webhook_secret and not verify_fathom_signature(body, signature, webhook_secret):
        logger.warning(
            "Fathom webhook signature verification failed",
            remote_addr=request.client.host if request.client else "unknown",
        )
        return JSONResponse(
            {"error": "Invalid signature"},
            status_code=401,
        )

    # Parse payload
    try:
        payload: dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Fathom webhook payload", error=str(e))
        return JSONResponse(
            {"error": "Invalid JSON payload"},
            status_code=400,
        )

    recording_id = payload.get("recording_id", "unknown")
    title = payload.get("title", "Untitled")

    logger.info(
        "Received Fathom webhook",
        recording_id=recording_id,
        title=title,
        has_transcript="transcript" in payload,
        has_summary="summary" in payload,
        has_action_items="action_items" in payload,
    )

    # Store the event
    webhook_store.store_event(payload)

    return JSONResponse(
        {
            "status": "ok",
            "recording_id": recording_id,
            "message": f"Webhook received for: {title}",
        },
        status_code=200,
    )


async def handle_health(request: Request) -> Response:
    """Health check endpoint for the webhook receiver."""
    return JSONResponse({
        "status": "healthy",
        "service": "quanta-insights-webhooks",
        "events_stored": webhook_store.event_count,
        "meetings_stored": webhook_store.meeting_count,
    })


async def handle_webhook_events(request: Request) -> Response:
    """List recent webhook events (for debugging/monitoring)."""
    limit = int(request.query_params.get("limit", "50"))
    events = webhook_store.get_recent_events(limit=limit)
    return JSONResponse({
        "events": events,
        "total": webhook_store.event_count,
        "showing": len(events),
    })


# Starlette ASGI application
webhook_app = Starlette(
    routes=[
        Route("/webhooks/fathom", handle_fathom_webhook, methods=["POST"]),
        Route("/webhooks/events", handle_webhook_events, methods=["GET"]),
        Route("/health", handle_health, methods=["GET"]),
    ],
)


def run_webhook_server(
    host: str = "0.0.0.0",
    port: int | None = None,
) -> None:
    """Run the webhook receiver HTTP server.

    Args:
        host: Bind address
        port: Bind port (defaults to settings.webhook_port)
    """
    import uvicorn

    if port is None:
        port = settings.webhook_port

    logger.info(
        "Starting webhook receiver",
        host=host,
        port=port,
        endpoint="/webhooks/fathom",
    )
    uvicorn.run(
        webhook_app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    run_webhook_server()
