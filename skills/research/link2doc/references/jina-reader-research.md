# Jina Reader — Research via Content Extraction

Jina Reader (`https://r.jina.ai/<url>`) is a free service that renders web pages as clean Markdown, bypassing most anti-bot measures:

- DuckDuckGo CAPTCHAs
- X/Twitter login walls (but not all — some still block)
- Cloudflare challenges (some)
- General anti-scraping protections

## Usage patterns

### Simple fetch
```bash
curl -sL "https://r.jina.ai/https://en.wikipedia.org/wiki/Acquired_(podcast)" | head -200
```

### Parallel research for multi-item curation
Use `delegate_task` to research multiple items simultaneously — much faster than serial browsing:

```python
delegate_task(
    context="Research these items using Jina Reader: curl -sL 'https://r.jina.ai/<url>' ...",
    tasks=[
        {"goal": "Research item 1 details", "toolsets": ["terminal"]},
        {"goal": "Research item 2 details", "toolsets": ["terminal"]},
        {"goal": "Research item 3 details", "toolsets": ["terminal"]},
    ]
)
```

### What to extract from Jina Reader output

| Field | Example |
|-------|---------|
| Title | Top of markdown output |
| URL Source | `URL Source: https://...` line |
| Published Time | `Published Time: 2024-...` line |
| Body content | Full markdown after headers |

### Limitations

- Some sites return empty or truncated content (X posts sometimes fail)
- **X/Twitter 帖子提取**：Jina Reader 是当前首选方案，能绕过登录墙和反爬限制，无需浏览器 daemon。输出包含完整正文、作者信息、互动数据和解析后的真实 URL。详见 `references/x-twitter-post-extraction.md`。
- Rate limits may apply for rapid-fire requests
- Not reliable for JavaScript-heavy SPAs (use browser instead)
- Wikipedia works very well; podcast/Apple Podcasts listings sometimes return empty
- Fallback to `browser_navigate` when Jina Reader returns insufficient content
