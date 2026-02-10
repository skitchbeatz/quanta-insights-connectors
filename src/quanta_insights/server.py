"""Main MCP server for Quanta Insights Connectors."""

import asyncio
import sys
from typing import Any

import click
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import settings
from .logging import get_logger, setup_logging
from .vault_client import get_vault_client

logger = get_logger(__name__)


class QuantaInsightsServer:
    """Main MCP server that manages all connectors."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("quanta-insights-connectors")
        self.connectors: dict[str, Any] = {}  # Will hold connector instances

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools from all enabled connectors."""
            tools = []

            for connector_name, connector in self.connectors.items():
                try:
                    connector_tools = await connector.list_tools()  # type: ignore[arg-type]
                    for tool_def in connector_tools:
                        tools.append(Tool(
                            name=tool_def.name,
                            description=tool_def.description,
                            inputSchema=tool_def.input_schema,
                        ))
                        logger.debug(
                            "Registered tool",
                            tool=tool_def.name,
                            connector=connector_name,
                        )
                except Exception as e:
                    logger.error(
                        "Failed to list tools from connector",
                        connector=connector_name,
                        error=str(e),
                    )

            logger.info(
                "Listed all available tools",
                total_tools=len(tools),
                connectors=list(self.connectors.keys()),
            )
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a tool call."""
            logger.info(
                "Tool call received",
                tool=name,
                arguments=arguments,
            )

            # Find which connector handles this tool
            connector = None
            for conn in self.connectors.values():
                try:
                    tool_names = [t.name for t in await conn.list_tools()]  # type: ignore[arg-type]
                    if name in tool_names:
                        connector = conn
                        break
                except Exception:
                    continue

            if not connector:
                logger.error(
                    "Tool not found in any connector",
                    tool=name,
                    available_connectors=list(self.connectors.keys()),
                )
                raise ValueError(f"Tool '{name}' not found")

            try:
                result = await connector.execute(name, arguments)  # type: ignore[arg-type]
                logger.info(
                    "Tool executed successfully",
                    tool=name,
                    connector=connector.name,
                )

                return [TextContent(
                    type="text",
                    text=str(result) if result is not None else "null"
                )]

            except Exception as e:
                logger.error(
                    "Tool execution failed",
                    tool=name,
                    connector=connector.name,
                    error=str(e),
                )
                raise

    async def initialize(self) -> None:
        """Initialize all enabled connectors."""
        logger.info(
            "Initializing Quanta Insights MCP Server",
            transport=settings.transport,
            enabled_connectors=settings.enabled_connectors_list,
        )

        # Connect to Vault if not in mock mode for all connectors
        all_mock = all(
            settings.is_mock_mode(conn) for conn in settings.enabled_connectors_list
        )

        if not all_mock:
            try:
                get_vault_client()  # Just test connection
                logger.info("Connected to Vault successfully")
            except Exception as e:
                logger.error(
                    "Failed to connect to Vault",
                    error=str(e),
                )
                raise

        # Initialize connectors
        for connector_name in settings.enabled_connectors_list:
            try:
                # Import and instantiate the connector
                if connector_name == "bullhorn":
                    from .connectors.bullhorn import BullhornConnector
                    connector: Any = BullhornConnector()
                elif connector_name == "fathom":
                    from .connectors.fathom import FathomConnector
                    connector = FathomConnector()
                elif connector_name == "sourcewhale":
                    from .connectors.sourcewhale import SourcewhaleConnector
                    connector = SourcewhaleConnector()
                elif connector_name == "linkedin":
                    from .connectors.linkedin import LinkedInConnector
                    connector = LinkedInConnector()
                else:
                    logger.warning(
                        "Unknown connector",
                        connector=connector_name,
                    )
                    continue

                # Authenticate the connector
                await connector.authenticate()  # type: ignore[arg-type]
                self.connectors[connector_name] = connector

                logger.info(
                    "Connector initialized",
                    connector=connector_name,
                    mock_mode=settings.is_mock_mode(connector_name),
                )

            except Exception as e:
                logger.error(
                    "Failed to initialize connector",
                    connector=connector_name,
                    error=str(e),
                )
                # Continue with other connectors in dev mode
                if not settings.is_mock_mode(connector_name):
                    raise

        if not self.connectors:
            raise RuntimeError("No connectors were successfully initialized")

        logger.info(
            "All connectors initialized",
            total_connectors=len(self.connectors),
            connectors=list(self.connectors.keys()),
        )

    async def run_stdio(self) -> None:
        """Run the server with stdio transport."""
        await self.initialize()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

    async def run_http(self) -> None:
        """Run the server with HTTP transport (placeholder for future implementation)."""
        await self.initialize()
        # TODO: Implement HTTP+SSE transport
        raise NotImplementedError("HTTP transport not yet implemented")


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default=None,
    help="Transport mode (overrides env var)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default=None,
    help="Log level (overrides env var)"
)
def main(transport: str | None, log_level: str | None) -> None:
    """Main entry point for the Quanta Insights MCP server."""

    # Override settings with CLI options if provided
    if transport:
        settings.transport = transport
    if log_level:
        settings.log_level = log_level

    # Setup logging
    setup_logging()

    logger.info(
        "Starting Quanta Insights MCP Server",
        version="0.1.0",
        transport=settings.transport,
        log_level=settings.log_level,
    )

    # Run the appropriate transport
    server = QuantaInsightsServer()

    try:
        if settings.transport == "stdio":
            asyncio.run(server.run_stdio())
        else:
            asyncio.run(server.run_http())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(
            "Server failed to start",
            error=str(e),
            error_type=type(e).__name__,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
