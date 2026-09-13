# Evaluation Plan: AI News Sources Whitelist Audit

## Overview & Objectives

This evaluation plan establishes the methodology, tools, and test harness to validate the 35 source entries defined in `evaluation/whitelist.csv`. 

The objective is to answer four key operational questions for the AI News Letter pipeline:
1. **Can we reach these sources reliably?** (Network, DNS, SSL/TLS, HTTP status).
2. **Are they blocked by captchas or anti-bot defenses?** (Cloudflare Turnstile, Datadome, PerimeterX, login/paywalls).
3. **Do they have good content?** (Frontier technical signal vs marketing PR, noise, or generic aggregations).
4. **Should the domains be scoped further?** (Targeting `/feed`, `/news/research`, RSS/Atom feeds, API endpoints, or subdirectories rather than bare landing pages).

---

## Tooling & MCP Server Integration

We utilize the existing tools and MCP services built into the AI News platform:

| Service / Tool | Code Location | Role in Evaluation |
| :--- | :--- | :--- |
| **URL Validator** | `backend/app/services/url_validator.py` / `agents/app/tools/url_validator_tool.py` | Validates HTTP status codes (200 OK vs 403/404/500), follow redirects, headers inspection. |
| **Firecrawl Client** | `backend/app/services/firecrawl.py` / `agents/app/tools/firecrawl_tool.py` | Tests full-page Markdown extraction, content density, and identifies JS-rendering / anti-bot challenge pages. |
| **SearXNG Engine** | `backend/app/services/searxng.py` / `agents/app/tools/searxng_tool.py` | Evaluates domain-specific search indexability (`site:<domain>`), freshness, and discovery viability. |
| **Editorial MCP Server** | `editorial_mcp/server.py` | Syncs approved source evaluation results and scraping guidelines into `editorial_memories` (table `editorial_memories`) for pipeline agent enforcement. |
| **Headless Browser** | `browser_subagent` / Playwright | Inspects DOM rendering for 403/challenge pages (e.g. Cloudflare Turnstile, PerimeterX) to identify solvable vs hard barriers. |

---

## 4-Step Evaluation Workflow

```
[evaluation/whitelist.csv]
           │
           ▼
[Step 1: Network & HTTP Reachability] ──> (Status Codes, Redirects, Latency)
           │
           ▼
[Step 2: Bot & Captcha Detection]     ──> (Cloudflare, Paywalls, Datadome, Reddit limits)
           │
           ▼
[Step 3: Content Extraction & Signal] ──> (Markdown density, Signal-to-Noise, Primary vs Secondary)
           │
           ▼
[Step 4: Domain Scoping & Feed Audit] ──> (RSS / Atom / API / Subdirectory optimization)
           │
           ▼
[Outputs: evaluation_report.md + whitelist_evaluated.csv + MCP Memory Sync]
```

### Step 1: Network & HTTP Reachability Probe
- Execute async HTTP GET / HEAD requests with desktop browser headers (`User-Agent`, `Accept`).
- Identify HTTP 200 vs 301/302 redirects vs 403 Forbidden / 404 Not Found / 429 Too Many Requests.
- Record final resolved URL and response time.

### Step 2: Captcha, Anti-Bot & Paywall Analysis
- **Cloudflare Interstitials**: Check for Cloudflare Turnstile / challenge tokens (`cf-mitigated`, "Just a moment...").
- **Commercial Anti-Bot Systems**: Detect Datadome, PerimeterX (Human Security), and Akamai bot management.
- **Paywalls**: Classify paywalls into:
  - *Hard Paywalls* (*The Information*, *WSJ*, *FT*): Full text inaccessible without credentials.
  - *Metered / Soft Paywalls* (*MIT Tech Review*, *Bloomberg*): Snippets accessible, full text restricted.
  - *Open Technical Access* (*ArXiv*, *Hugging Face*, *DeepMind*, *GitHub*).
- **Rule Formulation**: Domains with hard paywalls are marked as `secondary_discovery_only` (used by SearXNG to detect breaking stories, but research agent must find primary open sources).

### Step 3: Content Quality & Signal-to-Noise Evaluation
- Calculate **Content Density Ratio**: ratio of substantive article text to navigation/ad boilerplate.
- Assess **Editorial Alignment**:
  - *Tier 1 (Frontier Labs)*: Anthropic, OpenAI, DeepMind, Meta AI, Mistral. (Highest priority for frontier model breakthroughs).
  - *Tier 2 (Industry & Silicon)*: SemiAnalysis, Reuters, Bloomberg. (Essential for compute infrastructure, CAPEX, supply chains).
  - *Tier 3 (Technical Newsletters & Analysis)*: Latent Space, Interconnects, Last Week in AI, Import AI. (Deep context and technical curation).
  - *Tier 4 (Preprints & Raw Communities)*: ArXiv, Reddit. (High discovery value, but high noise; requires filtering).

### Step 4: Domain Scoping & Endpoint Optimization
- Determine whether each URL in `whitelist.csv` should be refined:
  1. **Substack & Newsletters**: Refine to RSS feeds (`/feed`) for clean XML/Markdown parsing.
  2. **ArXiv Preprints**: Replace HTML list scraping (`arxiv.org/list/cs.AI/recent`) with the structured ArXiv API (`export.arxiv.org/api/query`) or Hugging Face Daily Papers.
  3. **Reddit Communities**: Use JSON API (`https://www.reddit.com/r/LocalLLaMA/top.json?t=day&limit=15`) with a minimum score filter (e.g. score >= 100) to strip noise and memes.
  4. **Primary Lab Newsrooms**: Scope to research-specific categories (e.g., `openai.com/news/research` instead of consumer announcements).

---

## Test Automation Plan

We will build the following scripts in `evaluation/`:

1. **`evaluate_whitelist.py`**:
   - Automated async script that parses `whitelist.csv`.
   - Runs all 4 evaluation steps against each domain.
   - Saves results to `evaluation/whitelist_evaluated.csv` and compiles `evaluation/evaluation_report.md`.

2. **`sync_editorial_sources.py`**:
   - Connects to the Editorial MCP server or database.
   - Registers the vetted domain policies into `editorial_memories` with key `source_domain_whitelist`.

---

## Initial Domain Triage Summary

| Domain | Status | Captcha / Paywall | Signal Quality | Recommended Scoping |
| :--- | :--- | :--- | :--- | :--- |
| `openai.com/news` | 403 on raw HTTP | Cloudflare protection | Very High | Use Firecrawl / SearXNG / RSS feed (`openai.com/news/rss.xml`) |
| `anthropic.com/news` | 200 OK / dynamic JS | Occasional Cloudflare | Exceptional | Target `/news` or RSS feed |
| `deepmind.google/discover/blog` | 200 OK | None | Exceptional | Scope to `/discover/blog` or RSS |
| `semianalysis.com` | 200 OK | Substack paywall (partial) | Outstanding | Scope to `semianalysis.com/feed` |
| `theinformation.com/ai` | 403 / Paywall | Hard Paywall + Datadome | High (Scoops) | **Secondary Discovery Only** via SearXNG; do not scrape body |
| `bloomberg.com/technology` | 403 / Paywall | Hard Paywall + PerimeterX | High (Business) | **Secondary Discovery Only** via SearXNG |
| `arxiv.org/list/cs.AI/recent` | 200 OK | Strict rate limits | High, but noisy | Use ArXiv API with query & citation filter |
| `reddit.com/r/LocalLLaMA` | 200 / Bot blocking | Reddit User-Agent block | High community value | Scope to Reddit JSON API with `score >= 100` filter |
| `latent.space` | 200 OK | None | Exceptional | Scope to `latent.space/feed` |
| `interconnects.ai` | 200 OK | None | Exceptional | Scope to `interconnects.ai/feed` |
