---
name: content-creator-pipeline
description: "Use when user says 存/做 or runs X/公众号/小红书 pipeline."
version: 1.0.0
author: 智子
tags: [content, social-media, x, wechat, xiaohongshu, pipeline, creator]
trigger:
  - 用户要发推文
  - 用户要写公众号
  - 用户要发小红书
  - 用户要生成内容
  - 内容选题
  - 内容队列
  - 创作工作流
---

# 内容创作流水线 — 工程审美主义者

翡冷翠的自媒体内容创作系统。核心理念：**AI 是生产力工具，但表达的是真实自我**。

## 定位参考与「单人创意团队」三角色分工（2026-11 升级）

完整定位文档：`~/Workspace/playground/HermesWork/marovole-Superpowers/docs/social-media/personal-brand-engineering-aesthete.md`
**个人思想签名与上下文总表（SSOT）**：
- Obsidian Vault：`/Users/marovole/Library/CloudStorage/Dropbox/Obsidian Vault/05-Outputs/content-creator/BRAND-SIGNATURE-FEILENGCUI.md`
- 仓库镜像：`~/Workspace/playground/HermesWork/marovole-Superpowers/docs/social-media/personal-brand-signature-feilengcui.md`

### 三角色分离法则（吸收自 Dan Koe "One-Person Creative Team"）

避免把 AI 直接当无脑写手产出「无限垃圾（Infinite Slop）」，智子与用户的协作严格按三层拆解：
1. **Brand Strategist（品牌签名槽位）**：生成任何长文、脚本、推文前，**必须先读取 `BRAND-SIGNATURE-FEILENGCUI.md`**（先看 Part 0 个人 IP slogan「不用学写代码，学会像产品经理一样指挥 AI」+ 三步法「说清需求 / 拆成步骤 / 验收结果」，个人号所有视频与文章都以它为骨架），对齐 8 维思想签名（痛点原话、12年 PM + 非技术公司 FDE 实战锚点、4 条反共识立场、专属造词词典如「撤销键与验收台」「先改工作流再挂模型」「生成便宜验证昂贵」「纯文本主权」）。
2. **Content Strategist（跨平台侦察与三级选题树）**：智子负责去**非当前发布的跨平台**（如海外 X 长文、arXiv、System Card、Reddit 周榜）提取经过验证的爆款结构，维护 `ideas/content-map-YYYY-MM.md`（`3-4 支柱 → 子话题 → 高潜选题 → 4 个标准切角`）。
3. **Grounded Writer（初稿引擎） vs Creative Director（人类总监）**：智子完成 `Grounding 事实锁死 + 挂载思想签名的 80 分初稿 + Humanizer 去 AI 味`；用户只花 20% 精力做 Creative Director（注入真实 FDE 现场细节、个人暴论与终审拍板）。

**一句话定位**：工程审美主义者——在一切领域寻找精确与美的交集（个人号主轴：AI + 科技 + 财富，以 12 年 PM + 一线 FDE 视角落地）。

**结构**：职业底色 + 四大兴趣（按优先级）

> 详见 [references/positioning-engineering-aesthete.md](references/positioning-engineering-aesthete.md)（完整定位、调性指南、排期、互动账号）
> 草稿模板见 [references/templates.md](references/templates.md)

- **职业底色**：12年PM + AI全栈开发。不是独立透镜，是所有内容的底层视角。不写教程，写"我作为12年PM对这个产品决策的判断"。
- **兴趣1（最高优先级）**：游戏——从系统设计/叙事结构/视觉语言/交互哲学评价，偏爱独立游戏美学
- **兴趣2**：硬件——从工程设计哲学/材料选择/散热声学/工业设计评价，M2 Max 64GB用户
- **兴趣3**：美学艺术——设计是信息的结构，字体排印/色彩理论/UI拆解/工业设计评论
- **兴趣4**：文化艺术——认知框架/跨领域类比/长期主义/BTC底层哲学

一篇好内容往往从兴趣出发，用职业视角来拆解。

## 零摩擦素材沉淀与「存 / 做」双暗号路由（全局跨会话生效）

用户的原话是「我看到好的信息、新鲜的、有价值的、引人思考的，都需要沉淀下来」。为保证跨会话零摩擦，全局固定两条暗号（无论同会话续接还是新开独立 Session 均直接生效，**严禁被 `x2doc`、`image-generation`、`tool-evaluation-workflow` 等单点技能劫持而漏掉自媒体管线**）：

**暗号要生效，必须落在「加载层」而不是聊天记录**：新 session 只带 memory / USER 档案和 skill 索引，看不到任何历史会话。所以任何常设约定（暗号、固定叫法、固定流程）都要同时写进本 skill 的 `description`/触发词（保证用户裸发「做：…」也能命中加载）和用户档案里的一句记忆；只写进当次对话 = 下次必然失忆。

### 暗号一：「存：[内容/链接/想法]」（或用户直接丢链接/截图不说话，或明说「先挖掘信息，再给出最适合做的方向」）
👉 **只做「入库 + 30秒编导判断单」，不直接生稿排产**：
1. 抓一手原文与硬数字（`grounding.py fetch` / 源码 / 抽帧），写入 `VAULT/05-Outputs/content-creator/ideas/raw-sparks.md`（截图拷入 `assets/YYYY-MM-DD-<slug>/`）。
2. 按 [templates/director-brief.md](templates/director-brief.md) 直接回复两段式 **【30 秒编导判断单 + A/B/C/D 排产勾选单】**。
3. 停下等用户回代号（不回就默认只存库不排产）。

### 暗号二：「做：[方向 / 刚才第X条 / 链接]」
👉 **代表用户已拍板立项，必须直接走完事实核查与生稿管线，把成品推到草稿箱/预览界面等用户点头（绝不能只回一张判断单停下来等选 A/B/C/D！）**：
- **情况 A（指定代号或方向，如「做 A B」「做刚才第2条的公众号长文」）**：直接按指定形态走完 Grounding + 独立 Subagent 逐句事实核查 + Humanizer，把成品推入公众号草稿箱 / 落盘预览。
- **情况 B（新开 Session 直接发 `做 @url:...` 或 `做 [某个选题]`，且未要求“先给方向”）**：
  1. 后台一步完成：一手原文抓取 + `raw-sparks.md` 入库 + `media-hub` 事实表锁定；
  2. **不停车问选择题**，直接产出最匹配该题材的主力成品包并推入草稿箱/预览界面：
     - **必交主力（A）**：**公众号深度长文（`article.py render` → `grounding` → 独立 Subagent 逐句核查 → `article.py draft` 推入公众号草稿箱）+ 微信贴图 3 卡（推入公众号草稿箱）**；
     - **同步交付（B/C）**：**X 双语/英文 Thread 草稿（`x-thread.md`）+ 小红书图文文案/卡片**（若用户点名做视频则同步出 **D 60-85s 短视频**）；
  3. 最终回复直接交付：**已入箱的 `draft_media_id` 回执 + 卡片/海报预览图 + 本地稿件路径**，并在末尾顺手附简明编导判断单与可追加形态（如短视频 D），等用户点头发表。

### 一单多形态的产出落点（「做」的交付位置）

一个选题 = 一个 slug 目录 `VAULT/05-Outputs/content-creator/queue/longform/YYYY-MM-DD-<slug>/`，里面放 `article.md` + `evidence.json` + `x-thread.md`；小红书文案落 `queue/xiaohongshu/YYYY-MM-DD-<slug>.md`，配图在正文里写相对路径指着素材目录。配图一律复用当日 `queue/tietu/<date>/<slug>/<theme>/01-cover.png|02-facts.png|03-take.png` 已渲好的卡片，不重渲、不留占位符。

一次「做」多单（如「补 1…补 5」）= 每单一个 slug 目录，按目录逐个跑 `check`，全部成稿后一次派 2 个 subagent 并行核查（每人 2 篇），不要一单一派——逐句核查是读全文，批量并行才不拖时间。

### 落盘（必须做，不然等于没沉淀）

- 一条素材 = 一段 `VAULT/05-Outputs/content-creator/ideas/raw-sparks.md`（新条目放最上面，按日期倒序）。每条必带四样：
  1. `@session:default/<session_id>` 原始会话追溯（结论要能回到现场，用户随时会追问「当时怎么跑的」）
  2. 截图整包目录 `assets/YYYY-MM-DD-<slug>/` —— 从 `~/.hermes/cache/images/` 拷过去，缓存会被清，不拷就丢
  3. 反共识切入点：**别人教程里的痛点 / 收费点 / 失败点**，这条比内容本身更值钱
  4. 独家一手事实：真实报错原话、真实 IP/ASN、真实耗时与费用、被停用的安装路径——二手新闻一律降级使用
- 末尾挂「思想签名」：这条素材如何体现工程审美（工具组合、跨端协同、验证门禁），供 `BRAND-SIGNATURE-FEILENGCUI.md` 对齐时引用。

### 交付：编导判断单 + 排产勾选单

素材沉淀完的那一轮，直接给两段式回复，不写过程复述：

1. **编导判断单**：为什么这条极爆（痛点反差 / 工程爽感 / 自然裂变钩子）、3–5 个别人没有的实测干货点（可核的技术细节）、思想签名落点。
2. **排产勾选单**：表格给 2–4 个**已带标题方向**的代号（A 公众号长文+贴图 / B 小红书图文卡 / C X thread / D 60-85s 短视频…），每行写形态与目标平台、核心打法与标题、**预估用户审核耗时**。结尾一句「回我代号即可开工」。

模板见 [templates/director-brief.md](templates/director-brief.md)。

### 规则

- **一次真实跑通的技术流程 = 一条 A 级素材**，至少能拆 4 个切角（公众号上手实操 / 小红书避坑卡 / X 海外 thread / 短视频双屏接力）；优先于任何二手热点。
- 平台分工不在这里重复，按 `topic-to-matrix` 的 `references/platform-matrix.md` 选形态。
- 用户勾了代号才进起草；起草仍走本 skill 的 grounding + subagent 逐句事实核查 + 人工终审，素材库里的事实可以直接引用，但数字必须回原始会话/原文核一遍再写进稿子。

## ✅ 现行主线：公众号「AI 快讯贴图」（2026-10-02 起）

- 定位：快讯只是入口，判断才是价值。主题=AI 工具/模型更新的实测判断（PM+全栈视角）
- 代码与规范：`~/HermesWork/ai-tietu/`（README.md 规范 / render.py HTML→PNG 3:4@2x / themes/{blueprint,paper,swiss}.css / cron-prompt.md）
- 每条=封面+事实+判断 3 卡 + caption；中文卡片一律 HTML 渲染，不用 AI 生图（会写错字）
- 队列：`VAULT/05-Outputs/content-creator/queue/tietu/<date>/<id>/`，发布后移 `published/tietu/`
- Cron `cb3ae0a9b0a3` 每日 10:15 读当日 x-pulse 出 2–3 条草稿（draft≥6 只报待审）；只出草稿，发布永远人工
- 旧 X/公众号长文/小红书生成 cron（e0a3ffb23365/42e9bc5fde3c/91775eae2d6a）与 X 推进 ca96fca6 已 pause；x-pulse 保留为上游
- 发草稿：`md2wechat create_image_post -t 标题 -c "$(cat caption.txt)" --images 01..,02..,03.. --open-comment`（进草稿箱，发表由用户点）
- 公众号 API 固定出口：Surge DMIT.conf `DOMAIN,api.weixin.qq.com,WeChatAPI`（fallback 02-DMIT-LA2/07-DMIT-LA2-HY2）→ 白名单 IP=<WHITELIST_IP>（后台已在白名单）。报 40164 先 `surge-cli rule match api.weixin.qq.com` + `test-policy-external-ip 02-DMIT-LA2`；JP 节点 10-02 不通
- 日更节奏（10-02 用户定）：每天 3 贴图 + 3 长文。长文=一个多图文草稿（A《AI 早知道 · MM.DD》简报头条 / B 深度判断 / C 上手实操），用户中午 12:00 手机一次群发（10-02 从 20:00 提前；10:45 出稿后即可发）。工具 `ai-tietu/article.py`（md→内联样式 HTML + 封面 → draft/add）；cron `97034ee88833` 10:45，说明 `cron-prompt-longform.md`，台账 `ab/longform-ledger.csv`
- md2wechat 的 api 排版模式 key 无效、ai 模式只吐 prompt，所以长文不用 md2wechat convert；微信 batchget 响应无 charset，必须 `.content.decode('utf-8')`
- 发表接口 freepublish/* 返回 48001 api unauthorized（该号无发布接口权限，无法用接口发表）；草稿接口正常。默认发表方式=智子推草稿 → 用户在手机「公众号助手」App 草稿箱点发表（已验证：无需扫码，点确认即可；草稿发出后会从草稿箱消失，可据此判断已发）；网页发表必须管理员扫码
- 核草稿是否入箱：stable_token + draft/batchget（经 127.0.0.1:6152 代理，走 WeChatAPI 策略组）
- 素材主源=用户站点 news.neumabio.xyz（/api/latest、/api/day/<date>），由 cron script `~/.hermes/scripts/neumabio-ai-hot.py` 注入；出现 STALE 时用 x-pulse 补充
- 站点更新（10-02 起智子接管，Grokbot 已退订）：cron `6af8733ab925` 每日 06:00（pin gemini-3.8-flash/antigravity-oauth，简报也算写作），管道 `~/HermesWork/neuma-briefing/`（cron-prompt.md + scripts/briefing.py codexiq/validate/publish）；token `<SECRET_FILE>` 取自 Railway 项目 daily-briefing 的 UPDATE_TOKEN；站点代码 GitHub marovole/neuma-daily-briefing。站点 STALE 先查这个 cron
- 节奏：每天 3 条起步（12:00 / 18:00 / 21:30），每周日看单条中位数决定升档 3→5→7→10 或退档；不凑数
- 模板 A/B：`ai-tietu/ab/`（README 判定规则 + ledger.csv），theme 按 no 轮换 blueprint/paper/swiss，每组 ≥5 条后比中位数
- 发表流程（用户授权智子代发）：ego-browser 草稿箱→贴图→悬停卡片点「发表」→编辑页底部「创作来源」选 **个人观点，仅供参考**（用户指定，勿选 AI 生成）→ 发表 → 弹窗再点发表 → 管理员扫码（必须 handOff 给用户）
- 渲染坑：标题高亮色块在 line-height<1.3 时会压住上一行；标题用 \n 手动断行防止孤字。
- 出图后先跑机械自检再交付：PIL 逐张统计暗像素占比与底 40px 墨迹，`dark%` 落在 3–7%、底边无墨（页脚内缩）为正常，接近 0 = 白卡或文字没渲出来；文字溢出看 render.py 有无 overflow 告警。探测通过只证明「有字且没画到边」，排版好不好仍要自己看一眼图再交付。
- 「一张图」类非新闻贴图（如 2026-10-07 亲密线）：`lines_cards.py posts/<id>.json --out <dir>`（paper 模板 + SVG 重画线条，4 卡）；post.json 加 `"evergreen": true` 跳过时效检查；图片里的文字用 `grounding.py image <图片URL> --text 转录.txt [--published D]` 记成证据（正文标【图片转录】），review 才能核对。重画他人作品要在卡片和正文写明「重画，非原图」+原作者。
- 审稿服务坑：`render.py`（贴图）与 `article.py render/draft`（长文）**两条通道都内嵌 review 闸门**，交互出片一律带 `GROUNDING_REVIEW_MODEL=glm-5.3-flash HTTPS_PROXY=http://127.0.0.1:6152`。贴图只加代理、不指定核对模型时会直接抛 `核对调用失败 The read operation timed out`——那是核对源超时，不是稿件问题，换模型原样重跑同一条命令即可，**别改稿、别用 GROUNDING_GATE=0 绕过**。模型次序：glm-5.3-flash 交互出片首选（能啃长文不超时）→ gpt-6-sol（长文上易超时）→ dogbooks gpt-6-luna（常 502 / SSL EOF）。系统 /usr/bin/python3（3.9）走代理会 SSL EOF，gate 子进程用 `GROUNDING_PYTHON=$(which python3)`（gate.py 已支持）。
- 长文封面 v2（10-02，用户嫌旧版「深蓝网格+整句标题」不行）：`ai-tietu/cover.py`。1068×455@2x；封面不复述标题，只放「栏目 tag + 大关键词 cover_word + 一行 cover_sub」；全部放中间 455 方块且靠上（iOS 头条标题叠在底部 ~40%）；draft 带 cover_info 显式 1:1 中心裁剪；三栏目三底色（A 暖纸橙 / B 墨黑朱红宋体 / C 深绿终端字）。改封面先跑 `cover_preview.py` 看仿微信列表图；已有草稿换封面用 draft/update（逐 index），不要新建草稿
- 内容存档（10-02 用户定）：长文+贴图文字源（md / post.json / caption.txt，不含 png/html）同步到私有仓库 marovole/ai-kuaixun-content（本地 ~/GitHub/个人作品集/ai-kuaixun-content）。脚本 ~/.hermes/scripts/content-repo-sync.py（无变更无输出，成功打印 PUSHED）。两个写作 cron 的 prompt 末步都调它；no_agent 兜底 cron c86203efc680 每晚 23:50。交互里改完稿子也顺手跑一次
- **贴图标题必须单独看得懂（10-07 用户定）**：读者在草稿箱/信息流里只看到这一条标题，不能依赖同系列前后条。写清主语+结论；禁用「它/他/这」指代开头和「…说起」「哪只手」「默认的直线」这类悬念半句。自检：只念标题给没看过前文的人，能复述出意思。系列多条（如诺奖 5 条）最容易犯，每条都要独立成立。已写入 ai-tietu/cron-prompt.md 与诺奖贴图 cron 提示词。
- **两条线区分度（10-02 用户定）**：长文=严肃深度（从业者读者，论证链、术语直用、克制）；贴图=通俗（非工程师，大白话、专业词带括号解释、数字换算成日常说法、标题每行≤8字）。同一事件：贴图讲「对普通人意味着什么」，长文讲「为什么/接下来」。规则写在 ai-tietu/cron-prompt.md 与 cron-prompt-longform.md 开头
- ai-tietu 脚本必须用 `env -u PYTHONPATH -u PYTHONHOME /usr/bin/python3` 跑：Hermes 环境泄漏的 PYTHONPATH 会让系统 python 加载 py3.14 的 urllib3 报 TypeError；homebrew python3 没有 playwright
- 长文（B 深度判断）落地序列：`article.py render <md>`（出 html + 封面；front matter 至少 title/digest/cover_kicker/cover_title，`\n` 手动断行）→ `grounding.py check` → `review` → **派独立 subagent（`delegate_task`）对照本地抓取原文逐句严苛事实核查并修完所有事实错误与措辞偏差（2026-11-07 用户硬性要求，写任何文章必做）** → 复跑 `check` + `review` → `article.py draft <md>`（内部再跑一次 gate，打印 `RECEIPT draft_media_id=…`；若已建草稿则用 `draft/update` 原地更新，勿重复建草稿）→ `content-repo-sync.py`。`render` 断言 title≤32 且按 `len()` 计、空格也算：中文标题带空格常卡在 34 字左右报 `AssertionError: title 超过 32 字`，压缩空格与标点后重跑，不要改标题措辞。同一条 `render` 断言还卡 `digest 超过 120 字`：digest 按字符计，写成两句完整摘要必超（90–100 字才稳），压缩后重跑 render，不要为凑长度改正文。整篇长文的核对模型用 `GROUNDING_REVIEW_MODEL=glm-5.3-flash`（默认推理型核对模型常返回空正文，见 content-grounding）。
- **写作模型（10-02 用户定）**：公众号长文 + 贴图文案一律用 Gemini 3.8 Flash（`--provider antigravity-oauth -m gemini-3.8-flash`，走 Antigravity 订阅额度，用户认为它最擅长写作）。cron cb3ae0a9b0a3/97034ee88833/42e9bc5fde3c/91775eae2d6a 已 pin 该模型。交互会话里写稿：起草正文交给 `hermes -z "<完整写作指令+素材>" --provider antigravity-oauth -m gemini-3.8-flash` 产出，主模型只做选题/核实/排版/推草稿；新建写作 cron 同样 pin。agy 登录失效时先 `hermes auth status antigravity-oauth`，不要静默换回其他模型

## ⚠️ 旧管道状态：已暂停（2026-08-09 · Week 32）

**权威文件**：`ideas/inbox.md` 顶部状态块 + `review/weekly-review.md` + `review/2026-08-09-weekly-review.md`。

| 项 | 现状 |
|----|------|
| queue | **0**（48 篇已移入 `review/archived-2026-08-09/`：x31 + wechat5 + xhs12；未删除） |
| published | 自 2026-06-22 启动以来仍为 **0** |
| 生成 cron（X/公众号/小红书） | **禁止自动回灌**新草稿 |
| x-pulse / 情报日报 | 可继续写 vault + 邮件；**不要**再向 `ideas/inbox.md`「待筛选」追加创作选题 |
| 周复盘 cron | 无发布且无重启声明时，可 `[SILENT]` 或极短状态，避免空转长文 |

### 生成 cron 每次启动必读

1. 读 `ideas/inbox.md` 顶部：若写着「管道已暂停 / Pipeline Paused」→ **跳过生成**，输出状态报告（引用恢复条件），**不写** queue 新文件。
2. 恢复条件须**同时**满足才可生成：
   - `published/` 近 7 天 ≥ 2 篇（任意平台）
   - `queue/x` ≤ 5，`queue/xiaohongshu` ≤ 3，`queue/wechat` ≤ 1
   - inbox 待筛选：兴趣1 游戏 ≥ 3 且 兴趣2 纯硬件 ≥ 2
   - 用户显式说「恢复内容管道」
3. 未满足时即使用户没说暂停：仍执行原 **3a 发布队列深度检查**（queue>10 且 7 日 0 发布 → 跳过）。

### 若要重启 — 只做这一件

先从归档取峰值稿人工发布，**不要先开生成**：

1. `review/archived-2026-08-09/wechat/2026-07-15-weekly.md`（「好的产品敢让你费点劲」）
2. 备用：同目录 `wechat/2026-07-29-weekly.md`、`x/2026-07-05-1.md`、`xiaohongshu/2026-07-06-1.md`

### 闸门覆盖面

- X / 小红书：3a 闸门 + 暂停旗标
- **公众号 cron 也曾漏生成**（07-29 在零发布期仍产出 1 篇）→ wechat 生成前同样读暂停旗标 + 近 7 天 published / queue 上限
- x-pulse 与创作管道**解耦**：日报价值独立；职业底色堆进待筛选会制造虚假选题丰富度（暂停期实测 ~45 条几乎全职业底色，游戏/纯硬件 = 0）

## Obsidian 内容队列路径

```
VAULT="/Users/marovole/Library/CloudStorage/Dropbox/Obsidian Vault"
CONTENT_DIR="${VAULT}/05-Outputs/content-creator"
```

### 目录结构

```
05-Outputs/content-creator/
├── queue/           # 待审核的草稿
│   ├── x/           # X/Twitter 草稿
│   ├── wechat/      # 公众号草稿
│   └── xiaohongshu/ # 小红书草稿
├── published/       # 已发布内容存档
│   ├── x/
│   ├── wechat/
│   └── xiaohongshu/
├── ideas/           # 选题灵感池
│   └── inbox.md     # 随时收集的灵感（顶部含管道暂停旗标）
├── templates/       # 各平台模板
│   ├── x-single.md
│   ├── x-thread.md
│   ├── wechat.md
│   └── xiaohongshu.md
├── assets/          # 配图素材
├── review/          # 审核日志（每周复盘用）
    ├── weekly-review.md              # 最新复盘速览
    ├── YYYY-MM-DD-weekly-review.md   # 历史完整复盘
    └── archived-YYYY-MM-DD/          # 暂停/清空时的草稿整包归档（可 mv 回 queue）
```

## 选题来源

### 自动采集（cron + RSS）
- Smol AI News RSS（已有 cron job）
- Hacker News 热帖
- Reddit: r/macapps, r/Switch, r/Design, r/typography, r/Biohackers
- X 信息流策展（手动 + 半自动）

### 外网热帖改写（英文热帖 → 中文帖 + 卡片图）

用户丢一条海外热帖链接说「实践一下这个做法」时的固定流程：

1. **取周榜**：`reddit.com/r/<sub>/top/?t=week`（TIL 类用 r/todayilearned，科技类用 r/technology）。页面上的 score / 评论数是可核事实，可以引用；「浏览上千万」这类页面看不见的指标不要写。
2. **热帖标题只是线索，不是来源**。点开帖子外链或媒体报道核对原文；标题里的数字一律回溯原始报道再写。
3. **按账号主线选材**：默认挑 AI / 科技 / 工程向；名人轶事类即使 score 更高也丢掉（个人号主轴是 AI+科技+财富）。
4. **写成中文**：结论句开头 → 一到两个可核细节 → 来源链接。按 X 单条帖的口气，不写「据报道」式翻译腔，也不复述原文的营销口吻。
5. **配一张中文大字卡片**（`image-generation` 方案 E），出图必须 vision 逐字转录核验。
6. **发前把稿子和图一起给用户拍板，默认不发**（见 Pitfalls 4）。「实践一下这个做法」= 走到可发状态并交付草稿，不是发布授权。

**热帖本身指向一个开源仓库时**（清单类、工具类、awesome-* 类帖最常见）：热帖给的星数、协议、维护状态一律现抓核实，别信转述。

1. `api.github.com/repos/<owner>/<repo>` 取 `stargazers_count` / `open_issues_count` / `pushed_at` / `created_at`；热帖写的「10万Star」「MIT 协议」经常过时或抄错。
2. 授权要逐个文件看：`LICENSE`、`README.md` 末尾、`package.json`（含 npm registry 上的包）三处常互相打架，一篇稿子里并列出这种不一致，比复述「MIT 开源」有分量得多。
3. 回答「它为什么活了十年」不看条目数量，看产线：近一月合入 PR 数（搜索 API `merged:>YYYY-MM-DD`）、镜像累计 pulls、`build/` 下有没有把 README 编译成 JSON 的脚本、`.codex|.claude/skills/` 里有没有写给自己看的 SKILL.md。这几样才是热帖里没有的独家事实。

核对时优先用「标题说法 vs 原文说法」并列出偏差：二手标题最常见的错法是压掉分母（见 `content-grounding` 的二手标题 pitfall）。稿子里顺手指出偏差，反而比照抄更有价值。

### 个人素材
- Obsidian 日记中的灵感
- Neumina 构建日志
- 个人设备/游戏/软件使用体验
- 读书/看片/玩游戏后的思考

### 三级选题树生成法（Research-Backed Content Map Prompt）

当用户要求「规划未来 1-2 个月选题」「生成内容地图」或补充选题池时，拒绝临时拍脑袋，按以下工作流执行：

> 用户丢来海外创作者方法论（「学习一下，有什么可以借鉴」「整合进 skill 并落地」）时，按 [references/external-framework-integration.md](references/external-framework-integration.md) 走：拆机制/广告 → 决定落哪一层 → 四件套交付（SSOT + 内容地图 + 一个成品稿 + 接进 cron prompt）。只改 skill 不交成品稿、不挂载到 cron，等于没落地。

1. **挂载双文档**：读取 `BRAND-SIGNATURE-FEILENGCUI.md`（Brand & Content Signature）+ 近期已核验的一手情报源（`news.neumabio.xyz` 简报 json / `x-pulse` 一手深潜报告）。
2. **跨平台结构降维**：优先从**非目标发布平台**（例如用海外 X 长文/Substack 爆款结构反哺公众号与短视频，用硬核工程报告反哺小白说明书）提取高留存叙事结构。
3. **执行三级分叉 Prompt 生成 `ideas/content-map-YYYY-MM.md`**：
   ```text
   基于 [BRAND-SIGNATURE-FEILENGCUI.md] 的 Part 0 个人 IP 原则（「不用学写代码，学会像产品经理一样指挥 AI」，三步法：说清需求/拆成步骤/验收结果）和独特透镜（12年 PM + 非技术公司一线 FDE + 工程审美），结合近期已核验的一手情报，生成一份研究背书的三级内容地图（Content Map）。每个选题必须标注：真实提问原话（或「无」）、主讲哪一步、ip_fit（0-5）、所属线（方法演示 70% / FDE 现场 20% / 立场观点 10%）：
   - 第一级（Pillars）：3 个核心内容支柱（① AI 工程与 Agent 真相；②《零基础AI说明书》与 FDE 落地；③ AI 时代的财富、算力与个人杠杆）
   - 第二级（Topics）：每个支柱分支出 2–3 个当前高痛点子话题
   - 第三级（Verified Ideas）：每个子话题分支出 3–5 个带一手硬数字/真实例证的高潜力选题
   - 第四级（4 Angles 一鱼四吃）：每个选题固定展开 4 个跨平台切角：
     * 切角 A【60-85s 深蓝硬数字短视频】：反直觉硬数字前 3 秒砸脸（限 1 年内新研究与当季最新模型）→ 实验对比 → 1 个动作
     * 切角 B【FDE 小白说明书】：真实提问开场 → 同一任务「随手问 vs 按三步法」并排实测 → 实测耗时/费用 + slogan 收口（竖屏≤130s，结构见 topic-to-matrix/references/ip-principle.md）
     * 切角 C【PM 深度判断长文】：系统机制 + $/task 单位经济学 + 「我还没想清楚的地方」
     * 切角 D【公开重构 Public Teardown】：还原某传统岗位低效一天 vs 2026 Agent 管线 10 分钟重构方案
   ```

### 公开工作流重构专栏（Public Teardown / Permissionless Apprentice）

用于《零基础AI说明书》深度线及 B 端咨询/内训引流（存放于 `ideas/public-teardown-*.md` 或推入长文次条）：
1. **选靶**：挑一个具体的传统低效工作场景（如“买了 20 个 AI 账号却只会当百度用的业务团队”、“每天花 3 小时对账做表的运营”、“靠复制粘贴写周报的 PM”）。
2. **对比拆解**：先还原旧做法的崩溃现场（痛点原话），再给出用「本地纯文本 + Git 撤销键 + Grounding 对账门禁 + 封装 Skill」重做的 3 步方案，附上真实耗时与 Token 成本。
3. **硬核背书**：必须嵌入至少 2 组当周已核验的一手行业硬数字（如 Multi-step SWE 通关率、GDPx 基准、大厂预算变动），拒绝空谈方法论。

### 选题→草稿流程

1. **灵感入池**：任何来源的灵感写入 `ideas/inbox.md`
2. **选题评估**：每周日 cron 自动筛选最佳选题，生成下周排期
3. **预生成审计（每次生成前必做）**：读取 inbox.md 后，先扫描"待筛选"池中是否有已被其他平台/日期生成但未移入"已用"的灵感。方法：检查"已用"列表是否有同源灵感，或对照 queue/ 各子目录的已有草稿。发现漂移项立即移入"已用"，避免重复生成或选题混乱。
3a. **发布队列深度检查（每次生成前必做，在预生成审计之后）**：统计 `queue/{platform}/` 下当前平台待发布草稿数量，以及最近 7 天 `published/{platform}/` 的实际发布量。判定规则：
   - **queue/{platform}/ 积压 > 10 篇 且 最近 7 天 published 为 0** → **跳过本次生成**，输出改为"⚠️ 发布队列积压 N 篇，连续 0 发布。今日不生成新草稿。请审核 queue 中已有草稿并发布，优先选 quality 最高的。"并列出 queue 中按创建时间排序的前 5 篇草稿标题供用户选择。
   - **queue 积压 5-10 篇 且 最近 7 天发布 < 2** → 降频至生成 1 篇（而非 2 篇），并在输出中标注降频原因。
   - **queue 积压 < 5 篇 或 最近 7 天发布 ≥ 2** → 正常生成。
   这条规则防止"生成 cron 持续堆积草稿但用户从不发布"的失衡——2026-06-22~07-07 实测中连续两周生成 38 篇零发布，根因就是生成 cron 没有这道闸门。实测中多次发现跨平台生成后 inbox 未同步（如 xiaohongshu 草稿已生成但灵感仍在"待筛选"）。
4. **草稿生成**：按排期，cron 每日/每周生成对应平台草稿。生成后**立即更新 inbox.md**，将已生成的灵感从"待筛选"移入"已用"（附文件路径）或移入"已排期"
5. **池余量检查（生成后必做）**：更新 inbox.md 后检查"待筛选"池剩余数量。如果 < 5 个，在输出中提醒用户补充灵感，并在周日复盘时优先处理。不要等周复盘才发现池子空了。
4. **人工审核**：用户审核 queue/ 中的草稿，修改/批准/拒绝
5. **发布**：批准后通过 xurl（X）或 md2wechat（公众号）发布。发布后将草稿从 queue/ 移入 published/
6. **归档**：发布后移入 published/，记录数据

## 草稿模板

### X 单条帖模板（同 `references/templates.md` 的 x-single）

```markdown
---
platform: x
type: single | thread
lens: [透镜1-7名称]
status: draft
created: YYYY-MM-DD
---

# [标题/首行钩子]

[正文内容]

§

[可选：配图说明]

**配图**: [描述需要的配图风格，由AI生成]
**发布时间**: [建议时间]
**标签**: #[相关标签]
```

### 公众号模板（同 `references/templates.md` 的 wechat）

```markdown
---
platform: wechat
type: deep-dive
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
target_length: 1500-3000
---

# [标题：有观点的标题]

## 导语
[100字以内的引子，制造好奇]

## 正文

### [小标题1]
[内容]

### [小标题2]
[内容]

### [小标题3]
[内容]

## 结尾
[总结 + 个人立场 + CTA]

---
**配图需求**: [列出需要的配图]
**发布命令**: `md2wechat publish [file] --mode ai --theme autumn-warm`
```

### 小红书模板（同 `references/templates.md` 的 xiaohongshu）

```markdown
---
platform: xiaohongshu
type: visual | guide | review
lens: [透镜名称]
status: draft
created: YYYY-MM-DD
images: [数量]
---

# [标题：emoji + 吸引眼球但不标题党]

[200-400字正文]
[第一人称，口语化但不low]
[有明确观点和推荐/不推荐]

§

**配图需求**:
1. [封面图描述]
2-9. [内容图描述]

**标签**: #标签1 #标签2
```

## 去 AI 味（Humanizer）

所有草稿生成后，必须执行 Humanizer 步骤。加载 `creative-content-tools` skill，参照其 29 种 AI 写作模式清单逐条检查。

### 高频 AI 味清单（每条草稿必须检查）

1. **负面平行主义**："不是X，是Y" / "不仅X，更Y" → 最多用1次，多了就是 AI
2. **三段式强迫**：凡事都列三点 → 打散，有的给两点有的给四点
3. **破折号过度**：AI 特别喜欢用破折号做补充说明 → 改成句号断句或括号
4. **权威套路**："一个更底层的问题" / "真正的关键是" → 删掉前缀直接说
5. **翻译腔**："跃迁" / "范式" / "赋能" → 换成人话
6. **对称强迫**：整篇 A→B→C 完美递进 → 允许跑题、啰嗦、重复
7. **收尾金句**：最后一句必须是"升华" → 砍掉，或改成具体的、未完成的思考
8. **表演感**："我赌后者" / "答案很简单" → 换成犹豫的、真实的语气
9. **过度书面化**：连词堆砌、定语过长 → 短句、口语
10. **Em dash 滥用**：— 出现超过2次 → 减少到0-1次

### Humanizer 执行步骤

1. 生成草稿后，扫描上述10种模式
2. 逐条修正
3. 注入人感：句子长短不一、允许口语词、允许犹豫和跑题
4. 最终自问："这段话如果是我自己打字发的，会这么写吗？"
5. 在 frontmatter 中标记 `humanizer_pass: 1`

### 翡冷翠的人感特征

- 说话有犹豫和修正（"看你怎么定义'够'"）
- 会用具体场景代替抽象论述（"活动监视器红一片"）
- 会有真实情绪（"烦的不是慢，是总得管"）
- 结尾不升华，停在具体的判断上
- § 符号偶尔用，不是每段都用
- 技术术语不翻译，直接用英文原词

## 内容调性检查清单

每篇草稿生成后，AI 自动执行以下检查（写入草稿末尾）：

```
## 自检清单
- [ ] 有明确观点/立场（不是信息搬运）
- [ ] 有具体细节支撑（不是空泛论述）
- [ ] 不追热点（不是"XX又更新了"式内容）
- [ ] 有个人色彩（只有翡冷翠能写的内容）
- [ ] 配图需求明确
- [ ] 不超过平台字数限制（X: 280字符/条，公众号: 1500-3000字，小红书: 200-400字）
- [ ] 跨领域连接（从兴趣出发，用职业视角拆解）
```

## 发布工作流

### X/Twitter 发布

**方式 A：ego-browser 网页发推（默认首选，`@marovole` 在 Default profile 已登录）**
1. 新建或复用 Default profile 的 TaskSpace，打开 `https://x.com/compose/post`，等 `[data-testid="tweetTextarea_0"]`（或 `loc=role:textbox[name="Post text"]`）可见。
2. 点击文本框后用 `page.keyboard.insertText(copy)` 一次性填入；中文长文别逐字 type（易丢字、触发草稿自动保存）。
3. 上传媒体：`/compose/post` 同时渲染弹窗和底层时间线的多个隐藏 `input[type="file"]`，一律给目标 input 打临时属性再 setInputFiles，别用 `>> nth=0`——Thread 里 `nth=0` 会把图挂到首帖：
   ```js
   await page.evaluate(() => {
     document.querySelectorAll('[data-x-up]').forEach(e => e.removeAttribute('data-x-up'));
     const dlg = document.querySelector('[role="dialog"]') || document;
     const inps = [...dlg.querySelectorAll('input[type="file"]')];
     inps[inps.length - 1].setAttribute('data-x-up', '1');
   });
   await page.setInputFiles('input[data-x-up="1"]', [abs]);
   ```
4. 视频上传后轮询 `page.snapshot()`，确认媒体状态从 `Processing` 变为 `Ready`（此时先不要点 Post）。
5. **发前审核门禁**：在发帖框已填好、媒体已 `Ready` 的状态下，向用户展示候选文案（可用 `clarify` 提供推荐文案与备选），待用户拍板后再点击 `[data-testid="tweetButton"]`（或 `loc=css:div[role="dialog"] button:has-text("Post") >> nth=-1`）。
6. **发布后核验**：见下「发布后核验」。

**方式 A-Thread：一次发多帖 Thread**
1. 填第 0 条：点 `[data-testid="tweetTextarea_0"]` 后 insertText。
2. 点 `[data-testid="addButton"]` 追加下一条，等 `[data-testid="tweetTextarea_1"]` 出现再填；索引按追加顺序递增，已填的 textarea 不会消失。
3. 某条要配图就填完该条立刻按第 3 步上传（先点该条的 textarea，再标 input），逐条上传。
4. 全部填完等 2–3 秒、截图确认条数与每条配图，再点一次 `[data-testid="tweetButton"]` 整串发出。Thread 一发出即公开，发前门禁同单帖。

**方式 A-定时发布（X 网页端排期，多帖跨天时首选）**
1. `https://x.com/compose/post` → 在弹窗里点 `[data-testid="scheduleOption"]`，等排期面板出现（六个原生 `select`：`#SELECTOR_1..6` = 月 / 日 / 年 / 时 / 分 / AM-PM）。全部用 `page.selectOption` 设，不要点日历。
2. 设完读 `[role="dialog"]` 里的 `Will send on …` 与目标时间逐字对一遍，再点 `[data-testid="scheduledConfirmationPrimaryAction"]`（或文案为 `Confirm` 的按钮）。
3. 确认之后才回到发帖框填正文（`insertText`）并上传媒体（打 `data-x-up` 临时属性再 `setInputFiles`，同上）。
4. **发前门禁**：媒体图数达到预期、`[data-testid="tweetButton"]` 文案为 `Schedule` 且未 disabled、`Will send on` 行仍在，三条都满足才点。
5. 弹窗消失即提交成功；收尾去 `https://x.com/compose/post/unsent/scheduled` 把每条的时间与首句读回来核对。

**发布后核验（单帖与 Thread 通用）**
- 必须**重新加载** `https://x.com/marovole`（再 `reload()`），滚 3–4 屏读 `article` 文本前缀与 `a[href*="/status/"]`。刚点完就跳转常拿到旧快照，看不到新帖不等于没发出去，不要因此重发。
- Thread 会拆成多条独立 status、同一时间戳相邻排列；汇报给**首帖**链接，并核对条数与实际发帖数一致。
- 收尾 `await task.finish({ keep: [] })`。

**方式 B：xurl CLI（需已配置 OAuth 凭据）**
```bash
# 前提：xurl 已完成 OAuth 认证（验证：xurl auth status）
xurl media upload /path/to/image.png   # → 返回 MEDIA_ID
xurl post "内容文本" --media-id MEDIA_ID
```

### 公众号发布
```bash
# 1. 审核草稿后，用 md2wechat 发布
md2wechat publish [草稿文件路径] --mode ai --theme autumn-warm

# 2. 或先预览
md2wechat preview [草稿文件路径] --mode ai --theme autumn-warm
```

### 小红书发布
- 目前无 CLI 自动发布工具
- AI 生成草稿 + 配图需求 → 人工在 App 内发布
- 未来可考虑浏览器自动化

## Cron 排期

### 每日 X 草稿生成（每日 7:00）
- 读取 `ideas/inbox.md` + RSS 素材
- 按当日透镜（周一=AI/产品，周二=游戏/硬件...）
- 生成 1-2 条 X 草稿 → `queue/x/`
- 通知用户审核

### 每日 x-pulse AI/科技日报（每日 9:15）
- Job：`2fab94f5879a` · schedule `15 9 * * *` · pin `xai-oauth`/`grok-4.5`
- 产出：`VAULT/AI-Newsletter-Second-Brain/x-pulse/YYYY-MM-DD-xai-ai-tech-daily.md`
- 选题：管道**未暂停**时最多 3 条写入 `ideas/inbox.md`（标注 `x-pulse YYYY-MM-DD`）；**暂停期只写日报/邮件，不追加待筛选**（情报与创作解耦）
- 邮件：跑 `python3 ~/.hermes/scripts/send-xpulse-daily-email.py <当日md>` → To `<EMAIL>` / CC `<EMAIL>`（Apple Mail）
- Prompt 备份：`~/.hermes/scripts/xai-ai-tech-daily-prompt.md`
- 详情与 fallback：`references/x-pulse-source-integration.md`
- **用户再说「要个 X 科技日报」时：update 此 job，禁止新建重复 cron**
- X 层：`xurl` 常 `No apps registered` → 允许 web/HN/jina partial；**禁止编造** X 互动数

### 每周公众号草稿（周三 9:00）
- 从本周 X 高互动帖 + 选题池中选最佳主题
- 生成公众号深度草稿 → `queue/wechat/`
- 通知用户审核，目标周五发布

### 周三 Thread 深度分析结构

周三的 Thread 是每周最深度的内容，跨 2-3 个兴趣用职业底色拆解。从已发布的两条 Wednesday Thread（Death Stranding 菜单 / 不可逆设计）中提炼出以下结构：

1. **Post 1 钩子**：个人体验切入（"玩了40小时 X，最反复琢磨的是…"），不要宏大开篇。PM 视角亮明身份但用犹豫语气。
2. **Post 2-3 拆解**：2-3 个不同领域的具体例子，每个附可感知细节（不是抽象论述）。例子之间是同一逻辑的不同切面，不是递进。
3. **Post 4-5 合成**：从例子中提炼一个 PM 判断，落在产品决策上。"做产品12年，我越来越觉得…"是典型句式，后面接具体判断而非金句。
4. **Post 6 落地**：停在具体判断上，不升华。允许"不是说 X 不好"式的犹豫和自我修正。

关键：Thread 的最后一帖必须是可操作的判断或未完成的思考，不能是"这就是为什么 X 如此重要"式收尾。

### 每周小红书草稿（周一/周四 10:00）
- 生成 2-3 条小红书草稿 → `queue/xiaohongshu/`
- 附带配图需求描述

### 每周复盘（周日 cron，如当前 cron 周期）

**前置检查**：确认所在周期是周日。如果 cron 触发在其他日期，先确定当前最近的完整周（上周一~上周日）。

**执行步骤**：

1. **读入数据**
   - 列出 `published/` 下所有子目录（x/ wechat/ xiaohongshu/）的已发布文件 → 本周发布统计
   - 列出 `queue/` 下所有子目录的草稿文件 → 本周产出统计（生成量 vs 发布量）
   - 读取 `ideas/inbox.md` → 选题池状态（待筛选 / 已排期 / 已用）
   - 读取上一期复盘（`review/` 目录下日期最新的文件）→ 上周调整项追踪

2. **生成复盘报告**
   - 文件名格式：`review/YYYY-MM-DD-weekly-review.md`
   - 使用 skill 中"周复盘模板"框架，但需扩展以下部分：
     - **发布统计**：计划 vs 实际 vs 最优帖
     - **兴趣覆盖**：逐兴趣统计本周草稿的 lens 分布（从 frontmatter 提取）
     - **Humanizer 质量**：逐份草稿检查 humanizer_pass 标记，统计 AI 味残留
     - **选题池筛选**：从 inbox.md 待筛选池选出下周 3-5 个优先选题
     - **下周排期建议**：按日安排发布顺序 + 兴趣偏重建议
     - **观察与调整**：管道健康度（生成量/发布量比率）、内容质量趋势、系统问题

3. **清理 inbox.md**
   - 将本周已生成草稿的灵感项从"待筛选"移入"已用"（附带生成文件路径）
   - 将本周已排期的项从"已排期"移入"已用"
   - 保持"待筛选"池不为空（留至少 5 个选项供下周生成 cron 使用）

4. **输出摘要**
   - 评论区发送本周复盘摘要（包含关键数字、最高质量草稿、核心建议）

**无前次复盘的兜底**：如果 `review/` 目录为空或无最近文件，这是首次复盘，跳过追踪环节，直接输出当前数据作为基准。

## 互动策略

### 目标互动账号（按透镜分组）
- **AI/产品**：@karpathy, @sama, @rowancheung, @levelsio
- **Biohacking**：@DrAndyGalpin, @peterattiamd, @hubermanlab
- **游戏/设计**：@davidhellman, @NoelFB, @Enichan (独立游戏开发者)
- **硬件**：@reneritchie, @DaringFireball, @stroughtonsmith
- **中文区**：@dotey, @FinanceYF5, @op7418

### 互动规则
- 每天去 5 个目标账号留高质量评论（有信息增量，不是"好文"）
- 发帖后 2h 内回复所有评论（触发算法加权）
- 被大V回复/转发时，及时跟进回复

## 周复盘模板

```markdown
# Week [N] 复盘 — YYYY-MM-DD

## 发布统计
| 平台 | 计划 | 实际 | 最优帖 |
|------|------|------|--------|
| X    | 7-14 |      |        |
| 公众号 | 1   |      |        |
| 小红书 | 2-3 |      |        |

## 数据
- 周初粉丝: 
- 周末粉丝: 
- 新增: 
- 最高浏览: 
- 最高收藏: 
- 最高互动: 

## 内容反馈
- 收藏率最高: 
- 互动率最高: 
- 被大V互动: [是/否]

## 领域覆盖
- [ ] 职业底色 (PM/AI 开发)
- [ ] 兴趣1: 游戏
- [ ] 兴趣2: 硬件
- [ ] 兴趣3: 美学艺术
- [ ] 兴趣4: 文化艺术

## 下周调整
- 增加的领域: 
- 减少的领域: 
- 新尝试: 
```

## Pitfalls

1. **X 发布优先走 ego-browser Default profile** — `xurl` 未注册 app 时直接用 `ego-browser` 的 Default profile（已登录 `@marovole`）发推；`/compose/post` 有多个隐藏 `input[type="file"]`，上传前给目标 input 打临时属性再 `setInputFiles`（`>> nth=0` 在 Thread 里会把图挂到首帖），等状态变 `Ready`，经用户确认后再点 Post
2. **公众号 md2wechat 需要有效凭据** — 检查 `~/.config/md2wechat/config.yaml`
3. **小红书无 CLI 工具** — 只能生成草稿+配图需求，人工发布
4. **不要自动发布** — 所有内容必须经过用户审核后才发布
5. **配图不能1K** — 使用 GPT-image-2 或 FLUX 2，至少 2K 分辨率
6. **跨领域连接是核心** — 从兴趣出发，用职业视角拆解，避免单一领域自嗨
7. **Obsidian 路径** — 使用 Dropbox vault 路径，不是默认 Documents 路径
8. **模板文件在 Obsidian 和 skill 中各有一份** — Obsidian 中的 `templates/` 是用户实际使用的模板；`references/templates/` 是 skill 的参考副本。如果更新模板，两处都需更新。
9. **管道健康度监控** — 每周复盘需计算"生成量 vs 发布量"比率。如果 queue 持续积压（发布量 << 生成量），说明管道瓶颈在审核环节，应减少生成频率或提醒用户审核，而非继续增量。**但这不应只在周复盘才被发现** — 每日生成 cron 必须执行步骤 3a「发布队列深度检查」作为前置闸门：queue/{platform}/ 积压 > 10 篇且近 7 天零发布 → 跳过生成，改为催发布。2026-06-22~07-07 实测连续两周生成 38 篇零发布，就是因为只有周复盘才检查、生成 cron 无闸门。
10. **inbox.md 漂移** — 跨平台生成（如小红书 cron 和 X cron 在不同时间运行）容易导致灵感被使用后未同步移入"已用"。表现为"待筛选"池中残留已生成草稿的灵感。预生成审计步骤（流程步骤3）专门处理此问题，但根本解法是每次生成后立即更新 inbox，不要批量延迟到周复盘
11. **待筛选池下限** — 池中灵感 < 5 个时，周日复盘应优先从 RSS/个人素材补充，否则下周每日生成 cron 会因选题不足而重复已有角度或降低质量
12. **xAI/x-pulse 配额周期性耗尽** — xAI 的 `x_search` 和 `web_search` 共享同一配额池（月度账单制）。每月上旬（1-10 日）可用，中下旬（11 日-月底）经常 403。x-pulse cron 需内置 fallback 检测：若 `x_search`/`web_search` 均返回 403/空结果，自动切换为浏览器直采 HN + VentureBeat（可用 HN Algolia `front_page` API 作 HN 捷径）。详见 `references/x-pulse-source-integration.md`。不要连续多日在无配额下重试 API 调用却不 fallback — 那样会产出空报告。
13. **web_extract 受 Surge Fake-IP 拦截** — 在 Surge TUN 模式下，`web_extract` 对多数域名返回 `198.18.x.x` 私有 IP 错误。x-pulse 日报若依赖 `web_extract` 获取正文需先确认 Surge 状态。可靠替代：`browser_navigate` 直接访问。
14. **x-pulse cron 必须 pin 模型，禁止重复建任务** — 用户要「每天 X 科技资讯日报」时，先查既有 job `2fab94f5879a`（**`15 9 * * *`**），**修复/更新它**，不要再 `create` 一份。未 pin 时全局模型一变（如切到 openai-codex）会被 skip：`Skipped to prevent unintended spend: global inference config drifted`。正确配置：`provider=xai-oauth` + `model=grok-4.5` + `deliver=local`（邮件走脚本，不走 Hermes `deliver=email`）+ toolsets `[web,browser,terminal,file,skills]` + prompt 内嵌 xAI 配额 fallback + 收尾调用 `send-xpulse-daily-email.py`。修完后 `cron run` 补跑并确认 vault 当日 md + `last_status=ok` + 邮件 stdout 含 `OK emailed via Apple Mail`。旧的泛「科技日报」(`a2c541cbfcb0`, deliver=email) 与 x-pulse 重叠且投递易挂，应 pause 而非并行。
15. **情报日报邮件推送 = Apple Mail 脚本，不是 Hermes email platform** — Hermes `deliver=email` 依赖 `EMAIL_*` + `EMAIL_HOME_ADDRESS`（当前未配会 `no delivery target resolved`）。ClawEmail/`mail-cli` 可能 JWT 有效仍 `COREMAIL_UPSTREAM_ERROR`。x-pulse 与同类 digest 统一：`deliver=local` + `python3 ~/.hermes/scripts/send-xpulse-daily-email.py <md>`（Mail.app Google=`<EMAIL>`，CC 次邮）。正文 ASCII 摘要 + 中文 Markdown 附件（AppleScript `-e` 中文易炸）。详见 `email-clients` skill。

16. **重排期 = 删旧 + 重排，两个平台都不会去重** — 已经排过一条内容再排一次，后台会留两条同时间同标题的条目。X 进 `/compose/post/unsent/scheduled` 点 `Edit` 进多选、勾中旧那条（行左侧 checkbox）、`Delete`、确认框 `[data-testid="confirmationSheetConfirm"]`；小红书进 note-manager 悬停旧卡最右图标删。改稿也走「重新上传一版 + 删旧卡」，不碰网页端的编辑入口（点进去常不跳发布页）。排期提交后的 URL / 成功弹窗都不是判据，必须回后台列表逐条比对精确时间。
17. **发布 payload 里的 `$` 会被 shell 吃掉** — 用双引号 shell 字符串/heredoc 生成 JSON/JS 发布包时，`$39/月` 会被展开成 `9/月`（`$3` 当变量），字符级损坏肉眼极难发现。用 `write_file` 或转义 heredoc（`<<'EOF'`）写 payload；填表后用 evaluate 从页面回读实际文本与源稿做一次比对再提交。

## 与相关 Skill 的边界

| Skill | 职责 | 何时加载 |
|-------|------|----------|
| `content-creator-pipeline`（本 skill） | 日常运营：选题→草稿→审核→发布→复盘 | 用户要生成/审核/发布内容时 |
| `x-brand-strategy-planning` | 战略层：账号定位、Bio设计、重启策略、增长阶段规划 | 用户要重新定位、改Bio、规划增长阶段时 |
| `content-pipeline` | 素材采集：RSS监控、YouTube转录、Newsletter digest | 用户要监控信息源、采集素材时 |
| `social-platforms` (xurl) | 发布工具：X API 操作（post/search/media） | 用户要直接操作 X API 时 |

典型流程：`content-pipeline` 采集素材 → `content-creator-pipeline` 生成草稿 → `social-platforms` 发布到 X