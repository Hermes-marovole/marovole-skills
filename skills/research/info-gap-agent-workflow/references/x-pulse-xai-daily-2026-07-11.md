# x-pulse 落地记录（2026-07-11）

## What shipped

- Series dir: `AI-Newsletter-Second-Brain/x-pulse/`
- First file: `2026-07-11-xai-ai-tech-daily.md`
- Cron: `2fab94f5879a`, `15 7 * * *`, deliver `local`, workdir `/Users/marovole`
- Prompt: `~/.hermes/scripts/xai-ai-tech-daily-prompt.md`
- Inbox: 3 条职业底色选题写入 `content-creator/ideas/inbox.md`

## Data path that worked

1. `x_search_tool(query=…)` via `~/.hermes/hermes-agent/venv/bin/python` + `tools.x_search_tool`
   - requirements True; model `grok-4.20-reasoning`; credential `xai-oauth`
   - Returns JSON with synthesized `answer` + post citations
2. `web_search_tool(query=…, limit=8)` with `search_backend=xai`
   - Structured `data.web[]` titles/urls/descriptions

## Config prerequisite (same day)

```bash
hermes config set web.backend xai
hermes config set web.search_backend xai
hermes config set web.extract_backend tavily
```

Agent cannot patch `config.yaml` directly. Verifier may warn about refused patch; trust `hermes config set` + re-read yaml.

## Top signals captured that day (for format reference)

1. OpenAI Work OS / $/workflow narrative
2. Grok 4.5 economics + Tesla Hey Grok entry
3. Anthropic efficiency / governance narrative
4. Meta Muse Spark 1.1 coding-agent pricing
5. SK Hynix / HBM infrastructure

## Trust

Both search paths are Grok-synthesized. Label `trust: synthesized`. Validate before publish.