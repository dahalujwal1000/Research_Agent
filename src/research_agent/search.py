"""Tavily search client: query -> list of {title, url, snippet}."""
from __future__ import annotations

import requests

from . import config

TAVILY_URL = "https://api.tavily.com/search"


def search(query: str, max_results: int = 5) -> list[dict]:
    """Search via Tavily and return normalized results."""
    if not config.TAVILY_API_KEY:
        raise RuntimeError("Missing Tavily key. Set TAVILY_API_KEY in .env")

    resp = requests.post(
        TAVILY_URL,
        json={
            "api_key": config.TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
        },
        timeout=config.REQUEST_TIMEOUT_SECS,
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("results", []):
        url = (item.get("url") or "").strip()
        if not url:
            continue
        results.append(
            {
                "title": (item.get("title") or url).strip(),
                "url": url,
                "snippet": (item.get("content") or item.get("snippet") or "").strip(),
            }
        )
    return results
