"""Optional live smoke test against Crawlbase (no mocks).

Set RUN_CRAWLBASE_LIVE=1 and valid CRAWLBASE_REGULAR_TOKEN, then run:

    python code/scripts/smoke_crawlbase.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow imports from code/
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

    from crawlbase_client import CrawlbaseClient

    token = os.environ.get("CRAWLBASE_REGULAR_TOKEN", "").strip()
    if not token:
        print("CRAWLBASE_REGULAR_TOKEN is required.", file=sys.stderr)
        return 1

    url = os.environ.get("CRAWLBASE_SMOKE_URL", "https://example.com/")
    with CrawlbaseClient.from_env() as client:
        data = client.fetch_json(url, use_javascript=False)

    pc = data.get("pc_status")
    print(f"OK url={data.get('url')} pc_status={pc} original_status={data.get('original_status')}")
    body = data.get("body", "")
    preview = (body[:200] + "...") if isinstance(body, str) and len(body) > 200 else body
    print("body preview:", preview)
    return 0 if pc == 200 or str(pc) == "200" else 2


if __name__ == "__main__":
    raise SystemExit(main())
