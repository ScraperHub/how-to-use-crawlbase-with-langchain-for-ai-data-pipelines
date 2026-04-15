"""HTTP client for Crawlbase Crawling API (https://crawlbase.com/docs/crawling-api/)."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

import httpx

CRAWLBASE_API_BASE = "https://api.crawlbase.com/"
DEFAULT_TIMEOUT_S = 90.0


class CrawlbaseError(Exception):
    """Raised when Crawlbase returns an error or unexpected payload."""


class CrawlbaseClient:
    """GET crawling with format=json for structured status and body fields."""

    def __init__(
        self,
        regular_token: str,
        js_token: str | None = None,
        *,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not regular_token or not regular_token.strip():
            raise ValueError("CRAWLBASE_REGULAR_TOKEN is required")
        self._regular_token = regular_token.strip()
        self._js_token = (js_token or "").strip() or None
        self._timeout = timeout_s
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout_s),
            headers={"Accept-Encoding": "gzip"},
            transport=transport,
        )

    @classmethod
    def from_env(cls) -> CrawlbaseClient:
        regular = os.environ.get("CRAWLBASE_REGULAR_TOKEN", "")
        js = os.environ.get("CRAWLBASE_JS_TOKEN")
        return cls(regular_token=regular, js_token=js)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> CrawlbaseClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _token(self, use_javascript: bool) -> str:
        if use_javascript:
            if not self._js_token:
                raise CrawlbaseError(
                    "JavaScript crawling requested but CRAWLBASE_JS_TOKEN is not set"
                )
            return self._js_token
        return self._regular_token

    def fetch_json(self, url: str, *, use_javascript: bool = False) -> dict[str, Any]:
        """Request a URL via Crawlbase; returns parsed JSON (format=json)."""
        params = {
            "token": self._token(use_javascript),
            "url": url,
            "format": "json",
        }
        query = urlencode(params)
        full = f"{CRAWLBASE_API_BASE}?{query}"
        resp = self._client.get(full)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise CrawlbaseError("Crawlbase response is not a JSON object")
        return data
