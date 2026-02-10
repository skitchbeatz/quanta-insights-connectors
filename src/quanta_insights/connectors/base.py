"""Base connector interface for all API connectors."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolAccessLevel(StrEnum):
    """Access level for MCP tools.

    READ: Tool only reads data from upstream APIs (default).
    WRITE: Tool creates, updates, or deletes data upstream.
          Requires explicit allow_writes=True in connector config.
    """

    READ = "read"
    WRITE = "write"


class ToolDefinition(BaseModel):
    """Definition of an MCP tool provided by a connector."""

    name: str = Field(description="Tool name (must be unique across all connectors)")
    description: str = Field(description="Human-readable description of what the tool does")
    input_schema: dict[str, Any] = Field(description="JSON Schema for tool input parameters")
    access_level: ToolAccessLevel = Field(
        default=ToolAccessLevel.READ,
        description="Access level: 'read' (default) or 'write' (requires explicit opt-in)",
    )


class BaseConnector(ABC):
    """Abstract base class for all API connectors.

    Each connector (Bullhorn, LinkedIn, etc.) must implement this interface.
    The MCP server discovers and registers tools from all enabled connectors.
    """

    def __init__(self, name: str, allow_writes: bool = False) -> None:
        """Initialize the connector.

        Args:
            name: Human-readable name of the connector (e.g., "Bullhorn", "LinkedIn")
            allow_writes: If False (default), write-level tools are filtered out
                          and write tool execution is blocked. Must be explicitly
                          set to True to enable write operations.
        """
        self.name = name
        self.allow_writes = allow_writes
        self._authenticated = False

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the upstream API.

        Should establish any necessary sessions, tokens, or connections.
        Must be called before any other methods.

        Raises:
            AuthenticationError: If authentication fails
        """
        ...

    @abstractmethod
    async def _get_all_tools(self) -> list[ToolDefinition]:
        """Return all tool definitions (read + write) for this connector.

        Subclasses implement this instead of list_tools() directly.
        The base class filters out write tools when allow_writes is False.

        Returns:
            List of all tool definitions this connector can provide
        """
        ...

    async def list_tools(self) -> list[ToolDefinition]:
        """List available tools, filtered by access level.

        Write-level tools are only included when allow_writes=True.

        Returns:
            List of tool definitions that can be registered with the MCP server

        Raises:
            NotAuthenticatedError: If authenticate() has not been called
        """
        if not self.is_authenticated:
            raise NotAuthenticatedError(f"{self.name} connector not authenticated")

        all_tools = await self._get_all_tools()

        if self.allow_writes:
            return all_tools

        # Filter to read-only tools by default
        return [t for t in all_tools if t.access_level == ToolAccessLevel.READ]

    @abstractmethod
    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool (internal implementation).

        Subclasses implement this instead of execute() directly.
        The base class enforces write protection before calling this.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool input parameters

        Returns:
            Tool execution result
        """
        ...

    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a specific tool with write-protection enforcement.

        Write-level tools are blocked unless allow_writes=True.

        Args:
            tool_name: Name of the tool to execute (must be from list_tools())
            arguments: Tool input parameters (validated against the tool's schema)

        Returns:
            Tool execution result (will be serialized by the MCP server)

        Raises:
            NotAuthenticatedError: If authenticate() has not been called
            ToolNotFoundError: If tool_name is not available
            WriteProtectionError: If attempting a write tool without allow_writes
            ValidationError: If arguments don't match the tool's schema
            APIError: If the upstream API call fails
        """
        if not self.is_authenticated:
            raise NotAuthenticatedError(f"{self.name} connector not authenticated")

        # Check write protection: even if someone bypasses list_tools filtering,
        # the execute path also blocks write operations
        all_tools = await self._get_all_tools()
        tool_def = next((t for t in all_tools if t.name == tool_name), None)

        if tool_def is None:
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")

        if tool_def.access_level == ToolAccessLevel.WRITE and not self.allow_writes:
            raise WriteProtectionError(
                f"Tool '{tool_name}' requires write access. "
                f"Set allow_writes=True for the {self.name} connector to enable."
            )

        return await self._execute_tool(tool_name, arguments)

    @property
    def is_authenticated(self) -> bool:
        """Check if the connector is authenticated.

        Returns:
            True if authenticate() has completed successfully
        """
        return self._authenticated

    def _set_authenticated(self, authenticated: bool = True) -> None:
        """Set authentication status. Used by concrete implementations."""
        self._authenticated = authenticated


class ConnectorError(Exception):
    """Base exception for connector-related errors."""
    pass


class AuthenticationError(ConnectorError):
    """Raised when authentication with the upstream API fails."""
    pass


class NotAuthenticatedError(ConnectorError):
    """Raised when trying to use a connector that hasn't been authenticated."""
    pass


class ToolNotFoundError(ConnectorError):
    """Raised when requesting a tool that doesn't exist."""
    pass


class ValidationError(ConnectorError):
    """Raised when tool arguments don't match the expected schema."""
    pass


class APIError(ConnectorError):
    """Raised when the upstream API returns an error."""
    pass


class WriteProtectionError(ConnectorError):
    """Raised when attempting a write operation without explicit allow_writes=True."""
    pass
