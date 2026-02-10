# Vault AppRole + Policy Setup Guide

> **Target:** `vault.chateaumac.com`
> **Namespace:** `secret/business/quanta-insights/`
> **Auth method:** AppRole

This guide walks through creating the Vault policy and AppRole for the
`quanta-insights-connectors` service. You can run these commands from any
machine with `vault` CLI access to `vault.chateaumac.com`.

---

## Prerequisites

- `vault` CLI installed (`brew install vault` on macOS)
- Vault token with admin/root privileges (or sufficient policy to create policies and AppRoles)
- Network access to `vault.chateaumac.com`

```bash
# Set Vault address (add to ~/.zshrc for persistence)
export VAULT_ADDR="https://vault.chateaumac.com"

# Authenticate (use your preferred method)
vault login
```

---

## Step 1: Create the Vault Policy

This policy grants **read-only** access to the `quanta-insights` secrets namespace.
The service can read credentials but cannot modify them — secret management is done
by an admin, not the running service.

```bash
# Create the policy file
cat > /tmp/quanta-insights-policy.hcl << 'EOF'
# quanta-insights-connectors service policy
# Grants read-only access to connector credentials

# Read secrets (KV v2 data path)
path "secret/data/business/quanta-insights/*" {
  capabilities = ["read"]
}

# List secrets (to discover available connectors)
path "secret/metadata/business/quanta-insights/*" {
  capabilities = ["read", "list"]
}

# Deny all other paths explicitly
path "secret/data/homelab/*" {
  capabilities = ["deny"]
}

path "secret/data/business/*" {
  capabilities = ["deny"]
}

# Override the deny above for our specific namespace
path "secret/data/business/quanta-insights/*" {
  capabilities = ["read"]
}
EOF

# Write the policy to Vault
vault policy write quanta-insights /tmp/quanta-insights-policy.hcl

# Verify the policy was created
vault policy read quanta-insights
```

---

## Step 2: Enable AppRole Auth (if not already enabled)

```bash
# Check if approle is already enabled
vault auth list

# If not listed, enable it
vault auth enable approle
```

---

## Step 3: Create the AppRole

```bash
# Create the AppRole with the quanta-insights policy
vault write auth/approle/role/quanta-insights \
  token_policies="quanta-insights" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=0 \
  secret_id_num_uses=0

# Explanation of parameters:
#   token_policies    - Attach our read-only policy
#   token_ttl         - Tokens expire after 1 hour (auto-renewed by the service)
#   token_max_ttl     - Maximum token lifetime of 4 hours
#   secret_id_ttl=0   - Secret ID never expires (long-lived service)
#   secret_id_num_uses=0 - Secret ID can be used unlimited times
```

---

## Step 4: Retrieve Role ID and Secret ID

```bash
# Get the Role ID (this is not sensitive — like a username)
vault read auth/approle/role/quanta-insights/role-id

# Generate a Secret ID (this IS sensitive — like a password)
vault write -f auth/approle/role/quanta-insights/secret-id
```

**Save both values securely.** You'll need them as environment variables:

```bash
# For local development (.env file — DO NOT commit this file)
VAULT_ROLE_ID=<role-id-from-above>
VAULT_SECRET_ID=<secret-id-from-above>

# For production (set in deployment config or CI/CD secrets)
```

---

## Step 5: Store Connector Secrets

Store the API credentials for each connector. Use KV v2 format.

### Bullhorn ATS

```bash
vault kv put secret/business/quanta-insights/bullhorn \
  client_id="<bullhorn-client-id>" \
  client_secret="<bullhorn-client-secret>" \
  api_username="<bullhorn-api-username>" \
  api_password="<bullhorn-api-password>"
```

### Fathom

```bash
vault kv put secret/business/quanta-insights/fathom \
  api_key="<fathom-api-key>"
```

### Sourcewhale

```bash
vault kv put secret/business/quanta-insights/sourcewhale \
  api_key="<sourcewhale-api-key>"
```

### LinkedIn

```bash
vault kv put secret/business/quanta-insights/linkedin \
  client_id="<linkedin-client-id>" \
  client_secret="<linkedin-client-secret>" \
  redirect_uri="https://quanta-insights.chateaumac.com/auth/linkedin/callback"
```

---

## Step 6: Verify Access

Test that the AppRole can authenticate and read secrets:

```bash
# Authenticate as the AppRole
VAULT_TOKEN=$(vault write -field=token auth/approle/login \
  role_id="<role-id>" \
  secret_id="<secret-id>")

# Test reading a secret (should succeed)
VAULT_TOKEN=$VAULT_TOKEN vault kv get secret/business/quanta-insights/fathom

# Test reading a homelab secret (should be denied)
VAULT_TOKEN=$VAULT_TOKEN vault kv get secret/homelab/some-secret
# Expected: "permission denied"

# Test writing (should be denied — policy is read-only)
VAULT_TOKEN=$VAULT_TOKEN vault kv put secret/business/quanta-insights/test foo=bar
# Expected: "permission denied"
```

---

## Step 7: Configure the Service

### Local Development

Create a `.env` file (already in `.gitignore`):

```bash
# .env (DO NOT COMMIT)
VAULT_ADDR=https://vault.chateaumac.com
VAULT_ROLE_ID=<your-role-id>
VAULT_SECRET_ID=<your-secret-id>

# Connector config
ENABLED_CONNECTORS=bullhorn,fathom,sourcewhale,linkedin
BULLHORN_MOCK_MODE=false
FATHOM_MOCK_MODE=false
SOURCEWHALE_MOCK_MODE=false
LINKEDIN_MOCK_MODE=false
ALLOW_WRITES=false
```

### Docker Compose

Uncomment the Vault lines in `docker-compose.yml`:

```yaml
environment:
  - VAULT_ADDR=https://vault.chateaumac.com
  - VAULT_ROLE_ID=${VAULT_ROLE_ID}
  - VAULT_SECRET_ID=${VAULT_SECRET_ID}
```

### Production (GitHub Actions / CI/CD)

Store `VAULT_ROLE_ID` and `VAULT_SECRET_ID` as GitHub Actions secrets,
then pass them to the deployment workflow.

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `permission denied` on read | Policy not attached to AppRole | Re-run `vault write auth/approle/role/quanta-insights token_policies="quanta-insights"` |
| `no handler for route` | AppRole auth not enabled | Run `vault auth enable approle` |
| `invalid role ID` | Wrong role ID | Re-read with `vault read auth/approle/role/quanta-insights/role-id` |
| `failed to find role` | AppRole doesn't exist | Re-create with Step 3 |
| `secret not found` | Secret path wrong or not created | Verify with `vault kv list secret/business/quanta-insights/` |
| Token expired | TTL exceeded | Service auto-renews; check `token_ttl` setting |

---

## Security Notes

- **Role ID** is like a username — not highly sensitive but don't expose publicly
- **Secret ID** is like a password — treat as a secret, rotate periodically
- The policy is **read-only** — the service cannot modify secrets in Vault
- The policy **denies access** to all paths outside `secret/business/quanta-insights/`
- Token TTL of 1 hour means compromised tokens have limited blast radius
- For production, consider binding the AppRole to specific CIDR blocks
