# Quanta Insights — Integration Status & Requirements

> **Living Document** — Tracks the status of every integration, what's built,
> what's blocked, and what's needed to move forward. Last updated: 2026-02-10.

---

## Summary Dashboard

| Connector | Mock Built | API Access | Real Integration | Blocker |
|-----------|-----------|------------|-----------------|---------|
| **Bullhorn ATS** | ✅ 2 tools | 🔴 Need credentials | 🔴 Not started | Scope ATS API in admin UI |
| **Fathom** | 🔴 Not started | 🟡 API key available | 🔴 Not started | Generate API key from settings |
| **Sourcewhale** | 🔴 Not started | 🔴 No API docs yet | 🔴 Not started | Locate API documentation |
| **LinkedIn RSC** | ✅ 2 tools | 🔴 Need RSC access | 🔴 Not started | Apply via LinkedIn partner program |

### Infrastructure

| Component | Status | Blocker |
|-----------|--------|---------|
| **MCP Server** | ✅ Running (stdio) | None |
| **Docker** | ✅ Container builds & runs | None |
| **Vault Client** | ✅ Code written | Need AppRole + policy |
| **Vault Policy** | 🔴 Not created | Manual setup on vault.chateaumac.com |
| **CI/CD** | 🔴 Not created | Need GitHub Actions workflows |
| **Webhook Receiver** | 🔴 Not started | Need Fathom integration first |

---

## Detailed Integration Status

### 1. Bullhorn ATS

**Current State:** Mock connector with 2 tools running in Docker.

#### What's Built
- [x] `BullhornConnector` class implementing `BaseConnector`
- [x] Mock authentication flow
- [x] `bullhorn_search_placements` tool (mock data)
- [x] `bullhorn_get_placement_stats` tool (mock data)
- [x] Unit tests (6 passing)
- [x] Docker integration

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **ATS API credentials** | 🔴 Missing | Scope in Bullhorn admin UI → generate OAuth app | Admin |
| **client_id** | 🔴 Missing | Generated when OAuth app is created | Admin |
| **client_secret** | 🔴 Missing | Generated when OAuth app is created | Admin |
| **api_username** | 🔴 Missing | Service account for API access | Admin |
| **api_password** | 🔴 Missing | Service account password | Admin |
| **ATS API permissions** | 🔴 Not scoped | Configure read-only access to: Placement, JobOrder, Candidate, Submission, ClientCorporation, ClientContact | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/bullhorn/` | Dev |
| **OAuth flow implementation** | 🔴 Not started | `bullhorn/auth.py` — authorization code + REST token | Dev |
| **API client** | 🔴 Not started | `bullhorn/client.py` — httpx async client | Dev |
| **Pydantic models** | 🔴 Not started | `bullhorn/models.py` — typed entity models | Dev |
| **Additional tools** | 🔴 Not started | 4 more tools: search_submissions, get_candidate, search_job_orders, get_client_corporation | Dev |

#### Architecture Decision: ATS API
- **Why ATS instead of back-office:** Permissions can be scoped directly in the
  Bullhorn admin UI without contacting Bullhorn support. Data access can be
  limited per entity type. Read-only enforcement at the API permission level.
- **Trade-off:** May have fewer entities available than the full back-office API.
  Need to confirm entity availability after scoping.

---

### 2. Fathom

**Current State:** No code yet. API documentation reviewed.

#### What's Built
- [ ] Nothing yet — new connector

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **API key** | 🟡 Available | Generate from Fathom settings page | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/fathom/` | Dev |
| **Mock connector** | 🔴 Not started | `fathom/connector.py` with mock data | Dev |
| **API client** | 🔴 Not started | `fathom/client.py` — httpx async client | Dev |
| **Pydantic models** | 🔴 Not started | `fathom/models.py` — Meeting, Transcript, Summary, ActionItem | Dev |
| **MCP tools** | 🔴 Not started | 5 tools: list_meetings, get_summary, get_transcript, search_by_domain, get_action_items | Dev |
| **Webhook receiver** | 🔴 Not started | `webhooks.py` — receive real-time meeting data | Dev |
| **Webhook registration** | 🔴 Not started | POST to Fathom API to register webhook endpoint | Dev |

#### API Details (from docs review)
- **Base URL:** `https://api.fathom.ai/external/v1`
- **Auth:** `X-Api-Key` header
- **Rate limits:** Headers `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`
- **Pagination:** Cursor-based (`next_cursor`)
- **Key endpoints:**
  - `GET /meetings` — list meetings (filters: date, domain, team, recorded_by)
  - `GET /recordings/{id}/summary` — get AI summary
  - `GET /recordings/{id}/transcript` — get full transcript
  - `GET /teams` — list teams
  - `GET /team-members` — list team members
  - `POST /webhooks` — register webhook for real-time data
  - `DELETE /webhooks/{id}` — remove webhook
- **Webhook payload includes:** transcript, summary, action_items, crm_matches
- **Webhook triggers:** my_recordings, shared_team_recordings, shared_external_recordings

#### Estimated Effort
- Mock connector: **2-3 hours**
- Real API integration: **1-2 days** (after API key obtained)
- Webhook receiver: **1 day**

---

### 3. Sourcewhale

**Current State:** No code yet. API documentation not yet located.

#### What's Built
- [ ] Nothing yet — new connector

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **API documentation** | 🔴 Not found | Search Sourcewhale docs/support for API reference | Admin/Dev |
| **API key** | 🔴 Not generated | Generate from Sourcewhale settings (once docs confirm method) | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/sourcewhale/` | Dev |
| **Mock connector** | 🔴 Not started | `sourcewhale/connector.py` with mock data | Dev |
| **API client** | 🔴 Not started | `sourcewhale/client.py` — httpx async client | Dev |
| **Pydantic models** | 🔴 Not started | `sourcewhale/models.py` — Sequence, CandidateOutreach, etc. | Dev |
| **MCP tools** | 🔴 Not started | 5 tools: list_sequences, get_sequence_stats, search_candidates, get_outreach_history, get_campaign_analytics | Dev |

#### Discovery Needed
- [ ] **Locate API documentation** — check Sourcewhale settings, support docs, or contact support
- [ ] **Confirm authentication method** — likely API key, but need to verify
- [ ] **Map available endpoints** — what data can we read?
- [ ] **Identify rate limits** — what are the request limits?
- [ ] **Confirm data model** — what entities are available?

#### Estimated Effort
- API discovery: **1-2 hours** (once docs found)
- Mock connector: **2-3 hours**
- Real API integration: **1-2 days** (after API key obtained)

---

### 4. LinkedIn Recruiter (RSC)

**Current State:** Mock connector with 2 tools running in Docker.

#### What's Built
- [x] `LinkedInConnector` class implementing `BaseConnector`
- [x] Mock authentication flow
- [x] `linkedin_search_candidates` tool (mock data)
- [x] `linkedin_list_recruiter_projects` tool (mock data)
- [x] Unit tests (6 passing)
- [x] Docker integration

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **RSC API access** | 🔴 Not applied | Apply through LinkedIn partner program | Admin |
| **OAuth app registration** | 🔴 Not started | Register app in LinkedIn Developer Portal | Admin |
| **client_id** | 🔴 Missing | Generated when OAuth app is created | Admin |
| **client_secret** | 🔴 Missing | Generated when OAuth app is created | Admin |
| **Recruiter seats** | ❓ Unknown | Confirm active Recruiter seat licenses | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/linkedin/` | Dev |
| **OAuth flow implementation** | 🔴 Not started | `linkedin/auth.py` — 3-legged OAuth 2.0 | Dev |
| **API client** | 🔴 Not started | `linkedin/client.py` — httpx async client | Dev |
| **Pydantic models** | 🔴 Not started | `linkedin/models.py` — typed entity models | Dev |
| **Additional tools** | 🔴 Not started | 2 more tools: get_profile, get_inmail_history | Dev |

#### Timeline Note
LinkedIn RSC API access typically takes **2-4 weeks** for approval. This is the
longest lead time of all integrations. Apply immediately.

---

## Vault Integration Status

### Current State
- ✅ `vault_client.py` written with AppRole authentication
- ✅ Configuration supports Vault address, role_id, secret_id
- 🔴 No Vault policy created yet
- 🔴 No AppRole created yet
- 🔴 No secrets stored yet

### What's Needed

| Requirement | Status | Action |
|-------------|--------|--------|
| **Vault policy** | 🔴 Not created | Create `quanta-insights-policy.hcl` on vault.chateaumac.com |
| **AppRole** | 🔴 Not created | Create `quanta-insights` AppRole bound to policy |
| **role_id** | 🔴 Not generated | Generated when AppRole is created |
| **secret_id** | 🔴 Not generated | Generated when AppRole is created |
| **Bullhorn secrets** | 🔴 Not stored | Store at `secret/business/quanta-insights/bullhorn/` |
| **Fathom secrets** | 🔴 Not stored | Store at `secret/business/quanta-insights/fathom/` |
| **Sourcewhale secrets** | 🔴 Not stored | Store at `secret/business/quanta-insights/sourcewhale/` |
| **LinkedIn secrets** | 🔴 Not stored | Store at `secret/business/quanta-insights/linkedin/` |

### Vault Policy Template

```hcl
# quanta-insights-policy.hcl
path "secret/data/business/quanta-insights/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/business/quanta-insights/*" {
  capabilities = ["read", "list"]
}
```

---

## Code Quality Status

| Check | Status | Command |
|-------|--------|---------|
| **Unit tests** | ✅ 12 passing | `python -m pytest tests/ -v` |
| **Linting** | ✅ Clean | `ruff check .` |
| **Type checking** | ⚠️ Minor issues | `mypy src/` |
| **Formatting** | ✅ Clean | `black --check .` |
| **Docker build** | ✅ Builds | `docker compose build` |
| **Docker run** | ✅ Runs | `docker compose up quanta-insights` |

---

## Priority Action Items (Ordered)

### Immediate (No blockers — can do now)
1. **Generate Fathom API key** — go to Fathom settings, create key
2. **Build Fathom mock connector** — no API key needed for mock
3. **Build Sourcewhale mock connector** — no API key needed for mock
4. **Search for Sourcewhale API docs** — check settings, support, contact

### Short-term (Need admin action)
5. **Scope Bullhorn ATS API** — log into Bullhorn admin, configure permissions
6. **Generate Bullhorn API credentials** — create OAuth app in admin UI
7. **Create Vault policy + AppRole** — manual setup on vault.chateaumac.com

### Medium-term (External dependencies)
8. **Apply for LinkedIn RSC API** — submit application via partner program
9. **Implement real Fathom integration** — after API key obtained
10. **Implement real Bullhorn integration** — after credentials obtained
11. **Implement real Sourcewhale integration** — after API key obtained

### Long-term (Waiting on approvals)
12. **Implement real LinkedIn integration** — after RSC API approved (2-4 weeks)

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-10 | Initial version — full inventory of all 4 integrations |
