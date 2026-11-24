# Coding-agent subscription plans: which ones serve a given frontier model, and how much

A snapshot, not a source of truth. Every number here was read off the vendor's own docs page. Plans and per-model caps change monthly, and introductory model pricing has hard end dates — re-open the URLs below before quoting any figure in a deliverable, and re-stamp the date.

Snapshot taken: 2026-11-12.

## The two pages that settle each vendor

| Page kind | What it holds | What it never holds |
| --- | --- | --- |
| Model detail page (`<vendor>/models/<model>`) | list price, context, benchmark score, entry tier ("runs on Pro and up"), a usage calculator | the per-model monthly dollar cap |
| Plan docs page (`<vendor>/docs/plans/<tier>` or `/docs/resources/pricing-limits`) | entry price, monthly allowance, per-model cap, 5h/weekly windows, which premium models are gated to Max | the model's own benchmark/pricing context |

Read both for every candidate. The model page alone makes two plans look identical when the plan page shows different caps for two models of the same list price.

## Index first

- `models.dev/models/<lab>/<model>` — e.g. `models.dev/models/google/gemini-4-argon`. Lists 30+ providers including subscription-plan providers (OpenCode Go, GitHub Copilot, Command Code, Devin, Vercel AI Gateway, Vertex, OpenRouter). Fastest way to enumerate who serves the model at all.
- `models.dev` says nothing about tier gating or included allowance. Treat it as a phone book, not a price list.
- Aggregators that answer "is it in a flat-rate plan, cheapest being X" exist (`sovyron.com/models/<model>`) — they are copies of models.dev with a different cut. Use to spot a candidate you missed, never to source the number.

## Command Code (commandcode.ai)

Subscription plans, all credit-bucket:

| Plan | Price/mo | Credits/mo | 5h window | Weekly | Notes |
| --- | --- | --- | --- | --- | --- |
| Go | $1 | $10 | $2 | $5 | open models only |
| GOAT | $10 | up to $100 | up to $20 | up to $50 | open models + some closed per-model allowances |
| Pro | $20 | up to $110 | up to $22 | up to $55 | first tier with frontier models |
| Max 10× | $100 | $150 | $45 | $90 | standard $150 / premium $100 split |
| Max 20× | $200 | $300 | $90 | $180 | standard $300 / premium $200 split |
| Provider | $15 + PAYG | — | — | — | OpenAI/Anthropic-compatible endpoints, zero markup |
| Teams | $40 | — | $12 | $24 | pooled bucket |

**Per-model caps on Pro** — this is the part the model page hides. Most Claude/GPT/Gemini models get **$20/mo each**, but the cap is assigned per model and can differ: one Gemini 4 variant sat at $30 while its identically-priced sibling sat at $20. Claude Opus / Fable / Fugu Ultra require Max or the Provider API.

**Premium vs standard on Max is decided by billing category, not branding.** Some models marketed as premium bill against the standard limit. Read the page, do not infer from the name.

**Reference request cost** they publish: $0.0084/request, from 800 in / 180 out / 50K cache-read tokens. That is the only legitimate basis for turning the dollar allowance into a request count.

Docs: `commandcode.ai/docs/resources/pricing-limits`, `commandcode.ai/docs/plans/pro`, `commandcode.ai/docs/plans/max`.

## OpenCode Go (opencode.ai)

| Plan | Price/mo | Notes |
| --- | --- | --- |
| Go | $10 | single-member workspace |
| Go Plus | $40 | higher limits, same token prices |
| Go Teams | $20/member/mo | per-member limits, each ~$5 above Go on every model |

**Window math is stated explicitly:** 5h = 20% of that model's monthly limit, weekly = 50%, monthly = 100%. Every response reports its own consumption as `opencode.allowance`.

Allowances are **per model, in dollars**, and they are NOT proportional to the model's price — a cheap model can carry a bigger bucket than a premium one. Read the model row, never extrapolate from a sibling row or a plan tab.

**Client requirements:** the API expects coding-agent traffic, a real user agent, and a stable `x-opencode-session` header per conversation (it drives routing and prompt caching). Hermes needs v0.21.6+ which sends it on main and auxiliary requests. If a client drops the header, caching degrades and the allowance burns faster — a "the plan gives less than advertised" report is usually this, not the plan.

**Restricted models:** DeepSeek V4.x and some contributor models need Region = Global in Settings › Privacy; Meta contributor models need the "allow paid endpoints that train on request data" toggle.

Docs: `opencode.ai/docs/console/go` (per-model table lives in the PlanTabs HTML — read the raw file, the tabbed markdown drops the non-default tabs), `opencode.ai/console/go` (relative request allowances + est. requests per 5h).

## Editors: available ≠ included

- **Cursor** — frontier third-party models are explicitly *outside* plan usage: billed from prepaid credit on the X Subscription, or drawn from the legacy "Other Models" pool. A $20/mo editor subscription does not buy one token of them. Docs: `cursor.com/docs/models/<model>`.
- **GitHub Copilot** — the model appears in the picker and counts against the plan, but the binding constraint is the request/rate multiplier, not a dollar bucket. Cheapest entry to a frontier model for light interactive use; the wrong tool for a long agent pipeline.
- **Devin Desktop / CLI (ex-Windsurf)** — model is in the picker and draws on the plan's quota / ACU balance. Quota is dollar-denominated at each model's own token rate, so it *is* convertible to a token count — see the Devin section below.

## Devin (Desktop / CLI / Cloud)

- **额度单位是美元，按每个模型自己的单价扣。** 日 + 周（Max 只有周额度、无日上限）。docs 原文：lead and sidekick tokens draw down your quota at each model's own per-token rate。所以这个档位可以折成 token 数，别被「task points」的描述误导。
- **额度大小不公布**（只写「significantly larger」）。只能实测反推，方法见 `references/quota-to-token-budget.md`。量级参考：Max 周额度约 $300、Pro 约 $30/周（$15/日）—— 引用前重测，这档被下调过不止一次，旧快照会高出一倍。
- **Fusion 是双模型配对，不是单一模型。** 默认 lead = Opus 5.5 Medium，sidekick = SWE-2 Medium。harness 指令是按每个 pair 单独调的，换 lead 不是等价替换。lead 资格以 picker 为准：docs 只给默认组合，只有被显式标注「as a Fusion lead」的模型才算确认。
- **免费模型只免单价，不免限流。** SWE-2 在 Desktop/CLI 对 Pro/Max/Teams 免费（公告称永久，docs 仍写期限 —— 两个口径都报）；SWE-2 Flash 有独立免费期后转 $0.10/$0.50。社区有免费模型被单独限流的反馈，别把「免费」读成「不限量」。
- **两个吃额度的隐藏项：** 长会话缓存过期后命中率掉到 10% 以下（官方建议新开 session）；Windows 会话比 Linux 多约 9%。
- **外接 ChatGPT 计划**：GPT 用量可走 ChatGPT 订阅不占额度，但经 Devin 走会收缓存写入费，断连还会回落到 Devin 额度 —— 别当主路径。
- 「同样工作额度变少」的体感通常是三件事叠加：额度下调 + 缓存掉档 + 计量口径不公开。归因时分开说，别一律归给「厂商砍额度」。

## Devin Fusion：lead 选谁（2026-11 快照）

Fusion 按各自单价扣额度，所以 lead 的选择直接决定每任务成本。AA Coding Agent Index v2.1（2026-11-13，322 任务）给出的 per-task API 成本（不是订阅价）：

| 配置 | Index | $/任务 | token/任务 | 备注 |
|---|---|---|---|---|
| Claude Code + Fable 5.2 high | 58.2 | $7.51 | 5.12M | 与 Opus 5.5 max 同分，便宜 40% |
| Claude Code + Fable 5.2 xhigh | 58.5 | $15.47 | 9.75M | 分数只高 0.3，贵一倍 |
| Claude Code + Fable 5.2 max | 55.7 | $44.22 | — | **更贵反而更低**：更多尝试撞时间上限 |
| Claude Code + Opus 5.5 max | 58.2 | $12.61 | 15.9M | |
| Claude Code + Sonnet 5.5 max | 56.3 | $11.40 | 26.4M | 便宜的是单价，不是每任务 |
| Devin Fusion + Opus 5.5 max + Luna high | 58.4 | $8.75 | 12.4M | AA 唯一测过的 Fusion 组合 |

三条可复用的判断：

- **弱模型不一定省钱**：Sonnet 5.5 单价比 Opus 便宜一半，但每任务多烧 66% token（26.4M vs 15.9M），折成额度只省约 17%，还掉 2 分。谈「用便宜模型省额度」时先算每任务 token，不要比单价。
- **Fable 5.2 对 5.1 是全面碾压**：Devin 单价 $8/$40 对 $10/$50（-20%），FrontierCode 2.0 49.1% 对 32.4%，AA 每任务 $7.51 对 $11.70。不存在「贵一点但更好」的权衡。
- **effort 不是越大越好**：Fable 5.2 在 max 上分数掉到 55.7 且成本 6 倍；Cognition 自己的 FrontierCode 也验证同一现象。选 lead 时固定 high。
- **benchmark 的 per-task 价格不通用**：AA 测出 Fable 5.2 high $7.51/任务（比 Opus 5.5 max 便宜 40%），但 SemiAnalysis 在 GDPx 上测到 5.2 反而比 5.1 贵 31%（$88.15 vs $67.16）—— 因为 5.2 更爱多写测试、起子 agent 自检。判断 lead 便宜与否要看自己工作负载里“验证/自检”的占比。
- **Fusion 的免费 sidekick 有边界**：SWE-2 免费只限 Desktop/CLI 本地会话（Devin Cloud 里只是打折），且社区实测有小时级限流（“Reached free model rate limit，10 分钟重置”），6 个并发就能打满。

社区证据（2026-11，Reddit/X/linux.do）：Fable 5.2 上线一周还没有“Fable 5.2 + SWE-2 当主力”的公开长期报告；有量化的只有一条——medium effort 下 40M token 吃掉 Pro 93% 的日额度。主流 Fusion 组合仍是 GPT-6 Astra + SWE-2 和 Opus 5.5 + SWE-2（默认）。KOL/大使口径分歧：有人称 5.2 在 Devin 上“烧额度很快、对比 Codex 无优势”。

Fusion 的 lead 只在规划/审阅上花钱（默认 Opus 5.5 Medium + SWE-2 Medium，实测 token 分配约 54/46），所以「换更会授权的 lead」比「换更聪明的 lead」更容易省钱。
- **有跨厂商 review 兜底时，lead 可以選更便宜的**：如果用户习惯拿另一家的模型（Gemini/GPT）审 diff 作为最终闸门，Fusion lead 只承担规划和第一轮 review，lead 的边际智能度就不敏感——此时选 Fable 5.2 high（或更便宜的 lead）而不是 Opus max，风险小于没兜底时。反过来，review 一定要走便宜通道（flat 订阅或 cache-read 便宜的模型），别用 lead 同一模型再审一遍。

## Google's own subscription is usually the answer first

For Gemini models, the lab's consumer plan gives native access on several surfaces at no extra per-token cost:

| Plan | Price/mo | Argon | Carbon | Antigravity | AI Studio |
| --- | --- | --- | --- | --- | --- |
| AI Plus | $4.99 | — | — | — | — |
| AI Pro | $19.99 | yes (4× free limits) | — | Argon needs Ultra | Argon with expanded limits |
| AI Ultra 5× | $99.99 | highest | highest | yes | yes |
| AI Ultra 20× | $199.99 | highest | highest | yes | yes |

So when the user asks "what subscription can run model X" and X is from a lab whose consumer plan they may already hold, check that first. Recommending a $10–20/mo third-party bucket to someone already on the lab's top tier is a duplicate purchase.

## Introductory pricing has an end date — the allowance halves with it

Model list prices in this segment launch on promo and revert:

- Gemini 4 Argon / Carbon: **$2 / $10 / cache $0.10** per 1M through **2026-11-30**, then **$4 / $20 / cache $0.20** from 2026-12-01. Batch tier at 50% off ($1 / $5). No free tier. Implicit cache only.
- OpenCode marks its Argon row as "50% off through November 30, 2026" — the discount is on the vendor's price table, not a separate coupon.

Consequence for every dollar-denominated allowance: the same $20–30 monthly cap buys **half the requests** after the revert date. Print both figures, or at minimum name the date and the post-revert price in the conclusion. A table stamped "today" without this note reads as a permanent number.
