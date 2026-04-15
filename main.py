"""CLI: run the Crawlbase + LangChain agent with a user prompt."""

from __future__ import annotations

import sys
from pathlib import Path

_CODE = Path(__file__).resolve().parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))

from dotenv import load_dotenv

load_dotenv(_CODE.parent / ".env")


def main() -> None:
    from agent import run_agent

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
    else:
        query = sys.stdin.read().strip()

    if not query:
        print("Usage: python main.py <prompt>", file=sys.stderr)
        print("   or: echo '<prompt>' | python main.py", file=sys.stderr)
        sys.exit(1)

    print(run_agent(query))


if __name__ == "__main__":
    main()
