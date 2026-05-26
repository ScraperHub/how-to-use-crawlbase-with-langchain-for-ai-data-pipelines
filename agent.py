"""LangGraph ReAct agent with Anthropic Claude and Crawlbase web grounding."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_crawlbase import CrawlbaseTool
from langgraph.prebuilt import create_react_agent

_CODE_DIR = Path(__file__).resolve().parent
load_dotenv(_CODE_DIR / ".env")
load_dotenv(_CODE_DIR.parent / ".env")

SYSTEM_PROMPT = """You are a helpful assistant with access to real-time web fetch tools backed by Crawlbase.

Use crawlbase_fetch when the user needs current information from mostly static HTML pages.
Use crawlbase_fetch_js when the target site relies on client-side JavaScript rendering (only available if configured).

Prefer these tools over guessing when the user needs live or external web content.

Limitations: some sites block crawlers, require login, or show captchas; the tools may fail for those. Do not assume fetched content is complete—large pages may be long.
"""


def _default_model_name() -> str:
    return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def _build_crawlbase_tools() -> list[CrawlbaseTool]:
    token = os.environ.get("CRAWLBASE_TOKEN", "").strip()
    if not token:
        raise ValueError("CRAWLBASE_TOKEN is not set")

    tools: list[CrawlbaseTool] = [CrawlbaseTool(token=token)]
    js = os.environ.get("CRAWLBASE_JS_TOKEN", "").strip()
    if js:
        tools.append(
            CrawlbaseTool(
                token=js,
                name="crawlbase_fetch_js",
                description=(
                    "Fetches JS-rendered / SPA pages via Crawlbase and returns Markdown. "
                    "Use for sites where content is loaded client-side."
                ),
            )
        )
    return tools


def build_agent() -> Any:
    """Return a compiled LangGraph ReAct agent."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")

    model = ChatAnthropic(
        model=_default_model_name(),
        api_key=api_key,
        temperature=0,
    )
    return create_react_agent(model, _build_crawlbase_tools(), prompt=SYSTEM_PROMPT)


def run_agent(query: str) -> str:
    """Run the agent and return the final assistant text."""
    app = build_agent()
    result = app.invoke(
        {"messages": [HumanMessage(content=query)]},
    )
    messages: list[BaseMessage] = result["messages"]
    last = messages[-1]
    if isinstance(last, AIMessage):
        content = last.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
    return str(last.content)
