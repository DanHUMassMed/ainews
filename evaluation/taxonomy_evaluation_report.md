# Taxonomy & Story Filtering Evaluation Report

## 1. Executive Summary

An audit of the editorial taxonomy classification and filtering pipeline revealed that **only ~64% of production stories are properly aligned with their assigned domains**, with **44% of the database polluted by mock/future test artifacts**, **20.3% of real stories having zero categories (orphans)**, and **33.3% of taxonomy domains completely dead (0 stories)**.

| Metric | Current State | Target Baseline | Status |
| :--- | :--- | :--- | :--- |
| **Database Cleanliness** | 56.0% (62 mock test stories) | 100.0% | ❌ Severe Pollution |
| **Category Recall (Tagged Stories)** | 79.7% (16 orphan stories) | > 98.0% | ⚠️ Degraded |
| **Domain Precision / False Positives** | ~64.0% (e.g. 9 Hardware false positives) | > 92.0% | ❌ Unaligned |
| **Scope Integrity (AI Only)** | 93.7% (5 non-AI stories) | 100.0% | ⚠️ Leakage |
| **Active Categories** | 8 of 12 (4 dead domains) | 12 of 12 | ❌ Dead Domains |
| **Frontend Filter Integrity** | Lead story bypasses filter | 100% Filter compliance | ❌ Critical UI Bug |

---

## 2. Root Cause Analysis: How the System Works & Where it Breaks

### A. Ingestion & Pre-Filtering Flaws
- Ingestion pulls from whitelisted RSS feeds (such as the general AWS Architecture / Machine Learning feeds). 
- Articles without AI relevance (e.g., *Serverless Git metrics pipeline for QuickSight*, *BMW cloud cost anomaly detection*) are ingested because relevance checks rely on generic heuristics rather than semantic domain gates.

### B. Categorization Mechanism (`infer_story_categories`)
In `agents/app/workflows/root_workflow.py`, category assignment relies on naive substring searches:
```python
if any(k in combined for k in ["hardware", "gpu", "accelerator", "cluster", "chips", ...]):
    categories.append("hardware")
```
- **False Positives**: Any article mentioning that a model was deployed on an "accelerator cluster" or "Nvidia GPUs" is incorrectly tagged as `hardware`, even if the article is about legal software (e.g., *Astra for Law*) or cloud pricing.
- **Dead Categories**: `science-ai` and `ai-business` have zero keywords in `infer_story_categories`. Venture funding articles are forced into `enterprise-ai`.
- **Naming Confusion**: The category `open-ai` is ambiguous (conflating OpenAI company news with open-weight models), leading to 0 organic production classifications.
- **Writing Agent Disconnect**: While `WritingAgent` instructions mention category taxonomy, the JSON output schema requested from the LLM only asks for `{"headline", "summary", "why_it_matters", "body"}`. The agent's semantic understanding of the story is discarded, and the system falls back to the flawed regex engine.

### C. Frontend Taxonomy Tab Bug (`App.tsx`)
In `frontend/src/App.tsx`:
```typescript
const lead = edition.lead_story || allStories.find((s) => s.is_lead) || allStories[0];
```
When a user selects a category (e.g., "Regulation"), the filter runs on `allStories`, but `lead` unconditionally defaults to `edition.lead_story`. If the lead story is about "AI Models", it is displayed at the top under "TODAY'S LEAD STORY" despite the user filtering for "Regulation".

Additionally, selecting a category currently only filters the 5–8 stories of today's edition instead of calling the existing backend endpoint `GET /api/public/categories/{slug}` to show all historical stories in that domain.

---

## 3. Discovered Data Anomalies

### 1. Mock / Future Test Stories (62 rows)
- Editions with dates between 2030 and 2253 (e.g. `2253-05-22`, `2154-01-27`, `2056-12-11`).
- Titles like *"Significant AI Technical Advance Number 1 in Infrastructure"*, *"MCP Valid Lead Story for Test Edition"*.

### 2. Non-AI Off-Topic Stories
- *How BMW Group detects cost anomalies across 14,000 cloud accounts*
- *Serverless Git metrics pipeline delivers near-real-time QuickSight analytics*
- *OpenAI and AARP launch ChatGPT workshops for 1,000 older adults*
- *Google and UN Launch Searchable Open Data Commons Platform*

### 3. Orphan Stories (0 Categories)
- *Altman Proposes UN-Backed Compute Governance for Frontier AI* (Should be: `regulation`)
- *Private AI Compute adds encrypted server-side memory* (Should be: `infrastructure`, `developer-tools`)
- *Hugging Face Releases Tokenizers v1 with Faster Rust Pipeline* (Should be: `developer-tools`)
- *Gemini 3.8 Live adds low-latency streaming* (Should be: `ai-models`)

---

## 4. Remediation Plan

1. **Purge Polluted Data**: Delete the 62 mock/future editions and stories from the production database.
2. **Remove Off-Topic Stories**: Remove non-AI entries (*BMW cost anomalies*, *Git metrics*).
3. **Re-align Category Mappings**: Update `story_categories` for the 79 real stories so that orphans are classified and false positives (e.g. `hardware` on software/law) are removed.
4. **Fix Frontend Taxonomy Filtering**:
   - Update `App.tsx` so `leadStory` honors `selectedCategory` (or hides the lead banner if no lead matches).
   - Update `CategoryView.tsx` to display true story counts and render a dedicated category archive view using `GET /api/public/categories/{slug}`.
5. **Upgrade Pipeline Classification**:
   - Update `WritingAgent` to include `category_slugs` in its structured output.
   - Refactor `infer_story_categories` to use whole-word matching and include `science-ai`, `ai-business`, and `robotics`.
   - Add a strict scope gate to reject non-AI feed items during discovery.
