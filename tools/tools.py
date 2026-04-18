from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import time
import hashlib
import json
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ── Simple in-memory cache ────────────────────────────────────────────────────
_search_cache: dict[str, str] = {}
_scrape_cache: dict[str, str] = {}


def _cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ── Retry helper with exponential backoff ─────────────────────────────────────
def _retry(fn, max_retries=3, base_delay=1.0):
    """Execute fn() with exponential backoff on failure."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    raise last_error


# ── Rate limiter ──────────────────────────────────────────────────────────────
_last_call_time: dict[str, float] = {}
MIN_INTERVAL = 0.5  # seconds between calls per tool


def _rate_limit(tool_name: str):
    now = time.time()
    last = _last_call_time.get(tool_name, 0)
    if now - last < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - (now - last))
    _last_call_time[tool_name] = time.time()


# ── Tools ─────────────────────────────────────────────────────────────────────
@tool("web_search")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for recent and reliable information on a topic.
    Returns title, url, snippets. Use max_results to control depth (1-10)."""
    _rate_limit("web_search")

    key = _cache_key(f"{query}:{max_results}")
    if key in _search_cache:
        return _search_cache[key]

    try:
        max_results = max(1, min(10, max_results))

        def do_search():
            return tavily.search(query=query, max_results=max_results)

        results = _retry(do_search)

        out = []
        for r in results["results"]:
            out.append(
                f'Title: {r["title"]}\nURL: {r["url"]}\nSnippet: {r["content"][:300]}\n'
            )

        result = "\n--------\n".join(out)
        _search_cache[key] = result
        return result
    except Exception as e:
        return f"Search failed after retries: {str(e)}"


@tool("web_scrape")
def web_scrape(url: str) -> str:
    """Scrapes the content of a webpage and returns the cleaned text content."""
    _rate_limit("web_scrape")

    key = _cache_key(url)
    if key in _scrape_cache:
        return _scrape_cache[key]

    try:
        def do_scrape():
            resp = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            resp.raise_for_status()
            return resp

        response = _retry(do_scrape)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)[:5000]

        _scrape_cache[key] = text
        return text
    except Exception as e:
        return f"Scrape failed after retries: {str(e)}"


def clear_cache():
    """Clear all cached search and scrape results."""
    _search_cache.clear()
    _scrape_cache.clear()
