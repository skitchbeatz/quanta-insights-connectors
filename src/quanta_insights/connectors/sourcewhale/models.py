"""Pydantic models for Sourcewhale API entities.

NOTE: These models are PROVISIONAL. Sourcewhale's API documentation is not
publicly available. Models are inferred from common outreach platform patterns
(Outreach.io, Salesloft, Apollo) and Sourcewhale's known feature set.
They will be updated once official API documentation is obtained.

Known Sourcewhale features (from product marketing):
- Multi-channel outreach sequences (email + LinkedIn)
- Candidate/contact management
- Campaign analytics and reporting
- CRM integrations
- API key authentication (confirmed via admin console)
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SequenceStep(BaseModel):
    """A single step in an outreach sequence."""

    step_number: int = Field(description="Order of this step in the sequence")
    channel: str = Field(description="Channel: 'email', 'linkedin', or 'phone'")
    delay_days: int = Field(default=0, description="Days to wait after previous step")
    subject_template: str | None = Field(
        default=None, description="Email subject template (email channel only)"
    )
    body_preview: str | None = Field(
        default=None, description="Preview of the message body template"
    )


class SequenceStats(BaseModel):
    """Aggregate statistics for a sequence."""

    total_contacted: int = Field(default=0, description="Total contacts added to sequence")
    total_replied: int = Field(default=0, description="Total contacts who replied")
    total_opened: int = Field(default=0, description="Total email opens")
    total_clicked: int = Field(default=0, description="Total link clicks")
    total_bounced: int = Field(default=0, description="Total bounced emails")
    reply_rate: float = Field(default=0.0, description="Reply rate as percentage")
    open_rate: float = Field(default=0.0, description="Open rate as percentage")
    bounce_rate: float = Field(default=0.0, description="Bounce rate as percentage")


class Sequence(BaseModel):
    """An outreach sequence (campaign)."""

    id: str = Field(description="Unique sequence ID")
    name: str = Field(description="Sequence name")
    status: str = Field(description="Status: 'active', 'paused', 'completed', 'draft'")
    created_at: datetime | None = Field(default=None, description="When the sequence was created")
    updated_at: datetime | None = Field(default=None, description="When the sequence was last updated")
    steps: list[SequenceStep] = Field(default_factory=list, description="Steps in the sequence")
    stats: SequenceStats | None = Field(default=None, description="Aggregate statistics")
    tags: list[str] = Field(default_factory=list, description="Tags/labels for organization")


class ContactOutreach(BaseModel):
    """A contact's outreach status within a sequence."""

    contact_id: str = Field(description="Unique contact ID")
    name: str = Field(description="Contact full name")
    email: str | None = Field(default=None, description="Contact email address")
    company: str | None = Field(default=None, description="Contact's company")
    title: str | None = Field(default=None, description="Contact's job title")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    sequence_id: str | None = Field(default=None, description="Current sequence ID")
    sequence_name: str | None = Field(default=None, description="Current sequence name")
    current_step: int | None = Field(default=None, description="Current step number in sequence")
    status: str = Field(
        description="Outreach status: 'active', 'replied', 'bounced', 'opted_out', 'completed'"
    )
    last_contacted_at: datetime | None = Field(
        default=None, description="When the contact was last contacted"
    )
    reply_received_at: datetime | None = Field(
        default=None, description="When a reply was received (if any)"
    )


class OutreachEvent(BaseModel):
    """A single outreach event (email sent, opened, replied, etc.)."""

    event_type: str = Field(
        description="Event type: 'sent', 'opened', 'clicked', 'replied', 'bounced', 'opted_out'"
    )
    channel: str = Field(description="Channel: 'email' or 'linkedin'")
    timestamp: datetime | None = Field(default=None, description="When the event occurred")
    step_number: int | None = Field(default=None, description="Which sequence step triggered this")
    subject: str | None = Field(default=None, description="Email subject (if email)")
    body_preview: str | None = Field(default=None, description="Preview of message body")


class OutreachHistory(BaseModel):
    """Full outreach history for a contact."""

    contact_id: str = Field(description="Contact ID")
    contact_name: str = Field(description="Contact name")
    events: list[OutreachEvent] = Field(default_factory=list, description="Chronological events")
    total_events: int = Field(default=0, description="Total number of events")


class CampaignAnalytics(BaseModel):
    """Aggregated analytics across sequences/campaigns."""

    period: str = Field(description="Time period for analytics")
    total_sequences: int = Field(default=0, description="Number of active sequences")
    total_contacts: int = Field(default=0, description="Total contacts across all sequences")
    total_emails_sent: int = Field(default=0, description="Total emails sent")
    total_linkedin_messages: int = Field(default=0, description="Total LinkedIn messages sent")
    overall_reply_rate: float = Field(default=0.0, description="Overall reply rate")
    overall_open_rate: float = Field(default=0.0, description="Overall open rate")
    overall_bounce_rate: float = Field(default=0.0, description="Overall bounce rate")
    top_performing_sequences: list[dict[str, Any]] = Field(
        default_factory=list, description="Top sequences by reply rate"
    )
