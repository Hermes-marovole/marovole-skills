# creator-generalist：把 ~1,000 个 YouTube 制作教程蒸馏成 2D/3D 全能 Agent Skill 套件 - X2Doc 整理与引擎适配评估

> 推荐帖来源：https://x.com/BeyondTheBoxCN/status/2119808480098046168 （@BeyondTheBoxCN 黑箱之外，2026-11-09）
> 原作者与首发视频来源：https://x.com/anxuanng/status/2119507831024123908 （An Xuan @anxuanng，2026-11-08）
> 开源仓库：https://github.com/codepawl/creator-generalist （MIT License，2026-11-09 实时 22 stars / 0 forks，实测 commit：`85bb905d78802935a5643231b0836e1fb1b85c30`）
> 关联 3D 引擎仓库：https://github.com/codepawl/67.js （315 stars / 16 forks，作者自研的 AI Agent 驱动 3D 引擎）
> 本地只读浅克隆路径：`/Users/marovole/Workspace/playground/creator-generalist`
> 整理时间：2026-11-09
> 来自翡冷翠

---

## TL;DR

- **它是什么**：`codepawl/creator-generalist` 是作者 An Xuan (`@anxuanng`) 开源的一套跨工具 2D + 3D 创作 Agent Skill 套件（MIT 协议，支持 Claude Code、Codex、Cursor、Gemini CLI、OpenCode）。作者让 AI 观看并拆解了约 1,000 个 YouTube 专业制作教程，将其蒸馏为 **4 个插件、14 个 Skill 文件夹（12 个功能 Skill + `/3dg` 与 `/2dg` 两个入口命令）、124 份 `references/*.md` 工艺手册与 59 个自动化及测试脚本（`scripts/` 下 56 个文件 + `tests/` 下 4 个测试文件，含 1 份词表 `vocabulary.txt`）**。
- **核心架构与杀手锏**：
  1. **双主控 + 工艺/工具分层**：`3d-generalist`（覆盖 Blender 5.x、Three.js、67js 的 3D 剖面短片、叙事短片、角色建模绑定与场景搭建）与 `2d-generalist`（Vox / Johnny Harris 风格动态地图、真比例尺时间轴、档案拼贴）作为主入口，按需调用 `model-characters`、`rig-characters`、`sculpt-models`、`animate-characters`、`use-3d-software`、`edit-video`、`design-sound` 等底层技能。
  2. **教程自我进化流水线（`watch-video`）**：这正是它“看 1,000 个教程学手艺”的母机——自动抓取 YouTube 频道字幕与免费工程资源，抽帧跑 PP-OCRv6 读软件参数，并用 `check_blender_names.py` 对照本机导出的 `blender-names.json`（Blender 5.2 节点/修改器字典）校验老教程中已改名的节点（如把 Blender 2.8–4.x 的 `Mix RGB` 修正为 5.x 的 `Mix (Color)`），最后让干净 Worker 盲跑 3 个核心技法与原视频成片帧同屏比对。
  3. **去 AI 塑料感（Anti-Slop）的硬门禁**：3D 端用 `check_contact_and_slip.mjs` 按 30fps 逐帧扫描模型悬空（>2.5cm）、滑步（>0.25m/s）、瞬移（>0.30m/帧）；2D 端用 `check_render.py` 检查纯白/纯黑死帧、超过 1.5s 的画面静止（Dead air）、以及 `-14 ±1.5 LUFS` 响度与 `-1.0 dBTP` 真峰值；声音端用 `mix.py` 做 1–4kHz 频段动态避让（TrackSpacer 思路）、150Hz 以下手机扬声器谐波补偿（`phone_bass`）与 AAC/Opus 有损编码防爆音回测。
- **首发 27 秒 Showreel 成片实盘反测（用它自己的门禁测它自己的片）**：我们下载了原帖 `1920×1080`（30fps，27.05s，811 帧）Showreel 原片并直接运行其自带的 `check_render.py`：
  - **通过项（6/7 PASS）**：无纯白/纯黑死帧（PASS）、音频存在（PASS）、集成响度 **`-14.2 LUFS`**（精准落在 `-14 ±1.5 LUFS` 目标内，PASS）、真峰值 **`-1.3 dBTP`**（≤ `-1.0 dB` 门限，PASS）、无超过 0.4s 的静音断口（最长静音 `0.0s`，50ms 步长 RMS 扫描证实全片在 `-11.0` 至 `-43.2 dBFS` 间平滑收尾，PASS）。
  - **抓出的 1 项 FAIL（恰恰验证门禁有效）**：`FAIL no hold over 1.5 s`——脚本精准抓出 **`10.97s` 处存在长达 `2.33s` 的画面静止**（抽帧核对证实：该段为 `11s–13s` 展示的丝绸之路 2D 地图卡片，路线画完后画面定格了 2.33 秒，触发了它自己设定的 1.5s Dead Air 拦截线）。
- **对我们现有产线的取舍结论（借件不换栈，借形态不借赛道）**：
  - **不整套替换现有管线**：我们已有跑通的 `xilo-opus-video`、`papermorph-book-film`、`blender-3d-scene-video` 及昨日刚评估吸收的 `sarpstar/cinecode`；且该仓库脚本存在多处 Windows/Linux 环境硬编码（如 `check_vox_toolchain.py` 只扫 `C:\Program Files` 把本机已装的 `Blender 5.2.3 LTS` 误报为未安装；`perceive.py` 强依赖本机 Homebrew 默认未编译的 FFmpeg `drawtext` 滤镜导致 6 项测试报错）。
  - **不借泛科普赛道**：它内置的 `@BarelyInvented` 式“挖坑建地堡/修水磨坊”泛 3D 科普或中世纪地图，与我们个人 IP（12 年 PM + AI 全栈 + FDE 一线实战纪实）及公司线（灵知 AI 家庭精准营养）变现漏斗无交集。
  - **精准借 4 件高价值资产**：① **`watch-video` 的「YouTube 教程频道 → 校验级 Skill 蒸馏流水线」**（用于我们自己批量吃透海外专业课程/评测频道）；② **`3d-generalist` 的 `check_contact_and_slip.mjs` + `cutaway` 剖面叙事语法**（用于营养/生理机制 3D 剖面或系统架构拆解）；③ **`design-sound` 的 `mix.py` 频谱级动态避让（Unmask）与 `phone_bass` 手机低音补偿 + AAC/Opus 解码真峰值回测**；④ **`technique-atlas.md`（症状→专业技法速查表）与 `vox-modern-measured.md`（2026 实测版 Vox 极简静帧规范）**。

---

## 一、 原帖与首发帖核心内容还原

### 1.1 中文推荐帖（@BeyondTheBoxCN 黑箱之外，2026-11-09）

> 有人让 AI 学习了大约 1,000 个 YouTube 制作教程，然后把学到的方法整理成了一套开源 Skill。
>
> 现在，Claude Code、Codex 这些原本擅长写代码的 AI Agent，也能用它来制作 3D 模型、角色动画、游戏场景，甚至二维科普视频。
>
> 作者 An Xuan 把这个项目叫做 Creator Generalist，视频里展示了不少实际效果：
> - 从一张角色设计图制作可旋转的 3D 人物
> - 为古代水磨坊建立 3D 剖面模型和运转动画
> - 制作丝绸之路的动态地图
> - 根据照片制作 3D 物体
> - 分析视频、安排剪辑和音效
>
> 它把建模、绑定骨骼、动画、灯光、镜头、剪辑等专业制作流程，整理成 AI 能理解和调用的 Skills，并支持 Blender、Three.js 等工具。
>
> 我觉得这个项目最有意思的地方，是它展示了 AI Agent 扩展专业能力的一条很实用的路线。以前我们让 AI 制作复杂动画，需要反复解释制作方法、工具怎么用、哪些地方需要修正。现在可以把专业教程里的经验逐步整理成 Skills，让 AI 在做项目时直接调用。积累得越多，能独立处理的专业任务就越多。
>
> 我尤其看好它在独立游戏和短视频制作上的用途。一个人就有机会完成以前需要建模师、动画师、剪辑师协作的部分工作，而且制作流程可以反复复用。
>
> 项目已经开源，支持 Claude Code、Codex、Cursor 等 AI 编程工具。
>
> GitHub：https://github.com/codepawl/creator-generalist

### 1.2 英文首发帖（An Xuan @anxuanng，2026-11-08）

> Your agent writes code fine but falls apart when you ask it for a 3D film or a 2D explainer
>
> So I let mine watch about a thousand YouTube tutorials and learn the craft on its own, then packed it into creator generalist, a skill pack that makes any agent work like a 2D and 3D generalist
>
> This showreel was made with it

### 1.3 定位与样本说明（Caveat & 事实核对）

1. **「约 1,000 个 YouTube 教程」去了哪里？**
   - 我们在仓库中执行 `grep -rIiE "youtube.com|youtu.be|Source:" plugins/` 仅查得 123 处匹配（或 `grep -rnE "Source:|Sources:" plugins/` 共 134 处来源行，其中绝大部分仅标注软件官方手册或测试日期，无具体教程视频 URL），为何没有直接看到 1,000 条 YouTube 链接？
   - 原因写在 `plugins/watch-video/skills/watch-video/references/tutorials-to-skill.md` §6 第 66–68 行：
     > *"Creator names, channel handles and video links appear only in `Source:` or `Sources:` lines and in a `## Credit` section, never in headings, prose or tables. **A public copy drops those lines, so the learning stays private and nobody can pick a fight over who it came from.**"*
   - 也就是说，作者在发布公开版仓库前，按自定规则故意剥离了绝大部分 YouTube 频道名与视频链接（仅在 `shorts-storytelling.md` 残留了一处 `@BarelyInvented`、以及在 `shorts-storytelling.md` §2b/2c 披露了对 **1,960 条科普 Shorts** 与 **2,589 条 30 秒 3D 事实 Shorts** 的播放量回归统计）。
2. **Showreel 中「一句话生成」背后的真实工具链（逐帧角标核查）**：
   - 我们对原帖 27 秒 Showreel 进行了 1920×1080 全尺寸抽帧（`sr_1.0s.jpg` 至 `sr_26.0s.jpg`），发现画面右下角诚实标注了单靠代码无法凭空生成的外部依赖：
     - **0–3s（东京地铁日出 POV）**：提示词 `> /3dg POV ride on a Tokyo metro at sunrise`，右下角小字明确写着 **`Models: Tripo · built in 67js`**（模型由 Tripo 3D AI 生成，场景在作者另一个开源项目 `codepawl/67.js` 中组装）。
     - **4–6s（14世纪水磨坊 3D 剖面）**：提示词 `> /3dg cutaway a 14th-century water mill`，左下角调用标签 `3d-generalist · use-3d-software`，右下角标注 **`Poly Haven · Quaternius, CC0`**。
     - **7–10s（三视图转低多边形 3D 角色）**：提示词 `> /3dg character from this turnaround sheet`，左下角标签 `model-characters · rig-characters`（README 披露左侧三视图由 ChatGPT 生成）。
     - **11–13s（丝绸之路动态地图与比例尺时间轴）**：提示词 `> /2dg map the Silk Road with a true-scale timeline`，右下角标注 **`Natural Earth`**。
     - **14–16s（单张照片转日本红邮筒 3D 资产）**：提示词 `> /3dg asset this post box from one photo`，左下角标签 **`3d-generalist · Tripo Studio`**，右下角标注 **`Photo: kitmasterbloke, CC BY 2.0`**。
     - **17–19s（NASA 毅力号降落伞视频逐帧审片与标注）**：提示词 `> watch this video and check every claim`，画面展示 `Claude [00:12.8] seen` 与 `Claude [00:13.4] heard` 的声画核查叠层。
     - **20–21s（自动配音效与 -14 LUFS 混音谱图）**：提示词 `> make the SFX and mix it to -14 LUFS`，频谱图上标注 `pull back`、`pin`、`whoosh`、`typing`、`gears` 及右下角 `-14.0 LUFS · -1.0 dBTP`。
     - **22–24s（多轨节拍剪辑）**：提示词 `> cut it to the beat`，展示 `V1`（67js film / 3D cutaway / Character / 2D map / Hero asset / Watch / Sound / Edit）、`A1`（频谱）、`A2`（节拍切片点）三轨时间线。

---

## 二、 仓库全貌与数量三处对账

按照 `x2doc` 工具审计规范，我们对仓库宣称的插件/技能数、文档规模与实测命令进行了三处对账：

### 2.1 仓库结构与数量对账表

| 统计维度 | README / INSTALL 宣称口径 | 仓库实际文件扫描 (`commit 85bb905`) | 差异说明与核查结论 |
|---|---|---|---|
| **顶层插件数 (`plugins/*`)** | 4 个 (`3d-generalist`, `2d-generalist`, `watch-video`, `design-sound`) | **4 个** | 完全一致 |
| **Skill 目录数 (`SKILL.md`)** | `README.md` 表格列出 10 个功能 Skill；`README.md` 手动安装列出 **14 个文件夹**；`INSTALL.md` 第 40 行文字写 "Copy these twelve folders" 但列表实际有 **13 个**（漏了 `sculpt-models` 计数） | **14 个 `SKILL.md` 文件**（含 2 个主控 + 6 个 Craft + 2 个 Tool + 1 个 Learning + 1 个 Sound + `3dg`/`2dg` 2 个命令包装器） | `INSTALL.md` 文字写 12 个但列表列了 13 个，实际仓库共 **14 个** |
| **每个 `SKILL.md` 行数限制** | `AGENTS.md` 硬性规定："Every `SKILL.md` stays at or under 100 lines" | 13 个文件在 31–94 行之间；仅 `watch-video/SKILL.md` 为 **101 行**（超 1 行） | 工程纪律极严，主文件只做路由，细节全下沉到 `references/` |
| **工艺参考手册 (`references/*.md`)** | README 仅概述 | **124 个 Markdown 文件** | 真正的核心资产库（含约 250 个 Blender 5.x 配方、Vox 实测参数等） |
| **自动化与测试脚本 (`scripts/*` + `tests/*`)** | 按模块分散说明 | **`scripts/*` 下 56 个文件 + `tests/*` 下 4 个文件**（共 59 个 `.py`/`.mjs`/`.sh` 脚本 + 1 个 `vocabulary.txt`） | 覆盖渲染门禁、骨骼滑步检测、音频混音、视频感知、教程抓取与单元测试 |

### 2.2 四大插件与 12 个核心 Skill 功能矩阵

| 所属插件 | Skill 名称 | 角色定位 | 核心能力与关键脚本 / 参考文件 |
|---|---|---|---|
| **3d-generalist** | `3d-generalist` (+ `/3dg`) | 主控 (Main) | 5 种模式（`cutaway` 剖面短片、`story` 叙事短片、`world` 场景、`character` 角色、`asset` 资产）；含 `check_contact_and_slip.mjs`（30fps 物理接触门禁）、`technique-atlas.md`（症状→技法总表） |
| **3d-generalist** | `model-characters` | 工艺 (Craft) | 从三视图/设定图建低多边形（PS1/N64/Chibi/Anime）、雕刻或写实人体；含 `read_character_ref.py`（自动测量三视图头身比与色板）、`check_character.py`（网格水密/法线/对称检查） |
| **3d-generalist** | `sculpt-models` | 工艺 (Craft) | 生物/头像/岩石断层雕刻、重拓扑与烘焙；含 `check_sculpt.py`、`procedural_rock.py` |
| **3d-generalist** | `rig-characters` | 工艺 (Craft) | Rigify 骨骼命名、权重、IK/FK 吸附、面部绑定、机械绑定、导出 Unity/Godot/glTF |
| **3d-generalist** | `animate-characters` | 工艺 (Craft) | 12 条动画法则、曲线编辑器、步行/待机循环、2D/3D 抽帧（Stepped on twos）、残影（Smears） |
| **3d-generalist** | `use-3d-software` | 工具 (Tool) | 约 250 条 Blender 5.x 配方、Three.js 色彩与加载、Godot/Unity/Unreal 指南、C4D/Houdini/Maya 概念映射表 (`paid-to-blender.md`) |
| **2d-generalist** | `2d-generalist` (+ `/2dg`) | 主控 (Main) | Vox / Johnny Harris 风格动态图形（`map`、`chart-timeline`、`vox-now`、`archival-collage`）；含 `generate_vox_assets.py`（SVG 滤镜与比例尺时间轴生成）、`check_render.py`（成片门禁） |
| **2d-generalist** | `edit-video` | 工具 (Tool) | DaVinci Resolve / Fusion、CapCut、Premiere、Kdenlive、FFmpeg 剪辑配方；含 AE 付费插件转免费方案映射表 (`paid-to-free.md`) |
| **2d-generalist** | `draw-and-paint-art` | 工艺 (Craft) | 动态速写、透视缩减、灰度上色、Krita / Grease Pencil 绘制、为 3D 准备标准三视图 |
| **2d-generalist** | `paint-stylized-backgrounds` | 工艺 (Craft) | 3D 粗模叠绘（Paint-over）、视差图层、Blender 卡片背景、风格化水面与草地风场 |
| **watch-video** | `watch-video` | 学习 (Learning) | 视频全模态感知（`perceive.py` 抽帧接触表+切点+声谱图+音频时间轴）、教程频道转校验级 Skill 流水线（`fetch_tutorial_transcripts.py` + `check_blender_names.py` + `read_screen.py`） |
| **design-sound** | `design-sound` | 声音 (Sound) | CLAP 语义搜本地音效库（`search.py`）、抓 Openverse/Archive/YouTube 音效（`fetch_web.py`）、ElevenLabs 音效/配乐生成、HunyuanVideo-Foley 视频生拟音（`video_foley.py`）、工程级混音与母带门禁（`mix.py`） |

---

## 三、 本机实测与外部引擎适配评估（External Engine Fit）

我们在本机（M2 Max MBP 64GB，macOS）对 `/Users/marovole/Workspace/playground/creator-generalist` 进行了完整脚本实跑与原帖视频反测。

### 3.1 本机环境与自带测试集实跑结果

1. **工具链探针实跑（揪出 Windows 硬编码 Bug）**：
   - 运行 `python3 plugins/2d-generalist/skills/2d-generalist/scripts/check_vox_toolchain.py`：
   - 检测出已安装：`ffmpeg 9.0.2`、`ffprobe 9.0.2`、`yt-dlp 2026.08.19`、`node v22.22.3`、`uv 0.11.21`（`stack_a_code_driven_2d_3d [READY]`）。
   - **发现的平台兼容问题**：脚本将本机已安装的 **`Blender 5.2.3 LTS`**（位于 `/Applications/Blender.app/Contents/MacOS/Blender`）和 **`OBS.app`** 误判为 Missing，并打印出了 Windows 专属命令 `winget install BlenderFoundation.Blender`。查看源码 `check_vox_toolchain.py` 第 29–35 行证实，作者在 `candidate_paths` 中只硬编码了 `C:\Program Files\Blender Foundation\...`，未加入 macOS `/Applications/Blender.app` 路径。
2. **自带单元测试实跑**：
   - `test_vox_skill.py`：**6 / 6 passed (`0.518s, OK`)**。
   - `test_character_skill.py`：**3 / 3 passed (`0.055s, OK`)**。
   - `test_foley_shots.py`：**passed (`ok`)**。
   - `test_watch_video.py`：**52 项测试中 44 项通过、2 项跳过、6 项失败**。6 项失败原因完全一致：本机 Homebrew 默认安装的 `ffmpeg 9.0.2` 未编译 `libfreetype`（报错 `No such filter: 'drawtext'`），而 `perceive.py` 在拼接触表时强依赖 `drawtext` 在缩略图下方打时间戳（相比之下，`check_render.py` 仅用 `tile=6x5` 滤镜，不依赖 `drawtext`，因此在本机直接跑通）。
3. **Blender 5.x 名称校验器实跑**：
   - 运行 `uv run --no-project python plugins/watch-video/skills/watch-video/scripts/check_blender_names.py plugins/`：扫描全部 138 个 Markdown 文件，对照 `Blender 5.2.2 LTS` 字典报出 132 处需注意的名称，其中精准抓出 `stylized-shading-recipes.md:329` 中残留的旧节点名 `Invert -- old name, now Invert Color`（其余多为 DaVinci Fusion / Godot / Unreal 文档中的非 Blender 节点名）。

### 3.2 原帖 27 秒 Showreel 成片反测（用它的门禁验它的片）

我们对下载的 `creator_generalist_showreel.mp4`（`1920×1080`，`27.05s`，H.264 + AAC 48kHz）执行了 `check_render.py`、FFmpeg `ebur128` 与 50ms 步长 RMS 扫描：

```text
PASS  no sterile white or black frames
FAIL  no hold over 1.5 s
PASS  audio present
PASS  loudness -14 ±1.5 LUFS
PASS  true peak at or under -1 dB
PASS  no silence over 0.4 s
PASS  duration in range
longest hold 2.33 s at 10.97 s; stepped frames 42%
loudness -14.2 LUFS, true peak -1.3 dB, longest silence 0.0 s
```

- **音频母带极度扎实**：实测 Integrated Loudness 为 **`-14.2 LUFS`**（LRA `3.3 LU`），True Peak 为 **`-1.3 dBFS`**，与视频第 21 秒画面上自标的 `-14.0 LUFS · -1.0 dBTP` 误差仅 `0.2 LU`，证明这条 Showreel 的音轨确实跑过了它自己的 `mix.py` 母带限幅链。
- **画面静止门禁（Dead Air Gate）实证有效**：脚本在 `10.97s` 处抓出 `2.33s` 的画面静止（超过默认 `1.5s` 阈值），同时测出全片 `stepped frames = 42%`（符合其 8–12fps 抽帧手绘感/定格感设计）。

### 3.3 形态映射表（Creator Generalist 形态 vs 我们的内容矩阵）

| 插件 / 模式 | 画布与技术栈 | 视觉语法 | 官方样片 | 对应我们哪条线 / 哪类选题 |
|---|---|---|---|---|
| **`3dg cutaway`（3D 剖面演进短片）** | `1080×1920` 或 `1920×1080`（Blender / Three.js / 67js） | 单一微缩场景内，通过 5–7 轮 `But <故障> -> So <原位加装结构>` + 3D 引导线部件标签（`ADOBE`, `U-BEND`）完成工程演进 | 14 世纪水磨坊剖面（齿轮与水轮联动） | **灵知 AI（家庭营养/生理机制微缩剖面）** 或 **个人号（AI Agent 架构/缓存路由机制 3D 剖面拆解）** |
| **`2dg vox-now / chart-timeline`** | `1920×1080` / `1080×1620`（Remotion + SVG + Three.js） | 60–75% 留白纸面（`#F1ECE6`）、3 色墨水、柠檬黄整行高亮（`#F7EC02`）、真比例尺刻度尺时间轴 | 丝绸之路动态地图与公元前 130–1453 比例尺时间轴 | **个人号第一人称 AI 实测 / 账单审计长视频与短视频卡片**（与 `cinecode` 桌面调查风互补） |
| **`3dg character / asset`** | Blender + Tripo / 2D 三视图建模 | 2D 设定图转复古低多边形（PS1/N64/Anime）绑定角色，或单图转 PBR 资产 | 黄雨衣蓝发角色旋转待机、日本红邮筒网格生成 | **自有开源项目 / 游戏化交互演示资产**（非日更刚需，按需单调） |
| **`watch-video`（视频审片与教程转 Skill）** | Python + FFmpeg + PP-OCRv6 + Whisper | 抽帧接触表、声谱图、逐句语调分析、把整个 YouTube 教程频道蒸馏并校验为本地 Skill | 毅力号降落伞声画同步核查叠层 | **内部知识吸收基建**：批量把海外顶尖创作者/技术频道转化为我们自己的已校验 Skill |

### 3.4 与我们现有视频工具链的取舍表（谁强·怎么配合）

| 维度 | 我们现有管线 (`xilo` + `Papermorph` + `science-video-daily` + `cinecode`) | `codepawl/creator-generalist` | 结论：谁更强 / 怎么配合 |
|---|---|---|---|
| **日更科普/知识短视频出片速度** | **极强**：单页 HTML/Canvas 确定性逐帧导出 + ElevenLabs 字级时间戳，2:3 画幅一键成片 | 较重：依赖 Blender / 67js / Tripo 外部建模或多步问答（Intent Brief） | **日更单条继续用现有管线**，绝不为日常短视频套它的 3D 全家桶 |
| **3D 物理穿模与滑步机器门禁** | `ChrisHKAI-Video` 有静态包围盒碰撞检测 `clearance.mjs` | **极强**：`check_contact_and_slip.mjs` 按 30fps 检查角色髋部瞬移（>0.3m/帧）、脚跟/脚尖滑步（离地 <3cm 时速度 >0.25m/s）与腾空 | 做 Three.js / WebGL 角色动画时，**直接复用 `check_contact_and_slip.mjs`** |
| **音频混音与手机外放工程化** | `cinecode` 有 `voice_treat.py`（人声介质化）；现有管线有基础 ducking | **极强**：`design-sound/scripts/mix.py` 具备 **STFT 频谱级动态避让（Unmask，只在音效与人声重叠频段压人声）**、**150Hz 以下手机谐波补偿（`phone_bass`）**、以及 **AAC 128k / Opus 64k 实编解码真峰值反测（`codec_check`）** | **核心吸收项**：将 `mix.py` 的 `phone_bass`、频谱 Unmask 和有损编码真峰值回测抽入我们的音频母带步骤 |
| **Vox 视觉规范的量化程度** | `cinecode` 有 `styles/vox-explainer.md`（偏早期拼贴风） | **极强**：`vox-modern-measured.md` 对 2026 年 4 部新 Vox 视频做了像素级实测，区分了**现代极简 Vox（60–75% 留白、无撕边、无网点、1.8s 硬切、`#F7EC02` 整行高亮不压暗其余字）**与早期复古拼贴风 | **直接吸收 `vox-modern-measured.md` 与 `technique-atlas.md`** 作为视觉设计参数字典 |
| **从视频教程批量蒸馏 Skill** | `x2doc` 含单长视频转写配方（`long-video-transcription.md`） | **极强（独创）**：`watch-video` 定义了完整的「Pick → Distill → Verify（软件字典校验+全尺寸帧 OCR 读参数+新版文档比对）→ Blind Worker 实建对比图」闭环 | **核心吸收项**：把这套三重验证（防听错、防看错、防软件改版过期）合入我们的教程吸收工作流 |

### 3.5 中文落地必改的四项（直接套原版必踩坑）

| 项 | 原版病灶 | 我们的改法 |
|---|---|---|
| **1. macOS 路径与 FFmpeg `drawtext` 依赖** | `check_vox_toolchain.py` 只扫 Windows `C:\Program Files`；`perceive.py` 用 FFmpeg `drawtext` 打时间戳，在 macOS Homebrew 标准 `ffmpeg` 下直接报错退出 | macOS 调 Blender 显式指向 `/Applications/Blender.app/Contents/MacOS/Blender`；打时间戳改用 Python `Pillow (PIL.ImageDraw)` 在内存画完再存图（与 `check_render.py` 保持一致，彻底摆脱 `drawtext` 滤镜依赖） |
| **2. 配音与语速预算 (`shorts-storytelling.md`)** | 按英文 `3.4–3.6 words/s`（60 秒 230 词）排拍，逐词居中大字幕（`Y=1010`）按英文空格切词 | 中文按 **3.8–4.5 字/秒** 重算每拍时长；中文不搞逐字蹦迪字幕，按语义短句切分，继续走我们已跑通的字级时间戳对齐 |
| **3. 字体与排版安全区** | 默认英文字体（Sora / 衬线体），且 `qa-and-gates.md`（第 29–30 行）与 `technique-atlas.md`（第 210 行）以大写拉丁字母高度（Cap height ≥ 5%，1080p 下 ≥54px）定最小字号 | 中文正文字号在 1080p 下锁死 **≥56px**（手机端清晰可读底线），字体栈显式加入 `"PingFang SC", "Noto Sans CJK SC", "Songti SC"` |
| **4. 画幅规范** | 竖屏默认 `9:16` (`1080×1920`)，横屏 `16:9` (`1920×1080`) | 抖音/视频号竖屏统一按我们 `video-common` 的 **`2:3` (`1080×1620`)** 输出；YouTube 长片与 X 视频用 `16:9` (`1920×1080`) |

### 3.6 三栏成本账本（拆穿“一键免费”表象）

| 成本维度 | 费用明细 | 真实评估 |
|---|---|---|
| **1. 外部 API（3D 生成 / 音效 / 配音）** | Showreel 中的复杂单图转 3D（日本邮筒、东京地铁部件）实际调用了 **Tripo Studio / Tripo 3D API**（按生成次数计费）；音效/配乐生成可选调用 **ElevenLabs API** 或 **fal.ai (`HunyuanVideo-Foley`)**；仅 Poly Haven / Natural Earth / Openverse 为 `$0` | 纯靠免费 CC0 资产只能拼出基础几何与现成扫描件；要做特定照片转 3D 资产仍需外部 3D 生成模型额度 |
| **2. 本地算力与渲染时间** | Blender 5.2 Cycles/EEVEE 渲染、本地 `HunyuanVideo-Foley`（需 **9 GB VRAM**）、PP-OCRv6 屏幕文字识别：本机 M2 Max 64GB 跑得动，但 3D 6-subframe 运动模糊成片与视频全帧 OCR 耗时数分钟至数十分钟 | 硬件零现金支出，但重度吃本机 GPU 队列时间 |
| **3. LLM Token（真正大头）** | 无论是让 Agent 跑完 8 步 3D 制作 + 10 道 QA 门禁，还是用 `watch-video` 派并发 Worker 蒸馏几十个 YouTube 教程并盲跑 Blender 渲染比对，单次任务均是**百万至千万级 Token 消耗** | 适合用高额度包月订阅（Codex Pro / Claude Max / Devin Max）跑高价值精品或沉淀长期 Skill，不适合高频日更挥霍 |

---

## 四、 最值得我们直接借走的 4 个核心机制（含实证数据）

不用安装它全部 14 个 Skill 污染全局命名空间，下面 4 项机制可以直接抽进我们的武器库：

### 1. `shorts-storytelling.md` §2c：对 2,589 条爆款 Shorts 的反直觉实测结论
作者在 `shorts-storytelling.md` 中对 **1,960 条科普 Shorts** 和 **2,589 条 30 秒 3D 事实 Shorts**（并抽样 209 条核对上传年份）做了回归分析，得出了一个极其诚实的结论：
- **播放量差距主要来自发布年份（先发红利与幸存者偏差）**：2022–2024 年上传的中位播放量为 **28M**，2025 年降至 **20.5M**，2026 年降至 **17M**。
- **在 2025–2026 年的新视频中，所有“黄金文案句式”的流量加成全部归零**：假设性开头（`"If you..."`）为 `1.00x`，前 25 词含 `"you"` 为 `1.00x`，`"most people think"` 反常识句式为 `0.97x`；转折位置（25% 处）、数字密度、结尾句式对播放量均无显著影响。
- **真正决定 2026 年播放量的三个变量在文案套路之外**：**① 切中当下正在发生的趋势（Live trend）、② 核心前提本身的新颖度（Premise novelty）、③ 画面第一眼的视觉冲击力（The picture）**。这直接验证了我们“不迷信爆款文案模板、靠真实一线内容与硬核视觉立 IP”的判断。

### 2. `watch-video` 的「教程转 Skill 三重防错闭环」（`tutorials-to-skill.md`）
以前把 YouTube 教程转成文档只靠跑 Whisper 字幕总结，必犯三个错：**语音识别听错专业名词、总结者看错操作目的、老视频里的软件菜单在新版里早就改名了**。它的解法非常值得照搬：
1. **名称字典硬核对（Names）**：导出当前软件版本的全量 API/节点名 JSON（如 `blender_names_dump.py`），用脚本扫笔记里的每一个专有名词，自动提示旧版改名（如 `Mix RGB -> Mix (Color)`）。
2. **全尺寸原帧读数（Values on screen）**：凡是决定视觉效果的参数（强度、字号、色值），严禁只信口播或缩略图，必须用 `yt-dlp --download-sections` 切出那 2 秒的 1080p 原片抽单帧读取真实面板数值。
3. **干净 Worker 盲测出图（Prove it builds）**：挑出新 Skill 最核心的 3 个技法，派一个**没有任何上下文、只拿到这份新 Skill** 的干净 Subagent 独立写出渲染结果，与原教程视频的结果帧拼在同一张对比图上验收——画不对就是 Skill 没写清楚，改 Skill 而不是改渲染图。

### 3. `design-sound` 的 `mix.py` 四项工程级母带机制
可以作为我们 `cinecode` `voice_treat.py` 的完美下游补充：
1. **1–4kHz 动态频段避让 `carve`（`scripts/mix.py` 第 58–59、87–92 行；`references/mix.md` 第 30–31 行）**：人声或音效响起时，用零相位带通滤波器仅将背景音乐的 `1–4 kHz` 人声敏感频段动态衰减默认 `-3 dB`，其余频段保持不动，避免整轨音乐忽大忽小（Pumping）。
2. **频谱级 Unmask（`scripts/mix.py` 第 46–52、95–125 行；`references/mix.md` 第 32–36 行）**：当关键音效（Cue）与旁白同时响起时，在 21ms STFT 频谱上，**仅在音效能量接近人声（6dB 内）的特定频段和瞬间，把人声按 `unmask_db`（默认 `-3 dB`，实测比对 `-3` 与 `-6 dB`）微让**，让人声保持饱满的同时音效颗粒感清晰透出。
3. **手机扬声器低音谐波补偿 `phone_bass`（`scripts/mix.py` 第 60、127–135 行；`references/mix.md` 第 37–38 行）**：手机喇叭在 200Hz 以下几乎无响应；脚本提取 150Hz 以下的重击低频，通过软削波生成 **150–600Hz 的 2 次/3 次谐波并以 `-6 dB` 混入**，利用缺失基频效应让小手机外放也能听出低音重击。
4. **有损编码真峰值回测 `codec_check`（`scripts/mix.py` 第 74–78 行；`references/mix.md` 第 110–114 行）**：作者实测发现 `-3.19 dBTP` 的 WAV 母带（Kevin MacLeod `"Latin Industries"`）经 FFmpeg `AAC 128k` 编码解码后真峰值会暴涨 `3.17 dB` 到 `-0.02 dBTP` 导致爆音。因此 `mix.py` 在输出前会自动试编码一次 `AAC 128k` 和 `Opus 64k` 并解码测峰值，动态下调限幅器天花板直到有损解码后依然 `≤ -0.3 dBTP`。

### 4. `technique-atlas.md`（症状→技法字典）与 `vox-modern-measured.md`
当画面显得“假、平、塑料、廉价”时，不再让 Agent 盲目改代码，而是查表按物理参数修正：
- **画面太扁平（Flat）**：套用大气透视公式 `T = exp(-sigma * d)` 混入地平线雾色，加 5–8 层 `1/distance` 速度比的视差图层。
- **2026 现代 Vox 极简规范（`vox-modern-measured.md`）**：画面 **60–75% 留白**（底色 `#F1ECE6`）、**最多 3 色墨水**（金 `#C29A16`、灰 `#80807F`、暖黑 `#1A130F`，高饱和像素占比 ≤3%）、**柠檬黄 `#F7EC02` 整行矩形高亮**（切入后停 `0.45s` → `0.5s` 线性从左往右划过 → 静止保持 `2.7s` → 硬切，不压暗其余文字）。

---

## 五、 可执行下一步（低成本借件方案）

遵循“现有 skill 能出活就直接复用，不随便大改主力管线”的原则，建议按以下三步轻量吸收：

- [ ] **Step 1（保持只读参考库，不全局安装 14 个 Skill）**：保留 `/Users/marovole/Workspace/playground/creator-generalist` 作为本地只读配方与脚本库，不往 `~/.hermes/skills/` 塞入全部 14 个目录，避免与现有的 `blender-3d-scene-video`、`xilo-opus-video`、`baoyu-visual-content` 发生触发词碰撞。
- [ ] **Step 2（在下次制作 YouTube 英文/中文长片时直接调它的 2 个独立脚本）**：
  1. 混音母带阶段调用 `/Users/marovole/Workspace/playground/creator-generalist/plugins/design-sound/skills/design-sound/scripts/mix.py`，开启 `phone_bass: true` 与 `codec_check: true`，确保手机外放低频扎实且 AAC 转码绝不爆音；
  2. 成片交付前跑一遍 `/Users/marovole/Workspace/playground/creator-generalist/plugins/2d-generalist/skills/2d-generalist/scripts/check_render.py <film.mp4>`，用机器门禁自动抓出超时静止帧（Dead Air）与响度偏差。
- [ ] **Step 3（按需启用 `watch-video` 的教程频道蒸馏法）**：后续当你看中某个海外硬核 YouTube 播放列表或创作者频道、想把对方的独门手艺沉淀为内部 Skill 时，直接按 `watch-video/references/tutorials-to-skill.md` 的「字幕提取 → 全尺寸帧参数核对 → 干净 Subagent 盲跑成片对比」三步法执行。

---

*来自翡冷翠*
