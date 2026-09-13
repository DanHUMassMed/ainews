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
