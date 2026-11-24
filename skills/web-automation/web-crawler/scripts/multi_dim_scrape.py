#!/usr/bin/env python3
"""Multi-dimension search × scrape pipeline for large-scale research data collection.

Writes one Markdown file per dimension to <outdir>/<country>/<dim_name>.md.
Each file contains: search keywords, source URLs, page content (via Jina Reader),
and falls back to DuckDuckGo snippets if Jina scraping fails.

Usage:
    python3 multi_dim_scrape.py --config keywords.json --outdir ./raw-data --country china --dims 0,1,2,3
    python3 multi_dim_scrape.py --config keywords.json --outdir ./raw-data --country us --dims all

Config format (keywords.json):
    {
      "china": {
        "01-health": ["kw1", "kw2", "kw3"],
        "02-career": ["kw1", "kw2", "kw3"]
      },
      "us": {
        "01-health": ["kw1", "kw2", "kw3"]
      }
    }

Designed to run in terminal(background=True) batches of 3-4 dimensions each
(~3-5 min per batch). Use notify_on_complete=True to get notified per batch.
"""
import argparse, json, os, sys, time
import requests
from ddgs import DDGS

BASE = os.path.expanduser("~/Workspace/research")


def search_ddg(query, max_results=6):
    """DuckDuckGo text search. verify=False for macOS LibreSSL TLS compat."""
    try:
        with DDGS(verify=False) as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"  [!] Search failed: {query[:50]} -> {e}", flush=True)
        return []


def scrape_jina(url, timeout=20, cap=6000):
    """Scrape page via Jina Reader. Returns truncated markdown or None."""
    try:
        resp = requests.get(f"https://r.jina.ai/{url}", timeout=timeout)
        if resp.status_code == 200 and len(resp.text) > 300:
            return resp.text[:cap]
    except Exception:
        pass
    return None


def process_dim(country, dim_name, keywords, outdir):
    """Search + scrape one dimension. Writes <outdir>/<country>/<dim_name>.md."""
    os.makedirs(os.path.join(outdir, country), exist_ok=True)
    outfile = os.path.join(outdir, country, f"{dim_name}.md")

    parts = [
        f"# {'🇨🇳' if country == 'china' else '🇺🇸'} {country} — {dim_name}",
        f"> Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} UTC",
        f"> Keywords: {len(keywords)} | Max pages/keyword: 2 | Jina cap: 6000 chars\n",
        "## Search Keywords\n",
    ]
    for kw in keywords:
        parts.append(f"- `{kw}`")
    parts.append("\n## Sources\n")

    total = 0
    for kw in keywords:
        print(f"  [{country}/{dim_name}] Search: {kw[:60]}...", flush=True)
        results = search_ddg(kw, max_results=6)
        time.sleep(0.3)

        scraped = 0
        for r in results[:5]:
            if scraped >= 2:
                break
            url = r.get("href") or r.get("link") or ""
            title = r.get("title", "")
            snippet = r.get("body", "")
            if not url:
                continue
            print(f"    Scrape: {url[:80]}...", flush=True)
            content = scrape_jina(url)
            if content and len(content) > 400:
                parts.append(f"\n### {title}")
                parts.append(f"**Source:** {url}")
                parts.append(f"**Snippet:** {snippet[:200]}\n")
                parts.append(content)
                parts.append("\n---\n")
                scraped += 1
                total += 1
                time.sleep(0.2)

        # Fallback: save search snippets if no scrape succeeded
        if scraped == 0 and results:
            for r in results[:3]:
                url = r.get("href") or r.get("link") or ""
                title = r.get("title", "")
                snippet = r.get("body", "")
                if url:
                    parts.append(f"\n### {title}")
                    parts.append(f"**Source:** {url}")
                    parts.append(f"**Snippet:** {snippet[:400]}\n")
                    parts.append("\n---\n")
                    total += 1

    parts.append(f"\n> Total sources: {total}\n")
    with open(outfile, "w") as f:
        f.write("\n".join(parts))
    print(f"  [{country}/{dim_name}] DONE: {total} sources -> {outfile}", flush=True)
    return total


def main():
    ap = argparse.ArgumentParser(description="Multi-dimension search × scrape pipeline")
    ap.add_argument("--config", required=True, help="Path to keywords JSON file")
    ap.add_argument("--outdir", default=".", help="Output directory for raw data")
    ap.add_argument("--country", required=True, help="Country key in config (e.g. china, us)")
    ap.add_argument("--dims", default="all", help="Comma-separated dimension indices or 'all'")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    dims = config[args.country]
    dim_names = list(dims.keys())

    if args.dims == "all":
        target_dims = dim_names
    else:
        indices = [int(x) for x in args.dims.split(",")]
        target_dims = [dim_names[i] for i in indices]

    grand_total = 0
    for dim_name in target_dims:
        keywords = dims[dim_name]
        grand_total += process_dim(args.country, dim_name, keywords, args.outdir)

    print(f"\n{'='*50}")
    print(f"[{args.country}] ALL DONE ({len(target_dims)} dims). Total sources: {grand_total}", flush=True)


if __name__ == "__main__":
    main()