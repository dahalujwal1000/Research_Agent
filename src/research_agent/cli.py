"""CLI entry: research-agent "your topic" -> reports/<topic>.md

Kept thin so FastAPI/Streamlit can import research_agent.agent.run() later.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from . import agent  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def slugify(topic: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
    return slug[:60] or "report"


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Usage: research-agent "your research topic"')
        return 2
    topic = sys.argv[1].strip()

    result = agent.run(topic)

    out_dir = PROJECT_ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"{slugify(topic)}-{stamp}.md"
    path.write_text(result["report"], encoding="utf-8")

    print("\n" + "=" * 60)
    print(result["report"][:2000])
    if len(result["report"]) > 2000:
        print(f"\n...[report truncated in console, full saved to {path}]")
    print("=" * 60)
    print(f"\nSaved: {path}")
    print(f"Sources: {len(result['sources'])} | Model: {result['model']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
