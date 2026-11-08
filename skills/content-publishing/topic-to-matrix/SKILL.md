---
name: topic-to-matrix
description: "Use when given a 自媒体选题 to plan all formats+platforms."
version: 1.0.0
author: 智子
license: MIT
metadata:
  hermes:
    tags: [content, orchestration, youtube, wechat, x, xiaohongshu, bilibili, weibo, kuaishou, matrix]
    related_skills: [content-grounding, long-form-ai-explainer-film, youtube-channel-growth-playbook, science-video-daily, wechat-animated-longform, md2wechat, native-subtitle-quote-image, cn-social-image-post-publishing, creator-channel-analytics, video-common]
---

# 选题 → 全形态全平台矩阵（总编排）

用户只给一个选题或方向。本技能负责：搜集信息 → 建一份共用事实表 → 判断做哪些形态、发哪些平台、先做哪个 → 等用户一句话拍板 → 按路由调用各条生产线 → 汇总草稿 → 记账，之后用数据复盘修正判断。
本技能**不自己做内容**：渲染、配音、排版、发布都交给下游技能（路由表见 `references/format-routing.md`）。

## When to Use
用户说「这个选题怎么做 / 围绕 XX 方向出内容 / 这个热点要不要跟 / 先挖掘信息再给出最适合做的方向」，或发送暗号 **「存：[内容/链接/想法]」**（或只丢链接/截图不说话）时。
⚠️ **注意区分「存」与「做」两条全局暗号**（详见 `content-creator-pipeline`）：
- **「存：…」或显式要求「先挖掘信息，再给方向」** → 走本技能步骤 1–5（抓原文 + 归档 `raw-sparks.md` + `media-hub` 建档 + 输出【30秒编导判断单与 A/B/C/D 勾选单】），停下等用户回代号。
- **「做：[链接/选题/方向]」（且未说“先给方向”）** → 用户已直接拍板立项！**禁止停在步骤 5 等用户选 A/B/C/D**，必须在完成 `raw-sparks.md` 与 `facts.json` 建档后，立即自动进入步骤 6 走完主力生稿管线（默认直接把 **公众号深度长文 + 微信贴图 3 卡** 过完独立 Subagent 事实核查推入公众号草稿箱，并同步产出 **X Thread / 小红书草稿**），直接把草稿箱回执与预览图端给用户点头。

## Goal
一个选题只抓一次原文、只核一次事实，派生出四种形态（长视频 / 短视频 / 图文贴图 / 长文章），按平台分工分发到中美两边；每个决定都写明理由，可以复盘。

## Success
- 选题目录 `~/HermesWork/media-hub/<YYYYMMDD-slug>/` 内有：`facts.json`（每条都是本次抓到的原文逐字引语）、`decision.json` + `brief.md`（判断单）、`ledger.csv` 里有这一行。
- `python3 <SKILL_DIR>/scripts/hub.py check <dir>` 输出 `HUB OK`。
- 四种形态都有结论：GO / LATER / SKIP，每个结论带一句理由；GO 的都写了平台、语言、下游技能、预估审核小时、引用的事实编号。
- 用户拍板后，各下游产物的路径和 RECEIPT（草稿 media_id、成片路径、管理页状态）回填到 `brief.md` 的「交付」一节。

## Constraints
- **事实红线**：遵守 `content-grounding`。事实只能来自 `grounding.py fetch` 抓到的原文；web_search 摘要、AI 摘要只当线索。所有派生内容只能引用 `facts.json` 里的编号（[F01]…），新事实要先补进事实表。
- 用户本轮点名了平台（如「发抖音 小红书 视频号」）就以点名为准，判断单只排这些平台，其余形态标 SKIP/LATER 并写理由。
- **平台范围**（用户 10-07 定）：主力 = YouTube、微信公众号、视频号、微信贴图、X；次要 = 小红书、B站；再次 = 微博、快手。抖音只同步视频（不发图文、长文）。YouTube 用英文；X 短视频/机器拆解类按用户要求发中文版。其他平台（如 TikTok）不进判断单，除非用户明说。分工见 `references/platform-matrix.md`。
- **先判断、后生产**：判断单出来后停下等用户拍板。用户的习惯是一句话决定（如「按建议做」「长片先不做」），不要逐项追问。
- **产能预算**：用户每周给 10 小时审核。判断单里 GO 项的审核小时数加上本周已承诺的（`hub.py status` 能看到）超过 10 小时，就把优先级低的形态降为 LATER，不要硬塞。
- **只做草稿**：发布、群发、删帖都要用户明确授权；平台声明怎么勾按各下游技能里用户已拍板的规则执行，本技能不另定规则。
- 个人身份（翡冷翠），与公司无关；健康/医疗类选题要加免责行，不做带货。
- **个人 IP 原则（用户 11-08 定，最高优先）**：「不用学写代码，学会像产品经理一样指挥 AI」。每个选题先过 `references/ip-principle.md` 的三问（谁在问 / 卡在说清需求·拆成步骤·验收结果哪一步 / 能否并排实测），打 `scores.ip_fit`；短视频需 ip_fit≥4。brief 必填「IP 对齐」一节。公司号选题不适用，ip_fit 填 0 并在 brief 注明「公司号」。

## Procedure
1. **接题**：判断输入是「具体选题」还是「方向」。是方向就先做第 2 步的线索搜索，给 3 个候选选题（每个一句钩子 + 主要原始来源是否存在），推荐一个，用户不选就按推荐走。
2. **搜集**：`hub.py init "<选题>" --slug <slug>` 建目录。先 `web_search` 找线索（中英各搜一轮，看中美两边的讨论热度和角度差异，记进 `brief.md` 的「中美差异」）。再用 `grounding.py fetch --date <今天>` 抓原始来源（官方页、论文、原始数据、当事人原话），按 `long-form-ai-explainer-film` 的事实表格式写 `facts.json`：`{id, url, local, quote}`，quote 从本地正文逐字复制。
   - 没有 `grounding.py` 时的可用替代：`web_extract` 会把每页全文存到 `~/.hermes/cache/web/<host>-<hash>.md`（截断提示里有路径；未截断的用 `grep -l "<页面标题>" ~/.hermes/cache/web/*` 找）。把这些文件复制进 `<hub>/sources/<短名>.md` 当 `local`，写完 facts 先用「压缩空白后子串匹配」自检每条引语，再跑 `hub.py check`。缓存目录会被清理，所以必须复制进 hub，不能直接指向缓存。
   - `hub.py init` 先打印 `HUB <dir>` 再写台账；如果之后卡住超时，目录和模板通常已经建好——`ls <dir>` 确认有 brief.md/decision.json/facts.json 就继续，不要重跑 init。
3. **判断**：先按 `references/ip-principle.md` 过三问、定主讲哪一步、选一种开头式、归到三条线之一（方法演示 70 / FDE 现场 20 / 立场 10）；再按 `references/judgment-rubric.md` 打分，填写 `decision.json`（init 时已从模板复制）；`brief.md` 用人话写清：核心角度、钩子、中美各用什么切入、四种形态的结论和理由、建议的先后顺序、风险。
4. **自检**：`hub.py check <dir>`。再派一个子代理当「反方编辑」（给它 `brief.md`、`facts.json` 和 `references/ip-principle.md`），让它找四类问题：钩子是否言过其实、哪个 GO 证据不够撑、哪个 SKIP 其实值得做、是否违反 IP 原则（前 5 秒有术语、无依据倍数、靠贬低人群、接不回 slogan）。有道理的改进去，没采纳的在 brief 里写一句为什么。
5. **拍板**：给用户一张短表（形态｜结论｜平台｜预估审核小时｜理由），每行前面加字母编号（A/B/C…），加一句推荐。停下等回复。
   - 用户的放行是**跨轮、逐项**的：常见回法就是单字母「A」，下一轮再说「D 也可以做」「C 也可以做，B 也可以做」。收到哪一项就在当轮立刻开工那一项（并行派发下游技能、回填 brief），不要等全部选定、不要重复追问没回的那几项。
   - 未放行的项保持原结论挂在那里即可；用户后续逐条补选时，接着原判断单执行，不重做事实表。
6. **派发**：按 `decision.json` 里的 `order`，逐个加载下游技能执行；每个下游任务的输入都是这个选题目录（事实表 + 判断单），产物放在各自原来的工作目录，路径回填到 `brief.md`。长片和长文最费时间，适合用 `delegate_task` 并行，或拆成定时任务。
7. **收尾**：`hub.py set <dir> status=drafted`（或 published），各平台管理页读到的状态写进 brief。一周后用 `creator-channel-analytics` 取数，把每个平台的表现写回 ledger，并在 `references/judgment-rubric.md` 末尾的「校准记录」里追加一条：哪个判断准了、哪个错了。

## Stop
- 原始来源抓不到，或可用事实少于 3 条：如实告诉用户「这个选题撑不起来」，给出缺的是什么，不硬做。
- 选题前提和原文对不上（比如用户以为的事实是错的）：先告诉用户，改角度，不迁就前提。
- 判断单出来后、用户拍板前：不进入生产。
- 需要登录、扫码、权限弹窗：交给用户处理。
- **「实测某工具」类选题要花钱时**（订阅、积分、按次计费）：研究阶段就把门槛抓成事实（是否必须付费、按次扣费规则、套餐价格、哪档能用该功能——查不到就写「未核实」），在拍板表里单列「要不要付费、建议哪档、预计多少钱」作为用户要决定的事；同时给一个不花钱的备选角度（例如用自有代码流水线复刻效果），并写明备选版标题不能声称测过该工具。付款和登录由用户自己完成。

## Verify
- [ ] brief「IP 对齐」已填：真实提问原话、主讲哪一步、并排实测方案、所属线、接回 slogan 的一句
- [ ] `hub.py check` = `HUB OK`（事实引语都能在本地原文里找到；四种形态都有结论；平台都在允许列表里；审核小时没超预算或已写明理由）
- [ ] 反方编辑的意见已处理
- [ ] 交付时每个产物都有路径或 RECEIPT；没做的形态写明是 SKIP 还是 LATER
- [ ] 没有任何内容被自动发布

## 已知缺口（做到这些平台时如实告诉用户）
- 微博：本机还没有发布技能和后台操作记录。
- X 与 YouTube / Shorts：虽然没有 CLI 自动发布脚本，但均可通过 `ego-browser` 默认 profile 网页端直接上传并发布（X 用 `x.com/compose/post`、YouTube 用 `studio.youtube.com/.../videos/upload?d=ud`，具体 DOM 选择器与步骤见 `science-video-daily` 技能下的 `publishing.md`）。

## References
- `references/ip-principle.md` — 个人 IP 原则：三问、ip_fit 打分、三条线配比、钩子结构、红线
- `references/judgment-rubric.md` — 打分维度、形态判断规则、校准记录
- `references/platform-matrix.md` — 10 个平台各自承担什么、用什么语言、来自哪个形态
- `references/format-routing.md` — 形态 → 下游技能 / 工作目录 / 门禁
- `templates/brief.md`、`templates/decision.json`
- `scripts/hub.py` — init / check / set / status
