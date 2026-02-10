"""Tests for write protection enforcement in BaseConnector."""

from typing import Any

import pytest

from quanta_insights.connectors.base import (
    BaseConnector,
    ToolAccessLevel,
    ToolDefinition,
    WriteProtectionError,
)


class MockConnectorWithWriteTools(BaseConnector):
    """Test connector that has both read and write tools."""

    def __init__(self, allow_writes: bool = False) -> None:
        super().__init__("MockConnector", allow_writes=allow_writes)

    async def authenticate(self) -> None:
        self._set_authenticated(True)

    async def _get_all_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="mock_read_tool",
                description="A read-only tool",
                input_schema={"type": "object", "properties": {}},
                access_level=ToolAccessLevel.READ,
            ),
            ToolDefinition(
                name="mock_write_tool",
                description="A write tool (creates data upstream)",
                input_schema={"type": "object", "properties": {}},
                access_level=ToolAccessLevel.WRITE,
            ),
        ]

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name == "mock_read_tool":
            return {"result": "read data"}
        elif tool_name == "mock_write_tool":
            return {"result": "wrote data"}
        else:
            from quanta_insights.connectors.base import ToolNotFoundError
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_tools_hidden_by_default():
    """Write tools should not appear in list_tools when allow_writes=False."""
    connector = MockConnectorWithWriteTools(allow_writes=False)
    await connector.authenticate()

    tools = await connector.list_tools()
    tool_names = [t.name for t in tools]

    assert "mock_read_tool" in tool_names
    assert "mock_write_tool" not in tool_names
    assert len(tools) == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_tools_visible_when_allowed():
    """Write tools should appear in list_tools when allow_writes=True."""
    connector = MockConnectorWithWriteTools(allow_writes=True)
    await connector.authenticate()

    tools = await connector.list_tools()
    tool_names = [t.name for t in tools]

    assert "mock_read_tool" in tool_names
    assert "mock_write_tool" in tool_names
    assert len(tools) == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_tool_execution_blocked_by_default():
    """Executing a write tool should raise WriteProtectionError when allow_writes=False."""
    connector = MockConnectorWithWriteTools(allow_writes=False)
    await connector.authenticate()

    with pytest.raises(WriteProtectionError) as exc_info:
        await connector.execute("mock_write_tool", {})

    assert "write access" in str(exc_info.value).lower()
    assert "MockConnector" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_write_tool_execution_allowed_when_enabled():
    """Executing a write tool should succeed when allow_writes=True."""
    connector = MockConnectorWithWriteTools(allow_writes=True)
    await connector.authenticate()

    result = await connector.execute("mock_write_tool", {})
    assert result == {"result": "wrote data"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_read_tool_always_works():
    """Read tools should always work regardless of allow_writes setting."""
    # With writes disabled
    connector_no_writes = MockConnectorWithWriteTools(allow_writes=False)
    await connector_no_writes.authenticate()
    result = await connector_no_writes.execute("mock_read_tool", {})
    assert result == {"result": "read data"}

    # With writes enabled
    connector_with_writes = MockConnectorWithWriteTools(allow_writes=True)
    await connector_with_writes.authenticate()
    result = await connector_with_writes.execute("mock_read_tool", {})
    assert result == {"result": "read data"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_default_tool_access_level_is_read():
    """ToolDefinition should default to READ access level."""
    tool = ToolDefinition(
        name="test_tool",
        description="Test",
        input_schema={"type": "object"},
    )
    assert tool.access_level == ToolAccessLevel.READ
