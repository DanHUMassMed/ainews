"""Unit tests for Specialized Editorial Agents in Google ADK 2.x."""

import pytest
from agents.app.agents import (
    create_discovery_agent,
    create_research_agent,
    create_evaluation_agent,
    create_selection_agent,
    create_writing_agent,
    create_critic_agent,
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
    assert len(agent.tools) == 3
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
