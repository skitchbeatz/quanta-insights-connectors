# Quanta Insights Connectors — Master Plan

## 🎯 Current Status & Next Actions (Updated 2026-02-10)

### ✅ **Completed: Epic 1 - Project Scaffolding & Infrastructure**
- **Repository**: Created on GitHub with complete project structure
- **Package**: Python 3.12+ with FastMCP, httpx, Pydantic, hvac
- **MCP Server**: Full stdio transport with tool registration
- **Connectors**: Bullhorn + LinkedIn with mock data support
- **Security**: Vault client with AppRole authentication
- **Docker**: Local development environment working
- **Code Quality**: ruff, mypy, black configured and passing
- **Branch**: `epic/1-project-scaffolding` pushed to GitHub

### ✅ **Completed: Mock Connectors & Write Protection**
- **Fathom connector**: 5 mock tools (list_meetings, get_summary, get_transcript, search_by_domain, get_action_items)
- **Sourcewhale connector**: 5 mock tools (list_sequences, get_sequence_stats, search_contacts, get_outreach_history, get_campaign_analytics)
- **Pydantic models**: Full typed models for both Fathom and Sourcewhale entities
- **Write protection layer**: `ToolAccessLevel` enum (READ/WRITE) on `ToolDefinition`, enforced at both `list_tools()` and `execute()` in `BaseConnector`
- **Config**: `allow_writes=False` by default, per-connector mock mode flags
- **Vault setup guide**: `docs/vault-setup.md` — step-by-step AppRole + policy creation
- **Refactored**: All connectors use `_get_all_tools()` / `_execute_tool()` pattern

### ✅ **Completed: Real API Clients, Webhook Receiver, CI/CD**
- **Fathom API client** (`fathom/client.py`): Full async httpx client with rate limiting, pagination, retries
- **Sourcewhale API client** (`sourcewhale/client.py`): Provisional async httpx client (endpoints unverified)
- **Fathom webhook receiver** (`webhooks.py`): Starlette ASGI app with HMAC signature verification
  - `POST /webhooks/fathom` — receives real-time meeting data
  - `GET /webhooks/events` — lists recent events (monitoring)
  - `GET /health` — health check
  - In-memory `WebhookStore` with configurable capacity and auto-eviction
- **CI/CD**: GitHub Actions workflows (`ci.yml` + `deploy.yml`)
  - CI: lint (ruff), type check (mypy), test (pytest on 3.12 + 3.13), Docker build
  - Deploy: builds + pushes to GHCR, deploys via SSH to homelab service runner
- **Docker Compose**: Webhook service added (`--profile webhooks`)
- **Testing**: 54 passing unit tests (Bullhorn 6, Fathom 11, Sourcewhale 13, LinkedIn 6, write protection 6, webhooks 12)

### 🔄 **Current State**
- All tests passing (54/54)
- Docker container running successfully
- MCP server initialized with 14 tools (2 Bullhorn + 5 Fathom + 5 Sourcewhale + 2 LinkedIn)
- All connectors in mock mode — ready for real API integration
- Real API clients built for Fathom and Sourcewhale (awaiting API keys)
- Webhook receiver ready for Fathom real-time events
- CI/CD pipeline ready (needs GitHub secrets configured)
- Write operations blocked by default (read-only enforcement)
- Sourcewhale models are **provisional** — will update when official API docs are obtained

### 🚀 **Immediate Next Actions (Priority Order)**

#### **1. Bullhorn ATS API Access** (Epic 3)
- [ ] **Scope ATS API permissions** in Bullhorn admin UI (read-only, limited entities)
- [ ] **Generate API credentials** via admin panel
- [ ] **Configure Vault secrets** at `secret/business/quanta-insights/bullhorn/`
- [ ] **Test OAuth flow** with real credentials

#### **2. Fathom API Access** (Epic 5)
- [x] **Build mock Fathom connector** (5 tools with realistic data)
- [x] **Pydantic models** for all Fathom entities
- [ ] **Generate Fathom API key** from Fathom settings
- [ ] **Build real httpx API client** (`fathom/client.py`)
- [ ] **Design webhook receiver** for real-time meeting data
- [ ] **Store API key** in Vault at `secret/business/quanta-insights/fathom/`

#### **3. Sourcewhale API Access** (Epic 6)
- [x] **Build mock Sourcewhale connector** (5 tools, provisional models)
- [x] **Pydantic models** for inferred Sourcewhale entities
- [ ] **Locate Sourcewhale API documentation** (blocker)
- [ ] **Generate Sourcewhale API key**
- [ ] **Build real httpx API client** (`sourcewhale/client.py`)
- [ ] **Store API key** in Vault at `secret/business/quanta-insights/sourcewhale/`

#### **4. Vault Integration** (Epic 2)
- [x] **Vault setup guide written** (`docs/vault-setup.md`)
- [ ] **Create Vault policy** on vault.chateaumac.com (manual step)
- [ ] **Set up AppRole** on vault.chateaumac.com (manual step)
- [ ] **Test Vault client** with real secrets

#### **5. LinkedIn RSC API** (Epic 4)
- [ ] **Apply for LinkedIn Recruiter System Connect** access
- [ ] **Implement OAuth 2.0 flow**
- [ ] **Build LinkedIn connector** with real API

### 📋 **When Resuming Work**
1. **Build Fathom real API client** — httpx async client ready for when API key is obtained
2. **Build Fathom webhook receiver** — HTTP endpoint for real-time meeting data
3. **Generate Fathom API key** — straightforward, no approval wait
4. **Scope Bullhorn ATS API** — admin UI, generate credentials
5. **Locate Sourcewhale API docs** — update provisional models when available
6. **Create Vault AppRole + policy** — follow `docs/vault-setup.md`
7. **Build CI/CD pipeline** — GitHub Actions deploy workflow
8. **Refer to `docs/data-flows.md`** for recruiter workflow context
9. **Refer to `docs/integration-status.md`** for detailed blocker tracking

### 🔗 **Key Resources**
- **GitHub**: https://github.com/skitchbeatz/quanta-insights-connectors
- **Branch**: `epic/1-project-scaffolding`
- **Local Development**: `docker compose up quanta-insights`
- **Testing**: `python -m pytest tests/ -v`
- **Server Test**: `python test_server.py`
- **Fathom API Docs**: https://developers.fathom.ai/api-reference
- **Data Flow Map**: `docs/data-flows.md`
- **Integration Status**: `docs/integration-status.md`
- **Vault Setup Guide**: `docs/vault-setup.md`

---

## Goal

Build a **multi-connector MCP platform** that wraps staffing/recruiting APIs (starting with
**Bullhorn ATS**, **Fathom**, **Sourcewhale**, and **LinkedIn Recruiter**), authenticates via
OAuth or API keys, securely stores credentials in Vault, and exposes read-only MCP tools to
any AI-assisted IDE (Codex, Claude Desktop, Windsurf, Cursor, etc.).

The platform models the **full recruiter workflow**: discovery calls (Fathom) → candidate
outreach (Sourcewhale) → ATS tracking (Bullhorn) → talent sourcing (LinkedIn). An AI agent
can read data across all systems to generate insights at each stage.

Architected from day one as a **shippable product** — each connector is a pluggable adapter so
new integrations can be added without touching the core MCP server.

**Phase 1 End State:**

* Any MCP-compatible client can call tools via stdio (local) or HTTP+SSE (remote)
* MCP server fetches real data from Bullhorn ATS, Fathom, Sourcewhale, and LinkedIn Recruiter
* AI agent can read across the full recruiter workflow for context-aware insights
* No writes to any upstream system
* Deployed to homelab via existing CI/CD infrastructure

---

## Scope (Phase 1 — Read-Only)

### In Scope

* Custom MCP server — Python + FastMCP
* **Dual transport**: stdio (local dev) + HTTP+SSE (production / product)
* **Bullhorn ATS API** connector (read-only, admin-scoped)
* **Fathom API** connector (meeting summaries, transcripts, action items)
* **Sourcewhale API** connector (sequences, candidate outreach, messaging)
* **LinkedIn Recruiter System Connect (RSC) API** connector (read-only)
* Plugin/adapter pattern for connectors
* OAuth / API key authentication flows per connector
* Secure credential storage via **homelab Vault** (AppRole auth — already operational)
* Webhook receiver for Fathom real-time meeting data
* Deployment to homelab via `deploy-service.yml` reusable workflow
* Traefik routing (e.g. `quanta-insights.chateaumac.com`)
* Single-user context (multi-tenant deferred to Phase 2)
* Mock/sandbox data layers for development while awaiting API credentials

### Out of Scope (Phase 1)

* Write/update/delete operations on any upstream API
* Multi-tenant auth / per-customer credential isolation
* ChatGPT Web / remote tunnel exposure (Cloudflare)
* Scheduled automation / cron jobs
* UI dashboard

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  MCP Client (Codex / Claude Desktop / Windsurf)     │
│  ↕ stdio (local) or HTTP+SSE (remote)               │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Quanta Insights MCP Server  (Python / FastMCP)     │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │  Bullhorn   │  │  Fathom    │  │  Sourcewhale │  │
│  │  ATS        │  │  Connector │  │  Connector   │  │
│  │  Connector  │  │            │  │              │  │
│  └──────┬─────┘  └──────┬─────┘  └──────┬───────┘  │
│         │               │               │           │
│  ┌──────┴───┐  ┌────────┴──────────┐    │           │
│  │ LinkedIn  │  │ Webhook Receiver  │    │           │
│  │ Connector │  │ (Fathom events)   │    │           │
│  └──────┬───┘  └───────────────────┘    │           │
│         │                                │           │
│  ┌──────▼────────────────────────────────▼────────┐ │
│  │  Connector Interface (abstract base)            │ │
│  │  - authenticate()                               │ │
│  │  - list_tools() -> list[Tool]                   │ │
│  │  - execute(tool_name, params) -> Result          │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  Secrets → Vault (AppRole via homelab-automation)    │
│  Config  → Environment / config files               │
│  Logging → Structured JSON (stdout + file)           │
└─────────────────────────────────────────────────────┘

Deployment:
  GitHub Actions → homelab-automation/deploy-service.yml
  → Docker container on service-runner (10.10.5.40)
  → Traefik reverse proxy → quanta-insights.chateaumac.com
```

---

## Tech Stack (Decided)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | **Python 3.12+** | Strongest MCP ecosystem, Pydantic models, type hints |
| MCP SDK | **FastMCP** (`mcp[cli]`) | Most mature Python MCP framework, dual transport built-in |
| HTTP client | **httpx** | Async support, connection pooling, timeout handling |
| Data models | **Pydantic v2** | Typed entity models, validation, serialization |
| Secrets | **hvac** (Vault client) | Native Python Vault client, AppRole support |
| Testing | **pytest + pytest-asyncio** | Async test support for MCP tools |
| Containerization | **Docker** | Deployed via homelab-automation CI/CD |
| CI/CD | **GitHub Actions** | Reusable workflows from `homelab-automation` |

---

## Project Structure

```
quanta-insights-connectors/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, type-check, test
│       └── deploy.yml                # Calls homelab-automation/deploy-service.yml
├── src/
│   └── quanta_insights/
│       ├── __init__.py
│       ├── server.py                 # FastMCP server entry point
│       ├── config.py                 # Configuration loading (env, Vault)
│       ├── vault_client.py           # Vault AppRole integration
│       ├── webhooks.py               # Webhook receiver (Fathom events)
│       ├── connectors/
│       │   ├── __init__.py
│       │   ├── base.py               # Abstract connector interface
│       │   ├── bullhorn/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py           # Bullhorn ATS OAuth flow
│       │   │   ├── client.py         # Bullhorn ATS REST API client
│       │   │   ├── models.py         # Pydantic models (Placement, Candidate, etc.)
│       │   │   ├── tools.py          # MCP tool definitions
│       │   │   └── mock.py           # Mock data layer for development
│       │   ├── fathom/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py           # Fathom API key auth
│       │   │   ├── client.py         # Fathom REST API client
│       │   │   ├── models.py         # Pydantic models (Meeting, Transcript, Summary)
│       │   │   ├── tools.py          # MCP tool definitions
│       │   │   └── mock.py           # Mock data layer for development
│       │   ├── sourcewhale/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py           # Sourcewhale API key auth
│       │   │   ├── client.py         # Sourcewhale REST API client
│       │   │   ├── models.py         # Pydantic models (Sequence, Campaign, etc.)
│       │   │   ├── tools.py          # MCP tool definitions
│       │   │   └── mock.py           # Mock data layer for development
│       │   └── linkedin/
│       │       ├── __init__.py
│       │       ├── auth.py           # LinkedIn OAuth 2.0 flow
│       │       ├── client.py         # LinkedIn RSC API client
│       │       ├── models.py         # Pydantic models (Profile, Project, etc.)
│       │       ├── tools.py          # MCP tool definitions
│       │       └── mock.py           # Mock data layer for development
│       └── logging.py                # Structured logging setup
├── tests/
│   ├── conftest.py
│   ├── test_bullhorn/
│   ├── test_fathom/
│   ├── test_sourcewhale/
│   └── test_linkedin/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── docs/
    ├── plan.md                       # This file — master plan
    ├── data-flows.md                 # Recruiter workflow data flow map
    └── integration-status.md         # API access status & blockers
```

---

## Epic Breakdown

---

## ✅ EPIC 1: Project Scaffolding & Infrastructure (COMPLETED)

**Status**: ✅ **COMPLETED** - All tasks finished and pushed to `epic/1-project-scaffolding`

### Task 1.1 — Repository Structure & Dependencies ✅
- [x] Initialize Python project with `pyproject.toml`
- [x] Set up `src/quanta_insights/` package structure
- [x] Install core dependencies: `mcp[cli]`, `httpx`, `pydantic`, `hvac`
- [x] Configure linting (`ruff`), type-checking (`mypy`), testing (`pytest`)
- [x] Create `.gitignore`, `README.md`

### Task 1.2 — Connector Interface (Abstract Base) ✅
- [x] Define `BaseConnector` abstract class in `connectors/base.py`
- [x] Interface methods: `authenticate()`, `list_tools()`, `execute()`
- [x] Define `ToolDefinition` Pydantic model

### Task 1.3 — Docker & Compose Setup ✅
- [x] Create `Dockerfile` (multi-stage build)
- [x] Create `docker-compose.yml` with Traefik labels
- [x] Environment variables for configuration

### Task 1.4 — CI/CD Pipeline ✅
- [x] Ready for GitHub Actions (will use homelab-automation workflows)

### Task 1.5 — Mock Connectors ✅
- [x] Bullhorn connector with 2 mock tools
- [x] LinkedIn connector with 2 mock tools
- [x] MCP server integration working

---

## 🔄 EPIC 2: Vault Integration (NEXT PRIORITY)

**Status**: 🔄 **READY TO START** - Infrastructure exists, need policy and AppRole

> **Architecture Decision: Shared Vault with Business Namespace**
>
> We use the existing homelab Vault instance (`vault.chateaumac.com`) rather than
> provisioning a dedicated Vault for this project. Business secrets live under a
> `secret/business/` namespace, fully isolated from personal `secret/homelab/*` paths
> via AppRole policy scoping.
>
> **Rationale:** Single operator, same trust boundary, no additional unseal/backup
> overhead. AppRole + policy scoping provides sufficient logical isolation.
>
> **Migration trigger for a separate Vault instance:**
> - A second operator or client needs independent seal keys
> - Infrastructure moves to a VPS where the trust boundary changes
> - Regulatory or contractual requirement for physical secret isolation

### Task 2.1 — Vault Policy for Business Namespace

* Create Vault policy `quanta-insights-policy.hcl`
* Allow read/write to `secret/business/quanta-insights/*`
* Deny access to `secret/homelab/*` paths
* Attach policy to AppRole

**Acceptance Criteria:**
* Policy created and tested
* AppRole can only access business namespace

---

### Task 2.2 — Vault Client in MCP Server

* Implement `vault_client.py` using `hvac` library
* Authenticate via AppRole (role_id + secret_id from env vars)
* Read secrets at runtime — no credentials in code, env, or config files
* Graceful fallback: if Vault unavailable, log error and exit (no silent degradation)
* Vault address configurable (supports future migration to separate instance)

**Acceptance Criteria:**
* MCP server starts with secrets pulled from Vault
* Missing or expired secrets produce clear error messages
* Vault address is not hardcoded — sourced from env var

---

### Task 2.3 — Bullhorn Secrets Structure

Create Vault secrets at `secret/business/quanta-insights/bullhorn/`:

```json
{
  "client_id": "...",
  "client_secret": "...",
  "username": "...",
  "password": "...",
  "api_key": "...",
  "rest_url": "https://rest.bullhorn.com/rest-services/..."
}
```

**Acceptance Criteria:**
* Secrets structure documented
* Template for LinkedIn secrets prepared

---
---

## 🚀 EPIC 3: Bullhorn ATS Connector (Read-Only) (WAITING FOR API ACCESS)

**Status**: 🚀 **WAITING FOR API ACCESS** - Mock implementation complete, pivoting to ATS API

> **Architecture Decision: ATS API instead of Back-Office API**
>
> We are using Bullhorn's **ATS (Applicant Tracking System) API** rather than the
> back-office API. The ATS API can be **scoped directly in the Bullhorn admin UI**,
> allowing us to limit data access to specific entities and fields. This provides
> better security posture and avoids needing Bullhorn support involvement for
> initial credential provisioning.
>
> **Key differences from back-office API:**
> - Permissions scoped via admin UI (no support ticket required)
> - Data access can be limited per entity type
> - Same OAuth flow, different endpoint base
> - Read-only enforcement at the API permission level

### Task 3.1 — Bullhorn ATS OAuth Flow (PENDING)

* Implement Bullhorn's OAuth flow in `bullhorn/auth.py`:
  * Authorization code exchange
  * Access token retrieval
  * REST token (Bullhorn-specific session token via `/rest-services/login`)
  * Automatic refresh before expiry
* Credentials sourced from Vault
* **ATS API scoping configured in Bullhorn admin UI**

**Acceptance Criteria:**
* Tokens retrieved successfully
* Refresh works without manual intervention
* Token state is not persisted to disk
* API permissions limited to read-only entities via admin UI

---

### Task 3.2 — Bullhorn API Client (PENDING)

* Implement reusable async client in `bullhorn/client.py` using `httpx`
* Support:
  * Pagination (start/count based)
  * Field selection (`fields` parameter)
  * Filtering (`where` clauses)
  * Rate-limit handling (retry with backoff)
  * Request/response logging

**Acceptance Criteria:**
* Can fetch any Bullhorn entity reliably
* Rate limits handled gracefully

---

### Task 3.3 — Entity Models (Pydantic) (PENDING)

Create typed models in `bullhorn/models.py` for:

* `Placement`
* `Submission` (aka Sendout)
* `JobOrder`
* `Candidate`
* `ClientCorporation`
* `ClientContact`

**Acceptance Criteria:**
* Raw API responses validate against models
* Models include field descriptions for MCP tool documentation

---

### Task 3.4 — Bullhorn MCP Tools (PARTIALLY COMPLETE)

**Current Status**: 2/6 tools implemented with mock data

Define MCP tools in `bullhorn/tools.py`:

* ✅ `bullhorn_search_placements` — filter by date range, client, status
* ✅ `bullhorn_get_placement_stats` — aggregated metrics (count by month, by client)
* [ ] `bullhorn_search_submissions` — filter by job order, candidate, date
* [ ] `bullhorn_get_candidate` — by ID, with related entities
* [ ] `bullhorn_search_job_orders` — filter by status, client, date
* [ ] `bullhorn_get_client_corporation` — by ID or name

Each tool:
* Is read-only (enforced at wrapper level — no POST/PUT/DELETE methods exist)
* Validates inputs via Pydantic
* Logs the request and response summary
* Returns structured data with field descriptions

**Acceptance Criteria:**
* Tools callable via any MCP client
* Responses are structured and useful for AI-generated insights

---

### Task 3.5 — Bullhorn Mock Data Layer (COMPLETE)

* Implement `bullhorn/mock.py` with realistic fake data
* Same interface as the real client — swap via config flag
* Useful for development while awaiting Bullhorn API credentials

**Acceptance Criteria:**
* ✅ MCP server fully functional with mock data
* ✅ Switching to real API is a config change, not a code change

---

## EPIC 4: LinkedIn Recruiter Connector (Read-Only)

> **Prerequisite:** LinkedIn RSC API access must be applied for through LinkedIn's partner
> program. Having Recruiter seats is necessary but not sufficient. **Start the application
> process immediately** — build against mock data in the meantime.

### Task 4.1 — LinkedIn OAuth 2.0 Flow

* Implement LinkedIn's 3-legged OAuth 2.0 in `linkedin/auth.py`:
  * Authorization code grant
  * Access token + refresh token
  * Scope: `r_liteprofile`, `r_emailaddress`, and RSC-specific scopes
* Credentials sourced from Vault

**Acceptance Criteria:**
* OAuth flow works end-to-end
* Tokens refresh automatically

---

### Task 4.2 — LinkedIn RSC API Client

* Implement async client in `linkedin/client.py`
* Support:
  * Candidate search (keywords, location, skills)
  * Profile retrieval
  * Recruiter project/pipeline listing
  * InMail history (read-only)
  * Pagination and rate-limit handling

**Acceptance Criteria:**
* Can query LinkedIn Recruiter data reliably
* Rate limits handled gracefully

---

### Task 4.3 — LinkedIn Entity Models

Create typed models in `linkedin/models.py`:

* `LinkedInProfile`
* `RecruiterProject`
* `CandidateSearchResult`
* `InMailThread`

**Acceptance Criteria:**
* Models validate against RSC API responses

---

### Task 4.4 — LinkedIn MCP Tools

Define MCP tools in `linkedin/tools.py`:

* `linkedin_search_candidates` — keyword, location, skills, experience level
* `linkedin_get_profile` — by LinkedIn member ID
* `linkedin_list_recruiter_projects` — active pipelines and candidate lists
* `linkedin_get_inmail_history` — read-only conversation history for a candidate

Each tool:
* Is read-only
* Validates inputs via Pydantic
* Logs request and response summary

**Acceptance Criteria:**
* Tools callable alongside Bullhorn tools from the same MCP server

---

### Task 4.5 — LinkedIn Mock Data Layer

* Implement `linkedin/mock.py` with realistic fake recruiter data
* Same interface as the real client — swap via config flag

**Acceptance Criteria:**
* LinkedIn tools fully functional with mock data

---

## 🆕 EPIC 5: Fathom Connector (Read-Only + Webhook)

**Status**: 🆕 **NEW** - API docs reviewed, ready to build mock connector

> **Context:** Fathom is the meeting intelligence tool used during **discovery calls**
> with candidates and clients. It records meetings, generates AI summaries, extracts
> action items, and provides full transcripts. This is the **first step** in the
> recruiter workflow — insights from discovery calls feed into Sourcewhale outreach
> and Bullhorn ATS tracking.
>
> **Auth:** Simple API key via `X-Api-Key` header. No OAuth required.
> **API Docs:** https://developers.fathom.ai/api-reference

### Task 5.1 — Fathom API Key Auth

* Implement API key authentication in `fathom/auth.py`
* API key stored in Vault at `secret/business/quanta-insights/fathom/`
* Auth via `X-Api-Key` header on every request
* Rate limit awareness (headers: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`)

**Acceptance Criteria:**
* API key loaded from Vault at startup
* Rate limit headers parsed and respected

---

### Task 5.2 — Fathom API Client

* Implement async client in `fathom/client.py` using `httpx`
* Base URL: `https://api.fathom.ai/external/v1`
* Endpoints:
  * `GET /meetings` — list meetings with filters (date, domain, team, recorded_by)
  * `GET /recordings/{recording_id}/summary` — get meeting summary (sync or async via `destination_url`)
  * `GET /recordings/{recording_id}/transcript` — get full transcript (sync or async)
  * `GET /teams` — list teams
  * `GET /team-members` — list team members
* Support:
  * Cursor-based pagination (`next_cursor`)
  * Optional includes: `include_transcript`, `include_summary`, `include_action_items`, `include_crm_matches`
  * Rate-limit handling with backoff

**Acceptance Criteria:**
* Can fetch meetings, summaries, and transcripts reliably
* Pagination works correctly
* Rate limits handled gracefully

---

### Task 5.3 — Fathom Entity Models (Pydantic)

Create typed models in `fathom/models.py` for:

* `Meeting` — title, recording_id, url, timestamps, calendar_invitees, recorded_by
* `CalendarInvitee` — name, email, domain, is_external, matched_speaker
* `TranscriptEntry` — speaker (display_name, email), text, timestamp
* `MeetingSummary` — template_name, markdown_formatted
* `ActionItem` — description, completed, recording_timestamp, playback_url, assignee
* `CrmMatch` — contacts, companies, deals
* `WebhookPayload` — full meeting data received via webhook

**Acceptance Criteria:**
* Raw API responses validate against models
* Models include field descriptions for MCP tool documentation

---

### Task 5.4 — Fathom MCP Tools

Define MCP tools in `fathom/tools.py`:

* `fathom_list_meetings` — filter by date range, domain, team, recorded_by; include summary/transcript
* `fathom_get_meeting_summary` — get AI summary for a specific recording
* `fathom_get_meeting_transcript` — get full transcript for a specific recording
* `fathom_search_meetings_by_domain` — find all meetings with a specific company domain
* `fathom_get_action_items` — extract action items from a meeting

Each tool:
* Is read-only
* Validates inputs via Pydantic
* Logs request and response summary
* Returns structured data with field descriptions

**Acceptance Criteria:**
* Tools callable via any MCP client
* AI agent can retrieve discovery call context for any candidate/client

---

### Task 5.5 — Fathom Webhook Receiver

* Implement webhook endpoint in `webhooks.py`
* Register webhook via Fathom API (`POST /webhooks`):
  * `destination_url`: our webhook endpoint
  * `triggered_for`: `["my_recordings", "my_shared_with_team_recordings"]`
  * `include_transcript`: true
  * `include_summary`: true
  * `include_action_items`: true
* Verify webhook signature using `secret` from registration response
* Store received meeting data for MCP tool access

**Acceptance Criteria:**
* Webhook receives real-time meeting data after calls complete
* Signature verification prevents spoofed payloads
* Data available to MCP tools immediately after webhook fires

---

### Task 5.6 — Fathom Mock Data Layer

* Implement `fathom/mock.py` with realistic meeting data
* Mock data includes: discovery calls, client meetings, candidate screens
* Same interface as the real client — swap via config flag

**Acceptance Criteria:**
* MCP server fully functional with mock Fathom data
* Switching to real API is a config change, not a code change

---

## 🆕 EPIC 6: Sourcewhale Connector (Read-Only)

**Status**: 🆕 **NEW** - API documentation search in progress

> **Context:** Sourcewhale is the **outreach and sequencing platform** used after
> discovery calls (Fathom) to engage candidates and clients. It manages email/LinkedIn
> sequences, tracks responses, and provides analytics on outreach effectiveness.
> This is the **second step** in the recruiter workflow — after discovery, recruiters
> use Sourcewhale to follow up with candidates and manage client sales messaging.
>
> **Auth:** API key (generation process TBD — need to locate API docs)
> **API Docs:** TBD — searching for documentation

### Task 6.1 — Sourcewhale API Discovery

* Locate Sourcewhale API documentation
* Determine authentication method (likely API key)
* Map available endpoints and data models
* Identify rate limits and pagination patterns

**Acceptance Criteria:**
* API documentation located and reviewed
* Authentication method confirmed
* Available endpoints catalogued

---

### Task 6.2 — Sourcewhale API Client

* Implement async client in `sourcewhale/client.py` using `httpx`
* Endpoints (TBD — based on API discovery):
  * List/search sequences (outreach campaigns)
  * Get sequence details and stats
  * List candidates in a sequence
  * Get candidate outreach history (emails sent, responses)
  * Get campaign analytics (open rates, reply rates)
* Support pagination and rate-limit handling

**Acceptance Criteria:**
* Can fetch sequence and outreach data reliably
* Rate limits handled gracefully

---

### Task 6.3 — Sourcewhale Entity Models (Pydantic)

Create typed models in `sourcewhale/models.py` for (TBD — based on API discovery):

* `Sequence` — name, status, stats, created_at
* `SequenceStep` — type (email/LinkedIn), template, delay
* `CandidateOutreach` — candidate info, sequence, step, status, response
* `CampaignAnalytics` — open_rate, reply_rate, bounce_rate, total_sent

**Acceptance Criteria:**
* Models validate against API responses
* Models include field descriptions for MCP tool documentation

---

### Task 6.4 — Sourcewhale MCP Tools

Define MCP tools in `sourcewhale/tools.py`:

* `sourcewhale_list_sequences` — list active/completed outreach sequences
* `sourcewhale_get_sequence_stats` — get performance metrics for a sequence
* `sourcewhale_search_candidates` — find candidates by sequence, status, response
* `sourcewhale_get_outreach_history` — get full outreach timeline for a candidate
* `sourcewhale_get_campaign_analytics` — aggregated outreach performance metrics

Each tool:
* Is read-only
* Validates inputs via Pydantic
* Logs request and response summary

**Acceptance Criteria:**
* Tools callable via any MCP client
* AI agent can correlate outreach data with Fathom discovery and Bullhorn ATS data

---

### Task 6.5 — Sourcewhale Mock Data Layer

* Implement `sourcewhale/mock.py` with realistic outreach data
* Mock data includes: email sequences, LinkedIn outreach, response tracking
* Same interface as the real client — swap via config flag

**Acceptance Criteria:**
* MCP server fully functional with mock Sourcewhale data
* Switching to real API is a config change, not a code change

---

## EPIC 7: MCP Server & Transport

### Task 7.1 — FastMCP Server Core

* Implement `server.py` using FastMCP
* Auto-discover and register tools from all enabled connectors
* Support dual transport:
  * **stdio** — for local IDE integration (Codex, Windsurf, Cursor)
  * **HTTP+SSE** — for remote/production use (Streamable HTTP)
* Transport mode selected via config / CLI flag

**Acceptance Criteria:**
* Server starts in either transport mode
* All connector tools appear in tool listing

---

### Task 7.2 — Configuration Management

* Implement `config.py`:
  * Load from environment variables (12-factor)
  * Vault integration for secrets
  * Feature flags per connector (enable/disable)
  * Transport mode (stdio / http)
  * Mock mode toggle per connector

**Acceptance Criteria:**
* Zero hardcoded credentials
* Config validated at startup with clear error messages

---

### Task 7.3 — Structured Logging & Observability

* Implement `logging.py`:
  * Structured JSON logging (stdout for Docker log aggregation)
  * Log every MCP tool call (tool name, params, duration, success/error)
  * Log every upstream API call (method, URL, status code, latency)
  * Error logging with stack traces
* No sensitive data in logs (mask tokens, credentials)

**Acceptance Criteria:**
* Logs are parseable by standard log aggregation tools
* Audit trail for all MCP and API activity

---

## EPIC 8: Integration Testing & Validation

### Task 8.1 — Unit Tests

* Test each connector's models, auth flow, and client (using mocks/fixtures)
* Test MCP tool input validation and error handling
* Test Vault client (mock Vault responses)

**Acceptance Criteria:**
* >80% coverage on connector and server code
* CI runs tests on every push

---

### Task 8.2 — MCP Client Integration Tests

Test via MCP clients:

* Register server in Codex / Windsurf / Claude Desktop config
* Invoke Bullhorn tools: search placements, filter by client, get candidate
* Invoke LinkedIn tools: search candidates, list projects
* Cross-connector prompts: "Find candidates on LinkedIn matching this Bullhorn job order"

**Acceptance Criteria:**
* Data returned correctly from both connectors
* AI produces coherent, data-backed insights

---

### Task 8.3 — Insight Validation Prompts

Test prompts such as:

* "Show placement trends by client for the last 12 months"
* "Compare submission-to-placement ratio across job orders"
* "Find LinkedIn candidates matching the top 3 open job orders in Bullhorn"
* "Which recruiters have the highest placement rate this quarter?"

**Acceptance Criteria:**
* AI-generated insights are accurate, useful, and grounded in real data

---

## EPIC 9: Guardrails & Safety

### Task 9.1 — Read-Only Enforcement

* Enforce read-only at **three layers**:
  1. **MCP tool definitions** — no write tools registered
  2. **Connector interface** — `execute()` rejects unknown tool names
  3. **API client** — only GET methods implemented; no POST/PUT/DELETE

**Acceptance Criteria:**
* Writes are impossible without modifying code at all three layers

---

### Task 9.2 — Input Validation & Sanitization

* All MCP tool inputs validated via Pydantic models
* Reject excessively broad queries (e.g. "get all candidates" with no filters)
* Rate-limit tool calls per minute (configurable)

**Acceptance Criteria:**
* Malformed or abusive inputs rejected with clear error messages

---

## Deployment Reference (Homelab Integration)

This service deploys via the existing `homelab-automation` infrastructure:

| Component | Detail |
|-----------|--------|
| **Build runner** | `10.10.5.42` (Docker builds) |
| **Service runner** | `10.10.5.40` (deployment target) |
| **Vault** | `vault.chateaumac.com` (AppRole auth, already operational) |
| **Reverse proxy** | Traefik → `quanta-insights.chateaumac.com` |
| **CI/CD** | GitHub Actions → `deploy-service.yml` reusable workflow |
| **Secrets** | Vault path: `secret/business/quanta-insights/*` |
| **Network** | Local-only; no public ingress in Phase 1 |

### Vault Secrets Structure

```
secret/business/
└── quanta-insights/
    ├── bullhorn/
    │   ├── client_id
    │   ├── client_secret
    │   ├── api_username
    │   └── api_password
    ├── fathom/
    │   └── api_key
    ├── sourcewhale/
    │   └── api_key
    └── linkedin/
        ├── client_id
        ├── client_secret
        └── redirect_uri
```

> Namespace `secret/business/` is reserved for business/product secrets.
> Personal homelab secrets remain under `secret/homelab/`.

---

## ✅ Phase 1 — Final Acceptance Criteria

* [ ] MCP server runs in Docker on service-runner
* [ ] Vault stores all connector credentials securely (AppRole auth)
* [ ] Bullhorn ATS OAuth works end-to-end (or mock mode active)
* [ ] Fathom API key auth works end-to-end (or mock mode active)
* [ ] Sourcewhale API key auth works end-to-end (or mock mode active)
* [ ] LinkedIn OAuth works end-to-end (or mock mode active)
* [ ] Any MCP client can invoke tools via stdio or HTTP+SSE
* [ ] Bullhorn ATS data retrieved and structured correctly
* [ ] Fathom meeting data (summaries, transcripts) retrieved correctly
* [ ] Sourcewhale outreach data retrieved correctly
* [ ] LinkedIn Recruiter data retrieved and structured correctly
* [ ] AI agent can read across full recruiter workflow (Fathom → Sourcewhale → Bullhorn → LinkedIn)
* [ ] No writes to any upstream system
* [ ] CI/CD pipeline builds, tests, and deploys on merge to main
* [ ] Structured logging captures all MCP and API activity

---

## Parallel Workstreams (Start Immediately)

These are **non-code tasks** that should begin in parallel with development:

- [ ] **Bullhorn ATS API access**: Scope permissions in admin UI, generate API credentials
- [ ] **Fathom API key**: Generate from Fathom settings (no approval needed)
- [ ] **Sourcewhale API**: Locate API documentation, generate API key
- [ ] **LinkedIn RSC API**: Apply through LinkedIn's partner program for Recruiter System Connect API access
- [ ] **Vault setup**: Create AppRole and policies for `quanta-insights-connectors` in homelab Vault

---

## Future Phases (Not Implemented in Phase 1)

| Phase | Scope |
|-------|-------|
| **Phase 2** | Multi-tenant auth — each customer brings their own credentials |
| **Phase 3** | Write capabilities — draft-only previews with human-in-the-loop approval |
| **Phase 4** | Additional connectors (ATS systems, job boards, CRM platforms) |
| **Phase 5** | UI dashboard for non-IDE users |
| **Phase 6** | Workflow automation and scheduled insight reports |

---

## Timeline Estimate

| Phase | Scope | Estimate |
|-------|-------|----------|
| **Phase 1a** | Scaffolding, Bullhorn ATS + Fathom + Sourcewhale mock connectors | 2–3 weeks |
| **Phase 1b** | Real API integration (as credentials become available) | 1–3 weeks |
| **Phase 1c** | LinkedIn RSC connector (mock + real when API approved) | 1–3 weeks |
| **Phase 1d** | Homelab deployment (Docker, CI/CD, Vault, Traefik) | 3–5 days |
| **Phase 2** | Multi-tenant auth, product packaging | 3–4 weeks |
| **Phase 3** | Write capabilities, approval workflows | 4–6 weeks |

**Phase 1 total: ~5–8 weeks to a working internal tool (4 connectors).**
**Shippable MVP (through Phase 2): ~12–16 weeks.**

---

**This plan intentionally optimizes for trust, safety, and visible recruiter value before
automation or write capabilities. The plugin architecture ensures new connectors can be
added without touching the core server. See `docs/data-flows.md` for the recruiter workflow
map and `docs/integration-status.md` for detailed API access tracking.**
