# Subscription price dataset: reading the local snapshot instead of re-scraping

A JSON snapshot of a third-party "real price" board (monthly fee ÷ saturated monthly tokens, per plan × model) is already on disk from prior runs. Read it before scraping anything: it answers "what does one million tokens of model M cost on plan P, and what does a coding task cost" in one query, with the confidence label the board itself assigns.

Find it under `~/HermesWork/抖音科普视频/_research/S2-sources/real-api-pricing-site-*.json` (newest date wins) or `~/.hermes/cache/`. Check `generatedAt` first — a stale snapshot silently reframes the whole comparison.

## Shape

```python
import json
d = json.load(open(path))          # generatedAt: 'YYYY-MM-DD'
for p in d['points']:
    p['label']            # 'Claude Opus 5.5 · Droid Max'
    p['plan'], p['model'], p['vendor']
    p['price_usd']        # monthly fee of the plan
    p['monthly_yi']       # saturated monthly tokens, in 亿 (1e8)
    p['real_usd_per_mtok']# THE ranking number: $ per 1M tokens
    p['confidence']       # 'high' | 'medium' | 'low' — low = one community screenshot
    p['source'], p['data_date'], p['promo_until']
for c in d['configurations']:     # coding-agent leaderboard rows
    c['board']            # 'aa_coding_agent_index'
    c['variant']          # 'Claude Code - Opus 5.5 (max)'
    c['score'], c['mean_cost_usd_per_task']
```

Rank by `real_usd_per_mtok`. Do not compare `monthly_yi` across plans — a plan with more allowance can still be far worse per dollar for a given model.

## Rules that keep the table honest

- **Filter by model first, then rank.** "Cheapest plan" is meaningless; "cheapest per unit of model M" is the question. The same vendor can be cheapest for one model and 15× worst for another.
- **Carry `confidence` into the sentence.** A `low` row is one person's screenshot of a usage screen; quote it as "one user's report", never as the plan's spec.
- **A third-party CLI plan can beat the vendor's own subscription for cost and still lose on access.** Report the cost axis on its own line and put the access/region question in a separate sentence — they are different decisions.
- **The leaderboard's `mean_cost_usd_per_task` is a cost-per-task number, not a value score.** A tool scoring 66 at $13/task is not "5% better" than one scoring 62.9 at $1/task; write both axes.
- **Do not synthesize a row that is missing.** Plan × model cells the snapshot omits stay blank; some rows are derived from a sibling model by a stated multiplier (the `source` field says so) — that derivation is the board's, not yours, so label it.

## Scraping fallbacks

- Vendor pricing pages: `web_extract` returns the tier table intact. `r.jina.ai` proxies of the same page drop the tabular pricing block and leave the feature bullets — if a pricing page comes back with plans but no numbers, the reader stripped the table, not the site.
- The `web_extract` result is cached as `~/.hermes/cache/web/<host>-<hash>.cache.md`; grep that cache by a phrase from the page (`grep -l "<phrase>" ~/.hermes/cache/web/*.md`) instead of re-fetching a page whose proxy output came back mangled.
- Vendor policy pages (region availability, plan terms) go through `r.jina.ai` better than pricing pages do, and their exact wording is what a compliance claim must rest on — quote the sentence, including whether resellers are covered.
