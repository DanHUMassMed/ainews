import os
import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

DEFAULT_COMMON_ENTITIES = [
    "OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "NVIDIA", "Apple",
    "DeepSeek", "Mistral", "Cohere", "Amazon", "AMD", "Intel", "Hugging Face",
    "xAI", "Cerebras", "Groq", "TSMC", "Alibaba", "Tencent", "Baidu"
]

DEFAULT_CATEGORY_KEYWORDS = {
    "hardware": [
        "blackwell", "gpu", "tpu", "npu", "wafer", "silicon",
        "chips", "accelerator", "cerebras", "nvidia", "amd",
        "semiconductor", "h100", "b200", "gb200", "asic", "hbm"
    ],
    "agents": [
        "agent", "autonomous", "tool use", "mcp", "agentic", "runtime",
        "harness", "workflow", "browser agent", "multi-agent", "code agent"
    ],
    "ai-models": [
        "model", "weights", "llm", "parameters", "qwen", "deepseek",
        "mistral", "llama", "claude", "gpt", "checkpoint", "vision", "open weight", "gemini"
    ],
    "open-source": [
        "open source", "open-source", "open weight", "open-weight", "open weights",
        "weights released", "apache 2.0", "mit license", "hugging face", "huggingface", "github"
    ],
    "research": [
        "paper", "arxiv", "benchmark", "reasoning", "attention",
        "transformer", "architecture", "theorem", "sparse attention", "pre-training", "interpretability"
    ],
    "developer-tools": [
        "sdk", "library", "framework", "pytorch", "vllm",
        "tensorrt", "triton", "ollama", "huggingface", "developer", "api", "ide"
    ],
    "robotics": [
        "robot", "humanoid", "embodied", "actuator", "vla", "manipulation", "boston dynamics", "figure"
    ],
    "regulation": [
        "regulation", "policy", "copyright", "ftc", "legal", "eu ai act",
        "safety institute", "compliance", "antitrust", "legislation", "governance"
    ],
    "science-ai": [
        "science", "scientific", "biology", "protein", "alphafold", "chemistry",
        "materials", "genomics", "clinical", "biotech"
    ],
    "ai-business": [
        "valuation", "funding", "seed round", "series a", "series b", "series c",
        "venture", "acquisition", "market cap", "ipo"
    ],
    "enterprise-ai": [
        "enterprise", "sovereign", "deployment", "customer", "forward deployed", "enterprise ai"
    ],
    "infrastructure": [
        "infrastructure", "serving", "inference engine", "latency", "throughput", "cluster networking", "kv-cache"
    ]
}


def _find_taxonomy_file() -> Path | None:
    env_path = os.getenv("AINEWS_TAXONOMY_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    candidates = [
        Path("config/taxonomy.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "config" / "taxonomy.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def load_taxonomy() -> dict:
    tax_path = _find_taxonomy_file()
    if tax_path:
        try:
            with open(tax_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Failed to load taxonomy from %s, using defaults: %s", tax_path, e)
    return {}


def get_common_entities() -> List[str]:
    data = load_taxonomy()
    return data.get("common_entities", DEFAULT_COMMON_ENTITIES)


def get_category_keywords() -> Dict[str, List[str]]:
    data = load_taxonomy()
    return data.get("category_keywords", DEFAULT_CATEGORY_KEYWORDS)
