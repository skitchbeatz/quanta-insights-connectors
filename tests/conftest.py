"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from quanta_insights.config import Settings

    return Settings(
        transport="stdio",
        log_level="DEBUG",
        vault_addr="http://mock-vault:8200",
        vault_role_id="mock-role-id",
        vault_secret_id="mock-secret-id",
        vault_namespace="secret/test",
        enabled_connectors="bullhorn,fathom,sourcewhale,linkedin",
        bullhorn_mock_mode=True,
        fathom_mock_mode=True,
        sourcewhale_mock_mode=True,
        linkedin_mock_mode=True,
        allow_writes=False,
        fathom_webhook_secret="test-webhook-secret",
        webhook_port=8081,
        tool_calls_per_minute=60,
    )
