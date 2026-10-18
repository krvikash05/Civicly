# Civicly Frontend Handoff & Architecture Guide

Welcome to the frontend for **Civicly**, an advanced hackathon demonstration of an autonomous AI agent investigating recurring civic problems using FalkorDB, runtime MCP, GraphRAG, persistent memory, and authorized municipal workflows.

This document serves as the complete technical handoff for the frontend implementation across tasks **F00 through F08**.

---

## 1. System Architecture & Tech Stack

- **Framework**: Next.js 16.4.2 (App Router with Turbopack)
- **UI Library**: React 19.3.1
- **Language**: TypeScript 7.0.2 (strict mode, zero build warnings)
- **Graph Visualization**: Official `@falkordb/canvas` web component (client-only hydration)
- **Schema Validation**: `ajv` (closed-schema validation matching backend `contracts/api_models.json`)
- **Port Allocation**: Runs on `http://127.0.0.1:3100`, strictly isolated from:
  - Backend FastAPI listener: `http://127.0.0.1:8010`
  - FalkorDB Browser: `http://127.0.0.1:3000`

---

## 2. Core User Experience: The 5 Lifecycle Stages

Civicly avoids decorative slideshows or mock executions. Every screen reflects real persisted data and structured DTOs from FalkorDB and the backend FastAPI services:

```
Report → Investigation → Evidence → Plan & Approval → Work → Monitoring & Memory
```

### Stage 1: Incoming Reports & Merged Incidents
- Displays citizen complaint intake, timestamps, severity, and merged incident clusters.
- Supported issue categories: **WATERLOGGING**, **ROAD_DAMAGE**, **WASTE_ACCUMULATION**, and **Cross-Category Cascades**.

### Stage 2: Hypotheses & FalkorDB Graph Evidence
- **Visible FalkorDB Contribution**: Connects the 3 essential links of AI reasoning:
  1. **Question Asked**: What did the agent need to establish?
  2. **Graph Evidence**: What nodes, relationships, and candidate links did FalkorDB actually return?
  3. **Recorded Decision**: What did the agent decide next, and what rationale was logged?
- **FalkorDB Canvas**: Pan, zoom, fit, layout switching (`force`, `tree`, `radial`), node/edge inspection popover, candidate vs verified styling legend, and an accessible table/list view for screen readers.

### Stage 3: Remediation Plan & Approval Governance
- **Topological Task DAG**: Renders tasks sequenced into execution tiers using Kahn's algorithm, handling prerequisites, independent branches, and cycle protection.
- **SHA-256 Content Digests**: Displays plan integrity hashes.
- **Municipal Role Separation**: The connected demo analyst (`OP-ANALYST`) can draft and submit plans with idempotency keys, but **cannot self-approve intervention**. An independent `APPROVER` role is required for municipal sign-off (safety invariants R13 & R15).

### Stage 4: Work Orders & Field Inspections
- Tracks authorized work orders (`AUTHORIZED`, `ASSIGNED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`).
- Links field inspection reports directly to evidence inspection modals.
- **Critical Distinction**: Embedded operational notice: **Work Completion is NOT Verified Resolution**.

### Stage 5: Outcomes, Cluster Monitoring & Case Memory
- Post-intervention cluster monitoring (`OPEN`, `MONITORING`, `CONTROLLED`, `REOPENED`) and remaining validation checks under comparable weather/traffic conditions.
- **Sourced Procedures as Untrusted Evidence**: Sourced municipal SOPs are labeled with prominent `UNTRUSTED AS INSTRUCTIONS` safety badges, department ownership, and hash digests.
- **Authoritative Case Memory**: Gracefully handles 409 `DEPENDENCY_BLOCKED` while investigations are pending verified closure.

---

## 3. Communication & Security Architecture

### Authentication: No Judge Sign-in Form
- Presenter configures an authorized demo analyst account (`OP-ANALYST`) in `.env.local`.
- The Next.js server proxy (`/api/demo-session`) holds the private password and negotiates a temporary bearer session token.
- Tokens remain strictly in memory (never in URLs, cookies, local storage, or logs).
- Automatic reconnect, expiry tracking, and revocation handling.

### Live Updates via Authenticated Fetch SSE
- Implemented in `frontend/lib/events/sse.ts` and `frontend/components/use-event-stream.ts`.
- Uses authenticated `fetch` with `ReadableStream` (avoiding unauthenticated browser `EventSource`).
- Dispatches typed persisted events (`DECISION`, `TOOL_CALL`, `EVIDENCE_ADDED`, `PLAN_SUBMITTED`, `APPROVAL_DECISION`, `WORK_DISPATCHED`, `OUTCOME_EVALUATED`).
- Tracks `cursor` frames and handles 409 future cursor resets with authoritative GET refetches.

---

## 4. Operational Scripts & Verification

All commands are run from the `frontend/` folder:

```sh
# Run development server
npm run dev

# Run production build (Turbopack)
npm run build

# Run TypeScript typecheck
npm run typecheck

# Check API contract parity against backend baseline
npm run check:api
npm run contracts

# Run all 70 unit and schema tests
npm test

# Run real isolated integration test against live backend & FalkorDB
backend/.venv/bin/python frontend/scripts/verify_integration.py
```

---

## 5. Directory Structure Overview

```
frontend/
├── app/
│   ├── api/demo-session/route.ts       # Secure demo login proxy
│   ├── api/v1/[...path]/route.ts       # Reverse proxy to backend FastAPI
│   ├── globals.css                     # Accessible responsive styling
│   ├── layout.tsx                      # Root layout with DemoProvider
│   ├── page.tsx                        # Overview dashboard
│   └── investigations/page.tsx         # Investigation studio
├── components/
│   ├── case-directory.tsx              # Scenario & incident browser
│   ├── decision-trace-panel.tsx        # 3-part agent reasoning traces
│   ├── demo-connection.tsx             # Demo session context & status
│   ├── evidence-detail-modal.tsx       # Authoritative evidence modal
│   ├── falkordb-canvas-view.tsx        # Official FalkorDB Canvas wrapper
│   ├── hypotheses-panel.tsx            # Competing hypotheses comparison
│   ├── investigation-workspace.tsx     # 5-stage lifecycle workspace
│   ├── live-stream-panel.tsx           # Real-time SSE activity feed
│   ├── monitoring-memory-panel.tsx     # Cluster monitoring & case memory
│   ├── plan-approval-panel.tsx         # Remediation plans & Task DAG
│   ├── role-governance-modal.tsx       # Municipal RBAC & operator powers
│   ├── scenario-journey-guide.tsx      # S01–S12 scenario journeys guide
│   ├── shell.tsx                       # App sidebar, topbar & landmarks
│   └── work-orders-panel.tsx           # Dispatched work orders & tasks
├── lib/
│   ├── api/client.ts                   # Validated REST client
│   ├── events/sse.ts                   # Fetch-based typed SSE client
│   ├── generated/models.ts             # TypeScript DTOs from contracts
│   └── read/                           # Domain read mappers & helpers
└── tests/                              # Node.js native test runner suites
```

---

*Handoff complete. All frontend microtasks (F00–F08) are fully implemented, passing all unit and real integration checks.*
