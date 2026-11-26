# X2Doc 源帖存档与代码核查：QingYue 开源 `herd-skill` 对比 Google Antigravity `/swarm`

> **整理归属**：来自翡冷翠  
> **抓取与核查日期**：2026-11-26  
> **触发原帖**：https://x.com/YuLin807/status/2125497884569452723  
> **引用前帖**：https://x.com/YuLin807/status/2125239971661697033  
> **开源仓库**：https://github.com/ythx-101/herd-skill  
> **官方对照文档**：https://antigravity.google/docs/swarm.md · https://herdr.dev/ · https://herdr.dev/tui/

---

## 一、源帖与作者快照（2026-11-26 抓取）

- **作者**：QingYue（X：`@YuLin807`，接口记录粉丝 `10,135`；GitHub：`ythx-101`，简介 `非程序员 · pi + herdr · agent 工具开源 · 2k stars`，公开仓库 `48` 个，粉丝 `100`）
- **主帖**（`2026-11-25T07:52:40Z`，接口快照：`10,475` 浏览、`97` 赞、`131` 收藏、`9` 转发、`6` 回复、`2` 引用）：
  > 谷歌家的/swarm 功能过于好用，我很早就想对它下手，所以我基于 herdr 来创建一个适用于任意 Agent 和任意模型的 skill，我管这个叫做 herd。
  > 他吸收了/swarm 中的巡检和多 Agent 协同的优点，同时还发挥了 herdr 的多设备协同的特点，现在我通常会和 hark 充分交流之后，然后把任务安排给 Fable，然后让他统帅 opus Neon 等一众 Claude、Gemini 系列模型做完。
  > 是完全不用操心的程度，是晚上能睡得着觉第二天醒来收菜的程度。
  > 欢迎大家的来访。
- **评论区互动摘录**（来自 teapawt 存档）：
  - Ray Tien（`@raysnote`）称之前用 herdr 遇到「main agent 不會收到 subagent idle 的問題，都需要用 loop 等 workaround 去處理」且夸 herdr 可以跨机器；QingYue 回复「从发现他开始 就成为了我的 Agent 基建产品」「因为我本来是有好几个 vps 所以想让他们合作起来 就正好用到 herdr」。
  - AI 嘉豪（`@Davidwuuu92`）问是否对 `/swarm` 做了逆向（rea）；QingYue 回复「还可以这样吗 没有 就是观察了他的运行模式和优点」。
- **引用前帖**（`2026-11-24T14:47:48Z`，接口快照：`13,231` 浏览、`26` 赞、`48` 收藏、`2` 回复、`1` 引用）：
  > 今天和fable仔细拆了一下 /swarm 这个技能，真正的是多模型编排的好帮手啊！

---

## 二、3 张原帖配图逐字核心摘录

### 图 1（主帖对比海报：`01-poster-herd-vs-swarm.jpg`）

- 标题：`herd: 让一群 agent 跨机器干活`；副标题：`和它借鉴的 Antigravity /swarm 逐项放在一起看`
- 右上角元数据：`ythx-101/herd-skill` / `2026.11.25` / `v0.1.0 · MIT`
- 顶部三项指标：`5 个脚本加一份技能说明`、`34 项自测全部通过`、`20 秒 轮询一次公告板`
- 摘要对照：
  - **herd 多出来的**：不同席位可以用不同的命令行和模型；验收绑定检查命令和写死的截止时间；worker 可以分布在多台机器上。
  - **herd 没做的**：进度总览页和全屏看板；每个 worker 独立的工作副本；低额度预警和原地换模型。
- 页脚注明：`原版资料: antigravity.google/docs/swarm.md, 2026-11-25 读取`

### 图 2（引用帖截图 1：`02-swarm-study-part1.jpg`）

- 核心结论原话：「`/swarm` 的核心机制我们都能在 herdr 上复现，真正的差距主要是三处（成员互相唤醒、停滞监控、额度预警），而我们在跨模型、机检闸门、硬截止这三点上已经比它强。」
- 证据说明：称读了 `agy 1.5.16` 自带的 swarm 指令文件（375 行）和 `eqart3` 完整记录；公开资料份由模型摘要，未逐字核对官方页。
- `eqart3` 实测代价表：
  - 成员：`1 协调者 + 8 worker，全部 Claude Opus 5.5`
  - 有效运行时间：`约 67 分钟`
  - 总跨度：`5 小时 1 分钟`
  - 因额度耗尽停摆：`约 4 小时 10 分钟`

### 图 3（引用帖截图 2：`03-swarm-study-part2.jpg`）

- 开头原话：「开跑 10:44 就把 Opus 额度打空了，全员停摆。额度重置后它不会自己恢复，是你手动发话才续上的。」
- 列出 5 项差距：成员不能互相唤醒、没有停滞监控（称 `/swarm` 有每 3 分钟巡检的监控角色）、没有额度预警（称 `/swarm` 剩 10% 提醒且可原地换模型保留上下文）、没有进度总览、工作区隔离靠约定。
- 列出 4 项优势：跨模型、机检闸门（文字一致性和对比度两个硬脚本）、硬截止、跨机器。
- 提出 2 项优先借鉴做法：1）门铃加监控，用脚本做、不用模型；2）公告板改成带序号的结构化帖子流，沿用 `[done]`、`#序号` 约定。

---

## 三、`ythx-101/herd-skill` 仓库与源码核查（2026-11-26）

- **GitHub API 元数据**：`13` Stars、`0` Forks、`0` Open Issues、`MIT` 协议；创建于 `2026-11-25T02:56:17Z`，最后推送 `2026-11-25T11:49:40Z`（共 `2` 次提交：`16aba8b` 初始提交、`0dc2afa` 添加 52 秒中文宣传片）；GitHub Tags 与 Releases 均为空（`v0.1.0` 标注在 `herdr-plugin.toml` 中）。
- **12 个核心文件行数清点（合计 743 行）**：
  - `skills/herd/SKILL.md`：98 行
  - 5 个 `bin/` 脚本合计 **420 行**：`herd-post`（36 行）、`herd-read`（31 行）、`herd-watch`（36 行）、`herd-preflight`（34 行）、`herd-watchd.py`（283 行，纯 Python 标准库）
  - 3 个模板合计 70 行：`BRIEF.md`（30 行）、`BRIEF.zh-CN.md`（30 行）、`roster.json`（10 行）
  - 可选弹窗插件：`herdr-plugin.toml`（14 行，`min_herdr_version = "0.9.5"`，`platforms = ["linux", "macos"]`）、`plugin/board.sh`（27 行）
  - 自测脚本：`tests/selftest.sh`（114 行，含 34 项断言）
- **关键机制（源码逐行确认）**：
  1. `herd-post`：通过 `flock -w 30 9` 对 `.board.lock` 加锁写入 `board.jsonl`（JSONL 格式，含 `seq`、`time`、`agent`、`text`），支持 `-` 从 stdin 读正文防止 ssh 展开 `~`、`$` 和引号。
  2. `herd-watchd.py`：默认每 20 秒轮询，识别词首 `@名字`、`@all`、`@coordinator` 及前缀组（`@fix` 匹配 `fix-1`、`fix-2`），通过 `herdr [--machine <label>] agent prompt` 发送单行唤醒消息；用 `watch.state.json` 维护已通知记录与游标，遇 `blocked` 成员时不推进游标（`min(pending) - 1`）等待解阻后重送；支持 `HERD_DENY_PANES` 禁发名单；触发三类一次性协调者提醒（绝对截止时间 `deadline_utc`、无 `[done]` 且静默超 `stall_minutes`、窗格最近 60 行匹配 `quota reached|RESOURCE_EXHAUSTED|exhausted your quota`）。
  3. `herd-preflight`：默认调用 `agy -p 'Reply with exactly: pong' --model {model} --dangerously-skip-permissions`，超时 60 秒，结果归类为 `ok` / `quota` / `no-capacity`（识别 `503`/`no capacity`）/ `timeout` / `error`。
  4. 验收与盲审规则（`SKILL.md`）：明确写明 `herdr's idle or done state is not acceptance`，只认 `@coordinator [done]` 加任务书全部检查命令通过；到截止时间硬收卷不延期；可选盲审启用未读过公告板的新成员（尽量换模型），将产物改名为 `A / B / C` 仅传文件路径与评分标准。

---

## 四、官方文档对照与 macOS 自测核验

1. **对照 Google 官方 `/swarm` 文档（`https://antigravity.google/docs/swarm.md`）**：
   - `/swarm` 对所有套餐（all plans）开放（预览阶段，企业与商业账号受管理员策略控制），官方提示因每个 worker 是独立 agent，耗额度远快于单次对话。
   - 模型支持：默认与主对话同模型，但官方文档明确支持在提示词里为单个或全部 worker 指定模型选择器中的其他模型（并给出「跨模型编码与验证」示例提示词），也支持将等待中的 worker 原地切换到另一模型并保留上下文。
   - 额度耗尽：官方文档证实成员耗尽额度后会暂停，**额度刷新后不会自动恢复**，需要新帖、切模型或用户发话才能继续。
   - 隔离与巡检：默认共享工作区，支持给每个 worker 独立工作副本（移除 worker 会删除其工作副本）；通常每 2–4 个 worker 配一个 `@verifier`，另配一个 `@monitor` 在全员静默时介入。
   - Antigravity 官方提供 4 档多 Agent 编排：Subagents（全套餐）、`/boost`（付费套餐）、`/swarm`（全套餐）、`/teamwork`（付费套餐，独立项目目录与 Critic/Challenger/Auditor/Success Auditor 里程碑门禁）。
2. **对照 Herdr 官方文档（`https://herdr.dev/` 与 `https://herdr.dev/tui/`）**：
   - Herdr 开源协议为 Apache 2.0，现分为两个独立程序：**Herdr TUI**（`herdr` 命令，主页展示 `49,770` GitHub stars、`2,163,682` installs、`2,081` community plugins、`22` agent CLIs detected）与新版原生 **Herdr App + `herdr-core`**（`hc` 命令），官方 FAQ 明确说明两者**不共享 agent**（`They don't share agents, so what runs in one doesn't show up in the other`）。
   - `herd-skill` 适配的是 `herdr` 0.9.5（TUI 路线），不是 `hc`。
3. **本机 macOS 实跑 `bash tests/selftest.sh` 记录（2026-11-26）**：
   - **默认环境直接运行**：`passed=18 failed=16`。16 项失败全部由 `skills/herd/bin/herd-post` 第 14 行触发：macOS 默认不带 Linux `util-linux` 的 `flock`，报错 `flock: command not found`，随后被 `||` 分支吞掉并输出 `herd-post: lock timeout`。
   - **临时补齐 `flock` 兼容脚本后复测**：`passed=33 failed=1`。唯一失败项为 `tests/selftest.sh` 第 25 行 `FAIL herd-read --since`——该行用字符串相等 `[ "$(... | wc -l)" = 1 ]`，而 macOS BSD `wc -l` 输出带前导空格，导致比对失败。

*来自翡冷翠*
