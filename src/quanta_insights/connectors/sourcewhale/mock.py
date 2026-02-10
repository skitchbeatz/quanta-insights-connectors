"""Mock data layer for Sourcewhale connector.

Provides realistic fake outreach data for development without API credentials.
Mirrors expected Sourcewhale API response structure so switching to real API
is a config change, not a code change.

NOTE: These mocks are PROVISIONAL. Data models are inferred from common
outreach platform patterns. Will be updated once official API docs are obtained.
"""

from typing import Any

MOCK_SEQUENCES: list[dict[str, Any]] = [
    {
        "id": "seq_001",
        "name": "Senior Engineers - Acme Corp Roles",
        "status": "active",
        "created_at": "2024-02-16T09:00:00Z",
        "updated_at": "2024-02-20T14:30:00Z",
        "steps": [
            {
                "step_number": 1,
                "channel": "email",
                "delay_days": 0,
                "subject_template": "Exciting Senior Engineer opportunity at Acme Corp",
                "body_preview": "Hi {{first_name}}, I came across your profile and thought you'd be a great fit...",
            },
            {
                "step_number": 2,
                "channel": "linkedin",
                "delay_days": 2,
                "subject_template": None,
                "body_preview": "Hi {{first_name}}, I sent you an email about an opportunity at Acme Corp...",
            },
            {
                "step_number": 3,
                "channel": "email",
                "delay_days": 3,
                "subject_template": "Re: Exciting Senior Engineer opportunity at Acme Corp",
                "body_preview": "Hi {{first_name}}, just following up on my previous message...",
            },
            {
                "step_number": 4,
                "channel": "email",
                "delay_days": 5,
                "subject_template": "Last check-in: Senior Engineer at Acme Corp",
                "body_preview": "Hi {{first_name}}, I wanted to reach out one more time...",
            },
        ],
        "stats": {
            "total_contacted": 25,
            "total_replied": 8,
            "total_opened": 18,
            "total_clicked": 5,
            "total_bounced": 2,
            "reply_rate": 32.0,
            "open_rate": 72.0,
            "bounce_rate": 8.0,
        },
        "tags": ["engineering", "acme-corp", "senior"],
    },
    {
        "id": "seq_002",
        "name": "ML Engineers - TechStart Inc",
        "status": "active",
        "created_at": "2024-02-18T10:00:00Z",
        "updated_at": "2024-02-21T11:00:00Z",
        "steps": [
            {
                "step_number": 1,
                "channel": "email",
                "delay_days": 0,
                "subject_template": "ML Engineer role at a fast-growing AI startup",
                "body_preview": "Hi {{first_name}}, TechStart is building something exciting in AI logistics...",
            },
            {
                "step_number": 2,
                "channel": "linkedin",
                "delay_days": 3,
                "subject_template": None,
                "body_preview": "Hi {{first_name}}, I'd love to chat about an ML role...",
            },
            {
                "step_number": 3,
                "channel": "email",
                "delay_days": 4,
                "subject_template": "Re: ML Engineer role at a fast-growing AI startup",
                "body_preview": "Hi {{first_name}}, following up on the ML Engineer opportunity...",
            },
        ],
        "stats": {
            "total_contacted": 15,
            "total_replied": 6,
            "total_opened": 12,
            "total_clicked": 4,
            "total_bounced": 1,
            "reply_rate": 40.0,
            "open_rate": 80.0,
            "bounce_rate": 6.7,
        },
        "tags": ["ml", "techstart", "ai"],
    },
    {
        "id": "seq_003",
        "name": "Client Outreach - Q1 Business Development",
        "status": "completed",
        "created_at": "2024-01-05T08:00:00Z",
        "updated_at": "2024-02-01T16:00:00Z",
        "steps": [
            {
                "step_number": 1,
                "channel": "email",
                "delay_days": 0,
                "subject_template": "Staffing partnership opportunity",
                "body_preview": "Hi {{first_name}}, I noticed {{company}} is growing...",
            },
            {
                "step_number": 2,
                "channel": "linkedin",
                "delay_days": 3,
                "subject_template": None,
                "body_preview": "Hi {{first_name}}, I'd love to discuss how we can help...",
            },
        ],
        "stats": {
            "total_contacted": 40,
            "total_replied": 10,
            "total_opened": 28,
            "total_clicked": 8,
            "total_bounced": 3,
            "reply_rate": 25.0,
            "open_rate": 70.0,
            "bounce_rate": 7.5,
        },
        "tags": ["business-development", "q1", "clients"],
    },
]

MOCK_CONTACTS: list[dict[str, Any]] = [
    {
        "contact_id": "con_001",
        "name": "Jane Smith",
        "email": "jane.smith@gmail.com",
        "company": "MidSize Corp",
        "title": "Full Stack Developer",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "sequence_id": "seq_001",
        "sequence_name": "Senior Engineers - Acme Corp Roles",
        "current_step": 2,
        "status": "replied",
        "last_contacted_at": "2024-02-18T09:00:00Z",
        "reply_received_at": "2024-02-18T14:30:00Z",
    },
    {
        "contact_id": "con_002",
        "name": "Michael Chen",
        "email": "michael.chen@techco.com",
        "company": "TechCo",
        "title": "Senior Software Engineer",
        "linkedin_url": "https://linkedin.com/in/michaelchen",
        "sequence_id": "seq_001",
        "sequence_name": "Senior Engineers - Acme Corp Roles",
        "current_step": 3,
        "status": "active",
        "last_contacted_at": "2024-02-20T10:00:00Z",
        "reply_received_at": None,
    },
    {
        "contact_id": "con_003",
        "name": "Priya Patel",
        "email": "priya.patel@bigdata.io",
        "company": "BigData Inc",
        "title": "ML Engineer",
        "linkedin_url": "https://linkedin.com/in/priyapatel",
        "sequence_id": "seq_002",
        "sequence_name": "ML Engineers - TechStart Inc",
        "current_step": 1,
        "status": "replied",
        "last_contacted_at": "2024-02-19T11:00:00Z",
        "reply_received_at": "2024-02-19T16:45:00Z",
    },
    {
        "contact_id": "con_004",
        "name": "Alex Rivera",
        "email": "alex.rivera@deeplearn.ai",
        "company": "DeepLearn AI",
        "title": "Senior ML Engineer",
        "linkedin_url": "https://linkedin.com/in/alexrivera",
        "sequence_id": "seq_002",
        "sequence_name": "ML Engineers - TechStart Inc",
        "current_step": 2,
        "status": "active",
        "last_contacted_at": "2024-02-21T09:00:00Z",
        "reply_received_at": None,
    },
    {
        "contact_id": "con_005",
        "name": "David Park",
        "email": "david.park@techstart.io",
        "company": "TechStart Inc",
        "title": "VP of Engineering",
        "linkedin_url": "https://linkedin.com/in/davidpark",
        "sequence_id": "seq_003",
        "sequence_name": "Client Outreach - Q1 Business Development",
        "current_step": 2,
        "status": "replied",
        "last_contacted_at": "2024-01-08T10:00:00Z",
        "reply_received_at": "2024-01-09T09:15:00Z",
    },
    {
        "contact_id": "con_006",
        "name": "Emily Watson",
        "email": "emily.watson@startup.co",
        "company": "Startup Co",
        "title": "Backend Engineer",
        "linkedin_url": "https://linkedin.com/in/emilywatson",
        "sequence_id": "seq_001",
        "sequence_name": "Senior Engineers - Acme Corp Roles",
        "current_step": 4,
        "status": "completed",
        "last_contacted_at": "2024-02-21T08:00:00Z",
        "reply_received_at": None,
    },
]

MOCK_OUTREACH_HISTORY: dict[str, list[dict[str, Any]]] = {
    "con_001": [
        {
            "event_type": "sent",
            "channel": "email",
            "timestamp": "2024-02-16T09:00:00Z",
            "step_number": 1,
            "subject": "Exciting Senior Engineer opportunity at Acme Corp",
            "body_preview": "Hi Jane, I came across your profile and thought you'd be a great fit...",
        },
        {
            "event_type": "opened",
            "channel": "email",
            "timestamp": "2024-02-16T10:15:00Z",
            "step_number": 1,
            "subject": "Exciting Senior Engineer opportunity at Acme Corp",
            "body_preview": None,
        },
        {
            "event_type": "sent",
            "channel": "linkedin",
            "timestamp": "2024-02-18T09:00:00Z",
            "step_number": 2,
            "subject": None,
            "body_preview": "Hi Jane, I sent you an email about an opportunity at Acme Corp...",
        },
        {
            "event_type": "replied",
            "channel": "email",
            "timestamp": "2024-02-18T14:30:00Z",
            "step_number": 1,
            "subject": "Re: Exciting Senior Engineer opportunity at Acme Corp",
            "body_preview": "Hi Regan, thanks for reaching out! I'd love to learn more about this role...",
        },
    ],
    "con_002": [
        {
            "event_type": "sent",
            "channel": "email",
            "timestamp": "2024-02-16T09:05:00Z",
            "step_number": 1,
            "subject": "Exciting Senior Engineer opportunity at Acme Corp",
            "body_preview": "Hi Michael, I came across your profile...",
        },
        {
            "event_type": "opened",
            "channel": "email",
            "timestamp": "2024-02-16T12:00:00Z",
            "step_number": 1,
            "subject": None,
            "body_preview": None,
        },
        {
            "event_type": "sent",
            "channel": "linkedin",
            "timestamp": "2024-02-18T09:05:00Z",
            "step_number": 2,
            "subject": None,
            "body_preview": "Hi Michael, I sent you an email about an opportunity...",
        },
        {
            "event_type": "sent",
            "channel": "email",
            "timestamp": "2024-02-20T10:00:00Z",
            "step_number": 3,
            "subject": "Re: Exciting Senior Engineer opportunity at Acme Corp",
            "body_preview": "Hi Michael, just following up on my previous message...",
        },
    ],
    "con_003": [
        {
            "event_type": "sent",
            "channel": "email",
            "timestamp": "2024-02-18T10:00:00Z",
            "step_number": 1,
            "subject": "ML Engineer role at a fast-growing AI startup",
            "body_preview": "Hi Priya, TechStart is building something exciting...",
        },
        {
            "event_type": "opened",
            "channel": "email",
            "timestamp": "2024-02-18T11:30:00Z",
            "step_number": 1,
            "subject": None,
            "body_preview": None,
        },
        {
            "event_type": "replied",
            "channel": "email",
            "timestamp": "2024-02-19T16:45:00Z",
            "step_number": 1,
            "subject": "Re: ML Engineer role at a fast-growing AI startup",
            "body_preview": "Hi, this sounds interesting! I'd be happy to chat...",
        },
    ],
}


def get_mock_sequences(
    status: str | None = None,
    tag: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return filtered mock sequences."""
    filtered = MOCK_SEQUENCES

    if status and status != "all":
        filtered = [s for s in filtered if s["status"] == status]

    if tag:
        filtered = [s for s in filtered if tag in s.get("tags", [])]

    return {
        "sequences": filtered[:limit],
        "total": len(filtered),
    }


def get_mock_sequence_stats(sequence_id: str) -> dict[str, Any] | None:
    """Return mock stats for a specific sequence."""
    for seq in MOCK_SEQUENCES:
        if seq["id"] == sequence_id:
            return {
                "sequence_id": sequence_id,
                "sequence_name": seq["name"],
                "status": seq["status"],
                "stats": seq.get("stats", {}),
                "steps": seq.get("steps", []),
            }
    return None


def get_mock_contacts(
    sequence_id: str | None = None,
    status: str | None = None,
    email: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return filtered mock contacts."""
    filtered = MOCK_CONTACTS

    if sequence_id:
        filtered = [c for c in filtered if c.get("sequence_id") == sequence_id]

    if status and status != "all":
        filtered = [c for c in filtered if c["status"] == status]

    if email:
        filtered = [c for c in filtered if c.get("email", "").lower() == email.lower()]

    return {
        "contacts": filtered[:limit],
        "total": len(filtered),
    }


def get_mock_outreach_history(contact_id: str) -> dict[str, Any] | None:
    """Return mock outreach history for a contact."""
    events = MOCK_OUTREACH_HISTORY.get(contact_id)
    if events is None:
        return None

    # Find the contact name
    contact_name = "Unknown"
    for contact in MOCK_CONTACTS:
        if contact["contact_id"] == contact_id:
            contact_name = contact["name"]
            break

    return {
        "contact_id": contact_id,
        "contact_name": contact_name,
        "events": events,
        "total_events": len(events),
    }


def get_mock_campaign_analytics(period: str = "last_30_days") -> dict[str, Any]:
    """Return mock campaign analytics."""
    return {
        "period": period,
        "total_sequences": len(MOCK_SEQUENCES),
        "total_contacts": len(MOCK_CONTACTS),
        "total_emails_sent": 45,
        "total_linkedin_messages": 18,
        "overall_reply_rate": 31.1,
        "overall_open_rate": 73.3,
        "overall_bounce_rate": 7.5,
        "top_performing_sequences": [
            {
                "id": "seq_002",
                "name": "ML Engineers - TechStart Inc",
                "reply_rate": 40.0,
                "total_contacted": 15,
            },
            {
                "id": "seq_001",
                "name": "Senior Engineers - Acme Corp Roles",
                "reply_rate": 32.0,
                "total_contacted": 25,
            },
        ],
    }
