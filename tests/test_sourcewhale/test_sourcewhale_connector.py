"""Tests for Sourcewhale connector."""

import pytest

from quanta_insights.connectors.base import ToolNotFoundError
from quanta_insights.connectors.sourcewhale import SourcewhaleConnector


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_connector_initialization():
    """Test Sourcewhale connector can be initialized."""
    connector = SourcewhaleConnector()
    assert connector.name == "Sourcewhale"
    assert not connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_connector_authenticate_mock():
    """Test Sourcewhale connector authentication in mock mode."""
    connector = SourcewhaleConnector()
    await connector.authenticate()
    assert connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_connector_list_tools():
    """Test Sourcewhale connector can list tools."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    tools = await connector.list_tools()
    assert len(tools) == 5

    tool_names = [tool.name for tool in tools]
    assert "sourcewhale_list_sequences" in tool_names
    assert "sourcewhale_get_sequence_stats" in tool_names
    assert "sourcewhale_search_contacts" in tool_names
    assert "sourcewhale_get_outreach_history" in tool_names
    assert "sourcewhale_get_campaign_analytics" in tool_names


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_list_sequences():
    """Test Sourcewhale list sequences tool returns mock data."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_list_sequences", {})

    assert "sequences" in result
    assert "total" in result
    assert result["total"] == 3  # 3 mock sequences


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_list_sequences_filter_by_status():
    """Test Sourcewhale list sequences filtered by status."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_list_sequences", {"status": "active"})

    assert "sequences" in result
    # Should return only active sequences (seq_001 and seq_002)
    assert result["total"] == 2
    for seq in result["sequences"]:
        assert seq["status"] == "active"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_get_sequence_stats():
    """Test Sourcewhale get sequence stats tool."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_get_sequence_stats", {"sequence_id": "seq_001"})

    assert "sequence_id" in result
    assert "stats" in result
    assert result["stats"]["reply_rate"] == 32.0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_get_sequence_stats_not_found():
    """Test Sourcewhale get sequence stats for nonexistent sequence."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_get_sequence_stats", {"sequence_id": "nonexistent"})

    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_search_contacts():
    """Test Sourcewhale search contacts tool."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_search_contacts", {"sequence_id": "seq_001"})

    assert "contacts" in result
    assert "total" in result
    # seq_001 has 3 contacts: con_001, con_002, con_006
    assert result["total"] == 3


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_search_contacts_by_email():
    """Test Sourcewhale search contacts by email."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_search_contacts", {"email": "jane.smith@gmail.com"})

    assert "contacts" in result
    assert result["total"] == 1
    assert result["contacts"][0]["name"] == "Jane Smith"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_get_outreach_history():
    """Test Sourcewhale get outreach history tool."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_get_outreach_history", {"contact_id": "con_001"})

    assert "contact_id" in result
    assert "events" in result
    assert "total_events" in result
    assert result["total_events"] == 4  # con_001 has 4 events
    # Check event structure
    event = result["events"][0]
    assert "event_type" in event
    assert "channel" in event
    assert "timestamp" in event


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_get_outreach_history_not_found():
    """Test Sourcewhale get outreach history for nonexistent contact."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_get_outreach_history", {"contact_id": "nonexistent"})

    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_get_campaign_analytics():
    """Test Sourcewhale get campaign analytics tool."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    result = await connector.execute("sourcewhale_get_campaign_analytics", {"period": "last_30_days"})

    assert "period" in result
    assert result["period"] == "last_30_days"
    assert "overall_reply_rate" in result
    assert "top_performing_sequences" in result
    assert len(result["top_performing_sequences"]) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sourcewhale_unknown_tool():
    """Test Sourcewhale connector raises error for unknown tool."""
    connector = SourcewhaleConnector()
    await connector.authenticate()

    with pytest.raises(ToolNotFoundError):
        await connector.execute("unknown_tool", {})
