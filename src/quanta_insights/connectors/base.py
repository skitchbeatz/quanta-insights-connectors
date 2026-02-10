"""Base connector interface for all API connectors."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Definition of an MCP tool provided by a connector."""

    name: str = Field(description="Tool name (must be unique across all connectors)")
    description: str = Field(description="Human-readable description of what the tool does")
    input_schema: dict[str, Any] = Field(description="JSON Schema for tool input parameters")


class BaseConnector(ABC):
    """Abstract base class for all API connectors.

    Each connector (Bullhorn, LinkedIn, etc.) must implement this interface.
    The MCP server discovers and registers tools from all enabled connectors.
    """

    def __init__(self, name: str) -> None:
        """Initialize the connector.

        Args:
            name: Human-readable name of the connector (e.g., "Bullhorn", "LinkedIn")
        """
        self.name = name
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
    async def list_tools(self) -> list[ToolDefinition]:
        """List all available tools from this connector.

        Returns:
            List of tool definitions that can be registered with the MCP server

        Raises:
            NotAuthenticatedError: If authenticate() has not been called
        """
        ...

    @abstractmethod
    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a specific tool.

        Args:
            tool_name: Name of the tool to execute (must be from list_tools())
            arguments: Tool input parameters (validated against the tool's schema)

        Returns:
            Tool execution result (will be serialized by the MCP server)

        Raises:
            NotAuthenticatedError: If authenticate() has not been called
            ToolNotFoundError: If tool_name is not available
            ValidationError: If arguments don't match the tool's schema
            APIError: If the upstream API call fails
        """
        ...

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
