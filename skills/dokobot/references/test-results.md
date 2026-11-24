# Dokobot Testing Results — 2026-04-30 Session

## Environment
- Dokobot CLI: v2.10.6
- Chrome Extension: v0.2.7
- Browser: Chrome (macOS)
- Mode: `--local` (free, unlimited)
- Device ID: `<YOUR_CHROME_DEVICE_ID>`

## Test Results

### ✅ Xiaohongshu (小红书) — PASS
- URL: https://www.xiaohongshu.com/explore
- Result: Successfully extracted explore feed with column-aware layout
- Output: Structured Markdown with titles, authors, like counts, image URLs, and link references
- Key finding: Works on JS-heavy Chinese SPA platforms where Browserbase struggles

### ❌ Perplexity Publisher Program (pplx.ai) — FAIL
- URL: https://pplx.ai/publisher-prog
- Result: Cloudflare JS Challenge page returned
- Output: "Performing security verification" — same as Browserbase and Jina Reader
- Key finding: CDP-based reading (Chrome DevTools Protocol) triggers Cloudflare's bot detection even from a real browser

### ✅ Dokobot Homepage — PASS
- URL: https://dokobot.ai/
- Result: Full page extracted with structured output
- Output: Column-aware, images as references, links numbered

## Capability Matrix

| Site Type | Browserbase | Jina Reader | Dokobot |
|-----------|------------|-------------|---------|
| Static HTML | ✅ | ✅ | ✅ |
| JS SPA (XHS) | ❌ | ❌ | ✅ |
| Cloudflare JS Challenge | ❌ | ❌ | ❌ |
| Login-walled | ❌ | ❌ | ✅ |
| API endpoints | ❌ | ✅ | ✅ |

## Lessons Learned

1. **Multi-device handling**: When multiple Chrome profiles exist, `dokobot read --local` fails with "Multiple bridges found". Must use `dokobot doko list` first and specify `--device`.

2. **Cloudflare JS Challenge is a hard boundary**: Even a real browser accessed via CDP triggers it. Requires human interaction to pass.

3. **Device ID is stable**: Once identified, the device ID can be reused across sessions.

4. **Output quality**: Column-aware layout extraction is genuinely useful for multi-column pages. Image extraction as numbered references saves tokens.

5. **Free & unlimited**: Local mode has no rate limits or usage caps. Zero cost.
