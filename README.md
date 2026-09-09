# Research_Agent

AI Research Agent — topic in, structured markdown report out.

## Pipeline
```
Topic → LLM generates 3 queries → Tavily search (5 URLs each)
→ requests + trafilatura crawl → per-source LLM summary → final report
```

## Setup
```powershell
pip install -r requirements.txt
copy .env.example .env   # then fill OPENROUTER_API_KEY + TAVILY_API_KEY
```

## Usage
```powershell
python main.py "benefits of drinking green tea"
# report saved to reports/<topic>-<timestamp>.md
```

## Global install (call from anywhere)
```powershell
pip install -e .
research-agent "benefits of drinking green tea"
```
This creates a `research-agent` command on PATH. Reports still save to the
project's `reports/` folder, and API keys are always read from the project's
`.env` no matter which folder you run from.

## Files
- `main.py` — CLI (thin, imports `agent.run` so API/UI can reuse later)
- `agent.py` — orchestrator
- `config.py` — env keys + tunables
- `search.py` — Tavily client
- `crawler.py` — requests + trafilatura
- `llm.py` — OpenRouter client with per-stage free models:
  - queries → `nvidia/nemotron-3-ultra-550b-a55b:free` (reasoning)
  - summaries → `google/gemma-4-31b-it:free` (fast extraction)
  - report → `thinkingmachines/inkling:free` (long-form writing)
  - NOTE: `qwen/qwen3-next-80b-a3b-instruct:free` was removed — OpenRouter
    retired its free variant (404: paid-only). Override per stage via
    `QUERY_MODEL` / `SUMMARY_MODEL` / `REPORT_MODEL` env vars.

Free stack: Tavily free tier + OpenRouter free models + local run.
