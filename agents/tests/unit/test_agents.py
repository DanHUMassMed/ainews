"""Unit tests for Specialized Editorial Agents in Google ADK 2.x."""

import pytest
from agents.app.agents import (
    create_discovery_agent,
    create_research_agent,
    create_evaluation_agent,
    create_selection_agent,
    create_writing_agent,
    create_critic_agent,
    select_edition_lineup_algorithmic,
    extract_source_entity,
    DISCOVERY_INSTRUCTION,
    RESEARCH_INSTRUCTION,
    EVALUATION_INSTRUCTION,
    SELECTION_INSTRUCTION,
    WRITING_INSTRUCTION,
    CRITIC_INSTRUCTION,
)
from google.adk.agents import LlmAgent

def test_discovery_agent_initialization():
    agent = create_discovery_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "DiscoveryAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 7
    tool_names = [t.__name__ for t in agent.tools]
    assert "search_web" in tool_names
    assert "run_discovery_matrix" in tool_names
    assert "fetch_editorial_memory" in tool_names
    assert "Discovery Agent" in agent.instruction

def test_research_agent_initialization():
    agent = create_research_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "ResearchAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 1
    assert agent.tools[0].__name__ == "scrape_webpage"
    assert "Research Agent" in agent.instruction
    assert "factual dossier" in agent.instruction

def test_evaluation_agent_initialization():
    agent = create_evaluation_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "EvaluationAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 2
    tool_names = [t.__name__ for t in agent.tools]
    assert "get_editorial_context" in tool_names
    assert "get_feedback_analytics" in tool_names
    assert "Significance" in agent.instruction
    assert "Novelty" in agent.instruction
    assert "Evidence" in agent.instruction
    assert "Saturation" in agent.instruction

def test_selection_agent_initialization():
    agent = create_selection_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "SelectionAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 2
    tool_names = [t.__name__ for t in agent.tools]
    assert "fetch_editorial_memory" in tool_names
    assert "submit_candidate_stories" in tool_names
    assert "70% Core" in agent.instruction
    assert "Low-Signal Day" in agent.instruction
    assert "Strict Source & Entity Diversity Constraints" in agent.instruction

def test_writing_agent_initialization():
    agent = create_writing_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "WritingAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 1
    assert agent.tools[0].__name__ == "get_editorial_context"
    assert "Why It Matters" in agent.instruction
    assert "Prohibited Words" in agent.instruction

def test_critic_agent_initialization():
    agent = create_critic_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "CriticAgent"
    assert "openrouter/" in agent.model
    assert len(agent.tools) == 3
    tool_names = [t.__name__ for t in agent.tools]
    assert "stage_edition_draft" in tool_names
    assert "get_edition_status" in tool_names
    assert "record_editorial_override" in tool_names
    assert "Publication Gate" in agent.instruction
    assert "Buzzword" in agent.instruction

def test_selection_source_entity_extraction():
    """Verify canonical entity resolution across subdomains and publishers."""
    assert extract_source_entity({"url": "https://aws.amazon.com/blogs/machine-learning/post-1", "publisher": "aws.amazon.com"}) == "amazon"
    assert extract_source_entity({"url": "https://blog.google/technology/ai/gemini-3", "publisher": "Google Blog"}) == "google"
    assert extract_source_entity({"url": "https://deepmind.google/discover/blog/paper", "publisher": "Google DeepMind"}) == "google"
    assert extract_source_entity({"url": "https://blogs.nvidia.com/blog/2026/09/rubin", "publisher": "NVIDIA"}) == "nvidia"
    assert extract_source_entity({"url": "https://developer.nvidia.com/blog/cuda-kernels", "publisher": "NVIDIA Developer"}) == "nvidia"
    assert extract_source_entity({"url": "https://openai.com/index/proaction", "publisher": "OpenAI"}) == "openai"
    assert extract_source_entity({"url": "https://latent.space/p/ainews", "publisher": "Latent Space"}) == "latent.space"
    assert extract_source_entity({"url": "https://qwenlm.github.io/blog/qwen-image", "publisher": "Qwen Team"}) == "qwen"
    assert extract_source_entity({"url": "https://mistral.ai/news/announcement", "publisher": "Mistral AI"}) == "mistral"
    assert extract_source_entity({"url": "https://semianalysis.com/feed/colossus", "publisher": "SemiAnalysis"}) == "semianalysis"

def test_selection_agent_prevents_aws_clustering_and_enforces_source_diversity():
    """Verify Selection Agent rejects multiple stories from same source (e.g. AWS) to diversify layout."""
    candidates = [
        # 3 AWS stories with high/medium scores
        {"title": "SkyRL on SageMaker HyperPod", "url": "https://aws.amazon.com/blogs/machine-learning/1", "publisher": "aws.amazon.com", "score": 6.80, "tier": "Core", "category_slugs": ["infrastructure"]},
        {"title": "NarrateAI on Amazon Bedrock", "url": "https://aws.amazon.com/blogs/machine-learning/2", "publisher": "aws.amazon.com", "score": 6.50, "tier": "Core", "category_slugs": ["infrastructure"]},
        {"title": "AWS EKS MoE RL Scaling", "url": "https://aws.amazon.com/blogs/machine-learning/3", "publisher": "aws.amazon.com", "score": 6.40, "tier": "Core", "category_slugs": ["infrastructure"]},
        # Other distinct ecosystem sources
        {"title": "Qwen-Image High-Resolution Synthesis", "url": "https://qwenlm.github.io/blog/qwen-image", "publisher": "qwenlm.github.io", "score": 6.75, "tier": "Core", "category_slugs": ["ai-models"]},
        {"title": "NVIDIA Rubin Platform Architecture", "url": "https://blogs.nvidia.com/blog/rubin", "publisher": "blogs.nvidia.com", "score": 6.60, "tier": "Core", "category_slugs": ["hardware"]},
        {"title": "Mistral and Cloudera Sovereign AI Partnership", "url": "https://mistral.ai/news/cloudera", "publisher": "mistral.ai", "score": 6.30, "tier": "Exploratory", "category_slugs": ["enterprise-ai"]},
        {"title": "OpenAI Proaction Systems Benchmark", "url": "https://openai.com/index/proaction", "publisher": "openai.com", "score": 6.20, "tier": "Core", "category_slugs": ["agents"]},
        {"title": "The Future of Latent Space Critique", "url": "https://latent.space/p/future", "publisher": "latent.space", "score": 6.10, "tier": "Contrarian", "category_slugs": ["research"]},
    ]

    selected, notice, rationale = select_edition_lineup_algorithmic(candidates, min_stories=5, max_stories=7)

    # Verify story count
    assert 5 <= len(selected) <= 7

    # Verify only ONE AWS story was selected (highest scoring one: SkyRL)
    aws_selected = [s for s in selected if extract_source_entity(s) == "amazon"]
    assert len(aws_selected) == 1
    assert aws_selected[0]["title"] == "SkyRL on SageMaker HyperPod"

    # Verify rejected AWS stories have informative audit reason
    narrate_cand = next(c for c in candidates if "NarrateAI" in c["title"])
    assert narrate_cand["selected"] is False
    assert "Source diversity limit reached for entity 'amazon'" in narrate_cand["rejected_reason"]

    # Verify selected stories come from diverse entities
    entities = [extract_source_entity(s) for s in selected]
    assert len(entities) == len(set(entities))  # all unique entities
    assert "qwen" in entities
    assert "nvidia" in entities
    assert "mistral" in entities
    assert "openai" in entities
    assert "latent.space" in entities

def test_selection_agent_off_the_hook_exception():
    """Verify that a second story from the same source is only allowed if score >= 8.5."""
    candidates = [
        {"title": "OpenAI Breakthrough: GPT-5 Architecture", "url": "https://openai.com/gpt5", "publisher": "openai.com", "score": 9.20, "tier": "Core", "category_slugs": ["ai-models"]},
        {"title": "OpenAI Scaling Law Empirical Proof", "url": "https://openai.com/scaling", "publisher": "openai.com", "score": 8.70, "tier": "Exploratory", "category_slugs": ["research"]},
        {"title": "OpenAI Minor SDK Bugfix", "url": "https://openai.com/sdk-patch", "publisher": "openai.com", "score": 6.00, "tier": "Core", "category_slugs": ["developer-tools"]},
        {"title": "Google DeepMind Protein Model", "url": "https://deepmind.google/alphafold", "publisher": "deepmind.google", "score": 7.50, "tier": "Core", "category_slugs": ["science-ai"]},
        {"title": "NVIDIA Blackwell B200 Systems", "url": "https://blogs.nvidia.com/b200", "publisher": "blogs.nvidia.com", "score": 7.40, "tier": "Core", "category_slugs": ["hardware"]},
        {"title": "Contrarian LLM Reasoning Limits", "url": "https://arxiv.org/abs/reasoning", "publisher": "arXiv", "score": 7.00, "tier": "Contrarian", "category_slugs": ["research"]},
    ]

    selected, notice, rationale = select_edition_lineup_algorithmic(candidates, min_stories=5, max_stories=7, off_the_hook_threshold=8.5)

    openai_stories = [s for s in selected if extract_source_entity(s) == "openai"]
    # 2 stories allowed because 8.70 >= 8.5, but the 3rd (6.00) is rejected
    assert len(openai_stories) == 2
    assert not any(s["title"] == "OpenAI Minor SDK Bugfix" for s in selected)

    # Verify the two OpenAI stories are NOT placed consecutively
    openai_indices = [i for i, s in enumerate(selected) if extract_source_entity(s) == "openai"]
    assert abs(openai_indices[0] - openai_indices[1]) > 1


# =========================================================================
# Writing Agent Newspaper Styling & Self-Review Tests
# =========================================================================

from agents.app.agents import (
    clean_source_text,
    clean_sentence_closure,
    format_newspaper_headline,
    audit_story_draft,
    sanitize_story_completeness,
    synthesize_newspaper_article_algorithmic,
    synthesize_story,
)

def test_writing_agent_clean_source_text():
    """Verify that clean_source_text strips navigation headers and promotional CTAs."""
    raw = (
        "GITHUB HUGGING FACE MODELSCOPE DEMO DISCORD\n"
        "We are thrilled to release Qwen-Image, a 20B MMDiT image foundation model. "
        "To try the latest model, feel free to visit Qwen Chat and choose “Image Generation”. "
        "The key features include high fidelity text rendering."
    )
    cleaned = clean_source_text(raw)
    assert "GITHUB" not in cleaned
    assert "HUGGING FACE" not in cleaned
    assert "MODELSCOPE" not in cleaned
    assert "DISCORD" not in cleaned
    assert "feel free to visit" not in cleaned
    assert "The engineering team has released Qwen-Image" in cleaned
    assert "20B MMDiT" in cleaned

def test_writing_agent_clean_sentence_closure_eliminates_ellipses():
    """Verify that trailing ellipses and severed fragments are strictly eliminated."""
    # Test case 1: Raw truncated sentence ending in ...
    truncated = "We released Qwen-Image. The key features include: Superior Text Rendering: Qwen-Ima..."
    closed = clean_sentence_closure(truncated)
    assert not closed.endswith("...")
    assert not closed.endswith("…")
    assert "Qwen-Ima..." not in closed  # severed fragment removed
    assert "Superior Text Rendering" not in closed
    assert closed.endswith(".")
    assert closed == "We released Qwen-Image."

    # Test case 2: Unbalanced open parenthesis at snippet end
    paren_trunc = "The model supports both alphabetic languages (e."
    closed_paren = clean_sentence_closure(paren_trunc)
    assert not closed_paren.endswith("...")
    assert "(" not in closed_paren
    assert closed_paren.endswith(".")

def test_writing_agent_format_newspaper_headline():
    """Verify newspaper headline formatting."""
    assert format_newspaper_headline("Crafting with Native Text Rendering", "qwenlm.github.io") == "QwenLM: Crafting with Native Text Rendering"
    assert format_newspaper_headline("[AINews] The Future of Latent Space", "latent.space") == "The Future of Latent Space"
    assert format_newspaper_headline("SkyRL on SageMaker HyperPod", "aws.amazon.com") == "AWS: SkyRL on SageMaker HyperPod"

def test_writing_agent_self_review_audit_detects_flaws():
    """Verify that self-review audit detects incomplete sentences, ellipses, and nav debris."""
    flawed_draft = {
        "headline": "Short...",
        "summary": "GITHUB HUGGING FACE MODELSCOPE DEMO DISCORD We released Qwen-Image...",
        "why_it_matters": "Incomplete thought...",
        "body": "Too short body stub.",
    }
    flaws = audit_story_draft(flawed_draft)
    assert any("ellipses" in f.lower() for f in flaws)
    assert any("navigation debris" in f.lower() for f in flaws)
    assert any("too short" in f.lower() for f in flaws)

def test_writing_agent_sanitizer_guarantees_completeness():
    """Verify that sanitize_story_completeness deterministically repairs flaws."""
    flawed_draft = {
        "title": "Qwen-Image: Native Text Rendering",
        "summary": "GITHUB HUGGING FACE MODELSCOPE DEMO DISCORD We are thrilled to release Qwen-Image, a 20B MMDiT image foundation model that achieves significant advances in complex text rendering and precise image editing. The key features include: Superior Text Rendering: Qwen-Ima...",
        "why_it_matters": "This development alters architectural efficiency baselines for production vision workflows...",
        "body": "### Architectural Overview\n\nQwen-Image achieves significant advances in complex text rendering...",
        "category_slugs": ["ai-models"],
    }
    candidate = {"publisher": "qwenlm.github.io"}
    repaired = sanitize_story_completeness(flawed_draft, candidate=candidate)

    # Assertions
    assert not repaired["summary"].endswith("...")
    assert not repaired["summary"].endswith("…")
    assert not repaired["why_it_matters"].endswith("...")
    assert not repaired["body"].endswith("...")
    assert "GITHUB" not in repaired["summary"]
    assert "HUGGING FACE" not in repaired["summary"]
    assert "Qwen-Ima." not in repaired["summary"]  # No severed word
    assert repaired["summary"].endswith((".", "!", "?"))
    assert repaired["why_it_matters"].endswith((".", "!", "?"))
    assert repaired["body"].endswith((".", "!", "?"))
    assert len(repaired["summary"]) >= 150
    assert len(repaired["why_it_matters"]) >= 50
    assert len(repaired["body"]) >= 350

@pytest.mark.asyncio
async def test_writing_agent_qwen_image_example():
    """Directly test the user's reported Qwen-Image case end-to-end."""
    qwen_candidate = {
        "title": "Qwen-Image: Crafting with Native Text Rendering",
        "publisher": "qwenlm.github.io",
        "url": "https://qwenlm.github.io/blog/qwen-image",
        "summary": (
            "GITHUB HUGGING FACE MODELSCOPE DEMO DISCORD "
            "We are thrilled to release Qwen-Image, a 20B MMDiT image foundation model "
            "that achieves significant advances in complex text rendering and precise image editing. "
            "To try the latest model, feel free to visit Qwen Chat and choose “Image Generation”. "
            "The key features include: Superior Text Rendering: Qwen-Ima..."
        ),
        "category_slugs": ["ai-models"],
    }

    # Synthesize in deterministic/offline mode first
    story = await synthesize_story(qwen_candidate, idx=0, live=False)

    # 1. Headline must be declarative newspaper headline
    assert "Qwen" in story["headline"] or "Qwen" in story["title"]
    assert not story["headline"].endswith("...")

    # 2. Summary must be a multi-paragraph newspaper article
    summary = story["summary"]
    assert not summary.endswith("...")
    assert not summary.endswith("…")
    assert "GITHUB" not in summary
    assert "HUGGING FACE" not in summary
    assert "DISCORD" not in summary
    assert "feel free to visit" not in summary
    assert "Qwen-Ima..." not in summary
    assert "Qwen-Image" in summary
    assert "20B MMDiT" in summary
    assert len(summary) >= 200
    assert summary.endswith((".", "!", "?"))

    # 3. Why It Matters must be complete and relevant
    why = story["why_it_matters"]
    assert not why.endswith("...")
    assert len(why) >= 60
    assert why.endswith((".", "!", "?"))

    # 4. Body must have structured deep-dive sections
    body = story["body"]
    assert not body.endswith("...")
    assert "### Architectural & Benchmark Analysis" in body
    assert "### Compute Economics & Scaling" in body
    assert "### Enterprise Integration Takeaways" in body
    assert len(body) >= 400


def test_clean_markdown_headings_from_prose():
    from agents.app.agents import clean_markdown_headings_from_prose

    sample = (
        "### Architectural & Benchmark Analysis It’s been an absolutely MONSTER week already, "
        "from new Chinese Open Weight Frontier Lab claiming the throne for the first time. "
        "The underlying framework optimizes matrix multiplication kernels and memory access patterns. "
        "### Compute Economics & Scaling For practitioners deploying systems in the latent.space ecosystem, "
        "this development alters architectural efficiency baselines and latency budgets."
    )

    cleaned = clean_markdown_headings_from_prose(sample)
    assert "#" not in cleaned
    assert "Architectural & Benchmark Analysis" not in cleaned
    assert "Compute Economics & Scaling" not in cleaned
    assert "It’s been an absolutely MONSTER week" in cleaned
    assert "For practitioners deploying systems in the latent.space ecosystem" in cleaned


def test_format_body_markdown_ensures_proper_heading_newlines():
    from agents.app.agents import format_body_markdown

    raw_body = (
        "### Architectural & Benchmark Analysis\n\n"
        "The underlying framework optimizes matrix multiplication kernels and memory access patterns. "
        "### Compute Economics & Scaling For practitioners deploying systems in the latent.space ecosystem, "
        "this development alters architectural efficiency baselines."
    )

    formatted = format_body_markdown(raw_body)
    assert "\n\n### Compute Economics & Scaling\n\n" in formatted
    assert "memory access patterns.\n\n### Compute Economics & Scaling\n\nFor practitioners" in formatted


def test_sanitize_story_removes_markdown_from_summary_and_why():
    from agents.app.agents import sanitize_story_completeness

    draft = {
        "headline": "Latent Space: Scaled Reasoning Baselines",
        "title": "Latent Space: Scaled Reasoning Baselines",
        "summary": "### Architectural & Benchmark Analysis Researchers have released new open weights for production. ### Compute Economics & Scaling The model achieves 2.4x throughput improvements.",
        "why_it_matters": "### Why It Matters This alters inference latency baselines for enterprise architectures.",
        "body": "### Architectural & Benchmark Analysis\n\nThroughput scales linearly. ### Compute Economics & Scaling Cost per token drops 40%.",
        "category_slugs": ["ai-models"],
    }

    sanitized = sanitize_story_completeness(draft)
    assert "#" not in sanitized["summary"]
    assert "#" not in sanitized["why_it_matters"]
    assert "### Architectural & Benchmark Analysis" not in sanitized["summary"]
    assert "### Compute Economics & Scaling" not in sanitized["summary"]
    assert "\n\n### Compute Economics & Scaling\n\n" in sanitized["body"]
