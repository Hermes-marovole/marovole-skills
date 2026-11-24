# Hermes × xAI native web search (session knowledge)

## Mental model

| Layer | What it is |
|-------|------------|
| Grok Build CLI | xAI product; own agent loop + Agent Tools |
| Hermes agent | Nous product; own tools (`web_search`, `web_extract`, `x_search`, …) |
| Chat model = `grok-4.5` via `xai-oauth` | Inference only |
| `web.search_backend: xai` | Routes Hermes `web_search` to xAI Responses server-side `web_search` |
| `x_search` tool | Separate toolset; uses xAI `x_search` when credentials exist |

Grok as **brain** ≠ Grok Build **tool stack**.

## Config that worked (2026-07-11)

```yaml
# ~/.hermes/config.yaml
model:
  provider: xai-oauth
  default: grok-4.5
web:
  backend: xai
  search_backend: xai
  extract_backend: tavily   # required partner; xAI has no extract
  xai:
    timeout: 90
```

Commands (agent cannot write `config.yaml` directly):

```bash
hermes config set web.backend xai
hermes config set web.search_backend xai
hermes config set web.extract_backend tavily
hermes config set web.xai.timeout 90
```

Auth path used: `hermes auth` / `xai-oauth` logged in (`hermes doctor` shows xAI OAuth OK). `XAI_API_KEY` optional if OAuth is valid.

## Docs anchors

- Web backends: `website/docs/user-guide/features/web-search.md` in hermes-agent source
- xAI knobs: `web.xai.model` default `grok-build-0.1`, domains allow/deny max 5, timeout default 90s
- xAI **not** in auto-detect chain even when OAuth/API key present
- On 401 with OAuth: one forced token refresh + retry

## Verification

```text
search_backend = xai
extract_backend = tavily
web_search("Hermes Agent Nous Research", limit=3) → success with structured web[] results
```

Python entry for smoke tests: `~/.hermes/hermes-agent/venv/bin/python` (wrapper `~/.local/bin/hermes` execs that venv).

## Environment pitfall (not a backend bug)

Local URL safety may block `web_extract` when DNS resolves to Fake-IP ranges (`198.18.0.0/15`) under Surge TUN. Diagnose as proxy/Fake-IP, not "Tavily broken." Server-side xAI search bypasses that path.

## Backup switch

No automatic xai→tavily search failover. Keep `TAVILY_API_KEY`; flip `search_backend`/`backend` with `hermes config set` when needed.
