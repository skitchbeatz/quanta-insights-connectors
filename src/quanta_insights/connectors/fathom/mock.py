"""Mock data layer for Fathom connector.

Provides realistic fake meeting data for development without API credentials.
Mirrors the real Fathom API response structure so switching to real API
is a config change, not a code change.
"""

from typing import Any

MOCK_MEETINGS: list[dict[str, Any]] = [
    {
        "id": "mtg_001",
        "title": "Discovery Call - Acme Corp (Senior Engineer Role)",
        "recording_id": "rec_001",
        "url": "https://fathom.video/recordings/rec_001",
        "created_at": "2024-02-15T14:30:00Z",
        "duration_seconds": 2700,
        "calendar_invitees": [
            {
                "name": "Sarah Miller",
                "email": "sarah.miller@acme.com",
                "domain": "acme.com",
                "is_external": True,
                "matched_speaker": "Sarah Miller",
            },
            {
                "name": "Regan McCullough",
                "email": "regan@quantainsights.com",
                "domain": "quantainsights.com",
                "is_external": False,
                "matched_speaker": "Regan McCullough",
            },
        ],
        "recorded_by": {
            "display_name": "Regan McCullough",
            "email": "regan@quantainsights.com",
        },
    },
    {
        "id": "mtg_002",
        "title": "Candidate Screen - Jane Smith (Full Stack Developer)",
        "recording_id": "rec_002",
        "url": "https://fathom.video/recordings/rec_002",
        "created_at": "2024-02-16T10:00:00Z",
        "duration_seconds": 1800,
        "calendar_invitees": [
            {
                "name": "Jane Smith",
                "email": "jane.smith@gmail.com",
                "domain": "gmail.com",
                "is_external": True,
                "matched_speaker": "Jane Smith",
            },
            {
                "name": "Regan McCullough",
                "email": "regan@quantainsights.com",
                "domain": "quantainsights.com",
                "is_external": False,
                "matched_speaker": "Regan McCullough",
            },
        ],
        "recorded_by": {
            "display_name": "Regan McCullough",
            "email": "regan@quantainsights.com",
        },
    },
    {
        "id": "mtg_003",
        "title": "Client Sales Meeting - TechStart Inc",
        "recording_id": "rec_003",
        "url": "https://fathom.video/recordings/rec_003",
        "created_at": "2024-02-17T15:00:00Z",
        "duration_seconds": 3600,
        "calendar_invitees": [
            {
                "name": "David Park",
                "email": "david.park@techstart.io",
                "domain": "techstart.io",
                "is_external": True,
                "matched_speaker": "David Park",
            },
            {
                "name": "Lisa Wong",
                "email": "lisa.wong@techstart.io",
                "domain": "techstart.io",
                "is_external": True,
                "matched_speaker": "Lisa Wong",
            },
            {
                "name": "Regan McCullough",
                "email": "regan@quantainsights.com",
                "domain": "quantainsights.com",
                "is_external": False,
                "matched_speaker": "Regan McCullough",
            },
        ],
        "recorded_by": {
            "display_name": "Regan McCullough",
            "email": "regan@quantainsights.com",
        },
    },
    {
        "id": "mtg_004",
        "title": "Discovery Call - Acme Corp (Product Manager Role)",
        "recording_id": "rec_004",
        "url": "https://fathom.video/recordings/rec_004",
        "created_at": "2024-02-20T11:00:00Z",
        "duration_seconds": 2400,
        "calendar_invitees": [
            {
                "name": "Sarah Miller",
                "email": "sarah.miller@acme.com",
                "domain": "acme.com",
                "is_external": True,
                "matched_speaker": "Sarah Miller",
            },
            {
                "name": "Tom Harris",
                "email": "tom.harris@acme.com",
                "domain": "acme.com",
                "is_external": True,
                "matched_speaker": "Tom Harris",
            },
            {
                "name": "Regan McCullough",
                "email": "regan@quantainsights.com",
                "domain": "quantainsights.com",
                "is_external": False,
                "matched_speaker": "Regan McCullough",
            },
        ],
        "recorded_by": {
            "display_name": "Regan McCullough",
            "email": "regan@quantainsights.com",
        },
    },
]

MOCK_SUMMARIES: dict[str, dict[str, Any]] = {
    "rec_001": {
        "template_name": "Discovery Call",
        "markdown_formatted": (
            "## Discovery Call - Acme Corp (Senior Engineer Role)\n\n"
            "### Key Points\n"
            "- Acme Corp is looking for a **Senior Backend Engineer** with Python and AWS experience\n"
            "- Team size: 8 engineers, growing to 12 by Q3\n"
            "- Remote-first, but prefer candidates in EST/CST time zones\n"
            "- Budget: $160K-$190K base + equity\n"
            "- Timeline: Want to fill within 4-6 weeks\n\n"
            "### Requirements\n"
            "- 5+ years Python experience\n"
            "- AWS (ECS, Lambda, RDS)\n"
            "- Experience with event-driven architectures\n"
            "- Nice to have: Kubernetes, Terraform\n\n"
            "### Next Steps\n"
            "- Send 3-5 candidate profiles by end of week\n"
            "- Schedule follow-up for candidate review next Tuesday\n"
        ),
    },
    "rec_002": {
        "template_name": "Candidate Screen",
        "markdown_formatted": (
            "## Candidate Screen - Jane Smith\n\n"
            "### Background\n"
            "- 6 years experience as Full Stack Developer\n"
            "- Currently at MidSize Corp, looking for growth opportunity\n"
            "- Strong Python/Django backend, React frontend\n"
            "- AWS certified (Solutions Architect Associate)\n\n"
            "### Strengths\n"
            "- Solid system design thinking\n"
            "- Experience leading small teams (2-3 engineers)\n"
            "- Good communication skills\n\n"
            "### Concerns\n"
            "- Limited event-driven architecture experience\n"
            "- Salary expectation: $175K (within Acme range)\n\n"
            "### Fit Assessment\n"
            "- **Strong match for Acme Corp Senior Engineer role**\n"
            "- Recommend submitting to client\n"
        ),
    },
    "rec_003": {
        "template_name": "Client Sales Meeting",
        "markdown_formatted": (
            "## Client Sales Meeting - TechStart Inc\n\n"
            "### Company Overview\n"
            "- Series B startup, 50 employees, growing fast\n"
            "- Building AI-powered logistics platform\n"
            "- Engineering team: 15, need to double by year end\n\n"
            "### Hiring Needs\n"
            "- 3x Senior Backend Engineers (Python/Go)\n"
            "- 2x ML Engineers\n"
            "- 1x Engineering Manager\n\n"
            "### Terms Discussed\n"
            "- Contingency fee: 20% of first year salary\n"
            "- Exclusivity on ML Engineer roles\n"
            "- 90-day guarantee period\n\n"
            "### Next Steps\n"
            "- Send MSA for review\n"
            "- Start sourcing ML Engineers immediately\n"
            "- Schedule intake calls for each role\n"
        ),
    },
    "rec_004": {
        "template_name": "Discovery Call",
        "markdown_formatted": (
            "## Discovery Call - Acme Corp (Product Manager Role)\n\n"
            "### Key Points\n"
            "- New role: **Senior Product Manager** for platform team\n"
            "- Reports to VP of Product (Tom Harris)\n"
            "- Focus: developer experience and internal tooling\n"
            "- Budget: $150K-$180K base + equity\n\n"
            "### Requirements\n"
            "- 5+ years PM experience, preferably in developer tools\n"
            "- Technical background (former engineer preferred)\n"
            "- Experience with B2B SaaS products\n"
            "- Strong data-driven decision making\n\n"
            "### Next Steps\n"
            "- Draft job description for review\n"
            "- Begin sourcing candidates next week\n"
        ),
    },
}

MOCK_TRANSCRIPTS: dict[str, list[dict[str, Any]]] = {
    "rec_001": [
        {"speaker": {"display_name": "Regan McCullough", "email": "regan@quantainsights.com"}, "text": "Thanks for taking the time today, Sarah. I'd love to learn more about the Senior Engineer role you're looking to fill.", "timestamp": 15.0},
        {"speaker": {"display_name": "Sarah Miller", "email": "sarah.miller@acme.com"}, "text": "Of course! We're really excited about this hire. Our backend team has been growing and we need someone senior to help architect our next generation of services.", "timestamp": 22.0},
        {"speaker": {"display_name": "Regan McCullough", "email": "regan@quantainsights.com"}, "text": "Great. Can you walk me through the tech stack and what the day-to-day would look like?", "timestamp": 35.0},
        {"speaker": {"display_name": "Sarah Miller", "email": "sarah.miller@acme.com"}, "text": "Sure. We're primarily Python on the backend, running on AWS. We use ECS for container orchestration, Lambda for serverless functions, and RDS for our databases. The team is moving toward event-driven architecture using SNS and SQS.", "timestamp": 42.0},
        {"speaker": {"display_name": "Regan McCullough", "email": "regan@quantainsights.com"}, "text": "What's the compensation range for this role?", "timestamp": 120.0},
        {"speaker": {"display_name": "Sarah Miller", "email": "sarah.miller@acme.com"}, "text": "We're looking at 160 to 190 base, plus equity. We're also flexible on remote work, though we prefer someone in Eastern or Central time zones.", "timestamp": 128.0},
    ],
    "rec_002": [
        {"speaker": {"display_name": "Regan McCullough", "email": "regan@quantainsights.com"}, "text": "Hi Jane, thanks for joining. I'd love to hear about your background and what you're looking for in your next role.", "timestamp": 10.0},
        {"speaker": {"display_name": "Jane Smith", "email": "jane.smith@gmail.com"}, "text": "Thanks Regan. I've been at MidSize Corp for about 3 years now. I'm a full stack developer working primarily with Python and Django on the backend, and React on the frontend.", "timestamp": 18.0},
        {"speaker": {"display_name": "Regan McCullough", "email": "regan@quantainsights.com"}, "text": "What's motivating you to look for something new?", "timestamp": 45.0},
        {"speaker": {"display_name": "Jane Smith", "email": "jane.smith@gmail.com"}, "text": "I'm looking for more growth opportunity. I've been leading a small team of 2-3 engineers and I want to take on more architectural responsibility. I'm also interested in working with more modern cloud infrastructure.", "timestamp": 52.0},
    ],
}

MOCK_ACTION_ITEMS: dict[str, list[dict[str, Any]]] = {
    "rec_001": [
        {
            "description": "Send 3-5 candidate profiles for Senior Engineer role to Sarah Miller",
            "completed": False,
            "recording_timestamp": 2400.0,
            "playback_url": "https://fathom.video/recordings/rec_001?t=2400",
            "assignee": "Regan McCullough",
        },
        {
            "description": "Schedule follow-up meeting with Acme Corp for candidate review (next Tuesday)",
            "completed": False,
            "recording_timestamp": 2550.0,
            "playback_url": "https://fathom.video/recordings/rec_001?t=2550",
            "assignee": "Regan McCullough",
        },
    ],
    "rec_002": [
        {
            "description": "Submit Jane Smith's profile to Acme Corp for Senior Engineer role",
            "completed": False,
            "recording_timestamp": 1650.0,
            "playback_url": "https://fathom.video/recordings/rec_002?t=1650",
            "assignee": "Regan McCullough",
        },
    ],
    "rec_003": [
        {
            "description": "Send MSA to TechStart Inc for review",
            "completed": False,
            "recording_timestamp": 3200.0,
            "playback_url": "https://fathom.video/recordings/rec_003?t=3200",
            "assignee": "Regan McCullough",
        },
        {
            "description": "Start sourcing ML Engineers for TechStart Inc",
            "completed": False,
            "recording_timestamp": 3350.0,
            "playback_url": "https://fathom.video/recordings/rec_003?t=3350",
            "assignee": "Regan McCullough",
        },
        {
            "description": "Schedule intake calls for each TechStart role",
            "completed": False,
            "recording_timestamp": 3450.0,
            "playback_url": "https://fathom.video/recordings/rec_003?t=3450",
            "assignee": "Regan McCullough",
        },
    ],
    "rec_004": [
        {
            "description": "Draft job description for Acme Corp Product Manager role",
            "completed": False,
            "recording_timestamp": 2100.0,
            "playback_url": "https://fathom.video/recordings/rec_004?t=2100",
            "assignee": "Regan McCullough",
        },
        {
            "description": "Begin sourcing PM candidates next week",
            "completed": False,
            "recording_timestamp": 2250.0,
            "playback_url": "https://fathom.video/recordings/rec_004?t=2250",
            "assignee": "Regan McCullough",
        },
    ],
}


def get_mock_meetings(
    domain: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return filtered mock meetings.

    Args:
        domain: Filter by invitee email domain
        date_from: Filter meetings after this date (ISO format)
        date_to: Filter meetings before this date (ISO format)
        limit: Maximum number of results
    """
    filtered = MOCK_MEETINGS

    if domain:
        filtered = [
            m for m in filtered
            if any(
                inv.get("domain", "").lower() == domain.lower()
                for inv in m.get("calendar_invitees", [])
            )
        ]

    if date_from:
        filtered = [
            m for m in filtered
            if m.get("created_at", "") >= date_from
        ]

    if date_to:
        filtered = [
            m for m in filtered
            if m.get("created_at", "") <= date_to
        ]

    return {
        "meetings": filtered[:limit],
        "next_cursor": None,
        "has_more": len(filtered) > limit,
    }


def get_mock_summary(recording_id: str) -> dict[str, Any] | None:
    """Return mock summary for a recording."""
    return MOCK_SUMMARIES.get(recording_id)


def get_mock_transcript(recording_id: str) -> list[dict[str, Any]] | None:
    """Return mock transcript for a recording."""
    return MOCK_TRANSCRIPTS.get(recording_id)


def get_mock_action_items(recording_id: str) -> list[dict[str, Any]] | None:
    """Return mock action items for a recording."""
    return MOCK_ACTION_ITEMS.get(recording_id)
