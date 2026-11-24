# Demo 宣称能力核验：从一条社媒视频到一句可拍板的判断

触发：用户丢一条 X / 小红书 / YouTube demo，问「这个新模型做 X 的能力究竟如何」。这里只写**核宣称**这一步；视频本身的下载、抽帧、转写手法复用 `reference-video-teardown`。

## 1. 取最高码率原片

X 帖走 `curl https://api.fxtwitter.com/<handle>/status/<id>`，从 `tweet.media.videos[].variants` 里挑 `avc1/1920x1080` 那一档（直链形如 `video.twimg.com/amplify_video/<media_id>/vid/avc1/1920x1080/<hash>.mp4?tag=29`）。

```bash
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,nb_frames v.mp4
```

`Invalid NAL unit size` / `Error splitting the input into NAL units` 时不要排查文件，直接换 720p 变体重下再抽帧。

## 2. 抽帧：均匀抽，不指望切点

演示片通常是整段连续动画，`select='gt(scene,0.05)'` 返回 **0 个切点**是正常的，不是命令坏了。

```bash
ffmpeg -y -i v.mp4 -vf "fps=1/6,scale=1280:-1" frames/f_%03d.jpg
ffmpeg -framerate 1 -i frames/f_%03d.jpg -vf tile=4x5 -frames:v 1 sheet.jpg
```

拼图只用于看结构和讲法（章节顺序、有无空镜、结尾是否草收）。**任何数字都回单帧、回原分辨率读。**

## 3. 数字读法（本模式最容易翻车的一步）

```bash
ffmpeg -y -ss <t> -i v.mp4 -frames:v 1 full.png
```

再 `vision_analyze(image_url=full.png, question="读这一块的全部文字与数字，逐字抄", region=[x1,y1,x2,y2])`——`region` 用**原图像素坐标**，裁切保留全分辨率。整帧缩放会把 `10²¹` 读成 `10²²`、把 `47.2` 读成 `49.3`，这类差值恰好就是报告的核心结论。

OCR 兜底：`tesseract full.png - -l chi_sim+eng --psm 11`（稀疏文本模式才能读到散落角标）。

## 4. 口播与画面分开核

```bash
ffmpeg -i v.mp4 -ar 16000 -ac 1 a.wav
whisper a.wav --model large-v3-turbo --language en --output_format txt
```

三路数经常互相打架：画面标 `4.4x`、口播说「约四倍」、原文写 `approximately three times`。三者不一致时以原文为准，并把「画面 / 口播 / 原文」三列都写进报告——这组矛盾本身就是「demo 是模型现算的、没人核过数」的证据。

## 5. 回原文对账（脚本化）

取论文/文档的可解析版本（arXiv HTML、alphavxiv、`docs…/llms.txt`），然后：

```bash
python3 scripts/number_audit.py paper.html 47.2 49.0 "1.04" "4.4"
cat frame_numbers.txt | python3 scripts/number_audit.py paper.html -   # 从 stdin 读待查串
```

判读三条：
- **命中 0 次** → 该数来自别处，或写了量级（最先怀疑这个）。
- **命中多次** → 要挑对是哪一节的表，不能拿摘要里的同一个数当图表里的那个数。
- **命中但措辞不符** → 原文写 `approximately three times` 而 demo 画 `4.4x`，属于改写失真，不是数据错误，要分开定性。

## 6. 成本台账

按可信度排：作者自己贴的账单/截图 > 作者口述的耗时 > 第三方长测推算。必记四项：墙钟、input/output token、cache read、是否用了 subagent / 并行。

交叉项：第三方 benchmark 的分与它的步数/耗时并列写。分高但步数是对手数倍（例：同一个测法里拿了最高分，却花了 `431 分钟 / 1,128 步`，对手 `109 分钟 / 244 步`），结论就是「长程思考型，适合离线批量，不适合交互出片」。

## 7. 可用性台账

| 层 | 探针 | 结论写法 |
| --- | --- | --- |
| 订阅端点 | `GET <base>/v1/models` | 只在这里出现 = 仅订阅可用 |
| 通用/按量端点 | 同上再打一次 | 两处都在 = 接口层已铺开 |
| 官方文档 | `docs…/llms.txt`、model card、blog | 404 或停在上一代 = 文档滞后于接口 |
| 开源权重 | HF 组织页 | 无仓库 = 未开源，不拿榜单分栏推断 |

四层分别写，缺哪层就写明缺哪层。

## 8. 报告骨架

1. **一句话结论**：能力定性 + 是否独有（「属第一梯队但不是独有能力」比「很强」有用）。
2. **实测**：抽帧联系表 + 数字对账表（demo 值 / 原文值 / 判定），把抓到的量级错误明确写出来。
3. **模型底牌**：架构变化、输入模态（视频/图像输入是「能看懂自己渲染的帧」的唯一证据，别从 demo 反推）。
4. **真实代价**：墙钟、token、步数、可用性四行。
5. **判断与落地**：对自家哪条管线有用、什么场景用、什么场景别用。

## 9. 坑

- **归属信息在回复区，不在正文。** 作者本人可能只是转发别人的 demo；「首页之前一直是 Opus 做的，这次刚试新模型」这类关键句只在回复里。
- **厂商「对标 2-3T 参数」是体感宣称。** 没有公开跑分表、只公布小模型对照实验时，写「官方自述」，不写「实测对标」。
- **别把 demo 的形式当模型能力。** 3Blue1Brown / Manim 工程风的稳定输出，多半来自作者沉淀的分镜脚手架与设计系统；换模型能跑通只证明「可替换进该管道」。
- **同一作者的历史 demo 就是对照组。** 翻他最近几条同类帖，能直接看出这次是「模型更强」还是「管道更熟」。
