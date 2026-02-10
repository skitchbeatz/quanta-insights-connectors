# Quanta Insights Connectors — Master Plan

## 🎯 Current Status & Next Actions (Updated 2026-02-10)

### ✅ **Completed: Epic 1 - Project Scaffolding & Infrastructure**
- **Repository**: Created on GitHub with complete project structure
- **Package**: Python 3.12+ with FastMCP, httpx, Pydantic, hvac
- **MCP Server**: Full stdio transport with tool registration
- **Connectors**: Bullhorn + LinkedIn with mock data support
- **Security**: Vault client with AppRole authentication
- **Testing**: 12 passing unit tests with pytest
- **Docker**: Local development environment working
- **Code Quality**: ruff, mypy, black configured and passing
- **Branch**: `epic/1-project-scaffolding` pushed to GitHub

### 🔄 **Current State**
- All tests passing (12/12)
- Docker container running successfully
- MCP server initialized with 4 tools (2 per connector)
- Mock data working for development
- Ready for real API integration

### 🚀 **Immediate Next Actions (Priority Order)**

#### **1. Bullhorn API Access** (Epic 3)
- [ ] **Contact Bullhorn support** for API application
- [ ] **Register OAuth application** in Bullhorn admin
- [ ] **Request API key** (can take 1-2 weeks)
- [ ] **Configure Vault secrets** at `secret/business/quanta-insights/bullhorn/`
- [ ] **Test OAuth flow** with real credentials

#### **2. Vault Integration** (Epic 2)
- [ ] **Create Vault policy** for `secret/business/quanta-insights/*`
- [ ] **Set up AppRole** for this service
- [ ] **Test Vault client** with real secrets

#### **3. Bullhorn Implementation** (Epic 3 continued)
- [ ] **Implement OAuth authentication** (`bullhorn/auth.py`)
- [ ] **Build API client** (`bullhorn/client.py`)
- [ ] **Create data models** (`bullhorn/models.py`)
- [ ] **Expand to 6 tools** (currently 2 mock tools)
- [ ] **Replace mock with real data**

#### **4. LinkedIn RSC API** (Epic 4)
- [ ] **Apply for LinkedIn Recruiter System Connect** access
- [ ] **Implement OAuth 2.0 flow**
- [ ] **Build LinkedIn connector** with real API

### 📋 **When Resuming Work**
1. **Start with Bullhorn API application** - this is the longest lead time
2. **While waiting for approval**, implement Vault integration
3. **Once credentials received**, implement real Bullhorn connector
4. **Test end-to-end** with real data
5. **Proceed to LinkedIn integration**

### 🔗 **Key Resources**
- **GitHub**: https://github.com/skitchbeatz/quanta-insights-connectors
- **Branch**: `epic/1-project-scaffolding`
- **Local Development**: `docker compose up quanta-insights`
- **Testing**: `python -m pytest tests/ -v`
- **Server Test**: `python test_server.py`

---

## Goal

Build a **multi-connector MCP platform** that wraps staffing/recruiting APIs (starting with
**Bullhorn** and **LinkedIn Recruiter**), authenticates via OAuth, securely stores credentials in
Vault, and exposes read-only MCP tools to any AI-assisted IDE (Codex, Claude Desktop, Windsurf,
Cursor, etc.).

Architected from day one as a **shippable product** — each connector is a pluggable adapter so
new integrations can be added without touching the core MCP server.

**Phase 1 End State:**

* Any MCP-compatible client can call tools via stdio (local) or HTTP+SSE (remote)
* MCP server fetches real Bullhorn + LinkedIn Recruiter data
* Recruiter-facing insights can be generated (placements, trends, candidate pipelines)
* No writes to any upstream system
* Deployed to homelab via existing CI/CD infrastructure

---

## Scope (Phase 1 — Read-Only)

### In Scope

* Custom MCP server — Python + FastMCP
* **Dual transport**: stdio (local dev) + HTTP+SSE (production / product)
* Bullhorn REST API connector (read-only)
* LinkedIn Recruiter System Connect (RSC) API connector (read-only)
* Plugin/adapter pattern for connectors
* OAuth authentication flows (Bullhorn OAuth, LinkedIn OAuth 2.0)
* Secure credential storage via **homelab Vault** (AppRole auth — already operational)
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
│  │  Bullhorn   │  │  LinkedIn   │  │  Future      │  │
│  │  Connector  │  │  Connector  │  │  Connectors  │  │
│  └──────┬─────┘  └──────┬─────┘  └──────────────┘  │
│         │               │                            │
│  ┌──────▼───────────────▼────────────────────────┐  │
│  │  Connector Interface (abstract base)           │  │
│  │  - authenticate()                              │  │
│  │  - list_tools() -> list[Tool]                  │  │
│  │  - execute(tool_name, params) -> Result         │  │
│  └───────────────────────────────────────────────┘  │
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
│       ├── connectors/
│       │   ├── __init__.py
│       │   ├── base.py               # Abstract connector interface
│       │   ├── bullhorn/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py           # Bullhorn OAuth flow
│       │   │   ├── client.py         # Bullhorn REST API client
│       │   │   ├── models.py         # Pydantic models (Placement, Candidate, etc.)
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
│   └── test_linkedin/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── docs/
    └── plan.md
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

## 🚀 EPIC 3: Bullhorn Connector (Read-Only) (WAITING FOR API ACCESS)

**Status**: 🚀 **WAITING FOR API ACCESS** - Mock implementation complete, need real credentials

### Task 3.1 — Bullhorn OAuth Flow (PENDING)

* Implement Bullhorn's OAuth flow in `bullhorn/auth.py`:
  * Authorization code exchange
  * Access token retrieval
  * REST token (Bullhorn-specific session token via `/rest-services/login`)
  * Automatic refresh before expiry
* Credentials sourced from Vault

**Acceptance Criteria:**
* Tokens retrieved successfully
* Refresh works without manual intervention
* Token state is not persisted to disk

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

## EPIC 5: MCP Server & Transport

### Task 5.1 — FastMCP Server Core

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

### Task 5.2 — Configuration Management

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

### Task 5.3 — Structured Logging & Observability

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

## EPIC 6: Integration Testing & Validation

### Task 6.1 — Unit Tests

* Test each connector's models, auth flow, and client (using mocks/fixtures)
* Test MCP tool input validation and error handling
* Test Vault client (mock Vault responses)

**Acceptance Criteria:**
* >80% coverage on connector and server code
* CI runs tests on every push

---

### Task 6.2 — MCP Client Integration Tests

Test via MCP clients:

* Register server in Codex / Windsurf / Claude Desktop config
* Invoke Bullhorn tools: search placements, filter by client, get candidate
* Invoke LinkedIn tools: search candidates, list projects
* Cross-connector prompts: "Find candidates on LinkedIn matching this Bullhorn job order"

**Acceptance Criteria:**
* Data returned correctly from both connectors
* AI produces coherent, data-backed insights

---

### Task 6.3 — Insight Validation Prompts

Test prompts such as:

* "Show placement trends by client for the last 12 months"
* "Compare submission-to-placement ratio across job orders"
* "Find LinkedIn candidates matching the top 3 open job orders in Bullhorn"
* "Which recruiters have the highest placement rate this quarter?"

**Acceptance Criteria:**
* AI-generated insights are accurate, useful, and grounded in real data

---

## EPIC 7: Guardrails & Safety

### Task 7.1 — Read-Only Enforcement

* Enforce read-only at **three layers**:
  1. **MCP tool definitions** — no write tools registered
  2. **Connector interface** — `execute()` rejects unknown tool names
  3. **API client** — only GET methods implemented; no POST/PUT/DELETE

**Acceptance Criteria:**
* Writes are impossible without modifying code at all three layers

---

### Task 7.2 — Input Validation & Sanitization

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
* [ ] Bullhorn OAuth works end-to-end (or mock mode active)
* [ ] LinkedIn OAuth works end-to-end (or mock mode active)
* [ ] Any MCP client can invoke tools via stdio or HTTP+SSE
* [ ] Bullhorn data retrieved and structured correctly
* [ ] LinkedIn Recruiter data retrieved and structured correctly
* [ ] Recruiter-style insights can be generated across both data sources
* [ ] No writes to any upstream system
* [ ] CI/CD pipeline builds, tests, and deploys on merge to main
* [ ] Structured logging captures all MCP and API activity

---

## Parallel Workstreams (Start Immediately)

These are **non-code tasks** that should begin in parallel with development:

- [ ] **Bullhorn API access**: Coordinate with org admin to register API application, obtain client_id/secret
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
| **Phase 1a** | Scaffolding, connectors, Bullhorn read-only MCP (mock + real) | 2–3 weeks |
| **Phase 1b** | LinkedIn RSC connector (mock + real when API approved) | 1–3 weeks |
| **Phase 1c** | Homelab deployment (Docker, CI/CD, Vault, Traefik) | 3–5 days |
| **Phase 2** | Multi-tenant auth, product packaging | 3–4 weeks |
| **Phase 3** | Write capabilities, approval workflows | 4–6 weeks |

**Phase 1 total: ~4–6 weeks to a working internal tool.**
**Shippable MVP (through Phase 2): ~10–14 weeks.**

---

**This plan intentionally optimizes for trust, safety, and visible recruiter value before
automation or write capabilities. The plugin architecture ensures new connectors can be
added without touching the core server.**
