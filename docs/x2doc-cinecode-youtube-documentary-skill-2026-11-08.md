# cinecode：用代码写成的电影、YouTube 长纪录片与运动设计 Agent Skill - X2Doc 整理 & 视频落地分析

> 来源：https://x.com/sarpstar/status/2119082994925211686 （@sarpstar，仓库署名 Sarp Yıldız，2026-11-07）
> GitHub 仓库：https://github.com/sarpstar/cinecode （MIT License，2026-11-08 实时 762 stars / 130 forks，commit `67f9807`）
> 本地浅克隆路径：`/Users/marovole/Workspace/playground/cinecode`
> 整理时间：2026-11-08
> 来自翡冷翠

---

## TL;DR

- **它是什么**：`sarpstar/cinecode` 是土耳其电影制作人 Sarp Yıldız (@sarpstar) 开源的一套面向 Claude Code / Cursor 的代码出片 Agent Skill（MIT 协议，内置完整简体中文文档 `README.zh-CN.md`）。它通过无头 Chrome 逐帧渲染 `Canvas 2D` 或 `three.js + pmndrs/postprocessing` 场景，搭配多轨混音与 `-14 LUFS` 母带处理，端到端产出 15 秒短片到 10 分钟以上的 YouTube 纪录片 MP4。
- **它是「15+ 个开源代码视频 Skill 的集大成缝合怪」**：作者在致谢中明确列出，它把 `lemomo-ai/lemo-opuscar` 的 51 套风格配方（加 7 套自有共 58 套）、`charlie947/motion-graphics-skills` 的 `vox-explainer` 纸面调查纪录片语法、`tuzhechen2005/opus-video-skills` 的节拍网格、`howseen-ai/claude-motion-design` 的剪辑接缝与盲审测试、`blader/humanizer` 的去 AI 味词检、`sgossner/VCSL` & `VSCO-2-CE` 的 CC0 真实乐器采样、`Kenney` 的 CC0 音效库整合进了一套零 npm 依赖的 Python + Node 工具链。
- **原帖百慕大纪录片实盘验尸（7分51秒成片实测）**：作者自述“睡前对 cinecode 说『你做决定』，一觉醒来拿到 8 分钟几乎成品的百慕大纪录片，仅 1 轮修改定稿”。我们对原帖附带的 `471.5s`（24fps，11,315 帧）成片跑了它自带的 `qc.py` 与 `scene_check.py` 实测：**首 2 秒运动能量 `mean=1.09`（PASS）**；**去摄影机运动后的主体残差 `1.22–6.52`（8 个 1 分钟段落全 PASS，非死图推镜）**；抽帧接触表（24 张静帧）可见冷峻海洋 3D 水面雾气 + 1945 年美国海军调查报告高亮缩进 + 佛罗里达航线矢量海图 + 1893 航海日志与 1964 实体书脊特写 + 英土双语上下叠放字幕。
- **与我们现有栈的取舍结论（借件不换栈，立 IP 不追热点）**：**绝不要用它替换我们已跑通的 `long-form-ai-explainer-film` 或 `xilo-opus-video`，更不要跟风去做百慕大/超自然未解之谜泛流量号，甚至不要去做第三人称“硅谷巨头暗战/科技史说书”的博主**（那种内容没有“你是谁”，立不住个人 IP）。但它的 **5 个独立脚本与机制** 可以直接拿来武装我们的**第一人称工程与 FDE 实战纪实（做自己）**：
  1. **`scene_check.py action`（去运镜主体动作残差检测）**：算出扣掉平移/缩放后的画面真实变化，专治“光靠 Zoom-in 假装画面在动”；
  2. **`styles/vox-explainer.md` + `craft.md` §8（UI Hero Shots）**：不拿来拼贴维基百科老照片，而是用来**高亮展示你自己的真实账单、Git Commit、排障日志与 3D 倾斜暗场终端界面**，把一线实战过程拍出电影级调查质感；
  3. **`voice_treat.py`（旁白介质与空间声学卷积）**：拒绝干瘪原始 TTS 和端着的播音腔，用 `close` + `room` 把人声处理成温暖贴耳的“深夜书桌复盘感”；
  4. **`writing.md` §13–16（长片的「好奇心地图 Curiosity Map」+ `words_check.py` 禁破折号与 AI 套话门禁）**：用来组织你解决真实业务难题时的悬念与踩坑反转；
  5. **`asset_search.py supply`（11 个开放档案/图库源库存探针 + 自动 `LICENSES.csv`）**：仅在需要引用外部原始论文/标准文献作证时作为辅助探针。

---

## 一、 原帖核心内容与作者背景还原

### 1.1 原帖正文翻译（@sarpstar，2026-11-07）

> 如果你一直想开一个 YouTube 频道却迟迟没动手，这条帖子会是你的解药。
>
> 我本周分享的 `cinecode` skill 完全免费且开源。只需要你有 Claude 订阅，不用花钱买到处兜售的卖课教程，也不用订阅那些把同样功能包装起来收费的 SaaS 平台，你就能把频道开起来。
>
> 下面这条**百慕大纪录片（Bermuda belgeseli，实长 7分51秒）**，我是昨晚睡觉前对 cinecode 说了一句“你来做决定”然后去睡的。早上醒来看到交付报告：一条 8 分钟、几乎已经是最终版的视频。至于你们现在看到的成片，只是我把想改的地方详细写出来、经过**唯一一轮修改（single revision）**就出来的版本。写下这些话时我真心感到自豪，几周前我根本不敢想象能说出这种话。
>
> 它到底做了什么？**从你的一个点子出发编写剧本、用代码生成场景、在需要真实画面时扫描开放图库与历史档案馆抓取素材、用动态图形（Motion Design）搭建视觉钩子、加入开源音效和配乐，一路推进到最终剪辑成片。**
>
> 说真的，这个 skill 真的成了，不是噱头。去折腾它、熟悉它，你们肯定能做出比我更好的片子。不买相机、不露脸、不雇剪辑师开频道早就不是新鲜事；但现在，**不需要任何其他工具（başka hiçbir araca ihtiyaç duymadan），只靠 Claude 或你顺手的 AI 工具就能搞定**。只要你肯花心思投入精力，手里就有了一件能产出达到开号质量作品的武器。
>
> 请允许我也去开自己的频道了；要是不把你们全都变成我的竞争对手，我心里可过意不去。接下来就是选一个趋势话题和正确的细分赛道（Niche），跑通受市场欢迎的固定格式（Format）后进入批量化生产。也许我会先从像百慕大这样讲超自然/未解之谜的频道做起。
>
> 我会暂时放下 `cinecode` 的功能开发，它现在的状态已经绰绰有余。有新点子我会先记下来，手痒了再回来更。仓库和安装方法在首条评论，今晚就选好你的选题，我们 YouTube 见。

### 1.2 定位与样本说明（Caveat）

- **单样本自述偏差**：作者展示了 1 条 7 分 51 秒的百慕大纪录片成品（推文获 186,477 浏览、4,460 收藏、1,726 点赞），“睡一觉自动出 8 分钟初稿 + 1 轮修改定稿”属于作者对自己开发的工具在极熟悉状态下的单次最佳展示（Survivorship Bias），未披露该片在 Claude Code 中实际消耗的上下文轮次、子代理重启次数及失败废片率。
- **实际运行实测数据**：我们拉取了原帖 `480×270`（270p）视频流并跑完 `qc.py`、`scene_check.py` 及 20 秒一帧的接触表抽检，证实成片绝非粗制滥造的 PPT，而是具备完整电影感调色（青灰冷调海面 + 胶片颗粒）、真实历史档案（画面展示 1945 年美国海军调查报告原文高亮、1893 航海日志、Vincent Gaddis 1964 年《Argosy》封面/书脊特写）与矢量航线图的成熟混合纪录片。

---

## 二、 关键信息与生态基因表

`cinecode` 之所以一出手就极其完善，是因为作者系统性地把过去两个月 GitHub 上最火的 15+ 个代码动画/视频 Agent Skill 全部拆解重写并融为一炉：

| 模块类型 | 名称 / 脚本 | 来源或致谢基因 | 核心作用与为什么重要 |
|---|---|---|---|
| **核心仓库** | `sarpstar/cinecode` | Sarp Yıldız (@sarpstar), MIT | 主工程，含 Quick Mode（单文件 `film.html`）与 Film Mode（6 步门禁 + `three.js`） |
| **风格配方库** | `styles/` (58 套) | 51 套引自 `lemomo-ai/lemo-opuscar` + 7 套自有 | 覆盖 `vox-explainer`、`archive-lighttable`、`halftone-dossier`、`lidar-survey`、`teardown` 等 |
| **纪录片调查风** | `styles/vox-explainer.md` | 吸收 `charlie947/motion-graphics-skills` | 桌面撕边卡片、马克笔自绘圈重点、荧光笔划原件、计数器、地图航线 |
| **开放档案检索** | `scripts/asset_search.py` | 原创（零浏览器，纯官方 API） | 一键并发搜 Wikimedia、Internet Archive、Met、Cleveland、AIC、Rijksmuseum、Openverse、NASA、Poly Haven、Pixabay、FilmGrab 共 11 个源，下载即写 `LICENSES.csv` |
| **去运镜动作检查** | `scripts/scene_check.py` | 原创（中心加权网格配准） | 搜索最佳平移 `(dx, dy)` 与缩放 `s` 并扣除，计算画面真实主体运动残差，拦住“纯推拉死图” |
| **声学介质处理** | `scripts/voice_treat.py` | 原创（FFmpeg 滤镜链 + IR 卷积） | 将干声处理为 `close` / `tape` / `radio` / `phone` / `chorus` 等 10 种介质 × 5 种空间，支持 `--imprint` 卷积影片标志音并统一对齐 `-20 LUFS` |
| **去 AI 味词检** | `scripts/words_check.py` | 吸收 `blader/humanizer` + 维基百科 AI 写作特征 | **硬拦截破折号（`—` / `--`）**，扫描 `"not X but Y"`、`"imagine"`、`"at its core"`、三连排比等 AI 腔 |
| **参考视频扒谱** | `scripts/ref_video.py` | 原创 | 丢入任意参考视频，自动测量镜头切点、平均镜长、色板、光比、BPM 与踩点率，生成 `REFERENCE.md` |
| **口播粗剪提纯** | `scripts/footage_cut.py` | 吸收 `nateherkai/herk-edit-kit` | 基于 Whisper 词级时间戳自动缩减 >0.55s 气口，自动揪出结巴（Stutter）和重录（Retake）生成 `flags.md` 供人批阅 |
| **真实乐器与音效** | `samples.py` + `sounds.py` | `Vincentwei1021/mg-styles-15` (VCSL/VSCO-2) + `Kenney` | `samples.py list` 列出 87 个 CC0 真实乐器档位（底层 `CATALOG` 74 项）按需拉取 + Kenney CC0 拟音库（525 个音效：翻页、木头、玻璃、脚步等） |
| **上下文守卫** | `scripts/guard.py` + `hook.cjs` | Claude Code Hooks (`PreToolUse` / `Stop`) | 强行拦截超过 1.2MP 大图进上下文、子代理超 25 步强停、未展示剧本先提问强停、160K/260K token 提醒换会话 |

---

## 三、 结合我们现有产线的深度评估（External Engine Fit）

按照「外部引擎适配评估规范」，我们在本机（M2 Max MBP）完成了浅克隆、依赖探针、231 项单元测试与样片门禁实跑：

### 3.1 本机环境与门禁实测结果

1. **前置依赖实测**：
   - `node` (`v22.22.3` ≥ 22)、`python3` (`3.9.6`)、`ffmpeg` (`9.0.2`，支持 `h264_videotoolbox`)、Google Chrome 全部就绪。
   - GPU 探针实测：`node scripts/capture.mjs --url starter/index.html --probe` 返回 `renderer: ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Max)`，`1920x1080, 144 frames @ 24 fps` 硬件加速正常。
2. **自带单元测试实测**：
   - 运行 `python3 -m unittest discover -s tests`：**231 个测试用例全部通过（`OK, skipped=21`）**。
3. **原帖百慕大纪录片实跑门禁输出**：
   - `qc.py hook`：`steps=47 mean=1.09 min=0.127 first_step=0.133 -> PASS`（首帧即有云海与轰炸机编队运动）。
   - `scene_check.py action --every 60 --fps 1`：8 个一分钟段落残差分别为 `6.52, 1.90, 1.63, 1.74, 1.97, 1.22, 3.54, 1.48`，**`0 scene(s) flagged`**。
   - `scene_check.py sound --every 60`：8 个段落响度介于 `-15.9` 至 `-18.6 LUFS`（X 平台二次转码后电平），高频刺耳度（2–5 kHz）介于 `-14.5` 至 `-19.0 dB`，**`0 scene(s) flagged`**。

### 3.2 形态映射表（Cinecode 支持形态 vs 我们的内容矩阵）

| 引擎形态 | 画布与底层技术 | 视觉语法 | 对应我们哪条线 / 哪类选题（以打造个人 IP 为唯一准则） |
|---|---|---|---|
| **Film Mode · Documentary（长纪录片）** | `1920×1080` (`three.js` + `Canvas 2D` + 自有终端日志/账单原件/实测序列帧) | 真实账单与日志原件高亮 (`Document zoom`) + 3D 倾斜暗场界面 (`UI Hero Shot`) + 计数器 (`Counter`) | **YouTube 个人主频道（第一人称工程与 FDE 实战纪实）**：我自己在非技术公司落地 AI 的真实翻车与重构、真金白银亿级 Token 账单审计、跨模型路由实战复盘 |
| **Quick Mode · Explainer（实测/复盘短片）** | `1920×1080` 或 `1080×1920`（单文件 `film.html` + Web Audio 离线合成） | `vox-explainer`（桌面研究卷宗）、`archive-lighttable`（灯箱）、`halftone-dossier`、`teardown` | **个人号第一人称 AI 实测对比 / 踩坑切片**（1–3 分钟，X / 视频号 / B站 / YouTube Shorts） |
| **Ad & Product（产品/UI 主视觉片）** | `16:9` + `9:16` + `1:1` 三端同出 | **UI Hero Shot**（真实软件界面倾斜 30–50° 置于暗场，景深移焦，聚光灯滞后 0.4s 跟随操作） | **自有开源 Skill 演示视频 / 出海工具站实机演示 / 社群实战案例展示** |
| **Footage Edit（口播/录屏精剪）** | 任意画幅（Whisper 词级切气口 + 去重录 + 词同步图层） | 自动剪掉 >0.55s 停顿与口误重录，在说出关键词前 `0.2–0.6s` 弹出信息卡 | **FDE 带同事用 AI 的真实工作流实录 / 个人实操录屏复盘** |

### 3.3 与我们现有视频工具链的取舍表（谁强·怎么配合）

| 维度 | 我们现有管线 (`long-form-ai-explainer-film` + `Papermorph` + `xilo` + `science-video-daily`) | `sarpstar/cinecode` | 结论：谁更强 / 怎么配合 |
|---|---|---|---|
| **事实核查与防幻觉** | **极强**：`grounding.py` 原文落盘 + 子串精确匹配 `facts.json` `[Fxx]` + 双模型（Gemini + DeepSeek）盲审 + 独立 Subagent 逐句核查 | 较弱：虽规定写 `research/facts.md`，但无强制子串比对脚本，靠 Agent 自觉 | **严守我们现有的 `grounding.py` + `facts.json` 铁律**，绝不用 cinecode 的松散事实表替代 |
| **声画同步精度** | **极强**：ElevenLabs `eleven_v4` 字级时间戳 + `U.at('word')` / Papermorph `[[mark]]` 词级锚点 | 中等：按整句 WAV 测时长排 `shots.json`（除非装 Whisper 跑字幕对齐） | **继续用我们的 ElevenLabs `with-timestamps` 字级对齐** |
| **开放档案检索与版权台账** | `Papermorph` 仅有 `commons.py`（只搜 Wikimedia） | **极强**：`asset_search.py` 并发搜 11 个博物馆/档案馆/视频库，且有 `supply` 20 秒库存探针，自动写 `LICENSES.csv` 和简介致谢 | **直接引入 `asset_search.py`** 作为我们做 YouTube 纪录片的标准找素材工具 |
| **3D 氛围与后期电影感** | 以 2D Canvas / SVG 纸面与水墨为主 | **极强**：内置 `three.js` + `pmndrs/postprocessing`（AgX/ACES 影调、景深、体积雾、胶片颗粒、片门抖动）+ 58 套风格配方 | 当纪录片需要 **3D 海面/地形/建筑微缩景观** 或 **UI 3D 倾斜暗场特写** 时，借用 `starter/looks.mjs` 与 `finish.md` |
| **声音设计与人声质感** | BGM 闪避 + 简单合成音效，人声为 ElevenLabs 原声 | **极强**：`voice_treat.py`（10 种介质×5 种空间+标志音卷积）+ `sounds.py`（Kenney CC0 真实拟音，525 个音效）+ `samples.py`（`list` 87 个 CC0 乐器档位）+ 声音事件审计表 `sound-audit.md` | **核心吸收项**：把 `voice_treat.py` 和 `sounds.py` 接入我们的长片管线，彻底告别“干瘪 AI 读书声” |
| **画面死图与AI套话质检** | `gates.py`（仅 1080×1920）+ 抽帧人工/模型看 | **极强**：`scene_check.py action`（扣掉运镜测真实主体运动）、`words_check.py`（抓破折号和英文 AI 套话）、`qc.py sceneloud`（逐景测 2–5kHz 刺耳度） | **直接复用这 3 个脚本** 作为 YouTube 英文长片渲染后的机器门禁 |

### 3.4 中文落地必改项（若用于中文视频）

如果用 `cinecode` 制作中文版（B站长视频 / 视频号 / 抖音），原版模板有 4 处水土不服必须改：

| 项 | 病灶 | 改法 |
|---|---|---|
| **1. 字体加载 (`fonts.py` & `type.mjs`)** | 默认从 Fontsource 拉取包含土耳其语 `latin-ext`（`İĞÜŞÖÇ`）的拉丁字体，无中文字形 | 在 `TYPE` 配置与 CSS 中显式加入本地中文字体回退（`"PingFang SC", "Songti SC", "Noto Sans CJK SC"`），不要调 `fonts.py` 的 `latin-ext` 校验 |
| **2. 配音引擎 (`tts.py`)** | 默认调 Gemini TTS (`gemini-3.8-flash-tts`)、ElevenLabs (`eleven_v3`) 或土耳其语离线模型 `EMA Lightning`，且不输出字级时间戳 | YouTube 英文片继续用我们验证过的 ElevenLabs `eleven_v4` (`with-timestamps`)；中文片走我们的 `narrate.py` |
| **3. 剧本词检与字数预算 (`words_check.py`)** | 按英文词数算预算（110–140 词/分钟，每行 ≤9 词），且只扫英文/土耳其语陈词滥调 | 中文按 **220–260 字/分钟** 核算；保留它的“禁破折号 `—`”规则，补充中文 AI 套话词表（“不仅…更是…”、“在这场…的背后”、“让我们一起”） |
| **4. 竖屏画幅** | 竖屏默认 `9:16` (`1080×1920`) | 抖音/视频号 `2:3` (`1080×1620`) 继续走我们的 `science-video-daily` 管线，不套 `cinecode` |

### 3.5 三栏成本账本（拆穿“免费”表象）

| 成本维度 | 费用明细 | 真实评估 |
|---|---|---|
| **1. 外部 API（TTS / 素材 / 生图）** | 素材检索（Wikimedia / Archive / 博物馆）`$0`；音效与乐器采样（Kenney / VCSL CC0）`$0`；Pixabay 视频/图片 `$0`（需免费 Key）；旁白用 Gemini 免费额度 `$0`（但每天限约 10 次请求，长片必超）或 ElevenLabs 约 **`$0.70–$1.20 / 10分钟长片`** | 外部 API 极便宜，几乎只花一顿早饭钱的配音费 |
| **2. 本地渲染（GPU / CPU 时间）** | M2 Max 无头 Chrome 硬件加速渲染 + FFmpeg 编码：**`$0`**（8 分钟长片草稿+成片约 15–30 分钟机器时间，占用几 GB 磁盘） | 完全免费 |
| **3. LLM Token（真正大头）** | 作者在 `context-protocol.md` §6 中披露了真实负载（Load）：1 个 30 秒 Quick 短片定义为 `1.0 Load`（约 100–250 步工具调用）；**一部多分钟的 Film Mode 纪录片消耗 `10–17 Load`**。即便用了 `guard.py` 限制大图和 25 步子代理，一部 8–12 分钟纪录片仍需消耗数百万至上千万级缓存读取 + 推理 Token（折合 API 价约 **`$15–$35 / 部`**，或重度消耗 Claude Max / Devin / Codex Pro 订阅额度） | **绝非零成本**。必须在有包月高额订阅（Claude Pro/Max、Codex Pro）的前提下跑，且必须遵守它的 `STATE.md` 分段换会话机制 |

---

## 四、 核心命题回应：「用个人 IP 原则（做自己，不追热点）审视 YouTube 纪录片起号」

你明确了核心原则：**“博主是追热点的，总是想着流量；但是 IP 是做自己。我们做内容后续都是打造 IP。”** 用这条铁律重新审视 YouTube 纪录片起号，结论非常清晰：

### 4.1 战略红线：砍掉无面孔的「第三人称说书博主」模式，只拍「第一人称实战纪实（Skin in the Game）」

1. **为什么既不做“百慕大猎奇”，也绝不做“硅谷巨头秘史/科技史说书”？**
   - 作者提到的“百慕大三角/超自然事件”是纯泛流量猎奇，受众与我们的变现漏斗 0 交集。
   - 更具迷惑性的是模仿 *ColdFusion / MagnatesMedia* 去做《2017 Transformer 备忘录秘史》或《AI 巨头暗战》——**这依然是典型的「博主思维」**。因为这类题材跟“你是谁”毫无关系，任何一个没上过班的学生用 `cinecode` 抓维基百科都能批量生成。观众看完记住的是故事本身，不是你；你只是一个没有面孔的说书工具人（Faceless Channel），根本立不住个人 IP。
2. **什么是真正立得住的个人 IP 纪录片？**
   - 别人用 `cinecode` 可以一键复制你的视觉配方，但**抄不走你在非技术公司当 12 年 PM + AI 全栈兼 FDE 的真实排障日志、抄不走你真金白银烧出来的账单、也抄不走你带非技术同事落地 AI 时的思考过程**。
   - **✅ 我们的唯一打法（First-Person Engineering & FDE Chronicles）**：用 `cinecode` 的调查纪录片视觉与声学外壳（`vox-explainer` 桌面卷宗 + 荧光笔高亮原件 + 3D 倾斜暗场终端界面 + 贴耳书房人声），去拍**你自己亲手干过的事（I / We），而不是别人的八卦（They）**。

### 4.2 哪些母题真正属于「做自己」的第一人称纪实？

不再为了蹭搜索词去硬编自己没体感的话题，也不为了“凑周更”去套模板灌水，只从你的真实战场里取材：

1. **母题方向 A：FDE 一线落地与翻车纪实（全网独一份的非技术公司实战视角）**
   - 拍你在非技术公司推广 Codex / Claude Code / Hermes、带非技术同事用 AI 提效的真实过程：原本业务卡在哪 → 你怎么设计工作流 → 实际上线后哪里崩了 → 怎么修好并沉淀成开源 Skill 的。
2. **母题方向 B：真金白银的账单审计与架构复盘（晒自己的真账本）**
   - 直接摊开你自己的 `ccusage` / Factory 亿级 Token 真实账单、97% 缓存占比测算、跨模型兜底路由（GPT → Grok → DeepSeek）与代理排障实录。讲清楚**你遇到了什么问题、算出了什么反直觉结论、最后怎么改架构的**。

---

## 五、 立刻可借的 5 个工程机制（技术为「真实自我」服务）

我们不需要把工作流切到 `cinecode` 繁琐的交互问答模式，而是把 `/Users/marovole/Workspace/playground/cinecode/scripts/` 当作本地工具箱，用来高质感地呈现你的真实工作现场：

### 1. 借 `styles/vox-explainer.md` 与 `craft.md` §8（UI Hero Shots）呈现「自有实战证据」
我们的“历史档案馆”不是博物馆老照片，而是**你自己的 Git Commit、终端报错日志、`ccusage` 账单原件与 Obsidian 架构笔记**：
- **晒账单/日志/代码原件时**：按 `vox-explainer.md` 规范，放在暖米色/暗色研究桌面上，用黄色荧光笔从左到右动态划出关键数据行；
- **晒终端/工具实操时**：按 `craft.md` §8 的 **UI Hero Shot** 规范，不再放平铺直叙的全屏录屏，而是把你的真实界面置于暗色 3D 空间中倾斜 `30–50°`、旋转 `10–20°`，加上浅景深移焦（只让当前操作的 2–4 行代码清晰）和滞后 `0.3s` 的跟随柔光。

### 2. 借 `voice_treat.py` 打造「深夜书房跟朋友复盘」的贴耳人声
拒绝端着的播音腔和干瘪的原始 TTS。在 `narrate.py` 生成语音后、混音前加一步：
```bash
python3 /Users/marovole/Workspace/playground/cinecode/scripts/voice_treat.py apply \
  assets/audio/ch*.mp3 --medium close --space room --target -18 --out assets/audio/treated
```
- 全片主叙事固定用 `--medium close --space room`（温暖贴耳的书桌交谈感，传递一线实战者的真诚与冷静）；
- 搭配 `Kenney` CC0 真实物理音效（翻页、马克笔划重点、机械键盘敲击），让观众感觉就坐在你工位旁边看你拆解问题。

### 3. 借 `writing.md` §13 的「好奇心地图（Curiosity Map）」组织第一人称复盘叙事
把你自己踩坑和破局的过程拍出悬疑感，写剧本前先列 **Curiosity Map 表**：
- **0–5 秒（Pattern Break）**：第一帧直接亮出你在实战中撞上的真实反直觉结果或翻车现场（禁黑场淡入，首 2 秒必须有画面动作）；
- **5–30 秒（The Promise）**：用第一人称明确告诉观众，接下来几分钟我会摊开哪份真实日志/账单，带你复盘我是怎么解决这个真问题的；
- **每 60–90 秒一个排查闭环**：顺着你当时真实的排查思路（假设 1 失败 → 抓包/查日志发现盲点 → 最终解法），同时最多保持 2 个悬念，绝不堆砌枯燥的背景百科。

### 4. 借 `scene_check.py` + `words_check.py` 当成片交付门禁
在长片渲染出 MP4 后、发给你审片前，固定跑两道脚本：
1. `python3 /Users/marovole/Workspace/playground/cinecode/scripts/words_check.py`：消灭剧本和字幕里所有的破折号（`—`）和 AI 味套话（`\"not X but Y\"`, `\"in a world where\"`, `\"at its core\"`），确保台词像真人说话。
2. `python3 /Users/marovole/Workspace/playground/cinecode/scripts/scene_check.py action <film.mp4> --every 15`：自动揪出哪一段画面“只有摄影机在缓慢推拉，画面主体根本没动”，在交付前重做该镜头。

### 5. 借 `asset_search.py` 仅作外部论文/原始文献的辅助探针
不拿它去拼凑公共历史故事；只在你复盘自己的技术方案、需要顺带引用某篇原始论文或官方文档作对比时，用 `asset_search.py supply` 快速抓取合规原件并生成 `LICENSES.csv`。

---

## 六、 可执行下一步（低成本验证方案）

不改写现有主力 Skill，也不搞“为了周更硬凑选题”，分三步跑出第一条真正立住你个人 IP 的实战纪实样片：

- [ ] **Step 1（从你真正干过的事里挑 1 个首发母题）**：完全基于你现有的独家实战沉淀二选一——
  1. **母题 A（FDE 一线改造纪实）**：复盘你在非技术公司带同事落地 AI 工作流的真实案例（原本怎么卡壳 → 你怎么设计 Agent/Skill → 哪些地方翻车了 → 最终怎么跑通）。
  2. **母题 B（重度 AI 工程师的真实账单与路由架构）**：直接摊开你自己的 `ccusage` / Factory 亿级 Token 真实账单与 97% 缓存率实测，复盘你是怎么算清真账并搭起跨模型兜底架构的。
- [ ] **Step 2（90 秒第一人称纪实 Pilot 试跑）**：把该事件里你真实的终端截图、账单、Git 记录归档为证据库；借用 `cinecode` 的 **`vox-explainer` 原件高亮 + `UI Hero Shot` 3D 暗场终端特写 + `voice_treat.py`（`close/room` 书桌旁白）+ `Kenney` 拟音**，渲染出前 **90 秒（Cold Open + 第一幕）** 的 1080p 样片，并跑通 `qc.py` 与 `scene_check.py` 全 PASS 报告发你审看。
- [ ] **Step 3（有真仗打完再出片，宁缺毋滥）**：样片质感跑通后，把这套视觉与声音参数固化下来。后续每当你在工作或副业中真正打赢一仗、踩实一个坑、写出一个新 Skill，就用这套纪实语言把它拍成个人 IP 作品（同步切出竖屏切片与公众号长文），绝不为了博流量去做跟自己无关的热点题。

---

*来自翡冷翠*
