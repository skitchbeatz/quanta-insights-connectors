"""Tests for LinkedIn connector."""

import pytest

from quanta_insights.connectors.base import ToolNotFoundError
from quanta_insights.connectors.linkedin import LinkedInConnector


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_initialization():
    """Test LinkedIn connector can be initialized."""
    connector = LinkedInConnector()
    assert connector.name == "LinkedIn Recruiter"
    assert not connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_authenticate_mock():
    """Test LinkedIn connector authentication in mock mode."""
    connector = LinkedInConnector()
    await connector.authenticate()
    assert connector.is_authenticated


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_list_tools():
    """Test LinkedIn connector can list tools."""
    connector = LinkedInConnector()
    await connector.authenticate()

    tools = await connector.list_tools()
    assert len(tools) == 2

    tool_names = [tool.name for tool in tools]
    assert "linkedin_search_candidates" in tool_names
    assert "linkedin_list_recruiter_projects" in tool_names


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_search_candidates():
    """Test LinkedIn connector search candidates tool."""
    connector = LinkedInConnector()
    await connector.authenticate()

    result = await connector.execute("linkedin_search_candidates", {"keywords": "python"})

    assert "candidates" in result
    assert "total" in result
    assert "query" in result
    assert len(result["candidates"]) == 2  # Mock data


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_list_projects():
    """Test LinkedIn connector list projects tool."""
    connector = LinkedInConnector()
    await connector.authenticate()

    result = await connector.execute("linkedin_list_recruiter_projects", {"status": "active"})

    assert "projects" in result
    assert "total" in result
    assert "query" in result
    assert len(result["projects"]) == 2  # Mock data


@pytest.mark.asyncio
@pytest.mark.unit
async def test_linkedin_connector_unknown_tool():
    """Test LinkedIn connector raises error for unknown tool."""
    connector = LinkedInConnector()
    await connector.authenticate()

    with pytest.raises(ToolNotFoundError):  # Should raise ToolNotFoundError
        await connector.execute("unknown_tool", {})
