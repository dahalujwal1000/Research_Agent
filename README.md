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

## Files
- `main.py` — CLI (thin, imports `agent.run` so API/UI can reuse later)
- `agent.py` — orchestrator
- `config.py` — env keys + tunables
- `search.py` — Tavily client
- `crawler.py` — requests + trafilatura
- `llm.py` — OpenRouter client (default `openrouter/free` router + `:free` fallbacks)

Free stack: Tavily free tier + OpenRouter free models + local run.
