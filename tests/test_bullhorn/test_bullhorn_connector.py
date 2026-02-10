"""Tests for Bullhorn connector."""

import pytest

from quanta_insights.connectors.base import ToolNotFoundError
from quanta_insights.connectors.bullhorn import BullhornConnector


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_initialization():
    """Test Bullhorn connector can be initialized."""
    connector = BullhornConnector()
    assert connector.name == "Bullhorn"
    assert not connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_authenticate_mock():
    """Test Bullhorn connector authentication in mock mode."""
    connector = BullhornConnector()
    await connector.authenticate()
    assert connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_list_tools():
    """Test Bullhorn connector can list tools."""
    connector = BullhornConnector()
    await connector.authenticate()

    tools = await connector.list_tools()
    assert len(tools) == 2

    tool_names = [tool.name for tool in tools]
    assert "bullhorn_search_placements" in tool_names
    assert "bullhorn_get_placement_stats" in tool_names


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_search_placements():
    """Test Bullhorn connector search placements tool."""
    connector = BullhornConnector()
    await connector.authenticate()

    result = await connector.execute("bullhorn_search_placements", {"limit": 10})

    assert "placements" in result
    assert "total" in result
    assert "query" in result
    assert len(result["placements"]) == 2  # Mock data


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_get_placement_stats():
    """Test Bullhorn connector placement stats tool."""
    connector = BullhornConnector()
    await connector.authenticate()

    result = await connector.execute("bullhorn_get_placement_stats", {"group_by": "month"})

    assert "stats" in result
    assert "group_by" in result
    assert result["group_by"] == "month"
    assert len(result["stats"]) == 3  # Mock data


@pytest.mark.asyncio
@pytest.mark.unit
async def test_bullhorn_connector_unknown_tool():
    """Test Bullhorn connector raises error for unknown tool."""
    connector = BullhornConnector()
    await connector.authenticate()

    with pytest.raises(ToolNotFoundError):  # Should raise ToolNotFoundError
        await connector.execute("unknown_tool", {})
