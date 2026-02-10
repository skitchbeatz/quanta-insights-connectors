"""Tests for Fathom webhook receiver."""

import hashlib
import hmac

import pytest
from starlette.testclient import TestClient

from quanta_insights.webhooks import (
    WebhookStore,
    verify_fathom_signature,
    webhook_app,
    webhook_store,
)


@pytest.fixture(autouse=True)
def _clear_webhook_store():
    """Clear the global webhook store before each test."""
    webhook_store._meetings.clear()
    webhook_store._events.clear()
    yield
    webhook_store._meetings.clear()
    webhook_store._events.clear()


@pytest.fixture
def client():
    """Create a Starlette test client."""
    return TestClient(webhook_app)


SAMPLE_WEBHOOK_PAYLOAD = {
    "recording_id": "rec_test_001",
    "title": "Test Meeting - Webhook",
    "url": "https://fathom.video/recordings/rec_test_001",
    "created_at": "2024-02-20T14:00:00Z",
    "duration_seconds": 1800,
    "calendar_invitees": [
        {
            "name": "Test User",
            "email": "test@example.com",
            "domain": "example.com",
            "is_external": True,
        }
    ],
    "recorded_by": {
        "display_name": "Regan McCullough",
        "email": "regan@quantainsights.com",
    },
    "transcript": [
        {
            "speaker": {"display_name": "Regan McCullough"},
            "text": "Hello, this is a test meeting.",
            "timestamp": 10.0,
        }
    ],
    "summary": {
        "template_name": "General",
        "markdown_formatted": "## Test Meeting\n\nThis was a test meeting.",
    },
    "action_items": [
        {
            "description": "Follow up on test items",
            "completed": False,
            "assignee": "Regan McCullough",
        }
    ],
}


# ── WebhookStore unit tests ──────────────────────────────────────────────


@pytest.mark.unit
def test_webhook_store_store_and_retrieve():
    """Test storing and retrieving events from WebhookStore."""
    store = WebhookStore()
    event = {"recording_id": "rec_001", "title": "Test"}

    store.store_event(event)

    assert store.event_count == 1
    assert store.meeting_count == 1

    meeting = store.get_meeting("rec_001")
    assert meeting is not None
    assert meeting["title"] == "Test"
    assert "received_at" in meeting


@pytest.mark.unit
def test_webhook_store_recent_events():
    """Test getting recent events in reverse chronological order."""
    store = WebhookStore()

    for i in range(5):
        store.store_event({"recording_id": f"rec_{i}", "index": i})

    recent = store.get_recent_events(limit=3)
    assert len(recent) == 3
    # Most recent first
    assert recent[0]["index"] == 4
    assert recent[2]["index"] == 2


@pytest.mark.unit
def test_webhook_store_max_events():
    """Test that store evicts oldest events when at capacity."""
    store = WebhookStore(max_events=3)

    for i in range(5):
        store.store_event({"recording_id": f"rec_{i}", "index": i})

    assert store.event_count == 3
    # Oldest events (0, 1) should be evicted
    recent = store.get_recent_events()
    indices = [e["index"] for e in recent]
    assert 0 not in indices
    assert 1 not in indices
    assert 4 in indices


@pytest.mark.unit
def test_webhook_store_overwrite_same_recording():
    """Test that storing a new event for the same recording overwrites the old one."""
    store = WebhookStore()

    store.store_event({"recording_id": "rec_001", "version": 1})
    store.store_event({"recording_id": "rec_001", "version": 2})

    meeting = store.get_meeting("rec_001")
    assert meeting is not None
    assert meeting["version"] == 2
    assert store.event_count == 2  # Both events stored chronologically
    assert store.meeting_count == 1  # But only one meeting entry


# ── Signature verification tests ─────────────────────────────────────────


@pytest.mark.unit
def test_verify_fathom_signature_valid():
    """Test that a valid HMAC signature passes verification."""
    secret = "test-secret-key"
    payload = b'{"recording_id": "rec_001"}'

    signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    assert verify_fathom_signature(payload, signature, secret) is True


@pytest.mark.unit
def test_verify_fathom_signature_invalid():
    """Test that an invalid signature fails verification."""
    secret = "test-secret-key"
    payload = b'{"recording_id": "rec_001"}'

    assert verify_fathom_signature(payload, "invalid-signature", secret) is False


@pytest.mark.unit
def test_verify_fathom_signature_empty():
    """Test that empty signature/secret fails verification."""
    assert verify_fathom_signature(b"payload", "", "secret") is False
    assert verify_fathom_signature(b"payload", "sig", "") is False


# ── HTTP endpoint tests ──────────────────────────────────────────────────


@pytest.mark.unit
def test_webhook_endpoint_accepts_valid_payload(client):
    """Test that the webhook endpoint accepts a valid payload."""
    response = client.post(
        "/webhooks/fathom",
        json=SAMPLE_WEBHOOK_PAYLOAD,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["recording_id"] == "rec_test_001"

    # Verify event was stored
    assert webhook_store.event_count == 1
    meeting = webhook_store.get_meeting("rec_test_001")
    assert meeting is not None
    assert meeting["title"] == "Test Meeting - Webhook"


@pytest.mark.unit
def test_webhook_endpoint_rejects_invalid_json(client):
    """Test that the webhook endpoint rejects invalid JSON."""
    response = client.post(
        "/webhooks/fathom",
        content=b"not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["error"]


@pytest.mark.unit
def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "quanta-insights-webhooks"
    assert "events_stored" in data


@pytest.mark.unit
def test_webhook_events_endpoint(client):
    """Test the events listing endpoint."""
    # Store some events first
    client.post("/webhooks/fathom", json=SAMPLE_WEBHOOK_PAYLOAD)
    client.post(
        "/webhooks/fathom",
        json={**SAMPLE_WEBHOOK_PAYLOAD, "recording_id": "rec_test_002", "title": "Second Meeting"},
    )

    response = client.get("/webhooks/events")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["showing"] == 2
    # Most recent first
    assert data["events"][0]["recording_id"] == "rec_test_002"


@pytest.mark.unit
def test_webhook_events_endpoint_with_limit(client):
    """Test the events listing endpoint with limit parameter."""
    for i in range(5):
        client.post(
            "/webhooks/fathom",
            json={**SAMPLE_WEBHOOK_PAYLOAD, "recording_id": f"rec_{i}"},
        )

    response = client.get("/webhooks/events?limit=2")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["showing"] == 2
