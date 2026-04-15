"""LangGraph ReAct agent with Anthropic Claude and Crawlbase web grounding."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from tools import fetch_web_page

_CODE_DIR = Path(__file__).resolve().parent
load_dotenv(_CODE_DIR / ".env")
load_dotenv(_CODE_DIR.parent / ".env")

SYSTEM_PROMPT = """You are a helpful assistant with access to a real-time web fetch tool.

Use fetch_web_page when the user needs current information from the public web, facts that may have changed, or content that is not in your training data. Prefer the tool over guessing.

Limitations: some sites block crawlers, require login, or show captchas; the tool may fail for those. Do not assume fetched content is complete—large pages are truncated.

For mostly static HTML pages, call fetch_web_page with use_javascript=false. For heavy client-side JavaScript sites, use use_javascript=true (uses the Crawlbase JavaScript token).
"""


def _default_model_name() -> str:
    return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


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
    tools = [fetch_web_page]
    return create_react_agent(model, tools, prompt=SYSTEM_PROMPT)


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

