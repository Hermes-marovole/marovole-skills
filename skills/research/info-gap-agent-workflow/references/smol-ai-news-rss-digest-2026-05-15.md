# Smol AI News RSS Digest Notes — 2026-05-15

Session lesson for the info-gap agent workflow.

## What changed
- The 2026-05-14 Smol AI News issue was titled "not much happened today" but the RSS body was still ~27k chars and high-signal.
- The correct handling was to treat the title as low-confidence, then inspect `content:encoded` and save the full raw body before deciding whether to ingest.
- New issue detection should key off stable identifiers: `link`, GUID, raw filename, and body sha256 — not `pubDate` or title alone.

## Practical parsing recipe
1. `curl -sL https://news.smol.ai/rss.xml -o /tmp/smol-ai-news-rss.xml`
2. Parse the XML from a temp file.
3. Read `content:encoded` when present; fall back to `description`.
4. Normalize HTML to text.
5. Compute sha256 over the normalized body text.
6. Save raw source with frontmatter before compiling the digest.

## Digest composition notes
- Even when the feed title looks dormant, the body may contain useful sections on agent platforms, sandboxing, trace databases, and open-weight inference.
- Prefer a concise top-signal summary, then a deep-read candidate, then the raw/source status.
- Preserve idempotency: if today's digest/raw/log already exists, merge rather than duplicate.
