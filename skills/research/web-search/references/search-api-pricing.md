# Search API Pricing Reference (verified July 2026)

Pricing data fetched directly from vendor pricing pages. Re-verify if more than 6 months old.

## Quick Comparison

| Engine | Free Tier | Cheapest Paid | Best For | Includes LLM Answer |
|--------|-----------|---------------|----------|---------------------|
| Tavily | ✅ 1,000 credits/mo | $0.008/credit | AI research | ❌ |
| Exa | ✅ $1,000 credits (one-time) | $7/1k searches | Semantic discovery | ❌ |
| Serper | ❌ None | $1/1k (50k min $50) | Google results | ❌ |
| Perplexity | ❌ None | $5/1k (Search API) | Q&A with citations | ✅ Sonar models |

---

## Tavily

| Plan | Price | Credits | Notes |
|------|-------|---------|-------|
| Free (Researcher) | $0/mo | 1,000/mo | No credit card, email support |
| Pay As You Go | $0.008/credit | Flexible | Cancel anytime |
| Project | ~$30/mo (slider) | 4,000+/mo | Higher rate limits |
| Enterprise | Custom | Custom | SLA + security |

- 1 credit ≈ 1 search request
- Student program: free for verified students
- URL: https://tavily.com/pricing

## Serper

| Plan | Price | Credits | Per-1k | QPS |
|------|-------|---------|--------|-----|
| Starter | $50 | 50,000 | $1.00 | 50 |
| Standard | $375 | 500,000 | $0.75 | 100 |
| Scale | $1,250 | 2,500,000 | $0.50 | 200 |
| Ultimate | $3,750 | 12,500,000 | $0.30 | 300 |

- No free tier — must prepay
- Credits valid 6 months
- URL: https://serper.dev

## Exa

### Per-product pricing (per 1,000 requests, up to 10 results each)

| Product | Price | Description |
|---------|-------|-------------|
| Search | $7 | Real-time search |
| Contents | $1/1k pages | Full page content extraction |
| Deep Search | $12–15 | Multi-step research workflows |
| Monitors | $15 | Track new events across web |
| Answer | $5 | Direct-answer queries |
| Agent | $0.012–$1.00/run | Async deep research (effort-based) |

### Agent mode details

| Component | Price |
|-----------|-------|
| Agent Compute Units | $0.10/ACU |
| Search tool calls | $0.005/search |
| Email enrichment | $0.02/email |
| Phone enrichment | $0.07/phone |

Fixed effort modes: Minimal $0.012, Low $0.025, Medium $0.10, High $0.50, X-high $1.00 per request.

- Free: $1,000 worth of credits for startups/education
- URL: https://exa.ai/pricing

## Perplexity

### Search API (pure search, no LLM)

| API | Price/1k requests |
|-----|-------------------|
| Search API | $5.00 |

No token costs — charges per request only.

### Sonar models (search + LLM answer)

| Model | Input/1M | Output/1M | Citation/1M | Search/1k | Reasoning/1M |
|-------|----------|-----------|-------------|-----------|-------------|
| Sonar | $1 | $1 | — | — | — |
| Sonar Pro | $3 | $15 | — | — | — |
| Sonar Reasoning Pro | $2 | $8 | — | — | $3 |
| Sonar Deep Research | $2 | $8 | $2 | $5 | $3 |

### Request fee by search context size (per 1k)

| Model | Low | Medium | High |
|-------|-----|--------|------|
| Sonar | $5 | $8 | $12 |
| Sonar Pro | $6 | $10 | $14 |
| Sonar Reasoning Pro | $6 | $10 | $14 |

- Low = fastest/cheapest, High = maximum search depth
- Deep Research single request: ~$0.41 (low) to ~$1.32 (high) all-in
- URL: https://docs.perplexity.ai/guides/pricing

---

## Configuring in Hermes

Add API keys to `~/.hermes/.env`:

```
TAVILY_API_KEY=tvly-xxxxx
SERPER_API_KEY=xxxxx
EXA_API_KEY=xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx
```

The `web-search` skill's multi-engine router auto-detects which keys are set and routes accordingly. No config.yaml change needed.