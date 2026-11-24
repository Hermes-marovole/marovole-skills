# 调研与信息抓取技能体系与标准工作流

> 把「联网搜一搜 → 贴二手摘要」升级为可复现、可核验的工程化情报管线：覆盖 **多引擎搜索路由、反爬恢复与真实浏览器抓取、专项平台提取、四重事实核查闸门、14 维大样本商业/App/AI 调研与定时信息差监控**，共 **16 个核心 Skill + 1 个后台只读防护 Skill**、**28 个自动化脚本（22 Python / 3 Swift / 2 Shell / 1 Frida JS）**。

---

## 一、四层架构总览

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 4 · 深度调研、竞品拆解与持续监控（Research, Teardown & Monitoring）      │
│  market-intelligence · mobile-app-teardown · horizontal-vertical-analysis    │
│  ai-research-comparison · reference-video-teardown · info-gap-agent-workflow │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 3 · 事实核查与引用溯源闸门（Grounding & Verification — 强制门禁）        │
│  content-grounding (grounding.py + facts_check.py)                           │
│  grounded-citations (sources.py 逐字引语与台账校验)                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 2 · 专项内容提取与知识沉淀（Extraction & Curation）                      │
│  x2doc (X 帖子/长文/Space/论文与工具打假) · link2doc (多链接聚合策展)          │
│  book-and-pdf-sourcing (电子书/扫描 PDF 找源、OCR 与双语翻译)                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ Layer 1 · 多引擎搜索、反爬恢复与网页抓取（Acquisition & Scraping）             │
│  web-search (7 引擎路由 + CF Crawl + 域名情报) · url-to-markdown (含 doc2md)  │
│  blocked-page-recovery (5 级反爬恢复梯) · web-crawler (四引擎与批量 UGC)       │
│  dokobot (真实 Chrome 登录态读取) · browser-automation-guardrails (后台只读)  │
└──────────────────────────────────────────────────────────────────────────────┘
```

> **环境部署与 API Key 领齐**：首次在新机器或 Claude Code / Hermes 上配齐这套栈（Exa / Tavily / Firecrawl / Serper / Brave / TinyFish / OpenCLI / Dokobot / DDGS），直接按 [handoff-hermes-market-intelligence-setup-v1.0.md](handoff-hermes-market-intelligence-setup-v1.0.md) 执行，并用 `skills/research/market-intelligence/scripts/verify_stack.py` 跑通六层实测验收。

---

## 二、16 个核心技能与职责矩阵

### Layer 1：搜索与网页抓取（Acquisition & Scraping）

| Skill | 路径 | 解决什么问题 | 关键脚本 / 参考 |
|---|---|---|---|
| **web-search** | [skills/research/web-search/](../skills/research/web-search/) | 统一多引擎搜索与提取（Exa / Tavily / Serper / Brave / Firecrawl / TinyFish / DDGS / xAI Grok），含 Cloudflare Crawl、域名情报与 Surge fake-IP 排障 | `scripts/search.py`, `cf_crawl.py`, `domain_intel.py`, `duckduckgo.sh` |
| **blocked-page-recovery** | [skills/web/blocked-page-recovery/](../skills/web/blocked-page-recovery/) | 403/429、付费墙、Cloudflare/DDoS-Guard WAF 与国内平台登录墙的 5 级恢复梯 + 假 200 拦截（Google Cache/AMP/429 伪成功） | `scripts/recover_page.py`, `xhs_read_notes.py`, `references/cn-social-platform-lookup.md` |
| **web-crawler** | [skills/web-automation/web-crawler/](../skills/web-automation/web-crawler/) | 四引擎抓取决策树（Jina / Playwright / Dokobot / Firecrawl & Crawl4AI）与大批量社区 UGC / 多维度样本采集 | `scripts/community_ugc_scrape.py`, `multi_dim_scrape.py`, `references/bulk-dataset-export.md` |
| **url-to-markdown** | [skills/research/url-to-markdown/](../skills/research/url-to-markdown/) | URL、公众号、X、GitHub、PubMed/Europe PMC PDF 及本地 PDF/EPUB/DOCX 一键转干净 Markdown | `references/doc2md-cli.md` |
| **dokobot** | [skills/dokobot/](../skills/dokobot/) | 复用本机真实 Chrome（带登录态与 Cookie）读取 SPA、动态页面及国内登录墙站点 | `references/test-results.md` |
| **browser-automation-guardrails** *(协同护栏)* | [skills/web-automation/browser-automation-guardrails/](../skills/web-automation/browser-automation-guardrails/) | 抓取已登录的商户/业务后台时，用五层物理防护（只读子账号 + 接口直取 + DOM 隐藏 + 点击拦截 + 网络黑名单）防止误触写操作 | `kit/guard.user.js`, `kit/playwright-adapter.example.js`, `kit/ego-adapter.example.js` |

### Layer 2：专项内容提取与文档沉淀（Extraction & Curation）

| Skill | 路径 | 解决什么问题 | 关键脚本 / 参考 |
|---|---|---|---|
| **x2doc** | [skills/research/x2doc/](../skills/research/x2doc/) | X/Twitter 帖子、X Article、Quote 链、长视频与中文博主 Space 逐字稿整理；支持轻量调研打假（论文对账、工具能力三处核验、薄壳仓审计） | `scripts/ocr.swift`, `references/paper-claim-teardown.md`, `tool-claim-audit.md`, `cn-creator-method-sourcing.md` |
| **link2doc** | [skills/research/link2doc/](../skills/research/link2doc/) | 多链接合集/聚合帖批量提取、深度调研与结构化策展，沉淀为可复现 Markdown 文档并提交 GitHub | `references/extraction-scenarios.md`, `jina-reader-research.md`, `x-twitter-post-extraction.md` |
| **book-and-pdf-sourcing** | [skills/research/book-and-pdf-sourcing/](../skills/research/book-and-pdf-sourcing/) | 找书/教科书/扫描 PDF：确认版次与是否真实出版、Archive/GitHub/Libgen/Anna's 找源、PDF/EPUB 完整性校验、OCR 与双语翻译 | `scripts/ocr_pages.swift`, `pdf_ocr_pages.swift`, `translate_epub.py` |

### Layer 3：事实核查与引用溯源（Grounding & Verification）

| Skill | 路径 | 解决什么问题 | 关键脚本 / 参考 |
|---|---|---|---|
| **content-grounding** | [skills/research/content-grounding/](../skills/research/content-grounding/) | 内容依据硬闸门：原文落盘 → 机器硬校验 → 异构模型独立复核 → 独立 Subagent 逐句对账；覆盖榜单、评测表、厂商发布公告、推广帖与病毒信息图打假 | `scripts/grounding.py`, `scripts/facts_check.py`, `references/benchmark-claim-audit.md`, `release-announcement-audit.md`, `viral-chart-audit.md` |
| **grounded-citations** | [skills/research/grounded-citations/](../skills/research/grounded-citations/) | Perplexity 风格机械化来源台账：`url → [n]` 映射、逐字引语绑定 `--from page.txt`、`verify --evidence` 防编造 URL 与读错表格行列 | `scripts/sources.py`, `references/evidence-capture.md`, `citation-formats.md` |

### Layer 4：深度调研、竞品拆解与持续监控（Research, Teardown & Monitoring）

| Skill | 路径 | 解决什么问题 | 关键脚本 / 参考 |
|---|---|---|---|
| **market-intelligence** | [skills/research/market-intelligence/](../skills/research/market-intelligence/) | 14 维大样本（单次强制落盘 ≥300–1,000 条一手样本）商业/招股书/财报/1688 代工/闲鱼/黑猫投诉/VOC/第三方集成面/开源项目尽调与模型发布审计；交付浅色一页到底 HTML | `scripts/verify_stack.py`, `market_intel_tool.py`, `attach_cjk_quote.py`, `verify_report_anchors.py`, `templates/report-html.html` |
| **mobile-app-teardown** | [skills/research/mobile-app-teardown/](../skills/research/mobile-app-teardown/) | 安卓模拟器（BlueStacks Air / MuMu / AVD）或真机 ADB + `agent-device` 实测 App 6 阶段漏斗、暗黑模式 dp 像素测量、加壳 APK 脱壳与 Retrofit API 实测 | `scripts/adb_teardown_probe.py`, `dexdump_client.py`, `fix_dex_headers.py`, `rea_dexdump.js`, `templates/report_html_builder.py` |
| **horizontal-vertical-analysis** | [skills/research/horizontal-vertical-analysis/](../skills/research/horizontal-vertical-analysis/) | 横纵分析法：纵向历时因果线 × 横向共时竞争截面 → 交叉判断；附中国工商注册与一手数据源清单 | `references/corporate-registry-china.md`, `first-party-data-sources.md` |
| **ai-research-comparison** | [skills/research/ai-research-comparison/](../skills/research/ai-research-comparison/) | AI 模型/工具 7 模式硬核横评：模型深潜、高密对比表、多线路自测速（按可见正文里程碑而非虚高 TPS）、第三方 API 选型、订阅额度核算、买 vs 自建实测、Demo 宣称核验 | `scripts/number_audit.py`, `provider_speed_test.py`, `headless-screenshot.sh`, `references/model-release-factcheck.md` |
| **reference-video-teardown** | [skills/media/reference-video-teardown/](../skills/media/reference-video-teardown/) | 抖音 / 小红书 / B 站 / YouTube / TikTok / X 爆款视频与账号全量扫盘、变现链路打假、视觉封面差距表与讲法拆解 | 12 份平台与方法拆解手册（`douyin-account-teardown.md`, `youtube-channel-teardown.md`, `monetization-claim-audit.md` 等） |
| **info-gap-agent-workflow** | [skills/research/info-gap-agent-workflow/](../skills/research/info-gap-agent-workflow/) | 把一次高质量信息筛选逻辑沉淀为 Cron 定时监控 Agent，容错抓取 RSS / X / Reddit / GitHub → 筛选 Top N → 归档知识库 | 11 份容错抓取与 RSS/X 故障复盘参考（`rss-ingest-resilience.md`, `x-pulse-fallback-browser-2026-07-12.md` 等） |

---

## 三、任务路由决策表（遇到什么任务，调哪条链路）

| 用户需求场景 | 首选入口 Skill | 配套抓取与核查链路 | 交付形态 |
|---|---|---|---|
| **陌生行业 / 商业赛道 / 招股书 / 竞品全景调研** | `market-intelligence` (+ `horizontal-vertical-analysis`) | `verify_stack.py` → `web-search` + `web-crawler` + `blocked-page-recovery` → `grounded-citations` + `independent-audit-pass` | 原始证据库 + 浅色单页 HTML / A4 PDF 报告 |
| **移动端 App 竞品功能、付费墙、AI 交互与接口拆解** | `mobile-app-teardown` | ADB + `agent-device`（必要时 Frida/dexdump 脱壳 + Retrofit 接口实测）→ 独立 Subagent 逐条复算 | `evidence/*.png+.json` + 单页 HTML 拆解报告 |
| **AI 模型发布核验 / 价格订阅横评 / 线路测速 / 买 vs 自建** | `ai-research-comparison` | 实时探针（`/v1/models`, `models.dev`, OpenRouter, HF）+ `provider_speed_test.py` + `number_audit.py` + `content-grounding` | 同口径对比表 / 实测路线矩阵 |
| **单条 X 帖 / 长文 / 论文转述 / 工具宣传帖打假或整理** | `x2doc` | `fxtwitter` / Jina / Dokobot → `paper-claim-teardown` / `tool-claim-audit` / `content-grounding` | 轻量拆解结论 或 `docs/*.md` 归档 |
| **多链接合集 / 教程清单 / 网页转 Markdown** | `link2doc` / `url-to-markdown` | Jina Reader → `web_extract` → `dokobot` → `doc2md`（PDF/EPUB/DOCX） | 结构化 Markdown 文档 |
| **网页 403/429 / 付费墙 / WAF / 国内平台抓取受阻** | `blocked-page-recovery` | `recover_page.py`（5 级梯次）→ 兄弟站切换 → 登录态真实浏览器（Dokobot / ego-browser） | 带 `provenance`（live/snapshot+日期）的干净文本 |
| **抖音 / 小红书 / B 站 / YouTube / TikTok 账号与爆款拆解** | `reference-video-teardown` | 平台公开接口 / `yt-dlp` / 登录态抓包 + 抽帧联系表 + `monetization-claim-audit` | 台账式拆解报告 / 差距表与落地方案 |
| **找电子书 / 专业教材 / 扫描版 PDF 或生成中文版** | `book-and-pdf-sourcing` | 出版状态核验 → Archive/GitHub/Libgen/Anna's → `file`/页数/EPUB 结构校验 → OCR/翻译 | 本地可验证的 PDF / EPUB 文件 |
| **每日自动监控 AI / 竞品 / 垂直赛道动态** | `info-gap-agent-workflow` | Cron + 容错 RSS/X/Reddit/GitHub 抓取 + `content-grounding` | 每日结构化简报 + Obsidian/GitHub 归档 |

---

## 四、五条核心端到端标准工作流（SOP）

### 流程 1：网页与信息抓取的 5 级升级梯（Cheapest First）

遇到任何需要读取外部信息的任务，严格按成本与稳定性从低到高升级，**不在被 WAF 封死的页面上死循环重试**：

```text
Level 0 · 直接读数据源（零渲染、零配额消耗）
  └─ GitHub raw / 官方 JSON API / RSS / Sitemap / OpenCLI 181 站点 / fxtwitter API

Level 1 · 多引擎搜索与轻量提取
  └─ web-search/scripts/search.py（auto / exa / tavily / serper / brave / ddgs）
  └─ url-to-markdown（Jina Reader r.jina.ai / web_extract / Firecrawl scrape）

Level 2 · 封锁页三方存档与镜像恢复（blocked-page-recovery/scripts/recover_page.py）
  └─ 1) Wayback Machine available/CDX API（保留 snapshot 日期）
  └─ 2) archive.today 域名轮询（archive.ph → .md → .li → .is，校验正文防 429 假 200）
  └─ 3) Jina Reader（带 JINA_API_KEY）
  └─ 4) API-first 切换（/api/、/graphql、.json、兄弟门户站点如链家→房天下）

Level 3 · 真实浏览器与登录态抓取
  └─ dokobot read --local --device <ID> <url>（复用本机真实 Chrome Cookie）
  └─ ego-browser / Playwright（过 DDoS-Guard 等强挑战；涉业务后台必挂 browser-automation-guardrails）

Level 4 · 移动端 App 实机/模拟器抓取（mobile-app-teardown）
  └─ BlueStacks Air / MuMuPlayer Pro / AVD / USB 真机 + ADB + agent-device
  └─ 必要时脱壳提取 Retrofit 接口并实测 guest-token 实时返回
```

**反踩坑硬规则**：
- **拒绝假 200**：Google Cache 已停服、AMP 缓存常返 300B 跳转页、archive.today 429 仍带数 KB HTML；所有抓回正文必须校验有效内容与筛选条件。
- **保留来源时效（Provenance）**：来自 Wayback / archive.today 的内容必须注明 `snapshot` 日期，绝不冒充当前实时价格或状态。
- **Surge/Clash fake-IP 排障**：遇到 `web_extract` 全部报内网拦截时，检查 DNS 是否落入 `198.18.0.0/15`，在 Hermes 中配置 `security.fake_ip_ranges`（见 `skills/research/web-search/SKILL.md`）。

---

### 流程 2：大样本深度商业与竞品调研流水线（`market-intelligence`）

杜绝「搜 5 篇文章拍脑袋写报告」的表演式调研，强制 **先验收环境 → 再落盘大样本 → 再写报告 → 再过独立审计**：

1. **Step 0 · 环境六层实测验收**
   ```bash
   python3 skills/research/market-intelligence/scripts/verify_stack.py --topic "<核心品类词>"
   ```
   只认返回的实际 `engine` 字段，`FAILOVER` 不算 `OK`；任何必需链路不通先修环境再开工。
2. **Step 1 · 多维一手样本强制落盘（目标 ≥300–1,000 条）**
   - 招股书/年报/电话会（S-1/10-K/港交所披露易/A 股问询函）
   - 6 大平台搜索下拉词与购买意图雷达（`market_intel_tool.py intent`）
   - 电商买家 1–3 星差评、黑猫投诉、闲鱼弃坑、社区 UGC（`web-crawler/scripts/community_ugc_scrape.py`、`multi_dim_scrape.py`）
   - 1688 代工底价、招聘 JD 暴露的产品与私域成本、官方统计口径、PubMed/学术证据
   - 移动端 App 体验空白 → 转 `mobile-app-teardown` 补齐真实截图与节点树
3. **Step 2 · 结构化分析与定量三角校验**
   - 用 `horizontal-vertical-analysis` 建立纵向历时线 × 横向共时矩阵
   - TAM/SAM/SOM 双向校验（Top-Down × Bottom-Up）
   - 魔鬼代言人反方压测：对每个乐观结论寻找证伪证据
4. **Step 3 · 机械化引用与独立审计**
   - 用 `grounded-citations/scripts/sources.py` 建立来源台账并逐字绑定引语（CJK 长文可用 `attach_cjk_quote.py`）
   - 按 `market-intelligence/references/independent-audit-pass.md` 派异构审计模型做只读挑刺
   - 用 `verify_report_anchors.py` 校验 HTML 内所有引用锚点、图片与占位符零残留
5. **Step 4 · 交付**
   - 遵循「先产品后商业」结构，交付浅色简洁一页到底 HTML（`templates/report-html.html`）及可打印 A4 PDF。

---

### 流程 3：事实核查与防幻觉四重闸门（`content-grounding` + `grounded-citations`）

所有对外报告、评测、新闻简报、公众号长文与研究文档均须通过四道闸门：

```text
Gate 1 · 原文落盘（禁止只读搜索摘要或 AI 转述）
  └─ grounding.py fetch <URL...>  或  sources.py add + quote --from <local.txt>

Gate 2 · 确定性机器硬校验（0 幻觉、0 拼造链接）
  └─ grounding.py check --kind <briefing|tietu|longform> <FILE>   → 须输出 GROUNDED OK
  └─ 长稿/剧本无专用 kind 时：facts_check.py --facts facts.json --script <FILE> → FACTS OK
  └─ 报告/研究文档：sources.py verify <draft.md> --strict --evidence

Gate 3 · 异构模型独立核对（避免写稿模型自审盲区）
  └─ grounding.py review --kind <kind> <FILE>                     → 须输出 REVIEW PASSED

Gate 4 · 独立 Subagent 逐句对账与代码复算（长文与高风险报告必跑）
  └─ 传入成稿 + 本地 evidence 原文，按【完全准确 / 措辞轻微偏差 / 事实错误】逐句输出原句对照与改法
  └─ 涉及 N/M 计数、倍率、名次、表格行列、字节/单位换算时，一律用 Python 脚本重算（如 number_audit.py）
```

**高频失真专项核查清单**（已固化在对应 references 中）：
- **评测表 / Leaderboard**：先抄测试条件行（并发数、尝试次数、墙钟、harness、样本量），再引具体列（`content-grounding/references/benchmark-claim-audit.md`）。
- **厂商发布与「全面开源」声明**：按模型逐个落入五桶交付物矩阵（完整权重 / 量化版 / 仅编码器 / 仅代码 / 闭源 API），读模型卡推理配方而非营销稿（`ai-research-comparison/references/model-release-factcheck.md`、`market-intelligence/references/model-release-audit.md`）。
- **第三方集成面（有没有 API/MCP）**：按三态（接口存在 / 文档在线 / 官方支持）实测（`market-intelligence/references/integration-surface-audit.md`）。
- **开源项目尽调**：GitHub API 元数据 + raw docs + 本地黑盒实测 `x/N` 召回表 + 真实 LICENSE 文件（`market-intelligence/references/oss-project-dossier.md`）。

---

### 流程 4：单点高信号信息快评与策展（`x2doc` / `link2doc` / `reference-video-teardown`）

- **单条 X 帖 / 推文转述论文 / 新工具发布**：走 `x2doc`
  - 只需判断真伪 → **轻量调研模式**：`他在说什么 → 逐环节拆链 → 硬数字 → 水分与边界 → 值不值得抄`
  - 需要知识沉淀 → 抓取全文、Quote 链、图片 OCR（`scripts/ocr.swift`）与核心外链，落盘 Markdown 并提交仓库。
- **多链接聚合帖 / 教程资源清单**：走 `link2doc`，先提取全部子链接，再并行调研并保留「发布者一线洞察」，统一格式化入库。
- **短视频 / 长视频爆款与账号调研**：走 `reference-video-teardown`，按平台选用对应接口/抓包方案，抽帧拼联系表 + 变现链路打假 + 产出「他对 / 我们对」差距表。

---

### 流程 5：持续信息差定时监控（`info-gap-agent-workflow`）

1. **先定义判断力再自动化**：写清「从哪 20–30 个高信号源里、按什么标准筛 Top N」，避免泛泛抓取新闻。
2. **小范围跑稳 3 天再扩源**：4–5 个核心源 → 20–30 个 → 跨平台（RSS / X / Reddit / GitHub）。
3. **内置采集容错**：应对 RSS XML 脏字符（正则兜底）、Feed 体积缩水但有新内容、X 抓取失败降级真实浏览器等真实故障（详见 `skills/research/info-gap-agent-workflow/references/`）。
4. **结构化沉淀与闭环**：每次运行固定落盘「日期 / 来源 / 原文链接 / 摘要 / 分类 / 入选理由 / 后续动作」，高价值线索自动转入 `link2doc` 或 `market-intelligence` 深挖。

---

## 五、配套自动化脚本速查表

| 脚本路径 | 所属 Skill | 功能 |
|---|---|---|
| `skills/research/web-search/scripts/search.py` | web-search | 7 引擎统一搜索与提取路由器（支持 `--engine auto` 与 `--json`） |
| `skills/research/web-search/scripts/cf_crawl.py` | web-search | Cloudflare Browser Rendering 站点爬取封装 |
| `skills/research/web-search/scripts/domain_intel.py` | web-search | 域名/站点基础情报探查（DNS/WHOIS/技术栈等） |
| `skills/research/web-search/scripts/duckduckgo.sh` | web-search | 免 API Key 的 DuckDuckGo 快速检索封装 |
| `skills/web/blocked-page-recovery/scripts/recover_page.py` | blocked-page-recovery | 5 级梯次封锁页自动恢复 + 假 200 拦截 + provenance 标注 |
| `skills/web/blocked-page-recovery/scripts/xhs_read_notes.py` | blocked-page-recovery | 小红书笔记正文读取辅助脚本 |
| `skills/web-automation/web-crawler/scripts/community_ugc_scrape.py` | web-crawler | 社区 UGC 样本批量采集 |
| `skills/web-automation/web-crawler/scripts/multi_dim_scrape.py` | web-crawler | 多维度网页数据批量抓取 |
| `skills/research/x2doc/scripts/ocr.swift` | x2doc | macOS Vision 原生图片文字 OCR（图表/截图转文本） |
| `skills/research/book-and-pdf-sourcing/scripts/ocr_pages.swift` | book-and-pdf-sourcing | 扫描图片页批量 Vision OCR |
| `skills/research/book-and-pdf-sourcing/scripts/pdf_ocr_pages.swift` | book-and-pdf-sourcing | 扫描版 PDF 逐页 OCR 提取 |
| `skills/research/book-and-pdf-sourcing/scripts/translate_epub.py` | book-and-pdf-sourcing | 英文原版 EPUB 自动化翻译与重建 |
| `skills/research/content-grounding/scripts/grounding.py` | content-grounding | 原文证据抓取 `fetch`、确定性硬检查 `check`、异构模型复核 `review` 与抽查 `audit` |
| `skills/research/content-grounding/scripts/facts_check.py` | content-grounding | 通用长稿/剧本 `facts.json` 逐字子串比对与 `[Fxx]` 覆盖率校验 |
| `skills/research/grounded-citations/scripts/sources.py` | grounded-citations | 机械化来源台账 `add/ingest/quote/render/verify`（防编造链接） |
| `skills/research/market-intelligence/scripts/verify_stack.py` | market-intelligence | 调研环境六层全链路实测验收脚本（区分 `OK` 与 `FAILOVER`） |
| `skills/research/market-intelligence/scripts/market_intel_tool.py` | market-intelligence | 招股书检索式生成、6 大平台下拉词购买意图雷达、市场规模三角校验 |
| `skills/research/market-intelligence/scripts/attach_cjk_quote.py` | market-intelligence | 中文原文引语自动切片与台账绑定 |
| `skills/research/market-intelligence/scripts/verify_report_anchors.py` | market-intelligence | HTML 调研报告引用锚点、图片与模板占位符自动化检查 |
| `skills/research/mobile-app-teardown/scripts/adb_teardown_probe.py` | mobile-app-teardown | ADB 设备规格核验、截图/节点树采集与 dp 触控面积换算 |
| `skills/research/mobile-app-teardown/scripts/dexdump_client.py` + `rea_dexdump.js` + `fix_dex_headers.py` | mobile-app-teardown | 加壳 APK 内存 DEX 脱壳与头部校验和修复工具链 |
| `skills/research/mobile-app-teardown/templates/report_html_builder.py` | mobile-app-teardown | Markdown → 浅色单页 HTML 拆解报告生成器（含坏链/占位符自检） |
| `skills/research/ai-research-comparison/scripts/number_audit.py` | ai-research-comparison | 对比报告数字、百分比与口径自动化复算核查 |
| `skills/research/ai-research-comparison/scripts/provider_speed_test.py` | ai-research-comparison | 同模型多线路流式速度实测（按可见正文字符里程碑计） |
| `skills/research/ai-research-comparison/scripts/headless-screenshot.sh` | ai-research-comparison | 高密度对比表无头 Chrome 渲染截图 |

---

*来自翡冷翠* | 整理于 2026-11-24
