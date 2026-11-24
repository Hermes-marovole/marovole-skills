# RSS Ingest Resilience — 2026-07-18

## Observed pattern

A scheduled Smol AI News run initially hit a TLS transport error and mailbox scans returned `COREMAIL_UPSTREAM_ERROR`. Retrying the RSS request with `curl -k --http1.1 -sS -L` succeeded and returned a fresh feed. The mailbox auth token was valid, so mailbox authentication and folder availability must be reported separately.

## Reproduction pattern

```bash
curl -k --http1.1 -sS -L "https://news.smol.ai/rss.xml" -o /tmp/feed.xml
wc -c /tmp/feed.xml
```

Use this only as a bounded fallback after a normal `curl -sL` request fails; do not silently disable certificate verification for unrelated domains.

## Complete-body extraction

When parsing RSS with regex fallback, match the namespaced tag explicitly:

```python
body = field("content:encoded") or field("description")
raw_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
markdown = html2text.handle(html.unescape(body))
```

Do not use `field("encoded")`: it misses `<content:encoded>` and silently produces a short description-only raw file. Verify the extracted body length is plausibly large before writing the raw source. Hash the original entity-encoded body, before `html.unescape()` or Markdown conversion.

## Verification

After ingestion, verify every raw, digest, entity/concept, daily-report, index, sources, and log file exists and is non-empty. Confirm the daily report distinguishes “mailbox unavailable” from “mailbox empty.”
