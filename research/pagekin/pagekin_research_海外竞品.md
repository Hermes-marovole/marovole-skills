# 海外 AI 小说写作工具与开源替代调研笔记

> 用途：Pagekin 竞品调研（Pagekin：Electron+TypeScript 桌面应用、GPL-3.0 开源、~2.4k stars、本地优先、不绑模型：OpenAI 兼容 API + Ollama + Gemini、支持写作 Skill 导入）。
> 调研方式：基于公开网页 / 官方文档 / GitHub 仓库搜索结果（2026-11 检索）。凡未能直接从来源确证的信息一律标注「待核实」。第三方评测站的价格与功能描述可能与官方信息时点存在出入，已在冲突处注明。

---

## 1. Sudowrite

**定位**：闭源商业 SaaS（Web 应用），面向小说作者的「AI 共写」工具，主打情节衔接的句级/场景级生成与持续上下文。官方明确：所有订阅档功能相同，区别仅在 credits 额度；提供免费试用，无需绑卡。

**核心功能（长篇一致性管理机制——重点）**：
- **Story Bible（原 Story Engine）**：分层构建——Braindump（脑暴倾倒）→ Synopsis（大纲摘要）→ Character cards（最多 2000 字符/条：代词、性格、背景、外貌、对话风格等字段）→ Worldbuilding（设定、派系、魔法系统、政治结构）→ Outline/Beat。官方博客强调「每层读取上一层生成结果」，保证世界与人物从一开始就对齐。
- **持久上下文注入**：官方称 Write 功能每次生成时自动拉取「最近约 2 万词（20,000 words）的正文 + 全部 Story Bible 数据（文体、风格、大纲、人物卡、世界观）」，无需手动复制粘贴——即「常驻结构化实体卡 + 长正文回读」的混合方案。
- **Chapter Continuity**：可链接最多 25 个文档，让 AI 跨章节携带上下文（官方称之对连续性错误的第一道防线）。
- **Canvas**：可视化故事板，内置 4 套结构模板（Hero's Journey / Hollywood Beats / Story Circle / Romance Outline）。
- **First Draft**：从大纲/Story Bible 引导整本生成初稿的流程（官方博客多次提及；具体分步细节——待核实）。
- 机制小结：**以「每次生成都全量携带结构化 Story Bible + 最多 2 万词正文」对抗遗忘**，没有公开采用向量检索的证据（检索方式未公开，待核实）。

**接入的AI/模型**：自有专有模型 Muse（精调于小说文本，Muse 1.5 于 2025 年中公开）+ Ballad（第二自研小说模型）；另在 Experimental 面板提供约 20–30 个第三方模型（Claude Opus/Sonnet、GPT-4o Mini、DeepSeek、Gemini）。官方「Prose Modes」按体裁推荐模型（如言情/惊悚用 Muse、文学 fiction 用 Claude 3 Opus、动作用 DeepSeek-R1）。**不可自带 API key（待核实，未见官方 BYOK 说法）**。

**收费**：credits 计费的月订阅（年付）：Hobby & Student $10/月(225k credits)、Professional $22/月(1M)、Max $44/月(2M，credits 可滚动 12 个月)；月付分别为 $19/$29/$59。免费试用 10,000 credits（非限期，用完为止）。Hobby/Pro 的 credits 不跨月累计。第三方评测（UCStrategies 转述）称完整书稿常消耗 60 万–150 万 credits。
**平台**：Web 应用为主（待核实是否有桌面版）。
**开源状态**：闭源。

**来源**：
- 官方文档 Story Bible 概念: https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/what-is-story-bible/jmWepHcQdJetNrE991fjJC
- 官方文档 Characters: https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/characters/a7tdE1ZB8KvAwMD3Mopwpd
- 官方博客 Story Bible 机制: https://sudowrite.com/blog/story-bible-template
- 官方博客：产品工作原理: https://sudowrite.com/blog/how-sudowrite-works
- 官方博客模型切换: https://sudowrite.com/blog/sudowrite-prose-modes-explained
- 第三方定价对比: https://www.authorflows.com/blogs/authorflows-vs-sudowrite ；https://bloggingwizard.com/sudowrite-review ；https://nerdynav.com/sudowrite-review

---

## 2. NovelAI

**定位**：闭源商业订阅制 Web 服务，主打「文本生成（自家模型）+ 图像生成 + TTS」的一体化创作娱乐平台，社区偏互动同人/日式轻小说向。

**核心功能（长篇一致性管理机制——重点）**：
- **Lorebook（世界书）**：关键词触发式实体注入。每条 entry 含 Activation Keys（大小写不敏感匹配；另支持以 `/…/` 包裹的 regex key，可用 i/s/m/u flags）、触发时插入上下文的 Entry Text、Token Budget（0–1 之间的纯小数按「占比最大上下文」解释）、Insertion Order（值越高越优先占 token）、Prefix/Suffix 等。文档另有 **cascading activation**（entry 之间级联）、Delay/Duration 与 ephemeral context 等进阶设定【以上来自 docs.novelai.net 的 lorebook / advancedsettings 文档】。
- **Memory / Author's Note**：Memory 默认置于上下文最顶端，存放「当前设定、主角、同伴与之前剧情」的简报；Author's Note 默认插入上下文末端（最近正文之前），作为强提示层，需人工频繁更新。等价于「常驻摘要层 + 近端提示层」。
- **Context Viewer**：可逐 Stages 查看每次实际发送给模型上下文的组装（Memory/AN/Lorebook/正文分段、Insertion Order、被裁剪原因），是少有的透明化机制。
- 机制小结：**关键词触发式实体卡（Lorebook）+ 手工维护的常驻 Memory/AN 双层 + 显式 token 预算控制**；不内置向量检索（检索方式未公开，待核实）。

**接入的AI/模型**：多档自研模型：Kayra(13B)、Clio(3B)、Krake 等模型，以及 Erato、Xialong（新档独占/staff storyteller 是否为 Opus 独占——待核实）。模型上下文：Clio/Kayra 为 8192 tokens；订阅档影响可用模型与上下文（Opus 档位最高 28,672 tokens）。**不支持自带模型**（服务自带，按订阅解锁；BYO 模型未公开支持）。
**收费**：Paper 免费试用（50 次文本 + 30 次图像 + 100 次 TTS，一次性）；Tablet $10/月（无限文本生成，上下文较小）；Scroll $15/月（更大 token memory）；Opus $25/月（最大 context 28,672 tokens + 无限额小尺寸图像生成）。图像生成消耗 Anlas（Opus 内多数图像免费）。
**平台**：Web（移动端浏览器可写；无原生桌面版——待核实）。
**开源状态**：闭源（模型权重/架构不公开，社区 API 文档与第三方接入存在）。

**来源**：
- 官方订阅页: https://docs.novelai.net/en/subscription
- Lorebook 官方文档: https://docs.novelai.net/en/text/lorebook
- Story Settings（Memory/AN）: https://docs.novelai.net/en/text/editor/storysettings
- Context/Token Budget 文档: https://docs.novelai.net/en/text/editor/advancedsettings
- 模型页: https://docs.novelai.net/en/text/models
- 第三方评述对比: https://dreamgen.com/blog/articles/novelai-review ；https://blog.chapter.pub/novelai-pricing

---

## 3. Novelcrafter

**定位**：闭源商业 Web 应用，主打「结构化大纲 + 世界观 Codex + BYOK AI」体裁，不绑模型；用户自带 OpenAI/Anthropic/OpenRouter/本地 LLM API key。

**核心功能（长篇一致性管理机制——重点）**：
- **Codex（实体库）**：人物/地点/物品/组织的 wiki 式页面，带 Relations（实体间关联）与类型；同一套实体既能手动维护也可让 AI 生成/提取（Hobbyist 档有 AI Scene Summarization、AI Character extraction）。
- **Tracking（提及检测）机制**：每个 Codex entry 可设置——Always include（常驻上下文，旧称 global entry）/ Include when detected（默认：当正文或 beat/chat 消息中出现名称或别名时注入）/ Don't include when detected / Never include。名称匹配默认大小写不敏感，可选 case-sensitive、exclusion exclusion list。**Detected即高亮 + 项目 heatmap 统计提及密度**。
- **Codex 注入流程（官方 FAQ）**：①当前 beat/chat 消息与 beat 之前正文中的所有提及 → ②手动 added 到 scene 的条目 → ③POV 条目 → ④全局条目 → ⑤关联（子）条目 → ⑥过滤空条目，再按 global → 类型 → 名称排序注入 prompt，并避免重复。可见核心是 **mention-detection 实体自动注入 + 全局/POV 常驻 + 关系扩展**。
- **Scene 级上下文**：可手动给场景挂特定 Codex entries（ Yan 忽略大量条目时会提醒太杂——官方 troubleshooting 明确指出「Too many Codex entries attached → AI 过载」）。
- 机制小结：**提及检测自动注入 + 分档 tracking 规则（always/detected/never）+ 关系级联**。未见内置 RAG/向量检索（待核实）。

**接入的AI/模型**：严格 BYOK（OpenAI、Anthropic、OpenRouter、Mistral、本地 LLM 等 300+ 模型）。
**收费**：四档订阅（年付省 2 个月）：Scribe $4/月（无 AI，仅组织与基础 review）、Hobbyist $8/月（BYOK AI、场景摘要、人物提取、beat 生成）、Artisan $14/月（+工作坊 Workshop Chat、高级 Review）、Specialist $20/月（+协作/团队）。21 天全功能试用。
**平台**：Web 应用（官方未提供桌面版——待核实）。
**开源状态**：闭源。

**来源**：
- Codex 介绍: https://www.novelcrafter.com/features/codex
- 定价页: https://www.novelcrafter.com/pricing
- Codex Tracking（含 AI Context 三档）: https://www.novelcrafter.com/help/docs/codex/codex-tracking
- Codex entry 解剖: https://www.novelcrafter.com/help/docs/codex/anatomy-codex-entry
- context 组装 FAQ: https://www.novelcrafter.com/help/faq/ai-and-prompting/codex-context-in-prompting
- Scene 上下文教程: https://www.novelcrafter.com/courses/codex-cookbook/codex-scenes
- 第三方定价分析: https://checkthat.ai/brands/novelcrafter/pricing

---

## 4. SillyTavern（社区向）

**定位**：**开源**（AGPL-3.0，仓库 https://github.com/SillyTavern/SillyTavern 、社区活跃度极高、stars 数量级待核实）本地 Web 前端，面向角色扮演/互动小说社区，本质是「对各种 LLM API 的统一宿主 + 角色卡与世界观管理」，不内置小说工作流，但沉淀了 lorebook/World Info 的事实标准词汇与机制。

**核心功能（长篇一致性管理机制——重点）**：
- **World Info / Lorebook**：条目按 activation keys 触发插入 prompt。关键参数：**扫描深度 scan depth**（回看最近 N 条消息）、**预算 Context %**（默认全部上下文方面的 **25%**，invoice 预算用尽后「即使 keys 命中也不再激活」且默认无警告）、whole-word 匹配、**递归激活（recursion）**（条目内关键词可再触发其他条目）、**多插入位置 insertion strategy**（含系统提示前后与 context 深度处，深度可自定义——社区存在「更多深度档位」的 feature request）、触发概率 trigger %、速度限制 cooldown、delay、inclusion groups（互斥组）等。
- **Vector Storage（向量存储）**：近年将关键词匹配扩展到语义命中——用向量相似度在 lorebook 中检索候选，再按原有预算/过滤逻辑插入（官方 doc 明确此为对 keyword 检查的替换，其余预算仍生效）。这是**社区产品中少见的「keyword + embedding」双通道实体触发机制**。
- **Character Cards V2/V3**：角色卡（含嵌入 lorebook）是社区生态的核心数据格式，可导入导出、与其他角色隐式互联。大量周边工具（如 SillyTavern-Card-To-Lorebook）把角色卡拆为模块化 lorebook sub-entries（外貌/奇癖/背景/关系各设独立 keys、order、constant flag）。
- 机制小结：**关键词驱动 + token 预算（25% 默认）+ 递归 + 向量存储语义命中兜底**。技术上最「引擎化」的实体注入系统之一。

**接入的AI/模型**：纯 BYO（OpenAI/Claude/Gemini/OpenRouter/Ollama/本地代理/云端 NovelAI 等 API 都可接）。
**收费**：免费。
**平台**：本地运行（Windows/macOS/Linux 自部署；使用 Node.js 服务器）。
**开源状态**：开源（AGPL-3.0，待核实最新 license 细节与版本号）。

**来源**：
- World Info（budget、Vector Storage）: https://docs.sillytavern.app/usage/core-concepts/worldinfo
- 第三方机制深拆 (25% budget、scan depth 等，源自 source code 1.19.0): https://arcanumrpgs.com/blog/sillytavern-lorebook
- 插入顺序：https://www.memorylake.ai/en/blogs/sillytavern-world-info-insertion-order
- 卡转 lorebook 社区工具: https://github.com/ets1odoo-beep/SillyTavern-Card-To-Lorebook

---

## 5. Plottr

**定位**：闭源商业订阅 SaaS（Web + Windows/Mac 桌面端），**明确「无 AI」**的视觉大纲/系列圣经（series bible）软件。卖点为「#1 visual book outlining and series bible software」，40,000+ 用户。

**核心功能**：
- 可视化时间线（Timeline）+ 场景卡（Scene Cards，跟踪角色/地点/细节）+ Scene Stacks（章节内索引卡片式叠放）；
- **Series View**：可在系级与书级分别建立时间线；Unlimited Books；自动从时间线生成可导出大纲；
- **人物/地点追踪**：character 与 place 详情卡；**角色弧光层（character arc layers）** 作为独立的观测层（YouTube 教程演示 Save the Cat 结构层、角色弧层、副线层并列打谱）；
- 模板库：Hero's Journey、Save the Cat 等约 30 种结构框架；导出 Word/Scrivener，导入 Scrivener 项目。
- 机制小结：**无 AI 的一致性管理——完全靠人工维护的实体卡/时间线/系列视图**。官方明确 Pro 档列出「No AI 🎉」作为卖点（隐私/无 token 订阅的定位）。

**接入的AI/模型**：无。
**收费**：Classic $60/年 或 $199 终身；Pro $99/年（官网价）或 $9.99/月（官网同期显示 $14.99/月于 Community 档）；Pro + Community $129/年 或 $14.99/月。**价格两说：Kindlepreneur（2025-12 更新）记为 Pro $150/年**，官方 pricing 页与 AuthorFlows 亦有差异——待核实最新官方价。30 天全功能试用。
**平台**：Windows/Mac 桌面 + 浏览器（平板可用），云同步/云备份/实时协作在 Pro。
**开源状态**：闭源。

**来源**：
- 官方定价: https://plottr.com/pricing
- 官方功能页: https://plottr.com/features
- Kindlepreneur 评测（价格两说处）: https://kindlepreneur.com/plottr-review
- 第三方补评: https://www.authorflows.com/blogs/plottr-pricing

---

## 6. Atticus（以及「First Draft 类」）

**定位**：闭源商业的一次性买断软件，**非 AI 工具**——「写作编辑器 + 一键排版出书」二合一（ePub 与 KDP 打印 PDF），对标 Vellum（macOS-only, $249）。撰写端只是常规编辑器（含 Version control、front/back matter、面板预览、不同设备预览等）。

**核心功能**：
- 写作编辑器（章节、过滤器、模板、黑暗模式等）+ 全专业产出（EPUB/打印 PDF/多个版本）；
- **无 character/worldbuilding/beat 管理，无 AI 机制**（一致性管理不在此类工具的领域内）。跨平台是它与 Vellum 的核心差异。
- 「Atticus/First Draft 类」中的 **First Draft**：Sudowrite 有同名功能（见第 1 节）。若指独立软件「First Draft」则未检索到可靠海外知名同类工具——**待核实**。
- 机制小结：**不解决 AI 一致性问题**，但它划了「写作/排版工具」与「AI 内容生成」的边界——纯 B 端一次性买断的市场证据。

**接入的AI/模型**：无。
**收费**：$147 一次性买断（含终身更新），无试用，30 天退款保证。
**平台**：Windows/Mac/Linux/Chromebook + 网页端（Live、iOS/Android 待核实）。
**开源状态**：闭源。

**来源**：
- 官网: https://www.atticus.io
- 第三方评测与对比: https://bookbird.io/software/atticus ；https://kindlepreneur.com/atticus-review ；https://loreteller.com/learn/atticus-vs-vellum ；https://reedsy.com/studio/resources/atticus-review

---

## 7. Obsidian 生态（笔记软件路线，明确做长篇/世界观的插件）

Obsidian 插件开源为姊妹形态的 OSS 对标面。总体特征：**免费插件 + BYO API key + 数据留在本地 vault（Markdown 文件）**；一致性机制靠 Codex/lorebook 式结构化笔记，AI 侧靠外接模型。

### 7.1 Longform（结构不 AI）
- 开源（MIT，https://github.com/kevboh/longform ），把多场景笔记组织为有序手稿，含字数与你自己的 session goal、编译出版；单场景项目也支持。**无 AI**；
- 来源: https://github.com/kevboh/longform ；https://www.obsidianstats.com/tags/writing

### 7.2 Inkswell（Codex 世界圣经，无 AI）
- 开源（MIT），单一 host view 集成 Home/Plan/Write/Revise/Publish + **Codex** + Track；Codex 描述为 **story bible（人物、地点、世界、派系、物品、事件、概念）+ scene linking + mention 自动检测**；beat-sheet 模板、Kanban、revision audits；**明确了 no AI、no network calls、全本地**；
- 来源: https://community.obsidian.md/plugins/inkswell

### 7.3 InkPilot 墨航（AI 协作小说插件，中英双语社区作品）
- 开源（MIT），面向网文作者，全流程：「项目规划、人物设定、大纲生成 → 章节写作/流式 → **一致性审查（consistency review）**」，用 OpenAI/Anthropic/兼容 API，理念「AI 80% + Human 20%」、token 成本统计；是中文社区里最接近 Pagekin 定位的 Obsidian 对标物；
- 来源: https://community.obsidian.md/plugins/inkpilot

### 7.4 StoryLine / Fiction-canonical（《Severin》系等）
- StoryLine：官方社区 repo 插件，把 vault 变成 book planning tool（scenes、characters、locations、plotlines、progress），后期把角色与地点合并进 **Codex Hub**（支持自定义类别）；
- 来源: https://forum.obsidian.md/t/plugin-storyline-obsidian-plugin-for-writers/111494
- 还检索到 Medium 评述中呈报的一个非常丰富 storyteller 插件（Codex 人物属性/POV 百分比统计/地点层级/自定义类别），具体名称以 Medium 文介绍（作者未给 repo 名，待核实）：https://medium.com/@animalcrackerart/an-amazing-fiction-planning-plugin-for-obsidian-89133a07b969

### 7.5 AI 通用插件（非小说专用但机制可参考）
- **Smart Connections**（开源，local embedding 模型、零配置、无 API key 做语义检索侧栏；补 recomposition 的核心是「写时应背景恢复相关笔记」）；Copilot for Obsidian（前端开源、托管的 Plus 功能闭源；BYO/OpenAI 兼容本地服务器/Ollama 都可，RAG 式 Vault QA）；Text Generator（模板驱动）。三者皆非小说专用，但完整覆盖了「RAG/召回 + BYO 模型」这套机制在 Obsidian 的形态。
- 机制小结：**Obsidian 生态里 AI 长篇一致性方法有两类——artificial 结构化 Codex（人工维护 + mention 检测）与 embedding 召回（Smart Connections 类），但两套机制通常不合一**；未见把 novel-lore 做成专有 RAG 的成熟插件。
- 来源: https://github.com/brianpetro/obsidian-smart-connections ；https://community.obsidian.md/plugins/copilot ；https://wetheflywheel.com/en/radar/obsidian-ai-plugins ；https://smartconnections.app/obsidian-copilot

---

## 8. 思源笔记（SiYuan）AI 插件

- **siyuan-plugin-copilot**（开源）：基于思源的 AI 问答/编辑，ask 模式（多模型并行作答、拖拽块/文档发送）+ **agent 模式（AI 自主查询/编辑笔记、创建文档）**；内置 OpenAI/Gemini/DeepSeek/火山并支持任意 OpenAI 兼容 API；可保存多种预设（论文场景/博客/代码切换）。**不是小说专用工具**，但代表「思源类工具的 AI 插件形态」（本地笔记 + agent + BYOK）。纪检细节：思源官方热门 issue#17797 也在讨论原生 AI agent；第三方 agent UI 较多但不如专用工作流。长篇 lore 管理与 RAG 层面无成熟方案——待核实。
- 来源: https://github.com/Achuan-2/siyuan-plugin-copilot ；https://github.com/siyuan-note/siyuan/issues/17797

---

## 9. GitHub 上的其他开源同类（长篇 AI 写作，多数中文社区产品）

以下为检索中确认的、与 Pagekin 同形态（本地优先 + BYO/本地模型 + 长篇一致性管理）的开源项目，可作为机制参考或描述为「开源替代面」：

1. **AI Novel Writer**（ai-tldr.dev 收录）：本地优先桌面 AI 长篇工作台，Premise→人物→世界观→章节蓝图→草稿→审校→修订全流程；中文+英双语、TypeScript、GPL-3.0、GitHub ~2.3k stars、桌面安装器分发；模型由用户提供（Ollama 或云端 API key）。**（注：与 Pagekin 的公开描述高度近似，第三方列表很可能即指向 Pagekin 或其同类，待核实是否同一项目。）**
   - 来源: https://ai-tldr.dev/tools/ai-novel-writer
2. **ExplosiveCoderflome/AI-Novel-Writing-Assistant**（开源、中文）：AI Native 长篇系统，含 Agent「自动导演」、世界观写法引擎、**RAG 知识库检索（可选启用）**、卷纲/章节任务/场景结构、世界地图/角色关系图、反 AI 味写作规则与拆书工作台。Windows 桌面版 + 源码运行。
   - 来源: https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant
3. **KazKozDev/NovelGenerator**（155★，TypeScript，本地）: 章节式连贯长篇生成器：**causal planning（因果规划）、persistent story memory（持续故事记忆）、scene handoffs（场景交接）、continuity checks（连续性检查）**，Gemini API + Ollama。
   - 来源: https://github.com/KazKozDev/NovelGenerator
4. **Xiaoyangy/novel-studio**（152★，Go）：开源本地优先 AI 长篇引擎——**多智能体世界推演、按弧规划、RAG 长程记忆（Qdrant）、逐章审核与断点恢复**，OpenAI 兼容。
   - 来源: https://github.com/topics/creative-writing-ai?l=go&o=asc&s=stars （topic 页内 manifest）、repo 见 topic 页：Xiaoyangy / novel-studio
5. **SongFengYunHe/inkwell**：本地优先的 AI 长篇小说生产工作台（TypeScript + Electron）。仅获 topic 页述与，详细功能 GitHub 读取受阻——**待核实**。
   - 来源: https://github.com/topics/ai-novel-writing
6. **StoryMemory-Studio / quillgon / Writer-AI-studio** 等：本地优先长篇工作台/智能体流水线的同topic 项目（结构化故事记忆、consistency check、审校修订链路）。细节未逐一核实——**待核实**。
   - 来源: https://github.com/topics/ai-novel-writing
7. **中国网的 AI 长篇「事实层」写作插件**（GitHub topic: ai-novel）：zy-zmc/tianming-novel-ai-writer 与 tianyan（「15维事实快照 · 变更声明 · 生成门禁 | 写到3000章依然连贯，不依赖上下文，不靠模型记忆，靠每章状态回写」）以及 hoobnn/novel-harness（Claude Code 多智能体：时间线、人物状态、伏笔由独立事实层记录并校验）。机制独特：**不靠 RAG 靠状态回写的显式事实库**。
   - 来源: https://github.com/topics/ai-novel?o=asc&s=stars

---

## 10. 「长篇一致性管理机制」横向对比（核心结论）

| 工具 | 实体承载形式 | 注入策略 | 摘要/记忆层 | 检索方式 | 一致性校验 |
| --- | --- | --- | --- | --- | --- |
| Sudowrite | Story Bible 分层字符窗（含大纲/人物/世界观/风格） | 每次生成全量携带（约 + 2万词正文窗口） | 无（依赖 prompt 内正文窗口与 Chapter Continuity 跨文件） | 无向量证据（待核实） | 无显式校验，靠生成时对齐 |
| NovelAI | Lorebook 词条（key 触发、token 预算、插入序） | keyword 触发 + 递归 + 级联 | Memory（顶端常驻）+ Author's Note（近端） | 无向量证据 | Context Viewer 手工审计 |
| Novelcrafter | Codex wiki 实体 + 关系图 | 三档 tracking（always/detected/never）+ mention 检测 + POV + 关系级联 | AI Scene Summarization | 无向量证据 | Advanced Review（Artisan+，官方标 planned） |
| SillyTavern | World Info / lorebook + character card | keyword 触发（25% 预算、scan depth、递归、插入位置深度）+ Vector Storage 语义候补 | chat 记忆/摘要扩展（社区方法） | keyword + **embedding**（Vector Storage，双通道） | 无显式校验（社区延伸实践） |
| Plottr | 人物/地点卡 + Series bible | 无 AI | 无（人工） | 无 | 人工对齐 |
| Atticus | 无 | 无 | 无 | 无 | 无（纯写作排版） |
| Obsidian 插件群 | Codex story bible（Markdown/YAML 笔记） | mention 检测（Inkswell）/AI 全流程（InkPilot）/无 AI 结构（Longform） | 主动 RAG/Vault QA（Copilot 等） | embedding 召回（Smart Connections） | InkPilot 提供一致性审查流水线 |
| OSS 同类（NovelGenerator / novel-studio / AI-Novel-Writing-Assistant 等） | 结构化故事记忆/事实层 | 显式 handoff / 章节 inject | RAG（novel-studio 用 Qdrant、可选知识库） | RAG/向量库 | continuity check / 逐章审核 / 生成门禁 |

**机制分型总结**：
1. **「实体卡 + 全量带入」型**（Sudowrite）：不解释复杂检索，直接把结构化 Bible 与长窗口正文每次都送入；token 成本高但心智负担最低。
2. **「关键词触发 + 预算」型**（NovelAI Lorebook / Novelcrafter Codex / SillyTavern World Info 主线）：mention/keyword 决定注入，token 预算控制总量，插入序决定优先级——这是整个 lorebook 生态的共同祖先；NovelAI 与 SillyTavern 向社区奉献了机制原型。
3. **「关键词 + 语义双通道」型**（SillyTavern Vector Storage、Smart Connections、AI-Novel-Writing-Assistant、novel-studio）：embedding 召回兜底 keyword 的漏触发，但**在长篇正文 OOC/连续性错误上仍是主要盲区**（激活的实体不等于蓝线对齐）。
4. **「事实层状态回写」型**（tianming/tianyan/novel-harness 类、NovelGenerator continuity checks）：不依赖模型记忆或检索，靠每章生成后回写结构化事实并校验下章生成——在超长篇（3000 章）场景被验证的中文社区流派。
5. **主动「无 AI」**（Plottr / Inkswell-非AI模式 / Atticus）：一致性由人工维护的结构模板保证——它们是 AI 严重 OOC 市场定位的反面参照，而非竞品。

---

*报告完。检索时间：2026-11。标注「待核实」处均为本次未能从可靠来源交叉佐证的信息。*
