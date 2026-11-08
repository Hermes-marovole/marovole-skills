# marovole-skills

> 让你的 Agent 直接接管市场调研、写书、做片和发帖：从本机 120+ 个 Agent 技能里筛出的 10 个主力实战 Skill（含单篇 50 万+ 浏览的「大佬说」访谈长图管线、单次强制落盘 300+ 原始样本的 14 维商业情报、13 阶段全自动写书与零漂移 AI 短片导演），每个都自带验收脚本和防翻车护栏。

装上之后，直接对你的 Claude Code、Codex 或 Hermes 说一句：
- `做一条大佬说 <YouTube/X访谈链接>` — 自动切出 1080p 正脸特写 + 中英对译字幕长图（实测单篇最高 **50 万+ 浏览**，多篇 12w+/5.8w/3.6w）
- `用 market-intelligence 深度调研 XX 行业` — 先往硬盘落够 **300–1,000 条** 招股书、1688 底价、闲鱼弃坑、黑猫投诉与差评原始数据，才准动笔写报告
- `用 doctor-book 给某医生写一本 10 万字科普书` — **13 个阶段**全自动跑完素材入库、文风提炼、医学合规挑刺到 `docx/epub` 投稿包
- `用 ai-story-video-director 导一支 30 秒短片` — 文字 ¥0 改错，首尾帧背景像素差锁死为 **0**、过零上下文盲审才准送去烧钱渲染

本仓库不是 `~/.hermes/skills` 的完整镜像。完整 live skill registry 以本机 Hermes 环境为准：

```bash
/Users/marovole/.hermes/skills
```

本仓库的定位是：

1. 保存高信号 AI / Product / Biohacking / Agent 工作流文档
2. 存放少量已经推广为公共资产的精选 `marovole-*` 系列 skills
3. 记录技能体系的分类、审计、重构和吸收过程
4. 作为个人能力复利系统的 GitHub 版本化出口

---

## 项目主旨

从外部信号中提炼可执行能力。目标不是收藏链接，而是完成这条链路：

```text
捕获 Source → 研究 Research → 实验 Experiment → 固化 Skill/Workflow → 复用 Reuse
```

原则：

- 信号 > 噪音：只收集经过验证或高潜力的 AI 应用
- 文档即代码：所有研究过程与结论必须可复现、可版本化
- Skill 优先：有复用价值的流程最终沉淀为 Hermes skill 或工作流文档
- 精选入库：repo/skills 只放 promoted skills，不追求镜像全部本地 skills

---

## 当前仓库结构

```text
marovole-skills/
├── README.md
├── docs/                 # 主体：研究、教程、工具评估、工作流文档
├── research/             # 研究报告与专题分析
└── skills/               # 精选 promoted Hermes skills，不是完整 registry
```

当前 promoted skills（共 12 个）：

| Skill | 路径 | 一句话结果与核心护栏 |
|---|---|---|
| **interview-quote-image-posts**（大佬说） | [skills/content-publishing/interview-quote-image-posts/](skills/content-publishing/interview-quote-image-posts/) | **单篇最高 50 万+ 浏览**（多篇 12w+/5.8w/3.6w）：外文访谈 → 3:4 真人特写中文字幕长图；自动筛 1080p 原片、OpenCV 检出 ≥200px 正脸特写、避开 0.82 水印区、过 Gemini 盲审 `PASS` 后出多平台发布包 |
| **market-intelligence** | [skills/research/market-intelligence/](skills/research/market-intelligence/) | **单次强制落盘 ≥300–1,000 条一手样本**：14 维全覆盖（美港 A 股招股书、200+ 搜索联想词、80+ 电商买家评论、30–60 家 1688 代工底价、闲鱼弃坑率、招聘 JD 私域成本、黑猫投诉、20–50 篇 PubMed 文献），交付浅色一页到底 HTML |
| **doctor-book** | [skills/content-publishing/doctor-book/](skills/content-publishing/doctor-book/) | **13 阶段全自动写完 8–12 万字医生健康科普书**：从访谈入库、10+ 原句文风提取、三幕 10–14 章大纲，到 `lint_chapter.py` 质检、医学 6 大高危区合规挑刺，直接导出 `book.docx` / `book.epub` 与出版社投稿包 |
| **ai-story-video-director** | [skills/media/ai-story-video-director/](skills/media/ai-story-video-director/) | **首尾帧零漂移 + 最低抽卡率 AI 短片总导演**：人物锁 38%/62% 黄金位、倒序作画 + 局部修改 `patch` 贴回锁死背景像素差为 0、7 段式提示词 + 20 大翻车黑名单、零上下文盲审放行后才送渲染 |
| **exercise-follow-along-video** | [skills/media/exercise-follow-along-video/](skills/media/exercise-follow-along-video/) | **运动跟练视频管线**：拆解实拍样例 → `gpt-image-2` 锁死人物设定与动作关键帧 → MiniMax H3 首尾帧生成 → 循环拼装 + 倒计时 UI + 成片验收 |
| **minimax-h3-colab** | [skills/media/minimax-h3-colab/](skills/media/minimax-h3-colab/) | **Colab G4（RTX PRO 6000 96GB）跑 MiniMax H3 视频**：直出 768p 视频 + 立体声音频（文生 / 首尾帧 / 多镜头参考），内置跑完强制销毁运行时防漏扣 CCU |
| **neumina-lifestyle-course-design** | [skills/autonomous-ai-agents/neumina-lifestyle-course-design/](skills/autonomous-ai-agents/neumina-lifestyle-course-design/) | **14 天生活方式训练营课程骨架**：从抗炎饮食到皮质醇管理等主题的一键迁移课程设计系统 |
| **link2doc** | [skills/research/link2doc/](skills/research/link2doc/) | **外部链接 → 结构化知识库文档**：从网页、长文、GitHub 收集高信号内容，整理成可复现 Markdown 文档并归档入库 |
| **x2doc** | [skills/research/x2doc/](skills/research/x2doc/) | **X/Twitter 帖子 → 深度文档 + 转发推文 + 邮件简报**：自动抓取 X 长文、Quote 链与评论区洞察，一键生成知识库文档与可复制转发语 |
| **dokobot** | [skills/dokobot/](skills/dokobot/) | **真实 Chrome 网页提取器**：用带登录态的真实浏览器读取 JS-heavy 或登录墙后的深层网页内容 |
| **topic-to-matrix** | [skills/content-publishing/topic-to-matrix/](skills/content-publishing/topic-to-matrix/) | **一个选题 → 长片/短视频/贴图/长文四形态 × 中美多平台判断单**：只抓一次原文建事实表，`hub.py check` 校验引语可回溯、审核小时不超预算；个人号选题强制过「不用学写代码，学会像产品经理一样指挥 AI」IP 原则（真实提问 / 卡在哪一步 / 并排实测，短视频 ip_fit≥4） |
| **content-creator-pipeline** | [skills/social-media/content-creator-pipeline/](skills/social-media/content-creator-pipeline/) | **「存 / 做」双暗号内容流水线**：素材入库 + 30 秒编导判断单（含 IP 对齐），或直接走 grounding + 独立 subagent 逐句核查推草稿箱；本仓库副本已脱敏 IP/邮箱/密钥路径 |

完整 live registry 请查看本机：

```bash
find /Users/marovole/.hermes/skills -name SKILL.md
```

---

## 关键文档入口

### Skills 体系与 Hermes Agent OS

| 文档 | 说明 |
|---|---|
| [Superpowers Skills Health Map](docs/superpowers-skills-health-map-2026-05-02.md) | 当前 repo 与本地 Hermes skills 的健康检查、差异和后续建议 |
| [Hermes Skills Phase 3 Local Refactor](docs/hermes-skills-phase3-local-refactor-2026-05-02.md) | 本地 `~/.hermes/skills` 中 creative 与 software-development 拥挤分类拆分记录 |
| [Superpowers Skills 分类分析](docs/superpowers-skills-classification-analysis-2026-05-01.md) | 2026-05-01 skills 分类重构分析 |
| [Skills 重构完成报告](docs/REFACTORING_SUMMARY_2026-05-01.md) | `~/.hermes/skills` 分类优化总结 |
| [Hermes Skill Factory 分析](docs/hermes-skill-factory-analysis-2026-05-01.md) | 自动从工作流生成 skill 的机制研究 |
| [Hermes Agent 资源合集](docs/hermes-agent-resource-compilation-2026-05-01.md) | Hermes 生态资源整理 |
| [Hermes 多 Agent 设置教程](docs/hermes-multi-agent-setup-tutorial.md) | 多 Agent 协作配置 |

### Prompt / Agent / Workflow

| 文档 | 说明 |
|---|---|
| [GPT-5.5 Prompting Guide](docs/gpt-5.5-prompting-guide-2026-04-30.md) | 新一代模型 outcome-first prompt 标准来源 |
| [SkillClaw Agent Skill Evolution](docs/skillclaw-ai-agent-skill-evolution-2026-05-02.md) | Agent 技能进化机制 |
| [Waza Skills System Tutorial](docs/waza-skills-system-tutorial-2026-04-30.md) | Waza 技能体系教程 |
| [Claude Code Burn Token Workflow](docs/claude-code-burn-token-workflow-2025-04-30.md) | 夜间消耗 idle quota 的自主研究工作流 |
| [OpenClaw Browser Automation Guide](docs/openclaw-browser-automation-guide.md) | 浏览器自动化工具研究 |

### 内容与发布工具

| 文档 | 说明 |
|---|---|
| [md2wechat Skill Complete Guide](docs/md2wechat-skill-complete-guide-2026-04-27.md) | Markdown 到公众号排版发布 |
| [Markdown to Image Cards](docs/md-poster-markdown-to-image-cards-2026-04-29.md) | Markdown 转社交媒体卡片 |
| [HyperFrames AI Video Guide](docs/hyperframes-ai-video-guide.md) | AI 视频内容工具 |
| [AI Content Tools: HyperFrames + ChatPDF](docs/ai-content-tools-hyperframes-chatpdf-2026-05-02.md) | 内容工具指南 |

### GPT-image / Creative

| 文档 | 说明 |
|---|---|
| [Awesome GPT-image-2 Curation](docs/awesome-gpt-image-2-curation.md) | GPT-image-2 案例与提示词策展 |
| [GPT Image 2 Prompts Collection](docs/gpt-image-2-prompts-collection-2026-04-24.md) | GPT-image-2 提示词合集 |
| [Concept Poster Prompt Framework](docs/concept-poster-prompt-framework-2026-04-27.md) | 概念海报 prompt 框架 |
| [ChatGPT JSON Style Guide](docs/chatgpt-json-style-guide.md) | JSON 风格协议 |

---

## 工作流

### 内容策展

```text
source link/thread → link2doc → docs/*.md → review → git commit/push
```

默认输出位置：`docs/`

### Skill 吸收

```text
docs candidate → 判断是否可执行/可复用 → 对比现有 ~/.hermes/skills → create/patch skill → 必要时 promoted 到 repo/skills
```

注意：

- 纯信息清单不一定转 skill
- 已有 skill 覆盖时优先 patch，不重复创建
- 新 skill 应遵循 GPT-5.5 Prompt Strategy：Goal → Success Criteria → Constraints → Stop Rules → Verify

### 仓库维护

```bash
git pull --ff-only
# 新增或更新 docs/ 与 promoted skills
git status --short
git add <files>
git commit -m "docs: ..." 或 "skills: ..."
git push
```

---

## 与本地 Hermes Skills 的关系

本机 Hermes 使用的完整技能库位于：

```bash
/Users/marovole/.hermes/skills
```

`marovole-skills` 仓库只保存：

- 重要研究和教程文档
- 值得公开/迁移/复用的 promoted skills
- skills 分类、审计和重构报告
- 外部工具/方法论的吸收记录

这意味着 README 不再列出 120+ live skills 的完整索引，避免 GitHub 仓库结构与本地 Hermes 运行时状态发生误导性不一致。

---

## 更新原则

1. 新内容优先进入 `docs/`
2. 只有经过验证、可复用、适合共享的能力才进入 `skills/`
3. 每次 skills 结构变动后更新健康检查或相关说明
4. 署名保持个人身份：来自翡冷翠

---

*来自翡冷翠* | 持续更新于 2026-11-06
