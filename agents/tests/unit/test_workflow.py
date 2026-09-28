"""Unit and integration tests for ADK Root Editorial Workflow."""

import pytest
from unittest.mock import patch, AsyncMock
from agents.app.workflows.root_workflow import EditorialWorkflow, WorkflowResult

SAMPLE_TEST_CANDIDATES = [
    {
        "title": "vLLM Project Merges Speculative Chunked Prefill Scheduler",
        "url": "https://huggingface.co/blog",
        "summary": "Scheduler redesign yields 4x throughput boost on long reasoning traces.",
        "why_it_matters": "Cuts time-to-first-token latency for chain-of-thought models in production.",
        "category_slugs": ["developer-tools"],
        "publisher": "Hugging Face",
        "published_at": "2099-01-01T10:00:00Z",
        "significance": 9.5,
        "novelty": 9.0,
        "evidence": 9.5,
        "saturation": 2.0,
        "is_lead": True,
    },
    {
        "title": "PyTorch Foundation Merges Async Pipeline Parallelism with Native FP8 Kernel Compilation",
        "url": "https://pytorch.org/blog/",
        "summary": "Master branch enters production with 15 percent performance uplift on clusters.",
        "why_it_matters": "Relieves power density constraints for 2027 AI datacenter silicon.",
        "category_slugs": ["hardware"],
        "publisher": "PyTorch Foundation",
        "published_at": "2099-01-01T11:00:00Z",
        "significance": 9.0,
        "novelty": 8.5,
        "evidence": 9.0,
        "saturation": 3.0,
        "is_lead": False,
    },
    {
        "title": "ArXiv Research Formalizes Spatial and Robotic Verification Scaling Laws",
        "url": "https://arxiv.org/abs/2408.03314",
        "summary": "Empirical evaluations confirm test-time reasoning compute scaling on complex benchmarks.",
        "why_it_matters": "Cuts time-to-first-token latency for chain-of-thought models in production.",
        "category_slugs": ["ai-models"],
        "publisher": "arXiv",
        "published_at": "2099-01-01T12:00:00Z",
        "significance": 8.8,
        "novelty": 8.2,
        "evidence": 8.5,
        "saturation": 2.5,
        "is_lead": False,
    },
    {
        "title": "NVIDIA Developer Profiles Sub-Millisecond Group-Query Attention Kernels",
        "url": "https://developer.nvidia.com/blog/",
        "summary": "Enables local multi-accelerator model sharding across mixed desktop devices.",
        "why_it_matters": "Enables secure on-premise execution for privacy-sensitive enterprises.",
        "category_slugs": ["developer-tools"],
        "publisher": "NVIDIA Developer",
        "published_at": "2099-01-01T13:00:00Z",
        "significance": 8.2,
        "novelty": 8.0,
        "evidence": 8.0,
        "saturation": 3.0,
        "is_lead": False,
    },
    {
        "title": "Triton Compiler Adds Automated Memory Tiling for Custom Silicon Backends",
        "url": "https://github.com/triton-lang/triton",
        "summary": "Wafer-scale engine delivers sub-second medical model diagnostics.",
        "why_it_matters": "Unlocks real-time interactive verification at memory-bandwidth saturation speeds.",
        "category_slugs": ["hardware"],
        "publisher": "Triton",
        "published_at": "2099-01-01T14:00:00Z",
        "significance": 8.5,
        "novelty": 8.1,
        "evidence": 8.5,
        "saturation": 2.0,
        "is_lead": False,
    }
]

@pytest.mark.asyncio
async def test_workflow_end_to_end_staging():
    """Verify complete workflow execution from discovery to draft staging."""
    workflow = EditorialWorkflow(live=False)
    result = await workflow.run(
        target_date="2099-01-01",
        publish=False,
        sample_candidates=SAMPLE_TEST_CANDIDATES
    )

    assert result.status == "staged_draft"
    assert result.story_count == 5
    assert result.candidate_count == 5

    # Cleanup test edition from DB
    from backend.app.core.database import AsyncSessionLocal
    from backend.app.models.story import Story
    from backend.app.models.edition import Edition
    from sqlalchemy import delete
    import uuid as uuid_pkg
    if result.edition_id:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(Story).where(Story.edition_id == uuid_pkg.UUID(result.edition_id)))
            await session.execute(delete(Edition).where(Edition.id == uuid_pkg.UUID(result.edition_id)))
            await session.commit()
    assert result.critic_passed is True
    assert result.edition_id is not None
    assert result.staged_draft is not None

@pytest.mark.asyncio
async def test_workflow_low_signal_day_handling():
    """Verify workflow activates low_signal_notice when fewer than 5 candidates meet threshold."""
    low_signal_candidates = SAMPLE_TEST_CANDIDATES[:2]
    workflow = EditorialWorkflow(live=False)
    result = await workflow.run(
        target_date="2099-01-01",
        publish=False,
        sample_candidates=low_signal_candidates
    )

    assert result.status == "staged_draft"
    assert result.story_count == 2
    assert result.low_signal is True
    assert result.low_signal_notice is not None
    assert "low-signal" in result.low_signal_notice.lower()
    assert result.critic_passed is True

@pytest.mark.asyncio
async def test_workflow_critic_revision_loop_buzzwords():
    """Verify Critic revision loop detects prohibited buzzwords and self-corrects."""
    buzzword_candidates = [
        {
            "title": "Company Unleashes Revolutionary Groundbreaking Mind-Blowing AI Chip",
            "url": "https://deepmind.google/research/breakthroughs/",
            "summary": "A revolutionary architecture that will unleash game-changer capabilities.",
            "why_it_matters": "", # empty why_it_matters to trigger revision
            "category_slugs": ["infrastructure"],
            "publisher": "Buzz Corp",
            "published_at": "2099-01-01T10:00:00Z",
            "significance": 8.5,
            "novelty": 8.0,
            "evidence": 8.0,
            "saturation": 2.0,
            "is_lead": True,
        }
    ] + SAMPLE_TEST_CANDIDATES[:4]

    workflow = EditorialWorkflow(live=False, max_revisions=2)
    result = await workflow.run(
        target_date="2099-01-01",
        publish=False,
        sample_candidates=buzzword_candidates
    )

    assert result.status == "staged_draft"
    assert result.critic_passed is True
    assert result.revisions_performed >= 1

    # Verify buzzwords were replaced
    staged_stories = result.staged_draft.get("stories", [])
    for story in staged_stories:
        title_lower = story["title"].lower()
        summary_lower = story["summary"].lower()
        assert "game-changer" not in title_lower and "game-changer" not in summary_lower
        assert "revolutionary" not in title_lower and "revolutionary" not in summary_lower
        assert "groundbreaking" not in title_lower and "groundbreaking" not in summary_lower


@pytest.mark.asyncio
async def test_workflow_stale_backup_recovery_on_low_signal():
    """Verify workflow recovers high-value stale (>48h) opportunities to fill edition to 5 stories on low-signal days."""
    # 2 fresh candidates within lookback
    fresh_candidates = [
        {
            "title": "Fresh Frontier Model Scaling Report Released Today",
            "url": "https://huggingface.co/blog",
            "summary": "Engineering teams confirm benchmark accuracy gains on reasoning benchmarks.",
            "why_it_matters": "Changes latency budgets for enterprise reasoning models in production.",
            "category_slugs": ["ai-models"],
            "publisher": "Hugging Face",
            "published_at": "2099-01-01T10:00:00Z",
            "significance": 9.5,
            "novelty": 9.0,
            "evidence": 9.5,
            "saturation": 2.0,
            "is_lead": True,
        },
        {
            "title": "Async Inference Engine Lowers GPU Memory Footprint Native FP8",
            "url": "https://pytorch.org/blog/",
            "summary": "Master branch enters production with 20 percent performance uplift on clusters.",
            "why_it_matters": "Enables cost-effective hardware utilization across distributed reasoning nodes.",
            "category_slugs": ["hardware"],
            "publisher": "PyTorch Foundation",
            "published_at": "2099-01-01T11:00:00Z",
            "significance": 9.0,
            "novelty": 8.5,
            "evidence": 9.0,
            "saturation": 2.5,
            "is_lead": False,
        }
    ]

    # 4 stale candidates older than 48 hours with high value
    stale_candidates = [
        {
            "title": f"High-Value Technical Deep Dive #{idx + 1}: Memory Kernels Optimization",
            "url": f"https://arxiv.org/abs/2408.0{idx + 100}",
            "summary": "Detailed empirical evaluations confirm memory bandwidth saturation retention.",
            "why_it_matters": "Provides architectural foundation for low-latency production pipelines.",
            "category_slugs": ["developer-tools"],
            "publisher": "arXiv",
            "published_at": "2098-12-15T12:00:00Z", # > 48h older than 2099-01-01
            "significance": 8.8,
            "novelty": 8.0,
            "evidence": 8.5,
            "saturation": 2.0,
            "is_lead": False,
        }
        for idx in range(4)
    ]

    combined_candidates = fresh_candidates + stale_candidates
    workflow = EditorialWorkflow(live=False)
    result = await workflow.run(
        target_date="2099-01-01",
        publish=False,
        sample_candidates=combined_candidates
    )

    assert result.status == "staged_draft"
    # Should have recovered 3 stale opportunities to reach exactly 5 stories
    assert result.story_count == 5
    assert result.critic_passed is True

    assert result.story_count == 5
    assert result.candidate_count >= 5


def test_infer_story_categories():
    from agents.app.workflows.root_workflow import infer_story_categories

    # Hardware keywords
    cats_hw = infer_story_categories("NVIDIA Blackwell GPU Cluster Deployed with Liquid Cooling")
    assert "hardware" in cats_hw

    # Agent keywords
    cats_agent = infer_story_categories("New Autonomous Agent Protocol and Runtime Harness Released")
    assert "agents" in cats_agent

    # Open Source keywords
    cats_os = infer_story_categories("Mistral releases open-weight model with Apache 2.0 license on Hugging Face")
    assert "open-source" in cats_os

    # Research keywords
    cats_res = infer_story_categories("Sparse Attention Transformer Architecture Benchmark Paper on arXiv")
    assert "research" in cats_res

    # Enterprise AI keywords
    cats_ent = infer_story_categories("Enterprise Sovereign Deployment and 3 Billion Funding Round")
    assert "enterprise-ai" in cats_ent


def test_resolve_candidate_feedback_bias_like_stories():
    from agents.app.workflows.root_workflow import resolve_candidate_feedback_bias

    # Simulated feedback profile from previous published stories
    feedback_analytics = {
        "cold_start_active": False,
        "categories": [
            {
                "category_name": "Hardware",
                "slug": "hardware",
                "upvotes": 17,
                "downvotes": 3,
                "approval_rate": 0.85, # 85% approval
            },
            {
                "category_name": "Enterprise AI",
                "slug": "enterprise-ai",
                "upvotes": 2,
                "downvotes": 8,
                "approval_rate": 0.20, # 20% approval
            },
            {
                "category_name": "Robotics",
                "slug": "robotics",
                "upvotes": 1,
                "downvotes": 0,
                "approval_rate": 1.0, # only 1 vote (< 3 minimum quorum)
            }
        ],
        "top_positive_topics": ["hardware"],
        "top_negative_topics": ["enterprise-ai"],
    }

    # Candidate A: Hardware story (should receive +2.10 boost)
    cand_hw = {
        "title": "Cerebras Wafer-Scale AI Accelerator Benchmark",
        "category_slugs": ["hardware"],
    }
    bias_hw = resolve_candidate_feedback_bias(cand_hw, feedback_analytics)
    assert bias_hw == 2.1 # 6.0 * (0.85 - 0.50) = 2.1

    # Candidate B: Enterprise story (should receive -1.80 penalty)
    cand_ent = {
        "title": "Corporate Venture Acquisition Round",
        "category_slugs": ["enterprise-ai"],
    }
    bias_ent = resolve_candidate_feedback_bias(cand_ent, feedback_analytics)
    assert bias_ent == -1.8 # 6.0 * (0.20 - 0.50) = -1.8

    # Candidate C: Robotics story with only 1 total vote (< 3 minimum quorum) -> should be neutral 0.0
    cand_rob = {
        "title": "Humanoid Actuator Sensor Suite",
        "category_slugs": ["robotics"],
    }
    bias_rob = resolve_candidate_feedback_bias(cand_rob, feedback_analytics)
    assert bias_rob == 0.0

    # Candidate D: Unknown topic with no feedback -> should be neutral 0.0
    cand_unknown = {
        "title": "Random Topic Without Feedback History",
        "category_slugs": ["misc"],
    }
    bias_unknown = resolve_candidate_feedback_bias(cand_unknown, feedback_analytics)
    assert bias_unknown == 0.0

def test_resolve_candidate_feedback_bias_with_editorial_override():
    from agents.app.workflows.root_workflow import resolve_candidate_feedback_bias

    # Feedback analytics where Enterprise AI is downvoted by readers, but overridden by editor
    feedback_analytics = {
        "cold_start_active": False,
        "categories": [
            {
                "category_name": "Enterprise AI",
                "slug": "enterprise-ai",
                "upvotes": 1,
                "downvotes": 9,
                "approval_rate": 0.10,
                "override_active": True,
                "override_bias": 1.25,
            },
            {
                "category_name": "Hardware",
                "slug": "hardware",
                "upvotes": 18,
                "downvotes": 2,
                "approval_rate": 0.90,
                "override_active": False,
                "override_bias": None,
            },
        ],
        "category_overrides": {
            "robotics": {
                "manual_bias": 2.0,
                "active": True,
                "reason": "Prioritize robotics breakthrough",
            }
        },
    }

    # Candidate 1: Enterprise AI should use editorial override +1.25 instead of reader downvotes (-2.4)
    cand_ent = {"title": "Enterprise Cloud Deployment", "category_slugs": ["enterprise-ai"]}
    assert resolve_candidate_feedback_bias(cand_ent, feedback_analytics) == 1.25

    # Candidate 2: Robotics should use top-level override +2.0
    cand_rob = {"title": "New Bipedal Robot", "category_slugs": ["robotics"]}
    assert resolve_candidate_feedback_bias(cand_rob, feedback_analytics) == 2.0

    # Candidate 3: Hardware has no override, should use reader votes: 6.0 * (0.90 - 0.50) = 2.4
    cand_hw = {"title": "Next Gen TPU", "category_slugs": ["hardware"]}
    assert resolve_candidate_feedback_bias(cand_hw, feedback_analytics) == 2.4
