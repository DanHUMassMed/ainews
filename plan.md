# Refactoring Plan

## Preface: Areas of Minor Disagreement / Modification
While the review provides excellent guidance, I am proposing slight modifications to two of the recommendations to balance architectural purity with pragmatism:

1. **Database vs. Config Files for Extensibility (OCP):** The review suggests moving `COMMON_ENTITIES` and category inferences to the database or a configuration file. For simple lists that change infrequently, building a full database schema and admin UI is often overkill. We will instead extract these into a YAML or JSON configuration file, which satisfies OCP without unnecessary overhead.
2. **Interface Segregation for MCP Client (ISP):** Splitting the `EditorialMCPClient` into separate classes (`EditorialReader`, `CandidateSubmitter`, `EditionPublisher`) is conceptually correct. However, to avoid creating multiple HTTP/transport connections or duplicating setup logic, we will implement this by having the specialized clients wrap a shared connection manager (or using composition) rather than acting as completely independent network clients.
3. **Overly Granular API Responses:** Creating a separate `StoryListItem` vs `StoryResponse` is good, but we should ensure we don't prematurely optimize if the data size is small. We will implement this, but keep the schema simple.

---

## Phase 1: Consolidation and Shared Utilities (DRY & Config)
*Goal: Eliminate duplication and establish a single source of truth for configuration and common functions.*

1. **Configuration Unification:**
   - Create a shared configuration package (or move `backend/app/core/config.py` logic to a place accessible by both).
   - Update `agents/app/config.py` to import from this unified config rather than redefining `os.getenv()` calls.
2. **Utility Extraction:**
   - Create `backend/app/utils/urls.py` for `extract_domain()` and `normalize_url()`.
   - Create `backend/app/utils/dates.py` for `parse_datetime_flexible()`.
   - Create `backend/app/utils/text.py` for `slugify()`, `strip_html()`, and `PROHIBITED_BUZZWORDS`.
   - Update `scoring.py`, `whitelist.py`, `selection.py`, `schemas/source.py`, `root_workflow.py`, and `writing.py` to use these shared utilities.
3. **Text Sanitization:**
   - Extract text sanitization logic currently mixed in the writing agent to a dedicated `agents/app/utils/text_sanitizer.py`.

## Phase 2: Abstractions and Dependency Inversion (LSP & DIP)
*Goal: Decouple high-level workflow logic from concrete implementations.*

1. **Service Interfaces (Protocols/ABCs):**
   - Define Python `Protocol`s for `SearchService`, `ScraperService`, `WhitelistService`, and `ScoringService`.
2. **Dependency Injection:**
   - Refactor `root_workflow.py`, `editorial_memory.py`, and API routers (`editorial.py`, `public.py`) to accept these interfaces via constructors or FastAPI's `Depends()`.
   - Manage the lifecycle of singletons (e.g., `WhitelistService` caches, `SearXNGClient`) using FastAPI's dependency injection system instead of module-level variables.
3. **Fix Sync Client (LSP):**
   - Refactor `EditorialMCPSyncClient` to use a `concurrent.futures.ThreadPoolExecutor` instead of wrapping `asyncio.run()` directly, preventing event loop crashes.

## Phase 3: Workflow and Routing Decomposition (SRP)
*Goal: Break down God Objects and fat routers into single-responsibility components.*

1. **Deconstruct `root_workflow.py`:**
   - Extract each pipeline step into its own class (e.g., `DiscoveryStep`, `SelectionStep`, `WritingStep`).
   - Leave `root_workflow.py` as an orchestrator that simply calls these modular steps.
2. **Refactor API Routers:**
   - Move inline business logic out of routers. For example, move the inline vote counting in `public.py`'s `build_story_response()` into `FeedbackService`, preferably using a single batch SQL query or view.

## Phase 4: Interface Segregation and Type Safety (ISP & Types)
*Goal: Ensure clients only depend on what they need and improve type safety across the pipeline.*

1. **Split MCP Client:**
   - Divide `EditorialMCPClient` into `EditorialReader`, `CandidateSubmitter`, and `EditionPublisher`, ensuring they share a single underlying transport to avoid connection bloat.
2. **Type Safety Enhancements:**
   - Define `TypedDict` or `Pydantic` dataclasses for Candidates, Dossiers, and Evaluated Items to replace `Dict[str, Any]` in the agents layer.
   - Update `response_model`s in `editorial.py` from `Dict[str, Any]` to proper Pydantic schemas.
3. **Slim API Responses:**
   - Introduce a `StoryListItem` schema without nested `sources` and `categories` lists for list endpoints, reserving the fat `StoryResponse` for detail views.

## Phase 5: Extensibility Improvements (OCP)
*Goal: Make the system easier to extend without modifying existing code.*

1. **Discovery Sources:**
   - Implement a `DiscoverySource` abstract base class.
   - Refactor `SearXNGDiscovery`, `RSSDiscovery`, etc., to inherit from it and register them in a discovery manager.
2. **Configuration Extensibility:**
   - Move `COMMON_ENTITIES` (from `editorial_memory.py`) and category inference mappings into a YAML configuration file.

## Phase 6: Error Handling and Observability
*Goal: Stop swallowing errors and improve system visibility.*

1. **Refine Error Catching:**
   - Replace bare `except Exception:` blocks in `public.py` and `whitelist.py` with specific exception handling.
2. **Add Structured Logging:**
   - Implement structured logging with request context across backend API routes.
   - Ensure `search_stories()` logs original exceptions before falling back.

## Phase 7: Frontend Refactoring
*Goal: Improve maintainability and UX of the React frontend.*

1. **Component Decomposition:**
   - Split `App.tsx` (480+ lines) into modular sub-components.
   - Break down `AdminInspector.tsx` (1,465 lines) into smaller, single-purpose components.
2. **State and Styling:**
   - Extract data fetching logic (like `loadEdition`) into custom hooks (e.g., `useEdition`).
   - Migrate inline styles to CSS classes (using the project's existing CSS strategy, e.g., vanilla CSS or Tailwind).
3. **UX Improvements:**
   - Persist `session_id` in `localStorage` so vote history survives page reloads.
   - Implement React Error Boundaries to prevent entire app crashes from unhandled render errors.

## Phase 8: Testing Gaps
*Goal: Ensure the new architecture functions correctly end-to-end.*

1. **Integration Testing:**
   - Write integration tests for the full agent pipeline.
   - Add tests for all backend API endpoints.
2. **Unit Testing:**
   - Add unit tests for `ScoringEngine.partition_portfolio()` to verify diversity enforcement.
   - Add tests for `DeduplicationService.cluster_candidates()`.
   - Add tests for `FeedbackService.get_analytics()`.
