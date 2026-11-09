# Claude 官方课程全集拆解：从 GitHub 归档 (5门) 到 Skilljar (23门) 再到 Claude Academy (29门) 的三代演进与底层架构

> **整理人**：来自翡冷翠  
> **数据核验基准日**：2026-11-09（全部基于本次直接抓取的 Anthropic 官方页面与 GitHub API 原文）  
> **核心结论**：市面上大量“Claude 官方教程合集”还在转发 2024 年 5 月建仓、**目前已正式 `archived`（归档停更）** 的 `github.com/anthropics/courses`（仅 5 门基于 Claude 3 Haiku 的提示词与 API 基础课）；而第二代 `anthropic.skilljar.com`（23 个课程/路径条目）页面顶部已挂出黄牌警告：**将于 2026 年 12 月初永久关闭**。真正的最新官方大本营是 **Claude Academy（`academy.claude.com`，全站聚合 322 项学习资源［`/all` 总表正文显示 429 项］、29 门正式课程）**。把这 29 门课拆到底，Anthropic 已经不再把重心放在“酷炫提示词（cool prompts）”，全面转向 **「4D 人机协作框架 + 6 阶段 AI 原生研发（SDLC）+ 3 层指令表面 + 5 项企业治理决策」**。

---

## 一、三代官方课程演进全景图（避坑第一课）

| 代际 | 平台入口 | 课程规模 | 核心模型与定位 | 2026-11 真实状态（一手核验） |
|---|---|---|---|---|
| **第一代（2024.05）** | `github.com/anthropics/courses` | **5 门** Jupyter Notebook 课程 | 基于 **Claude 3 Haiku**，讲 API 请求、9 章提示词基础（角色/数据指令分离/分步思考/示例/防幻觉等）、Promptfoo 评测、基础 Tool Use | **已归档（`archived: true`，22,999 Stars / 2,547 Forks）**，最后推送停在 2026-08-28 |
| **第二代（2025–2026）** | `anthropic.skilljar.com` | **23 个**课程/路径条目 | 引入 Claude 101、Claude Code 101、Cowork、MCP、4D AI Fluency、AWS Bedrock / Google Cloud 专班 | **即将关停**：顶部横幅写明 *"This legacy learning experience will no longer be available in early December 2026"*，进度与证书需在 12 月初前同邮箱导入新站 |
| **第三代（现行主力）** | `academy.claude.com`（Claude Academy） | **29 门**正式课程（课程筛选页显示 322 项资源，`/all` 总表正文显示 429 项） | 围绕 **5 大产品入口**（Claude / Cowork / Claude Code / Claude Tag / Claude Platform）+ **Fable / Opus / Sonnet / Haiku / Mythos 5** 构建完整 Agent 与组织治理体系 | **全面免费开放**（免付费订阅即可保存进度并在带测验的课程考取 Completion Badge；Pearson/Credly 监考认证仅面向合作伙伴站点 `anthropic-partners.skilljar.com`） |

---

## 二、现行 Claude Academy 全部 29 门官方课程完整清单与分类拆解

Anthropic 官方在 `academy.claude.com/courses` 将 29 门课程划分为 **4 大模块（5 大产品底座）**。以下为逐门核实的课时、测验、时长与核心教学内核：

### 模块 A：Start your journey（5 大核心产品 101 入门 · 共 5 门）

| # | 课程名称与官方链接 | 规模与证书 | 适用人群与核心教学内容拆解 |
|---|---|---|---|
| 01 | **Claude 101**<br>`/courses/claude-101` | 13 课 · 1 测验 · 2.5 小时 · 含徽章 | **全员起点**：第一次对话、4D 框架基础提示词、桌面端**三种工作形态区分**（Turn-by-turn 逐轮对话 / Handing work off 交办任务 / Building software 写软件）、Projects 与 Skills 复用上下文、Artifacts（设计/PPT/文档）、Connectors、Enterprise Search 与 Research。 |
| 02 | **Claude Code 101**<br>`/courses/claude-code-101` | 12 课 · 1 测验 · 1.5 小时 · 含徽章 | **终端与 IDE 编程 Agent 入门**：覆盖 Terminal / VS Code / JetBrains / Desktop / Web 五端安装；三种权限模式（manual / approval mode、auto-accept、Plan Mode）；核心日常节拍 **Explore → Plan → Code → Commit**；上下文管理三命令（`/compact`、`/clear`、`/context`）；5 节定制课（`CLAUDE.md`、Subagents、Skills、MCP、Hooks）。 |
| 03 | **Introduction to Claude Cowork**<br>`/courses/introduction-to-claude-cowork` | 14 课 · 1 测验 · 2.5 小时 · 含徽章 | **非技术知识工作者的桌面 Agent**（注：2026.09.16 起 Cowork 与 Chat 合并进统一 Claude，课程依然有效）：直接读写本地文件夹与应用；**Cowork 任务循环（写需求 → 答澄清问题 → 中途纠偏 Steer → 审交付物）**；定时任务与手机端远程查看；Standing Context（全局指令/项目/Skills/Plugins）；联动 **Claude in Chrome** 与 **Claude for Microsoft 365（Word/Excel/PPT/Outlook）**；用 Evals 验证 Skill 并分享团队插件。 |
| 04 | **Introduction to Claude Tag**<br>`/courses/introduction-to-claude-tag` | 11 课 · 1 测验 · 2.5 小时 · 含徽章 | **Slack 里的多人协作 Teammate（Beta）**：在团队频道直接 `@Claude` 派单；区分 DM / 私密频道 / 公开频道边界；**三大核心习惯**：① 像对同事一样交办整块工作；② 把工作留在业务频道（一人纠偏，全频道共享记忆）；③ 渐进放权（先给检查手段，稳定后再开免 `@` 主动回复、定时任务与持续值守）。 |
| 05 | **Claude Platform 101**<br>`/courses/claude-platform-101` | 13 课 · 1 测验 · 1.5 小时 · 含徽章 | **从聊天框到生产级 Agent 的桥梁**：第一性原理拆解 API 请求结构；按评测选模型（**Fable / Opus / Sonnet / Haiku**）；**先手写 Agent Loop（Act → Observe → Decide），懂原理后再用 SDK Tool Runner 收敛**；Extended Thinking、内置工具（Web Search / Code Execution / Web Fetch）、Skills、MCP、超 10 轮长对话上下文降本，以及 **Managed Agents（托管沙箱 Agent）**。 |

---

### 模块 B：Learn the products（高阶工程、Agent 编排与企业落地 · 共 7 门）

| # | 课程名称与官方链接 | 规模与证书 | 适用人群与核心教学内容拆解 |
|---|---|---|---|
| 06 | **Claude Code in action**<br>`/courses/claude-code-in-action` | 9 课 · 1 测验 · 1 小时 · 含徽章 | **长时无人值守（Hands-off）实战**：① **Steer**：Plan Mode 定界、定向 Compaction 保关键信息、Rewind 菜单回滚纠偏、Autonomous Goal & Loop + Git Worktrees 并行；② **Configure**：精简 `CLAUDE.md`、封装验证 Skill、Hooks 硬门禁（Permission-decision JSON + Exit Codes）；③ **Automate**：云端定时 Routines、Headless 结构化输出、PR 自动 Code Review 与 GitHub Action；④ **Verify**：「盯得越少，验收越严（verify in proportion to how little you watched）」。 |
| 07 | **Introduction to agent skills**<br>`/courses/introduction-to-agent-skills` | 6 课 · 1 小时 · 无徽章 | **把重复流程写成自动触发的 Markdown**：停止重复粘贴提示词；手写 `SKILL.md` Frontmatter（精准触发描述 + `allowed-tools` 预授权工具）；**渐进式披露（Progressive Disclosure）**组织多文件参考与免占上下文的可执行脚本；辨析 **Skills vs `CLAUDE.md` vs Subagents vs Hooks vs MCP**；通过仓库、插件、企业托管设置分发；用 Skills Validator 与 `claude --debug` 排障。 |
| 08 | **Introduction to subagents**<br>`/courses/introduction-to-subagents` | 4 课 · 45 分钟 · 无徽章 | **隔离上下文窗口的专家分身**：子代理如何开辟独立 Context Window、输入如何流入、摘要如何返回以保持主对话干净；用 `/agents` 创建代码审查或文档生成子代理；**可靠子代理三大设计模式（结构化输出格式、障碍如实上报 Obstacle Reporting、最小工具权限）**；常见反模式避坑。 |
| 09 | **Introduction to Model Context Protocol**<br>`/courses/introduction-to-model-context-protocol` | 10 课 · 1 测验 · 1 小时 · 含徽章<br>*(Skilljar 标 16 课/1 小时视频)* | **MCP 基础与三大原语控制模式**：用 Python SDK 从零搭 MCP Server 与 Client；基于控制模式（control patterns）区分三大核心原语——**Tools（暴露工具函数）**、**Resources（直接暴露数据）**、**Prompts（预定义工作流指令）**；内置 MCP Inspector 测试调试，并实战完成文档管理系统项目。 |
| 10 | **Model Context Protocol: Advanced topics**<br>`/courses/model-context-protocol-advanced-topics` | 11 课 · 1 测验 · 1.5 小时 · 含徽章<br>*(Skilljar 标 15 课/1.1h/2 测验)* | **生产级 MCP 架构**：**Sampling（让 Server 发起 LLM 请求，把 AI 推理成本卸回客户端）**；长任务 Progress & Logging 通知；**Roots 文件系统访问权限模型**；JSON-RPC 双向消息流；Stdio 本地传输 vs **StreamableHTTP 与无状态 HTTP 水平扩容权衡（何时为可扩展性取舍特性）**。 |
| 11 | **The AI-native SDLC playbook**<br>`/courses/ai-native-sdlc-playbook` | 14 课 · 1 小时 · 无徽章<br>*(配套万字博客/PDF)* | **全套课程含金量最高的工程圣经（12 个打法 Plays）**：「写代码已不再是瓶颈，瓶颈移到了代码左右两边的人类审批与交接」。把 6 大研发阶段重构成**以 Git 提交物（Committed Artifacts）驱动的闭环**：<br>① **Plan**：业务方口述生成 `intent.md`；<br>② **Design**：挂载品牌/安全/合规 Skill 一气呵成产出 `spec.md`；<br>③ **Build**：强制 Plan Mode 产出 `plan.md` → `CLAUDE.md`（不超 1 页，犯错两次必入库）→ Skills（建议性控制）+ Hooks（确定性拦截，`exit 2` 硬阻断）→ Worktrees 并行（2–3 个上限）+ Verifier 子代理；<br>④ **Test**：给 Claude 自检闭环（先写必挂测试并锁死禁止改测试文件）+ CI 连续评测（收集 20–50 个真实任务，改 `CLAUDE.md`/Skill 自动触发回归）；<br>⑤ **Deploy**：`REVIEW.md` 三轮审查（Bugs/Security/Compliance，Nit 限 5 条）+ 生产发布 Hook 门禁 + 演练单命令回滚；<br>⑥ **Maintain**：监控脚本按 **1σ（仅日志）/ 2σ（只读诊断）/ 3σ（提 PR 或触发预批回滚）** 唤醒无状态 Claude，自动写新 `intent.md` 闭合循环；配合 **Claude Security（基于 Claude Mythos 5 定时扫库）** 与 **Claude Tag** 值班。 |
| 12 | **Deploying Claude Enterprise with confidence: The five decisions that shape your rollout**<br>`/courses/deploying-claude-enterprise-with-confidence` | 14 课 · 1 测验 · 2.5 小时 · 含徽章 | **企业级落地 5 大顺序决策**（以虚构公司 Pluto 贯穿，每课固定三步：你的决定 · 可选项 · 事后反悔代价）：<br>① **Structure & Identity**（单组织还是多组织、权限组并集设计）；<br>② **Access**（各组开放哪些入口与 Connectors 三道门）；<br>③ **Governance**（Skills/Plugins/Projects 治理姿态）；<br>④ **Spend**（额度上限 Caps 与超限 4 种应对剧本）；<br>⑤ **Visibility**（成员进场前先开记录、留存策略、区分有效采用信号与虚荣指标）。 |

---

### 模块 C：Become AI fluent（人机协作心智模型与行业通识 · 共 12 门）

由 Anthropic 教育团队（Drew Bent、Maggie Vo）联合 Ringling 艺术与设计学院 **Rick Dakan 教授**、爱尔兰科克大学（UCC）**Joseph Feller 教授**（及 CodePath、Teach For America、AFT、PayPal、GivingTuesday 等合作方）共同开发，多采用 **CC BY-NC-SA 4.0** 协议开放：

| # | 课程名称与官方链接 | 规模与证书 | 核心心智模型拆解 |
|---|---|---|---|
| 13 | **AI Fluency: Framework and foundations**<br>`/courses/ai-fluency-framework-foundations` | 14 课 · 1 测验 · 4 小时 · 含徽章<br>*(视频约 1.1 小时)* | **人类侧 4D 核心能力框架**（超越“酷炫提示词”，任何模型换代都不失效）：<br>1. **Delegation（委派）**：拆解问题，决定什么交给 AI、什么判断留给自己；<br>2. **Description（描述）**：把模糊需求翻译成清晰上下文、约束与期望格式；<br>3. **Discernment（鉴别）**：批判性评估 AI 产出质量（与 Description 构成 **Inner Loop 内循环**）；<br>4. **Diligence（尽责）**：对最终交付、数据隐私、伦理与结果兜底负责（与 Delegation 构成 **Outer Loop 外循环**）。 |
| 14 | **AI capabilities and limitations**<br>`/courses/ai-capabilities-and-limitations` | 13 课 · 1 测验 · 3.5 小时 · 含徽章 | **机器侧 4 大核心属性**（与人类 4D 框架配套呼应）：<br>1. **Next Token Prediction（逐词预测）**；<br>2. **Knowledge（知识与截止边界）**；<br>3. **Working Memory（工作记忆与上下文限制 context limits）**；<br>4. **Steerability（可控性）**。<br>外加 `How AI Gets Its Character` 与 `When Properties Collide（当属性发生碰撞）`，帮学习者在遇到意外输出时分辨意外类型、定位任务在“能力—限制连续谱”上的位置并给出针对性修复。 |
| 15 | **Building effective human-agent teams (beta)**<br>`/courses/building-effective-human-agent-teams` | 5 课 · 1 测验 · 45 分钟 · 含徽章 | **从「单人模式（Single-player AI，不再只是“穿上 AI 超级战衣 donning an AI super suit”）」到「多人模式（Multiplayer AI 人机混编团队）」**：健康人机团队的**四条准则**——清晰的角色边界（Clear roles）、成文的北极星目标（Written north star）、渐进式放权（Gradual release）、恰当的信息访问权限（Right information access）。 |
| 16 | **AI Fluency for builders**<br>`/courses/ai-fluency-for-builders` | 9 课 · 1 测验 · 3 小时<br>*(Skilljar 标 10 课/1 小时视频)* | 联合 **CodePath** 开发（面向 PM/工程师/创造者）：写代码前先写 **可复用 Brief + 验收测试（Acceptance Tests）**；走通从混乱用户需求到精确指令的 **Description Chain**；用 **5 个透镜评估代码并评判 UX**（让“能跑就行 It works”不再是及格线，**你的品味 Taste 才是区分度**）；用反馈闭环决定 Ship / Fix / Stop。 |
| 17 | **AI Fluency for creative work**<br>`/courses/ai-fluency-for-creative-work` | 8 课 · 1 测验 · 5 小时 | 联合 **Rick Dakan 与 Joseph Feller** 开发（面向创作者/写作者/插画师/设计师/音乐人）：**刻意从“完全不用 AI（no AI）”出发**，提供两个分析工具——**Creative Value Lens（创意价值透镜）** 与 **Production Lens（生产透镜）**，围绕署名权、独特性与受众关系决定是否、在何处及如何引入 AI。 |
| 18 | **AI Fluency for small businesses**<br>`/courses/ai-fluency-for-small-businesses` | 8 课 · 1 测验 · 3.5 小时<br>*(Skilljar 标 9 课/0.9 小时视频)* | 联合 **PayPal、Prospect Butcher Co.、MAKS Enterprises TIPM Rebuilders** 开发：用交互式 Next-Token 模拟器理解能力边界；在供应商与账单流、研究与客户数据管理中落地 Description-Discernment 与 Delegation-Diligence 双循环；写出简短诚实的 AI 使用规范（a short, honest AI use policy）。 |
| 19 | **AI Fluency for nonprofits**<br>`/courses/ai-fluency-for-nonprofits` | 9 课 · 1 测验 · 4 小时 | 联合 **GivingTuesday** 开发：在筹款、传播、项目执行、运营与多方问责下，运用双循环安全开展 AI 研究、写作、隐私保护与数据分析。 |
| 20 | **AI Fluency for educators**<br>`/courses/ai-fluency-for-educators` | 4 课 · 1 测验 · 1.5 小时 | 联合 **Joseph Feller 与 Rick Dakan** 开发（面向高校教师与教学设计者）：将 4D 框架融入课程设计、学习成果、教学材料与作业设计（附官方公开的《How we used AI in building the course》PDF）。 |
| 21 | **Teaching AI Fluency**<br>`/courses/teaching-ai-fluency` | 7 课 · 1 测验 | 面向讲师与引导者（For facilitators）：如何在面授课堂上讲授并**评估考核（Assess）学生的 4D 能力**，结合学科专业设计作业。 |
| 22 | **AI Fluency for students**<br>`/courses/ai-fluency-for-students` | 5 课 · 1 测验 · 3 小时 | 面向学生：把 AI 当思维伙伴（Thinking partner）而非替代自身批判性思考与创造力，在学术与职业规划中保持主体性（Agency）、判断力与责任感。 |
| 23 | **AI Fluency for pK–12 educators**<br>`/courses/ai-fluency-for-k-12-educators` | 10 课 · 1 测验 · 3 小时 · 含徽章 | 联合 **Teach For America（全美 72,000+ 教育者网络）** 开发：针对基础教育教师的一线减负与教学实践。 |
| 24 | **AI Fluency for pK-12 Train the Trainer**<br>`/courses/ai-fluency-for-pk-12-train-the-trainer` | 4 课 · 45 分钟 · 无徽章 | 联合 **美国教师联合会（AFT）** 开发：给骨干教师配齐可直接开课的 Workshop 课件、引导手册与分学段练习包。 |

---

### 模块 D：Build with the API（底层 API、工具调用、评测与云厂商专班 · 共 5 门）

| # | 课程名称与官方链接 | 规模与证书 | 核心工程方法拆解 |
|---|---|---|---|
| 25 | **Building with the Claude API**<br>`/courses/building-with-the-claude-api` | 67 课 · 8 测验 · 9 小时 · 含徽章<br>*(Skilljar 标 84 课/8.1h/10 测验)* | **旗舰级全栈 API 课**：API 鉴权、基本请求、多轮对话管理、System Prompt、流式传输、结构化输出生成；提示词策略与自动化评测流水线；Function Calling、多轮工具交互、Batch Tool Calling 与内置工具（Web Search / 文件操作）；**生产级多索引 RAG（Text Chunking + Embeddings + BM25 混合检索 + Reranking + Contextual Retrieval）**；Extended Thinking、图像/视觉处理、Citations、**Prompt Caching**；MCP Server/Client 全生命周期；Claude Code & Computer Use；**自主系统三大工作流架构（Parallel execution 并行 / Operation chaining 串行链 / Conditional routing 条件路由）与调试策略**。 |
| 26 | **Tool use with the Messages API**<br>`/courses/tool-use-with-the-messages-api` | 9 课 · 1 测验 · 1.5 小时 · 含徽章 | **专治“基础工具能调通但生产环境出问题”**：以虚构工程咨询公司 Meridian 在 8 节正课里逐课修一个真实痛点——写清 Tool Description 防选错工具、开启 **Strict Tool Use** 强校验 JSON Schema、**Parallel Tool Use** 并发调工具、Streaming 提前展示工具名防前端转圈卡死、控制每次工具返回带来的输入 Token 增长、接入官方内置 Code Execution（配 Files API）、限定站点的 Web Search 与容器内 Computer Use。 |
| 27 | **Introduction to evals**<br>`/courses/introduction-to-evals` | 4 课 · 1 测验 · 1 小时 · 含徽章 | **产品经理与工程师必学的“选模算账课”**：「没有任何公开模型对比见过你的提示词（No published model comparison has seen your prompt）」。围绕虚构咨询公司 Meridian 讲透四步闭环：① 根据“答错一次代价多大”设定**准确率底线（Accuracy Floor）**；② 按 **单次完结任务成本（Cost per completed task）** 选过底线的最便宜模型；③ 从真实数据建小测试集（精确字段用代码打分，自由文本用 LLM Judge + Rubric）；④ **先对着失败用例改 Prompt，改不动再升级模型**；最后放进 GitHub Actions 做 PR 冒烟门禁。 |
| 28 | **Claude with Amazon Bedrock**<br>`/courses/claude-with-amazon-bedrock` | 65 课 · 8 测验 · 8 小时 · 含徽章<br>*(Skilljar 标 85 课/8h/10 测验)* | 原 AWS 内部员工认证培训公开版：基于 `boto3` 在 AWS Bedrock 上完整落地上述 API、自动化客观评测、Tool Use、混合 RAG、Prompt Caching、Extended Thinking、图像处理、MCP 与 Claude Code / Computer Use。 |
| 29 | **Claude on Google Cloud**<br>`/courses/claude-with-google-cloud-s-vertex-ai` | 66 课 · 9 测验 · 8.5 小时 · 含徽章<br>*(Skilljar 标 85 课/8h/10 测验)* | 基于 Google Cloud Vertex AI / Agent Platform 完整落地 Claude 全栈能力（API、评测、工具调用、混合 RAG、Extended Thinking、Citations、Prompt Caching、MCP、工作流与 Agent 架构）。 |

*(附：第一代已归档 GitHub `anthropics/courses` 的 5 门历史课为：① Anthropic API fundamentals [6 节]；② Prompt engineering interactive tutorial [9 章+附录]；③ Real world prompting [5 节：提示词回顾/医疗/提示词工程流程/通话摘要/客服机器人]；④ Prompt evaluations [9 节：Evaluations 101 + Workbench + 代码打分 + Promptfoo]；⑤ Tool use [6 节]。)*

---

## 三、跨课程提炼：Anthropic 官方真正想教的「4 大底层心智反转」

把这 29 门课放到一起看，你会发现 Anthropic 官方教学体系和市面上让人死记硬背的“提示词模板合集”截然不同。它用同一套工程逻辑贯穿了从普通知识工作者（Cowork / 4D Fluency）到工程与平台负责人（SDLC Playbook / Evals）的所有课程：

### 反转 1：从「背酷炫提示词（Cool Prompts）」到「双环人机协作（4D + 4 属性）」
- **普通人卡点**：遇到意料之外的 AI 输出（包括幻觉与知识截止边界）时，分不清属于哪一类意外，只会盲目重试提示词。
- **官方翻转**：先在《AI capabilities and limitations》建立机器的 4 大属性心智模型（逐词预测 Next Token Prediction、知识 Knowledge、工作记忆 Working Memory 与上下文限制、可控性 Steerability，以及属性碰撞 When Properties Collide），再在《AI Fluency》落地人类侧双环能力——**外环（Delegation 委派 ↔ Diligence 尽责）+ 内环（Description 描述 ↔ Discernment 鉴别）**。

### 反转 2：从「写代码是瓶颈」到「代码两头的审批与交接才是瓶颈（6 阶段交付物链）」
- **团队卡点**：AI 让写代码速度大幅加快、构建阶段被压缩到几小时，但左右两边的计划、评审/测试和部署仍按人类速度运转，导致审查队列堆积或代码未经充分审查就上线。
- **官方翻转**：重构整个研发流，**每一个阶段结束必须向版本控制提交一份交付物（Committed Artifact），下一阶段靠读取它启动（早期阶段以 `.md` 文件为主，构建起为代码与记录），整条提交链同时构成审计证据链**：
  `intent.md`（发起人原话痛点与约束）→ `spec.md`（挂载策略 Skill 自动标风险点）→ `plan.md`（Plan Mode 先审方案再动代码）→ `Diff + Tests`（先写必挂测试并用 Hook 锁死测试文件）→ `PR + Review findings`（按 `REVIEW.md` 跑 Bugs/Security/Compliance 三轮，Nit 限 5 条，人只审意图与风险）→ 生产监控 `1σ/2σ/3σ` 自动写回新 `intent.md`。

### 反转 3：从「每次在对话框重复唠叨」到「5 层定制机制各司其职」
官方在《Claude Code 101》《Claude Code in Action》《Intro to Agent Skills》中反复划清了 **5 种定制机制的边界**：
1. **`CLAUDE.md`（常驻项目记忆）**：每次会话开始必读的入职背景。**必须控制在 1 页以内**（过时内容白占上下文），只保留新成员第一天需要的构建/测试/Lint 命令、核心规范，以及**“Claude 犯过两次的错误”**。
2. **Skills（按需触发的组织制度与 SOP）**：放到 `.claude/skills/<name>/SKILL.md`，用渐进式披露（Progressive Disclosure）组织参考文件与免占上下文的执行脚本。它是**建议性控制（Advisory Control）**，让违规变得罕见（rare）。
3. **Hooks（确定性的硬护栏）**：在工具执行等动作匹配时运行确定性脚本（如 `exit 2` 硬阻断未授权生产发布、禁止在修 Bug 时修改测试文件、文件编辑后跑 Formatter/Linter）。它是**确定性控制层（Deterministic Layer）**，让违规近乎不可能（close to impossible）。
4. **Subagents（隔离上下文的专职分身）**：放到 `.claude/agents/`（如 `verifier.md`、代码精简器、代码库研究员）。在独立 Context Window 与受限工具权限下工作，只把摘要传回主会话，保持主对话干净，且让最终验证不被写代码时的假设污染。
5. **MCP（标准化的外部连接器）**：基于控制模式区分 **Tools（工具函数）**、**Resources（直接暴露数据）**、**Prompts（预定义工作流）**，进阶用 **Sampling** 让 Server 发起 LLM 请求、把 AI 成本卸回客户端。

### 反转 4：从「看公开跑分买最贵模型」到「按 $/Completed Task 与先改提示词再升模」
- **官方《Introduction to evals》明言**：*"No published model comparison has seen your prompt."*（没有任何公开排行榜见过你的提示词）。
- **标准动作**：先按“错一次赔多少钱”定准确率及格线（Accuracy Floor）→ 用自己的真实业务数据建小评测集 → 选过及格线里**单次完结任务成本最低**的模型 → **遇到不及格，先对着失败用例改 Prompt，改到极限还不行再换更贵的模型**。

---

## 四、给不同角色的最短学习路径（官方推荐 + 翡冷翠实操版）

1. **零代码职场人 / 业务骨干 / PM（想让 AI 替自己干活）**：
   - 必学 4 门：`Claude 101`（2.5h）→ `AI Fluency: Framework & Foundations`（4h）→ `AI Capabilities & Limitations`（3.5h）→ `Introduction to Claude Cowork`（2.5h）。
   - 核心收获：告别网页聊天框一问一答，学会在本地文件夹用「说清需求（Description）→ 拆成步骤（Delegation + Task Loop）→ 验收结果（Discernment + Diligence）」交办多步任务。
2. **Vibe Coder / 一线开发者 / FDE（想让 Agent 稳定跑长任务不翻车）**：
   - 必学 5 门：`Claude Code 101`（1.5h）→ `Claude Code in Action`（1h）→ `Introduction to Agent Skills`（1h）→ `Introduction to Subagents`（45m）→ `The AI-native SDLC Playbook`（1h）。
   - 核心收获：掌握 `Explore → Plan → Code → Commit`，搭好 1 页纸 `CLAUDE.md` + `SKILL.md` + `Hooks` + `verifier.md` 验收闭环。
3. **AI 产品架构师 / 全栈工程师（把 Claude 变成线上产品）**：
   - 必学 5 门：`Claude Platform 101`（1.5h）→ `Introduction to Evals`（1h）→ `Tool use with the Messages API`（1.5h）→ `Introduction to MCP` & `Advanced MCP`（2.5h）→ `Building with the Claude API`（9h）。
4. **团队负责人 / 企业 AI 推进者（带团队从单机走向多人协作）**：
   - 必学 3 门：`Building effective human-agent teams`（45m）→ `Introduction to Claude Tag`（2.5h）→ `Deploying Claude Enterprise with confidence`（2.5h）。

---

*整理自 Anthropic 官方 Claude Academy (`academy.claude.com`)、Skilljar (`anthropic.skilljar.com`) 及 GitHub (`anthropics/courses`) 2026-11-09 实时抓取档案 — 来自翡冷翠*
