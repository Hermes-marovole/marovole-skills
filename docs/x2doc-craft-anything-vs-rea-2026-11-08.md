# Craft Anything：2万星纯Rust开源「净室」软件复刻引擎与REA对比实测 - X2Doc 整理

> 来源：https://x.com/voidJan/status/2119072623560941762 （@voidJan，2026-11-07）
> GitHub 仓库：https://github.com/storytold/craft-anything （MIT / Apache-2.0 双许可，2026-11-08 实时 20,641 stars / 3,950 forks，commit `56aa319`，最新 Release `v0.5.0`）
> 对标仓库：https://github.com/morluto/rea （MIT 许可，2026-11-08 实时 441,068 stars / 109,130 forks）
> 本地浅克隆路径：`/Users/marovole/Workspace/playground/craft-anything`
> 整理时间：2026-11-08
> 来自翡冷翠

---

## TL;DR

- **它是什么**：`storytold/craft-anything` 是 ArtCraft 团队开源的纯 Rust 软件研究与 AI 重建引擎（MIT / Apache-2.0 双许可）。2026-10-31 公开建仓（此前于 10-12 至 10-30 在私有仓完成了 261 次提交），8 天冲上 **20,641 Star**。它把「检查目标软件（Study）→ 调度本机编码 Agent 重写（Build）→ 自动比对原件（Check）→ 预览/试玩或继续迭代（Ready）」做成了一个端到端产品（含 `egui` 桌面端、CLI 与 MCP Server）。
- **核心架构亮点（默认 Clean Room 净室模式 + 三屏宽 SSIM 验收）**：在 2026 年 10 月 REA（Reverse Engineer Anything，44.1 万 Star）爆火并引发 AI 厂商拦截逆向请求与 Anthropic 限制游戏克隆风波的背景下，Craft Anything 默认开启 **Clean room（净室模式）**——**绝不读取原件的代码、文件或网页源码**，只基于访客可见的截图、文字、测量布局、颜色、字体与间距（或用户授权截取的窗口画面）让 AI 重建，从根源上切割源码抄袭风险；只有显式开启 **Deep（深度模式）** 时，才会动用内置纯 Rust 反汇编/反编译引擎与可选的 Ghidra 读取内部代码与网页 JS。
- **把「结果验收」写进死循环（Check, not guessed）**：针对网页复刻，它的 `rebuild_check` 会在本地回环启动构建产物，在 **1440px、768px、390px 三种屏幕宽度**下与原网站逐页比对（对原网页连拍 3 次剔除动态变化区域后，计算布局与感知细节均值 SSIM 相似度，并列出漏掉的颜色、字体、字号、间距、横向溢出、新增报错和无障碍缺口），不达标则自动打回给 Agent 继续收敛。
- **官方审计表揭穿营销号滤镜（为什么评论区有人骂「垃圾」）**：原帖吹嘘「内置 320+ 工具扒光目标软件底裤、原地盖楼」，但我们直接查验仓库内的 `docs/tool-status.md` 与 `docs/STATUS.md` 并实跑 macOS `v0.5.0` CLI 发现：项目明确标注处于 **Early Alpha**；在官方功能审计表中，**Frida 动态插桩（9 个工具，部分会话处理在源码中系模拟）、Runtime 进程捕获（5 个工具）、Android 真机 adb（23 个工具）以及 Apple（6 个）、Android 静态（4 个）等共计 52 个工具（其中仅 adb、Frida、Runtime 三项就占 37 个）全部处于 `Unverified`（未验证）状态**；构建端首选支持本机已登录的 **Claude Code**（`STATUS.md` 中亦记录 Maki、DeepSeek Harness、Aider、GitHub Copilot、Grok Build 已跑通实机测试，而 Codex 适配器与内置 API-key 构建循环尚未跑过真实账号构建）。冲着「一键破解任意大型商业软件」去的用户必然败兴而归。
- **与我们现有栈的取舍结论（借机制、不重复挂 MCP）**：我们的 Hermes 环境已内置 `rea` 插件（`rea-agents@6.7.0`，209 个按需加载的 MCP 工具）。**不需要**再把 Craft Anything 的 321 个工具挂进全局 `~/.hermes/config.yaml` 造成工具名空间膨胀；真正值得吸收的是它的 **① Clean Room / Deep 双模式权限边界设计**、**② 网页三屏宽连拍三次去噪 + SSIM 自动化验收清单**、以及 **③ `AGENTS.md` 与 `docs/pitfalls.md` 的极致 Rust 工程纪律**。

---

## 一、原帖核心内容与评论区两极反差

### 1.1 原帖正文（`@voidJan`）

> 逆向界的真神来了！
>
> 18.7k ⭐️ 的 Craft Anything，站在REA的肩膀上直接给你原地盖楼！
>
> 它直逆向跑通了「取证 ➔ 编码 ➔ 验证」闭环：
> 1️⃣ Study：内置 320+ 工具，反汇编/抓包/DOM检查，先扒光目标软件底裤，输出结构化证据；
> 2️⃣ Build：通过 MCP 调度 Claude Code 写代码；
> 3️⃣ Check：多分辨率自动比对，SSIM 视觉+交互检查，不达标自动迭代修复
>
> 对比 REA：REA 偏重调 IDA/Ghidra 做深度逆向调查；Craft 则是把「逆向+复刻+验收」做成了端到端产品
> 现在你可以直接创建一个自己享用的工具了
> https://github.com/storytold/craft-anything

### 1.2 评论区的真实碰撞

原帖评论区第 1 条高赞回复（`@KkitHello31319`）直接泼了冷水：
> 「很垃圾的项目 用过一次再也不用了」

为什么一个 8 天拿下 2 万 Star、底层有 923+ 个自动化测试兜底的纯 Rust 项目，会在中文区引发「真神」与「垃圾」的极端对立？因为中文营销帖把它的「320 个工具」包装成了无所不能的黑客破译神器，却隐去了它**默认开启 Clean Room（禁止读内部代码）**以及**处于 Early Alpha（大量底层动态工具未验证、强依赖用户自己的 Claude Code 额度）**这两个核心前提。

---

## 二、一手源码与本机 CLI (`v0.5.0`) 实测验尸

我们在 M2 Max macOS（`macos-aarch64`）上浅克隆了 `storytold/craft-anything`（commit `56aa319`），并下载官方公证的 `craft-anything-cli-0.5.0-macos-universal.zip` 进行了实机验证。

### 2.1 真实工具盘点与分层架构（`AGENTS.md` + `craft-anything-cli commands`）

- **纯血 Safe Rust 架构**：全仓库强制 `unsafe_code = "forbid"`，生产代码严禁出现 `unwrap` / `expect` / `panic!` / `todo!` / 未检查的下标访问。所有外部进程调用（Ghidra、Java、adb、浏览器、Agent CLI、SSH）必须经过 `craft_anything_platform::process` 统一封装（强制关闭 stdin 防挂起、带超时死线与进程组清理），锁机制强制使用自研防死锁 `craft_anything_platform::sync::Mutex`（由 `cargo xtask layers` 与 `cargo xtask locks` 在 CI 静态拦截）。
- **工具数量核实**：README 写有「320 tools（引擎内 300 个，其余来自 AI 与设置层）」，`docs/tools.md` 生成列表为 **302 个引擎工具**，而 `v0.5.0` 的 `craft-anything-cli commands` 实测共输出 **321 个命令/MCP 工具**，分布在 17 个 toolset 中：
  - `native` (55) · `core` (36) · `formats` (36) · `projects` (28) · `adb` (24) · `browser` (22) · `setup` (20) · `application` (17) · `apple` (14) · `android` (14) · `runtime` (14) · `javascript` (11) · `frida` (9) · `managed` (8) · `java` (6) · `build` (6) · `database` (1)。

### 2.2 实测 1：Clean Room（净室模式）的硬拦截机制

不加 `--deep` 标志直接让它分析二进制文件时，引擎在毫秒级直接拒绝并返回结构化 `ToolError`：

```json
{
  "error": {
    "category": "missing",
    "code": "feature_missing",
    "details": { "reason": "clean_room", "tool": "native_rust_binary_show" },
    "message": "This looks inside the original (its code, files or page source), which Clean room never does.",
    "remediation": "Turn on Deep mode: the switch in the title bar or Settings, `settings_set deep_mode true`, or `--deep` on the CLI.",
    "retryable": false
  }
}
```

查阅 `crates/engine/src/clean_room.rs` 源码可见，默认 Clean Room 白名单精确放行 **107 个不碰目标内部的工具**（会话与证据管理、项目与构建控制、设置、以及仅以外部访客视角观察网页截图/可见布局或应用窗口画面的工具）。在 Clean Room 下启动 Claude Code 聊天或提问时，还会通过 `--disallowedTools` 显式禁用 Claude Code 自带的 `Read`、`Glob`、`Grep`、`LS` 等本地文件读取工具，确保 AI 只能依据外部可见特征做净室重建。

### 2.3 实测 2：Deep（深度模式）纯 Rust 内置引擎免外部依赖拆包

加上 `--deep` 参数后，无需安装 Ghidra 或 IDA，仅靠它内置的纯 Rust 解析器：
1. **自检 `craft-anything-cli` 自身（`native-rust-binary-show`）**：瞬间解析出 65.3MB Mach-O 二进制内的 **31,364 个 Rust 符号**、`rustc` 提交哈希（`58cf8f9c...`）、**116 个 Cargo 依赖包及精确版本号**（如 `iced-x86 1.21.0`、`oxc_parser 0.153.0`、`wasmparser 0.261.0`、`yaxpeax-arm 0.5.0`），以及源码目录结构。
2. **拆解本机 `/Applications/Vorssaint.app`（`apple-macho-show`）**：毫秒级输出 `arm64` Mach-O 的 **89 条 Load Commands**、**71 个动态链接库（Frameworks/dylibs）**、**4,376 个导入符号**、代码签名与安全缓解标记（`canary: true`, `nx: true`, `pie: true`, `code_signature: true`），并返回带 SHA-256 与置信度（`confidence: "observed"`）的标准 Evidence 记录。

### 2.4 官方 `docs/tool-status.md` 揭露的真实短板（避坑必看）

为什么不能把 Craft Anything 当成全能逆向工具？官方在 `docs/tool-status.md` 里非常诚实地公布了真实审计状态：

| 工具集 (Toolset) | 已验证 (Verified) | 部分可用 (Partial) | 修复重验 (Fixed) | 未验证 (Unverified) | 官方披露的真实原因与短板 |
|---|---|---|---|---|---|
| **Core / Native / Browser / JS** | 79 | 8 | 11 | 2 | 核心静态分析与网页捕获已跑通；但 CLI 单次命令会各自新建会话，`web-site-open` 与 `web-site-capture` 分开调会找不到站点（#153） |
| **Managed (.NET)** | 7 | 0 | 0 | 0 | **内置引擎无 C# 反编译器**（`no C# decompiler (IL + structure only)`；外部反编译需另装 `ilspycmd`） |
| **Android 静态分析** | 9 | 0 | 0 | 4 | JADX / Apktool / JEB 路径均未在审计中验证 |
| **Android 真机 (`adb`)** | 2 | 0 | 0 | **23** | 审计时未连接真实 Android 设备，23 个设备操作工具未实测 |
| **Apple / App Graphs / Formats** | 31 | 3 | 0 | **9** | Apple 6 项（仅测合成 Mach-O/plist）、App Graphs 2 项、Formats 1 项未验证 |
| **Runtime (进程捕获/UI)** | 0 | 0 | 0 | **5** | 涉及运行外部代码，审计中**0 个实测** |
| **Frida 动态插桩** | 0 | 0 | 0 | **9** | **9 个工具全部未验证**；官方注明：`Frida not installed; parts of session handling are simulated in source`（部分会话处理在源码中只是模拟的！） |

---

## 三、Craft Anything vs. REA：双雄正面对比与我们的取舍

| 对比维度 | **REA (`morluto/rea`)** | **Craft Anything (`storytold/craft-anything`)** | **我们的选型与取舍结论** |
|---|---|---|---|
| **核心定位** | **逆向调查与证据工具箱（Investigation Toolkit）**：帮 Agent 看懂二进制、包体、流量与运行时状态 | **端到端软件复刻产品（Study → Build → Check → Ready）**：看懂之后直接调 Agent 盖新楼并验收相似度 | **调查用 REA，复刻工作流借 Craft** |
| **GitHub 体量（截至 11-08）** | **441,068 Stars** / 109,130 Forks（2026-04-14 建仓） | **20,641 Stars** / 3,950 Forks（2026-10-31 公开建仓） | REA 生态成熟度高出一个量级 |
| **技术栈与分发** | TypeScript / Node.js（`rea-agents@6.7.0`），深度桥接 Ghidra / IDA / Hopper / Wireshark | **100% Safe Rust**（内置无依赖反汇编/解析器 + `egui` 桌面端 + CLI + MCP + WASM 查看器） | Craft 的单文件纯 Rust 零依赖静态解析极快 |
| **版权与封号防御** | 直接做底层逆向，10 月爆火后引发部分用户被 Claude / ChatGPT 拦截或限制游戏克隆 | **默认 Clean Room（净室模式）**，不读源码只看外观与布局；调用用户本机未改动的 `claude` 二进制 | **高价值设计**：做竞品 UI/工具参考时，严守 Clean Room 边界 |
| **构建与验收闭环** | 偏重导出证据包（Evidence Bundle）与重构台账，不内置 GUI 像素级验收 | **内置 `rebuild_check`**：网页在 `1440 / 768 / 390px` 三屏宽连拍 3 次去动态噪点后算 SSIM 与布局差异 | **最值得借鉴的机制**：把「三屏宽自动截图比对」抽进我们的前端开发验收流 |
| **本机集成状态** | **已内置于 Hermes `rea` 插件**（209 个工具按需通过 `tool_search` 加载） | 已下载 CLI 至本地测试，**不注册进全局 MCP**（避免与 REA 的 209 个工具重复碰撞） | **保持现状：主力逆向继续用内置 REA**，按需单次调用 Craft CLI |

---

## 四、可借鉴的 3 个工程机制（吸收进我们的工作流）

1. **前端/网页复刻的「三屏宽 × 三连拍去噪 + 结构化体检」验收法（来自 `STATUS.md` §Rebuild workflow）**
   - 以前让 Agent 仿写网页，往往只截一张全屏图肉眼看。Craft Anything 的 `rebuild_check` 给出了工业级标准：
     - 对原网页连拍 **3 次**截图，自动识别并剔除轮播图/动画等自身会变化的区域；
     - 在本地回环启动新构建的网页，同时在 **1440px（桌面）、768px（平板）、390px（手机）** 三个宽度下测量：**SSIM 感知相似度 + 是否出现横向滚动条（sideways scroll）+ 标题字号/区块 Padding/每行元素个数差异 + 控制台报错与失败请求 + 无障碍缺失**。
     - 这一套标准可以直接作为我们做「出海 SEO 工具站（`overseas-tool-site-launch`）」和前端原型复刻时的机器验收门禁。
2. **「净室模式（Clean Room）」的合规与提示词隔离**
   - 当参考外部成熟产品做自用工具或出海站点时，强制区分「外部可见特征（布局尺度、色彩 Token、交互状态机）」与「受版权保护的内部资产（源码、Logo、照片、专有文案）」，在工具层直接拦截对原件源码与静态资源的复制。
3. **`AGENTS.md`、`docs/pitfalls.md` 与 `cargo xtask` 的多 Agent 协同护栏**
   - Craft Anything 能在不到一个月内（10-12 私有建仓至 11 月初）高并发推进超千号 Issue/PR（如 `#1070`）而不把主干搞崩，靠的是 `AGENTS.md` 与 `docs/pitfalls.md` 里的硬规矩：认领任务前先提 claim 分支、合并时用 `--match-head-commit` 锁死跑过 CI 的 commit SHA、两个各自绿灯的 PR 合入前用 `git merge-tree` 测组合冲突、所有工具错误必须带可执行的 `remediation` 字段。这套规则与我们的 `kanban-orchestrator` / `merge-reconciler` 高度同构。

---

## 五、关键信息与资源

| 类型 | 名称 | 链接 | 说明与价值 |
|---|---|---|---|
| X 原帖 | `@voidJan` 推荐帖 | https://x.com/voidJan/status/2119072623560941762 | 中文区传播源头（178 赞 / 216 收藏） |
| GitHub 仓库 | `storytold/craft-anything` | https://github.com/storytold/craft-anything | 纯 Rust 净室软件研究与 AI 重建引擎（MIT/Apache-2.0） |
| 真实状态表 | `docs/STATUS.md` & `docs/tool-status.md` | https://github.com/storytold/craft-anything/blob/main/docs/tool-status.md | 查验哪些工具真能跑、哪些仍是 Unverified 模拟桩 |
| 合规说明 | `docs/claude-code.md` | https://github.com/storytold/craft-anything/blob/main/docs/claude-code.md | 解释为何直接调用用户本机 `claude` 二进制及潜在条款边界 |
| 对标仓库 | `morluto/rea` (REA) | https://github.com/morluto/rea | 44.1 万 Star 的 Agent 逆向工具箱（Hermes 已内置插件） |
| 外部报道 | PBX Science 深度报道 | https://pbxscience.com/craft-anything-open-source-rust-tool-lets-ai-study-and-rebuild-websites-apps-and-games/ | 梳理 REA 封号背景与 Craft Anything 净室模式来龙去脉 |

---

## 六、可执行下一步

- [x] 浅克隆 `storytold/craft-anything`（commit `56aa319`）至 `/Users/marovole/Workspace/playground/craft-anything` 并实测 `v0.5.0` CLI。
- [x] 完成公众号「AI 快讯贴图」3 卡草稿（No.42 · Paper 主题）并通过 Grounding + 独立模型 Review。
- [ ] 待拍板后：生成公众号深度长文（《从 44 万星 REA 到 2 万星 Craft Anything：当 AI 开始「净室复刻」任何软件，真正的壁垒还剩什么？》）与 60–85s 深蓝硬数字短视频。

---

*来自翡冷翠*
