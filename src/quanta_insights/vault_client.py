"""Vault client for secure credential management."""

from typing import Any

import hvac
from hvac.exceptions import VaultError

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)


class VaultClient:
    """Vault client for retrieving secrets using AppRole authentication."""

    def __init__(self) -> None:
        """Initialize the Vault client."""
        self.client: hvac.Client | None = None
        self._authenticated = False

    def connect(self) -> None:
        """Connect to Vault and authenticate using AppRole."""
        try:
            self.client = hvac.Client(
                url=settings.vault_addr,
                verify=True,  # Use TLS verification
            )

            # Check if we have the required credentials
            if not settings.vault_role_id or not settings.vault_secret_id:
                raise VaultError(
                    "VAULT_ROLE_ID and VAULT_SECRET_ID must be set for AppRole authentication"
                )

            # Authenticate using AppRole
            auth_response = self.client.auth.approle.login(
                role_id=settings.vault_role_id,
                secret_id=settings.vault_secret_id,
            )

            if not auth_response or "auth" not in auth_response:
                raise VaultError("Failed to authenticate with Vault using AppRole")

            # Set the token for subsequent requests
            self.client.token = auth_response["auth"]["client_token"]

            # Verify the authentication worked
            if not self.client.is_authenticated():
                raise VaultError("Vault authentication failed")

            self._authenticated = True
            logger.info(
                "Successfully authenticated with Vault",
                vault_addr=settings.vault_addr,
                namespace=settings.vault_namespace,
            )

        except Exception as e:
            logger.error(
                "Failed to connect to Vault",
                vault_addr=settings.vault_addr,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def get_secret(self, path: str) -> dict[str, Any]:
        """Retrieve a secret from Vault.

        Args:
            path: Secret path (relative to the configured namespace)

        Returns:
            Dictionary containing the secret data

        Raises:
            VaultError: If the secret cannot be retrieved
        """
        if not self._authenticated or not self.client:
            raise VaultError("Vault client is not authenticated")

        full_path = f"{settings.vault_namespace}/{path}"

        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=full_path)

            if not response or "data" not in response:
                raise VaultError(f"No data found at path: {full_path}")

            # Extract the actual secret data
            secret_data: dict[str, Any] = response["data"]["data"]

            logger.debug(
                "Retrieved secret from Vault",
                path=full_path,
                keys=list(secret_data.keys()),
            )

            return secret_data

        except hvac.exceptions.InvalidPath:
            logger.error(
                "Secret path not found in Vault",
                path=full_path,
            )
            raise VaultError(f"Secret not found: {full_path}") from None
        except Exception as e:
            logger.error(
                "Failed to retrieve secret from Vault",
                path=full_path,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise VaultError(f"Failed to retrieve secret {full_path}: {e}") from e

    def get_connector_secrets(self, connector: str) -> dict[str, Any]:
        """Get all secrets for a specific connector.

        Args:
            connector: Connector name (e.g., "bullhorn", "linkedin")

        Returns:
            Dictionary containing all secrets for the connector
        """
        return self.get_secret(f"{connector}/")

    def health_check(self) -> bool:
        """Check if Vault is accessible and authenticated.

        Returns:
            True if Vault is healthy and authenticated
        """
        if not self._authenticated or not self.client:
            return False

        try:
            # Try to read our own token info
            self.client.auth.token.lookup_self()
            return True
        except Exception:
            return False

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated with Vault."""
        return self._authenticated


# Global Vault client instance
_vault_client: VaultClient | None = None


def get_vault_client() -> VaultClient:
    """Get the global Vault client instance.

    Returns:
        VaultClient instance (connected and authenticated)

    Raises:
        VaultError: If connection fails
    """
    global _vault_client

    if _vault_client is None:
        _vault_client = VaultClient()
        _vault_client.connect()

    return _vault_client
