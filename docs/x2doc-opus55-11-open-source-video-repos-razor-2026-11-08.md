# Opus 5.5 + 11 个开源视频剪辑仓库 + Clawd Motion Lab《THE RAZOR》与动效工作室指南 - X2Doc 整理 & 适配分析

> 来源：
> - 主帖：https://x.com/dyfwsammy/status/2119081781198553269 （@dyfwsammy / S 🫧，2026-11-07）
> - 首评 Google Drive PDF：https://x.com/dyfwsammy/status/2119081819224043857 → `https://drive.google.com/file/d/1_QFqZCIRUl_wv7ahYg90VHivhRK-_oG_/view`（Clawd Motion Lab 6 页《PROMPT PACK: THE RAZOR Opus 5.5 prompt》）
> - 引用推文 X Article：https://x.com/dyfwsammy/status/2117905023145267550 → `https://x.com/i/article/2117626780584431616`（《Design Engineering: Build a Motion Studio Around Opus 5.5》，2026-11-04）
> - 相关前置文档：[Opus 5.5 用代码做视频万字拆解（xilo）](./x2doc-opus55-code-video-xilo-2026-09-29.md) · [cinecode 代码纪录片 Skill 整理](./x2doc-cinecode-youtube-documentary-skill-2026-11-08.md)
> 整理时间：2026-11-08
> 来自翡冷翠

---

## TL;DR

- **这组内容共有三层，推文正文只是最浅的钩子**：
  1. **表层（主帖）**：列举 11 个免费开源仓库（`PySceneDetect`、`Auto-Editor`、`vid.stab`、`color-matcher`、`rembg`、`RIFE`、`Real-ESRGAN`、`Demucs`、`librosa`、`HyperFrames`、`FFmpeg`）组成免 Premiere Pro 的全套剪辑管线。注意原帖所有 `t.co` 短链跳转的 GitHub URL 均被截断在 32 字符（除 `librosa` 和 `FFmpeg` 外全部 404），本文已通过 GitHub API 还原并校验全部 11 个真实仓库。
  2. **核心层（Google Drive 6 页 PDF《PROMPT PACK: THE RAZOR》+ 19.58s 1080×1350@60fps 演示成片）**：真正惊艳的不是“11 个老牌开源库”，而是 **Clawd Motion Lab 用 Claude Opus 5.5（Effort High）驱动 Blender 5 Cycles GPU + Python 音频合成，把 4分23秒真实素材经 11 个仓库处理后的真实输出，放进一个 3D 剪辑台场景里，让吉祥物 Clawd 举着剃须刀踩着 120 BPM 的 Long Tresillo（每 3 拍一刀）逐一劈开片段**。PDF 完整公开了 880 词画面 Prompt、240 词纯代码音频合成 Prompt，以及**从首版废片到定稿的 12 轮视觉修正 + 3 轮声学修正真实记录**。
  3. **方法论层（引用 X Article《Design Engineering: Build a Motion Studio Around Opus 5.5》）**：一套极度干练的 UI/Web 动效工程规范——先写 `MOTION.md` 与 CSS/TS 弹簧/缓动 Token → 用物理手感描述原型并暴露调试面板 → 用零成本正则脚本 `motion-lint.ts` 卡 CI → 用 `motion-review.ts` 调 Opus 5.5 审代码 → 每次留存 ADR 决策记录。
- **原帖 19.58 秒成片独立验尸（FFmpeg / `ebur128` / `cinecode` 门禁实测 vs PDF 自述）**：
  - 响度与真峰值：我们用 `ffmpeg -af ebur128=peak=true` 实测原帖 MP4 为 **`-15.9 LUFS`、真峰值 `-1.6 dBFS`**，与 PDF 第 6 页披露的 `-15.8 LUFS, -1.6 dBTP` 高度吻合（误差仅 `0.1 LU`）；
  - 200ms 绝对静音顿挫（THE STOP）：实测在 `16.45s–16.60s` 出现深度静音（`16.50s–16.55s` 达 **`-84.03 dBFS` 至 `-88.64 dBFS`**，相比前一小节压低超 `66 dB`），紧接着 `16.65s` 爆发全片最响重击（`-8.79 dBFS`），证实了 PDF 中“先混响、在混响之后切 200ms 静音、再进 Brickwall 限制器”的工程技巧；
  - 首帧运动与主体残差：`qc.py hook` 实测首 2 秒 `mean=16.55`（PASS）；`scene_check.py action` 扣除摄影机运镜后的 4 个段落主体运动残差高达 `32.26–45.75`（`0 scene(s) flagged`）。
- **对我们现有产线的吸收结论（借件不换栈）**：
  - **不搬它的 Blender 5 Cycles 重型 3D 流程做日更**（作者在 RTX 4060 笔记本上渲 20 秒 1200 帧耗时 **2 小时 06 分钟**，且历经 12 轮返工才修平遮挡与偏色）；
  - **直接借用 4 个高价值机制**：① **单一时间轴真相源 `timeline.py` + `screen.py` 预渲染真实输出序列帧贴进 3D/2.5D 发光屏幕**；② **先混响后切 200ms 极静顿挫（THE STOP）再进限制器的高潮声学公式**；③ **可度量的机器门禁清单（RGB 距离 `<10`、跳跃速度 `≤2.6 m/s`、首尾帧像素差 `/255`、真峰值 `-1.6 dBTP`）**；④ **X Article 的 `MOTION.md + motion-lint.ts + motion-review.ts` 三件套**直接用于我们前端项目与代码动画的动效品控。

---

## 一、 原帖核心内容与 11 个开源仓库真实还原（修正原帖截断死链）

### 1.1 主帖正文（@dyfwsammy，2026-11-07）

> HOLY F*CK. OPUS 5.5 JUST TURNED 11 FREE OPEN-SOURCE REPOS INTO A COMPLETE VIDEO EDITING WORKFLOW.
> You don’t need Premiere Pro for every editing task.
> Cut. Stabilize. Color grade. Slow motion. Upscale. Audio stems. Titles. Export.
> Every tool below is free, and each one was tested on 4:23 of real footage.

### 1.2 11 个开源仓库完整对照表（含 GitHub 实时数据与本机就绪度）

> **⚠️ 原帖死链排雷**：@dyfwsammy 在发推时直接复制了带省略号的截断文本，导致原帖中编号 01–08 及 10 的 `t.co` 短链解析后全是截断的 404 链接（例如 `https://github.com/Breakthrough/P`、`https://github.com/heygen-com/hyp`）。下表是我们通过 GitHub 官方 API 核验还原后的真实仓库地址、Star 数（截至 2026-11-08）、开源协议及在视频管线中的实际角色：

| 序号 | 仓库名称 | 真实 GitHub 链接（已修复原帖截断） | Stars (2026-11) | 协议 | 在 4:23 实测视频中的真实产出（据 PDF P05） | 我们本机 (`M2 Max`) 状态与定位 |
|---|---|---|---|---|---|---|
| **01** | **PySceneDetect** | [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | ★ 5,404 | BSD-3 | 在 4分23秒原片中自动切出 **96 个镜头（96 shots）** | `ffmpeg` 已内置 `scdet` 滤镜；做参考视频扒谱可直调 `cinecode/scripts/ref_video.py` |
| **02** | **Auto-Editor** | [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | ★ 5,804 | Unlicense | 20% 阈值下将 4:23 剪至 **3:57（砍掉 26s 静音气口）** | 剪纯静音可用它；口播带气口/结巴精剪优先用 Whisper 词级时间戳（如 `footage_cut.py`） |
| **03** | **vid.stab** | [georgmartius/vid.stab](https://github.com/georgmartius/vid.stab) | ★ 989 | GPL | 将手持晃动画面锁死稳像（`locked shot, shake removed`） | 底层为 C 库，通常作为 FFmpeg 的 `vidstabdetect` + `vidstabtransform` 滤镜调用 |
| **04** | **color-matcher** | [hahnec/color-matcher](https://github.com/hahnec/color-matcher) | ★ 704 | GPL-3.0 | 用 `mkl` 算法将灰片一键匹配至参考帧色调 | Python 库（`pip install color-matcher`），适合多机位/多素材色调统一 |
| **05** | **rembg** | [danielgatis/rembg](https://github.com/danielgatis/rembg) | ★ 25,376 | MIT | 免绿幕抠出 **158 帧干净遮罩（15px 开运算修边）** | 成熟图像/序列帧去背景工具，适合人物/物品贴片合成 |
| **06** | **RIFE** | [hzwer/ECCV2022-RIFE](https://github.com/hzwer/ECCV2022-RIFE) | ★ 5,667 | MIT | 30fps 光流插帧 **6 倍（x6）**，以 **3 倍慢放（x3 slow）** 呈现 | 苹果芯片推荐走 `rife-ncnn-vulkan`（Metal/Vulkan 加速），无需装庞大 PyTorch |
| **07** | **Real-ESRGAN** | [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | ★ 37,404 | BSD-3 | 将 `480×270` 低清片段 **4 倍超分（x4）至 `1920×1080`** | 同样推荐走 `realesrgan-ncnn-vulkan` CLI，单张/序列帧超分极快 |
| **08** | **Demucs** | [facebookresearch/demucs](https://github.com/facebookresearch/demucs) | ★ 10,405 | MIT | 将配乐分离为 **4 条独立音轨（drums / bass / other / vocals）** | Meta 开源音源分离标杆；抽人声或把有唱词 BGM 拆出纯伴奏时必用 |
| **09** | **librosa** | [librosa/librosa](https://github.com/librosa/librosa) | ★ 8,806 | ISC | 测出配乐 **119.7 BPM、34 个拍点**，驱动画面踩点切镜 | Python 音频分析标准库，配合 `numpy/scipy` 做节拍网格（Beat Grid）极稳 |
| **10** | **HyperFrames** | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | ★ 80,586 | Apache-2.0 | 用纯 HTML/CSS 渲染出带动态排版的片头大字 `CUT BY CLAWD` | HeyGen 开源的 Agent 原生 HTML 视频渲染框架（我们此前已在 `ai-content-tools-hyperframes-chatpdf-2026-05-02.md` 收录） |
| **11** | **FFmpeg** | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | ★ 66,714 | LGPL/GPL | 合成最终 `1080×1350` 60fps 视频（H.264 CRF 16, BT.709, AAC 320k） | 本机已装 `/opt/homebrew/bin/ffmpeg` (`9.0.2`，含 `h264_videotoolbox` 硬编) |

---

## 二、 核心拆解：Google Drive 6 页 PDF《PROMPT PACK: THE RAZOR》全量还原与验尸

原帖首评给出的 Google Drive PDF（6 页，署名 **Clawd Motion Lab**）才是这条推文真正的硬核资产。它完整展示了一个顶级的「代码驱动 Blender 3D + 真实工具链回填 + 纯代码音频合成 + 12 轮量化自检」闭环。

### 2.1 工程架构：为什么它的画面不是假 UI Mockup？

作者没有让 3D 软件去“画假界面”，而是设计了 **4 个解耦脚本 + 1 个单一时间轴真相源**：

1. **`jobs.ps1`（真实跑完 11 个仓库）**：先把作者自己过往的 16 条短片拼成一条 `4:23`（263 秒）的原始素材，真实调用上述 11 个开源工具处理这段视频，产出分镜截图、降噪波形、稳像对比、调色对比、抠像序列、插帧慢放、超分画面、四轨波形、拍点标记与 HTML 标题。
2. **`timeline.py`（单一时钟真相源）**：全片 `20.0s`、`60 fps`（共 `1200` 帧）、`120 BPM`（1 拍 = 0.5s = 30 帧）。从 `2.00s` 到 `17.00s`，每隔 `1.50s`（即 **3 拍，4/4 拍下的 Long Tresillo 切分律动**）劈下一刀，共 11 刀。台面滚动、屏幕切换、吉祥物跳跃、刀光火花、合成器音效全部从同一个 `timeline.py` 读取帧号（`frame = time * 60 + 1`）。
3. **`screen.py`（1.5 分钟生成 1200 张真实监视器贴图）**：读取 `jobs.ps1` 的真实输出，在 1.5 分钟内写出 `1200` 张 JPEG 序列帧。Blender 将这组序列帧贴在剪辑台正上方的巨型监视器发光材质（Emitter）上——**监视器不仅是画面，更是整个 3D 房间的主光源，真实视频的色彩直接照亮吉祥物 Clawd 并反射在胡桃木桌面与轨道甲板上**。
4. **`motion.py` & `scene.py`（Numpy 算运动曲线 + Blender 5 Cycles 渲染）**：所有运动通道先在 `motion.py` 里用 `numpy` 计算（五次方缓动 Quintic Easing + 落地阻尼弹簧 Damped Spring，动态模糊 `0.42`），并在渲染前直接打印物理校验值（跳跃最高速度、劈砍坐标、首尾接缝差）。

### 2.2 原文完整 Prompt 照录（Page 2：880 词画面 Prompt + Page 6：240 词声音 Prompt）

#### （1）画面主 Prompt（Page 2，Copy-Ready 880 Words）

> Paste it as is into Claude Code running Opus 5.5 at effort high, with Blender 5, ffmpeg, node with puppeteer and a Python venv (scenedetect, auto-editor, color-matcher, rembg, demucs, librosa, opencv) installed. Give it your own films as the raw footage. It builds the bay in code, runs all 11 repos and reads its own stills.

```text
BRAND
HERO: Clawd, the Claude Code mascot as one smooth voxel toy: body 12x8x6 units, two side nubs, four short legs, black eye slits that switch to happy ^^ and a squint "> <" on the swing; terracotta D97757
PROP: a giant safety-razor blade with the classic slots on a black grip with an orange ring: the razor tool of an editor as an object, as wide as he is, in his right hand
APP: a Premiere-style edit bay built in 3D, no logos: a huge program monitor on top, a timeline deck under it with a timecode ruler, a blue playhead, video clips as thick slabs, the audio as a glowing waveform lane
LIST: 11 clips = 11 free repos, in the order a real edit happens: PySceneDetect (finds every shot); Auto-Editor (cuts the dead air); vid.stab (steadies the shake); color-matcher (grades every shot); rembg (no green screen); RIFE (smooth slow motion); Real-ESRGAN (upscales x4); Demucs (splits the stems); librosa (cuts on the beat); HyperFrames (titles from HTML); FFmpeg (exports the film)
RESULT: 4:23 of raw footage, all of our own 16 short films end to end, becomes 0:20; every monitor picture is the real output of that repo run on that footage
SET: an edit bay at night: walnut slats, a warm bias light behind the monitor, shelves of drives with small LEDs, a deck that mirrors the monitor
PALETTE: near-black deck, walnut, playhead blue, clip violet 9B86FF, audio green 3FDC9B, title pink FF7FB0, export orange F57A45, Clawd D97757

FORMAT: Blender 5 Python, Cycles GPU, 1080x1350 (4:5), 60 fps, 20 s = 1200 frames, 120 BPM, quintic easing on every move, a damped spring on every landing, motion blur 0.42. One timeline.py holds the list and every event, one motion.py holds every channel in numpy and prints the checks. The monitor is an image sequence of 1200 frames written by screen.py from the job outputs.

BEATS (seconds):
0-0.5 the poster: 11 slabs as a 3x4 grid, each with a real thumbnail, the repo name and its job; Clawd stands in cell 12 with the razor raised; a high 62 mm shot
0.5-1.5 the crane drops, the slabs fly down into one row and lose their colour: raw clips; he hops to the row
2.0-17.0 eleven chops, one every 3 beats: he hops, the timeline scrolls one clip under him, the razor lands on the playhead, sparks, the clip splits and takes its colour, the monitor wipes from the input to the real output
2.0 PySceneDetect: every shot it found in the raw pops in as a thumbnail wall, a counter runs to the real number
3.5 Auto-Editor: the waveform of the raw, the dead bars turn red and fall, the rest closes up; the right half of the slab falls through the deck and the row ripples shut
5.0 vid.stab: handheld shake on a locked shot, then its stabilised output; the slab shakes until the chop, then it is dead still
6.5 color-matcher: a flat grey version, then the grade matched to one reference frame
8.0 rembg: the background wipes away and he stands over a planet; the cut piece of the slab lifts onto V2
9.5 RIFE: 30 fps frames, then the x6 in-betweens at x3 slow motion; the slab stretches, the music sinks
11.0 Real-ESRGAN: a 480x270 clip, its real x4 output behind the wipe
12.5 Demucs: our own track splits into 4 real stems on the monitor and on the deck
14.0 librosa: every shot change on a beat it detected in the same track, the measured BPM, green pins rise on the audio lane
15.5 HyperFrames: an animated title rendered from HTML over the planet
16.8 THE STOP: 200 ms of silence
17.0 THE LAST CHOP: FFmpeg, the bar fills, its real log scrolls, 4:23 -> 0:20, happy eyes, the loudest moment
18.0-19.5 the playhead rewinds to zero, the clips fly back into the grid one by one up a scale, he hops home, the razor goes up

LOOP: frame 1200 is frame 1: every clip, the scroll, the camera and every face channel return home; print them all at the seam.
CAMERA: the poster: 62 mm from high up, he leans back 0.7 rad so his face reads from above. The wide: 33 mm, low, aimed at the centre of the monitor, so the monitor fills the top half and the timeline the bottom half, like the app. A slow arc through the jobs, one path through a 0.2 s wrapped Gaussian.
LOOK: AgX Medium High Contrast, 256 samples, adaptive 0.015. The monitor is the main light on the room: a real emitter, so the footage colours him and mirrors in the deck. A soft key, a small key on the hero only, a warm bias light on the slats.
CHECKS: all 11 names readable at 640 px wide on frame 1; the name strip sits on TOP of the monitor so he never covers it; the whole monitor in frame in every job; each picture is the repo's real output; hop speed at most 2.6 m/s; he is whole in frame from the first chop; the orange within 10 of D97757 on full frames; the last chop the loudest quarter, the stop at least 12 dB under; true peak measured on the MP4; last frame vs frame 1.
```

#### （2）纯代码音频合成 Prompt（Page 6，Copy-Ready 240 Words）

```text
Add sound. Synthesize everything in Python with numpy, scipy and pedalboard: no samples, no borrowed melody. 48 kHz stereo WAV, 20 s. Read every event from timeline.py and land each hit on its frame. Finish it before the picture: Demucs and librosa run on this file.

Music: 120 BPM in A minor, a kick on every beat, a snare on 2 and 4, 8th hats, a bass on A, A, F, G; plucks join at 8 s, 16th hats at 14 s. A wordless formant line gives Demucs something to look at. A pulse and a snare roll under the poster, so the open is never dead. A 55 Hz drone with whole cycles in 20 s closes the loop.

Design: every chop = a low thump, a steel shing and a metal ring, each a step higher up the scale; one sound per job (the table on page 5); on RIFE the whole mix sinks through a low-pass; 200 ms of real silence, then the last chop, a sub drop and a held A minor chord, the loudest moment; 11 clicks up a scale as the clips land.

Master: normalize to -4 dBFS, the room reverb, THEN the stop after the reverb, the groove at 0.74 under the last hit, a gentle compressor, +10.5 dB into a lookahead brickwall at 4x oversampling with a -1.2 dB ceiling. Print loudness per quarter second and the stop. Measure the MP4, not the WAV.
```

### 2.3 为什么“一句 Prompt 出大片”是神话？看作者真实的 12+3 轮返工台账（Page 3 & Page 6）

这份 PDF 最诚实、最值得工程团队学习的地方在于第 3 页和第 6 页：**作者明确记录了 Opus 5.5 第一版跑出来有大量低级缺陷，是通过 12 轮视觉检查 + 3 轮声音检查才修成定稿的**：

| 轮次 | 发现的真实翻车问题（First Still / Early Render） | 量化修复动作（Fix） | 对我们的工程启示 |
|---|---|---|---|
| **Follow-up 1** | 监视器只占半屏且偏在一侧；首帧 11 格卡片只占画幅 42%；剃须刀像根黑木棍 | 监视器从 `1.6m` 扩至 `2.1m`，镜头推近 `0.5m`；首帧换长焦；刀片放大至 `0.30×0.16m` 亮钢材质 | 3D 空间里的构图比例必须靠抽帧视觉检查，模型盲写必偏 |
| **Follow-up 2** | 仓库长名字（如 `PySceneDetect`）冲出卡片边界并压住副标题 | 按字符数动态算字号：13 字符用 `125px`，8 字符用 `190px` | 动态排版必须写字符长度自适应函数 |
| **Follow-up 3** | `color-matcher` 默认 `hm-mkl-hm` 算法把天空弄出色阶断层（Posterized），且素材带旧 HUD | 改用干净素材 + 基础 `mkl` 算法 + 单帧参考 | 算法参数不能盲信默认，必须看真实输出图 |
| **Follow-up 4** | `Auto-Editor` 默认 `4%` 阈值在 263s 视频里只剪掉 2s（因为原片全程有底乐） | 阈值提到 `20%`，剪至 `3:57`（砍掉 26s），把真实数字印上屏幕 | 诚实展示工具边界：有 BGM 的视频必须提阈值 |
| **Follow-up 5** | `HyperFrames` 渲染的 `CUT BY CLAWD` 在 `300px` 下右侧出界；且 linter 报错缺 `@font-face` | 字号缩至 `228px`；补齐真实 `@font-face` 直至 `0 errors` | 调用子引擎必须跑通子引擎自带的 Linter |
| **Follow-up 6** | 吉祥物站在监视器前挡住了底部工具名（`"Real-E..."`） | **把名字条移到监视器最顶端（Top）**，监视器抬高 `0.14m`，角色永远只能挡到底部画面 | **黄金构图法则：前景有角色时，字幕/标题条一律放屏幕顶部** |
| **Follow-up 7** | 第一跳有 `0.5s` 半截身子出画；监视器边缘被切导致 `"drums"` 变成 `"rums"`；刀光过曝（`+90`）洗白画面 | 提前在 `1.52s` 落位；监视器缩至 `1.96m` 并让镜头正对监视器中心；刀光砍半至 `+48`、持续 `0.07s` | 摄像机运动过渡区最容易切边与出画 |
| **Follow-up 8** | 远景里 Clawd 的陶土橙（`#D97757`，目标 RGB `217, 119, 87`）暗成 `166, 81, 56` | 给主角单独加一盏 `9W` 小主光，材质 RGB 调至 `0.84, 0.165, 0.072`，实测成片 RGB 达 `213, 116, 82`（距离 `<5`） | Blender AgX 色调映射会压暗饱和色，必须从最终 MP4 吸色反推材质值 |
| **Follow-up 9–12** | 首尾循环接缝差 `3.7/255`（标尺和波形偏了 4 米）→ 修回退后因监视器余光反射仍有 `2.1/255`；全量渲染发现计数写成了 `"1 shots"`、星球越界、抠像残留细线 | 局部重渲 **74 帧**修掉 3 处穿帮；末尾加 **15 帧交叉叠化（Dissolve）回第 1 帧**，接缝降为 `0.0` | 局部错帧只重渲坏帧（74/1200 帧），不用全片重跑 2 小时 |
| **Sound 1–3** | 初版混音 `-18.1 LUFS` 过轻；前 2 秒 `-30 dB` 像死片；AAC 编码导致真峰值越界 | 前 2 秒加底鼓脉冲与军鼓滚奏；送入限制器前推 `+10.5 dB`，进 AAC 前预留 `-1 dB` 余量，最终 MP4 实测 **`-15.8 LUFS / -1.6 dBTP`** | **音频必须在编码后的 MP4 上测 LUFS 和 True Peak，不能只测 WAV** |

---

## 三、 引用长文拆解：《Design Engineering: Build a Motion Studio Around Opus 5.5》

主帖末尾引用的 X Article（`2117626780584431616`）讲的是另一件事：**如何用 Opus 5.5 搭建一个单人 UI 动效工程工作室**。核心流程共 5 步，全部给出了极简可运行代码：

1. **先定义动效语言（`MOTION.md` + 双端 Tokens）**：
   - 规定时长档位（`120ms / 240ms / 400ms`）、命名缓动曲线（`enter / exit / emphasis`）、弹簧参数（`sheet: stiffness 380, damping 32`）以及 `prefers-reduced-motion` 降级策略。每次会话作为项目指令喂给 Opus 5.5。
2. **用物理手感（Feel）而非实现细节描述原型，并暴露真机调参面板**：
   - 示例提示词：*“做一个感觉很沉的底部弹窗（Bottom Sheet）：向上拖拽有阻力，落位有轻微回弹，快速向下轻扫（velocity > 800）即使距离短也能关闭。”*
   - 关键工程动作：紧接着让模型把 `stiffness`、`damping` 和 `flick threshold` 暴露在一个 Debug 面板里，在真实手机上凭手感调参，而不是在提示词里盲猜数字。
3. **用零成本正则脚本卡住 CI（`scripts/motion-lint.ts`）**：
   - 扫描 `src/**/*.{css,tsx,ts}`，硬拦截 3 件事：① 裸写 `cubic-bezier(` 而不用 `--ease-*` 变量；② 裸写 `\d+ms` 而不用 `--dur-*` 变量；③ 严禁写 `transition: all`。
4. **用 Opus 5.5 做代码动效专项审查（`scripts/motion-review.ts`）**：
   - 将 `MOTION.md` 与组件代码发给 `claude-opus-5-5`，强制只检查 5 项：**是否动画了触发 Layout 的属性（如 width/height/top）、可打断性（Interruptibility）、`reduced-motion` 处理、焦点管理（Focus Management）、Token 使用率**，输出纯 JSON `{line, severity, issue, fix}`。
5. **留存动效决策记录（Motion Decision Records）**：
   - 每个组件写完后生成 4 行记录（Decision / Why / Rejected / Reduced motion），避免日后团队或自己反复争论“为什么用弹簧不用 240ms 补间”。

---

## 四、 对我们现有体系的吸收判断与落地动作

### 4.1 取舍表：哪些不搬、哪些立刻借？

| 模块 | 作者方案 | 我们的现状 | 决策：借还是不搬？ |
|---|---|---|---|
| **3D 渲染底座** | Blender 5 Cycles GPU（RTX 4060 渲 20s 耗时 2小时06分） | 本机虽已装 `Blender 5.2.1 LTS`，但主力短视频走 Canvas/WebGL/SVG（`science-video-daily` / `xilo`），长片走 `long-form-ai-explainer-film` + `cinecode` | **日更不搬 Blender Cycles**。2 小时渲 20 秒太重；只有做年度旗舰宣传片或需要 3D 吉祥物剧场时才调用本机 Blender 5.2 |
| **真机输出贴进屏幕（Screen-as-Light）** | 先真跑工具产出截图，合成序列帧贴在发光监视器上照亮桌面 | 我们做实测视频常直接平铺截图或录屏 | **🔥 强烈借用**：做 FDE 实测/开源工具对比视频时，先跑出真实终端/工具输出，再用 `UI Hero Shot` 贴在暗场发光屏幕上，真实感拉满 |
| **声学高潮公式（THE STOP）** | 在全片最高潮（第 11 刀）前，于混响之后硬切 **200ms 绝对静音（-88 dBFS）**，紧接 Sub Drop + A 小调长和弦 | 目前我们的视频配乐是连续铺底 + 人声闪避（Ducking），缺生理级节奏断口 | **🔥 立刻借用**：在 60–85s 深蓝硬数字短视频的「核心反转句」或「最终结论砸出」前 `0.2s`，加入 `200ms` 全轨静音断口（THE STOP），抓耳度翻倍 |
| **UI 动效 Linter + Review** | `MOTION.md` + `motion-lint.ts` + `motion-review.ts` | 我们有 `emil-design-eng`、`animate`、`review-animations`、`improve-animations` 技能，但在灵知前端仓缺 CI 硬拦截脚本 | **🔥 借入前端与代码动效门禁**：把“禁 `transition: all`、禁裸写 `ms/cubic-bezier`、禁动画 Layout 属性”加进前端 PR 自检 |
| **11 个开源音视频工具** | 11 个独立仓库拼装 | 已装 `ffmpeg 9.0.2`、已整合 `cinecode` 工具箱 | 按需单点调用：去背景用 `rembg`，拆伴奏用 `Demucs`，插帧超分走 `ncnn-vulkan` 命令行，不装冗余重依赖 |

### 4.2 可执行下一步

- [ ] **1. 沉淀为自媒体高潜选题（已同步归档至 `raw-sparks.md`）**：这条帖子是绝佳的「戳破 AI 营销神话 + 展示硬核工程审美」素材——外面都在无脑转发“11 个免费仓库替代 PR（连链接全是 404 都没人点开看）”，只有我们真的把它的 6 页 PDF 拆穿、用 `ebur128` 验出它 `-88 dBFS` 的 200ms 静音断口，并提炼出它背后 **12 轮量化返工的工程真相**。
- [ ] **2. 在下一条短视频 / 代码动画中实测「200ms THE STOP 声学断口」**：在关键数据反转前 200ms 切断 BGM 与混响尾音，实测留存提升。

---

*来自翡冷翠*
