<a href="https://crawlbase.com/signup?utm_source=github&utm_medium=readme&utm_campaign=crawling_api_banner" target="_blank">
  <img src="https://github.com/user-attachments/assets/afa4f6e7-25fb-442c-af2f-b4ddcfd62ab2" 
       alt="crawling-api-cta" 
       style="max-width: 100%; border: 0;">
</a>


# Crawlbase + LangChain sample

Small CLI demo: a **LangGraph ReAct** agent (Anthropic Claude) with **[langchain-crawlbase](https://github.com/crawlbase/langchain-crawlbase)** tools that pull live web pages as Markdown for grounding.

## Setup

Python 3.11+ recommended.

```bash
cd code
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` in this folder (or use a `.env` in the parent directory; the agent loads both).

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Yes | Claude API |
| `CRAWLBASE_TOKEN` | Yes | Crawlbase normal (non-JS) requests via `crawlbase_fetch` |
| `CRAWLBASE_JS_TOKEN` | For JS renders | Optional second tool `crawlbase_fetch_js` for SPA pages |
| `ANTHROPIC_MODEL` | No | Overrides default `claude-sonnet-4-20250514` |

## Run

```bash
python main.py What is the title of https://example.com/ ?
```

Or pipe a prompt:

```bash
echo "Summarize https://example.com/" | python main.py
```

## Layout

| File | Role |
|------|------|
| `main.py` | CLI entrypoint |
| `agent.py` | ReAct agent + `CrawlbaseTool` wiring |
| `scripts/smoke_crawlbase.py` | Optional live Crawlbase check (no LLM) |

Web fetching is handled by the official [langchain-crawlbase](https://github.com/crawlbase/langchain-crawlbase) package (`CrawlbaseTool`, `CrawlbaseLoader`, `CrawlbaseRetriever`).

## Optional: live Crawlbase check

To verify tokens against the real API (no LLM):

```bash
set RUN_CRAWLBASE_LIVE=1
python scripts\smoke_crawlbase.py
```

On macOS/Linux use `export RUN_CRAWLBASE_LIVE=1`. Optional: `CRAWLBASE_SMOKE_URL` to change the target URL (default `https://example.com/`).
