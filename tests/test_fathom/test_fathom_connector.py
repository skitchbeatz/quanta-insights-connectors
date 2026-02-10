"""Tests for Fathom connector."""

import pytest

from quanta_insights.connectors.base import ToolNotFoundError
from quanta_insights.connectors.fathom import FathomConnector


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_connector_initialization():
    """Test Fathom connector can be initialized."""
    connector = FathomConnector()
    assert connector.name == "Fathom"
    assert not connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_connector_authenticate_mock():
    """Test Fathom connector authentication in mock mode."""
    connector = FathomConnector()
    await connector.authenticate()
    assert connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_connector_list_tools():
    """Test Fathom connector can list tools."""
    connector = FathomConnector()
    await connector.authenticate()

    tools = await connector.list_tools()
    assert len(tools) == 5

    tool_names = [tool.name for tool in tools]
    assert "fathom_list_meetings" in tool_names
    assert "fathom_get_meeting_summary" in tool_names
    assert "fathom_get_meeting_transcript" in tool_names
    assert "fathom_search_meetings_by_domain" in tool_names
    assert "fathom_get_action_items" in tool_names


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_list_meetings():
    """Test Fathom list meetings tool returns mock data."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_list_meetings", {})

    assert "meetings" in result
    assert len(result["meetings"]) == 4  # 4 mock meetings


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_list_meetings_filter_by_domain():
    """Test Fathom list meetings filtered by domain."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_list_meetings", {"domain": "acme.com"})

    assert "meetings" in result
    # Should return meetings with acme.com invitees (mtg_001 and mtg_004)
    assert len(result["meetings"]) == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_get_meeting_summary():
    """Test Fathom get meeting summary tool."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_get_meeting_summary", {"recording_id": "rec_001"})

    assert "summary" in result
    assert "markdown_formatted" in result["summary"]
    assert "Acme Corp" in result["summary"]["markdown_formatted"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_get_meeting_summary_not_found():
    """Test Fathom get meeting summary for nonexistent recording."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_get_meeting_summary", {"recording_id": "nonexistent"})

    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_get_meeting_transcript():
    """Test Fathom get meeting transcript tool."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_get_meeting_transcript", {"recording_id": "rec_001"})

    assert "transcript" in result
    assert "entry_count" in result
    assert result["entry_count"] > 0
    # Check transcript entries have expected structure
    entry = result["transcript"][0]
    assert "speaker" in entry
    assert "text" in entry
    assert "timestamp" in entry


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_search_meetings_by_domain():
    """Test Fathom search meetings by domain tool."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_search_meetings_by_domain", {"domain": "techstart.io"})

    assert "domain" in result
    assert result["domain"] == "techstart.io"
    assert "meetings" in result
    assert result["total"] == 1  # Only mtg_003 has techstart.io invitees


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_get_action_items():
    """Test Fathom get action items tool."""
    connector = FathomConnector()
    await connector.authenticate()

    result = await connector.execute("fathom_get_action_items", {"recording_id": "rec_001"})

    assert "action_items" in result
    assert "total" in result
    assert result["total"] == 2  # rec_001 has 2 action items
    item = result["action_items"][0]
    assert "description" in item
    assert "assignee" in item


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fathom_unknown_tool():
    """Test Fathom connector raises error for unknown tool."""
    connector = FathomConnector()
    await connector.authenticate()

    with pytest.raises(ToolNotFoundError):
        await connector.execute("unknown_tool", {})
