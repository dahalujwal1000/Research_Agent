"""Orchestrator: topic -> queries -> search -> crawl -> summarize -> report."""
from __future__ import annotations

from . import config
from . import crawler
from . import llm
from . import search


def run(topic: str) -> dict:
    print(f"\n[1/5] Generating {config.NUM_QUERIES} queries for: {topic}")
    queries = llm.generate_queries(topic, n=config.NUM_QUERIES)
    for q in queries:
        print(f"  - {q}")

    print(f"\n[2/5] Searching Tavily ({config.RESULTS_PER_QUERY} per query)...")
    seen_urls: set[str] = set()
    hits: list[dict] = []
    for q in queries:
        for r in search.search(q, max_results=config.RESULTS_PER_QUERY):
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                hits.append(r)
    print(f"  Found {len(hits)} unique URLs")
    for h in hits:
        print(f"  - {h['title'][:80]} | {h['url'][:80]}")

    print("\n[3/5] Crawling + extracting text...")
    pages: list[dict] = []
    for h in hits:
        print(f"  fetching {h['url'][:90]}")
        text = crawler.fetch_text(h["url"])
        if text:
            pages.append({**h, "text": text})
            print(f"    ok ({len(text)} chars)")
    if not pages:
        raise RuntimeError("No pages could be crawled. Try another topic.")

    print(f"\n[4/5] Summarizing {len(pages)} sources with LLM...")
    summaries: list[dict] = []
    for p in pages:
        s = llm.summarize_source(topic, p["title"], p["url"], p["text"])
        summaries.append({"title": p["title"], "url": p["url"], "summary": s})
        print(f"  summarized: {p['title'][:70]}")

    print("\n[5/5] Building final report...")
    report, model_used = llm.build_report(topic, summaries)
    print(f"  done with model {model_used}")

    return {
        "topic": topic,
        "queries": queries,
        "sources": [{"title": p["title"], "url": p["url"]} for p in pages],
        "report": report,
        "model": model_used,
    }
