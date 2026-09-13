# AI News Whitelist Sources Evaluation Report

**Date:** 2026-09-12 | **Total Sources Evaluated:** 47

## Executive Summary

- **Direct HTTP 200 Reachable:** 38 / 47 (80.9%)
- **Blocked / Challenge Interstitial:** 8 / 47 (17.0%)
- **Paywalled Outlets:** 8 / 47
- **Clean RSS / Atom / API Feeds Discovered:** 30 / 47 (63.8%)
- **SearXNG Search Indexable:** 8 / 47

---

## Core Findings & Architectural Answers

### 1. Can we reach these sources?
Most open tech labs, engineering blogs, research institutes, and newsletters resolve directly with HTTP 200. However, major lab newsrooms (e.g. `openai.com/news`) and Tier 2 financial press return HTTP 403 or require browser headers and trailing slash enforcement.

### 2. Are they blocked by captcha?
- **Cloudflare Turnstile**: `openai.com`, `theinformation.com`, `techcrunch.com`.
- **PerimeterX / HUMAN Anti-Bot**: `bloomberg.com`, `wsj.com`.
- **Reddit Anti-Bot User-Agent Blocking**: `reddit.com/r/LocalLLaMA` and `r/MachineLearning`.
**Mitigation**: Use SearXNG search caching, RSS feeds (`/feed`), and Reddit JSON endpoints instead of direct HTML scraping.

### 3. Do they have good content?
- **Tier 1 & Newsletters**: Frontier labs (Anthropic, OpenAI, DeepMind, Meta, Qwen, Mistral) and specialist newsletters (*SemiAnalysis*, *Latent Space*, *Interconnects*, *Simon Willison*, *Import AI*) offer pristine editorial signal.
- **Preprints & Community Forums**: *ArXiv* lists and *Reddit* have high signal buried under substantial volume. They require strict threshold filtering.
- **Commercial Scoops**: *The Information*, *Bloomberg*, *WSJ*, and *FT* provide high-value business scoops, but full text cannot be scraped. They should serve as *lead triggers* for primary source searches.

### 4. Should the domains be scoped further?
**Yes, universally:**
1. **Substack Newsletters & Developer Blogs**: Ingest via clean `/feed` or `/atom/entries/` endpoints.
2. **ArXiv**: Switch from `/list/cs.AI/recent` HTML scraping to ArXiv API queries.
3. **Reddit**: Use `.json?t=day&limit=15` with an upvote filter threshold (`score >= 100`).
4. **Paywall Outlets**: Categorize as `secondary_discovery_only`.

---

## Detailed Source-by-Source Scorecard

| URL Path | Tier | Status | Challenge / Barrier | Feed Endpoint | Recommended Strategy | Action |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| `openai.com/news` | Tier 1 | **`403`** | Cloudflare Turnstile / Challenge | `rss.xml` | firecrawl_or_feed | Stealth Markdown Scrape / RSS |
| `anthropic.com/news` | Tier 1 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `deepmind.google/discover/blog` | Tier 1 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `blog.google/technology/ai` | Tier 1 | `200` | None | `rss` | rss_feed | Direct Feed Ingestion |
| `ai.meta.com/blog` | Tier 1 | **`400`** | None | None | direct_scrape | Direct Firecrawl Scrape |
| `mistral.ai/news` | Tier 1 | `200` | None | `rss` | rss_feed | Direct Feed Ingestion |
| `huggingface.co/blog` | Tier 1 | `200` | None | `feed.xml` | rss_feed | Direct Feed Ingestion |
| `blogs.nvidia.com/blog/category/deep-learning` | Tier 1 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `news.microsoft.com/source/features/ai` | Tier 1 | **`404`** | None | `feed` | secondary_discovery_only | Lead Discovery Signal |
| `aws.amazon.com/blogs/machine-learning` | Tier 1 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `cohere.com/blog` | Tier 1 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `x.ai/news` | Tier 1 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `qwenlm.github.io/blog` | Tier 1 | `200` | None | `index.xml` | rss_feed | Direct Feed Ingestion |
| `research.google/blog` | Tier 1 | `200` | None | `rss` | rss_feed | Direct Feed Ingestion |
| `ai21.com/blog` | Tier 2 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `01.ai/blog` | Tier 2 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `z.ai/blog` | Tier 2 | **`404`** | None | None | direct_scrape | Direct Firecrawl Scrape |
| `reuters.com/technology/artificial-intelligence` | Tier 2 | **`401`** | None | None | direct_scrape | Direct Firecrawl Scrape |
| `bloomberg.com/technology` | Tier 2 | **`403`** | PerimeterX / HUMAN Anti-Bot | None | secondary_discovery_only | Lead Discovery Signal |
| `wsj.com/tech/ai` | Tier 2 | **`401`** | None | None | secondary_discovery_only | Lead Discovery Signal |
| `ft.com/artificial-intelligence` | Tier 2 | **`403`** | Cloudflare Turnstile / Challenge | `rss.xml` | secondary_discovery_only | Lead Discovery Signal |
| `theinformation.com/artificial-intelligence` | Tier 2 | **`403`** | Cloudflare Turnstile / Challenge | `feed` | secondary_discovery_only | Lead Discovery Signal |
| `semianalysis.com` | Tier 2 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `epoch.ai` | Tier 2 | `200` | None | None | direct_scrape_or_feed | Direct Technical Report Scrape |
| `metr.org` | Tier 2 | `200` | None | `index.xml` | direct_scrape_or_feed | Direct Technical Report Scrape |
| `arxiv.org/list/cs.AI/recent` | Tier 4 | `200` | None | `query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=10&sortBy=submittedDate` | api_query | Filtered API Ingestion |
| `arxiv.org/list/cs.CL/recent` | Tier 4 | `200` | None | `query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=10&sortBy=submittedDate` | api_query | Filtered API Ingestion |
| `arxiv.org/list/cs.LG/recent` | Tier 4 | `200` | None | `query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=10&sortBy=submittedDate` | api_query | Filtered API Ingestion |
| `paperswithcode.com` | Tier 4 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `nature.com/subjects/machine-learning` | Tier 4 | `200` | None | None | direct_scrape | Direct Firecrawl Scrape |
| `alignmentforum.org` | Tier 4 | `200` | None | `rss` | rss_feed | Direct Feed Ingestion |
| `reddit.com/r/LocalLLaMA` | Tier 4 | `200` | None | None | json_filtered | Threshold-Gated Community Pulse |
| `reddit.com/r/MachineLearning` | Tier 4 | `200` | None | None | json_filtered | Threshold-Gated Community Pulse |
| `latent.space` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `interconnects.ai` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `stratechery.com` | Tier 3 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `techcrunch.com/category/artificial-intelligence` | Tier 3 | `200` | Cloudflare Turnstile / Challenge | `feed` | rss_feed | Direct Feed Ingestion |
| `lastweekin.ai` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `importai.net` | Tier 3 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `venturebeat.com/category/ai` | Tier 3 | `200` | None | `feed` | rss_feed | Direct Feed Ingestion |
| `technologyreview.com/topic/artificial-intelligence` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `arstechnica.com/ai` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `theverge.com/ai-artificial-intelligence` | Tier 3 | `200` | Hard / Metered Paywall | `rss.xml` | rss_feed | Direct Feed Ingestion |
| `simonwillison.net` | Tier 3 | `200` | None | `` | rss_feed | Direct Feed Ingestion |
| `aiweekly.co` | Tier 3 | `200` | Hard / Metered Paywall | `feed` | rss_feed | Direct Feed Ingestion |
| `openreview.net` | Tier 4 | `200` | Cloudflare Turnstile / Challenge | None | api_query | Structured API / Search |
| `papers.cool` | Tier 4 | `200` | None | None | direct_scrape | Scoped Category Ingestion |

---

## Actionable Scoping & Ingestion Directory

### `openai.com/news` (Tier 1 - Primary Lab)
- **Endpoint:** `https://openai.com/news/rss.xml`
- **Strategy:** `firecrawl_or_feed` | **Action:** Stealth Markdown Scrape / RSS
- **Scoping Recommendation:** Direct HTTP returns 403. Use Firecrawl stealth mode or official RSS feed. Focus on /research and /announcements tags.
- **SearXNG Indexed:** Yes (5 items found)

### `anthropic.com/news` (Tier 1 - Primary Lab)
- **Endpoint:** `https://anthropic.com/news`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** Yes (5 items found)

### `deepmind.google/discover/blog` (Tier 1 - Primary Lab)
- **Endpoint:** `https://deepmind.google/discover/blog/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** Yes (5 items found)

### `blog.google/technology/ai` (Tier 1 - Primary Lab)
- **Endpoint:** `https://blog.google/technology/ai/rss`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `ai.meta.com/blog` (Tier 1 - Primary Lab)
- **Endpoint:** `https://ai.meta.com/blog/ (with trailing slash)`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Enforce trailing slash on request (ai.meta.com/blog/) to avoid HTTP 400 redirect error. High signal for Llama and FAIR research.
- **SearXNG Indexed:** No (0 items found)

### `mistral.ai/news` (Tier 1 - Primary Lab)
- **Endpoint:** `https://mistral.ai/news/rss`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `huggingface.co/blog` (Tier 1 - Ecosystem / Open Source)
- **Endpoint:** `https://huggingface.co/blog/feed.xml`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** Yes (5 items found)

### `blogs.nvidia.com/blog/category/deep-learning` (Tier 1 - Compute / Hardware)
- **Endpoint:** `https://blogs.nvidia.com/blog/category/deep-learning/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `news.microsoft.com/source/features/ai` (Tier 1 - Enterprise Cloud)
- **Endpoint:** `SearXNG site:news.microsoft.com + RSS snippets`
- **Strategy:** `secondary_discovery_only` | **Action:** Lead Discovery Signal
- **Scoping Recommendation:** Do NOT attempt full text scrape. Ingest headline/summary as lead signal, then execute primary source search (GitHub/paper/lab blog) for verification.
- **SearXNG Indexed:** No (0 items found)

### `aws.amazon.com/blogs/machine-learning` (Tier 1 - Enterprise Cloud)
- **Endpoint:** `https://aws.amazon.com/blogs/machine-learning/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `cohere.com/blog` (Tier 1 - Primary Lab)
- **Endpoint:** `https://cohere.com/blog`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `x.ai/news` (Tier 1 - Primary Lab)
- **Endpoint:** `https://x.ai/news`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `qwenlm.github.io/blog` (Tier 1 - Primary Lab)
- **Endpoint:** `https://qwenlm.github.io/blog/index.xml`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `research.google/blog` (Tier 1 - Primary Lab)
- **Endpoint:** `https://research.google/blog/rss`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** Yes (5 items found)

### `ai21.com/blog` (Tier 2 - Primary Lab)
- **Endpoint:** `https://ai21.com/blog`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `01.ai/blog` (Tier 2 - Primary Lab)
- **Endpoint:** `https://01.ai/blog`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `z.ai/blog` (Tier 2 - Primary Lab)
- **Endpoint:** `https://z.ai/blog`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `reuters.com/technology/artificial-intelligence` (Tier 2 - Global Wire Service)
- **Endpoint:** `https://reuters.com/technology/artificial-intelligence`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `bloomberg.com/technology` (Tier 2 - Business & Financial)
- **Endpoint:** `SearXNG site:bloomberg.com + RSS snippets`
- **Strategy:** `secondary_discovery_only` | **Action:** Lead Discovery Signal
- **Scoping Recommendation:** Do NOT attempt full text scrape. Ingest headline/summary as lead signal, then execute primary source search (GitHub/paper/lab blog) for verification.
- **SearXNG Indexed:** No (0 items found)

### `wsj.com/tech/ai` (Tier 2 - Business & Policy)
- **Endpoint:** `SearXNG site:wsj.com + RSS snippets`
- **Strategy:** `secondary_discovery_only` | **Action:** Lead Discovery Signal
- **Scoping Recommendation:** Do NOT attempt full text scrape. Ingest headline/summary as lead signal, then execute primary source search (GitHub/paper/lab blog) for verification.
- **SearXNG Indexed:** No (0 items found)

### `ft.com/artificial-intelligence` (Tier 2 - Global Financial)
- **Endpoint:** `SearXNG site:ft.com + RSS snippets`
- **Strategy:** `secondary_discovery_only` | **Action:** Lead Discovery Signal
- **Scoping Recommendation:** Do NOT attempt full text scrape. Ingest headline/summary as lead signal, then execute primary source search (GitHub/paper/lab blog) for verification.
- **SearXNG Indexed:** Yes (1 items found)

### `theinformation.com/artificial-intelligence` (Tier 2 - Scoops & Business)
- **Endpoint:** `SearXNG site:theinformation.com + RSS snippets`
- **Strategy:** `secondary_discovery_only` | **Action:** Lead Discovery Signal
- **Scoping Recommendation:** Do NOT attempt full text scrape. Ingest headline/summary as lead signal, then execute primary source search (GitHub/paper/lab blog) for verification.
- **SearXNG Indexed:** No (0 items found)

### `semianalysis.com` (Tier 2 - Silicon & Infra Deep-Dive)
- **Endpoint:** `https://semianalysis.com/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `epoch.ai` (Tier 2 - AI Research & Forecasting)
- **Endpoint:** `https://epoch.ai`
- **Strategy:** `direct_scrape_or_feed` | **Action:** Direct Technical Report Scrape
- **Scoping Recommendation:** High signal technical reports on compute thresholds and frontier capability evaluations. Scrape research papers and report summaries directly.
- **SearXNG Indexed:** Yes (2 items found)

### `metr.org` (Tier 2 - AI Safety & Evaluation)
- **Endpoint:** `https://metr.org/index.xml`
- **Strategy:** `direct_scrape_or_feed` | **Action:** Direct Technical Report Scrape
- **Scoping Recommendation:** High signal technical reports on compute thresholds and frontier capability evaluations. Scrape research papers and report summaries directly.
- **SearXNG Indexed:** No (0 items found)

### `arxiv.org/list/cs.AI/recent` (Tier 4 - Preprints)
- **Endpoint:** `http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=15&sortBy=submittedDate`
- **Strategy:** `api_query` | **Action:** Filtered API Ingestion
- **Scoping Recommendation:** Avoid HTML scraping of /recent (rate-limits and hundreds of low-signal preprints). Query ArXiv API with explicit category filter and abstract length check.
- **SearXNG Indexed:** Yes (5 items found)

### `arxiv.org/list/cs.CL/recent` (Tier 4 - Preprints)
- **Endpoint:** `http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=15&sortBy=submittedDate`
- **Strategy:** `api_query` | **Action:** Filtered API Ingestion
- **Scoping Recommendation:** Avoid HTML scraping of /recent (rate-limits and hundreds of low-signal preprints). Query ArXiv API with explicit category filter and abstract length check.
- **SearXNG Indexed:** No (0 items found)

### `arxiv.org/list/cs.LG/recent` (Tier 4 - Preprints)
- **Endpoint:** `http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&max_results=15&sortBy=submittedDate`
- **Strategy:** `api_query` | **Action:** Filtered API Ingestion
- **Scoping Recommendation:** Avoid HTML scraping of /recent (rate-limits and hundreds of low-signal preprints). Query ArXiv API with explicit category filter and abstract length check.
- **SearXNG Indexed:** No (0 items found)

### `paperswithcode.com` (Tier 4 - Benchmarks & SOTA)
- **Endpoint:** `https://paperswithcode.com`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `nature.com/subjects/machine-learning` (Tier 4 - Peer-Reviewed Science)
- **Endpoint:** `https://nature.com/subjects/machine-learning`
- **Strategy:** `direct_scrape` | **Action:** Direct Firecrawl Scrape
- **Scoping Recommendation:** Standard web scrape via Firecrawl with mainContent isolation.
- **SearXNG Indexed:** No (0 items found)

### `alignmentforum.org` (Tier 4 - Safety & Alignment)
- **Endpoint:** `https://alignmentforum.org/rss`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `reddit.com/r/LocalLLaMA` (Tier 4 - Community / Open Weights)
- **Endpoint:** `https://www.reddit.com/r/localllama/top.json?t=day&limit=15`
- **Strategy:** `json_filtered` | **Action:** Threshold-Gated Community Pulse
- **Scoping Recommendation:** Bypass HTML bot blocks using Reddit JSON endpoint with custom user-agent. Enforce strict filter: upvotes >= 100 and comment_count >= 15.
- **SearXNG Indexed:** No (0 items found)

### `reddit.com/r/MachineLearning` (Tier 4 - Community / Research)
- **Endpoint:** `https://www.reddit.com/r/machinelearning/top.json?t=day&limit=15`
- **Strategy:** `json_filtered` | **Action:** Threshold-Gated Community Pulse
- **Scoping Recommendation:** Bypass HTML bot blocks using Reddit JSON endpoint with custom user-agent. Enforce strict filter: upvotes >= 100 and comment_count >= 15.
- **SearXNG Indexed:** No (0 items found)

### `latent.space` (Tier 3 - AI Engineering & Stack)
- **Endpoint:** `https://latent.space/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `interconnects.ai` (Tier 3 - Technical Newsletter)
- **Endpoint:** `https://interconnects.ai/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `stratechery.com` (Tier 3 - Strategic Business Tech)
- **Endpoint:** `https://stratechery.com/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `techcrunch.com/category/artificial-intelligence` (Tier 3 - Venture & Startups)
- **Endpoint:** `https://techcrunch.com/category/artificial-intelligence/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `lastweekin.ai` (Tier 3 - Curated Digest)
- **Endpoint:** `https://lastweekin.ai/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `importai.net` (Tier 3 - AI Policy & Governance)
- **Endpoint:** `https://importai.net/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `venturebeat.com/category/ai` (Tier 3 - Enterprise AI)
- **Endpoint:** `https://venturebeat.com/category/ai/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `technologyreview.com/topic/artificial-intelligence` (Tier 3 - Tech Analysis)
- **Endpoint:** `https://technologyreview.com/topic/artificial-intelligence/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `arstechnica.com/ai` (Tier 3 - Tech Journalism)
- **Endpoint:** `https://arstechnica.com/ai/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `theverge.com/ai-artificial-intelligence` (Tier 3 - Tech Journalism)
- **Endpoint:** `https://theverge.com/rss.xml`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Clean RSS feed identified. Use feed parser to extract title, publication date, and full text.
- **SearXNG Indexed:** No (0 items found)

### `simonwillison.net` (Tier 3 - AI Engineering / Developer)
- **Endpoint:** `https://simonwillison.net/atom/entries/`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `aiweekly.co` (Tier 3 - Curated Digest)
- **Endpoint:** `https://aiweekly.co/feed`
- **Strategy:** `rss_feed` | **Action:** Direct Feed Ingestion
- **Scoping Recommendation:** Ingest directly via clean RSS/Atom feed endpoint. Yields complete markdown/content without paywall popups or styling clutter.
- **SearXNG Indexed:** No (0 items found)

### `openreview.net` (Tier 4 - Peer Review / Research)
- **Endpoint:** `https://api2.openreview.net or SearXNG site:openreview.net`
- **Strategy:** `api_query` | **Action:** Structured API / Search
- **Scoping Recommendation:** Heavy client-side SPA. Ingest via OpenReview REST API or SearXNG to target accepted papers and oral presentations.
- **SearXNG Indexed:** No (0 items found)

### `papers.cool` (Tier 4 - Research Discovery)
- **Endpoint:** `https://papers.cool/arxiv/cs.AI`
- **Strategy:** `direct_scrape` | **Action:** Scoped Category Ingestion
- **Scoping Recommendation:** Scope to specific arXiv subcategory feeds (e.g. /arxiv/cs.AI, /arxiv/cs.CL) for curated Kimi/community paper highlights.
- **SearXNG Indexed:** No (0 items found)
