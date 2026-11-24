# Neuma 简报站 + AI 快讯 pipeline

Projects (not git repos; back up as `*.bak-<date>` before edits):
- `~/HermesWork/personal/news/neuma-briefing/` — 简报站 news.neumabio.xyz. Cron reads `cron-prompt.md`; job 6af8733ab925 (daily 06:00).
- `~/HermesWork/personal/media/ai-tietu/` — 公众号贴图 (`cron-prompt.md`, 10:15) and 长文 (`cron-prompt-longform.md`, 10:45).

## 简报 commands (`scripts/briefing.py`)

| Command | What it does |
|---|---|
| `leads DATE` | Horizon 多源雷达精选（当日 run，score ≥6，带摘要/选题角度/社区讨论）置顶 + HN 48h AI stories >100 points + official/media RSS → `data/DATE.leads.md` (topic hints only) |
| `codexiq DATE` | Codex Radar metrics → `data/DATE.codexiq.json` |
| `validate DATE` | schema + per-section freshness (`MAX_AGE_DAYS` ai 3 / pharma 7 / women40 90) + link liveness (404/410 fail, 403/429 WARN) + `grounding.py check` on each sidecar |
| `publish DATE` | validate → `grounding.py review` (refuses on FAIL) → merge → POST `/api/update` → read back `/api/day/DATE`; success only on `PUBLISHED` |

Sidecars: `data/DATE.{ai,women40,pharma}.json`, each item with `evidence`/`derived`; `MIN_ITEMS = 6`. Emergency-only overrides (never in cron): `BRIEFING_GROUNDING_SKIP=women40,pharma`, `BRIEFING_REVIEW=0`.

Verify live: `curl -s -A 'Mozilla/5.0' https://news.neumabio.xyz/api/day/DATE` → `updatedAt` + per-section counts (page paths return SPA HTML).

## 贴图 / 长文

- Input script `~/.hermes/scripts/neumabio-ai-hot.py` prints the site's AI items plus the local sidecar's evidence quotes; the Chinese summaries are leads only.
- `post.json` must carry `evidence`; 长文 writes `<dir>/evidence.json`.
- `ai-tietu/gate.py` runs `grounding.py check` + `review`; it is called at the start of `render.py` and `article.py draft`, which exit on `GROUNDING GATE BLOCKED`. `GROUNDING_GATE=0` is emergency-only.
- `article.py draft` writes `ab/longform-ledger.csv` rows itself and prints `RECEIPT draft_media_id=…`; the agent must copy that line and never hand-write the ledger or an ID.
- 贴图 also go to the 公众号 草稿箱 (user requirement): `tietu_draft.py <post dir> ...` gates via `gate.py`, uploads the rendered `<theme>/0N-*.png` as permanent material (`material/add_material?type=image`), then `draft/add` with `article_type: "newspic"`, `content` = caption.txt (plain text), `image_info.image_list[].image_media_id` (≤20 images, first = cover; per WeChat official 新增草稿 doc). One draft per post; prints `RECEIPT tietu=… draft_media_id=…` and writes it back to post.json. Title = post title with `**`/newlines stripped, ≤32 chars.
- After the user says they published: set the posts' `status` to `published` (the tietu queue gate counts `draft` posts and blocks at ≥6), then list the draft box (`draft/batchget`) to confirm what is left.
- Draft-box cleanup: match drafts by title, delete with `draft/delete {media_id}`, re-list to confirm. Deleting a draft does not touch an already-published article (published deletion is a separate `freepublish/delete` API). Confirm with the user which drafts are stale before deleting; never delete by position.
- WeChat API calls need the whitelisted proxy path; an SSL EOF on `stable_token` means the draft step did not run. Surge 的主 profile 若带 `#!MANAGED-CONFIG`（订阅每 24h 刷新）不能直接改，把 `DOMAIN,api.weixin.qq.com,<白名单节点>` 写进独立 `.sgmodule` 再 reload，用 `surge-cli rule explain` 验命中（详见 md2wechat 技能 `references/workflows-and-pitfalls.md` 陷阱 1）。
- 推完必须用 `python3 article.py check` 回读草稿箱确认在列（当日贴图 + 长文各一条，带标题与 `draft_media_id`），再把 media_id 回填 `brief.md` 与台账；`article.py draft` 打印的 `RECEIPT` 与 `check` 列表对得上才算推到，别只报 RECEIPT。

## Downstream rule

A bad briefing item propagates into that morning's 贴图/长文 drafts. After correcting the briefing, list the same-day drafts, re-run `grounding.py check/review` on them, and tell the user which ones not to publish.

## Upstream decision

No pipeline uses the x-pulse digest (or any other LLM-written digest) as a fact base; leads come from `briefing.py leads`, facts from fetched originals.

`briefing.py leads` 的第一段现在是 Horizon 本地雷达（`~/HermesWork/personal/news/Horizon`，`_horizon_leads()`）：它复用当日 `data/mcp-runs/` 产物或现跑管线，只贡献**线索**（AI 摘要 + HN/Reddit 社区争议 + 原始链接），落地与部署细节见 content-pipeline 技能的 `references/horizon-radar.md`。它的摘要一律按线索处理，入稿前仍要 `grounding.py fetch` 原文；管线失败时该段静默为空，不阻断其余信源。
