#!/usr/bin/env python3
"""Alma Multi-Engine Web Search & Extract Router (Synced with Hermes Agent + TinyFish).

Supports:
  - search <query> [--engine auto|exa|tavily|serper|tinyfish|firecrawl|brave|ddgs|hermes] [--max-results N] [--json]
  - extract <url...> [--engine firecrawl|tinyfish|jina|hermes] [--json]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path.home() / ".config/alma/web-search-plus"
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"


def load_env_file() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*)$", line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


def load_config() -> dict:
    load_env_file()
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def get_key(cfg: dict, engine: str, env_name: str) -> str:
    val = (cfg.get(engine, {}).get("api_key") or os.getenv(env_name, "")).strip()
    if not val or val.startswith("<YOUR_") or val.startswith("在这里填"):
        return ""
    return val


def route_engine(query: str, cfg: dict) -> str:
    q = query.lower()
    routing = cfg.get("auto_routing", {})
    if not routing.get("enabled", True):
        return cfg.get("defaults", {}).get("provider", "exa")
    mappings = routing.get("keyword_mappings", {})
    best_engine = None
    best_hits = 0
    for engine, kw_list in mappings.items():
        if engine in routing.get("disabled_providers", []):
            continue
        hits = sum(1 for kw in kw_list if kw.lower() in q)
        if hits > best_hits:
            best_hits = hits
            best_engine = engine
    if best_engine:
        return best_engine
    return cfg.get("hermes_native", {}).get("search_backend") or cfg.get("defaults", {}).get("provider", "exa")


def http_json(url: str, method: str = "GET", headers: dict = None, payload: dict = None, timeout: int = 25) -> dict:
    hdrs = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    if headers:
        hdrs.update(headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def search_exa(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "exa", "EXA_API_KEY")
    if not key:
        raise RuntimeError("EXA_API_KEY not configured")
    res = http_json(
        "https://api.exa.ai/search",
        method="POST",
        headers={"x-api-key": key},
        payload={"query": query, "numResults": limit, "type": cfg.get("exa", {}).get("type", "neural"), "contents": {"text": {"maxCharacters": 800}}},
    )
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": (r.get("text") or "")[:500], "publishedDate": r.get("publishedDate")}
        for r in res.get("results", [])
    ]


def search_tavily(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "tavily", "TAVILY_API_KEY")
    if not key:
        raise RuntimeError("TAVILY_API_KEY not configured")
    res = http_json(
        "https://api.tavily.com/search",
        method="POST",
        payload={"api_key": key, "query": query, "max_results": limit, "search_depth": cfg.get("tavily", {}).get("depth", "advanced")},
    )
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")[:500], "score": r.get("score")}
        for r in res.get("results", [])
    ]


def search_serper(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "serper", "SERPER_API_KEY")
    if not key:
        raise RuntimeError("SERPER_API_KEY not configured")
    res = http_json(
        "https://google.serper.dev/search",
        method="POST",
        headers={"X-API-KEY": key},
        payload={"q": query, "num": limit},
    )
    return [
        {"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", ""), "date": r.get("date")}
        for r in res.get("organic", [])[:limit]
    ]


def search_tinyfish(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "tinyfish", "TINYFISH_API_KEY")
    if not key:
        raise RuntimeError("TINYFISH_API_KEY not configured")
    base = cfg.get("tinyfish", {}).get("search_url", "https://api.search.tinyfish.ai")
    url = f"{base}?{urllib.parse.urlencode({'query': query})}"
    res = http_json(url, method="GET", headers={"X-API-Key": key}, timeout=45)
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": (r.get("snippet") or "")[:500], "date": r.get("date")}
        for r in res.get("results", [])[:limit]
    ]


def search_brave(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "brave", "BRAVE_SEARCH_API_KEY")
    if not key:
        raise RuntimeError("BRAVE_SEARCH_API_KEY not configured")
    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={limit}"
    res = http_json(url, method="GET", headers={"X-Subscription-Token": key, "Accept": "application/json"})
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("description", ""), "age": r.get("age")}
        for r in res.get("web", {}).get("results", [])[:limit]
    ]


def search_firecrawl(query: str, limit: int, cfg: dict) -> list:
    key = get_key(cfg, "firecrawl", "FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY not configured")
    res = http_json(
        "https://api.firecrawl.dev/v1/search",
        method="POST",
        headers={"Authorization": f"Bearer {key}"},
        payload={"query": query, "limit": limit},
    )
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": (r.get("description") or r.get("markdown") or "")[:500]}
        for r in res.get("data", [])[:limit]
    ]


def search_ddgs(query: str, limit: int, cfg: dict) -> list:
    from ddgs import DDGS
    with DDGS() as ddgs:
        rows = list(ddgs.text(query, max_results=limit))
    return [
        {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": (r.get("body") or "")[:500]}
        for r in rows
    ]


def search_hermes(query: str, limit: int, cfg: dict) -> dict:
    py = cfg.get("hermes_native", {}).get("python_bin", "/Users/marovole/.hermes/hermes-agent/venv/bin/python")
    code = (
        "import os, sys; "
        "os.environ['HERMES_HOME'] = '/Users/marovole/.hermes'; "
        "sys.path.insert(0, '/Users/marovole/.hermes/hermes-agent'); "
        "from tools.web_tools import web_search_tool; "
        f"print(web_search_tool(query={query!r}, count={limit}))"
    )
    out = subprocess.check_output([py, "-c", code], text=True, timeout=45)
    return json.loads(out)


def extract_firecrawl(url: str, cfg: dict) -> dict:
    key = get_key(cfg, "firecrawl", "FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY not configured")
    res = http_json(
        "https://api.firecrawl.dev/v1/scrape",
        method="POST",
        headers={"Authorization": f"Bearer {key}"},
        payload={"url": url, "formats": ["markdown"]},
        timeout=45,
    )
    data = res.get("data", {})
    return {"url": url, "engine": "firecrawl", "title": data.get("metadata", {}).get("title", ""), "markdown": data.get("markdown", "")}


def extract_tinyfish(url: str, cfg: dict) -> dict:
    key = get_key(cfg, "tinyfish", "TINYFISH_API_KEY")
    if not key:
        raise RuntimeError("TINYFISH_API_KEY not configured")
    fetch_url = cfg.get("tinyfish", {}).get("fetch_url", "https://api.fetch.tinyfish.ai")
    res = http_json(
        fetch_url,
        method="POST",
        headers={"X-API-Key": key},
        payload={"urls": [url], "format": "markdown", "per_url_timeout_ms": 60000},
        timeout=70,
    )
    rows = res.get("results") or []
    if not rows:
        raise RuntimeError(f"TinyFish Fetch returned no content: {res.get('errors')}")
    r = rows[0]
    text = r.get("text") if isinstance(r.get("text"), str) else json.dumps(r.get("text") or {})
    return {"url": url, "engine": "tinyfish", "title": r.get("title", ""), "markdown": text}


def extract_jina(url: str, cfg: dict) -> dict:
    req = urllib.request.Request(f"https://r.jina.ai/{url}", headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    return {"url": url, "engine": "jina", "markdown": text}


def extract_hermes(urls: list, cfg: dict) -> dict:
    py = cfg.get("hermes_native", {}).get("python_bin", "/Users/marovole/.hermes/hermes-agent/venv/bin/python")
    code = (
        "import os, sys; "
        "os.environ['HERMES_HOME'] = '/Users/marovole/.hermes'; "
        "sys.path.insert(0, '/Users/marovole/.hermes/hermes-agent'); "
        "from tools.web_tools import web_extract_tool; "
        f"print(web_extract_tool(urls={urls!r}))"
    )
    out = subprocess.check_output([py, "-c", code], text=True, timeout=60)
    return json.loads(out)


def main():
    parser = argparse.ArgumentParser(description="Alma Multi-Engine Web Search & Extract")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp_search = sub.add_parser("search", help="Run web search across engines")
    sp_search.add_argument("query", help="Search query")
    sp_search.add_argument("--engine", "-e", default="auto", choices=["auto", "exa", "tavily", "serper", "tinyfish", "brave", "firecrawl", "ddgs", "hermes"])
    sp_search.add_argument("--max-results", "-n", type=int, default=5)
    sp_search.add_argument("--json", action="store_true")

    sp_ext = sub.add_parser("extract", help="Extract clean Markdown from URLs")
    sp_ext.add_argument("urls", nargs="+", help="URLs to extract")
    sp_ext.add_argument("--engine", "-e", default="firecrawl", choices=["firecrawl", "tinyfish", "jina", "hermes"])
    sp_ext.add_argument("--json", action="store_true")

    args = parser.parse_args()
    cfg = load_config()

    if args.cmd == "search":
        engine = route_engine(args.query, cfg) if args.engine == "auto" else args.engine
        if engine == "hermes":
            res = search_hermes(args.query, args.max_results, cfg)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        dispatch = {
            "exa": search_exa,
            "tavily": search_tavily,
            "serper": search_serper,
            "tinyfish": search_tinyfish,
            "brave": search_brave,
            "firecrawl": search_firecrawl,
            "ddgs": search_ddgs,
        }
        chain = [engine] + [fb for fb in ["exa", "tavily", "serper", "tinyfish", "brave", "firecrawl", "ddgs"] if fb != engine]
        errors = {}
        for eng in chain:
            try:
                rows = dispatch[eng](args.query, args.max_results, cfg)
                if not rows:
                    errors[eng] = "empty results"
                    continue
                out = {"ok": True, "engine": eng, "routed_from": args.engine, "query": args.query, "results": rows}
                if args.json:
                    print(json.dumps(out, indent=2, ensure_ascii=False))
                else:
                    print(f"[{eng.upper()}] ({len(rows)} results for: {args.query})")
                    for i, r in enumerate(rows, 1):
                        print(f"\n{i}. {r.get('title')}")
                        print(f"   URL: {r.get('url')}")
                        if r.get("snippet"):
                            print(f"   {r.get('snippet')}")
                return
            except Exception as e:
                errors[eng] = str(e)
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    elif args.cmd == "extract":
        if args.engine == "hermes":
            res = extract_hermes(args.urls, cfg)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return
        ext_dispatch = {
            "firecrawl": extract_firecrawl,
            "tinyfish": extract_tinyfish,
            "jina": extract_jina,
        }
        ext_chain = [args.engine] + [fb for fb in ["firecrawl", "tinyfish", "jina"] if fb != args.engine]
        results = []
        for u in args.urls:
            last_err = None
            for eng in ext_chain:
                try:
                    results.append(ext_dispatch[eng](u, cfg))
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
            if last_err is not None:
                results.append({"url": u, "error": str(last_err)})
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            for r in results:
                print(f"=== {r.get('url')} ({r.get('engine', 'error')}) ===")
                print(r.get("markdown") or r.get("error", ""))


if __name__ == "__main__":
    main()
