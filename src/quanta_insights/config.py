"""Configuration management for Quanta Insights Connectors."""


from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # MCP Server Configuration
    transport: str = Field(
        default="stdio",
        description="Transport mode: 'stdio' for local IDE, 'http' for remote/production"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind to when using HTTP transport"
    )
    port: int = Field(
        default=8080,
        description="Port to bind to when using HTTP transport"
    )
    log_level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    # Vault Configuration
    vault_addr: str = Field(
        default="https://vault.chateaumac.com",
        description="Vault server address"
    )
    vault_role_id: str | None = Field(
        default=None,
        description="Vault AppRole role ID (from environment or secrets)"
    )
    vault_secret_id: str | None = Field(
        default=None,
        description="Vault AppRole secret ID (from environment or secrets)"
    )
    vault_namespace: str = Field(
        default="secret/business/quanta-insights",
        description="Vault namespace for this service"
    )

    # Connector Configuration
    enabled_connectors: str = Field(
        default="bullhorn,linkedin",
        description="Comma-separated list of enabled connectors"
    )

    @property
    def enabled_connectors_list(self) -> list[str]:
        """Get enabled connectors as a list."""
        return [conn.strip() for conn in self.enabled_connectors.split(",") if conn.strip()]

    # Mock Mode (for development without real API credentials)
    bullhorn_mock_mode: bool = Field(
        default=True,
        description="Use mock data for Bullhorn connector"
    )
    fathom_mock_mode: bool = Field(
        default=True,
        description="Use mock data for Fathom connector"
    )
    sourcewhale_mock_mode: bool = Field(
        default=True,
        description="Use mock data for Sourcewhale connector"
    )
    linkedin_mock_mode: bool = Field(
        default=True,
        description="Use mock data for LinkedIn connector"
    )

    # Write Protection (read-only by default, must be explicitly enabled)
    allow_writes: bool = Field(
        default=False,
        description="Enable write operations on connectors. False by default for safety."
    )

    # Webhook Configuration
    fathom_webhook_secret: str | None = Field(
        default=None,
        description="HMAC secret for verifying Fathom webhook signatures (from webhook registration)"
    )
    webhook_port: int = Field(
        default=8081,
        description="Port for the webhook receiver HTTP server (separate from MCP transport)"
    )

    # Rate Limiting
    tool_calls_per_minute: int = Field(
        default=60,
        description="Maximum tool calls per minute per connector"
    )

    @field_validator("transport")
    @classmethod
    def validate_transport(cls, v: str) -> str:
        if v not in {"stdio", "http"}:
            raise ValueError("transport must be 'stdio' or 'http'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @field_validator("enabled_connectors")
    @classmethod
    def validate_connectors(cls, v: str) -> str:
        """Validate connector names."""
        connectors = [conn.strip() for conn in v.split(",") if conn.strip()]
        valid_connectors = {"bullhorn", "fathom", "sourcewhale", "linkedin"}
        invalid = set(connectors) - valid_connectors
        if invalid:
            raise ValueError(f"Invalid connectors: {invalid}. Valid: {valid_connectors}")
        return v

    def is_connector_enabled(self, connector: str) -> bool:
        """Check if a specific connector is enabled."""
        return connector in self.enabled_connectors_list

    def is_mock_mode(self, connector: str) -> bool:
        """Check if a connector should use mock mode."""
        mock_mode_map = {
            "bullhorn": self.bullhorn_mock_mode,
            "fathom": self.fathom_mock_mode,
            "sourcewhale": self.sourcewhale_mock_mode,
            "linkedin": self.linkedin_mock_mode,
        }
        return mock_mode_map.get(connector, True)


# Global settings instance
settings = Settings()
