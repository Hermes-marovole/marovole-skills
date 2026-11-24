# 自建 Agent 平台/桌面端：选型情报与可行性报告骨架（Build-vs-Buy for Agent Platforms）

用于回答「我们要不要自建一套桌面端 Agent / 企业内部 AI 工作台，怎么建」。这类问题的成品不是功能横评，而是**「买哪条路、要多久、花多少钱、资产归谁」**的可拍板方案。

## 1. 六款参照产品的底座事实（2026-11 核实，来源见文末）

| 产品 | 定位 | 底座架构 | 技能/记忆同步 | 该抄什么 / 该避什么 |
| :--- | :--- | :--- | :--- | :--- |
| Hermes Agent Desktop | 自进化个人/团队 Agent OS | Electron+React 壳，JSON-RPC 连本机 `hermes serve`；CLI/桌面/Webapp 共用同一会话队列与配置 | 本地 `skills/` 目录 + `skill_manage` 自写；`MEMORY.md`/`USER.md` 常驻注入 + `state.db` FTS5 | 抄：多端共享同一状态、Desktop Plugin SDK（单文件 ESM 热重载 + `/api/plugins/<id>` 后端路由）。避：后台自进化线程与主进程耦合（Issue 曾致后端崩溃） |
| Claude Desktop (Cowork 统一版) | 聊天与云端沙箱合一 | Electron 壳 + Anthropic 托管隔离 VM，空闲快照存 30 天，可挂本地文件夹/MCP | 本地目录每 ~10 分钟按 `updatedAt` 轮询组织 API 覆盖；`syncManaged:false` 保护个人技能；记忆=可编辑的 Topic 短文件 | 抄：技能静默下发 + 逃生舱、按主题可读可删的记忆、企业侧权限/审计全套。避：云端沙箱进不了本机已登录的微信/ERP 后台 |
| OpenAI Codex App | 多 Agent 并行指挥中心 | 原生客户端 + 系统级沙箱 + 内置浏览器 + SSH 远端 | 技能目录 + Git Team Config + **Record & Replay 演示录制转技能**；记忆 preview | 抄：演示录制代替写长指令、Automations 结果进 Review Queue、主动提议今日待办。避：Worktree/Branch/PR 作第一公民 |
| Paseo | 跨端多 Agent 编排 | Daemon 在主机跑，Electron + React Native 手机端都只是控制器；插件按 `client/`/`server/`/`shared/` 目录物理隔离 | 依赖底层所调 CLI 自身；Schedules（定时新建）/ Heartbeats（周期唤醒同一 Agent） | 抄：Daemon + 薄客户端的跨端形态、Heartbeats 防长任务停滞、插件前后端目录隔离。避：对非开发者暴露 worktree 概念 |
| NewMax | 本地优先白领工作台 | Electron + 本地 SQLite + 内置多身份 Chromium；**Agents 面板依赖本地 Hermes 运行时** | 三级技能加载（工作区>插件>用户级）；长期项目记忆 + **候选记忆人工复核** | 抄：一句话转长期计划（带追问向导）、四列看板 + 60s 轮询 + `mark_task_done` 强制校验产出文件、浏览器画中画与「交给 AI」、IM 群 Agent 接管台、按硬件自适应并发与文件写入锁 |
| DeepSeek Harness (`dsh`) | 万物皆插件的开源底座 | Cordis 插件树，模型适配器/工具表/会话日志/主循环皆可替换；`cordis.patch.yml` 有序叠加 | 会话存 append-only `session.vN.jsonl.zstd`，可重放；技能随 bundle/patch 分发 | 抄：**配置分层（只读基础 bundle + 薄个人 patch）**、append-only 事件流、MIT 许可当兜底内核 |

### 关键情报：白领工作台可以只是「运行时 + 壳」
NewMax 官方文档明写其 Agents 面板「兼容旧版虚拟环境及新版 Hermes 的 PM 托管环境；更新本地 Hermes 后需重启客户端」，设置页还提供一键导入 Claude Code / Codex / dsh 会话历史。**市面上体验最好的白领本地工作台，底层跑的就是 Hermes 运行时**——把研发预算全花在向导、看板、画中画和候选记忆复核上。做企业版时，这条等于官方背书：底座不必自研。

## 2. 本机已有的实证锚点（先读，别重跑）

`~/Workspace/playground/agent-fit-eval/`：

- `REPORT.md` — 7 harness × 2 开源模型 × 16 题，1,382 次有效 run。**完整需求全体 90–100%；换成一句话短需求，Hermes 77%、codex 97%、Claude Code 90%，T03 短需求档全体仅 26%。** 结论：白领真实口吻的短需求才是分水岭，产品必须前置追问把短需求补成规格。
- `docs/plans/2026-10-22-ambition-pilot-summary.md` — 技能触发消融，48 run + 96 场双盲。**A0 不装 0.48 / A1 装了不点名 0.50 / A2 显式调用 0.85（13:3）/ A3 只喊口号 0.17 且中位耗时 38s→237s、还改坏过真实数据。** 结论：把技能同步进目录等模型自动触发 = 白装；**必须在 UI 层强制绑定**。
- `memory-eval/DESIGN.md` — 记忆/技能跨会话积累的实验设计（LEARN/COLD/ORACLE、学习增益、串味率、衰减），尚未执行。

引用这些数字时说明它们来自本机评测，不是厂商 benchmark。

## 3. 三条路径的对比框架（不要只给一条）

| 维度 | A. 商业 SaaS 席位 | B. 从零自研内核 | C. 开源底座 + 自研白领壳（通常首选） |
| :--- | :--- | :--- | :--- |
| 首年软件成本 | 席位数 × 月费 × 12 | 0 | 0（底座开源） |
| 研发周期 | 1–2 周配好，但本地系统打通难 | 半年起（对照项：dsh 两万余次提交、Paseo 六千余次，作为「重写成本」的量尺） | MVP 2–3 周，全量 6–8 周 |
| 资产归属 | 锁在厂商云端 | 自有但生态脱节 | 100% 在自家仓库，可换模型迁移 |
| 致命短板 | 进不了本机登录态；断订即失能 | 重复造轮子、错过窗口 | 需自己维护壳与同步器 |

成本口径：席位数 × 官方月费 与「统一网关分流（多数杂务走低价模型、少数精品走强模型）」两条线分开算，不要合成一个含糊的「AI 预算」。

## 4. 报告的收束形状（用户要的是可拍板方案，不是调研综述）

1. 开篇 3–4 条判断，每条一句话结论 + 一句证据锚点，配 4 个数字 KPI 卡。
2. 参照系横评（上表），但行必须是**用户真实生产工序**：启动任务 → 注入上下文/技能 → 操作软件网页 → 跨天推进与通知 → 沉淀经验。
3. 用本机实测数据反驳拍脑袋假设（短需求断崖、被动装技能无效、空泛口号反向伤害）。
4. 目标架构图（壳 / 本地治理进程 / 企业同步面三层），标出每个机制抄自哪家。
5. 三条路径 TCO 总表 + 分阶段路线图（每阶段写「同事感知到的验收标准」，不写技术里程碑）+ 3 条 Do/Don't 底线。
6. 结尾给一个 24–48 小时可验证的最小动作（例如先做一个可热重载的桌面插件原型），把「要不要做」变成「先看效果」。

## 5. 企业侧必须回答的治理问题（易漏）

- **记忆三层隔离**：个人（本机，可读可删）/ 部门（审批后同步）/ 公司红线（只读强制下发）。禁止全员共写一个 memory 文件。
- **自动沉淀要过门禁**：自动提取的记忆/技能先作为「候选卡」弹给用户确认，绝不静默写共享库；提炼进程与主服务解耦，避免拖垮会话。
- **完成判定要验物**：后台任务标 done 前必须校验产出文件真实存在、非空、引用可验证，否则一律打回。

## 6. 供应商 SaaS 平台实测评测报告（「买这家」vs「自建」的交付形状）

用户拿一个商业 AI 工作台/AI 产品来问「我们要不要买」，成品不是功能横评表，而是**「哪些活交给它、哪些活绝不交给它」的岗位分派令**。默认按下面四层写，缺一层就会收到「做的不够清晰易懂，再优化一下写法」这类返工。

### 6.1 四层结构

1. **开篇一句话拍板 + 三张计数 KPI 卡**：`它胜出 N 项（全是日常快活）／两边打平 N 项／自建胜出 N 项（全是错不起的深活）`。用计数而非评分，决策者一眼看出取舍不是五五开而是泾渭分明。
2. **左右对照框替代长清单**：`✅ 放心交给它的 N 类日常快活` 与 `❌ 绝不能交给它的 N 类核心深活` 并排两栏，每条一句判词 + 一句实测证据摘述。这是全篇最被采用的一屏。
3. **分组能力总表**：`A. 日常高频办公（浅任务：求快求省心）` / `B. 专业内容与核心资产（深任务：错不起、不能泄密）` 两组分组行，每行三列「它的实测表现 / 我们的实测现状 / 谁占优」。分组行必须按**决策后果**切，不要按「输入/输出/协作」这类功能学切法。
4. **附录：真机案例逐字对照**（见 6.3）。

### 6.2 行文禁令

- **不写测试时间线**：禁止「第一轮测了什么、第二轮修正了什么」的叙事，测试过程按决策视角合并成结论；轮次只留在内部台账。
- **不写概括性评价**：`表现良好`、`能力较强`、`基本可用` 一律不算证据，每句判词后面挂一条可查的产物或原话。
- **双面性单独成栏，不要拉平成一个总评分**：同一套系统常见「问答/核查态诚实拒编，创作态大编特编」。这类反差是整份报告最有决策价值的一条，写成独立小节并给出两种用法（查资料问答安全 / 直接生稿危险），比给一个 7/10 分有用得多。
- **章节可以砍但要连着砍**：用户说「X 和 Y 不用写」时直接删，同一次编辑里重排后续章节序号（并在 SKILL.md 已列的断号自检里过一遍），不要留「一二四五六」。
- **厂商名统一**：用户指定中文名后全篇替换（含标题、KPI 卡、表格、附录、文件内的 meta 行），改完 grep 一遍英文代号残留。

### 6.3 附录：真机案例逐字对照（用户要「结果要有具体测试案例」，这就是验收条件）

5–7 个案例，每个案例一个卡片，三件套：

1. **灰底 prompt bar**：当时发给它的指令原话（可删节但保留判据）。
2. **左右并排引语栏**：`❌ 它交出的原文`（红左边框）／`✅ 我们交出的原文`（蓝/绿左边框）。两边都是**落盘产物的逐字摘录**，不是复述；差在哪靠并排自己说话。
3. **一句核验判定**：说明这段原文为什么是不能上交付的硬伤（编造病例数值、危险医疗建议、字数虚报倍数、工具调用抛底层报错），或为什么是超预期高光。

案例选择覆盖三种：① 深活翻车（含医疗/合规/事实类硬伤，这是买家最关心的）；② 幻觉或红线对抗的双探针（问答态 vs 创作态并列，制造反转）；③ 日常高光（带引用的问答、CSV 自修 bug、PPT 逐页结构、专业角色输出），证明不是一边倒的黑稿。

### 6.4 引语取证：从落盘产物和会话日志里捞，绝不凭记忆复述

- **它的原话**：查 `~/.hermes/state.db` 的 `messages` 表，按 `session_id` + `role='tool'` 取 `content`（多为 JSON，正文在 `output` 或 `content` 键里），用关键词过滤后打印命中行再摘。
- **我们的对照原文**：直接 grep 自家仓库的成稿目录（如 `books/*/07_drafts/*.md`），带文件名与行号，附录里标「第 N 行原文」。
- **产物层核验**：docx/pptx/xlsx 解包读 XML 校验页数与数字；字数虚报用脚本统计字符数，不要信对方自报的「1.8 万–2.6 万字」。
- 附录里写明「一字未改」并给出本地存档路径清单，让读者能自己打开验真；同一句话在对话里出现过一次不等于它是产物里的原文。

## 7. 来源

- Hermes Desktop 文档 https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/desktop.md
- Claude Cowork 企业统一版 https://support.claude.com/en/articles/17444462-set-up-and-manage-the-new-unified-claude-experience-for-your-enterprise-organization
- Claude 记忆 https://claude.com/resources/articles/claudes-memory-works-everywhere-and-you-decide-whats-in-it
- Cowork 技能同步逆向 https://lore.link/blog/how-cowork-implements-skills
- Codex App https://openai.com/index/introducing-the-codex-app/ ；https://openai.com/index/codex-for-almost-everything/
- Codex 录制回放 https://learn.chatgpt.com/docs/codex-manual
- Paseo https://github.com/getpaseo/paseo ；https://paseo.sh/docs/plugins ；https://paseo.sh/docs/schedules
- NewMax https://newmax.cc/docs ；/docs/features/projects ；/docs/features/im-agents ；/docs/features/browser ；/docs/features/settings
- DeepSeek Harness https://deepseek-harness.github.io/deepseek-harness/en/reference/
