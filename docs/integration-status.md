# Quanta Insights — Integration Status & Requirements

> **Living Document** — Tracks the status of every integration, what's built,
> what's blocked, and what's needed to move forward. Last updated: 2026-02-10.

---

## Summary Dashboard

| Connector | Mock Built | API Access | Real Integration | Blocker |
|-----------|-----------|------------|-----------------|---------|
| **Bullhorn ATS** | ✅ 2 tools | 🔴 Need credentials | 🔴 Not started | Scope ATS API in admin UI |
| **Fathom** | ✅ 5 tools + models | 🟡 API key available | 🔴 Not started | Generate API key from settings |
| **Sourcewhale** | ✅ 5 tools + models (provisional) | 🔴 No API docs yet | 🔴 Not started | Locate API documentation |
| **LinkedIn RSC** | ✅ 2 tools | 🔴 Need RSC access | 🔴 Not started | Apply via LinkedIn partner program |

### Infrastructure

| Component | Status | Blocker |
|-----------|--------|---------|
| **MCP Server** | ✅ Running (stdio), 14 tools registered | None |
| **Docker** | ✅ Container builds & runs | None |
| **Write Protection** | ✅ Enforced at BaseConnector level | None |
| **Vault Client** | ✅ Code written | Need AppRole + policy |
| **Vault Setup Guide** | ✅ `docs/vault-setup.md` | Manual steps on vault.chateaumac.com |
| **Vault Policy** | 🔴 Not created | Manual setup on vault.chateaumac.com |
| **CI/CD** | ✅ `ci.yml` + `deploy.yml` | Need GitHub secrets configured |
| **Webhook Receiver** | ✅ Starlette app with HMAC verification | None |
| **Fathom API Client** | ✅ httpx async client with retries + pagination | Need API key |
| **Sourcewhale API Client** | ✅ Provisional httpx client | Need API docs + key |
| **Tests** | ✅ 54 passing | None |

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

**Current State:** Mock connector with 5 tools and full Pydantic models. 11 unit tests passing.

#### What's Built
- [x] `FathomConnector` class implementing `BaseConnector`
- [x] Mock authentication flow
- [x] `fathom_list_meetings` tool (mock data, filters by date/domain)
- [x] `fathom_get_meeting_summary` tool (mock AI summaries)
- [x] `fathom_get_meeting_transcript` tool (mock speaker-attributed transcripts)
- [x] `fathom_search_meetings_by_domain` tool (mock domain search)
- [x] `fathom_get_action_items` tool (mock action items with assignees)
- [x] Pydantic models: Meeting, TranscriptEntry, MeetingSummary, ActionItem, CalendarInvitee, etc.
- [x] Realistic mock data: discovery calls, candidate screens, client meetings
- [x] Unit tests (11 passing)

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **API key** | 🟡 Available | Generate from Fathom settings page | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/fathom/` | Dev |
| **Mock connector** | ✅ Complete | 5 tools with realistic data | Dev |
| **Pydantic models** | ✅ Complete | `fathom/models.py` — full typed models | Dev |
| **API client** | 🔴 Not started | `fathom/client.py` — httpx async client | Dev |
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

**Current State:** Mock connector with 5 tools and provisional Pydantic models. 13 unit tests passing.

> **NOTE:** API documentation is not publicly available. Models are inferred from common
> outreach platform patterns (Outreach.io, Salesloft, Apollo) and Sourcewhale's known
> feature set. Will be updated once official API docs are obtained.

#### What's Built
- [x] `SourcewhaleConnector` class implementing `BaseConnector`
- [x] Mock authentication flow
- [x] `sourcewhale_list_sequences` tool (mock campaigns with steps + stats)
- [x] `sourcewhale_get_sequence_stats` tool (mock performance metrics)
- [x] `sourcewhale_search_contacts` tool (mock contacts by sequence/status/email)
- [x] `sourcewhale_get_outreach_history` tool (mock event timeline)
- [x] `sourcewhale_get_campaign_analytics` tool (mock aggregated analytics)
- [x] Pydantic models (provisional): Sequence, SequenceStep, ContactOutreach, OutreachEvent, CampaignAnalytics
- [x] Realistic mock data: engineering sequences, ML hiring, client outreach
- [x] Unit tests (13 passing)

#### What's Needed to Go Live

| Requirement | Status | Action | Owner |
|-------------|--------|--------|-------|
| **API documentation** | 🔴 Not found | Search Sourcewhale docs/support for API reference | Admin/Dev |
| **API key** | 🔴 Not generated | Generate from Sourcewhale settings (once docs confirm method) | Admin |
| **Vault secret** | 🔴 Not created | Store at `secret/business/quanta-insights/sourcewhale/` | Dev |
| **Mock connector** | ✅ Complete | 5 tools with provisional models | Dev |
| **Pydantic models** | ✅ Complete (provisional) | Will update when API docs obtained | Dev |
| **API client** | 🔴 Not started | `sourcewhale/client.py` — httpx async client | Dev |

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
