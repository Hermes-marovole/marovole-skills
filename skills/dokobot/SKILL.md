---
name: dokobot
description: "Extract JS-rendered web pages via Chrome. Not static URLs."
when_to_use: "Read and extract content from any web page using a real Chrome browser — including SPAs, JavaScript-rendered sites, and complex dynamic pages. Use when fetching page content that headless tools can't render, searching the web, or reading fully rendered pages via your own browser."
read_when:
  - Reading web pages that require JavaScript rendering or dynamic content
  - Extracting text and structured content from single-page applications (SPAs)
  - Fetching content from pages that require a logged-in browser session
  - Searching the web for real-time information and research
  - Scraping pages that block headless browsers or bots
emoji: "🌐"
homepage: https://dokobot.ai
compatibility: Requires @dokobot/cli (npm install -g @dokobot/cli) and Chrome browser with Dokobot extension. Local mode needs bridge (dokobot install-bridge). Remote mode needs DOKO_API_KEY.
allowed-tools: Bash
metadata:
  author: dokobot
  version: "2.3.5"
  openclaw: {"requires": {"bins": ["dokobot"]}, "optionalEnv": ["DOKO_API_KEY"]}
---

# Dokobot — Read Web Pages with a Real Browser

Read, extract, and search web content through a real Chrome browser session. Unlike headless scrapers, Dokobot uses your actual browser with full JavaScript rendering — so it works on SPAs, dynamic sites, and complex web applications.

Also useful for multilingual tasks: translate web pages (网页翻译), summarize articles (文章总结), and extract content (内容提取) in any language. Supports web search (联网搜索) and reading from social platforms like Twitter/X, Reddit, YouTube, GitHub, LinkedIn, Facebook, Instagram, WeChat articles (微信公众号), Weibo (微博), Zhihu (知乎), Xiaohongshu (小红书), and Bilibili (B站).

Supports two modes: **local** (free, unlimited, via local bridge) and **remote** (via cloud API with `DOKO_API_KEY`).

## Prerequisites
- `@dokobot/cli` installed globally (`npm install -g @dokobot/cli`)
- Chrome browser with Dokobot extension installed
- **For local mode**: bridge installed (`dokobot install-bridge`)
- **For remote mode**: `DOKO_API_KEY` set via `dokobot config`, Remote Control enabled in extension
- If no API Key is set, ask the user to create one at the Dokobot dashboard: https://dokobot.ai/dashboard/api-keys, then run `dokobot config`

## Discovering commands

Run `dokobot --help` to list available commands. Run `dokobot <command> --help` to see full usage, flags, and defaults for any command.

```bash
dokobot --help
dokobot read --help
dokobot search --help
```

Always refer to `--help` output for the authoritative list of parameters and defaults. Do NOT assume flags or defaults from memory.

## Core commands

| Command | Description | Example |
|---------|-------------|---------|
| `read <url>` | Read a web page and return text | `dokobot read 'https://dokobot.ai/about'` |
| `search <query>` | Web search | `dokobot search 'latest news'` |
| `download images <url>` | Download images from a web page (supports private/lazy-loaded images) | `dokobot download images --local 'https://dokobot.ai/about'` |
| `list` | List connected devices | `dokobot doko list` |
| `close <id>` | Close an active read session | `dokobot doko close <SESSION_ID>` |

## Tool Selection Decision Tree (Hermes Context)

When fetching a web page in Hermes, choose in this order:

| Priority | Tool | When to Use |
|----------|------|-------------|
| 1 | `browser_navigate` + `browser_snapshot` | Most pages. Built-in, zero friction. |
| 2 | `curl -sL` (Jina Reader: `r.jina.ai`) | Plain HTML, API responses, GitHub raw. Fastest/cheapest. |
| 3 | `dokobot read --local` | SPA/JS-heavy sites, login-walled pages, Chinese platforms (小红书/知乎/B站), sites blocking headless browsers. |

**Known Boundaries**:
- ✅ SPAs, JS rendering, login walls, internal sites
- ✅ Chinese platforms: 小红书, 知乎, B站, 微博, 微信公众号
- ✅ Sites with mild bot detection
- ❌ Cloudflare **JS Challenge** pages (e.g. pplx.ai, perplexity.ai) — CDP-based reading triggers the challenge; requires real human interaction

> See [references/test-results.md](references/test-results.md) for concrete testing data from the 2026-04-30 session, including the capability matrix across Browserbase / Jina Reader / Dokobot.

## Multi-Device Handling (Critical)

If you have multiple Chrome profiles, Dokobot will error with "Multiple bridges found". Always list devices first and pick one:

```bash
# Step 1: List available devices
dokobot doko list

# Step 2: Use --device with the chosen device ID
dokobot read --local --device <DEVICE_ID> <url>
```

The device ID is stable per Chrome profile. Pick one and use it consistently.

## Usage in Hermes

When you need to read a page that Hermes browser tools can't handle, invoke via `terminal`:

```bash
# Standard invocation
dokobot read --local --device <DEVICE_ID> "<url>"

# With longer timeout for slow pages
dokobot read --local --device <DEVICE_ID> --timeout 60 "<url>"

# Continue reading a long page (use session ID from previous output)
dokobot read --local --device <DEVICE_ID> --session-id <SESSION_ID> --screens 5 "<url>"
```

For web search:
```bash
dokobot search --local --device <DEVICE_ID> "<query>"
```

For image download:
```bash
dokobot download images --local --device <DEVICE_ID> --format png,jpg "<url>"
```

## Error handling
- 401: Invalid API Key — ask user to check `DOKO_API_KEY`
- 403: API Key scope insufficient
- 422: Operation failed or was cancelled by user (read only)
- 503: No extension connected (read only) — check read command requirements
- 504: Timed out — retry with a longer `--timeout`

## Troubleshooting
If a command fails unexpectedly, check the CLI version and update if needed:
```bash
dokobot --version
dokobot update
```
To report a bug or request a feature:
```bash
dokobot feedback -t bug -m "description of the issue"
```

## Security & Permissions
- **Local-first architecture**: In local mode (`--local`), all data flows directly between the CLI and your browser via a local Unix socket. No data leaves your machine.
- **End-to-end encryption**: In remote mode, page content is encrypted on the browser before transmission and decrypted only on the CLI. The server never sees plaintext page content.
- **User-provisioned credentials**: `DOKO_API_KEY` is created and managed by the user. The skill never generates, stores, or exfiltrates credentials.
- **Explicit opt-in**: Remote Control must be manually enabled in the browser extension by the user. Local mode requires no API key or server.
- **Read-only by default**: the `read` and `search` commands only extract content. They do not modify pages, submit forms, or execute scripts.
