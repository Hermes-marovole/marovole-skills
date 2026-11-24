---
name: ai-research-comparison
description: "Use when comparing AI model or tool prices and benchmarks."
category: research
tags: [comparison, benchmark, model-evaluation, tool-shootout, AI, content-production]
trigger: ["模型对比", "model comparison", "tool comparison", "benchmark", "对比表", "AI工具对比", "vibe coding 工具", "model ranking", "哪个模型更好", "哪个更适合", "测速", "哪个快", "provider 速度", "TTFT", "哪个订阅", "订阅能用多少", "还有什么订阅能用", "subscription coverage", "plan allowance", "plan quota", "订阅划不划算", "买还是自建", "该采购还是自研", "值不值得采购", "值不值得买", "这产品能不能干", "产品能力实测", "这个模型能力如何", "新模型实测", "这个 model 做X的能力", "demo 是真的吗", "演示视频 评估", "宣称能力", "调研一下 <发布公告链接>", "真的开源吗", "全面开源", "发布会 发了几个模型", "权重有没有发", "open weights 核验"]
---

# AI Research Comparison

Structured comparison workflows for AI models and tools. Seven modes: **model deep-dives** (capabilities, pricing, benchmarks), **tool shootouts** (feature matrices, scoring, content production), **自测线路速度** (same model, several providers/gateways — measured on the user's own link, not a public leaderboard), **第三方能力选型** (does an API/MCP actually do the job), **订阅可用性调研** (which subscription plans serve a given model, and how much each gives), and **买 vs 自建** (give a third-party AI product a real deep task and measure what comes out), and **Demo 宣称能力核验** (someone else's viral demo — is the capability the model's, the harness's, or an older model's).

Pick the mode from the question's shape, not the topic: "哪个模型好" → A, "做个对比图" → B, "哪条线快" → C, "有没有 API 能做" → D, "哪个订阅能用/能用多少" → E, "这产品能力如何/该采购还是自己做" → F, "这个新模型做 X 到底行不行/这条 demo 可信吗" → G.

---

## Mode A: Model Deep-Dive Comparison

When the user asks "which model is better for X" or requests benchmark analysis. 用户丢一条厂商发布公告链接 + 「调研一下」也走这里：先做交付物矩阵（谁真发了权重、谁只发编码器或代码），再谈分数。

### Step 1: Establish User Persona

Ask the user's role and daily workflow:

> "你的工作主要包含哪些类型？比如：写业务代码 / 做深度调研 / 写产品文档 / 跑数据分析……描述一下你每天的实际工作流。"

### Step 2: Data Sources (in priority order)

| Source | URL Pattern | Content |
|--------|-------------|---------|
| Artificial Analysis | `artificialanalysis.ai/models/{slug}` | Independent TPS, intelligence index, pricing |
| AA Providers | `.../models/{slug}/providers` | Turbo/optimized TPS per provider |
| DeepInfra Blog | `deepinfra.com/blog/...` | Provider-level TPS comparisons |
| LushBinary | `lushbinary.com/blog/` | Official benchmark tables |
| Kingy AI | `kingy.ai/category/ai/` | Architecture deep-dives |
| Fireworks Pricing | `fireworks.ai/pricing` | Third-party hosting costs |
| Official Benchmark | Model-specific pages | HLE, AIME, SWE, etc. |
| Bing Search | `bing.com/search?q=...` | Anti-CAPTCHA fallback |
| Community (V2EX/Reddit) | Real user reports | Latency, throttling, compatibility |

**Anti-CAPTCHA strategy:** Directly navigate to known data pages. Never search-first when you already know the URL.

### Step 3: Multi-Model Routing Strategy

If the user subscribes to multiple services, recommend a **layered model stack**:

```yaml
model:                    # Main session — daily fast tasks
  default: deepseek-v4-flash
  provider: opencode-go

delegation:               # Subagents — complex reasoning
  model: kimi-k2p5-turbo
  provider: firepass
  max_iterations: 100
```

**Typical stack:** Fire Pass ($28/mo Kimi K2.5 Turbo unlimited) + OpenCode Go ($10/mo DS V4 Flash/Pro) = $38/mo for full spectrum.

### Step 4: Output Format

```markdown
# [Model A] vs [Model B] Report

## Base Specs
| Dimension | Model A | Model B |
|-----------|---------|---------|
| Params | ... | ... |
| Context | ... | ... |
| TPS | ... | ... |
| Price/M | ... | ... |

## Benchmarks
| Task | Model A | Model B | Note |
|------|---------|---------|------|
| MMLU-Pro | ... | ... | Knowledge |
| LiveCodeBench | ... | ... | Coding |
| GPQA Diamond | ... | ... | Reasoning |

## Recommendations by Scenario
| Scenario | Pick | Why |
|----------|------|-----|

## Sources + Confidence
```

**Pitfalls:**
- Always check `/providers` page for Turbo TPS (main model page shows standard)
- Mark vendor-reported benchmarks with lower confidence
- For models < 3 days old, note limited independent data
- Use community reports for real-world latency/throttling info
- **发布首日先跑实时探针，别从新闻稿取事实**：订阅端点与通用端点的 `/v1/models` 各打一次、`models.dev/api.json`、`openrouter.ai/api/v1/models`、`docs…/llms.txt`、官方 blog/model card 的状态码、HF 组织页。冲突时按「接口返回 > 官方文档 > 实时镜像 > 控制台标签 > 媒体」取，媒体最快的错法是把上下文窗口写错一个量级。
- **榜单标题分与同口径分并列写进表**：早期内测榜普遍用「澄清提示词重跑」加分、「自评 + 对手评混合」打分，同提示词分常压在脚注里（标题 33.2 对应同题 31.8 这种差值很常见）。评分者名单与 `*`/`†` 脚注一起写进表注，否则读者拿两个不可比的分数在比模型。
- **「#1 Open Model」是榜单分栏，不是开源事实**：查 `open_weights`、HF 仓库、OpenRouter 路由、ModelScope 镜像，缺任一处就写「榜单归入开源阵营，权重未发」。
- **「全面开源」要按模型逐个验，并落进交付物矩阵**：一个家族发布会里同时会出现「完整权重 / 量化版 / 只发编码器 / 只发代码+评测集 / 全闭源」五种桶，媒体会把它们统一写成开源。只发编码器的那行必须点出「任务预测头未包含」，只在 API 后面的那行必须点出厂商依赖——把宣传里的能力数当交付是最常见的一处失真。
- **硬件门槛读模型卡的推理配方，不读「可在笔记本部署」**：卡片里 `--tp 4/8` 加 GPU 型号是事实，宣传语常差一个数量级；同时区分量化版能跑与浮点版推荐配置。
- **「SOTA」拆成「开源第 1」与「综合第 N」两个格子，并查指数的覆盖缺口**：自评基准图要 `vision_analyze` 读原图逐格取数（转述会漏掉落败项），第三方综合指数先看它只覆盖了评测矩阵的第几格、有没有整列空缺，再决定能不能当全景排名引用。
- **限免 API 是零成本实测入口，但要写截止日**：厂商 MaaS 模型页给单价 / 上下文 / P50 吞吐 / TTFT / 可用率，正适合先跑自家样本；限免期常只到发布会后几天，不写日期就是给用户一个会过期的方案。
- **聚合站给新模型挂的超低价常是占位**：若它同时与页面上标「Coming Soon」的下一代模型完全同价，就不能拿来做预算，退回上一代官方价做对照情景。
- **「慢」先拆首字延迟 / 单步耗时 / 总步数 / 推理 token，再谈 TPS**：多数新推理模型的耗时膨胀来自步数与 token，不是吐字速度；用同一批短任务在低/高档位各跑一次限时探针，能直接照出档位行为倒挂。

探针命令、榜单口径审计四问、额度措辞误读、「机制 vs 遥测」分栏写法，以及家族发布的交付物矩阵（五种桶）、硬件门槛与综合指数覆盖缺口：`references/model-release-factcheck.md`。

---

## Mode B: Tool Comparison Table (Kill-the-Wolf Style)

High-density comparison tables for X/Twitter and newsletter publication.

### Workflow
1. Pick a domain (Vibe Coding tools, LLM APIs, AI image generators)
2. Define 6-8 evaluation dimensions (ease of use, output quality, maintenance, cost, freedom, best audience)
3. Score each tool 1-10
4. Build visual table: heat bars, color coding, winner badges
5. Screenshot with headless Chrome
6. Write X post/thread copy
7. Publish and track engagement

### HTML Screenshot Pipeline
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1280,4300 \
  --screenshot=/path/to/output.png \
  "file:///path/to/comparison-table.html"
```
Headless Chrome captures the window height, not the document height, so a long table gets clipped or padded with blank canvas. Overshoot the window, then crop to the last non-background row (scan PNG scanlines for the last row brighter than the page background) and rewrite the file in place. `vision_analyze` downscales tall images hard enough to hide both the blank tail and clipped text — use it for layout, not for measuring height.

### Table Design
- Dark background `#0a0a0f`, secondary text `#94a3b8` (never `#64748b`)
- Container `1200–1280px` (X/Twitter long-image), rendered at 2x
- Heat bars: `linear-gradient` + fixed-width tracks
- Color: green=included/strong, yellow=available but metered, red=absent
- One "core insight" — a contradiction readers didn't expect
- Data source tags at the bottom, with the date the pages were opened

### Pricing and quota tables
- Split rows by billing unit before comparing them. A rolling-window allowance, a dollar credit, and a per-token rate are three columns, not one ranking.
- When the vendor publishes no message or token count, print the multiplier they do publish and say the count is unpublished. Do not backfill a count from community estimates or older archived help pages — those survive plan renames and limit raises, and a reader treats a number in the table as official.
- Verify model availability per tier from the vendor's own model matrix. A plan that lists "frontier models" often gates the newest one to a higher tier, or bills it from the first request outside the included pool. Third-party comparison sites copy each other's stale tier names.
- Rendered docs hide availability in icon `aria-label`s. Fetch the HTML and read those labels; markdown extraction drops the checkmarks and every cell looks blank.
- Exclude gray-market resellers (account rental, shared seats, top-up shops). Their price is not the vendor's price and their quota is unverifiable.
- A third-party "real price" dataset (monthly fee ÷ saturated monthly tokens) is usable, but only as its own section, never merged into the vendor-published column. Copy its snapshot date, confidence label, and workload convention next to the number. Two traps: the dataset keeps a plan's old name after the vendor renames it, and its allowance cutoff predates later limit raises — note both rather than silently relabeling. A plan × model cell the dataset does not contain stays blank; do not interpolate it from a sibling tier.
- In a multi-model plan, the quota is denominated in the plan's own units and each model carries a billing multiplier (one model at 1.6× another model's 0.8× of the same allowance). Convert to cost-per-model through that multiplier before ranking plans: comparing list API prices across a switcher plan produces the wrong winner, and the plan that looks cheapest on list price can be twice as expensive per unit of the model the user actually wants. Vendor pricing page + vendor model matrix are the two pages that settle it.
- When the user names a "cheapest / best value" option, rank it against the same model on the other plans before agreeing. A plan can win on flexibility, team seats, or model breadth and still lose badly on per-token cost of the one model the content is about; say which axis it actually wins on. See `references/subscription-price-dataset.md` for the snapshot file that answers this without new scraping.
- Recompute every derived ratio (plan A vs plan B, subscription vs list price) from the two source numbers before it goes in a cell. A ratio copied from a different model row in the same table looks plausible and is wrong.
- When the user has the subscription, their own account beats every dataset. A "real price" number is an estimate of a saturated month; the user's logs are the month. If the two disagree, report the measured figure and say which assumption in the estimate failed — do not defend the table against the account holder. See `references/local-usage-logs.md` for reading Factory/Droid and Claude Code logs on this machine.
- Attribute usage to a model before summing it. A streaming-result line often carries token counts but no model, while the model id lives on a different line of the same session; join on session id. And a "usage restored" record is a running cumulative total for that session, so summing those lines across a log multi-counts the same tokens — take the max per session, or sum the per-request lines instead.

### X Post Flywheel
| Phase | Action | Frequency |
|-------|--------|-----------|
| Warm-up | Poll for tool preference | Weekly |
| Publish | Screenshot + 3-line copy | Every 2 weeks |
| Engage | Reply to comments, add columns | Continuous |
| Archive | Full article/Newsletter | Monthly |
| Update | Re-publish with new data | Quarterly |

### Pitfalls
- Screenshot height — measure the PNG and crop (see the pipeline above); a vision pass on the downscaled image cannot tell a blank tail from a clipped row. The mirror error is just as common: a row cut by the viewport edge gets read as "this cell's text is clipped" — a screenshot cannot distinguish "continues below the fold" from "overflows the cell". Settle it in the page with `td.scrollHeight > td.clientHeight + 1` (also `table.scrollWidth > table.clientWidth` for horizontal overflow) before changing any width or padding.
- Low secondary text contrast on dark backgrounds — use `#94a3b8` not `#64748b`
- Data expiry — AI tools change in 4-6 weeks; always date-stamp
- First issue over-engineering — manually produce 3-5 tables before automating

---

## Mode C: 自测线路速度（同一模型，多条 provider / 中转）

用户说「我的两个 provider 哪个快」「测一下 X 和 Y 的速度」时，**不查公开榜，直接在本机网关上对拍**。
公开 TPS 是中转商机房里的数字，用户要的是自己这条链路现在的表现。

**「哪个快」和「哪个好」是两个问题。** 只答快慢会漏掉真正会咬人的差异：一边 422 不认某个参数、一边在紧预算下把预算烧在思考上、一边的输出在固定字面量处被切断。问「哪个好 / 哪个更适合我日常用」时，速度那套跑完再加下面第 7 步的质量臂。

1. **先确认两边是同一个模型、能通**：`curl -s http://127.0.0.1:3425/v1/models -H "Authorization: Bearer magpie"`，
   再用完整 `provider/model` 打一条 1-token 请求。magpie 对未列在 `/v1/models` 的路由也照样走，
   所以测速**不必**改 `providers.<name>.models`（那是让它可选，属配置改动，先问用户）。
2. **两条线都走同一个网关**。magpie 的 `providers.json` 把上游 key 打码，追真 key 是白费功夫；
   一边直连一边走网关还会把网关开销算成某一边的劣势。
3. **计时口径用「可见正文」**：`stream: true` + `stream_options.include_usage`，记首个**可见**字、
   前 100 / 300 字、全文完成。不要用 `completion_tokens / 总时长`——带思考的线路把
   `reasoning_content` 也计入 completion_tokens，同一提示词能多算近一倍 token，TPS 反而给它算高分。
4. **交替顺序、多轮取中位数**（≥4 轮，奇偶轮反转顺序）。网络尖峰比线路差异更大，报中位不报单次。
5. **用网关账本佐证归因**：`~/.config/magpie/usage.jsonl` 的 `ttft_ms` 是上游首 token（含思考），
   与客户端「首个可见字」对照，就能分辨「链路慢」还是「模型先想后说」。
6. **交付**：中位数表 + 谁快几倍 + 归因（链路 / 思考 / 输出长度）+ 一句选型建议 + 脚本路径。
   只给「A 快」不给原因，用户下一轮还得自己判断。
7. **质量臂：七题机器判分，两个预算。** 题库覆盖严格 JSON 抽取（带类型约束）、代码题 + 自写隐藏测试、
   长上下文埋码检索（≥4 万 token）、负约束写作（字数 + 禁词 + 必含词）、多步算术、固定字面量回显、
   400 字写作。质量题 `max_tokens` 给到 ≥2000；**再单独跑一组紧预算（约 900）只记完成率**，
   它衡量的是「会不会把预算烧在思考上」，本身就是一条有用指标，但绝不能和质量的格子混算。
8. **归因前先对拍另一条线路。** 某条线路出现输出损坏（字面量被切断、正文混进无关段落）时，
   同一个探针再打另一条；两边都断就说明问题在 checkpoint/推理栈，不是这一家的锅。
   只测一家会写出「避开某渠道」这种错结论，而它一翻原文就能被推翻。

直接跑 `scripts/provider_speed_test.py`；方法论、判读规则、质量臂题库（七题机器判分 + 两个预算口径）和踩过的坑见
`references/provider-speed-benchmark.md`。

---

## Mode D: 第三方能力选型（有没有 API / MCP 能做这件事）

用户问「有没有 API 或 MCP 能做 X」（识别、转写、OCR、抓取、支付、地图……）。这不是比价，是**能力采购**：先确认谁真的干活，再比钱。

0. **先确认用户给的对象是对的。** 用户常丢一个域名当作「那个产品」，同名不同公司极常见（一个做预约排期、一个做拍照算热量，都叫 Cal）。名字对上就往下做之前，打开页面确认业务是不是用户说的那件事；不是就直说，再纠正到对的目标上。
1. **先拆层，再找厂商。** 「照片 → 热量」实际是三层：感知（图 → 实体 + 份量）、数据（实体 → 数值）、编排（Agent 记账/查库）。多数厂商只做一层，宣称做全链的往往是把通用 VLM 拼起来。把这三层写出来再往厂商身上填，立刻能看出「便宜的那个其实只做了第一层的一半」。
2. **MCP 不等于厂商能力。** 托管 MCP 常常只是查库 + 记账，看图是宿主模型（Claude/GPT）干的。判定方法：读工具的 `inputSchema` —— 参数是 `image`（base64/URL）说明服务端做视觉；参数只有 `queries` / `food_name` / `text` 说明视觉在你这边。这条必须在结论里讲清，否则用户接完才发现「没有识图能力」。
3. **把计费单位归一到「一次用户动作」。** 按 token 计价的多模态能力要用厂商自己公布的「每次调用典型 token 数」折成单次成本，再去和按次计价的对手比；不折算就会得出「token 制更便宜」的错误结论。厂商没公布典型 token 数时，写明「无法折算」，不要用社区估值代填。
4. **官网状态 ≠ 接口状态。** 页面写「站点升级中」「仅对注册伙伴开放」「beta」都不构成「接口不可用/可用」的证据；打一次真实请求再下结论。反过来，官网写「即将上线」也不能当「没有 API」。
5. **同一页自相矛盾时两个口径都报。** 厂商常在标题写一个覆盖量、正文写另一个（差几倍很常见）。报「官方口径不一，取保守值」，不要挑好看的那个。
6. **输出粒度比价格更该先问。** 返回「每 100 g 热量」的接口不解决「这一盘多少克」；返回「整份热量」的不解决「吃了多少」。粒度不匹配时，报价再低也要把自建层的工程量算进总成本。
7. **精度宣称一律降级。** 厂商自报准确率没有方法论就不参与跨厂商比较；把「单图/单次」方案的物理下限说出来，别让用户拿宣传值做产品决策。

分层判定表、单位折算公式、托管 MCP 探测命令、精度基线：`references/api-capability-sourcing.md`。

---

## Mode E: 订阅可用性调研（哪些订阅能用模型 X，各给多少）

用户问「还有什么订阅能用 X」「A 的订阅能用多少量的 X」时，不是选模型，是**在模型已定的前提下找最便宜的合法入口**。顺序固定，别一上来就抄比价站。

1. **先查用户自己已有的订阅。** 模型自家实验室的消费级订阅常常是最便宜的一条路，而用户往往已经买了：Gemini 4 系列在 Google One AI Pro/Ultra 里的 Gemini app、AI Studio 原生给到高档配额。先把「你已经付过钱的那条」摆出来，再谈第三方 —— 否则会推荐一个他重复付费的方案。
2. **拿全量供应商索引：`models.dev/models/<lab>/<model>`。** 这一页列出 30+ 家供应商（含订阅型的 OpenCode Go、GitHub Copilot、Command Code、Devin）和各自的 context / 输出上限 / 单价。用它当「谁在供这个模型」的清单，不要靠搜索逐个猜。
3. **`available` ≠ `included`。** 索引里出现某个客户端只说明它**能选**这个模型，不说明算在订阅额度里。Cursor 把第三方模型明确排除在 plan usage 之外、从 prepaid 余额另扣。每个候选都要回它自己的 docs 找一句「是否计入配额」，找不到就是未确认。
4. **回厂商页面确认三件事：入门档位 / 月额度 / 滑动窗口。** 模型详情页通常只写「Pro and up」这类门槛，**每个模型的月额度住在 plan docs 里**，且同价的两个模型额度可以不同（同为 $2/$10 的两个变体，一个给 $30 一个给 $20）。把 plan docs 当必读页，别用模型页上的 calculator 当额度。
5. **额度是美元数时，请求数只能引厂商自己的基准。** 这类订阅普遍写「$X of usage per model」。厂商公布了参考请求成本（如 $0.0084/次，含 800 in / 180 out / 50K cache 的假设）就用它换算并写明假设；只公布「相对请求数」的就报相对值，不要自己乘一个 token 数出来（见上方 Pricing and quota tables 的同一条）。
6. **月额度旁边必须放 5h / 周窗口。** 通行口径是 5h = 月额度的 20%、周 = 50%（个别计划给更高）。按「月费 ÷ 月额度」赢的那家，突发档位可能只有对手的几分之一：跑长流水线的用户会先在 5h 撞墙，而不是月末撞墙。
7. **促销价到期会腰斩额度，把日期写进结论。** 模型单价处于首发折扣时（如 $2/$10 → $4/$20），订阅里那份美元额度的可用请求数在到期日直接减半。表里同时给「现在」和「到期后」两列，或至少在结论里点名日期与翻倍后的单价。
8. **最后一句按「用户实际要跑什么」落地。** 日常 agent 编程走量、大批量重构、突发密集高并发，三者的最优档位不同；只给对比表不给这句话，用户下一轮还得自己判断。

9. **额度大小用最近 2–4 周的用户实测当锚，第三方数据集只作交叉校验。** 厂商不公布额度时，唯一能反推的是「打满一次周/日限额烧了多少美元」这类带日期的实测（论坛/Reddit 的 usage 截图）。第三方数据集的「月费 ÷ 月 token」是快照，厂商静默下调额度后它不会跟着更新：同一个 Max 档，数据集反推的周额度可以比当期实测高一倍。两个数差一倍时以最近的实测为准，并在结论里点名「差的是哪一次下调」，不要把数据集那个数当现值继续算。
10. **组合能力（Fusion / router / 双模型配对）的资格只能在 picker 里确认。** docs 写的是默认组合和「lead 是前沿模型」这类描述，不等于可用组合的全集；某个新模型进了 picker，也不等于能当 lead 或 sidekick。唯一算证据的是显式标注（如「as a Fusion lead」）或 picker 截图里列出的下拉项。拿不到就明说「未确认」，并给出用户一条命令能自检的动作（打开 `/fusion` 看 Lead 下拉），不要用「应该可以」填空。
11. **免费模型 ≠ 不限量。** 「free models don't count against your quota」只说明单价为 0，不说明不限量：同一份 docs 往往还留着「quota consumption can differ from these rates」，社区也会出现免费模型被单独限流的反馈。把「单价 0」「额度豁免」「限流阈值」当三件事分别找证据。用户转述「官方说永久免费」时回原文核对；公告与 docs 冲突就把两个口径都报出来，别挑顺耳的那个。

各家订阅的档位、额度、文档地址和各自的坑：`references/coding-agent-subscription-plans.md`。
把额度换算成可用 token 量的算法（缓存配比、lead/sidekick 分摊、敏感性表）：`references/quota-to-token-budget.md`。

---

## Mode F: 买 vs 自建（用真实深度任务实测第三方产品）

用户丢一个产品 + 账号，问「它的能力如何，我们该采购还是自己开发」。这不是比价，也不是装来试一下，是**拿自己已经交付过的同一份活去对拍**；交付物是一份可拍板的采购建议。

1. **先定基准任务，再定问卷。** 同一个传主/同一份简报/同一个行业，Hermes 这边必须已有成品（如 doctor-book 的 `books/<slug>/10_package/`）。同题对拍才比得出「差在哪一层」；没有同题基准就明说只能比通用质量。
2. **接着用户已有的对话往下推，不重开。** 前面几轮（调研 → 方案 → 样章）是测试的一部分，先把已产物的 docx 全下载，缺的那一步通常是「剩下全部」。
3. **用必须拆分的指令逼出编排层**：「按方案写完剩余 N 章，输出全书 Word」。看它是否自行并行拆子代理、每组带不带章节简报（人物设定 / 概念清单 / 禁重复案例名单）、耗时多少——这是免费读到它内部机制的唯一窗口，写进报告。
4. **轮询产物目录，不信界面转圈，更不信它自述「已完成/已核对」。**
5. **把产品自报的数字全部重算。** 通用 agent 产品普遍虚报字数 2–4 倍且无人自检；声称「来源已标注」就 grep 链接与尾注；它自述的「对标手法逐项」当待验证清单，逐条在正文找实现。
6. **结构 + 体裁门禁体检。** 章标题在不在、目录有没有、有没有残留 markdown 星号；再按该体裁自己的红线 lint（零英文缩写 / 零化验单位 / 危险健康建议 / 虚构病例必须有名化声明 / 每条数据挂尾注）。它做不到的那几条就是采购决策的分界线。
7. **结论分两层写。** 它卖的是「通用编排 + 开箱 UI」（浅任务够用，可小成本买）；深度交付要的是「证据链 + 门禁 + 独立审稿 + 行业合规」（通用产品接不住，只能自建）。最后一句要回答用户真正的问题：两条线并行，不是一个替代另一个。
8. **附一条数据合规。** 这类产品在对方云端沙箱执行，稿子、调研、病例数据都过第三方服务器——医疗/法务/未公开素材场景单独投一票。
9. **别写成一无是处。** 承认它编排层真有东西（并行子代理 + 章节简报 + 防重复名单），短板落到机制（没有证据链、没有产出验证、没有领域合规），而不是「质量一般」。
10. **深任务测完必须补一轮浅任务扫测，否则结论会写偏。** 只测一项深活得到的画像是「它没有质量层」，很容易直接收成「这产品不行」——而它的真实卖点恰在浅活上。补三类，每类十分钟量级：① 传一份真 CSV 让它出分析报告 + 图（逐个重算数字，看它会不会自己发现并修错）；② 同一批数据做 5–8 页 PPT（看产出前有没有确认门、导出的是不是真 pptx）；③ 用它预置的行业角色做一件该行业的高频活（看角色自带的规则清单够不够专业）。三项里过两项，结论就必须从「能力不足」改成「更快的通用版，天花板在别处」。
11. **读它预置角色的技能/工具清单，判断是不是同构架构。** 打开角色详情，数技能模块与工具条目（如 23 技能 + 37 工具）。这个量级与你的 skill 体系相当，就说明底层同为「角色 = skill 包 + 工具集」，差别只在云端 SaaS vs 本地 agent——这句必须写进报告，它同时解释了为什么开箱体验它更好、而上限在你这边（接私域数据 / 写进公司红线 / 自建质量门）。
12. **区分「流程门」和「质量门」。** 它可能在产出前让你逐项确认设计（受众/配色/字体），这不是质量校验，是把决策前置给用户。真正的质量门在产出后：数字重算、引用闭环、体裁 lint、独立审稿。按这个口径分开评，别把确认流程算成质量能力。
13. **测试范围一变，回改报告的口径行。** 加测后「依据」里的任务数、能力画像、对比表的维度行、附件清单都要跟着改；只加一段新发现、留着旧的「三轮实测」字样，CEO 读到的是自相矛盾的两份材料。
14. **grounding 是角色级配置，不是产品级属性。** 同一平台里，接了租户文档的角色会给出带 `[1]`–`[6]` 内联引用的答案；没接文档的角色整篇零引用、病例照样编。只测一个角色就下「它有 / 没有 grounding」的结论，两种写法都是错的。至少各测一个：一个有知识库的角色（问只有文档才答得出的具体事实），一个裸角色（同类型问题）。正确的表述是「grounding 存在，但取决于运营方给这个角色喂了什么，用户自己不可治理」。
15. **每个角色给一个「本行当但有界」的任务。** 一句话需求 + 明确交付形态 + 字数或条数上限（如「400 字内」「只出一条」）。任务越开放，越会把角色拖进十分钟以上的空转；那样测出来的是稳定性而不是能力，两个维度不要混在一格里。
16. **缺料探针：故意给一个缺前置条件的任务。** 没有实拍图、没有成分表、没有检测报告——看它是硬编一个，还是拒绝产出并把事实卡归档等复检。区分两类门：产出前逐项找你确认（画布/配色/受众）是**流程门**，把决策前置给用户；产出中或产出后因为缺料而拒绝交付才是**质量门**。质量门单列一条评分项，它是这类 SaaS 最值钱的部分。
17. **卡死也是数据，但要先把变量分开。** 长任务十分钟以上无增量、stop 按钮点不动，记一条稳定性硬伤（同时说明「卡住时无法中断」本身是产品缺陷）。紧接着开一个新会话、用同一个角色发一个十分钟能完的小任务：能出结果写成「复杂任务把角色拖死」，出不了才写「角色不可用」。同一批角色里质量必然参差，逐角色记通过/不通过和卡死与否，不要拿单个角色代表整个平台。

18. **用户说「测得不充分」时，不要加测同质任务，先把旧测试的效力缺陷说出来。** 固定六查：不是同题对撞（两边比的是不同成品）、N=1 且单一评分者无盲（分不清能力差与随机性）、只测生成没测审计（核别人写错的稿才是日常）、测的场景不是公司主流程、使用者错位（专家驱动浏览器 vs 非技术同事）、治理与成本 0 数据。每一条都要说出代价，再把它变成变量：资料有条件/无条件两臂、重复 3 次、盲评改名打乱、真人臂。
19. **题目与权重先冻结，再开跑。** 域权重按「人天占比 × 错误代价」定，域内按可测性分配题数，不要平均；权重必须在看到任何分数前定稿——事后调权重可以把任何结论做出来。
20. **一票否决与加权分分账。** veto 沿用公司已有评测的口径（本地评测仓的 veto 定义表，别另造），命中即单题 0 分并单独计数；总分只回答「多好用」，veto 数回答「能不能用」。加权分可以互补，红线不能互补。
21. **先写预测再跑。** 哪几题对手会赢、哪几题会输、输在哪一层，写进方案；跑完对照。预测错了先改判断，不要改题或改权重来自圆其说。
22. **必带一条真人臂和一条成本臂。** 真人臂找 3 位真实使用者（不是团队里最懂 AI 的那位），同题不培训，只记首次即用 / 求助次数 / 用时 / 要重做的比例——「开箱即用」如果只对专家成立，总分再高也不该买。成本臂只报「每可用交付物成本」，把返工复核人天算进去，报价没拿到的格子留空，不要估。
23. **交付三件套，不是一份报告**：方案 HTML（讲清为什么这样测、旧测试哪里站不住）+ 机器可读题库 JSONL（prompt / 夹具 / must / mustNot / veto / 金标 / 双侧预测，字段尽量兼容公司现有评测 schema）+ 带公式的评分表 xlsx（评分页 + 汇总 + 决策 + 盲测页 + TCO 页）。夹具里的合成数据要带金标数值，真实资料留占位并标「待换」，不要用编造的产品参数充数。

24. **「它能不能做 X」不要用产品形态推结论，拆层实测并验到产物。** 抓取 / 本地操作 / 媒体这类能力面，拆成「云端沙箱能跑什么」「能不能碰用户本机」「能不能登录、点击、发布」三层分别给探针；抓取题至少一条用你 3 秒内能自己抓完的固定列表页做真值对照，它给的每个链接自己 curl 一遍看死活（自称「没有编造」不算证据）；媒体题自造带可辨认标记的素材（如画面本身有固定图案的测试视频），取回产物用 ffprobe + 抽帧验标记真在像素里。同一轮里顺手问它「你不能做什么、做不到直说」——这类产品对自己架构的自述几乎总是准确的，是一条低成本可引用证据。结论写成「能做的最小单元 vs 做不了的整条链路」，逐条点出后者恰好是自己那条管线的价值。

25. **幻觉与红线要分模式、分域测，别用一次探针代替一类结论。** 核查式提问（「这个疗法/这篇论文存在吗」）考的是验证路径，创作式任务考的是生成路径——同一产品可以在前者两次都拒编、在后者编造病例无人拦。两臂都跑，报告里分开写。红线同理：拿公司真实红线做一条变体（指令里明确要求被禁的那个方向）看它守不守；给了合规自查清单先别算成「有红线」，要分清那是运营方预置在角色里的协议还是平台机制，再换医疗/出版域交叉一次——域覆盖不全就只能写「营销域可信，其他域为零」。
26. **一次失败先当疑点，不当定论。** 同题重发一次再判：第二次正常完成就改写成「偶发」，并把所有引用该证据的地方（矩阵行、角色表、CEO 简报、稳定性结论）一起降级；复现了才写系统性缺陷。但「卡死时中断按钮无效」不论复现与否都单列保留，那是独立缺陷。
27. **判定汇总行是硬断言。** 对比表每新增/拆分一行，「A 占优 N / 平手 N / 我们占优 N」都要重算并同步两份材料；留着旧计数，CEO 读到的就是自相矛盾。

28. **对拍前先把对手的 agent 喂到我方同一水平，否则测的是我方技能库而不是产品能力。** 这类平台的角色常自带「风格卡蒸馏 / 写作方法训练 / 知识库接入」——把它当测试环节用起来：投 3–4 篇我方管线本来就据此调过的范文，再把自家方法论（结构比例、证据与意象独占、正文故事化＋尾注扛审计、母语呼吸感红线、行业合规底线）写成 SOP 一起喂，最后跑一段千字级校准练习并当场纠偏一次。省掉这步，报告第一句就会被「你那边有 skill 库、它这边没喂」推翻，而且分不清工程底座的差与准备度的差。角色自述协议里写着哪种能力，就测那条路——测最冷的路径得到的是「不会用」，不是「不能用」。

29. **两边拿的那份「同一个整段提示词」必须内嵌传主的已确认事实骨架。** 身份、从业年限、关键转折事件、不可改写的细节全都写进 prompt，两边信息集相同、只比方法。否则题目变成「谁更敢编私人履历」，赢家是最会幻觉的那个。

30. **分两棒交付：先大纲＋覆盖多种章型的代表章，再全书。** 任何 agent 被要求一轮吐完整本书都会把章节压成提纲，自报字数虚报 2–4 倍只是症状。首棒的 3–5 章要分别落在论证 / 机制 / 实战 / 收束等不同章型上，第二棒再用统一续写指令跑完——这样一枪成稿与长程完稿两个能力面都测到了。判分用自家 lint 脚本当客观标尺，并把「风格蒸馏吸收度」单列一维。

31. **喂完范文必须换一个全新会话，并清空对手的持久化产物目录，否则测出来的是抄袭而不是能力。** 风格蒸馏窗口里留着的样章正文会触发就近搬运（长稿单章可到 79% 段落逐字重合，新传主被写成样章主角、安排在样章城市坐诊）；这类平台的角色目录常是**跨会话共享**的，只点「新建会话」它照样回读上一轮写在共享盘的旧稿。顺序：清掉角色目录下本项目的稿件（**保留 `素材库/` 的风格卡与方法卡**，那是预热成果）→ 新建会话 → 再发同一段主提示词。**两轮都要报**：同会话那轮是「有母本可抄」的样本、不是能力上限；新会话那轮才是可比数字。删掉母本后指标会大幅塌陷（实测段落中位数 69–78 → 29–42 字），这个落差本身就是最强证据——它证明前面那些漂亮的可读性分数是抄来的。

32. **风格卡会把样章的实体一起写死，喂完先在卡里 grep 实体再做正赛。** 蒸馏出的「风格卡」常把样章的书名、主角姓名职业、诊室场景当成风格要素固化下来，于是新传主的书被直接命名为样章书名、第一章照样从「某岁会计走进诊室」开场。判定：在风格卡里搜样章独有的人名 / 书名 / 城市 / 场所 / 科室；命中就要求改成结构描述（冷开场用什么手法、节拍几段），改不干净则把「风格卡不具备去实体抽象能力」单列为能力短板，而不写成偶发失误。

33. **并行写章的子代理不带人设，一本书会出现多个叙述者——用角色词计数定位。** 为凑字数自行 fan-out 时，主代理常在后几个子任务里漏掉「第一人称作者是谁、什么职业、什么场景」，结果前言是传主本人、中间章变成医院坐诊开化验单的大夫、末章改成第三人称的科室医生，还顺带把指定好的章主题换掉。检验：逐章数角色词（`大夫 / 诊室 / 门诊 / 候诊区 / 某医生`），单章超过十次即人设穿帮；再翻它的子任务工具卡 Prompt 找根因（漏传作者身份、把风格卡里的示例场景当指令派下去）。这条要单列进报告，它同时解释了「为什么章节主题会跑掉」。

抽取脚本、重算手法、报告骨架与措辞：`references/product-buy-vs-build-teardown.md`（第 11 节为全角色矩阵实测的探针设计与读法；第 12 节为「实测不够、要升级成可复跑评测方案」时的题目/权重/判定设计；第 13 节为一手信息抓取 / 本地操作 / 媒体处理的能力面探针与网页版产品自动化坑；第 14 节为幻觉 / 红线 / 知识库自喂三组治理探针；第 15 节为「把对手喂到同一水平再同题对拍」的 method-aligned A/B 全流程）。

---

## Mode G: Demo 宣称能力核验（「这个新模型做 X 究竟行不行」）

用户丢一条社媒 demo（X 帖 + 视频），问「这个 model 做视频 / 做 3D / 写前端的能力如何，这是新模型」。这不是选型而是**核宣称**——demo 是别人做的，能力可能属于模型、属于作者的 harness、或属于半年前的另一代模型。交付一句可拍板的判断，不是参数表。

1. **先读作者的补充回复，再读 demo 本身。** 发帖人常在回复或后续帖里自曝「首页之前的同一类视频一直是另一个模型做的，这次只是刚拿新模型试」。漏掉这一条，整篇评估的归属就错了——这是本模式下最贵的一次误判。
2. **把 demo 里每个数字回一手原文核一遍，别信它自己算的。** 自动生成的论文讲解视频会出现数量级错误（原文 `1.04×10²² FLOPs` 被画成 `10²¹`；正文 `approximately three times` 被画成 `4.4x the compute`）。画面漂亮 ≠ 核过数；口播与画面还会互相矛盾，两路都要对账，并以原文为准把差异写进报告。
3. **数字读原分辨率，不读缩略图。** 指数、上标、脚注先下最高码率，再 `vision_analyze(region=[…])` 按原图像素坐标裁到那块看；整帧缩略或拼图会把 `10²¹` 与 `10²²` 读反，而这一个字符就决定结论。
4. **分清「模型能力」与「harness 能力」。** 代码渲染视频 = 写 Manim / Canvas / Remotion 代码 + 抽帧自检 + 外部 TTS / 编曲，模型只占一环。版式规范、分镜脚手架、音频同步若来自作者的固定管道，就不能写成「模型一次直出」；反过来，若作者把新模型塞进成熟管道跑通，也只能算「可替换进该管道」。
5. **成本取作者自己的账单，不推算。** 找公开的墙钟与 token 数（如 `12h34m` / `13.7M in` / `5.4M out` / `911.6M cache read`），再拿第三方长测的墙钟与步数交叉（同一模型 `55.3%` 但 `431 分钟 / 1,128 步`）。官方博客自认的「长程思考」与这两组数一致时，才写「慢是机制性的，不是吞吐问题」。
6. **可用性单独一行，不要和能力高低混说。** 订阅专属 / 自家客户端 / API / 开源权重是四件事，查 `/v1/models`、docs、HF 组织页；权重未发就写「榜单归入开源阵营，权重未发」。
7. **官方没给方法论的自评分只写「官方自述」。** 胜率图、只对自家小模型做的对照实验不能进跨模型比较；同时列出有口径的第三方分与它附带的步数代价。
8. **结论三段式：定性 → 真实短板 → 我们怎么用。** 一句「属第一梯队但不是独有能力」，一条机制性短板，一条明确适用场景（离线批量挂机 vs 交互式出片），最后才给采纳建议；只给「很强 / 一般」这类形容词等于没答。

取视频、抽帧、逐句核数、成本与可用性台账的命令与判读：`references/demo-claim-verification.md`（配套 `scripts/number_audit.py`，把帧里读到的数回原文批量找出处）。视频的下载 / 抽帧 / 转写手法复用 `reference-video-teardown`，不在本 skill 重写。

---

## Shared Pitfalls

1. **No search-first on known URLs** — navigate directly to avoid CAPTCHA
2. **DDGS TLS compatibility** — upgrade `ddgs` if hitting `ValueError: Unsupported protocol`
3. **Pricing changes fast** — date-stamp all price data
4. **Cross-validate benchmarks** — combine AA + LushBinary + community
5. **Always show file path** — save reports locally and tell the user where
6. **同一模型 id 在不同中转上可能一个带思考、一个不带**（一边 `reasoning_chars` 为 0）——先看有没有推理内容，再比速度和成本；「快」可能是靠不思考换来的，要说清
7. **并发压测榜上的 TPS 不是单路速度。** 榜单常把「N 路并发下单个 worker 的速度」放进 TPS 列（如 10 路压测下的每路 59 tok/s），抄进报告就成了「该 provider 单路 59 tok/s」，与用户自己用的体感差几倍。抄任何吞吐数字前先读列头/图例，写清是单路、并发每路，还是总吞吐。
8. **用户说「跟我的体验不一样」时，先回原始记录重算，不要辩护。** 体感差异八成来自口径（并发每路当单路、拿两个中位数相减、把思考 token 算到解码速度里），改数字比讲道理快；重算后仍不一致，就把两个口径都报出来并说清各自适用场景。
