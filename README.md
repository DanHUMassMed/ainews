# AI Industry News Daily ⚡

> **Signal over volume. Importance over popularity.**  
> An autonomous, self-correcting AI industry daily briefing platform engineered for machine learning engineers, systems researchers, and technical leaders.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK 2.x](https://img.shields.io/badge/Google%20ADK-2.8.0-4285F4.svg)](https://github.com/google/adk)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.100.0-orange.svg)](https://docs.litellm.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg)](https://www.typescriptlang.org/)
[![MCP Server](https://img.shields.io/badge/MCP-Protocol%201.2-purple.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

1. [Overview & Philosophy](#-overview--philosophy)
2. [Target Use Cases](#-target-use-cases)
3. [System Architecture](#-system-architecture)
4. [The Six Specialized Editorial Agents](#-the-six-specialized-editorial-agents)
5. [The Editorial MCP Server](#-the-editorial-mcp-server)
6. [Scoring Engine & Publication Gate](#-scoring-engine--publication-gate)
7. [Golden Evaluation Benchmark](#-golden-evaluation-benchmark)
8. [Frontend & Editorial Inspector](#-frontend--editorial-inspector)
9. [Directory Structure](#-directory-structure)
10. [Quickstart & Installation](#-quickstart--installation)
11. [Management CLI & Makefile](#-management-cli--makefile)
12. [API Reference](#-api-reference)
13. [Configuration Reference](#-configuration-reference)
14. [Testing Suite](#-testing-suite)
15. [License](#-license)

---

## 🌟 Overview & Philosophy

The modern AI news landscape is inundated with sensationalism, vendor marketing releases, and incremental wrapper re-writes. **AI Industry News Daily** is built on a single, uncompromising principle:

> **We publish only what fundamentally alters capability boundaries, systems economics, or strategic engineering decisions.** If a news cycle yields zero breakthrough developments, the system publishes an honest **Low-Signal Notice** rather than filling the briefing with noise.

### Core Architectural Pillars
- **Autonomous Multi-Agent Editorial Pipeline**: Driven by **Google ADK 2.x** and **LiteLLM**, routing to frontier models (e.g., DeepSeek V3/V4, Claude 3.5 Sonnet, GPT-4o) via OpenRouter.
- **Model Context Protocol (MCP) Decoupling**: Editorial memory, candidate staging, and gate enforcement are isolated in an async stdio **Editorial MCP Server** with 11 tools, ensuring the agent layer has zero direct database coupling.
- **Closed-Loop Reader Feedback ($w_5 	ext{FB}$)**: Reader upvotes and downvotes dynamically modulate topic scoring biases after a 30-day / 100-vote cold start.
- **Adversarial Critic with Auto-Revision**: The Critic Agent audits drafts against strict anti-hype buzzword dictionaries and factual groundings, triggering up to 2 automated self-correction cycles before draft staging.
- **Self-Hosted & Zero External Telemetry**: Runs fully self-contained via Docker Compose (Postgres 16, SearXNG metasearch, Firecrawl markdown scraper) and local FastAPI/Vite daemons.

---

## 🎯 Target Use Cases

| Use Case | Description |
| :--- | :--- |
| **Enterprise AI Engineering Briefing** | Run an automated daily newsroom inside your organization's intranet that delivers concise, mathematically grounded signals directly to Slack, email, or a web dashboard. |
| **Autonomous Research Radar** | Continuously scan arXiv, GitHub repositories, hardware announcements (silicon, interconnects, packaging), and frontier model labs without human triage overhead. |
| **Benchmarking Agent Orchestration** | A reference implementation for production-grade Google ADK 2.x multi-agent collaboration with LiteLLM, tool calling, and MCP server isolation. |
| **Adversarial Content Verification** | Deploy an automated publication gate with hallucination checks, buzzword bans, and source corroboration for publishing workflows. |

---

## 🏗 System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                INGESTION & DISCOVERY LAYER                             │
│  ┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────┐  │
│  │   SearXNG Metasearch    │   │  Firecrawl Scraper       │   │  ArXiv / Lab Feeds  │  │
│  │   (Port 8080)           │   │  (Port 3002)             │   │  (Raw HTML / PDF)   │  │
│  └────────────┬────────────┘   └────────────┬─────────────┘   └──────────┬──────────┘  │
└───────────────┼─────────────────────────────┼────────────────────────────┼─────────────┘
                │                             │                            │
                ▼                             ▼                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        GOOGLE ADK 2.x MULTI-AGENT EDITORIAL PIPELINE                   │
│                                                                                        │
│  ┌───────────────────────┐         ┌───────────────────────┐                           │
│  │    Discovery Agent    │ ──────> │    Research Agent     │                           │
│  │  (SearXNG Metasearch) │         │ (Firecrawl Synthesis) │                           │
│  └───────────────────────┘         └───────────┬───────────┘                           │
│                                                │                                       │
│                                                ▼                                       │
│  ┌───────────────────────┐         ┌───────────────────────┐                           │
│  │    Selection Agent    │ <────── │   Evaluation Agent    │                           │
│  │  (70/20/10 Portfolio) │         │  (5-Factor Scoring)   │                           │
│  └───────────┬───────────┘         └───────────────────────┘                           │
│              │                                                                         │
│              ▼                                                                         │
│  ┌───────────────────────┐         ┌───────────────────────┐                           │
│  │     Writing Agent     │ ◄─────► │     Critic Agent      │ (Max 2 Revision Cycles)   │
│  │  (Why-It-Matters)     │         │ (Adversarial Auditor) │                           │
│  └───────────┬───────────┘         └───────────────────────┘                           │
└──────────────┼─────────────────────────────────────────────────────────────────────────┘
               │  Tool Calls (MCP stdio bridge)
               ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EDITORIAL MCP SERVER                                   │
│  - get_editorial_context          - submit_candidates_batch   - stage_edition_draft    │
│  - get_publication_gate_status    - publish_edition           - unpublish_edition      │
│  - record_manual_override         - query_candidate_details   - get_editorial_memory   │
│  - update_scoring_weights         - get_feedback_analytics                            │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │  FastAPI REST API
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              POSTGRESQL 16 PERSISTENCE                                 │
│  - editions / stories / sources   - candidate_evaluations     - editorial_memory       │
│  - reader_feedback                - categories                - pipeline_runs          │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              REACT + TYPESCRIPT FRONTEND                               │
│  - Masthead & Theme Engine        - Lead Story Hero Card      - Secondary Stories Grid │
│  - 1-Click Reader Feedback        - Search & Archive Views    - Admin Inspector Drawer │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The Six Specialized Editorial Agents

The platform coordinates six specialized agents configured via Google ADK 2.x and LiteLLM (`agents/app/agents/`):

### 1. Discovery Agent (`discovery.py`)
- **Mission**: Scans external ecosystems via SearXNG for frontier model releases, systems innovations, custom silicon, throughput milestones, and binding AI governance.
- **Queries**: Executes a 5-dimension query matrix covering inference frameworks, open-weight architectures, hardware/accelerators, evaluation benchmarks, and regulation.
- **Constraints**: Ignores generic vendor blog posts, non-technical hype, and celebrity social media commentary.

### 2. Research Agent (`research.py`)
- **Mission**: Resolves canonical primary sources (arXiv PDFs, official GitHub repositories, original lab technical reports) via Firecrawl.
- **Extraction**: Extracts exact technical metrics: model parameters, context window lengths, memory footprints, tokens/sec throughput, latency speedups, and verified hardware topologies.

### 3. Evaluation Agent (`evaluation.py`)
- **Mission**: Computes dimensional scores across 5 vectors and aggregates the composite score $S$.
- **Tiers**: Classifies candidates into `Core` ($S \ge 6.0$), `Exploratory` ($5.0 \le S < 6.0$), `Contrarian` ($S \ge 5.0$), or `Rejected` ($S < 5.0$).
- **Audit**: Generates human-readable rejection reasons (e.g., *"Rejected: Vendor marketing fluff without verifiable benchmark data"*).

### 4. Selection Agent (`selection.py`)
- **Portfolio Constraint**: Enforces target distribution: **70% Core**, **20% Exploratory**, **10% Contrarian**.
- **Lead Story**: Designates exactly 1 Lead Story possessing the highest combination of architectural significance and broader systems consequence.
- **Diversity**: Caps stories to a maximum of 2 per category.
- **Low-Signal Rule**: If fewer than 5 candidates meet threshold, sets `low_signal_notice` rather than lowering editorial standards.

### 5. Writing Agent (`writing.py`)
- **Headline**: High-information, active-voice, news-wire style.
- **Why It Matters**: Mandatory 2–3 sentence analysis detailing concrete implications for engineers and systems designers.
- **Tone**: Technical, sober, analytical. Zero hyperbole.
- **Banned Buzzwords**: Strictly enforces bans on *game-changer, groundbreaking, next-gen, revolutionizing, paradigm shift, unifies all, mind-blowing, silver bullet*.

### 6. Critic Agent (`critic.py`)
- **Adversarial Audit**: Scans generated drafts for ungrounded claims, missing primary sources, banned buzzwords, and Publication Gate violations.
- **Self-Correction Feedback**: Returns structured critique items (`file_issues`, `buzzwords_detected`, `pass_gate`).
- **Loop**: Feeds issues back to the Writing Agent for up to 2 automated revision cycles.

---

## 🔌 The Editorial MCP Server

The **Editorial MCP Server** (`editorial_mcp/server.py`) adheres to the open **Model Context Protocol** specification, running over standard I/O (`stdio`) or HTTP. It isolates editorial state management from LLM logic.

### Registered Tools (11 Tools)

```json
[
  { "name": "get_editorial_context",       "description": "Fetch lookback coverage, candidate history, weights & feedback analytics" },
  { "name": "submit_candidates_batch",     "description": "Persist full candidate audit trail with dimensional scores & rejection reasons" },
  { "name": "stage_edition_draft",         "description": "Stage a complete multi-story daily briefing draft in PostgreSQL" },
  { "name": "get_publication_gate_status", "description": "Verify PRD Section 36 gate criteria on a staged edition" },
  { "name": "publish_edition",             "description": "Transition a verified draft to live published status" },
  { "name": "unpublish_edition",           "description": "Withdraw an edition back to draft status" },
  { "name": "record_manual_override",      "description": "Log human editor override for memory and fine-tuning signals" },
  { "name": "query_candidate_details",     "description": "Retrieve full candidate audit record by ID" },
  { "name": "get_editorial_memory",        "description": "Fetch past repetition warnings and active scoring weights" },
  { "name": "update_scoring_weights",      "description": "Adjust multi-factor scoring weights in persistent database memory" },
  { "name": "get_feedback_analytics",      "description": "Fetch aggregated reader upvotes, downvotes, and category biases" }
]
```

Run standalone for inspection:
```bash
make mcp-server
```

---

## 📐 Scoring Engine & Publication Gate

### 1. The Multi-Factor Scoring Formula

Every candidate is evaluated on a $[0.0, 10.0]$ scale across 5 distinct dimensions:

$$S = 0.35 \cdot 	ext{Significance} + 0.25 \cdot 	ext{Novelty} + 0.20 \cdot 	ext{Evidence} - 0.20 \cdot 	ext{Saturation} + w_5 \cdot 	ext{FeedbackBias}$$

| Parameter | Weight | Description |
| :--- | :---: | :--- |
| **Significance ($	ext{Sig}$)** | $0.35$ | Magnitude of architectural, economic, or capability impact. |
| **Novelty ($	ext{Nov}$)** | $0.25$ | Genuine paradigm shift vs. derivative wrapper or minor version bump. |
| **Evidence ($	ext{Evi}$)** | $0.20$ | Rigor of verification: peer-reviewed paper, open weights, reproducible code. |
| **Saturation ($	ext{Sat}$)** | $-0.20$ | Penalty for topic exhaustion within the 28-day lookback window. |
| **Feedback Bias ($	ext{FB}$)** | $w_5 \in [0.05, 0.15]$ | Reader approval rate bias ($2 \cdot (	ext{ApprovalRate} - 0.5)$). Zeroed during cold-start. |

### 2. Publication Gate Enforcement (PRD Section 36)

Before any edition transitions to `published`, the gate verifies:
1. **Story Count**: $\ge 5$ stories for a standard edition, OR an explicit `low_signal_notice` explaining candidate scarcity.
2. **Lead Story**: Exactly 1 story flagged with `is_lead = true`.
3. **Mandatory Analysis**: Every story must have a non-empty `why_it_matters` section ($\ge 30$ chars).
4. **Primary Sources**: Every story must have at least 1 verified primary source URL.
5. **No Slugs Collisions**: All story slugs within the edition must be strictly unique.
6. **No Banned Buzzwords**: Zero tolerance for sensationalist buzzwords.

---

## 🏆 Golden Evaluation Benchmark

To guarantee editorial quality across model updates, the platform includes an automated ground-truth benchmark suite (`agents/tests/eval/`):

- **Dataset**: `golden_cases.jsonl` contains 16 curated test cases covering true breakthroughs, silicon advances, schedulers, regulatory codes, PR fluff, celebrity posts, version bumps, and rumors.
- **Targets vs. Actuals**:

| Metric | PRD Target | Benchmark Result | Status |
| :--- | :---: | :---: | :---: |
| **Precision** | $\ge 85.0\%$ | **100.0%** | ✅ PASS |
| **Recall** | $\ge 85.0\%$ | **100.0%** | ✅ PASS |
| **Fluff Rejection Rate** | $\ge 95.0\%$ | **100.0%** | ✅ PASS |
| **Tier Accuracy** | $\ge 60.0\%$ | **68.8%** | ✅ PASS |

Run the benchmark anytime:
```bash
make adk-eval
```

---

## 💻 Frontend & Editorial Inspector

The user interface is built with **React 18**, **TypeScript**, and custom **Vanilla CSS** inspired by modern editorial typography (*Newsreader* serif + *Plus Jakarta Sans* UI + *JetBrains Mono* metrics).

### Features
- **Masthead**: Volume/Number, live edition metadata, and dark/light theme switch.
- **Lead Story Hero Card**: High-contrast editorial card featuring headline, summary, expandable body, primary source chips, and 1-click feedback voting.
- **Secondary Stories Grid**: Clean multi-column card layout with individual "Why It Matters" callouts.
- **Archive & Taxonomy**: Historical timeline of editions and category-level filtering.
- **Editorial Admin & Pipeline Inspector**: Slide-out panel providing real-time visibility into:
  - **Candidate Pipeline**: Live score audit trails, status badges, and rejection explanations.
  - **Draft Staging & Gate Controls**: Publication gate validation and 1-click publish/unpublish.
  - **ADK 2.x Agents & Eval**: Visual agent status cards, LiteLLM configuration, and live evaluation benchmark results.

Access the UI at: **`http://localhost:5173/`** or **`http://<LAN_IP>:5173/`**.

---

## 📁 Directory Structure

```text
ainews/
├── Makefile                          # Unified build, runtime, and test management
├── docker-compose.yml                # Postgres 16, SearXNG, and Firecrawl services
├── PRD2.md                           # Product Requirements Document (Google ADK & MCP)
├── plan2.md                          # Implementation & Migration Plan
│
├── backend/                          # FastAPI Intranet REST Service
│   ├── app/
│   │   ├── api/                      # Public, Editorial, Admin, and Feedback endpoints
│   │   ├── core/                     # Config, Database engine, and Security
│   │   ├── models/                   # SQLAlchemy ORM (Edition, Story, Candidate, Feedback)
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   └── services/                 # ScoringEngine, Ingestion, Deduplication, Feedback
│   └── tests/                        # 28 backend unit & integration tests
│
├── editorial_mcp/                    # Editorial Model Context Protocol Server
│   ├── server.py                     # Async stdio MCP server (11 tools)
│   └── client.py                     # High-level async/sync MCP client
│
├── agents/                           # Google ADK 2.x & LiteLLM Multi-Agent System
│   ├── app/
│   │   ├── config.py                 # OpenRouter model resolution & environment
│   │   ├── agents/                   # 6 Specialized Editorial Agents
│   │   │   ├── discovery.py          # Ecosystem metasearch
│   │   │   ├── research.py           # Deep markdown technical extraction
│   │   │   ├── evaluation.py         # Multi-factor scoring & tiering
│   │   │   ├── selection.py          # 70/20/10 portfolio allocator & lead story
│   │   │   ├── writing.py            # Synthesis & anti-buzzword enforcement
│   │   │   └── critic.py             # Adversarial audit & publication gate
│   │   ├── tools/                    # Async tool bindings (SearXNG, Firecrawl, MCP)
│   │   └── workflows/
│   │       └── root_workflow.py      # Master workflow & Critic revision loop
│   ├── run_editorial_workflow.py     # CLI execution runner
│   └── tests/                        # 19 agent, workflow, tool, and eval tests
│       ├── unit/                     # Agent initialization and tool binding tests
│       └── eval/                     # Golden benchmark cases & runner
│
├── frontend/                         # React 18 + TypeScript + Vite Web Application
│   ├── src/
│   │   ├── App.tsx                   # Main editorial application shell
│   │   ├── index.css                 # Custom editorial typography & design system
│   │   ├── api.ts                    # Typed API client
│   │   └── components/
│   │       ├── Header.tsx            # Masthead, navigation & theme toggle
│   │       ├── LeadStoryCard.tsx     # Hero story component with feedback
│   │       ├── StoryCard.tsx         # Secondary story component
│   │       ├── ArchiveView.tsx       # Historical edition timeline
│   │       ├── CategoryView.tsx      # Taxonomy browser
│   │       ├── SearchView.tsx        # GIN-indexed full-text search
│   │       └── AdminInspector.tsx    # Pipeline, gate, and ADK agent inspector
│   └── vite.config.ts                # Vite dev server with /api proxy to FastAPI
│
└── scripts/                          # Utility & Simulation Scripts
    ├── simulate_editorial_run.py     # Standalone pipeline simulation runner
    └── seed_demo_edition.py          # Seed multi-day briefings & feedback records
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Linux / macOS**
- **Python 3.11+**
- **Node.js 18+** & `npm`
- **Docker** & **Docker Compose**
- An **OpenRouter API Key** (or direct Anthropic / OpenAI / DeepSeek key)

### 1. Clone & Configure Environment

```bash
git clone https://github.com/your-org/ainews.git
cd ainews

# Copy and edit environment variables
cp .env.example .env
```

Ensure your `.env` contains:
```ini
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/ainews
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
LLM_MODEL=deepseek/deepseek-v4-flash-0731
EDITORIAL_SECRET_KEY=your-secure-editorial-token
ADMIN_API_TOKEN=your-secure-admin-token
```

### 2. Start Background Infrastructure

Start PostgreSQL, SearXNG, and Firecrawl via Docker Compose:
```bash
make start
```

### 3. Initialize Database

Run migrations and seed the initial taxonomy:
```bash
make migrate
make seed
```

*(Optional)* Seed rich multi-day demo briefings and reader feedback:
```bash
make seed-demo
```

### 4. Launch Development Services

In separate terminal sessions:

```bash
# Terminal 1: Backend API (port 8000)
make backend

# Terminal 2: Frontend UI (port 5173)
make frontend
```

Verify service status:
```bash
make status
```

---

## 🛠 Management CLI & Makefile

The project includes a streamlined `Makefile` for all common operations:

| Command | Description |
| :--- | :--- |
| `make start` | Start containerized services (Postgres, SearXNG, Firecrawl) |
| `make stop` | Stop containerized services |
| `make restart` | Restart containerized services |
| `make status` | Health check across Postgres, SearXNG, Firecrawl, Backend, and Frontend |
| `make ps` | Display running container status |
| `make logs` | Tail Docker container logs |
| `make backend` | Launch FastAPI backend dev server on `http://0.0.0.0:8000` |
| `make frontend` | Launch Vite frontend dev server on `http://0.0.0.0:5173` |
| `make mcp-server` | Run the Editorial MCP Server over standard I/O (`stdio`) |
| `make run-agents` | Execute the Google ADK multi-agent workflow in curated demo mode |
| `make run-agents-live` | Execute the Google ADK workflow with live SearXNG web discovery |
| `make adk-eval` | Run the Golden Evaluation benchmark suite |
| `make test` | Run the complete automated test suite (47 tests across backend and agents) |
| `make test-agents` | Run ADK agent, tool, and workflow tests only |
| `make test-skill` | Run standalone simulated pipeline runner |
| `make test-skill-live` | Run simulated pipeline runner with live SearXNG discovery |
| `make seed-demo` | Populate database with realistic multi-day editions and feedback |
| `make migrate` | Execute Alembic database migrations |
| `make seed` | Seed domain taxonomy categories |
| `make verify-db` | Verify PostgreSQL tables, GIN indexes, and schemas |
| `make clean` | Clean temporary Python and cache files |

---

## 📡 API Reference

### Public Endpoints (`/api/public/`)
- `GET /api/public/editions/today`: Fetch today's published edition with Lead Story and secondary stories.
- `GET /api/public/editions/{date}`: Fetch published edition by ISO date (`YYYY-MM-DD`).
- `GET /api/public/editions`: Paginated list of historical edition summaries.
- `GET /api/public/search?q={query}`: GIN-indexed full-text search across all published stories.
- `GET /api/public/categories`: List all taxonomy categories.
- `POST /api/public/feedback`: Submit 1-click reader feedback (`{ story_id, vote: 1 | -1, session_id }`).

### Editorial MCP Bridge Endpoints (`/api/editorial/`) *(Bearer Auth)*
- `POST /api/editorial/context`: Fetch lookback window, candidate history, and active weights.
- `POST /api/editorial/candidates`: Ingest batch candidate evaluation audit trails.
- `POST /api/editorial/draft`: Stage an edition draft for Publication Gate inspection.
- `GET /api/editorial/edition/{id}/status`: Inspect Publication Gate compliance status.
- `POST /api/editorial/edition/{id}/publish`: Publish a compliant draft.
- `POST /api/editorial/edition/{id}/unpublish`: Retract a published edition.
- `POST /api/editorial/override`: Log manual editor override for memory tracking.
- `GET /api/editorial/feedback-history`: Retrieve historical vote telemetry.
- `GET /api/editorial/memory`: Retrieve active editorial memory and weights.

---

## ⚙️ Configuration Reference

All settings are configured via `.env` or system environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async SQLAlchemy PostgreSQL connection string |
| `SEARXNG_URL` | `http://127.0.0.1:8080` | Local SearXNG metasearch instance endpoint |
| `FIRECRAWL_URL` | `http://127.0.0.1:3002` | Local Firecrawl markdown scraper endpoint |
| `OPENROUTER_API_KEY` | *None* | OpenRouter API Key for LiteLLM agent execution |
| `LLM_MODEL` | `deepseek/deepseek-v4-flash-0731` | Model identifier passed to LiteLLM |
| `EDITORIAL_SECRET_KEY` | `hermes_editorial_secret...` | Bearer token for Editorial MCP Server & Agent tools |
| `ADMIN_API_TOKEN` | `admin_editorial_secret...` | Bearer token for administrative overrides |
| `MIN_STORIES_PER_EDITION` | `5` | Minimum stories threshold before Low-Signal Notice is triggered |
| `DISCOVERY_LOOKBACK_HOURS` | `28` | Search lookback window for candidate discovery |
| `EDITORIAL_LOOKBACK_DAYS` | `28` | Memory lookback window for saturation penalty calculation |
| `FEEDBACK_COLD_START_DAYS` | `30` | Days required before reader feedback influences scoring |
| `FEEDBACK_COLD_START_THRESHOLD`| `100` | Minimum reader votes required before feedback influences scoring |

---

## 🧪 Testing Suite

The repository maintains an automated test suite with **100% pass rate (47 / 47 tests)**:

```bash
# Run all 47 tests
make test

# Run agent and workflow tests only
make test-agents

# Run Golden Evaluation benchmark
make adk-eval
```

### Test Coverage Breakdown
- **Backend Tests (28 tests)**: URL canonicalization, Jaccard candidate clustering, Publication Gate rules, scoring engine calculations, cold-start thresholds, portfolio partitioning, and MCP server tool dispatch.
- **Agent Tests (19 tests)**: Google ADK 2.x agent initialization, tool bindings, LiteLLM model resolution, multi-agent coordinator workflow, Critic revision loop buzzword elimination, low-signal day handling, and Golden Evaluation regression tests.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
