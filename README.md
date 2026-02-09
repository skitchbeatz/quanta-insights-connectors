# Quanta Insights Connectors

A multi-connector MCP (Model Context Protocol) platform that wraps staffing/recruiting APIs, enabling AI-assisted IDEs to query real-time recruiting data for insights.

## Overview

This project provides a unified MCP interface to multiple recruiting platforms:

- **Bullhorn** — REST API for placements, candidates, job orders, and client data
- **LinkedIn Recruiter** — Recruiter System Connect (RSC) API for candidate search and pipeline data

Built as a **shippable product** with a plugin architecture — new connectors can be added without touching the core MCP server.

## Architecture

```
MCP Client (Codex/Claude/Windsurf) 
  ↕ stdio or HTTP+SSE
Quanta Insights MCP Server (Python + FastMCP)
  ├── Bullhorn Connector
  ├── LinkedIn Recruiter Connector
  └── Future Connectors (plugin interface)

Secrets → Vault (AppRole auth)
Deployment → Homelab infrastructure via homelab-automation
```

## Tech Stack

- **Language**: Python 3.12+
- **MCP Framework**: FastMCP (`mcp[cli]`)
- **HTTP Client**: httpx (async)
- **Data Models**: Pydantic v2
- **Secrets**: hvac (Vault client)
- **Testing**: pytest + pytest-asyncio
- **Linting**: ruff
- **Type Checking**: mypy
- **Containerization**: Docker
- **CI/CD**: GitHub Actions (reusable workflows from homelab-automation)

## Phase 1 Scope (Read-Only)

- ✅ Multi-connector MCP server with dual transport (stdio + HTTP+SSE)
- ✅ Bullhorn REST API connector (read-only)
- ✅ LinkedIn Recruiter RSC API connector (read-only)
- ✅ Secure credential storage via Vault
- ✅ Mock data layers for development
- ✅ Deployment to homelab infrastructure
- ❌ Write/update/delete operations (deferred to Phase 2)
- ❌ Multi-tenant auth (deferred to Phase 2)

## Getting Started

See [docs/plan.md](docs/plan.md) for the complete implementation plan, architecture details, and epic breakdown.

## Development Status

- 📋 Planning complete
- 🏗️ Repository initialization in progress
- ⏳ Awaiting API credentials (Bullhorn + LinkedIn RSC)
- ⏳ LinkedIn RSC API application in progress

## License

Business project — all rights reserved.

---

**Note**: This project intentionally optimizes for trust, safety, and visible recruiter value before automation or write capabilities.
