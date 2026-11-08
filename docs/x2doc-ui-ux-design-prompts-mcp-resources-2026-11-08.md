# UI/UX 设计灵感画廊、DESIGN.md 规范库与 AI 建站 Prompt 实测拆解（5+1 站点） - X2Doc 整理

> 来源：https://x.com/amananimates/status/2119024322325217293
> 作者：@amananimates (Aman Singh, Co-founder @scrolltide.co)
> 发布时间：2026-11-07 11:09:02 UTC
> 整理时间：2026-11-08
> 关联前序文档：[AI 辅助设计与 Vibe Coding 19 个灵感与组件资源拆解 (2026-11-07)](./x2doc-ai-design-vibecoding-resources-2026-11-07.md)
> 来自翡冷翠

---

## TL;DR

- **原帖本质与数据脱水**：这是继昨日 `@BardhylBytyqi`（Modulify）之后又一个典型的**「特洛伊木马清单（Trojan Horse Listicle）」**冷启动样本（133 赞 / 20 转发 / **187 收藏** / 5,213 浏览）。作者 `@amananimates` 身为 `scrolltide.co` 联合创始人，将自家付费产品放在清单 **#1**，并在主帖与二楼 Thread 连发两段高清演示视频。**实测脱水发现**：原帖宣称 Scrolltide 拥有「600+ 设计 Prompts 和 200+ 组件」，但逐一清点官网 5 大栏目，实际总量为 **320 项**（143 模板 + 85 组件 + 55 着色器 + 23 页面区块 + 14 UI 屏幕），与其个人简介写的 `300+ prompts & websites` 一致，且全站**仅 7 个模板免费**（核心 3D、组件、着色器与 MCP 均锁在 $144/年或 $299 终身买断档位，且数字商品概不退款）。
- **全帖真正含金量最高的资产（#5 `styles.refero.design` + 开源 `refero_skill`）**：
  1. **`styles.refero.design`（免费免登录浏览）**：将 Apple、teenage engineering、Raycast、Brex 等 **2,000+ 顶级产品官网**逆向提取为 AI 可直接读取的 **`DESIGN.md` 设计系统文件**（含归一化色彩 Token、出现频次、角色边界、字体排印与组件还原），可直接喂给 Claude Code、Codex、Cursor、v0 或 Lovable。
  2. **`github.com/referodesign/refero_skill`（MIT 开源，343 Stars，免账号可用）**：提供了一套「先研究锁定参考、再写代码」的 Agent 设计方法论（含 `SKILL.md` 主文件与 10 份 `references/` 工艺参考文档）；其中 `anti-ai-slop.md` 系统定义了 **9 大「AI 味（AI Slop）」视觉指纹**（如 `#6366f1` 蓝紫默认色、万物皆卡片、默认暗黑模式、伪文艺衬线单字斜体、左侧装饰竖条等）与 **6 项出厂石蕊测试（Litmus Tests）**。
  3. **`refero.design/mcp`（Pro 付费层）**：为 AI Agent 提供 **145,000+ 真实产品界面**（76,000+ Web + 68,000+ iOS，GitHub 最新口径为 150,000+）与 **12,000+ 用户流**（GitHub README 口径为 6,000+）的结构化检索接口。
- **三个高实用度专项组件画廊（#2 / #3 / #4）+ 评论区补充（Shipped Gallery）**：`navbar.gallery`（导航栏专项）、`footer.design`（页脚专项，与昨日榜单 #10 重合）、`cta.gallery`（转化区块专项），外加评论区 `@MOwais2004` 自荐的 `shipped.gallery`（收录由 **Claude Code** 与 **Antigravity + Gemini 4 Argon** 构建的真实 WebGL 网站及复刻工作流）。

---

## 原帖核心内容与 Thread / 评论还原

### 1. 主帖正文（已将全部 `t.co` 短链还原为实际落地 URL）

> If you're a UI/UX designer, bookmark this.
>
> 1. https://www.scrolltide.co/ — 600+ design Prompts and 200+ components with full source code for 3D and scroll-driven sites. *(原短链 `https://t.co/0QEdrNJuNz`)*
> 2. https://www.navbar.gallery/ — navbar inspiration *(原短链 `https://t.co/kj7FnrwoVM`)*
> 3. https://www.footer.design/ — better footers *(原短链 `https://t.co/k25A3XTvZO`)*
> 4. https://www.cta.gallery/ — CTA inspiration *(原短链 `https://t.co/ZE5iPczbj3`)*
> 5. https://styles.refero.design/ — Real product design styles *(原短链 `https://t.co/cxlfDWRmgH`)*
>
> What did I miss?

- **主帖附带视频**：时长 24.05 秒（1080×1080），暗色蓝橙光晕背景下悬浮多块倾斜的网页卡片，居中高亮展示 Scrolltide 组件库中的 **Receipt Printer（热敏小票打印机定价卡片，视频首帧画面标题 *"Clock the hours. Keep the change."*）**。

### 2. 作者自评 Thread（二楼）
- **链接**：https://x.com/amananimates/status/2119024326834024646
- **正文**：
  > https://scrolltide.co - gives 600+ prompts for 3D and scroll-driven sites at
  > • Components nobody else has
  > • Shaders, sections and UI screens in one library
  > • Copy the prompt, paste it into Claude, Cursor or Lovable, launch live
  > • Full source code included
- **二楼附带视频**：时长 28.20 秒（3840×1992 超宽屏录屏），直接演示 `scrolltide.co` 首页（大标题 *"Ship websites that move like the tide."*，显示 *"13,500+ builders shipping faster"* 与顶部 `MCP NEW` 标签）。

### 3. 评论区高信号补充（`@MOwais2004`）
- **链接**：https://x.com/MOwais2004/status/2119166569913970999
- **正文**：`us. you missed us 👀 Shipped Gallery: real AI sites + their prompts`
- **对应站点**：https://www.shipped.gallery/ （作者 Owais `@MOwais2004` 刚上线的 AI 建站作品与 Prompt 展厅）。

---

## 关键信息与资源（5+1 站点逐一实测核验表）

| 序号 | 名称 | 实测落地链接 | 核心机制与真实体量（实测核验） | 免费/付费边界与价值判断 |
|---|---|---|---|---|
| **#5** ⭐ | **Refero Styles & Refero MCP / Skill** | • 样式库：https://styles.refero.design/ <br>• 主站与 MCP：https://refero.design/mcp <br>• 开源 Skill：[referodesign/refero_skill](https://github.com/referodesign/refero_skill) | **全清单最具工程价值的资产**。<br>1. **Styles 库**：收录 **2,000+** 顶级产品网站（Apple、teenage engineering、Raycast、Brex 等）的逆向设计系统，每套均提供归一化色彩 Token（含出现频次与语义角色）、字体、间距与可直接复制的 **`DESIGN.md`**。<br>2. **Refero MCP**：连接 **145,000+ 真实界面**（7.6 万+ Web + 6.8 万+ iOS，GitHub 标 15 万+）与 **12,000+ 用户流**（GitHub README 标 6,000+）。<br>3. **开源 `refero_skill`（MIT，343 Stars）**：含 `SKILL.md` 主文件与 10 份 `references/` 设计工艺参考文档（特别是 `anti-ai-slop.md`）。 | • `styles.refero.design` 浏览与 `DESIGN.md` 获取：**免费**。<br>• `npx skills add https://github.com/referodesign/refero_skill --skill refero-design` 安装本地工艺规范：**免费免账号**。<br>• `api.refero.design/mcp` 实时检索 14.5 万+ 界面：**需 Refero Pro 付费订阅**。 |
| **#2** | **Navbar Gallery** | https://www.navbar.gallery/ | **网站顶部/侧边导航栏专项画廊**。按 8 大结构分类：Static/Sticky（静态吸顶）、Dropdown/Flyout（下拉菜单）、Mega Menu（大型分类面板）、Side Bar（侧边栏）、Search Bar（搜索导航）、Announcement Bar（顶部公告条）、Full Screen（全屏菜单）、Breadcrumbs（面包屑导航）。 | **完全免费浏览**。做 SaaS 官网或后台布局前，先选定导航形态再让 AI 写，避免千篇一律的左 Logo 右三链。 |
| **#3** | **Footer.design** | https://www.footer.design/ | **「地球上唯一的页脚专项画廊」** *(注：与昨日 `@BardhylBytyqi` 清单 #10 重合)*。支持按 11 种风格筛选：Typographic、Small Type、Illustrative、Grid、Flat、Animated、Cards、Bright、Dark、Large Type、Bold。 | **完全免费浏览**。专治 AI 生成网页收尾粗糙、永远只会写四列灰色链接的通病。 |
| **#4** | **CTA.gallery** | https://www.cta.gallery/ | **网页转化区块（Call-to-Action）专项画廊**（由 Webestica 与 Iconstica 赞助）。支持按行业（Industry）与亮暗模式（Dark/Light Mode）筛选真实产品的底部或中段转化卡片。 | **完全免费浏览**。适合设计落地页注册引导、Waitlist 收集框与定价转化入口时参考构图。 |
| **#1** | **Scrolltide** *(发帖人自家产品)* | • 官网：https://www.scrolltide.co/ <br>• MCP：https://www.scrolltide.co/mcp <br>• 定价：https://www.scrolltide.co/pricing | **3D 与滚动驱动（Scroll-driven）网页 Prompt + 源码库**（技术栈：React + Vite / Next.js + Tailwind + Framer Motion + GSAP + Three.js + WebGL + Shaders + Lenis）。<br>⚠️ **体量脱水**：原帖宣称「600+ Prompts、200+ 组件」，但实测官网 5 大栏目合计 **320 项**：<br>• `/templates`：**143 个**整页/首屏模板（**仅 7 个免费**，如 `Otis`、`SELENE`）<br>• `/components`：**85 个**交互组件（如热敏小票机 `Receipt Printer`、液态玻璃 `Glass Tabs`）<br>• `/shaders`：**55 个** GPU 背景着色器（提供 MP4 + 静态图 + 单文件无依赖 React 组件，离屏自动暂停）<br>• `/sections`：**23 个**页面中段区块<br>• `/ui`：**14 个**完整应用仪表盘界面 | • **免费层**：仅开放 7 个基础模板。<br>• **Monthly ($39/月)**：仅含核心模板库与 23 个 Section，每周限解锁 10 个新付费模板；**不含** 3D 模板、85 个组件、55 个 Shader、14 个 UI 界面及 MCP。<br>• **Yearly ($144/年) / Lifetime ($299 买断)**：解锁全部内容 + `Scrolltide MCP`（`claude mcp add --transport http scrolltide https://www.scrolltide.co/api/mcp`）。<br>• **退款政策**：All sales are final（所有购买及忘记取消的自动续费均不退款）。 |
| **评论 #1** | **Shipped Gallery** | https://www.shipped.gallery/ | **真实 AI 建站成品与复刻工作流画廊**（由评论区 `@MOwais2004` 创立）。收录由 **Claude Code** 与 **Antigravity（搭配 Gemini 4 Argon 模型）** 构建的 WebGL / 3D 交互网站，每篇附带 5 步复刻工作流（Workflow）与完整 Prompt（如 `Spider-Verse WebGL Experience`）。 | **免费免登录浏览 Prompt 与工作流**。可直接观察高质感 AI 网站是如何拆解素材准备（Cutout 抠图 + 背景层）与 GSAP/Lenis 滚动指令的。 |

---

## 深度拆解：Refero 开源的「9 大 AI 味视觉指纹（Anti-AI-Slop）」与石蕊测试

在 `#5 styles.refero.design` 顺藤摸瓜找到的官方开源仓库 [`referodesign/refero_skill`](https://github.com/referodesign/refero_skill)（MIT 协议）中，`skills/refero-design/references/anti-ai-slop.md` 极其精准地总结了为什么大模型写出的前端页面总有一股廉价的「AI 味」，并给出了硬性门禁规则：

### 1. 九大 AI 生成界面指纹（The 9 Tells of AI Slop）

1. **一号指纹：无脑默认蓝紫色（Indigo/Violet，`#6366f1` / `#8b5cf6` / `#7c3aed`）**
   - **成因**：训练数据被 Tailwind CSS 默认的 Indigo 色系严重污染，LLM 求平均值时必然收敛到蓝紫色。
   - **铁律**：除非品牌明确要求，**严禁使用 `#6366f1` / `#8b5cf6` / `#7c3aed`**（可用 `#2563eb` 专业蓝、`#0d9488` 青绿或品牌主色替代）。
2. **二号指纹：万物皆卡片（Cards Everywhere）**
   - **成因**：AI 觉得把所有内容包进「圆角 + 边框 + 阴影」的盒子里最安全。
   - **铁律**：默认**不用卡片**，改用区块（Sections）、分栏（Columns）、分割线（Dividers）或媒体块。只有当容器本身承载点击、表单或展开交互时才允许用卡片。
3. **三号指纹：不分青红皂白默认暗黑模式（Dark Mode by Default）**
   - **铁律**：除非需求明确指定暗黑模式，专业基线默认使用**浅色模式（Light Mode）**。
4. **四号指纹：自动驾驶式的「伪文艺衬线风 + 单个斜体变色词」（Calm Editorial Serif on Autopilot）**
   - **成因**：新一代模型为了避开蓝紫 SaaS 风，又掉进了另一个安全模板——暖米白背景（Warm Ivory/Cream）+ 超大衬线标题 + **故意把标题里某一个词换成斜体/衬线/变色来强行装品味** + 橄榄绿/陶土色点缀。把这套模板套在开发者工具、金融看板或效率工具上就是新型 AI Slop。
5. **五号指纹：拿标准 Emoji 当图标（Emoji as Icons，如 😀🚀💡🎯）**
   - **铁律**：严禁在专业 UI 中用 Emoji 充当功能图标，必须使用 Lucide / Phosphor / Heroicons、Unicode 符号（`→ • ◆`）或 SVG。
6. **六号指纹：左侧装饰性彩色竖条（Left Accent Stripe，`border-left: 4px solid <accent>`）**
   - **铁律**：左侧竖条在真实产品中只用于表达状态、告警、优先级或当前选中项；如果你不能用一个词说出这条颜色代表什么业务状态，立刻删掉。
7. **七号指纹：多参考源求平均（Reference Averaging）**
   - **成因**：给 AI 喂了硬朗工业风、酸性黄文档站和衬线杂志风，AI 会把所有锋利特征磨平，吐出一个温吞的米白底圆角页（比如把 `#0f0e12` 纯直角工业风磨成圆角卡片）。
   - **铁律**：择一为主（保留其极端特征，如 teenage engineering 的 `Zero rounded corners, zero drop shadows, zero gradients`），次要参考只允许借 1–2 个局部细节。
8. **八号指纹：Token 角色漂移（Token Role Drift）**
   - **成因**：原设计系统规定「酸性黄仅用于主 CTA 按钮」或「代码高亮色仅用于代码块内」，AI 却拿它去涂满整块背景或边框。
   - **铁律**：Token 的「语义角色（Role）」是 Token 不可分割的一部分，保留原角色或干脆不用。
9. **九号指纹：用劣质 CSS 色块伪造复杂视觉（Fake Graphics / Text-Only Collapse）**
   - **铁律**：遇到摄影/产品实拍主导的参考风格，必须使用真实截图、生成图或明确标明宽高比与艺术指导的占位框（Intentional Placeholder），严禁用几个 CSS 渐变圆球冒充插画。

### 2. 交付前六大石蕊测试（6 Litmus Tests）

- **卡片测试（Card Test）**：如果去掉 `border + shadow + background + radius` 后既不影响交互也不影响理解 → 它根本不该是个卡片，拆掉。
- **首屏图测试（Image Test）**：如果删掉 Hero 配图后首屏依然成立 → 说明配图太弱，要么强化为主视觉，要么干脆删掉。
- **品牌测试（Brand Test）**：如果隐藏顶部导航栏后看不出这是谁家的网站 → 视觉层级太弱。
- **文案测试（Copy Test）**：如果删掉 30% 的文字反而更好读 → 继续删（AI 永远在过度抒情，人类设计师永远在做减法）。
- **身份测试（Identity Test）**：如果首屏换个名字就能当任何一家竞品的官网 → 缺少专属记忆点。
- **伪文艺测试（Editorial Test）**：如果把你的科技产品 Logo 换成一家精品咖啡馆、买手店或文学杂志依然毫无违和感 → 你掉进了「自动驾驶伪文艺风（Calm Editorial Slop）」陷阱。

---

## 我的吸收判断

### 1. 可复用能力与直接落点
- **零成本引入 `DESIGN.md` 工作流（`styles.refero.design`）**：以后无论是做个人出海工具站、单页数据应用（`single-file-data-app`），还是做灵知 AI 内部看板，写代码前先去 `styles.refero.design` 挑一个标杆（例如工业克制风选 `teenage engineering`、高密暗色效率风选 `Raycast`、清爽金融风选 `Brex`），把它的 `DESIGN.md`（含精确到出现频次的色彩 Token 表）直接存进项目根目录作为约束。
- **吸收 `anti-ai-slop.md` 作为前端与海报生成的「审美验收台」**：其总结的「9 大 AI 味指纹」与我们一贯坚持的「工程审美」「反对 Infinite Slop」「调研报告浅色一页到底」高度同频，可直接作为前端/UI 任务的自检清单。
- **借 Scrolltide 的「自然语言物理分镜写法」**：无需花 $144/$299 买 Scrolltide 会员——它公开在 `/templates`、`/components`、`/shaders` 列表页上的每段 30–50 词微交互描述（例如 `Receipt Printer`：*"switching plans rewinds the receipt and feeds a new one, ink lands on the total... and you can tear the receipt off"*；以及 `Ora`：*"240 decoded WebP frames taken apart chapter by chapter behind a real-progress preloader, with no animation library anywhere in the dependency list"*），本身就是极高水准的动效创意库与 Prompt 写法范本。

### 2. 值得沉淀到 skill / workflow 吗？
- **不新建冗余 Skill**（保持技能库精简）。
- 如需在具体前端项目中使用 Refero 的完整工艺参考，我们已将 `refero-anti-ai-slop.md` 与 `refero-teenage-engineering.md` 原文归档在本地 `media-hub/20261108-ui-ux-design-ai-resources/sources/`，随时可按需调取。

### 3. 对 AI × Product × Super Individual（超级个体 / 自媒体 IP）的价值
- **连续两天印证的海外增长公式**：昨天 `@BardhylBytyqi` 用「19 个 AI 设计站（#1 塞自家 Modulify）」拿到 944 收藏，今天 `@amananimates` 用「5 个 UI/UX 站（#1 塞自家 Scrolltide）」拿到 187 收藏（收藏数均大于点赞数）。**「细分组件免费画廊（Navbar / Footer / CTA）作饵 + 自家高客单价 Prompt/MCP 库置顶 + 高帧率微交互录屏」**已经是 2026 年海外 Indie Hacker 推设计工具的标准打法。
- **绝佳的自媒体选题切角**：普通博主转发这条推文只会当搬运工喊「快收藏这 5 个神站」；我们用 **「12 年 PM + FDE 实测脱水（戳破 #1 数量注水与不退款条款 + 挖出 #5 背后的 2,000 个免费 DESIGN.md 与 9 条去 AI 味铁律）」** 切入，既有信息增量又有鲜明的「工程审美」个人签名。

### 4. 风险或待验证点
- **Scrolltide 数量注水与锁权风险**：原帖写的 `600+ prompts and 200+ components` 与官网实际累加的 `320 项（含 85 个组件）` 存在近一倍的营销夸大；且 $39/月的基础订阅阉割了所有 3D、组件、Shader 和 MCP 权限，还在条款中写死自动续费不退费。
- **Refero MCP 权限边界**：`refero_skill` 仓库本身是 MIT 免费开源，但若在配置中启用 `https://api.refero.design/mcp` 调取在线 14.5 万张截图，则会触发 OAuth 登录并校验 Refero Pro 付费资格。

---

## 可执行下一步

- [x] 已将本帖 5+1 个站点的 24 份原始网页/JSON（含 `refero-anti-ai-slop.md` 与 `refero-teenage-engineering.md`）永久归档至本地 `/Users/marovole/HermesWork/media-hub/20261108-ui-ux-design-ai-resources/sources/`。
- [x] 已生成公众号「AI 快讯贴图」第 42 期（Swiss 主题 3 卡：`AI做网页总像套模板？收好这5个真实设计库`），过 Grounding 门禁并推入公众号草稿箱。
- [ ] 后续开发新出海站点或前端界面时，先从 `styles.refero.design` 导出目标风格的 `DESIGN.md` 放入仓库根目录，并对照 `anti-ai-slop.md` 的 9 条铁律做交付前自检。

---

*来自翡冷翠*
