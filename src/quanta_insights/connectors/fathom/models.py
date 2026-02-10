"""Pydantic models for Fathom API entities.

Based on the Fathom API reference: https://developers.fathom.ai/api-reference
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CalendarInvitee(BaseModel):
    """A person invited to a meeting via calendar."""

    name: str | None = Field(default=None, description="Display name of the invitee")
    email: str | None = Field(default=None, description="Email address of the invitee")
    domain: str | None = Field(default=None, description="Email domain (e.g. 'acme.com')")
    is_external: bool = Field(default=False, description="Whether the invitee is external to the org")
    matched_speaker: str | None = Field(
        default=None, description="Speaker name matched from transcript"
    )


class Speaker(BaseModel):
    """A speaker identified in a transcript."""

    display_name: str | None = Field(default=None, description="Display name of the speaker")
    email: str | None = Field(default=None, description="Email address if identified")


class TranscriptEntry(BaseModel):
    """A single entry in a meeting transcript."""

    speaker: Speaker = Field(description="The speaker for this transcript segment")
    text: str = Field(description="The spoken text")
    timestamp: float = Field(description="Timestamp in seconds from start of recording")


class ActionItem(BaseModel):
    """An action item extracted from a meeting."""

    description: str = Field(description="Description of the action item")
    completed: bool = Field(default=False, description="Whether the action item is completed")
    recording_timestamp: float | None = Field(
        default=None, description="Timestamp in the recording where this was discussed"
    )
    playback_url: str | None = Field(
        default=None, description="URL to play back the relevant section"
    )
    assignee: str | None = Field(default=None, description="Person assigned to this action item")


class MeetingSummary(BaseModel):
    """AI-generated summary of a meeting."""

    template_name: str | None = Field(
        default=None, description="Name of the summary template used"
    )
    markdown_formatted: str = Field(description="Summary content in markdown format")


class CrmContact(BaseModel):
    """A CRM contact matched to a meeting attendee."""

    name: str | None = Field(default=None, description="Contact name")
    email: str | None = Field(default=None, description="Contact email")
    company: str | None = Field(default=None, description="Company name")


class CrmMatch(BaseModel):
    """CRM matches found for meeting attendees."""

    contacts: list[CrmContact] = Field(default_factory=list, description="Matched CRM contacts")
    companies: list[str] = Field(default_factory=list, description="Matched company names")
    deals: list[str] = Field(default_factory=list, description="Matched deal/opportunity names")


class RecordedBy(BaseModel):
    """The user who recorded the meeting."""

    display_name: str | None = Field(default=None, description="Display name")
    email: str | None = Field(default=None, description="Email address")


class Meeting(BaseModel):
    """A Fathom meeting/recording."""

    id: str = Field(description="Unique meeting/recording ID")
    title: str | None = Field(default=None, description="Meeting title")
    recording_id: str = Field(description="Recording ID for fetching summary/transcript")
    url: str | None = Field(default=None, description="URL to view the recording in Fathom")
    created_at: datetime | None = Field(default=None, description="When the meeting was recorded")
    duration_seconds: int | None = Field(default=None, description="Duration in seconds")
    calendar_invitees: list[CalendarInvitee] = Field(
        default_factory=list, description="People invited via calendar"
    )
    recorded_by: RecordedBy | None = Field(
        default=None, description="The user who recorded the meeting"
    )
    summary: MeetingSummary | None = Field(
        default=None, description="AI summary (if requested via include_summary)"
    )
    transcript: list[TranscriptEntry] | None = Field(
        default=None, description="Full transcript (if requested via include_transcript)"
    )
    action_items: list[ActionItem] | None = Field(
        default=None, description="Extracted action items (if requested via include_action_items)"
    )
    crm_matches: CrmMatch | None = Field(
        default=None, description="CRM matches (if requested via include_crm_matches)"
    )


class MeetingListResponse(BaseModel):
    """Response from the list meetings endpoint."""

    meetings: list[Meeting] = Field(default_factory=list, description="List of meetings")
    next_cursor: str | None = Field(
        default=None, description="Cursor for next page of results"
    )
    has_more: bool = Field(default=False, description="Whether more results are available")


class WebhookRegistration(BaseModel):
    """Response from creating a webhook."""

    id: str = Field(description="Webhook ID")
    url: str = Field(description="Destination URL for webhook events")
    secret: str = Field(description="Secret for verifying webhook signatures")
    created_at: datetime | None = Field(default=None, description="When the webhook was created")
    include_transcript: bool = Field(default=False)
    include_crm_matches: bool = Field(default=False)
    include_summary: bool = Field(default=False)
    include_action_items: bool = Field(default=False)
    triggered_for: list[str] = Field(default_factory=list)
