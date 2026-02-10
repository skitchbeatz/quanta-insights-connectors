"""Structured logging configuration for Quanta Insights Connectors."""

import sys
from typing import Any, Dict, Mapping, MutableMapping

import structlog
from structlog.stdlib import LoggerFactory

from .config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""

    # Configure structlog to use standard library logging
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Filter sensitive data
            _filter_sensitive_data,
            # JSON renderer for production, pretty for development
            structlog.processors.JSONRenderer() if settings.log_level != "DEBUG"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    import logging

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("hvac").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _filter_sensitive_data(
    logger: Any, 
    method_name: str, 
    event_dict: MutableMapping[str, Any]
) -> Mapping[str, Any]:
    """Filter sensitive data from log entries."""

    sensitive_keys = {
        "token", "secret", "password", "key", "credential", "auth",
        "authorization", "bearer", "client_secret", "api_key",
    }

    def _filter_value(key: str, value: Any) -> Any:
        if isinstance(key, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
            return "***REDACTED***"
        elif isinstance(value, dict):
            return {k: _filter_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_filter_value(f"{key}[{i}]", item) for i, item in enumerate(value)]
        return value

    # Filter all keys and values in the event dict
    filtered_event = {}
    for key, value in event_dict.items():
        filtered_event[key] = _filter_value(key, value)

    return filtered_event


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with the given name."""
    return structlog.get_logger(name)
