# Graph Engineering with Claude（14步图工程）与 23.1万星 CLAUDE.md 源头对账 - X2Doc 整理

> 来源：
> - 主帖：[Movez @0xMovez](https://x.com/0xMovez/status/2119860140299997352)（2026-11-09）
> - 引用长文：[Codez @0xCodez](https://x.com/0xCodez/status/2079165300625330317)（2026-07-20，《Graph Engineering with Claude: 14-Step roadmap from 0 to graph architect (Full Course)》）
> - 关联仓库与源帖：[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)（前作整理见 [claude-md-karpathy-guidelines-2026-05-05.md](./claude-md-karpathy-guidelines-2026-05-05.md)）、[Andrej Karpathy @karpathy](https://x.com/karpathy/status/2015883857489522876)（2026-01-26）
> 整理时间：2026-11-10
> 来自翡冷翠

---

## TL;DR

- **二手营销帖的四处事实失真**：`@0xMovez` 宣称「Karpathy 的 `CLAUDE.md`（65行、6条规则）把 Claude Agent 准确率从 65% 提到 94%」，但对账源码与 Karpathy 原帖可见：① 仓库 `multica-ai/andrej-karpathy-skills`（实时 231,621 星）由 Multica 作者 Jiayuan Zhang（`forrestchang`）于 2026-01-27 创建，截图裁掉了组织名；② 65 行 `CLAUDE.md` 实为 **4 条原则**，热帖将第 3、4 条各拆成两步凑出「6 rules」；③ 全仓无任何「65% → 94%」评测数据；④ Karpathy 在 2026-01-26 原帖（786.6 万浏览）中明确写着：**「All of this happens despite a few simple attempts to fix it via instructions in CLAUDE . md.」**（即便在 `CLAUDE.md` 写简单指令去修，这些毛病照样发生）。
- **真正有工程增量的是引用长文《Graph Engineering with Claude》（14 步路线图）**：解决了「单线排队（linear script）在长上下文里失忆、慢且脆弱」的结构瓶颈。
- **核心架构公式**：**节点（Node = 绑 `JSON Schema` 的 `agent()` 判断单元） + 边（Edge = 0 Token 纯 JS 数据流转 `flatMap`/`Set`） + 屏障/流式拓扑（`parallel()` vs `pipeline()`） + 边上验证器（`correctness`/`security`/`repro` 三透镜投票） + 收敛回环（`loop-until-dry` 对 `seen` 全集去重）**。

---

## 一、`@0xMovez` 原帖与源头三方对账表

| 维度 | `@0xMovez` 推文宣称（2026-11-09） | 一手源头核实结果（GitHub API / 源码 / Karpathy 原帖） |
|---|---|---|
| **仓库归属与状态** | "karpathy's CLAUDE.md hit #1 on github trending. 228,000 stars."（截图红框仅框住 `andrej-karpathy-skills`） | 仓库全名 `multica-ai/andrej-karpathy-skills`，实时 **231,621** Stars、**23,028** Forks、**139** Open Issues。由 `forrestchang`（Jiayuan Zhang）与 Claude Opus 4.5 于 **2026-01-27** 首交（commit `8462496`），最后一次代码提交为 **2026-04-20**（共 28 commits）。README 写 MIT 协议，但根目录无独立 `LICENSE` 文件（API `license: null`）。 |
| **规则条数** | "65 lines. 6 rules."（列为 step 1 至 step 6） | `CLAUDE.md` 确为 **65 行**，但只有 **4 条原则**（`1. Think Before Coding`、`2. Simplicity First`、`3. Surgical Changes`、`4. Goal-Driven Execution`）。热帖把第 3 条拆成 step 3/4，把第 4 条拆成 step 5/6。 |
| **准确率数据** | "it took my Claude agents accuracy from 65% to 94%." | 仓库 `CLAUDE.md`、`README.md`、`EXAMPLES.md` 全文无任何 65% 或 94% 数据；检验标准仅为定性描述（diff 不必要改动减少、重写减少、实现前先提问）。 |
| **Karpathy 原话态度** | 暗示靠这份 `CLAUDE.md` 即可解决 Agent 编码缺陷 | Karpathy 2026-01-26 原帖（`2015883857489522876`，7,866,679 浏览）列完模型自作主张、把 100 行写成 1000+ 行、乱删注释后直言：**"All of this happens despite a few simple attempts to fix it via instructions in CLAUDE . md."** |

---

## 二、引用长文核心内容：《Graph Engineering with Claude》14 步路线图

> 原文标题：*Graph Engineering with Claude: 14-Step roadmap from 0 to graph architect (Full Course)*
> 作者：`@0xCodez`（2026-07-20，7,775,977 Views，15,507 Bookmarks）

### 核心问题：为什么单线 Agent 会撞墙？
9/10 的人构建多步 Agent 时写的是一条直线（Step 1 → Step 2 → Step 3），其中一半步骤根本不需要互相等待。单线排队不路由、不分支、不并行，所有东西塞进同一个上下文窗口，直到窗口塞满、Agent 彻底忘记自己在干什么。

Claude Code 的 **dynamic workflows** 让 Claude 直接编写普通 JavaScript 编排脚本，拉起协调的子 Agent 舰队（fleet），**编排层本身消耗 0 个模型 Token，因为它是代码而非对话**。

### 14 步架构清单

1. **01. Nodes are jobs. Edges are what flows.（节点是工作，边是流动的数据）**
   - 节点（Node）是一个有界的 `agent()` 调用（单输入、单输出、单一职责）。
   - 边（Edge）是数据依赖：只有当上一个节点的输出变量实际传入下一个节点的 prompt 时，边才存在。「总结文件，然后告诉我天气」之间没有边，不应串行等待。
2. **02. Your linear script is a degenerate graph（线性脚本是退化的图）**
   - `A → B → C → D` 没有冗余，C 卡住则 D 永远不跑。剪掉不传数据的假箭头，把窄链条压宽成「并行扇出 → 汇聚」。
3. **03. Give every node a contract（给每个节点一份契约）**
   - 显式传参（绝不假设共享上下文窗口），并用 JSON Schema 强制校验输出结构（在 tool-call 层校验，不匹配自动重试）：
   ```javascript
   const ITEM = {
     type: 'object', additionalProperties: false,
     properties: {
       title:  { type: 'string' },
       url:    { type: 'string' },
       impact: { type: 'string', enum: ['high', 'medium', 'low'] },
     },
     required: ['title', 'url', 'impact'],
   };
   const result = await agent(source.prompt, {
     label: `research:${source.key}`,
     schema: ITEM,
     agentType: 'general-purpose',
   });
   ```
4. **04. Treat the edge as a data contract（把边当成数据契约，别租 Agent 当水管工）**
   - 扇出与汇总之间的 `flatten`、`dedupe`、`filter` 全部用普通 JS 代码写（`results.flatMap(...)` + `Set`），确定性、零耗时、**0 Token**。
   - 原文金句：*"Save agents for judgment, not for plumbing. A graph where every edge is an agent is a graph paying rent on its own wiring."*
5. **05. Fan out with `parallel()`（用 `parallel()` 并发扇出）**
   - 传入 thunk 数组并发生成子 Agent。两个鲁棒细节：① 它是屏障（等待全员返回）；② 单个报错的 thunk 解析为 `null` 而非弄崩整批，下游用 `.filter(Boolean)` 过滤即可。主会话上下文永远不装 9 份原始材料，只收最终结果。
6. **06. Fan in at a barrier（在屏障处扇入）**
   - 只有真正需要全量上游结果一起处理的操作（跨源去重、按影响力全局排序、全空提前退出）才设 Barrier：
   ```javascript
   // The edge: plain JS, no agent, zero tokens.
   const flat = collected.flatMap((c) => c.items);
   log(`Collected ${flat.length} items`);

   phase('Curate');
   // The barrier node: needs the WHOLE set to dedupe + rank.
   const curated = await agent(
     `Dedupe and rank these by impact:\n${JSON.stringify(flat)}`,
     { phase: 'Curate', schema: CURATED_SCHEMA },
   );
   ```
7. **07. The diamond: split → work → merge（钻石拓扑：拆分 → 并行干活 → 合并）**
   - 标准范式：`fan out → reduce (plain code) → synthesize (final agent)`。适用于市场扫描、依赖审计、代码审查、研究报告。
8. **08. Route the edge at runtime with a conditional（运行时条件路由）**
   - 路由节点用 `agent()` 产出分类枚举（如 `severity: 'low' | 'high'`），分支跳转用 JS 的 `if/switch` 控制。判断靠模型，跳转靠确定性代码，杜绝「模型擅自跳过审计」。
9. **09. Put a verifier on the edge（在边上放验证器）**
   - 三种验证模式：
     - **Adversarial verify（对抗式验证）**：对每条发现派 N 个被提示去驳倒它的独立怀疑论者，多数存活才保留。
     - **Perspective-diverse verify（多视角验证）**：给每个验证器不同透镜——`correctness`（正确性）、`security`（安全性）、`repro`（可复现性），消除同质化盲区。
     - **Judge panel（评委团）**：多角度生成 N 份尝试，并行评委打分，以优胜者为主干嫁接亚军优点（Bun 运行时移植所用的真实模式）。
10. **10. Isolate nodes so one failure can't poison the graph（隔离节点防污染）**
    - 读操作靠 `.filter(Boolean)` 容忍局部缺失；**并行写文件时才启用 `worktree`（每个 Agent 跑在独立 git worktree 沙箱再合并）**，不作为只读任务的默认税。
11. **11. Add a cycle - but make it converge（加入可收敛回环：`loop-until-dry`）**
    - 未知规模的 Bug 排查：持续并发派 finder，直到连续 K 轮（如 `dry < 2`）没有新发现为止。
    - **核心防坑铁律**：**必须对着「所有见过的发现（`seen`）」去重，绝不能只对着「已确认的发现（`confirmed`）」去重**。否则上一轮被验证器毙掉的废案会在下一轮重新出现，循环永不跑干：
    ```javascript
    const seen = new Set(); const confirmed = []; let dry = 0;

    while (dry < 2) {                       // stop after 2 empty rounds
      const found = (await parallel(
        FINDERS.map((f) => () => agent(f.prompt, { schema: BUGS }))
      )).filter(Boolean).flatMap((r) => r.bugs);

      const fresh = found.filter((b) => !seen.has(key(b)));
      if (!fresh.length) { dry++; continue; } // nothing new → toward dry
      dry = 0;
      fresh.forEach((b) => seen.add(key(b))); // dedupe vs SEEN, not confirmed

      // diverse-lens verify each fresh finding before it counts
      const judged = await parallel(fresh.map((b) => () =>
        parallel(['correctness', 'security', 'repro'].map((lens) => () =>
          agent(`Judge "${b.desc}" via ${lens} — real?`, { schema: VERDICT })))
        .then((v) => ({ b, real: v.filter(Boolean).filter((x) => x.real).length >= 2 }))));

      confirmed.push(...judged.filter((v) => v.real).map((v) => v.b));
    }
    ```
12. **12. Tier the models across the nodes（跨节点模型分级）**
    - 子 Agent 默认继承当前会话模型。在扇出的重复性提取/分类节点显式指定便宜模型，把旗舰模型留给合并与裁决节点。
13. **13. Topology is your cost and latency（拓扑即成本与延迟：默认 `pipeline()`）**
    - `parallel()` 屏障会让所有快任务停下来等最慢的节点；`pipeline()` 让每个条目独立流过所有阶段（A 在阶段 3 时 B 在阶段 1）。除非需要跨集合去重/比较，否则默认用 `pipeline()`。
14. **14. Let Claude draw the graph - self-routing（自路由与 `.claude/workflows/` 版本控制）**
    - 提示词里说 `workflow`、运行内置 `/deep-research`（`scope → parallel search → fetch → adversarial verify → synthesize`），或开启 `ultracode`，跑通后按 `s` 存入 `.claude/workflows/` 入库复用。

---

## 三、关键信息与资源

| Type | Name | Link | Why it matters |
|---|---|---|---|
| X Post | `@0xMovez` 推文 | https://x.com/0xMovez/status/2119860140299997352 | 二手包装典型样本（截去组织名、4条拆6步、无依据 65%→94%） |
| X Article | `@0xCodez` 14步图工程 | https://x.com/0xCodez/status/2079165300625330317 | 777.6万浏览长文，系统讲透 Node/Edge/Schema/Verifier/Loop-until-dry |
| X Post | `@karpathy` Claude 编码随笔 | https://x.com/karpathy/status/2015883857489522876 | 786.7万浏览一手源头，提出 Declarative Leverage、Atrophy 与 Slopacolypse |
| GitHub Repo | `multica-ai/andrej-karpathy-skills` | https://github.com/multica-ai/andrej-karpathy-skills | 231,621 Stars，65行 `CLAUDE.md` 四条原则与 `EXAMPLES.md` 正反例 |

---

## 四、我的吸收判断

- **可复用能力**：
  1. **`loop-until-dry` 对 `seen` 而非 `confirmed` 去重**：在我们自己的多轮核查或 Bug 扫描脚本里，被 Verifier 驳回的条目必须记入 `seen` 黑名单，防止下一轮 Agent 重复提报同一假阳性。
  2. **三透镜独立投票（`correctness` / `security` / `repro`）**：比派 3 个相同 prompt 的审查员更能抓出盲区。
  3. **0 Token 代码边（Plumbing in Code, Judgment in Nodes）**：完全契合 Hermes `execute_code` + `delegate_task(output_schema=...)` 的设计哲学。
- **对个人 IP（翡冷翠）的价值**：
  - 极佳的「多源对账深潜体」标杆案例：把「营销号吹 94% 准确率」与「Karpathy 原帖说写进 `CLAUDE.md` 照样犯病」并置，再用 14 步图工程给出真正的结构化解法，完美落地「不用学写代码，学会像产品经理一样指挥 AI（说清需求、拆成步骤、验收结果）」。

---

*来自翡冷翠*
