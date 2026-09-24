"""ADK Agent Configuration and LiteLLM Model Resolution."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# OpenRouter & LiteLLM settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash-0731")

def normalize_model_name(model: Optional[str] = None) -> str:
    """Normalizes the model name for LiteLLM with OpenRouter.

    If the model string lacks a provider prefix (e.g., 'deepseek/deepseek-v4-flash-0731'),
    and an OpenRouter API key is set, ensures 'openrouter/' is prefixed.
    """
    target = (model or DEFAULT_LLM_MODEL).strip()
    if target.startswith("openrouter/"):
        return target
    # If it starts with another provider like 'gemini/' or 'openai/', keep it
    if "/" in target and not target.startswith("deepseek/") and not target.startswith("anthropic/") and not target.startswith("meta-llama/") and not target.startswith("google/"):
        return target
    # Default routing via OpenRouter
    return f"openrouter/{target}"

# Per-agent model configuration overrides
MODEL_REGISTRY = {
    "discovery": os.getenv("DISCOVERY_LLM_MODEL", DEFAULT_LLM_MODEL),
    "research": os.getenv("RESEARCH_LLM_MODEL", DEFAULT_LLM_MODEL),
    "evaluation": os.getenv("EVALUATION_LLM_MODEL", DEFAULT_LLM_MODEL),
    "selection": os.getenv("SELECTION_LLM_MODEL", DEFAULT_LLM_MODEL),
    "writing": os.getenv("WRITING_LLM_MODEL", DEFAULT_LLM_MODEL),
    "critic": os.getenv("CRITIC_LLM_MODEL", DEFAULT_LLM_MODEL),
}

def get_agent_model(role: str) -> str:
    """Retrieve normalized LiteLLM model identifier for a specific agent role."""
    raw_model = MODEL_REGISTRY.get(role.lower(), DEFAULT_LLM_MODEL)
    return normalize_model_name(raw_model)

# Host and Port Configuration
APP_HOST = os.getenv("APP_HOST", "192.168.1.101")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")

# Editorial MCP configuration
EDITORIAL_MCP_URL = os.getenv("EDITORIAL_MCP_URL", f"http://{APP_HOST}:{BACKEND_PORT}/api/editorial")
EDITORIAL_API_TOKEN = os.getenv("EDITORIAL_SECRET_KEY") or os.getenv("EDITORIAL_API_TOKEN", "secret-token-change-in-production")

# Search & Retrieval Services
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://127.0.0.1:8080")
FIRECRAWL_URL = os.getenv("FIRECRAWL_URL", "http://127.0.0.1:3002")
