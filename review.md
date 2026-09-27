# AI Industry News Daily — SOLID Principles Code Review

**Reviewer:** Automated Code Review Agent
**Date:** 2026-09-27
**Scope:** Full codebase — Backend (FastAPI), Agents (Google ADK), Frontend (React/Vite), Editorial MCP Server

---

## Overall Grade: **B-** (73/100)

The project is ambitious, well-structured at the macro level, and clearly built by someone who understands the domain deeply. The 6-agent editorial pipeline, MCP protocol integration, multi-factor scoring engine, and PostgreSQL-backed memory system are all genuinely impressive architectural choices. However, there are meaningful SOLID violations that will create friction as the codebase grows. The review below breaks down each principle with concrete file-level findings.

---

## Table of Contents

- [S — Single Responsibility Principle](#s--single-responsibility-principle-grade-c)
- [O — Open/Closed Principle](#o--openclosed-principle-grade-b)
- [L — Liskov Substitution Principle](#l--liskov-substitution-principle-grade-b)
- [I — Interface Segregation Principle](#i--interface-segregation-principle-grade-b-)
- [D — Dependency Inversion Principle](#d--dependency-inversion-principle-grade-c)
- [General Code Quality Findings](#general-code-quality-findings)
- [Security Findings](#security-findings)
- [Summary & Priority Recommendations](#summary--priority-recommendations)

---

## S — Single Responsibility Principle (Grade: C+)

> *"A class should have one, and only one, reason to change."*

### Violations

#### 1. `root_workflow.py` — The God Object (Critical)

This is the most significant SRP violation in the project. `EditorialWorkflow` is a ~700-line class that handles:

- Discovery orchestration (RSS, SearXNG, Reddit, ArXiv)
- URL validation and research
- Multi-factor scoring evaluation
- Portfolio selection and diversity enforcement
- Story synthesis and writing
- Adversarial critique and revision loop
- Edition staging and publication via MCP
- HTML sanitization and slug generation
- Date parsing and timezone normalization
- Category inference

**Every pipeline change** — whether it's adjusting the scoring formula, adding a new discovery source, tweaking the writing prompt, or modifying the critique loop — requires touching this single file. It has at least **10 distinct reasons to change**.

**Recommendation:** Extract each pipeline step into its own class (e.g., `DiscoveryStep`, `ResearchStep`, `EvaluationStep`, `SelectionStep`, `WritingStep`, `CritiqueStep`, `PublishStep`). The workflow class should only orchestrate the sequence.

```python
# Instead of one massive class:
class EditorialWorkflow:
    def __init__(self, steps: List[PipelineStep]):
        self.steps = steps

    async def run(self, context: PipelineContext) -> WorkflowResult:
        for step in self.steps:
            context = await step.execute(context)
        return context.result
```

#### 2. `editorial.py` API Router — Too Many Hats

The editorial API router (`backend/app/api/editorial.py`) mixes:

- Authentication logic (`/auth` endpoint doing plaintext password comparison)
- CRUD operations for candidates, editions, and memory
- Scoring configuration management (get/update/reset)
- Feedback analytics aggregation
- A `slugify()` utility function defined inline
- Inline Pydantic model definitions (`AdminAuthRequest`)

**Recommendation:** Split into sub-routers: `editorial_auth.py`, `editorial_candidates.py`, `editorial_scoring.py`, `editorial_memory.py`. Move `slugify()` to a shared `utils.py`.

#### 3. `writing.py` Agent — Writing + Sanitization + Formatting

The writing agent module contains the LLM agent definition, prompt engineering, *and* deterministic text sanitization logic (`sanitize_story_completeness`, `clean_sentence_closure`, `format_newspaper_headline`, `audit_story_draft`, `clean_markdown_headings_from_prose`, `format_body_markdown`). These pure text-processing functions have nothing to do with LLM orchestration.

**Recommendation:** Extract all text sanitization into `agents/app/utils/text_sanitizer.py`. The writing agent should delegate to it.

#### 4. `public.py` API — Inline Vote Counting

The `build_story_response()` helper executes two separate SQL queries (upvotes and downvotes) for *each story*. This is a data-access concern mixed into a response-building concern.

**Recommendation:** Move vote aggregation into `FeedbackService` and call it once with a batch of story IDs, or pre-aggregate with a SQL subquery or database view.

### What's Done Well

- **Models** are cleanly separated, each in its own file with a single table responsibility.
- **Schemas** are properly separated from models (Pydantic vs. SQLAlchemy).
- **Services** are generally focused: `DeduplicationService`, `ScoringEngine`, `FeedbackService`, `WhitelistService`, `URLValidatorService` each own one domain concept.

---

## O — Open/Closed Principle (Grade: B)

> *"Software entities should be open for extension, but closed for modification."*

### Violations

#### 1. Hardcoded Discovery Sources

Adding a new discovery source (e.g., Hacker News, OpenReview, Bluesky) requires modifying `root_workflow.py` directly. There's no plugin or registry pattern.

**Recommendation:** Create a `DiscoverySource` abstract base class and register implementations:

```python
class DiscoverySource(ABC):
    @abstractmethod
    async def discover(self, lookback_hours: int) -> List[Dict[str, Any]]: ...

class RSSDiscovery(DiscoverySource): ...
class SearXNGDiscovery(DiscoverySource): ...
class RedditDiscovery(DiscoverySource): ...
```

#### 2. Hardcoded Category Inference

`infer_story_categories()` in the workflow uses a hardcoded keyword-to-category mapping. Adding a new category requires editing the function body.

**Recommendation:** Load the mapping from configuration (database or YAML file).

#### 3. Hardcoded Entity List in `editorial_memory.py`

`COMMON_ENTITIES` is a static list of ~25 companies. The industry changes monthly.

**Recommendation:** Store in the database or a configuration file that can be updated without code deployment.

#### 4. Scoring Formula is Configurable (✓ Good)

The `ScoringEngine` loads weights and thresholds from the database with sensible defaults. The admin panel allows live updates. This is a genuine OCP win.

### What's Done Well

- Scoring weights/thresholds are database-driven with runtime configurability.
- The `MODEL_REGISTRY` in `agents/app/config.py` allows per-agent model overrides via environment variables — good extensibility.
- The MCP server design is inherently open to new tools being registered.

---

## L — Liskov Substitution Principle (Grade: B+)

> *"Objects of a superclass should be replaceable with objects of its subclasses without breaking the application."*

### Findings

#### 1. `EditorialMCPSyncClient` Wraps `asyncio.run()` — Dangerous Substitution

The `EditorialMCPSyncClient` claims to be a drop-in synchronous version of `EditorialMCPClient`, but calling `asyncio.run()` inside each method will **crash** if called from within an already-running event loop (e.g., from a FastAPI endpoint or an ADK agent callback). This violates LSP because the sync client *cannot* be used everywhere the async client can.

**Recommendation:** Use `asyncio.get_event_loop().run_until_complete()` with a check for running loops, or better yet, use a dedicated thread-pool pattern:

```python
import concurrent.futures
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def get_editorial_context(self, *args, **kwargs):
    loop = asyncio.new_event_loop()
    return _executor.submit(loop.run_until_complete,
        self._async.get_editorial_context(*args, **kwargs)).result()
```

#### 2. No Abstract Base Classes for Services

`WhitelistService`, `ScoringEngine`, `FeedbackService`, etc. are concrete classes with `@classmethod` or `@staticmethod` methods. There are no interfaces/ABCs, so LSP is somewhat vacuously satisfied — but it also means you can't substitute a mock or alternative implementation cleanly (e.g., an `InMemoryWhitelistService` for testing).

### What's Done Well

- Pydantic schemas form a clean hierarchy: `StoryBase` → `StoryCreate` / `StoryUpdate` / `StoryResponse`. Subclass contracts are respected.
- SQLAlchemy model relationships are well-defined and consistent.

---

## I — Interface Segregation Principle (Grade: B-)

> *"Clients should not be forced to depend on interfaces they do not use."*

### Violations

#### 1. `EditorialMCPClient` — One Client, All Operations

The `EditorialMCPClient` exposes **every** editorial operation (context, feedback, candidates, staging, publishing, overrides) in a single class. An agent that only needs to read editorial context is forced to depend on (and could accidentally call) `publish_edition()` or `record_editorial_override()`.

**Recommendation:** Split into role-based clients:

```python
class EditorialReader:      # get_editorial_context, get_feedback_analytics
class CandidateSubmitter:   # submit_candidate_stories, get_candidate_details
class EditionPublisher:     # stage_edition_draft, publish_edition, unpublish_edition
```

#### 2. `WhitelistService` — Mixed Responsibilities

The service mixes domain-level queries (`get_rss_feed_sources()`, `get_api_sources()`) with URL utility functions (`extract_domain()`, `is_whitelisted_domain()`). Consumers needing only domain extraction are coupled to the entire CSV-loading machinery.

#### 3. Fat API Responses

`StoryResponse` always includes `sources` and `categories` as nested lists, even on list endpoints where the client may only need titles and slugs. There's no "slim" response variant.

**Recommendation:** Consider a `StoryListItem` schema for list endpoints and reserve `StoryResponse` (with nested relations) for detail views.

### What's Done Well

- The backend API is cleanly split between `public` and `editorial` routers with different auth requirements.
- FastAPI's dependency injection (`Depends(get_db)`, `Security(verify_editorial_token)`) naturally segments concerns.

---

## D — Dependency Inversion Principle (Grade: C)

> *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*

### Violations

#### 1. Direct Module-Level Instantiation Everywhere (Critical)

This is the most pervasive DIP violation. Concrete implementations are imported and used directly with no abstraction layer:

- `root_workflow.py` directly imports and calls `SearXNGClient()`, `FeedIngestService`, `URLValidatorService`, `WhitelistService`, `ScoringEngine`, `EditorialMCPClient()`, `FirecrawlClient()`.
- `editorial_memory.py` directly imports `FeedbackService` and `ScoringEngine`.
- `editorial.py` API router directly imports `ScoringEngine`, `FeedbackService`, `EditorialMemoryService`.

If you wanted to swap SearXNG for a different search backend, replace Firecrawl with a different scraper, or use a different scoring algorithm, you'd need to modify every consumer.

**Recommendation:** Define protocols (ABCs) for key service interfaces and inject them:

```python
from typing import Protocol

class SearchService(Protocol):
    async def search(self, query: str, time_range: str) -> List[Dict]: ...

class ScraperService(Protocol):
    async def scrape_url(self, url: str) -> Dict[str, Any]: ...

class EditorialWorkflow:
    def __init__(self, search: SearchService, scraper: ScraperService, ...):
        self.search = search
        self.scraper = scraper
```

#### 2. Module-Level Singleton Pattern via Class Variables

`WhitelistService` uses class-level `_entries` and `_domain_map` as a manual singleton cache. `SearXNGClient` and `FirecrawlClient` are instantiated with hardcoded `settings.SEARXNG_URL` defaults in their constructors.

**Recommendation:** Use FastAPI's dependency injection to manage service lifecycle, or create a proper service registry/container.

#### 3. `config.py` Duplicated Across Layers

Configuration is defined in *two places*:
- `backend/app/core/config.py` — Pydantic `Settings` class
- `agents/app/config.py` — Standalone `os.getenv()` calls

Both define `APP_HOST`, `BACKEND_PORT`, `SEARXNG_URL`, `FIRECRAWL_URL`, etc. independently. When a configuration value changes, both files must be updated.

**Recommendation:** Have the agents layer import from the backend config, or create a shared config package at the project root.

#### 4. Database Session is Well-Injected (✓ Good)

The `get_db()` async generator with `Depends()` is textbook DIP for database access. Well done.

### What's Done Well

- FastAPI's `Depends()` mechanism is used correctly for database sessions and authentication.
- The MCP server acts as a clean abstraction layer between agents and the backend API.

---

## General Code Quality Findings

### DRY (Don't Repeat Yourself) Violations

| Violation | Files Involved |
|-----------|----------------|
| `extract_domain()` is implemented **3 separate times** | `scoring.py`, `whitelist.py`, `selection.py` |
| `parse_datetime_flexible()` date parsing logic is duplicated | `schemas/source.py`, `schemas/story.py`, `root_workflow.py` |
| `slugify()` logic appears in both | `editorial.py` and `root_workflow.py` |
| Edition-to-response mapping is copy-pasted | `public.py` and `editorial.py` |
| HTML stripping / `html.unescape()` chains | `schemas/story.py`, `root_workflow.py`, `writing.py` |
| `PROHIBITED_BUZZWORDS` list defined twice | `writing.py` and `root_workflow.py` |

**Recommendation:** Create shared utility modules:
- `backend/app/utils/urls.py` — `extract_domain()`, `normalize_url()`
- `backend/app/utils/dates.py` — `parse_datetime_flexible()`
- `backend/app/utils/text.py` — `slugify()`, `strip_html()`, `PROHIBITED_BUZZWORDS`

### Error Handling

| Issue | Location |
|-------|----------|
| Bare `except Exception` swallows errors silently | `public.py` search fallback, `whitelist.py` CSV parsing |
| No structured logging with request context | Backend API routes |
| `search_stories()` silently falls back on *any* exception, including programming errors | `public.py` |

**Recommendation:** Catch specific exceptions. Log the original error before falling back. Consider FastAPI exception handlers for consistent error responses.

### Type Safety

| Issue | Location |
|-------|----------|
| `Dict[str, Any]` used as the primary data structure throughout the agents pipeline | `root_workflow.py`, all agent modules |
| No TypedDict or dataclass for candidates, dossiers, or evaluated items | Agents layer |
| `response_model=Dict[str, Any]` on multiple editorial endpoints defeats OpenAPI documentation | `editorial.py` |

**Recommendation:** Define proper dataclasses or TypedDicts for the pipeline's internal data structures. Replace `Dict[str, Any]` response models with Pydantic schemas.

### Testing

The test suite (`agents/tests/unit/`) is genuinely strong for text sanitization and writing agent edge cases — good coverage of the Qwen-Image reproduction case. However:

| Gap | Impact |
|-----|--------|
| No integration tests for the full pipeline | Can't verify end-to-end flow |
| No tests for backend API endpoints | API regressions go undetected |
| No tests for `ScoringEngine.partition_portfolio()` edge cases | Diversity enforcement untested |
| No tests for `DeduplicationService.cluster_candidates()` | Clustering logic untested |
| No tests for `FeedbackService.get_analytics()` | Analytics calculations unverified |

### Frontend

| Issue | Impact |
|-------|--------|
| `App.tsx` is 480+ lines with inline styles, mixed state management, and render logic | Hard to maintain |
| `AdminInspector.tsx` is 1,465 lines — should be split into sub-components | Massive single component |
| No custom hooks for data fetching (`loadEdition` is inline in App) | Logic not reusable |
| Inline styles used extensively instead of CSS classes | Inconsistent, hard to theme |
| `session_id` for feedback is generated fresh each page load (no persistence) | Users lose vote history on refresh |
| No error boundaries | Unhandled render errors crash the entire app |

---

---

## Summary & Priority Recommendations

### Scorecard

| SOLID Principle | Grade | Key Issue |
|----------------|-------|-----------|
| **S** — Single Responsibility | **C+** | `root_workflow.py` God Object, bloated API routers |
| **O** — Open/Closed | **B** | Hardcoded discovery sources, entity lists, category mappings |
| **L** — Liskov Substitution | **B+** | Sync client `asyncio.run()` trap; no ABCs for testability |
| **I** — Interface Segregation | **B-** | Fat MCP client, bloated service interfaces |
| **D** — Dependency Inversion | **C** | No abstractions; direct concrete imports everywhere; duplicated config |

### Top 5 Refactoring Priorities

1. **Break up `root_workflow.py`** — Extract each pipeline step into its own class. This is the single highest-impact refactor.

2. **Introduce service abstractions (Protocols/ABCs)** — Define interfaces for `SearchService`, `ScraperService`, `ScoringService`, `WhitelistService`. Inject via constructor. Enables testing and swappability.

3. **Consolidate duplicated utilities** — `extract_domain()`, `parse_datetime_flexible()`, `slugify()`, `strip_html()`, `PROHIBITED_BUZZWORDS`. Create shared utility modules.

4. **Unify configuration** — Single source of truth for `APP_HOST`, `BACKEND_PORT`, `SEARXNG_URL`, etc. The agents layer should not re-derive these from `os.getenv()`.

5. **Fix security defaults** — Hash admin passwords, remove hardcoded credentials from source, restrict CORS origins, add rate limiting to auth endpoint.

### What's Already Strong

- **Domain modeling** — The SQLAlchemy models are clean, well-typed, and properly related.
- **Pydantic schema layer** — Good separation of concerns between API contracts and database models.
- **MCP architecture** — Using Model Context Protocol as the integration layer between agents and the backend is a forward-thinking design choice.
- **Scoring engine** — Database-driven weights with admin-panel configurability is exactly the right approach.
- **Test coverage for text sanitization** — The Qwen-Image reproduction tests demonstrate serious attention to real-world edge cases.
- **Makefile** — Clean, well-documented project automation.
- **Graceful degradation** — The frontend's triple-layer fallback (live → archive → localStorage cache) is production-thoughtful.

---

*This review evaluates architectural adherence to SOLID principles and is intended as constructive guidance. The project demonstrates strong domain expertise and a well-considered architecture that, with the refactoring priorities above, can scale significantly.*
