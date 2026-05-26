"""Optional live smoke test against Crawlbase (no mocks).

Set RUN_CRAWLBASE_LIVE=1 and valid CRAWLBASE_TOKEN, then run:

    python scripts/smoke_crawlbase.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_CODE = Path(__file__).resolve().parent.parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))

from dotenv import load_dotenv

load_dotenv(_CODE / ".env")
load_dotenv(_CODE.parent / ".env")


def main() -> int:
    if os.environ.get("RUN_CRAWLBASE_LIVE") != "1":
        print("Set RUN_CRAWLBASE_LIVE=1 to run this smoke test.", file=sys.stderr)
        return 0

    from langchain_crawlbase import CrawlbaseTool

    token = os.environ.get("CRAWLBASE_TOKEN", "").strip()
    if not token:
        print("CRAWLBASE_TOKEN is required.", file=sys.stderr)
        return 1

    url = os.environ.get("CRAWLBASE_SMOKE_URL", "https://example.com/")
    tool = CrawlbaseTool(token=token)
    result = tool.invoke({"url": url})

    if result.startswith("Error fetching"):
        print(result, file=sys.stderr)
        return 2

    preview = (result[:200] + "...") if len(result) > 200 else result
    print(f"OK url={url}")
    print("markdown preview:", preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
