# Plan: Identifying High-Impact Primary AI News Domains

## 1. Objective
Our current archive domain distribution is heavily skewed toward a small set of cloud provider blogs and lab feeds (AWS at ~30%, OpenAI at ~23%, Google at ~19%), leaving major sectors of the AI frontier underrepresented or absent.

The goal of this plan is to **empirically discover where the most important AI news originates globally**, independent of our existing platform, feeds, or internal biases.

---

## 2. Guiding Principles
1. **Primary Sources Over Secondaries:** Prioritize where breakthroughs, release weights, technical specs, and peer-reviewed results are first published—not SEO aggregators or wire regurgitators.
2. **Empirical Data Over Intuition:** Derive the target domain list by mining where technical communities, researchers, and established curators point when major breakthroughs occur.
3. **Multi-Sector Coverage:** Ensure discovery covers the entire AI stack: Frontier Labs, Open Weights / Systems, Compute / Silicon, Academic Labs, and Governance / Safety.

---

## 3. Four-Pronged Discovery Methodology

```
┌────────────────────────────────────────────────────────────────────────┐
│                      EMPIRICAL DOMAIN DISCOVERY                        │
└────────────────────────────────────────────────────────────────────────┘
          │                   │                  │                │
          ▼                   ▼                  ▼                ▼
   Hacker News &       Curator Inversion   Top Hugging Face    Targeted Milestone
  Community Mining      (Newsletter URLs)   & arXiv Papers      Backtracking
 (Algolia Point-Rank) (Jack Clark, Ng, etc) (Citation Links)   (Key Breakthroughs)
          │                   │                  │                │
          └───────────────────┴────────┬─────────┴────────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ Domain Normalization & Filter │
                       │ (Remove SEO spam, aggregators)│
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │   Categorization & Scoring    │
                       │   (Tier 1 / Tier 2 Domains)   │
                       └───────────────────────────────┘
```

### Phase 1: Community Consensus Mining (Hacker News Algolia API)
Hacker News represents the highest signal-to-noise ratio for engineering and research breakthroughs in AI.
- **Action:** Query the public Algolia HN Search API for submissions from the last 12 months containing core AI keywords (`LLM`, `transformer`, `frontier model`, `open weights`, `GPU cluster`, `agent`, `reasoning`).
- **Filter Criteria:** Posts with $\ge 150$ points and $\ge 50$ comments.
- **Metric:** Group by root domain and calculate:
  - Total qualifying submissions
  - Average points per domain
  - Community discussion volume

### Phase 2: Curator Citation Inversion
Reverse-engineer the source material of recognized, top-tier independent AI curators.
- **Action:** Collect the archive issues of 5 respected technical curators:
  - *Import AI* (Jack Clark / Anthropic Co-founder)
  - *The Batch* (Andrew Ng / DeepLearning.AI)
  - *Interconnects* (Nathan Lambert / AI2)
  - *Ahead of AI* (Sebastian Raschka)
  - *SemiAnalysis* (Dylan Patel / Silicon & Compute)
- **Extraction:** Extract all external outbound links and resolve them to their base domains.
- **Metric:** Rank domains by frequency of citation across multiple independent curators.

### Phase 3: Research & Open Weights Traceability
Major algorithmic and architectural advancements publish technical papers or model repositories before commercial PR.
- **Hugging Face Trending Hub:** Mine the external blog/paper links listed in the model cards of the top 100 trending open-weight models (e.g. DeepSeek, Qwen, Mistral, Meta Llama, Gemma, AllenAI).
- **arXiv High-Citation Ingestion:** Scan papers in `cs.AI`, `cs.CL`, `cs.LG`, and `stat.ML` with the highest social and citation velocity, noting author affiliation domains and hosted lab sites.

### Phase 4: Milestone Backtracking (Past 12 Months)
Take 20 undisputed major AI events from the past year (e.g., DeepSeek-R1 release, Llama 3/3.1 launch, Claude 3.5 Sonnet release, NVIDIA Blackwell benchmarks, AlphaFold 3 release, OpenAI o1/o3 reasoning announcements) and identify:
- Where the canonical announcement was published (primary domain).
- Where the technical documentation / evaluation benchmarks were hosted.

---

## 4. Ecosystem Categorization Grid

To prevent single-sector over-indexing (e.g. cloud provider tutorials), domains will be mapped into five essential categories:

| Category | Description | Target Archetypes |
|:---|:---|:---|
| **1. Frontier Labs** | Organizations pushing the frontier of model training and reasoning. | Anthropic, OpenAI, Google DeepMind, Meta FAIR, xAI, DeepSeek |
| **2. Open Weights & Frameworks** | Foundations, open research groups, and inference/serving runtimes. | Hugging Face, Mistral, Together AI, vLLM, SGLang, Ollama, Allen Institute (AI2) |
| **3. Silicon & Compute Infrastructure** | Hardware vendors, cluster architects, and semiconductor analysts. | NVIDIA Technical Blog, SemiAnalysis, AMD AI, Cerebras, TSMC, Cloud TPU Blog |
| **4. Academic Labs & Research Institutes** | Peer-reviewed academic groups producing novel architectures and safety foundations. | arXiv, Stanford HAI, Berkeley BAIR, CMU ML, MIT CSAIL, Epoch AI |
| **5. Policy, Standards & Governance** | Regulatory bodies, safety evaluation institutes, and standards organizations. | US/UK AI Safety Institutes (NIST CAISI, UK AISI), AI Alignment Forum, Frontier Model Forum |

---

## 5. Execution Steps

1. **Step 1: Automated Scraping & Data Extraction**
   - Write a standalone Python script to fetch the top 1,000 AI stories from the Hacker News Algolia API.
   - Run URL extraction on public archives of target technical newsletters.

2. **Step 2: Cleaning & Normalization**
   - Strip link shorteners (`t.co`, `bit.ly`).
   - Discard generic platforms (`youtube.com`, `x.com`, `reddit.com`) and extract the underlying target content domain if linked in threads.
   - Exclude generic press release aggregators (`prnewswire.com`, `businesswire.com`) and generic tech blogs that rewrite primary announcements.

3. **Step 3: Scoring & Domain Ranking**
   - Rank candidate domains using a Composite Impact Score:
     $$\text{Score} = (\text{HN Citations} \times 2) + (\text{Curator Citations} \times 3) + (\text{Model Card / Milestone Links} \times 4)$$

4. **Step 4: Output & Deliverable**
   - Produce a vetted **Master AI Source Directory** with:
     - Verified primary domain and RSS/Atom/API endpoint.
     - Content classification (Frontier, Silicon, Academic, etc.).
     - Ingestion priority tier (Tier 1: Daily/Breaking, Tier 2: Weekly Deep-Dive).

---

## 6. Success Metrics
- **Zero Provider Dominance:** No single company or cloud vendor accounts for more than 15% of the total incoming signal.
- **Coverage of Missing Frontier Players:** All major frontier labs (Anthropic, DeepSeek, Meta AI, NVIDIA Developer, etc.) have verified primary endpoints identified.
- **Signal-to-Noise Ratio:** Identified domains publish substantive architectural, code, model, or policy developments rather than promotional marketing.
