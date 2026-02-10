#!/usr/bin/env python3
"""Simple test script to verify the MCP server works."""

import asyncio
import sys

from quanta_insights.server import QuantaInsightsServer


async def test_server():
    """Test the MCP server initialization and tool listing."""
    print("Testing Quanta Insights MCP Server...")

    # Create server instance
    server = QuantaInsightsServer()

    try:
        # Initialize the server
        await server.initialize()
        print("✅ Server initialized successfully")

        # List tools from all connectors
        all_tools = []
        for connector_name, connector in server.connectors.items():
            tools = await connector.list_tools()
            print(f"📋 {connector_name} connector: {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
                all_tools.append(tool.name)

        print(f"✅ Total tools available: {len(all_tools)}")

        # Test a tool execution
        bullhorn_connector = server.connectors.get("bullhorn")
        if bullhorn_connector:
            result = await bullhorn_connector.execute("bullhorn_search_placements", {"limit": 5})
            print("✅ Bullhorn search_placements executed successfully")
            print(f"   Found {result['total']} placements")

        linkedin_connector = server.connectors.get("linkedin")
        if linkedin_connector:
            result = await linkedin_connector.execute("linkedin_search_candidates", {"keywords": "python"})
            print("✅ LinkedIn search_candidates executed successfully")
            print(f"   Found {result['total']} candidates")

        print("\n🎉 All tests passed! MCP server is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_server())
