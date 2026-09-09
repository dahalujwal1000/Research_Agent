"""Central configuration for the AI research agent.

Reads API keys and tunables from environment variables / .env.
Supports both the user's existing lowercase keys and standard uppercase names.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _get(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip().strip('"').strip("'")
    return default


OPENROUTER_API_KEY: str = _get("OPENROUTER_API_KEY", "openrouter_api_key")
TAVILY_API_KEY: str = _get("TAVILY_API_KEY", "Tavily-API-KEY", "TAVILY-API-KEY")

# Free OpenRouter model. Override with OPENROUTER_MODEL env var.
# "openrouter/free" auto-routes to any available free model (recommended:
# free model IDs rotate often, hardcoded :free IDs die fast).
# Specific current :free IDs are kept as fallbacks.
OPENROUTER_MODEL: str = _get("OPENROUTER_MODEL", default="openrouter/free")

OPENROUTER_FALLBACK_MODELS: tuple[str, ...] = (
    OPENROUTER_MODEL,
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/free",
    "thinkingmachines/inkling:free",
    "thinkingmachines/inkling-small:free",
    "google/gemma-4-26b-a4b-it:free",
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "poolside/laguna-s-2.1:free",
    "liquid/lfm-2.5-2.6b:free",
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# v1 pipeline tunables
NUM_QUERIES = int(_get("NUM_QUERIES", default="3") or 3)
RESULTS_PER_QUERY = int(_get("RESULTS_PER_QUERY", default="5") or 5)
MAX_CHARS_PER_PAGE = int(_get("MAX_CHARS_PER_PAGE", default="4000") or 4000)
REQUEST_TIMEOUT_SECS = int(_get("REQUEST_TIMEOUT_SECS", default="20") or 20)
