---
name: link2doc
description: "从链接/来源收集信息，整理成完整文档，提交到 GitHub 仓库的完整工作流。适用于：聚合类内容整理、教程合集、资源清单、竞品信息汇总等场景。中文名：内容策展流程。"
category: productivity
tags: [curation, documentation, github, content-aggregation, tutorial]
trigger: ["整理成文档", "收集这些内容", "提交到 GitHub", "聚合内容", "教程合集", "资源清单"]
---

# link2doc - 内容策展流程

将分散的链接/来源聚合为完整文档并发布到 GitHub 的标准化工作流。

## 触发条件

当用户出现以下行为时激活：
- 分享一个包含多个链接/资源的 X/Twitter 帖子
- 分享一个资源合集（教程清单、工具推荐等）
- 说"把这个整理成文档"、"收集这些内容"
- 要求"提交到 GitHub"

## 工作流

### Step 1: 理解任务与来源分析

**明确关键信息：**
- 来源链接是什么？（X 帖子、博客、GitHub 等）
- 目标仓库是哪个？（默认：`marovole-Superpowers`，路径：`/Users/marovole/Workspace/playground/HermesWork/marovole-Superpowers`。如果该仓库不存在，检查 `/Users/marovole/Workspace/` 下是否有其他合适的公司仓库。`/Users/marovole/GitHub` 只用于个人项目。注意：`marovole-Superpowers` 是 Hermes skills 聚合仓库，docs/ 目录专门存放策展文档。）
- 文档应放在哪个目录？（默认：`docs/`）
- 是否需要同步 Linear？（如果有相关 issue）
- 是否需要邮件通知？（默认发送给 <YOUR_PRIMARY_EMAIL>）

**署名要求（必须遵守）：**
- 文末署名：**"来自翡冷翠"**
- 禁止写："本文由 Neuma AI Agent 整理输出" 等机器人式表述
- 教程内容应面向"任何人"，不限定为"Neuma 团队"

### Step 2: 提取链接列表

**场景 A: X/Twitter 普通帖子 / 聚合帖**

X 帖子提取有两个可靠方案，优先尝试 Jina Reader（无需启动浏览器 daemon，绕过登录墙）：

```bash
# 首选：Jina Reader — 直接提取 X 帖子正文和嵌入链接
curl -sL "https://r.jina.ai/http://x.com/{user}/status/{id}"
# 输出包含：帖子正文、作者信息、图片链接、互动数据

# 备选：browser_navigate（需要 agent-browser daemon 已启动）
browser_navigate(url="https://x.com/...")
browser_snapshot()
```

**从正文提取所有引用的子帖子 URL 和外部链接**，然后进入 Step 3 逐一研究。

**场景 A-0: X/Twitter 自包含帖**（内容在帖文本中，无外部链接）

当帖文本本身就是一个完整的推荐/清单（如"推荐 6 个播客"），无外部子链接可提取时：
1. 直接从快照提取完整帖文本
2. 对清单中每个条目做深度调研（用 `delegate_task` 并行研究）
3. 输出文档结构：清单总览 → 逐条目详情（含研究补充）→ 汇总 → 使用建议
4. 这种帖子的价值在于筛选和点评，而非链接聚合

**场景 A-1: X/Twitter Articles（长文/长帖）**

X 的长文功能（Articles/X Articles）有特殊处理方式：

1. **识别 Article**：URL 格式为 `/article/xxxx` 或推文中有 "Focus mode" 链接
2. **直接访问可能 404**：文章链接 `/i/article/xxxx` 可能无法直接访问
3. **内容已嵌入推文页**：完整内容通常在原始推文页面中，以多个 `text:` 块和 `heading:` 呈现
4. **处理策略**：
   ```python
   # 第一步：访问原始推文
   browser_navigate(url="https://x.com/alphasignalai/status/2047014600713842728")
   browser_snapshot(full=true)  # 获取完整快照
   
   # 如果内容被截断（truncated），滚动页面加载更多
   browser_scroll(direction="down")
   browser_snapshot(full=true)
   
   # 不要尝试直接访问 /i/article/xxx 链接（通常会 404）
   # 所有内容已从推文页面快照中提取
   ```
5. **内容提取**：Article 内容在快照中以以下形式出现：
   - `heading "标题"` - 章节标题
   - `text: "正文内容"` - 段落文本
   - `blockquote: "引用内容"` - 引用块
   - `[... N more lines truncated]` - 提示有更多内容，需要滚动

**场景 B: 其他网页来源**
```python
# 尝试 web_extract，失败则 fallback 到 browser
web_extract(urls=["https://..."])
# 或使用 Jina Reader
# curl -sL "https://r.jina.ai/http://..."
```

**场景 C: 用户直接提供链接列表**
- 直接使用用户提供的链接列表，跳过提取步骤

> 完整场景处理（X Article、Quote Chain、GitHub Raw、Showcase、评论镜像等）见 [references/extraction-scenarios.md](references/extraction-scenarios.md)。

### Step 3: 逐一收集详情（含发布者洞察）

对每个提取到的链接：

```python
# 访问子链接收集完整信息
browser_navigate(url=sub_url)
browser_snapshot()

# 记录以下字段（特别注意发布者洞察）：
# - 标题
# - 作者/来源
# - 发布时间
# - 核心内容摘要
# - 关键资源链接（GitHub、官网等）
# - 代码/命令片段
# - ⚡ 发布者洞察：
#   * 个人体验（"我用了 X 个月..."）
#   * 核心优势（"比传统方式快 10 倍"）
#   * 推荐理由
#   * 可直接引用的原话
```

**收集策略：**
- 教程类：记录核心步骤、安装命令、使用示例 + 作者踩过的坑
- 工具类：记录功能特点、GitHub 链接、适用场景 + 作者的实际使用体验
- 文章类：记录核心观点、关键数据、引用来源 + 作者的个人立场

**多条目并行研究（推荐）**：当清单包含 3+ 个独立条目时，用 `delegate_task` 并行研究比逐个访问快得多。

```python
# 模式：delegate_task + terminal(Jina Reader) 并行研究
delegate_task(
    context="Research these items. Use Jina Reader: curl -sL 'https://r.jina.ai/<url>' ...",
    tasks=[
        {"goal": "Research item 1", "toolsets": ["terminal"]},
        {"goal": "Research item 2", "toolsets": ["terminal"]},
        {"goal": "Research item 3", "toolsets": ["terminal"]},
    ]
)
```

Jina Reader (`https://r.jina.ai/<url>`) 能绕过大多数反爬和登录墙（包括 DuckDuckGo CAPTCHA、X 登录墙、Cloudflare），是搜索/提取的可靠通用方案。

### Step 4: 构建综合文档

**标准文档结构：**

```markdown
# {主帖/来源标题} - 完整整理

> 来源：{原始链接}
> 整理时间：YYYY-MM-DD
> 来自翡冷翠

---

## 简介
（用 2-3 句话概括这个合集的核心价值）

## 内容清单总览

| 序号 | 标题 | 作者/来源 | 类型 | 核心亮点 |
|------|------|-----------|------|----------|
| 1 | ... | ... | 教程/工具/文章 | ... |
| 2 | ... | ... | ... | ... |

---

## 详细内容

### 1. {内容1标题}
**来源**：@{author} / {source}
**链接**：{url}
**类型**：{教程/工具/文章}

#### 核心内容
- 要点 1
- 要点 2
- 要点 3

#### 关键资源
- GitHub: {link}
- 官网: {link}
- 文档: {link}

#### 适用场景
（这段内容适合解决什么问题）

---

### 2. {内容2标题}
（同上结构）

---

## 资源汇总

### 所有 GitHub 仓库
| 项目 | 链接 | 简介 |

### 所有官方链接
| 名称 | 链接 | 说明 |

### 值得关注的人/账号
- @{handle} - {简介}

## 建议学习/使用路径

（如何按顺序使用这些资源，或推荐的学习路径）

## 附录：快速参考

（常用命令、配置片段、速查表）

---

*来自翡冷翠*
```

### Step 5: 提交到 GitHub

```bash
cd /Users/marovole/Workspace/playground/HermesWork/marovole-Superpowers

# 保存文档到目标目录
# 文件命名规范: {主题关键词}-{日期}.md
# 示例: hermes-tutorials-2026-04-22.md

# Git 操作
git add docs/{filename}.md
git commit -m "docs: add {主题} 完整整理 ({日期})"
git push origin main
```

**提交后记录：**
- 文件路径
- GitHub URL（如 `https://github.com/{user}/{repo}/blob/main/docs/{filename}.md`）

### Step 6: 同步 Linear（如有，仅公司项目）

**用户偏好：Linear 仅用于公司项目**
- 个人内容整理（如 Superpowers 技能库）**不**同步到 Linear
- 仅当内容与公司项目（如 Neuma/Neumina）相关时，才考虑同步

如果需要同步 Linear issue：

```python
# 更新 issue 状态为 Done
mcp_linear_save_issue(id="NEU-XXX", state="Done")

# 添加完成评论
mcp_linear_save_comment(
    issueId="NEU-XXX",
    body="""✅ 已完成

**产出物：**
- GitHub: {github_link}
- 本地路径: {local_path}

**文档概要：**
- 整理来源：{source}
- 内容数量：{N} 个
- 文档大小：{size} 字

来自翡冷翠"""
)
```

**决策流程**：
```
用户要求整理内容
    ↓
内容是否与公司项目相关？
    ├─ 是 → 询问是否需要同步 Linear
    └─ 否 → 跳过 Linear 步骤，直接 GitHub + 邮件交付
```

### Step 7: 邮件交付

**邮件配置（固定）**：
- 主收件人：**<YOUR_PRIMARY_EMAIL>**
- 抄送：**<YOUR_CC_EMAIL>**

**可靠方案：`write_file` 写入临时文件 + `terminal` 执行 `osascript`**

⚠️ 在 terminal 工具中，`osascript -e` 内联方式容易因特殊字符（`&`、中文引号等）触发工具的后台进程误判而失败。必须用 `write_file` 写入 `.applescript` 文件再执行。

```bash
# Step 1: 前置验证 Mail.app 是否已配置
osascript -e 'tell application "Mail" to try
    get name of every account
    return "Mail configured"
end try'

# Step 2: 用 write_file 工具写入 AppleScript 到临时文件
# 路径: /tmp/mail-script.applescript
# 内容见下方模板

# Step 3: 执行
osascript /tmp/mail-script.applescript
```

**AppleScript 模板**（写入 `/tmp/mail-script.applescript`）：

```applescript
tell application "Mail"
    try
        set newMessage to make new outgoing message with properties {subject:"{主题} - doc ready", content:"Hi,

「{文档标题}」已整理完成并提交到 GitHub。

GitHub: {github_link}
Local: {local_path}

Summary: {摘要}

- From Feilengcui"}
        tell newMessage
            make new to recipient with properties {address:"<YOUR_PRIMARY_EMAIL>"}
            make new cc recipient with properties {address:"<YOUR_CC_EMAIL>"}
            send
        end tell
        return "sent"
    on error errMsg
        return "fail: " & errMsg
    end try
end tell
```

**注意事项**：
- 邮件正文使用纯英文以避免 AppleScript 中文编码问题
- 必须包含 GitHub 链接，即使附件发送失败用户也能访问
- 如果 `osascript` 返回 `sent` 即为成功

**关键原则：**
1. **邮件正文必须包含 GitHub 链接** - 即使附件发送失败，用户仍能通过链接访问内容
2. **前置验证** - 先检查 Mail.app 是否已配置
3. **用 `write_file` + `osascript`** - 先 `write_file` 写入 `/tmp/mail-script.applescript`，再 `terminal` 执行 `osascript /tmp/mail-script.applescript`，避免内联 `-e` 参数的特殊字符陷阱
4. **失败不阻塞** - 邮件发送失败不应阻塞整个任务完成通知

## 吸收价值评估（用户可能询问"有什么值得吸收的"）

整理完资源合集后，用户常问："这两个内容 有什么值得吸收进的吗"

### 价值评估矩阵

| 维度 | 高价值信号 | 低价值信号 |
|-------|------------|------------|
| 可复用性 | 多次被引用、形成模式 | 一次性、场景特定 |
| 扩展性 | 可整合到现有流程 | 孤立、难以整合 |
| 质量 | 有完整文档/测试/社区 | 缺乏维护/文档过时 |
| 独特性 | 提供新的解决方案 | 重复现有技能能力 |
| 稳定性 | 主动维护、版本更新 | 已弃用、仓库下架 |

### 吸收策略决策树

```
评估资源价值
    ├─── 高价值 + 可直接使用 → 策略A: 直接 clone + 安装 + 测试
    ├─── 高价值 + 需整合 → 策略B: 修改现有 skill 整合该模式
    ├─── 中等价值 → 策略C: 保留分析文档作为未来参考
    └─── 低价值/已下架 → 策略D: 记录即可，不深入
```

### 实施步骤

**Step 1: 价值分级**
为每个资源打星（1-5 星）：
- ⭐⭐⭐⭐⭐ 高优先级 - 建议立即调研
- ⭐⭐⭐⭐ 中高优先级 - 有需要时调研
- ⭐⭐⭐ 中优先级 - 参考即可
- ⭐⭐ 低优先级 - 可以忽略

**Step 2: 与现有技能对比**
列表对比表：
| 资源 | vs 我的现有技能 | 关键差异 | 整合建议 |

**Step 3: 立即行动**
根据优先级推荐具体动作：
1. **clone 研究** - 高优先级资源的实现细节
2. **对比优化** - 与现有技能的差异对比
3. **创建 skill** - 如果值得整合，创建新 skill 或修改现有 skill

### 本会话示例

**场景**：整理 Hermes Agent 资源合集后，用户问"有什么值得吸收进的吗"

**执行**：
1. 分析 11+10 个资源
2. 打星分级：3 个 ⭐⭐⭐⭐⭐（4 个 ⭐⭐⭐⭐
3. 对比现有技能：
   - Skill Factory vs agent-self-evolution → 关键差异在于 AI 主动分析
   - Atlas 分类 vs 我的分类 → 可优化 Superpowers 结构
4. 推荐动作：clone Skill Factory 研究其自动提炼算法
5. 执行重构：重命名 4 个 skills，创建 7 个新分类，移动 20 个技能

### 参考文档

详细分析案例见：[references/high-value-content-patterns.md](references/high-value-content-patterns.md)
- `references/jina-reader-research.md` — Jina Reader 并行研究模式，`web_search` 不可用时的首选替代方案

---

## 工具选择决策树

| 任务 | 首选工具 | 备用方案 |
|------|----------|----------|
| 读取 X/Twitter 普通帖子 | `browser_navigate` + `browser_snapshot` | — |
| 读取 X/Twitter Articles（长文） | `browser_navigate` 原始推文页 + 滚动 | 不要尝试直接访问 `/i/article/xxx` |
| 读取普通网页 | `web_extract` | `curl` + Jina Reader |
| 读取 llms.txt / llms-full.txt | `curl -sL` | 不要用 browser（纯文本不会被渲染，返回空页） |
| 读取 GitHub README | `curl -sL raw.githubusercontent.com/...` | `web_extract` |
| 搜索补充信息 | `delegate_task` + terminal(Jina Reader) | `terminal` + `curl -sL` 直抓 |
| Cloudflare 防护页面 (pplx.ai 等) | Jina Reader (`r.jina.ai`) | 如果也 403，记录链接让用户手动访问 |
| 写文档 | `write_file` | — |
| Git 提交 | `terminal` (git) | — |
| 更新 Linear | `mcp_linear_*` | — |
| 发送邮件 | `write_file` → `terminal` (osascript) | — |

### 检查引用的 GitHub 仓库可访性

在安装或 clone 前，验证仓库是否存在：

```bash
# 验证仓库可访性
curl -sI https://github.com/Romanescu11/hermes-skill-factory.git
# 如果返回 404/403，记录并告知用户

# 示例：本会话发现
# - hermes-atlas 已下架 (404)
# - 需引用历史描述或搜索替代资源
```

**处理策略**：
- 404: 记录为"已下架"，尝试搜索镜像/替代
- 403: 可能变为私有，记录并告知用户无法访问
- 200: 正常 clone 分析
| 默认仓库不存在 | `Neuma-Superpower` 等旧路径已废弃 | 当前默认仓库为 `marovole-Superpowers`（`/Users/marovole/Workspace/playground/HermesWork/marovole-Superpowers`），docs/ 目录专门存放策展文档 |

## 变体场景

### 变体 A: 单来源深度整理
如果用户只提供 1 个链接但需要深度整理（如一个 GitHub 项目）：
- 省略"提取链接列表"步骤
- 直接进入"深度收集"模式
- 输出结构改为单篇详细教程

### 变体 B: 无需 GitHub 提交
如果用户只需要本地文档：
- 保存到 `~/Workspace/HermesWork/reports/`
- 跳过 Git 和 Linear 步骤
- 直接交付文件路径

### 变体 C: 单来源深度整理（长文/复盘/教程）

当用户提供的是 **1 个长篇文章链接**（非聚合帖），且内容本身足够丰富需要深度拆解时：

**流程调整**：
1. 用 Jina Reader 提取完整文章内容（长文通常 5,000–15,000 字）
2. 识别文章中引用的所有外部资源/工具/API/数据
3. 对关键资源做并行深度调研（delegate_task + terminal + Jina Reader）
4. 构建综合文档结构：
   - 简介（原文核心结论 2-3 句话概括）
   - 核心数据拆解（所有数据表格化）
   - 系统架构详解（如原文有多个子系统，逐一拆解）
   - 有效 vs 没效（诚实复盘，保留原文的自我批判）
   - 工具链汇总（所有工具的名称/用途/费用/链接）
   - 可复制检查清单（Phase 1/2/3 式的行动指南）
   - 核心金句（原文最值得传播的观点）

**文档规模**：单来源深度整理通常 500–800 行，远大于聚合帖整理（200–400 行）。

**示例**：yage.ai AI 托管增长复盘 → 528 行文档，含 5 大自动化系统详解、R/T/N 内容分类框架、UTM 归因模板、SEO 优化策略、复制检查清单。

### 变体 D: 学术文献 / PDF 缺失清单补全

当用户给出 handoff、manifest 或表格要求“找齐文献 / 下载 PDF / 放到某目录”时：
- 先读取清单，提取 docId、标题、作者、期刊、年份、DOI/PMID/PII。
- 优先使用 Crossref、PubMed ESummary、OpenAlex、Unpaywall 校验 DOI/PMID/标题是否匹配；不要只依赖 handoff 中的 DOI/PMID（可能错配）。
- 下载顺序：官方 OA PDF / repository PDF / Europe PMC PDF / publisher public PDF / public HTML 转 PDF fallback。
- 对闭源或登录墙文献，不要用摘要、患者版指南、错误相似文献冒充目标全文。若必须生成文件占位，应在文件和 README 中明确标注 `metadata/abstract fallback` 或 `NOT_TARGET`。
- 对 NCCN、NEJM、Elsevier、Taylor & Francis 等登录/订阅内容，记录获取障碍和官方 URL，建议用户用登录、机构订阅、作者共享链接或馆际互借手动获取。
- 保存 `download_manifest.json`（尝试记录）和 `FINAL_STATUS.json`（文件大小、页数、hash、状态），并写 README 说明哪些文件可入库、哪些不能当全文入库。
- 文件命名严格按 `{docId}.pdf`；补充/非目标资料用 `{docId}_..._NOT_TARGET.pdf`，避免被流水线误 ingest。

