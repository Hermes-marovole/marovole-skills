# Raw Frontmatter Schema Variance + Delayed Friday Issue (2026-07-26)

> Session notes from AI Newsletter Second Brain Sunday cron. Class-level lessons for RSS dedupe and weekend lag.

## 1. Frontmatter schema variance (sibling runs)

Two coexisting raw-source frontmatter styles in the same vault:

**Style A (newer / this run):**
```yaml
---
source_url: https://news.smol.ai/issues/26-07-24-opus-5/
ingested: 2026-07-26
source_title: "Opus 5"
published: Fri, 24 Jul 2026 05:44:39 GMT
sha256: 1f241a3cbd57ea62ed46a292cb099e94c9c61ab51e069b8fcba337fc5425ff0a
hash_formula: sha256(content:encoded)
slug: 26-07-24-opus-5
coverage: 2026-07-23 to 2026-07-24
---
```

**Style B (sibling Jul 25 compile of July 23):**
```yaml
---
title: "Smol AI News - 2026-07-23"
date: "2026-07-23"
source: "https://news.smol.ai/issues/26-07-23-not-much/"
rss_hash: "8e65026fdbb3333443731587d164ba722c089655acfd69bdc3ac4518a19f9348"
hash_formula: "sha256(content:encoded)"
type: newsletter-raw
coverage: "2026-07-22/2026-07-23"
tags: [smol-ai-news, raw-source]
---
```

### Failure mode

A dedupe script that only parses `source_url:` reported July 23 as **NEW** even though `raw/newsletters/2026-07-23-smol-ai-news.md` already existed (41,842 B).

### Correct compiled-set builder

```python
import re
from pathlib import Path

def compiled_slugs(raw_dir: Path) -> set[str]:
    slugs = set()
    for p in raw_dir.glob("*-smol-ai-news.md"):
        # Filename date is a strong signal even without frontmatter URL
        m = re.match(r"(\d{4}-\d{2}-\d{2})-smol-ai-news\.md", p.name)
        head = p.read_text(encoding="utf-8", errors="replace")[:1200]
        for pat in (
            r"source_url:\s*(\S+)",
            r"(?m)^source:\s*[\"']?(\S+?)[\"']?\s*$",
            r"https?://news\.smol\.ai/issues/([^/\s\"']+)",
        ):
            for hit in re.finditer(pat, head):
                val = hit.group(1)
                sm = re.search(r"issues/([^/\s\"']+)", val) if "issues/" not in pat else None
                slug = (sm.group(1) if sm else hit.group(1)).rstrip("/")
                if re.match(r"\d{2}-\d{2}-\d{2}", slug):
                    slugs.add(slug)
        # Optional: map filename date → yy-mm-dd prefix for date-level presence
        if m:
            y, mo, d = m.group(1).split("-")
            slugs.add(f"{y[2:]}-{mo}-{d}")  # soft date key, e.g. 26-07-23
    return slugs
```

**Rules:**
- Primary key remains full URL slug (`26-07-24-opus-5`), not hash.
- Accept `sha256` **or** `rss_hash`.
- Do **not** re-ingest when filename exists for that issue date and content already compiled.
- Feed regeneration may change body hash for already-compiled slugs (July 23 hash in live feed ≠ compiled `rss_hash`); slug/filename match wins.

## 2. Delayed Friday issue (weekend lag)

| Run | Feed size | Items | Top / new slugs | Action |
|---|---|---|---|---|
| 2026-07-25 (Sat) sibling | 2,099,934 | 682 | top `26-07-23-not-much` only | Compiled Jul 23; gap for Jul 24 |
| 2026-07-25 re-check | identical | 682 | still no Jul 24 | Confirm gap |
| 2026-07-26 (Sun) | **2,118,148** | **683** | **NEW `26-07-24-opus-5`** | Full ingest |

Classification: **delayed weekday publish**, not dormancy and not slug-rename-only regeneration.

Handling:
1. Saturday gap report: “Fri issue not in feed yet; may appear weekend/Mon.”
2. Do not escalate to 3–7 day dormancy after one weekend miss of a single Friday.
3. Sunday/Monday: always full slug scan for the missing weekday date (`26-07-24` etc.).
4. On appearance: normal pipeline (raw → digest → 3 concepts → index/log/sources).

## 3. Bulk wiki update preference

For multi-file concept + log + sources + index updates in one cron run, prefer a single `/tmp/update_wiki.py` over chained `patch()` calls (escape-drift + partial apply risk). Keep digest + daily-report as dedicated `write_file` artifacts; verify sizes before final response.

## 4. Mailbox (unchanged)

`mail-cli --profile 04`: JWT valid; all fid 1–6 `COREMAIL_UPSTREAM_ERROR` continues (78+ days zero inbound). RSS remains sole ingress. Backup RSS still critical/unconfigured.
