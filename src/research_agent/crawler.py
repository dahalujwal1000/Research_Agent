"""Crawler: fetch URL -> clean article text with requests + trafilatura."""
from __future__ import annotations

import requests
from trafilatura import extract

from . import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-agent-v1",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_text(url: str) -> str:
    """Return cleaned text for a URL, or '' on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT_SECS)
        resp.raise_for_status()
    except Exception as exc:  # network issues, 403s, timeouts
        print(f"  [skip] {url} ({exc})")
        return ""

    text = extract(resp.text, include_comments=False, include_tables=False) or ""
    text = text.strip()
    if len(text) > config.MAX_CHARS_PER_PAGE:
        text = text[: config.MAX_CHARS_PER_PAGE] + "\n...[truncated]"
    return text
