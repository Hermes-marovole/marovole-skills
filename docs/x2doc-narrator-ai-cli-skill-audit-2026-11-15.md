# Narrator AI CLI Skill 深度审计与工程机制拆解（@chenfacai0） - X2Doc 整理

> 来源：https://x.com/chenfacai0/status/2121704975642333515
> 作者：@chenfacai0（陈发财）
> 原帖时间：2026-11-14 20:41:00 UTC（抓取时 1,435 浏览、23 赞、27 收藏、5 转发）
> 关联开源仓库：
> - Skill 仓：`NarratorAI-Studio/narrator-ai-cli-skill`（commit `4b17c6f2175bd532c92db778a847f8fb6bdd3177`，★ 3,249，432 Forks，MIT）
> - CLI 仓：`NarratorAI-Studio/narrator-ai-cli`（commit `2d8bb1463058fb36f267f205994dca38b32f037d`，★ 148，28 Forks，MIT）
> 整理时间：2026-11-15
> 来自翡冷翠

---

## TL;DR

- **一句话定性**：原帖吹嘘“塞进 Claude Code 甩一句话全包、想批量起影视号人工成本几乎压到零”，但浅克隆两个仓库源码与内部运营文档（`docs/batch-processing.md`、`docs/sales-playbook.md`、`docs/finops.md`）对账后发现——**它根本不是本地开源视频生成引擎，而是闭源商业 API（`https://openapi.jieshuo.cn`，AI 解说大师）的薄壳 HTTP 客户端 + 提示词说明书**，必须加微信/发邮件（`merlinyang@gridltd.com`）充值购买点数才能跑。
- **内部运维文档自曝「人工核对」真相**：在 `narrator-ai-cli` 仓库被自动同步进来的内部文档里，官方白纸黑字写着：**① 单批默认上限 5 个视频，真实瓶颈是“测试人员（`@ShawYu19`）单批人工核对工时随数量线性上升”（`batch-processing.md`）；② 销售话术核心是“强调人工质保的服务（不强调 AI 商品），当抖音驳回『AI 一键生成』时主张产品本质是人工质保服务交付”（`sales-playbook.md` & `faq-troubleshooting.md`）**。
- **数量三处对账打架**：内置电影素材数量在原帖与 CLI `README_CN.md` 写 **93 部**，Skill 仓 `README_CN.md` 写 **约 100 部**，而 `references/resources.md` 的 JSON 响应示例写 **`"total": 101`**。
- **真正值得我们白嫖学习的 2 个硬核工程宝藏**（不装它的 CLI、不做影视号，只借它的 Agent 工程规范）：
  1. **防 Agent 失控的 `SKILL.md` 编写范式**：防 zsh `$status` 只读变量死循环、区分顶层 `.status` 与嵌套状态码、严禁一步问两个正交决策（Path vs `target_mode`）、不可逆计费动作（30 点/分钟）提交前强制打印完整 JSON 让人确认。
  2. **仓库内意外开源的 668 行企业级《GridLtd Organization Rules》（`AGENTS.md` / `org-rules.md`）**：一整套多组织（DevOps / BizDev / ProductDev / SecOps / PMO）管理 Coding Agent 的生产级宪章——含 Issue 模板底部的强制 `### Agent Execution Prompt` 六要素、PR 的 `## Agent Exposure Block`（暴露理解偏差与剩余风险）、9 类 GitHub Actions 工作流权限分层、跨仓 Issue 迁移完整溯源链，以及新产品上线前的“4 项命名红线审查（ADR-014）”。

---

## 一、原帖核心内容与宣称清单

**原帖正文（@chenfacai0）**：
> 发现一哥们儿光靠电影解说，一年就赚了一百万；可这会儿要是把这背后的门道透给他，他估计得整宿合不上眼。
> 有个开源项目叫 `narrator-ai-cli-skill`，塞进 Claude Code 这类 Agent 里，你只管甩一句“帮我做《喜羊羊与灰太狼》解说视频”，AI 就能把整摊子活儿一个人全包了：
> 1️⃣ 解说脚本自己就码出来了
> 2️⃣ 电影片段对得丝毫不差
> 3️⃣ 63 种音色随便选，声音克隆照样玩得转
> 4️⃣ 90+ 种视觉模板自动往上套
> 5️⃣ 146 首 BGM 智能挑着配
> 6️⃣ 成片直接送到手上
> 自带 93 部经典电影素材库，花销还能提前给你算得明明白白，工程化这一块整得相当硬核。
> 想批量起影视号的，人工成本几乎能压到零。
> 🔗 https://github.com/NarratorAI-Studio/narrator-ai-cli-skill

**原帖配图转录**：
配图为 `NarratorAI-Studio/narrator-ai-cli-skill` 的 `README.md` 英文页经浏览器机器翻译成繁体中文的截图（把 `Pegasus`《飞驰人生》翻成了英文，把 `CLI` 翻成“命令列工具 / 廚房用具”，`Skill` 翻成“一本食譜”）。

---

## 二、源码与内部文档四方对账表（营销话术 vs 仓库真相）

我们对 `NarratorAI-Studio` 组织下的 4 个公开仓库（`narrator-ai-cli-skill` ★3,249、`narrator-ai-cli` ★148、`narrator-ai-web` ★0、`narrator-ai-web-backend` ★0）进行了浅克隆与源码级审查，发现 `narrator-ai-cli/docs/` 目录下同步了大量该公司（GridLtd）内部的飞书运营手册：

| 审计维度 | 原帖 / README 营销话术 | 仓库源码與 `docs/` 内部文档真相 | 证据出处（精确到文件与行号） |
|---|---|---|---|
| **工具本质** | 开源项目，塞进 Agent 就能把整摊子活全包 | **纯闭源 SaaS 的薄壳客户端**：`narrator-ai-cli-skill` 只有 Markdown，0 行代码；`narrator-ai-cli` 只是用 `httpx` 把请求发往 `https://openapi.jieshuo.cn`，无任何本地剪辑/TTS/视觉算法 | `narrator-ai-cli/src/narrator_ai/config.py:15`、`client.py:23` |
| **获取与计费门槛** | “花销提前算得明明白白” | 必须发邮件至 `merlinyang@gridltd.com` 或加客服微信 `gezimufeng` 获取私有 `NARRATOR_APP_KEY` 充值点数：纯解说文案 `flash` 5 点/千字、`pro` 15 点/千字；原声混剪文案 `flash` 12 点/千字、`pro` 40 点/千字；`magic-video` 视觉模板 **30 点/分钟** | `SKILL.md:78,191`、`references/operations.md:205` |
| **“人工成本压到零” vs 真实履约** | “想批量起影视号的，人工成本几乎能压到零” | 内部 FinOps 与批量手册明确写着：**物料成本拆分为 4 类，第 4 类就是「人工核对工时（测试人员人天）」**；**单批默认上限 5 个视频**，因为“测试人员 (`@ShawYu19`) 单批审核工时随数量线性上升，>5 个会跑出 SLA” | `narrator-ai-cli/docs/finops.md:9,18`、`docs/batch-processing.md:9-20` |
| **对外合规口径** | “AI 一句话全自动生成” | 内部《销售作战手册》与《FAQ》规定：**“强调人工质保的服务（不强调 AI 商品）”**；当抖音上架因“AI 一键生成”被驳回时，标准话术是**“我们的产品本质是『人工质保的服务交付』，AI 是内部工具”** | `narrator-ai-cli/docs/sales-playbook.md:56`、`docs/faq-troubleshooting.md:53-54` |
| **“一句话全自动” vs 交互门禁** | “你只管甩一句……AI 一个人全包了” | `SKILL.md` 第 71 行强制规定 **`Confirm before acting. Every resource (source, BGM, dubbing, template) and every magic-video submission requires explicit user approval. Never auto-select, never auto-submit.`** —— 选片、选路径、选模式、选 BGM、选配音、选模板必须分回合逐一问用户确认，严禁一键全自动提交 | `narrator-ai-cli-skill/SKILL.md:70-71,121-132,176` |
| **内置电影数量三处打架** | 原帖写 **93 部** | ① CLI `README_CN.md` 写 **93 部**；② Skill `README_CN.md` 写 **约 100 部**；③ `references/resources.md` 的 JSON 实测返回示例写 **`"total": 101`** | `README_CN.md:96` vs `SKILL.md:104` vs `references/resources.md:24` |
| **二创版权红线** | “随便选片批量起影视号” | 内部《进阶用户技巧》第 6 节警告：**抖音二创授权片单白名单仅限 5 家（优酷/爱奇艺/腾讯视频/芒果/搜狐），其他片源未授权使用属高风险**，且客户上传素材的版权/肖像权完全由客户自负 | `narrator-ai-cli/docs/advanced-tips.md:49-53`、`docs/faq-troubleshooting.md:56-57` |

---

## 三、对我们现有产线的取舍（为什么不装它，但要借它的工程设计）

### 1. 赛道与栈取舍：明确不装 CLI、不碰影视解说号
- **赛道冲突**：我们的个人 IP 主轴是「AI + 科技 + 财富（12 年 PM + 一线 FDE 视角）」，公司号是「灵知 AI 家庭精准营养」，变现漏斗是 `开源 Skill → 付费社群 → FDE 内训咨询`。泛娱乐影视解说号既面临严苛的版权白名单限制，受众也与我们的高客单 B/C 端漏斗零交集（属于典型**“借工程机制，绝不借赛道”**）。
- **技术栈不兼容**：我们自己的短视频管线（`video-common` + `xilo-opus-video` + `stickman-omni-flash-pipeline` + 本机 `ffmpeg` / `Playwright` / `VoxCPM` / `ElevenLabs`）是 **100% 本地可控、纯函数确定性渲染、带 LUFS 与画面残差门禁**的自主产线；而 `narrator-ai-cli` 是把任务黑盒提交给外部收费 API（`openapi.jieshuo.cn`），不仅要按字数/分钟买点数，连后端 `search-movie` 都是调一个响应要 60 秒以上的 Gradio 接口（报错码 `40000 Gradio timeout`）。因此**本机不安装、不集成该 CLI**。

### 2. 真正值得吸收的两大工程宝藏（这才是高价值增量）

虽然不买它的影视解说 SaaS，但这家公司（GridLtd）在 **“怎么把一个多步骤异步 API 写成零翻车的 Agent Skill”** 以及 **“怎么用 GitHub 组织级规范管住一群 Coding Agent 和业务团队”** 上，做得非常扎实：

#### 宝藏 A：`narrator-ai-cli-skill` 里的 5 条防御性 Skill 编写设计（可直接反哺我们的 `skill-authoring`）
1. **将决策树按依赖层级强制拆成单回合提问（Anti-bundling Rule）**：
   - 很多粗糙的 Skill 会让 Agent 一上来同时问用户“① 选快速路线还是标准路线？② 选纯解说还是原声混剪？”。
   - 该 Skill 明确写出 **Anti-pattern 警告**（`SKILL.md:130`）：`纯解说 / 原声混剪`（`target_mode`）只在“快速路线（Fast Path）”下存在，“标准路线”根本没有这个参数！如果同回合一起问，用户选了“标准路线 + 原声混剪”就会直接触发参数冲突。**规则：下游分支问题必须在父节点确认后才能提问，每回合只问一个决策**。
2. **同名/近名字段的防呆映射表（Field Collision Guard）**：
   - 后端 API 历史包袱导致返回 JSON 里同时存在 `.task_id`（32位 hex）、`.task_order_num`（`fast_writing_clip_data_xxxxx`）和 `.results.order_info.order_num`（`script_xxxxx` 计费单号），而下游接口的参数名偏偏叫 `order_num`。
   - Lebih 致命的是，Fast Path 的 `video-composing` 接收的是第 2 步 `fast-clip-data` 的 `task_order_num`，而 Standard Path 的 `video-composing` 接收的却是第 2 步 `generate-writing` 的 `task_order_num`（传第 3 步 `clip-data` 的单号会直接报 `10001 任务关联记录信息缺失`）。
   - 作者没有去改后端，而是在 `SKILL.md` 和 `workflows.md` 里画了清晰的 **正反例真值表（✅ / ❌）**，把后端的坑在 Prompt 层徹底堵死。
3. **macOS `zsh` 轮询脚本的 `$status` 保留字防坑 + 双重熔断（`operations.md:38-82`）**：
   - 在 macOS 默认 shell `zsh` 中，`$status` 是只读内置变量（等同于 `$?`）。如果 Agent 顺手写出 `status=$(...)`，脚本第一行就会报 `read-only variable: status` 退出。因此强制规范变量名为 `task_status`。
   - 同时内置双重熔断：`MAX_EMPTY=12`（连续 12 次即 1 分钟解析不出 JSON 立刻跳出打印原始报错，防网络/鉴权挂死）+ `MAX_ITERATIONS=720`（1 小时绝对上限，防状态码卡在 `1` 无限死循环），并写明跳出循环不等于取消服务端任务及如何无损恢复。
4. **跨步骤语言链强一致性锁（Language Chain Rule）**：
   - 配音音色语种（`dubbing`）→ 文案生成语种（`language`）→ 视觉模板硬编码文字（`bottom_disclaimer_text` 默认是中文“本故事纯属虚构 请勿模仿”）。Skill 强制要求：只要配音选了非中文，Agent 必须主动把免责声明、侧边竖排字全部翻译成目标语种再展示给用户确认，严禁把中文默认值提交进外语视频。
5. **高成本不可逆动作的「全量 Payload 预审门禁」**：
   - `magic-video` 每分钟扣 30 点且不可撤销。Skill 硬性规定提交前必须向用户完整展示所选模板及每一个 `template_params` 键值对，拿到明确确认才准执行 `task create`。

#### 宝藏 B：`narrator-ai-cli/AGENTS.md`（`org-rules.md`）暴露的 668 行企业级 Agent 研发与商业化 SOP
这个仓库根目录下同步了一份来自私有组织 `Gridltd-DevOps/.github/org-rules.md` 的 **668 行企业级 Agent 宪章**，展示了他们如何用 GitHub 管住研发、PMO、法务和电商矩阵：
1. **Issue 模板强制收尾块 `### Agent Execution Prompt`（`AGENTS.md:111-226`）**：
   - 组织内所有可执行 Issue（Bug / Feature / Task / Regression / RFC）必须区分 Discovery（探索，不可直接关单）与 Delivery（交付），且 Issue 最末尾必须包含结构化的 6 行指令块：
     ```markdown
     ### Agent Execution Prompt
     - Execution mode:
     - Agent should:
     - Agent must not:
     - Required context to read:
     - Expected output:
     - Stop conditions:
     ```
   - 明确规定：如果一个待执行 Issue 缺少 `Original Requirement`、`Boundary / Non-goals` 或 `Agent Execution Prompt`，Agent **必须在动手写代码前停机反问负责人**，且 Prompt 无权凌驾于 `Boundary / Non-goals` 之上。
2. **Agent 提交 PR 的自曝块 `## Agent Exposure Block`（`AGENTS.md:100-106, 323-326`）**：
   - 凡是由 Agent 编写或实质修改的 PR，除了常规的 `## Related Issue`、`## Summary`、`## Test Plan` 外，必须附上 `## Agent Exposure Block`，强制 Agent 自己交代 7 件事：
     - `Understood Goal`（我理解的目标）
     - `Planned Scope`（计划范围）
     - `Actual Changes`（实际改动）
     - `Out-of-Scope`（未触碰部分）
     - `Test Evidence`（测试证据）
     - `Remaining Risk`（剩余风险）
     - `Confidence-of-Agreement`（与人类意图一致的置信度）
   - 这个设计极好地解决了“人类审 Agent 的 PR 时不知道它哪里是猜的、哪里漏测了”的痛点。
3. **员工身份确定性解析器（防 Agent 发错人）**：
   - 禁止 Agent 凭记忆或模糊花名（`alias` / `github_name`）直接指派 Issue 或发飞书消息，必须先调 `resolve_team_member.py --members-file team/members.yml` 解析出唯一的 `github`、`lark_open_id` 或 `email`，匹配多于 1 人必须停下让用户确认。
4. **跨仓库 Issue 迁移的完整溯源链（`AGENTS.md:556-582`）**：
   - 要求新 Issue 顶部必须用引用块写出从源头至今的完整迁移链（`A → B → C (this)`），双向写入正文（不只写评论），并先查 PMO 总看板防重复建单。
5. **新产品上线前的「4 项命名红线审查（ADR-014）」（`AGENTS.md:584-597`）**：
   - 任何新产品/子品牌排期前必须交齐 4 份截图证据，否则 PMO 一键打回（贴 `needs-naming-review`）：
     1. **同名/近名竞品搜索**：Google + Bing/百度首页前 10 条有同行同功能竞品 → 强烈建议改名；
     2. **品牌词原创度拆解**：词根 ≥50% 为行业通用词（如 `Video`、`AI`、`Smart`、`Quick`、`Pro`）→ 预警 SEO 稀释与 SEM 高成本风险；
     3. **域名与商标可注册性**：`.com` 与目标国别域名 WHOIS + 中国商标网（`sbj.cnipa.gov.cn` 第 9/35/42 类）+ USPTO TESS / EUIPO → 核心域名被同行占则强制改名；
     4. **国内主流平台账号预审**：公众号 / 视频号 / 小红书 / 抖音 / B站重名与资质实测 → ≥2 个平台拒审则强制改名。
6. **把 AI 工具包装成「人工质保服务」在 5 大电商平台卖 SKU 的商业闭环（`docs/finops.md` & `sales-playbook.md`）**：
   - 他们在淘宝（~5% 佣金）、拼多多（6‰ 虚拟商品）、小红书、闲鱼、微信小店上架解说定制服务；
   - 线索从 `leads-douyin` / `leads-xiaohongshu` 进 GitHub Issues（每客一 Issue），双向同步开源 `Twenty CRM`，成交后进飞书《电商记录表》bitable，每月按 `LLM token + TTS + 渲染队列 + 人工核对工时` 对账算 SKU 毛利率（目标毛利 **35%–55%**，连续 3 个月毛利为负即触发下架）。

---

## 四、可执行下一步

- [ ] **升级我们的 `kanban-worker` / `github-issue-to-pr` 规范**：引入 `## Agent Exposure Block`（7 项自曝清单：理解目标/计划范围/实际改动/范围外/测试证据/剩余风险/意图一致置信度），让 Subagent 交 PR 或交任务时强制暴露不确定性。
- [ ] **升级 `overseas-tool-site-launch` / 产品立项检查单**：把 ADR-014 的「4 项命名红线审查（同行前10排重 / 通用词根<50% / 域名+9·35·42类商标 / 国内5平台重名预审）」加入新项目立项门禁。
- [ ] **升级 `skill-authoring` 参考案例**：收录 `narrator-ai-cli-skill` 的“正交决策分步提问（Anti-bundling）”与“macOS zsh `$status` 只读变量防坑轮询模板”。

---

*来自翡冷翠*
