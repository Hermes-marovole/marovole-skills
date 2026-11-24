# LLM Reality Rank Project Scaffold Reference

Session-derived reusable pattern for building a public, source-backed comprehensive LLM leaderboard.

## Recommended project name

- Repository: `llm-reality-rank`
- Public name: `LLM Reality Rank / 大模型真实使用价值榜`
- Positioning: not an "absolute strongest model" list, but a transparent "综合使用价值榜" with scenario sub-rankings.

## Repository shape

```text
README.md
LICENSE
.gitignore

docs/
  llm-reality-rank-source-registry.md
  llm-reality-rank-scoring-methodology.md
  llm-reality-rank-model-normalization.md
  llm-reality-rank-scoring-pipeline-plan.md

data/llm-reality-rank/
  sources.yaml
  models.yaml
  raw_rankings.csv

scripts/llm-reality-rank/
  validate_data.py

outputs/llm-reality-rank/
  .gitkeep

tests/llm-reality-rank/
  .gitkeep
```

## Data layer contracts

### `sources.yaml`

Machine-readable source registry. Include for each source:

- `source_id`
- `priority`: P0 / P1 / P2
- `name`
- `urls`
- `organization`
- `categories`
- `metric_types`
- `source_trust`
- `contamination_risk`
- `recommended_weight`
- `update_frequency`
- `use_in`
- `ingestion_method`
- `notes`

### `models.yaml`

Canonical model registry. Include:

- `canonical_id`, e.g. `anthropic/claude-3.5-sonnet@2024-10-22`
- `display_name`
- `provider`, `provider_slug`
- `model_family`, `model_variant`, `version`, `release_date`
- `model_type`, `access_type`, `license_type`
- `context_window`, `modality`
- tool/structured-output/multimodal support flags
- `api_model_ids`
- `aliases`
- `match_confidence`
- `notes`

If a version is unknown, use `@unknown`, set `match_confidence: low`, and avoid treating it as publication-grade.

### `raw_rankings.csv`

Start with P0 source template rows. Columns:

```csv
source_id,source_name,source_priority,category_primary,metric_name,metric_type,model_name_raw,canonical_id,provider,rank_raw,score_raw,score_unit,score_higher_is_better,date_published,date_observed,source_url,evaluation_independence,source_trust,contamination_risk,freshness_weight,notes
```

Keep TODO rows clearly marked. Do not cite TODO rows as ranking conclusions.

## Validation script

Minimal `scripts/llm-reality-rank/validate_data.py` should:

1. Parse `sources.yaml` and `models.yaml` with PyYAML.
2. Assert required fields exist.
3. Assert unique `source_id` and `canonical_id`.
4. Parse `raw_rankings.csv`.
5. Assert every raw row references known `source_id` and `canonical_id`.
6. Assert `score_higher_is_better` is `true`, `false`, or empty.

Command:

```bash
python3 scripts/llm-reality-rank/validate_data.py
```

Expected:

```text
VALIDATION PASSED
```

## GitHub organization publishing pattern

When user says "Hermes&marovole" they likely mean org `Hermes-marovole`; verify org access via:

```bash
gh auth status
gh api user/orgs --jq '.[].login'
```

Create and push a new public repo from local folder:

```bash
git init -b main
git add .
git commit -m "Initial commit: add LLM Reality Rank foundation"
gh repo create Hermes-marovole/llm-reality-rank \
  --public \
  --description "LLM Reality Rank: 大模型真实使用价值榜 — transparent, source-backed LLM leaderboard methodology and data foundation" \
  --source . \
  --remote origin \
  --push
```

Verify remote:

```bash
gh repo view Hermes-marovole/llm-reality-rank --json nameWithOwner,url,visibility,defaultBranchRef,description
python3 scripts/llm-reality-rank/validate_data.py
```

## Pitfalls

- Do not call the main ranking "最强模型榜"; use "综合使用价值榜" to reduce false precision and debate.
- Do not mix ability signals with adoption/price/speed. OpenRouter usage, pricing, context, and TPS are practicality/ecosystem signals, not raw capability.
- Do not merge model variants: mini/full, pro/flash, base/instruct, preview/stable, dated API snapshots, and reasoning/non-reasoning variants should usually be separate.
- Do not over-automate first. Build docs + data contracts + validator first, then normalize/aggregate after real P0 numeric rows are collected.
- Treat厂商自报 benchmark as `vendor_reported` and downweight.
