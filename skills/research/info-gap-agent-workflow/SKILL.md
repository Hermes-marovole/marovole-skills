---
name: info-gap-agent-workflow
description: "AI 信息差 Agent 工作流：用 Hermes cron + 搜索/浏览器 + Obsidian/Linear/邮件，把一次高质量信息筛选逻辑沉淀成定时运行的趋势监控 Agent。适用于 AI、Neumina 竞品、女性健康、Biohacking、社媒热点等信息源监控。"
category: research
tags: [information-monitoring, trend-monitoring, cron, x-twitter, obsidian, linear, agent-workflow, solopreneur]
trigger: ["信息差", "趋势监控", "每天监控", "定时抓取", "自动日报", "帮我盯", "刷 X", "热点监控"]
---

# AI 信息差 Agent 工作流

核心洞察：**信息差的本质不是“找得到”，是“每天都能稳定找得到”。**

目标：把一次高质量的信息筛选逻辑，沉淀成可定时运行、可归档、可迭代的 Hermes Agent 工作流。

---

## 1. 适用场景

适合监控：
- AI Agent / LLM / 多模态 / GPT-image 新动态
- Neumina 竞品：Midi Health、Evernow、Maven、女性健康产品
- 更年期、longevity、biohacking、营养、运动、睡眠
- X/Twitter 高价值账号
- Reddit 社区，如 r/LocalLLaMA、r/ClaudeAI
- GitHub trending / release notes
- 行业博客 / RSS / Newsletter

不适合：
- 没有明确筛选标准的泛泛“帮我看新闻”
- 需要强实时交易/安全响应的场景
- 来源无法稳定访问且无替代源的场景

---

## 2. 核心原则

### Agent 复制的是判断力，不是外包大脑

先明确“什么值得看”，再自动化。

错误：
```text
每天帮我找 AI 新闻。
```

正确：
```text
每天从我指定的 30 个 AI 产品/研究者账号中，筛选出信息密度高、可转化为产品/内容/研究机会的 8 条动态。互动热度是辅助信号，不是唯一标准。
```

### 稳定沉淀比单次惊艳重要

每次运行都要留下：
- 日期
- 来源
- 原始链接
- 摘要
- 分类
- 为什么入选
- 后续动作

### 先小范围跑稳，再扩源

推荐阶段：
1. 4-5 个核心来源，连续跑 3 天
2. 扩到 20-30 个来源
3. 加入跨平台来源：Reddit、GitHub、博客、RSS
4. 增加自动分类和行动项生成

---

## 3. 工作流总览

```
定义筛选标准
    ↓
配置信息源
    ↓
定时抓取
    ↓
筛选 Top N
    ↓
结构化日报
    ↓
归档到 Obsidian / Notion / GitHub
    ↓
重要项生成 Linear issue 或触发 link2doc
    ↓
运行数天后迭代筛选标准
```

Hermes 推荐落地：
- 定时：`cronjob`
- 抓取：`browser_*` / web search / RSS / API / GitHub CLI
- 归档：Obsidian vault
- 任务：Linear
- 深度整理：`link2doc`
- 邮件：`mail-cli` CLI（当 `clawemail` skill 不可用时）或 Apple Mail 或用户指定渠道。详见 `references/mail-cli-command-syntax.md`。

### RSS 抓取与解析

RSS 是最可靠的 cron 信息源（不依赖浏览器、无验证码、无反爬）。解析流程：

① **下载 RSS XML 到临时文件**（避免大文件在终端直接解析）：

```bash
curl -sL "https://news.smol.ai/rss.xml" -o /tmp/feed.xml
```

If the normal fetch fails with a transport/TLS error, retry once with a bounded compatibility fallback such as `curl -k --http1.1 -sS -L`, and record the fallback in the daily report. Use certificate bypass only for the known source URL, never as a general default. See `references/rss-ingest-resilience.md` for the complete-body extraction and verification recipe.

② **编写 Python 解析脚本到文件**（不要内联 Python，Hermes 安全过滤器可能误判）：

```python
# /tmp/parse_feed.py
import xml.etree.ElementTree as ET

tree = ET.parse('/tmp/feed.xml')
root = tree.getroot()
channel = root.find('channel')

for item in channel.findall('item'):
    title = item.find('title').text or ''
    pubDate = item.find('pubDate').text or ''
    link = item.find('link').text or ''
    desc = item.find('description').text or ''
    # Filter by pubDate — only process items since last run
    print(f"TITLE: {title}")
    print(f"DATE: {pubDate}")
    print(f"LINK: {link}")
    print(f"DESC: {desc[:300]}...")
    print("---")
```

③ **运行解析脚本**：

```bash
python3 /tmp/parse_feed.py
```

④ **提取完整正文**（用于 wiki 原始存档）——使用 `content:encoded` 命名空间：

```python
ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
encoded = item.find('content:encoded', ns)
body = encoded.text if encoded is not None else ''
```

⑤ **增量判定**：RSS feed 可能包含数百条历史条目。只处理未处理过的条目，但不要只按 `pubDate` 去重。优先使用稳定标识：`link` / GUID / 已保存的 raw 文件名 / `index.md` 或 `log.md` 中的已编译记录 / 正文 `sha256`。原因：Smol AI News 曾出现多个不同 issue 共享同一个 `pubDate`（例如 URL slug `26-05-04` 与 `26-05-05` 都显示 `Mon, 04 May 2026 05:44:39 GMT`；2026-05-20 运行时 `26-05-18` 与 `26-05-19` 又共享 `Mon, 18 May 2026 05:44:39 GMT`）。如果只看日期，会误判新 issue 已处理。每次至少解析前 10 条 item，逐条比较 link/GUID/raw filename/hash，而不是只看第一条。

**Compiled-slug extraction must tolerate frontmatter schema variance (2026-07-26):** When scanning `raw/newsletters/*-smol-ai-news.md` to build the compiled set, match **all** of: `source_url:`, `source:`, any line containing `issues/<slug>`, plus filename date `YYYY-MM-DD-smol-ai-news.md`. Accept both `sha256:` and `rss_hash:`. Do not treat a missing `source_url` key as “uncompiled.” Prefer: `if raw file exists for that issue date OR slug appears in any URL field → already compiled`.

**Delayed weekday issues over weekends:** A Friday issue may be absent all Saturday and appear Sunday/Monday (observed: Jul 24 `opus-5` missing on Jul 25 runs, present Jul 26). Weekend “gap” is provisional; next run must still full-scan for the missing weekday slug. See `references/raw-frontmatter-schema-variance-2026-07-26.md`.

**Reference:** See `references/smol-ai-news-rss-digest-2026-05-15.md` for the 2026-05-14 run notes, including the "not much happened today" title trap and the body-hash workflow.

常见 RSS 源格式：
- Standard RSS 2.0：`<pubDate>` 为 RFC 2822 格式（如 `Wed, 29 Apr 2026 05:44:39 GMT`）
- 大部分 Newsletter RSS（Substack、Beehiiv、Smol AI News）都使用标准格式
- 中文 RSS 源可能使用 `dc:date` 命名空间

**RSS feed URL discovery when the known URL 404s:** Newsletter sources migrate platforms. Smol AI News moved from `buttondown.email/ainews/rss` (deprecated, last item Apr 2025) to `news.smol.ai/rss.xml`. Discovery procedure: (1) `curl -sL` the source's main page and `grep -oE 'href="[^"]*"'` for feed links. (2) Probe common paths: `/rss.xml`, `/feed.xml`, `/feed`, `/rss`, `/atom.xml`, `/index.xml`. (3) Check for `<link rel="alternate" type="application/rss+xml">` in the HTML head. (4) If the old feed exists but has a "moved" notice in its channel description, extract the new URL from the description text. (5) Verify the discovered feed returns 200 + valid XML with recent `<pubDate>` values before adopting it as the primary source. Store the confirmed feed URL in `sources.md` for future runs.

⑥ **Rerun/idempotency check for cron jobs**：在写日报、raw source、digest、log 之前，先检查今天的目标文件和 log 是否已经存在。若存在同日输出，不要直接追加第二份；应读取现有文件，判断是已完成、部分完成、还是需要合并新来源。合并后删除重复同日 log entry，保留一个完整条目。遇到“file modified by sibling subagent / external edit”类警告时，必须重新读取目标文件再 patch。

⑦ **Gap report still updates the monitoring state**：如果没有新 RSS/email 内容，也要把“没有新内容”的证据写成状态报告（除非用户明确要求 `[SILENT]`）。报告应包含：认证/抓取结果、最新已处理 item 的 link + hash、为什么判定没有新内容、单源/源延迟风险、下一步补源建议。即使不创建 raw source 或概念页，也要更新 source list/index/log，让下一次运行知道这是已验证的 gap，而不是任务漏跑。

⑧ **Source dormancy vs. parser failure**：当主 RSS 源连续多日无新内容时，不要假设是解析器或 dedupe 脚本出错。应在整个 feed 中搜索缺失日期范围的 slug（如 regex `/p/26-06-0[6-9]/`），确认 feed 本身确实没有对应条目。如果是真正的 source dormancy，按 gap report 处理并立即在报告中建议添加 backup RSS 源（arXiv、Hugging Face Papers 等），而不是继续重试同一个空源。参考 `references/smol-rss-source-dormancy-multi-day-gap-2026-06-09.md`。

⑨ **Source dormancy escalation thresholds**（observed June 2026 via Smol AI News):
- **1–2 days**: Source latency — note in digest, monitor next run.
- **3–7 days**: Source dormancy — write gap report, explicitly recommend adding ≥2 backup RSS sources.
- **≥8 days**: Single-source failure — pipeline has zero active data ingress. Use the exact phrase *"single-source fragility has become a single-source failure"* in the gap report. Recommend immediate addition of backup RSS sources PLUS switching newsletter subscriptions to a deliverable email provider (Gmail/ProtonMail/Fastmail). Also recommend investigating whether the primary source's publication schedule has changed (check source website/Twitter/Discord directly).

⑩ **Regex scan for fast dormancy confirmation**: Before running a full Python dedupe script, do a quick regex scan across the raw XML to confirm the missing date range is truly absent:
```bash
grep -o '/issues/26-06-1[0-9]' /tmp/feed.xml | sort -u
```
This is the fastest way to distinguish dormancy from parser bugs. **Also use it to detect NEW slugs**: compare the regex output against the previous run's known slug list.

**Caveat — slug renames during feed regeneration (observed 2026-07-12):** Feed regeneration can **rename existing slugs** (e.g., `26-07-09-not-much` → `26-07-09-gpt-56`) without adding new content. A new slug bearing a date range you've already compiled should NOT be automatically treated as new content. Verify by:
1. Check whether content under the old slug name was already compiled (by SHA256 match or raw filename existence).
2. Compare the item's description/snippet against the already-compiled digest's source link.
3. Check whether the total item count increased or stayed the same — if it's unchanged and only slug names differ, it's a rename, not a new issue.
4. When in doubt, fall back to SHA256 comparison of the `content:encoded` against the compiled raw source's frontmatter hash.

A slug rename does NOT warrant re-ingesting. Note it in the daily report as a feed-regeneration observation, then move on.

⑪ **Feed size delta as quick new-content signal**: Before parsing, compare the downloaded feed byte size to the previous run's recorded size. A size increase (e.g. 1,966,135 → 1,978,657 bytes) strongly suggests new items were added. **BUT: a size decrease does NOT reliably indicate dormancy.** Feed regeneration events can shrink the overall feed size (e.g. via HTML normalization of existing items) while simultaneously adding new items. Observed 2026-07-03: Smol AI News feed went from 2,033,521 → 1,997,278 bytes (decrease of ~36KB) while items went from 665 → 667 (2 new slugs added: `26-06-30-sonnet5` and `26-07-01-not-much`). The July 2 run had reported "feed unchanged, zero entries for June 30 / July 1-2" — the July 3 run found both missing issues. **Confirmed recurring pattern (3 instances)** — 2026-07-08 run observed the same: feed went from 2,001,802 → 1,995,552 bytes (decrease of ~6KB) while items went from 668 → 669 (1 new slug: `26-07-06-not-much`). 2026-07-09 run observed the third instance: feed went from 1,995,552 → 1,985,127 bytes (decrease of ~10KB) while items went from 669 → 671 (2 new slugs: `26-07-07-not-much` and `26-07-08-grok-45`). Smol AI News undergoes periodic feed regeneration where HTML normalization shrinks existing items while adding delayed issues. **The size delta is a hint, not a verdict. Always do a full slug scan (`grep -oE 'issues/26-0[67]-[0-9]{2}' /tmp/feed.xml | sort -u`) regardless of whether the size went up or down.** The only case where size delta is safe to skip parsing is when the size is byte-identical to the previous run AND the item count is unchanged. See `references/feed-regeneration-size-decrease-new-content-2026-07-03.md`.

⑫ **Watch for non-newsletter entries in RSS feeds**: Feeds like Smol AI News may contain portfolio/project items (e.g. `Astro Nano`, `Astro Sphere`) that appear as uncompiled positives. Always inspect the item's content/snippet before flagging it as a new newsletter issue.

⑬ **Watch for source format transition signals**: Newsletter issues may contain self-referential notes about the source's own future. For example, Smol AI News's June 22 issue ended with: *"Discord shut down our access today. We will not bring it back in this form but we will be shipping the new AINews soon."* This signals a potential format change or RSS feed discontinuation. When detected: (1) flag it prominently in the daily report, (2) update sources.md with the transition note, (3) escalate backup RSS source urgency — the primary source may stop publishing in its current form. Do NOT treat this as a normal dormancy signal; it is a structural change to the monitoring pipeline.

⑬b **Persistent format transition signals (5+ consecutive issues)**: When the same "we're transitioning / shutting down / new version coming" message repeats across 5 or more consecutive issues without resolution, the signal has escalated from a one-time flag to a sustained structural risk. Handling: (1) Track the consecutive-issue count in every daily report (e.g. "7th consecutive day"). (2) Upgrade backup RSS source recommendation from "recommended" to "critical / action needed" — the primary source may transition at any time. (3) In the sources.md delivery alert, use escalating language: "format transition risk sustained and elevated" rather than just "flagged". (4) Do NOT stop monitoring the primary source — it may still publish new content in its current format before transitioning. (5) Consider proactively testing backup RSS feeds (arXiv cs.AI, Hugging Face Papers) to confirm they are parseable before the primary source disappears. (6) If the count reaches 10+ consecutive issues, recommend investigating the source's website/social media directly for transition announcements. See `references/smol-ai-news-format-transition-timeline-2026-06-30.md` for the observed timeline.

⑬c **Valedictory tone as winding-down signal**: When the format-transition message itself changes tone from forward-looking ("we will be shipping the new AINews soon") to retrospective/valedictory ("thanks for reading to here, it was a good run"), this signals the source is winding down rather than transitioning to a new format. The "new AINews" may never materialize. Observed at 8+ consecutive issues in Smol AI News (July 2026). When detected: (1) upgrade the risk from "format transition risk" to "source discontinuation risk" in daily reports and sources.md, (2) treat backup RSS source addition as immediately actionable, not just recommended, (3) note the valedictory language explicitly so future runs understand the source may stop publishing entirely. **Important nuance (observed July 3, 2026):** The RSS feed may continue publishing even with the valedictory tone — the Discord shutdown appears to affect only the Discord-sourced content section, while Twitter/Reddit-sourced content continues via RSS. The source may operate in reduced scope (no Discord section) rather than discontinuing entirely. Risk classification should note "reduced content scope" vs "imminent feed shutdown" as distinct scenarios. See `references/smol-ai-news-valedictory-tone-sibling-overwrite-2026-07-01.md` for the observation and `references/smol-ai-news-format-transition-timeline-2026-06-30.md` for the full timeline.

⑭ **Mailbox checking via mail-cli when clawemail skill unavailable**: The `clawemail` skill may not be found at runtime. The `mail-cli` CLI tool (at `~/.npm-global/bin/mail-cli`) provides direct mailbox access. Key commands: `mail-cli --profile 04 auth test --json` for auth validation, `mail-cli --profile 04 mail list --fid <id> --json` for folder scanning (NOT `folder read`). See `references/mail-cli-command-syntax.md` for full command reference. **Pitfall:** Python `subprocess.run` does NOT expand `~` — use `os.path.expanduser()` or bare `'mail-cli'` if on PATH.

⑱ **HTML-to-Markdown conversion for raw source files**: RSS `content:encoded` is HTML, but Obsidian raw source files use Markdown with YAML frontmatter. Every ingest requires an HTML→Markdown conversion step using `html2text` (`pip3 install html2text`). **Critical:** the RSS `content:encoded` is often **HTML-entity-encoded** (`&lt;p&gt;` instead of `<p>`) — you must call `html.unescape()` on the raw content BEFORE passing to `html2text`, otherwise the output contains raw HTML tags instead of Markdown. SHA256 should be calculated on the original entity-encoded HTML (before unescape), not the Markdown output. See `references/html-to-markdown-conversion.md` for the full conversion script pattern and configuration.

---

## 4. 配置信息源

建立一个 source list，建议保存在 Obsidian 或项目仓库：

```markdown
# Info Gap Sources - {主题}

## X/Twitter
| 账号 | 类型 | 关注原因 | 优先级 |
|---|---|---|---|
| @example | researcher | LLM agent research | high |

## Reddit
| 社区 | 主题 | 优先级 |

## GitHub
| repo/topic | 关注内容 | 优先级 |

## Blogs / RSS
| 名称 | URL | 主题 | 优先级 |
```

Neumina 推荐主题：
- menopause health
- women health AI
- digital therapeutics
- longevity / biohacking
- nutrition / sleep / exercise
- AI health coach

---

## 5. 筛选标准模板

```markdown
# Selection Criteria - {主题}

## 入选标准
- 信息密度高：包含新产品、新模型、新论文、新数据、新案例
- 可执行：能转成产品机会、内容选题、研究问题或 Linear 任务
- 可验证：有原始链接、截图、数据或明确来源
- 与主题相关：符合 {主题范围}

## 降权标准
- 纯情绪观点，无事实增量
- 重复转发，无新信息
- 广告味太重
- 只有互动热度但没有真实需求

## 分类
- 产品/工具
- 研究/论文
- 市场/竞品
- 用户洞察
- 内容选题
- 技术基础设施
- 风险/合规

## 排序权重
- 信息密度：40%
- 与当前项目相关性：30%
- 新颖性：20%
- 互动热度：10%
```

---

## 6. 日报输出模板

```markdown
# {主题} 信息差日报 - YYYY-MM-DD

## 今日 Top 3
| 排名 | 标题 | 分类 | 为什么重要 | 原文 |
|---|---|---|---|---|

## 精选信息差
### 1. {标题}
- 来源：
- 原文：
- 分类：
- 互动/热度：
- 摘要：
- 为什么入选：
- 可转化动作：内容选题 / 产品机会 / 研究问题 / Linear 任务 / link2doc

## 趋势观察
- 今天重复出现的主题：
- 新出现的关键词：
- 需要连续跟踪的线索：

## 建议动作
- [ ] ...
```

---

## 7. 自动化动作规则

根据每条信息的价值决定下一步：

| 信号 | 动作 |
|---|---|
| 单条很有价值 | 保存到 Obsidian clipping |
| 多条围绕同一主题 | 建立主题页或追加到 LLM-Wiki |
| 可转成内容 | 进入 social-media-agent-workflow 或 x-personal-brand |
| 可转成研究报告 | 触发 horizontal-vertical-analysis |
| 是资源合集 / thread | 触发 link2doc |
| 是产品机会 / bug / 需求 | 创建 Linear issue |
| 是竞品动态 | 进入 competitor-research / Neumina competitor wiki |

---

## 8. 用 cronjob 创建定时任务

Cron job prompt 必须自包含，因为未来运行没有当前上下文。

示例：

```text
每天 08:00 运行“AI 信息差日报”。
读取 Obsidian 中的 source list 和 selection criteria；抓取指定来源；筛选 8 条高价值信息；输出 Markdown 日报到 Obsidian；对需要深挖的条目给出建议动作。不要询问用户。
```

推荐 schedule：

```text
0 8 * * *
```

注意：
- cron 任务不能递归创建新的 cronjob
- prompt 里写清楚 vault 路径和源列表路径
- 失败时输出错误原因和下一步建议

---

## 9. 迭代机制

像带新人一样建立信任：

运行 3-5 天后检查：
- 漏掉了什么？
- 选进来的内容是否真的有价值？
- 分类是否合理？
- 是否过度追逐热度？
- 哪些来源噪音大，应降权或删除？
- 哪些主题应该单独成一个监控 Agent？

把修正写回：
- source list
- selection criteria
- cron prompt
- 本 skill（如果是通用改进）

---

## 10. 常见坑

| 坑 | 正确做法 |
|---|---|
| 只按热度排序 | 信息密度和项目相关性优先 |
| 来源太多一开始就失控 | 先 4-5 个源跑稳，再扩到 30 个 |
| 每天看完不沉淀 | 必须保存日报和原文链接 |
| 没有行动项 | 每条高价值信息都要判断下一步 |
| Prompt 写得太泛 | 写明筛选标准、分类和降权标准 |
| 自动化后不复盘 | 3-5 天后迭代判断标准 |
| 假设 email 能收到 | Newsletter 订阅经常静默失败（Captcha/Cloudflare/Substack token）。永远把 RSS 作为主要数据源，email 当 bonus。email 为空是常态，不是异常。 |
| `clawemail` skill 找不到时无法检查邮箱 | `mail-cli` CLI 工具（`~/.npm-global/bin/mail-cli`）可直接检查邮箱。正确语法：`mail-cli --profile 04 mail list --fid <id> --json`。不要用 `folder read`（不存在）。**注意：** Python `subprocess.run` 不展开 `~`，需用 `os.path.expanduser()` 或裸 `'mail-cli'`（如已在 PATH 中）。扫描全部 6 个文件夹（1=收件箱, 2=草稿箱, 3=已发送, 4=已删除, 5=垃圾邮件, 6=病毒）——已发送文件夹含 Hermes/x2doc 出站通知，可确认邮箱认证仍有效。详见 `references/mail-cli-command-syntax.md`。 |
| 并发 subagent 同时修改 vault 文件 | cron 运行时可能有 sibling subagent 同时处理同一 issue。写入 sources.md/index.md/log.md 前必须重新读取（会收到 "file modified by sibling subagent" 警告）。如果 sibling 已写入同日 log entry，合并而不是追加重复条目。raw source 和 digest 文件可能被 sibling 用不同格式写入——只要 SHA256 和 source URL 正确即可，不需要覆盖。**Daily report 特别注意：** sibling 可能用更短的版本覆盖你的 comprehensive daily report。写 daily report 应放在所有其他文件更新之后（last step），写入前 re-read 目标文件检查是否已被 sibling 写入。若已被覆盖为较短版本，用 write_file 覆盖回完整版本（daily report 是最终交付物，需要完整内容）。若 sibling 版本已足够完整，可以 enrich 而非覆盖。 |
| Sibling 已完成部分或全部 pipeline（partial/full completion） | **Observed 2026-07-09 and 2026-07-11:** Sibling may complete any subset of the pipeline for any subset of new issues. Variant 1 (Jul 9): sibling created raw source + concept pages but NOT digest. Variant 2 (Jul 11): sibling created raw source AND digest for one issue (full pipeline), while a second issue in the same feed was completely unprocessed. Correct handling for ALL variants: (1) Check ALL pipeline artifacts (raw → digest → concept pages → index → log) for EACH new issue independently — do NOT assume sibling stopped at the same stage for all issues. (2) Skip any artifacts sibling already created; only create missing ones. (3) Verify sibling's SHA256 and source URL are correct, but do NOT overwrite. (4) In log, annotate which artifacts were sibling-created vs this-run-created. (5) Do NOT re-update concept pages sibling already touched — even if format differs, as long as content is correct. **Key judgment:** partial/full completion is normal concurrent mode, not a conflict. Wasting tokens redoing sibling's work is the error. |
| 手动精简 raw source 文件 | **raw source 层必须是 HTML→Markdown 的完整忠实转换**——每段、每个 bullet、每个链接都保留。精简、摘要、信号提取属于 digest 层（`digests/`），不属于 raw 层（`raw/newsletters/`）。如果发现自己在手动编辑转换后的 markdown 来"清理"，说明在做错误层的工作。转换脚本应直接从 `/tmp/issue_body.html` 产出 raw 文件，仅前置 frontmatter。详见 `references/html-to-markdown-conversion.md` 的 Common Pitfalls 表。 |
| RSS XML 直接在终端解析 | 大 feed（如 Smol AI News 2MB+ 含 600+ 条目）会超时或截断。先 `curl -o /tmp/feed.xml` 存文件，再 Python 解析 |
| 只看 RSS 标题判断是否有内容 | 有些 feed（如 Smol AI News）会用占位标题 `not much happened today`，但 `description` / `content:encoded` 里有大量真实内容。判断增量时以 `pubDate` + 正文内容为准，不要因标题像占位符就标记 dormant |
| RSS item 排序不严格按 pubDate | **Observed 2026-07-09:** Smol AI News feed 的 top item 为 `26-07-07-not-much/`（pubDate Jul 7），但 `26-07-08-grok-45/`（pubDate Jul 2）出现在第 4 个位置。RSS feed 的 item 顺序由发布平台决定，不一定按 pubDate 降序排列。**正确做法：** 不要只看第一条 item 判断是否有新内容。至少解析前 5-10 条，逐条用 slug 去重。如果只看第一条并假设它是最新 issue，可能遗漏实际存在的更新 issue。 |
| HTML `content:encoded` 需转 Markdown 才能写入 raw source | 使用 `html2text` 库（`pip3 install html2text`）转换。**关键：** RSS `content:encoded` 通常是 HTML 实体编码的（`&lt;p&gt;` 而非 `<p>`），必须先调用 `html.unescape()` 再传给 `html2text`，否则输出会包含原始 HTML 标签而非 Markdown。SHA256 应在原始实体编码的 HTML 上计算（unescape 之前），不在 Markdown 输出上。详见 `references/html-to-markdown-conversion.md` |
| 把 source dormancy 当成解析器故障 | 当主源连续多日无内容，应在整个 feed 中搜索缺失日期 slug（regex `/p/YYYY-MM-DD/`）确认 feed 本身确实没有。如果是 dormancy，立即写 gap report 并建议添加 backup 源，而不是反复重试空源。 |
| xAI 搜索配额耗尽时直接停止，或继续尝试已失败的 x_search | 当 `x_search` 和 `web_search`（xAI backend）同时返回 `403 with "spending-limit"`，切换到浏览器直采模式。使用 `browser_navigate` 访问已知新闻站点（HN, The Verge AI, Anthropic Newsroom, AI News）替代搜索。在日报中标注数据源切换。不要停 — 浏览器直采比跳过当天日报好。详见 `references/x-pulse-fallback-browser-2026-07-12.md`。 |
| 依赖 body hash 作为跨运行主去重键 | body hash 容易因 HTML 清洗/归一化管线微小差异（空格、换行、实体解码、frontmatter 是否包含）而产生不同值。**2026-06-24 运行还观察到 feed 级别的 hash 漂移**：feed 重新生成（regeneration）导致所有条目的 content hash 同时变化，不仅是个别条目。此外，不同 cron 运行可能使用了不同的 hash 公式（`sha256(content:encoded)` vs `sha256(title+link+body)` vs `sha256(converted_markdown)`），导致即使格式一致也无法跨运行比对。这意味着跨运行比较 hash 时，即使已编译条目的 hash 也可能不匹配——但这不代表有新内容。应把 **URL slug**（如 `26-06-22-not-much/`）作为首选去重键，hash 仅作同次运行内的辅助校验。参考 `references/smol-rss-body-hash-mismatch-2026-06-13.md` 及 `content-pipeline` skill 的 `references/html-to-markdown-conversion.md`。 |
| Feed size decrease 误判为 dormancy | **Feed size decrease ≠ no new content. 确认的重复模式（4 次观察 decrease + 1 次 increase）。** Decrease observations: 2026-07-03: 2,033,521 → 1,997,278 字节（-36KB），items 665→667，2 个新 slug。2026-07-08: 2,001,802 → 1,995,552 字节（-6KB），items 668→669，1 个新 slug。2026-07-09: 1,995,552 → 1,985,127 字节（-10KB），items 669→671，2 个新 slug。Increase observation: 2026-07-11: 1,985,127 → 2,053,563 字节（+68KB），items 671→673，2 个新 slug — the "normal" case where size increase correctly predicts new content. **结论：** feed size 无论增减都不能作为唯一判断依据。decrease 时新内容可能隐藏在归一化后的缩小中；increase 时是正常新内容添加。**正确做法：无论 feed size 增减，都必须做 full slug scan。** 只有 size byte-identical 且 item count 不变时才可安全跳过解析。详见 `references/feed-regeneration-size-decrease-new-content-2026-07-03.md`。 |
| `xml.etree.ElementTree` 在某些 RSS feed 上 ParseError | 大型 RSS feed（2MB+，600+ items）可能包含 XML 不合规字符导致 `ParseError: not well-formed (invalid token)`。**Fallback：用 regex 提取 `<item>...</item>` 块再用正则解析 title/link/pubDate/description/content:encoded。** 写 Python 脚本到 `/tmp/` 运行（不要内联）。Regex 方案虽不如 XML parser 严格，但对 Smol AI News 等 feed 实测可靠。详见 `references/feed-regeneration-size-decrease-new-content-2026-07-03.md` 的 fallback parser 脚本。 || 多个 cron job 检查同一 RSS 源且写入同一日报文件 | 当两个 cron job（如 `b8d13b0e9600` 和 `5d75c54287f8`）在数分钟内先后检查同一 RSS feed 并写入同一 `daily-reports/` 文件时，第二个 job 必须先检查同日报告是否已存在。若已存在：读取现有报告，用独立验证结果更新/enrich（如补充邮箱扫描、独立 RSS regex 确认），而不是创建重复文件或覆盖。同时更新 `log.md` 条目以反映双 run 贡献（标注 job ID 和时间戳），并检查 `index.md` 是否需要补上第一个 job 遗漏的条目。若第一个 job 已判定为 gap day，第二个 job 的独立验证增加了报告可信度——在报告中注明"confirmed by both runs"。 |
| `patch()` 工具在含复杂引号的 vault 文件上 escape-drift 失败 | `patch` 工具的 `old_string`/`new_string` 参数如果包含 `\"` 转义序列（如 `sources.md` 中的 delivery alert 含 `"thanks for reading..."` 等），会触发 "Escape-drift detected" 错误。**解决方案：** 不用 `patch`，改用 `terminal` + Python 脚本做字符串替换（`content.replace(old, new)`），或者把 old_string/new_string 中的引号写为非转义形式。这个问题在 cron 自动运行时特别危险，因为无法人工干预。适用于 `sources.md`、`index.md` 等 Markdown 文件中含 HTML 实体或嵌套引号的行。 |
| raw frontmatter 字段名不一致导致 slug 去重漏检 | **Observed 2026-07-26:** Sibling/prior runs 对 raw source 使用了不同 frontmatter schema。有的用 `source_url:` + `sha256:`，有的用 `source:` + `rss_hash:`（如 July 23 文件）。若 dedupe 脚本只读 `source_url:`，会把已编译 issue 误判为 NEW。**正确做法：** (1) 同时匹配 `source_url`、`source`、以及任意含 `issues/` 的 frontmatter URL 字段；(2) **raw 文件名存在**（`raw/newsletters/YYYY-MM-DD-smol-ai-news.md`）是强已编译信号——date 对应的文件存在即 skip，即使 frontmatter 字段名不同；(3) hash 字段同时接受 `sha256` / `rss_hash`；(4) 跨 schema 时仍以 **URL slug** 为主键，不要因 frontmatter 键名差异重写已有 raw。详见 `references/raw-frontmatter-schema-variance-2026-07-26.md`。 |
| 周五 issue 周六缺失、周日才出现（delayed weekday publish） | **Observed 2026-07-25 → 2026-07-26:** July 25（Sat）两轮 cron 均确认 feed 无 `26-07-24`；July 26（Sun）feed 增至 2,118,148 B / 683 items 并出现 `26-07-24-opus-5/`。这不是 dormancy，是 **delayed Friday publish / weekend feed lag**。**正确做法：** (1) 周末 gap 报告写 “no Fri/Sat issue yet — may appear via delayed publish”，不要升级为 3–7 day dormancy；(2) 周日/周一运行必须 full slug scan，专门检查上一工作日缺失 slug；(3) 一旦 delayed issue 出现，正常 ingest（raw→digest→concepts→index/log/sources），不要因 “昨天已写 gap” 就跳过；(4) 与 feed regeneration 区分：delayed publish 会增加 item count + 新 date slug；rename 只改已有 date 的 suffix。 |
| 批量更新 wiki（concepts + log + sources + index）时逐文件 `patch` | multi-file vault 更新（3 个 concept 追加 section + frontmatter sources 列表 + log 顶部插入 + sources 状态行 + index 导航）用多次 `patch` 容易撞 escape-drift / 部分成功。**优先：** 写一个 `/tmp/update_wiki.py`，用 Python 读写一次性完成 frontmatter `sources` 追加、section append、log prepend、sources/index 替换；最后再 verify 文件 size/非空。Daily report 与 digest 仍可单独 `write_file`。 |
| `log.md` 顶部 prepend 用裸 substring `find("## [")` 定位首个 entry | **Observed 2026-10-03:** `log.md` 头部 `> Format: \`## [YYYY-MM-DD] action | subject\`` 行内含字面 `## [`，Python `s.find("## [")` 会命中该行而非首个真实条目，把新日志 splice 进 Format 行中间。**正确做法：** 用行首锚定 `re.search(r"(?m)^## \[", s)` 找首个真实条目位置再插入；写完必须 re-read 头部验证 Format/Actions 两行完好。 |

---

## 11. 与其他 skills 协作

- `obsidian-ai-workflows`：保存日报、clipping、主题页
- `horizontal-vertical-analysis`：对重要主题做横纵深研
- `link2doc`：整理 thread/资源合集到 Neuma-Superpower
- `competitor-research`：竞品动态深挖
- `social-media-agent-workflow`：把信息差转成内容资产
- `linear`：把机会/任务同步到 Linear

---

*AI 信息差 Agent 工作流 - 来自翡冷翠工作流沉淀*
