"""OpenRouter LLM client with per-stage models + fallback chains.

Stage routing (all free):
- Query generation -> reasoning model (good search angles benefit from thought)
- Per-source summarization -> fast non-reasoning model (clean extraction)
- Final report -> strong long-form writer (markdown structure, large context)
"""
from __future__ import annotations

import requests

from . import config


def _call_model(model: str, messages: list[dict], max_tokens: int = 1500) -> str:
    resp = requests.post(
        config.OPENROUTER_BASE_URL,
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "AI Research Agent v1",
        },
        json={
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        },
        timeout=120,  # reasoning models (nemotron) can be slow: ~7 tok/s
    )
    if resp.status_code in (400, 401, 402, 404, 429):
        raise RuntimeError(f"{resp.status_code}: {resp.text[:300]}")
    resp.raise_for_status()
    data = resp.json()
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"bad response shape: {str(data)[:300]}")
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    # openrouter/free sometimes routes to reasoning-only models that put
    # output in `reasoning` with empty `content` -> fall through to next model
    reasoning = message.get("reasoning") or ""
    if isinstance(reasoning, str) and len(reasoning.strip()) > 50:
        return reasoning.strip()
    raise RuntimeError(f"empty content from {model}: {str(data)[:300]}")


def _chat_with(models: list[str], messages: list[dict], max_tokens: int = 1500) -> tuple[str, str]:
    """Try given models in order. Returns (text, model_used)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for m in models:
        if m and m not in seen:
            seen.add(m)
            ordered.append(m)

    last_error = ""
    for model in ordered:
        try:
            print(f"  [llm] trying {model} ...")
            return _call_model(model, messages, max_tokens), model
        except Exception as exc:
            last_error = str(exc)
            print(f"  [llm] {model} failed: {last_error[:150]}")
            continue
    raise RuntimeError(f"All OpenRouter models failed. Last error: {last_error}")


def chat(messages: list[dict], max_tokens: int = 1500) -> tuple[str, str]:
    """Generic chat using the global fallback chain (backwards compat)."""
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("Missing OpenRouter key. Set OPENROUTER_API_KEY in .env")
    return _chat_with(list(config.OPENROUTER_FALLBACK_MODELS), messages, max_tokens)


def generate_queries(topic: str, n: int = 3) -> list[str]:
    """Topic -> n diverse search queries (reasoning model for better angles)."""
    messages = [
        {
            "role": "system",
            "content": "You generate short, diverse web search queries for research. Reply with one query per line, no numbering, no quotes.",
        },
        {
            "role": "user",
            "content": f"Generate {n} diverse search queries to research this topic thoroughly:\n{topic}",
        },
    ]
    text, _ = _chat_with(list(config.QUERY_FALLBACKS), messages, max_tokens=600)
    queries = [q.strip().lstrip("1234567890.-) ").strip('"') for q in text.splitlines()]
    queries = [q for q in queries if q]
    return queries[:n] if queries else [topic]


def summarize_source(topic: str, title: str, url: str, text: str) -> str:
    """Condense one crawled page into key points (fast extraction model)."""
    messages = [
        {
            "role": "system",
            "content": "You summarize web pages for a research report. Keep only facts relevant to the topic. 5-8 bullets max.",
        },
        {
            "role": "user",
            "content": f"Topic: {topic}\nSource: {title} ({url})\n\nContent:\n{text}\n\nSummarize into bullets relevant to the topic.",
        },
    ]
    summary, _ = _chat_with(list(config.SUMMARY_FALLBACKS), messages, max_tokens=800)
    return summary


def build_report(topic: str, summaries: list[dict]) -> tuple[str, str]:
    """Merge per-source summaries into executive report (long-form writer)."""
    joined = "\n\n".join(
        f"### {s['title']}\nURL: {s['url']}\n{s['summary']}" for s in summaries
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You write concise research reports. Structure: "
                "# <topic> Research Report, ## Executive Summary (5-6 lines), "
                "## Key Findings (grouped bullets), ## Details by sub-topic, "
                "## Sources (title + URL list). Dedupe repeated facts. "
                "Cite inline like [Source Title](URL) where relevant."
            ),
        },
        {
            "role": "user",
            "content": f"Topic: {topic}\n\nSource summaries:\n{joined}\n\nWrite the final report in markdown.",
        },
    ]
    return _chat_with(list(config.REPORT_FALLBACKS), messages, max_tokens=4000)
