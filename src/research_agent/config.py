"""Central configuration for the AI research agent.

Reads API keys and tunables from environment variables / .env.
Supports both the user's existing lowercase keys and standard uppercase names.
"""
from __future__ import annotations

import os

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


def _get(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip().strip('"').strip("'")
    return default


OPENROUTER_API_KEY: str = _get("OPENROUTER_API_KEY", "openrouter_api_key")
TAVILY_API_KEY: str = _get("TAVILY_API_KEY", "Tavily-API-KEY", "TAVILY-API-KEY")

# Per-stage models: different jobs benefit from different models.
# Override any of these with env vars (QUERY_MODEL / SUMMARY_MODEL / REPORT_MODEL).
QUERY_MODEL: str = _get(
    "QUERY_MODEL", default="nvidia/nemotron-3-ultra-550b-a55b:free"
)
SUMMARY_MODEL: str = _get(
    "SUMMARY_MODEL", default="google/gemma-4-31b-it:free"
)
REPORT_MODEL: str = _get(
    "REPORT_MODEL", default="thinkingmachines/inkling:free"
)

# Kept for backwards compat (old .env / old code paths).
OPENROUTER_MODEL: str = _get("OPENROUTER_MODEL", default=QUERY_MODEL)

# Fallback chain per stage: preferred model first, then openrouter/free
# auto-router, then the other two stage models (a reasoning model can still
# summarize, just slower — better than crashing).
# poolside/laguna-s-2.1:free is fast (33 tok/s) + 99.8% availability, so it
# backs up the summarization + report stages (reliable "paid-grade" behavior).
OPENROUTER_FALLBACK_MODELS: tuple[str, ...] = (
    OPENROUTER_MODEL,
    "openrouter/free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "thinkingmachines/inkling:free",
    "thinkingmachines/inkling-small:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "liquid/lfm-2.5-2.6b:free",
)

QUERY_FALLBACKS: tuple[str, ...] = (
    QUERY_MODEL,
    "openrouter/free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "thinkingmachines/inkling:free",
    "poolside/laguna-s-2.1:free",
)

SUMMARY_FALLBACKS: tuple[str, ...] = (
    SUMMARY_MODEL,
    "openrouter/free",
    "google/gemma-4-26b-a4b-it:free",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "thinkingmachines/inkling-small:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
)

REPORT_FALLBACKS: tuple[str, ...] = (
    REPORT_MODEL,
    "openrouter/free",
    "poolside/laguna-s-2.1:free",
    "thinkingmachines/inkling:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# v1 pipeline tunables
NUM_QUERIES = int(_get("NUM_QUERIES", default="3") or 3)
RESULTS_PER_QUERY = int(_get("RESULTS_PER_QUERY", default="5") or 5)
MAX_CHARS_PER_PAGE = int(_get("MAX_CHARS_PER_PAGE", default="4000") or 4000)
REQUEST_TIMEOUT_SECS = int(_get("REQUEST_TIMEOUT_SECS", default="20") or 20)
