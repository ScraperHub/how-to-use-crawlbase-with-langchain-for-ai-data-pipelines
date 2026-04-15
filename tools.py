"""LangChain tools backed by Crawlbase for real-time web grounding."""

from __future__ import annotations

import html as html_module
import re
from html.parser import HTMLParser

import httpx
from langchain_core.tools import tool

from crawlbase_client import CrawlbaseClient, CrawlbaseError

DEFAULT_MAX_CHARS = 16_000


class _HTMLToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        t = data.strip()
        if t:
            self._chunks.append(t)

    def get_text(self) -> str:
        return " ".join(self._chunks)


def html_body_to_text(html: str) -> str:
    """Strip tags to plain text; collapse whitespace."""
    parser = _HTMLToText()
    try:
        parser.feed(html)
    except Exception:
        fallback = re.sub(r"<[^>]+>", " ", html)
        return html_module.unescape(re.sub(r"\s+", " ", fallback).strip())
    text = html_module.unescape(parser.get_text())
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20] + "\n...[truncated]..."


def _get_client() -> CrawlbaseClient:
    return CrawlbaseClient.from_env()


@tool
def fetch_web_page(url: str, use_javascript: bool = False) -> str:
    """Fetch a public web page in real time via Crawlbase for grounding.

    Use ``use_javascript=False`` (default) for mostly static HTML. Set
    ``use_javascript=True`` when the target site relies on client-side JS
    rendering (Crawlbase uses your JavaScript token for that path).

    Returns page text (HTML stripped), truncated to fit model context.
    """
    client = _get_client()
    try:
        data = client.fetch_json(url, use_javascript=use_javascript)
    except CrawlbaseError as e:
        return f"Crawlbase error: {e}"
    except httpx.HTTPError as e:
        return f"HTTP error calling Crawlbase: {e}"

    pc = data.get("pc_status")
    orig = data.get("original_status")
    final_url = data.get("url", url)
    body = data.get("body", "")

    if isinstance(pc, str):
        try:
            pc_int = int(pc)
        except ValueError:
            pc_int = None
    else:
        pc_int = int(pc) if pc is not None else None

    if pc_int is not None and pc_int != 200:
        return (
            f"Crawl failed (pc_status={pc}, original_status={orig}, url={final_url}). "
            "Page may be blocked, captcha, or require a different crawl mode."
        )

    if not isinstance(body, str):
        body = str(body)

    text = html_body_to_text(body)
    text = truncate(text, DEFAULT_MAX_CHARS)
    header = f"url={final_url} original_status={orig} pc_status={pc}\n\n"
    return header + text
