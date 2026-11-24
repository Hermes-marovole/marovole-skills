---
name: web-search
description: "Run web searches via Exa, DuckDuckGo, or native tools."
when_to_use: "Web search operations: free DuckDuckGo search (no API key), Hermes-native backends (xAI Grok / Tavily / Firecrawl), multi-engine intelligent routing (Tavily/Exa/Serper/Perplexity), and fallback strategies when primary search fails or returns empty."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [search, web-search, duckduckgo, tavily, exa, serper, perplexity, xai, grok, firecrawl, routing, fallback]
    category: research
---

# Web Search Operations

Unified skill for discovering and retrieving information from the web. Modes: free DuckDuckGo search, Hermes-native backend config (including Grok server-side search), intelligent multi-engine routing, and failover recovery when search breaks.

## Quick Decision Guide

| Situation | Mode |
|-----------|------|
| Free search, no API key, quick lookups | [DuckDuckGo Search](#duckduckgo-search) |
| Configure Hermes `web_search` / `web_extract` (xAI, Tavily…) | [Hermes Native Web Backends](#hermes-native-web-backends) |
| Need best engine per query type (shopping/research/discovery) | [Multi-Engine Router](#multi-engine-router) |
| Search failed (TLS error, empty results, rate limit) | [Fallback Strategy](#fallback-strategy) |

---

## DuckDuckGo Search

Free web search via DuckDuckGo. **No API key required.** Preferred when `web_search` is unavailable or unsuitable.

### Setup
```bash
pip install ddgs
```

### Python API (Primary)

**Critical**: `max_results` is **keyword-only** — positional usage raises an error.

```python
from ddgs import DDGS

with DDGS() as ddgs:
    # Text
    for r in ddgs.text("python async programming", max_results=5):
        print(r["title"], r["href"], r.get("body", "")[:200])

    # News
    for r in ddgs.news("AI regulation 2026", max_results=5):
        print(r["date"], r["title"], r.get("source"), r["url"])

    # Images
    for r in ddgs.images("semiconductor chip", max_results=5):
        print(r["title"], r["image"], r.get("thumbnail"))

    # Videos
    for r in ddgs.videos("FastAPI tutorial", max_results=5):
        print(r["title"], r.get("content"), r.get("duration"), r.get("provider"))
```

| Method | Best For | Key Fields |
|--------|----------|------------|
| `text()` | General research | title, href, body |
| `news()` | Current events | date, title, source, body, url |
| `images()` | Visuals, diagrams | title, image, thumbnail, url |
| `videos()` | Tutorials, demos | title, content, duration, provider |

### CLI (Alternative)
```bash
ddgs text -k "python async" -m 5
ddgs news -k "AI regulation" -m 5 -t w
ddgs images -k "landscape" -m 10
ddgs videos -k "python tutorial" -m 5 -o json
```

### Pitfalls
- `max_results` is keyword-only: `ddgs.text("q", 5)` raises TypeError
- macOS LibreSSL TLS failure: retry with `DDGS(verify=False)`
- Rate limiting: add delays between rapid sequential calls
- No full content extraction — follow up with `web_extract` or curl

---

## Hermes Native Web Backends

Hermes `web_search` / `web_extract` are **not** "whatever model is loaded."
Using `grok-4.5` (or Grok Build CLI) does **not** auto-inherit xAI Agent Tools search.
Backends are explicit under `web:` in `~/.hermes/config.yaml`.

| Backend | Auth | Search | Extract | Notes |
|---------|------|--------|---------|-------|
| **xAI (Grok)** | `XAI_API_KEY` or `xai-oauth` | ✔ | ❌ | Server-side Responses `web_search`; **opt-in only** (not auto-detected) |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | Good extract partner + manual search fallback |
| **Firecrawl** | `FIRECRAWL_API_KEY` | ✔ | ✔ | Common default search+extract |

Priority: `search_backend`/`extract_backend` → `web.backend` → auto-detect (**xAI excluded** from auto-detect).

### Dual-backend (Grok search + Tavily extract)

```bash
# Agent cannot patch config.yaml — use hermes config set
hermes config set web.backend xai
hermes config set web.search_backend xai
hermes config set web.extract_backend tavily
hermes config set web.xai.timeout 90
```

No automatic `xai → tavily` search failover. Keep Tavily key; switch with:

```bash
hermes config set web.search_backend tavily
hermes config set web.backend tavily
# reverse to xai when desired; leave extract_backend: tavily
```

Backend changes apply on **new session** (`/new` or relaunch).

### Trust model
- Tavily/Firecrawl/Exa: index/crawl-backed snippets
- **xAI**: LLM picks URLs and writes titles/descriptions — validate important links with `web_extract`/browser

### Smoke test
```bash
PY=~/.hermes/hermes-agent/venv/bin/python
$PY - <<'PY'
import os, sys
from pathlib import Path
os.environ["HERMES_HOME"] = str(Path.home()/".hermes")
sys.path.insert(0, str(Path.home()/".hermes"/"hermes-agent"))
from tools.web_tools import _get_search_backend, _get_extract_backend, web_search_tool
print("search=", _get_search_backend(), "extract=", _get_extract_backend())
print(web_search_tool(query="Hermes Agent Nous Research", limit=3)[:1200])
PY
```

### Which providers are actually usable (per-runtime)

A backend can be named in `web.*` config and still fail, because the key/package must exist in the **Hermes runtime venv** — `~/.hermes/hermes-agent/venv` (what `~/.local/bin/hermes` execs), not just in the system `python3` site-packages or the shell env.

```bash
PY=~/.hermes/hermes-agent/venv/bin/python
cd ~/.hermes/hermes-agent && HERMES_HOME=~/.hermes $PY - <<'PY'
import os, re, sys
from pathlib import Path
for line in open(os.path.expanduser('~/.hermes/.env')):
    m = re.match(r'^\s*([A-Z0-9_]+)\s*=\s*(.*)$', line)
    if m: os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))
sys.path.insert(0, str(Path.home()/'.hermes'/'hermes-agent'))
import tools.web_tools as wt
print("search:", wt._get_search_backend(), "extract:", wt._get_extract_backend())
for p in ('tavily','exa','firecrawl','parallel','brave-free','ddgs','searxng','perplexity'):
    print(f"  {p:11} -> {wt._is_backend_available(p)}")
PY
```

- `ddgs` reports False when the package sits only in the system python3: the free backend is then unreachable from Hermes (DDG stays a terminal-tool/skill route). Install into the runtime venv to make it a real backend.
- Profile `.env` copies (`~/.hermes/profiles/<n>/.env`) carry their OWN key variables, often empty; a root `~/.hermes/.env` edit does not reach a profile whose `web.backend` needs that key. Fix the profile file too.
- Verifying a key: read the resolved value and call the vendor API. Grepping `~/.zshrc` can capture an unexpanded `"${VAR:-$(...)}"` expression instead of the real secret — it 401s and looks like a dead key (char-count mismatch is the tell: 70 chars vs the real 36).

### Surge/Clash fake-IP breaks web_extract (every URL blocked)

Symptom: every `web_extract` entry returns `Blocked: URL targets a private or internal network address`, while `web_search` works fine. Cause: the TUN proxy answers DNS in fake-IP mode (`dig +short example.com` → `198.18.x.x`), and the pre-flight SSRF guard in `tools/web_tools.py` blocks that sentinel range before any provider call — so a server-side backend like Tavily never gets asked. Search is unaffected because the provider fetches server-side.

Fix: declare the proxy's sentinel block (Hermes' purpose-built escape hatch; loopback/RFC1918/link-local/metadata stay blocked even so).

```bash
hermes config set security.fake_ip_ranges '["198.18.0.0/15"]'   # match `dig +short` output
```

Verify without touching the live config (isolated copy): copy `config.yaml` to a scratch `HERMES_HOME`, add the block, then run the hermes venv python with `sys.path.insert(0, '~/.hermes/hermes-agent')` and check `tools.url_safety.is_safe_url('https://example.com')` returns True while `169.254.169.254` / `127.0.0.1` / `192.168.1.1` stay False. Takes effect on a new session/restart — the toggle is cached for the process lifetime.

Detail: `references/hermes-xai-web-backend.md`

---

## Multi-Engine Router

Intelligent routing across multiple search engines based on query intent.

### Supported Engines

| Engine | Type | Best Scene | Free Tier | Cheapest Paid |
|--------|------|------------|-----------|---------------|
| DuckDuckGo | General | Daily queries, privacy | Unlimited (no key) | — |
| Tavily | AI research | Deep research, academic | 1,000 credits/mo | $0.008/credit |
| Exa | Semantic/Neural | Discovery, similar content | $1,000 credits (one-time) | $7/1k searches |
| Serper | Google results | Shopping, local, prices | ❌ No free tier | $1/1k (50k min) |
| Perplexity | AI Q&A | Direct answers, citations | ❌ No free tier | $5/1k (Search API) |

> **See `references/search-api-pricing.md`** for full pricing breakdown, plan tiers, and cost-per-request examples for all four engines.

### Router CLI (one script, seven engines)

`scripts/search.py` in this skill **is** the router — call it instead of re-writing
intent dispatch. `--json` gives a stable `{engine, results}` envelope for chaining:

```bash
S=~/.hermes/skills/research/web-search/scripts/search.py
python3 $S search "Apple MacBook Pro price" --engine auto -n 5 --json   # intent-routed
python3 $S search "best peptide skincare brands" --engine exa -n 10      # semantic discovery
python3 $S search "site:hkexnews.hk 行业概览" --engine serper -n 10       # Google operators
python3 $S search "2026 营养补剂 市场规模" --engine brave -n 10          # independent index
python3 $S search "anything" --engine ddgs -n 5                          # no key, last resort
```

Engines: `auto | exa | tavily | serper | brave | firecrawl | ddgs`. `auto` scores the
query against the intent table below and picks for you; passing an engine explicitly
is how you enforce a source constraint (`serper` for `site:`/`filetype:`, `exa` for
"companies like X", `ddgs` when every key is rate-limited).

**`--engine` is a starting preference, not a pin.** The router walks
`[requested, serper, exa, tavily, tinyfish, brave, firecrawl, ddgs]` and returns the
first engine that produces rows, so a request for one engine whose key is missing,
rate-limited, or empty is answered by a *different* engine with no warning outside
the payload. Read the `engine` field in the JSON, never the fact that results came
back:

```bash
python3 $S search "probe" --engine ddgs -n 1 --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['engine'], '!= requested' if d['engine']!='ddgs' else 'ok')"
```

A per-engine health sweep that reports "5/5 green" without comparing `engine` to the
requested value is measuring nothing — five engines can be answered by Serper. Do
not record such a sweep as proof that engine N works. To genuinely test a keyless
engine (`ddgs`) that sits last in the chain, it must be reachable at all, which
means `ddgs` installed in the interpreter you invoke.

**Two deployed copies exist.** `scripts/search.py` in this skill is the source of
truth; the handoff-deployed copy lives at `~/.config/agent-research-router/search.py`
with its own `config.json` (intent table) and `.env`. Patch the intent table or a
bug in both, or a colleague running the handoff install behaves differently from
you while the skill looks correct.

**Keys live in more than one file.** The router reads the process env, so a key that
only exists in another agent's `.env` (`~/.config/<agent>/web-search-plus/.env`) is
invisible to it. Sync the ones you need into `~/.hermes/.env`, then assert the value
is **non-empty** — a line like `PARALLEL_API_KEY=` passes every "does the key exist"
check and still 401s:

```bash
python3 - <<'PY'
import re, pathlib
vals = dict(re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*(.*)$',
            pathlib.Path.home().joinpath('.hermes/.env').read_text(), re.M))
for k in ('EXA_API_KEY','TAVILY_API_KEY','SERPER_API_KEY','BRAVE_API_KEY','FIRECRAWL_API_KEY'):
    v = (vals.get(k) or '').strip().strip('"').strip("'")
    print(f"{k:18} {'OK ' + str(len(v)) + 'ch' if len(v) > 10 else 'EMPTY/MISSING'}")
PY
```

Then prove routing end-to-end per engine (`--engine <e> -n 1 --json`) rather than
trusting the key audit alone; a green audit with a 401 body still means no search.
Install `ddgs` into the **Hermes runtime venv** (`~/.hermes/hermes-agent/venv`), not
just system python3, or the free engine silently drops out of `auto`.

### Intent-Based Routing

```python
INTENT_SIGNALS = {
    "shopping": ["price", "buy", "shop", "cost", "deal", "sale", "purchase", "cheap", "review", "specs"],
    "local": ["near me", "local", "restaurant", "hotel", "weather", "directions"],
    "research": ["how does", "how to", "explain", "research", "analyze", "compare", "tutorial"],
    "discovery": ["similar to", "companies like", "alternatives", "competitors", "startup", "github", "paper"],
    "direct_answer": ["what is the", "who is", "when did", "where is", "current status"]
}
```

| Query Signal | Routed To | Example |
|--------------|-----------|---------|
| price/buy/cost | Serper | "iPhone 16 price" |
| near me / local | Serper | "pizza near me" |
| how does / explain | Tavily | "how does HTTPS work" |
| similar to / companies like | Exa | "companies like Stripe" |
| what is / current status | Perplexity | "status of Ethereum" |
| General query | DuckDuckGo | "Python tutorial" |

### Failure Modes
- 429 rate limit → exponential backoff 10s → 20s → 30s
- Engine unavailable → failover to next in chain
- Ambiguous query → route to DuckDuckGo and explain routing choice

---

## Fallback Strategy

When search fails, preserve query intent and switch routes instead of retrying the same broken path.

### Trigger Symptoms
- `ValueError: Unsupported protocol version 0x304` (LibreSSL/TLS)
- SSL/TLS, certificate, HTTP/2, library compatibility errors
- DuckDuckGo rate limits or empty results for clearly searchable topics
- Need current facts under provider instability

### Fallback Order

| Failure Point | Next Route |
|---------------|------------|
| Python `ddgs` fails | Browser search or direct vendor docs URL |
| Browser search blocked | `curl -L` official docs and parse |
| Official docs hard to find | Search vendor domain with targeted query |
| Conflicting results | Prefer official docs → SDK docs → integration docs |
| All general search Engines fail | Google News RSS (for news/time-sensitive topics) |
| All search engines + vendor sites fail (anti-bot/JS-walled) | Wikipedia category pages (for "list of X in year Y" structured queries) |

**Chinese-language queries**: 百度 answers automated traffic with a 安全验证 slider
and 搜狗 with a 点选 captcha, so neither is a reliable first route; 必应 with a
quoted Chinese personal name matches school/exam noise. Query unquoted
`姓名 单位 主题` on 必应, and for creator/social content use 头条搜索
(`so.toutiao.com/search?keyword=…&pd=video`), which indexes individual 抖音 video
titles with uploader, date and play count. Detail and login-wall map: the
`blocked-page-recovery` skill's cn-social-platform-lookup reference.

### Google News RSS Fallback (for news and current events)

When DuckDuckGo, Bing, and other search engines return empty or fail to extract content for **time-sensitive / news queries**, Google News RSS is a reliable fallback that returns structured XML with titles, links, and dates — no API key needed.

```bash
# Search Google News via RSS — returns XML with <title>, <link>, <pubDate>
curl -sL "https://news.google.com/rss/search?q=apple+price+hike+2025&hl=en-US&gl=US&ceid=US:en" \
  | python3 -c "
import sys, re, html as h
data = sys.stdin.read()
items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>', data, re.S)
for title, link, date in items[:15]:
    print(f'{h.unescape(title)[:120]}')
    print(f'  {date.strip()}')
"
```

**When to use**: breaking news, recent price changes, product launches, earnings calls — anything where freshness matters and general search engines return stale or empty results.

**Article content extraction**: Many news sites (CNBC, Forbes, Guardian, 9to5Mac) block curl or serve JS-heavy pages. TechCrunch and similar sites respond well to a simple `urllib.request` with a desktop User-Agent + regex `<p>` extraction:

```python
import urllib.request, re
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.S)
article_text = ' '.join(re.sub(r'<[^>]+>', '', p) for p in paragraphs)
article_text = re.sub(r'\s+', ' ', article_text).strip()
```

**Pitfall**: Google News article links are redirect URLs (news.google.com/rss/articles/...), not direct article URLs. Use them to identify which sources reported the story, then fetch the publisher's direct URL.

### Extracting Structured Data from JS-Rendered E-commerce Pages

Many vendor store pages (Apple, Dell, etc.) are JS-rendered but embed product/pricing JSON in the initial HTML payload. You can extract this with curl + regex without a browser.

**Apple Store example** — `apple.com.cn/shop/buy-mac/macbook-pro` embeds a `"prices"` JSON block with `priceKey` → `amount`/`raw_amount` mappings:

```python
import urllib.request, re

url = "https://www.apple.com.cn/shop/buy-mac/macbook-pro"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})
html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

# Method 1: Extract all priceKey → raw_amount pairs by proximity
price_keys = re.findall(r'"priceKey":\s*"([^"]*)"', html)
raw_amounts = re.findall(r'"raw_amount":\s*"?([\d,]+(?:\.\d+)?)"?', html)
# When counts match, they map 1:1 by position
for key, amount in zip(price_keys, raw_amounts):
    print(f"  {key}: RMB {amount}")

# Method 2: Extract the "prices" JSON block directly
prices_start = html.find('"prices":')
if prices_start >= 0:
    # Find matching closing brace by depth counting
    start = html.find('{', prices_start)
    depth, pos = 1, start + 1
    while depth > 0 and pos < len(html):
        if html[pos] == '{': depth += 1
        elif html[pos] == '}': depth -= 1
        pos += 1
    prices_json = html[start:pos]
    # Parse individual entries: "config-name":{"amount":XXXXX, ... "raw_amount":"XXXXX"}
    entries = re.findall(r'"([^"]+)":\s*\{[^}]*?"amount":\s*([\d.]+)[^}]*?"raw_amount":\s*"?([\d.]+)', prices_json)

# priceKey format: "16inch-silver-standard-m5max-18-40"
# Parse: size-color-finish-chip-cpuCore-gpuCore
```

**Key insights**:
- `priceKey` encodes the config: `16inch-silver-standard-m5max-18-40` = 16" / silver / standard finish / M5 Max / 18 CPU cores / 40 GPU cores
- `raw_amount` is the numeric price; `amount` may be a display string like "38,499"
- These are **base config prices only** — upgrade deltas (RAM/storage) are loaded via separate API calls not in initial HTML
- To estimate fully-configured prices: find base price + add known upgrade costs from news articles or AppleInsider "maxed out" reports
- For China store: prices are in RMB; for US store: in USD. Exchange at ~7.25 RMB/USD

**When browser tools fail**: Apple.com and many e-commerce sites block or 403/404 curl requests to article URLs, but the **store configuration pages** (`/shop/buy-*/`) are accessible because they need to be crawlable. Store pages return embedded JSON; news articles don't.

### Wikipedia Category Pages as Structured Data Fallback

When search engines fail (DuckDuckGo HTML anti-bot challenge, Bing result parsing yields nothing, IMDB/Metacritic 403/404/JS-required), **Wikipedia category pages** are accessible via simple `urllib.request` and provide structured, link-dense data — no API key, no JS rendering needed.

**Pattern**: Use for "list of X in year Y" queries — TV shows, films, albums, books, events by year, company acquisitions, etc.

```python
import urllib.request, re

# Category pages enumerate all entries with wiki links
url = "https://en.wikipedia.org/wiki/Category:2026_American_television_series_debuts"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
})
html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

# Extract all linked page titles
entries = re.findall(r'<a[^>]*href="/wiki/[^"]*"[^>]*>([^<]+)</a>', html)
# Filter out nav/category/portal cruft
entries = [e for e in entries if not e.startswith('Category') and not e.startswith('List of')
           and len(e) > 2 and e not in NAV_JUNK]
```

**Second step — fetch individual article pages for descriptions**:
```python
for entry in entries:
    slug = entry.replace(" ", "_").replace("&amp;", "&")
    url = f"https://en.wikipedia.org/wiki/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "..."})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
    text = re.sub(r'<[^>]+>', '', paragraphs[0]).strip()
    text = re.sub(r'\s+', ' ', text)  # first paragraph = article summary
```

**Category URL patterns that work**:
- `Category:YYYY_American_television_series_debuts` / `Category:YYYY_British_television_series_debuts`
- `Category:YYYY_films` / `Category:YYYY_video_games`
- `Category:YYYY_albums` / `Category:YYYY_books`
- `Category:YYYY_deaths` / `Category:YYYY_mergers_and_acquisitions`

**Pitfalls**:
- Wikipedia category pages may paginate (200+ entries). Look for a "next page" link.
- Some article titles contain special chars (`&amp;`, `&#039;`) — decode with `html.unescape()`.
- Non-ASCII slugs (e.g., `Étoile`) can break ASCII-only `urllib` — use `urllib.parse.quote(slug.encode('utf-8'))`.
- Categories only list * debut* dates — for ongoing series, use "List of YYYY American television seasons" or query specific show pages directly.

### Workflow
1. State the failing route; do not retry more than once
2. Rephrase into vendor-doc form: `site:<vendor-doc-domain> <product> API key`
3. Fetch official docs directly with browser/curl
4. Extract only actionable facts: console path, env var, base URL, SDK, model pattern
5. Verify against at least one official source when possible
6. Report uncertainty explicitly when only inferring model-specific naming

### Common Mistakes to Avoid
- Retrying the same `ddgs` call after TLS failure
- Treating search-provider failure as "information unavailable"
- Answering from memory without checking official docs
- Hiding uncertainty when only naming conventions were found

---

## Search + Extract Workflow

For full content, chain search with extraction:

```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("fastapi deployment guide", max_results=3))
    for r in results:
        print(r["title"], "->", r["href"])
# Then use web_extract tool on the best URL
```

If `web_extract` is unavailable:
- Use `browser_navigate` + `browser_snapshot` for rendered content
- Use `curl -L` + `python -m html2text` for static pages
- Use `url-to-markdown` skill for PDFs and complex pages

---

## Cross-References
- `url-to-markdown` — when search finds a URL and you need clean Markdown extraction
- `cloudflare-web-crawler` — when you need full-site crawl to Markdown
- `domain-intel` — when researching infrastructure (subdomains, SSL, WHOIS)
- `info-gap-agent-workflow` — for automated monitoring setups that include search triggers
- `hermes-ops` — config guards, backend ops, health checks
- `references/hermes-xai-web-backend.md` — Grok/xAI native search config that shipped on this machine
- `references/search-api-pricing.md` — Tavily/Exa/Serper/Perplexity pricing

---

*Web Search Operations — consolidated from duckduckgo-search, multi-engine-search, web-search-fallback-routing; + Hermes xAI native backend 2026-07*
