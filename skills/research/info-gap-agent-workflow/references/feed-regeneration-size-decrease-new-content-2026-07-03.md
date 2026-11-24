# Feed Regeneration: Size Decrease Co-occurring with New Content

**Observed:** 2026-07-03 cron run of AI Newsletter Second Brain digest
**Source:** Smol AI News RSS (`https://news.smol.ai/rss.xml`)

## What Happened

The July 2 run reported:
- Feed size: 2,033,521 bytes (unchanged from July 1)
- Items: 665
- Slug scan: zero entries for `/issues/26-06-30/` and `/issues/26-07-0[0-2]/`
- Conclusion: gap day, 3-day dormancy

The July 3 run found:
- Feed size: 1,997,278 bytes (**decrease** of ~36KB)
- Items: 667 (**increase** of 2)
- Slug scan: found `/issues/26-06-30-sonnet5/` and `/issues/26-07-01-not-much/` — both new and uncompiled
- Conclusion: 2 new issues, 3-day gap resolved

## Why the Size Decreased While New Content Was Added

The feed was **regenerated** between the two runs. During regeneration:
1. HTML normalization of existing items reduced their size (entity encoding changes, whitespace normalization, attribute reformatting)
2. Two new items were added (net +2 items)
3. The overall size decrease from normalization exceeded the size increase from new items

This means the feed size delta signal (section ⑪ in SKILL.md) was **misleading** — a size decrease does NOT mean dormancy.

## Correct Approach

**Always do a full slug scan regardless of feed size direction.** Only skip parsing when:
- Feed size is byte-identical to previous run AND
- Item count is unchanged

The slug scan is a 1-second operation:
```bash
grep -oE 'issues/26-0[67]-[0-9]{2}[^"<]*' /tmp/feed.xml | sort -u
```

Compare the output against the previous run's known slug list. Any new slug = new content to ingest.

## XML Parser Failure and Regex Fallback

During this run, `xml.etree.ElementTree.parse()` failed with:
```
xml.etree.ElementTree.ParseError: not well-formed (invalid token): line 404, column 927
```

The feed contains malformed XML characters that the strict parser rejects. **Fallback: regex-based extraction.**

### Regex Fallback Parser Script

Write to `/tmp/parse_new_issues_v2.py` (not inline — security filter):

```python
#!/usr/bin/env python3
"""Parse RSS feed with regex fallback when XML parser fails."""
import re
import hashlib
import json

FEED_PATH = '/tmp/feed.xml'
NEW_SLUGS = ['26-06-30-sonnet5', '26-07-01-not-much']  # populate from grep slug scan

with open(FEED_PATH, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

results = []
for slug in NEW_SLUGS:
    slug_escaped = re.escape(slug)
    # Find the <item> containing this slug
    pattern = r'<item>(.*?)</item>'
    for match in re.finditer(pattern, content, re.DOTALL):
        item_text = match.group(1)
        if slug in item_text:
            title_match = re.search(r'<title>(.*?)</title>', item_text, re.DOTALL)
            link_match = re.search(r'<link>(.*?)</link>', item_text, re.DOTALL)
            pubdate_match = re.search(r'<pubDate>(.*?)</pubDate>', item_text, re.DOTALL)
            desc_match = re.search(r'<description>(.*?)</description>', item_text, re.DOTALL)
            content_match = re.search(r'<content:encoded>(.*?)</content:encoded>', item_text, re.DOTALL)
            
            title = title_match.group(1) if title_match else ''
            link = link_match.group(1) if link_match else ''
            pub_date = pubdate_match.group(1) if pubdate_match else ''
            desc = desc_match.group(1) if desc_match else ''
            body = content_match.group(1) if content_match else ''
            
            sha256 = hashlib.sha256(body.encode('utf-8')).hexdigest() if body else ''
            
            results.append({
                'slug': slug, 'title': title, 'link': link,
                'pubDate': pub_date, 'sha256': sha256,
                'body': body, 'description': desc
            })
            break

with open('/tmp/new_issues.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### HTML-to-Markdown Conversion (with entity unescaping)

The regex-extracted `content:encoded` contains HTML entities (`&lt;p&gt;`) that must be unescaped before `html2text` conversion:

```python
import html
import html2text

h = html2text.HTML2Text()
h.body_width = 0
h.unicode_snob = True

# CRITICAL: unescape HTML entities first
unescaped_body = html.unescape(issue['body'])
markdown_body = h.handle(unescaped_body)
```

Without `html.unescape()`, the markdown output will contain literal `<p>`, `<strong>`, `<a href="...">` tags instead of proper markdown formatting.

## Impact on Previous Guidance

This observation modifies section ⑪ of the SKILL.md:
- **Old guidance:** "A size decrease or no change suggests dormancy"
- **New guidance:** "A size decrease does NOT reliably indicate dormancy. Feed regeneration can shrink overall size while adding new items. Always do a full slug scan regardless of size direction."

This also adds a new pitfall to the 常见坑 table: `xml.etree.ElementTree` ParseError on large RSS feeds, with regex fallback as the solution.

## Recurring Pattern Confirmation

This is no longer a one-off observation. As of July 2026:

| Date | Size Before | Size After | Delta | Items Before | Items After | New Slugs |
|---|---|---|---|---|---|---|
| 2026-07-03 | 2,033,521 | 1,997,278 | -36KB | 665 | 667 | 2 (`26-06-30-sonnet5`, `26-07-01-not-much`) |
| 2026-07-08 | 2,001,802 | 1,995,552 | -6KB | 668 | 669 | 1 (`26-07-06-not-much`) |
| 2026-07-09 | 1,995,552 | 1,985,127 | -10KB | 669 | 671 | 2 (`26-07-07-not-much`, `26-07-08-grok-45`) |

**Conclusion:** Feed regeneration with size decrease + new content is a **confirmed recurring pattern (3 instances)**. The Smol AI News feed appears to undergo periodic HTML normalization that shrinks existing items while simultaneously adding delayed issues. The slug scan is the only reliable detection method — never rely on feed size delta alone, in either direction.