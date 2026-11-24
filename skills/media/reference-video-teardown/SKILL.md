---
name: reference-video-teardown
description: "Use when mining a Douyin/XHS/B站/X video or account."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [douyin, xiaohongshu, transcript, whisper, fact-check, research]
    related_skills: [science-video-daily, ego-browser, content-grounding, video-content-automation]
---

# 对标视频拆解（爆款链接 → 挖掘报告 → 交给制作流水线）

## When to Use
用户贴抖音/小红书爆款链接，要"挖一下/拆解/对标做一期"。已定选题直接制作 → 用 science-video-daily。
用户贴的「一个视频」其实是**图文/实况多段片**（页面 SSR 脚本里出现多条 `douyinvod` 视频直链、各段时长之和明显小于配乐时长）→ 拆解走 `references/style-teardown.md` 的「抖音图文/实况」一节（多段逐个抽帧拼 `3xN` 联系表）；要复刻则转 `ai-story-video-director` 的 Step 3b（单张 char_ref 锚定 → 每镜尾帧 → 派生首帧），不要按正片写结构表、也不要试图拼成长片。
用户说"学习一下这个样例"、要的是**形式/视觉/配乐风格/剪辑节奏**而非复刻选题（典型：vibe知识大赏纯配乐动画片、高燃影视/歌舞片卡点混剪）→ 跳过第 3-4 步出处核查，走第 2b 步形式拆解，深度清单见 `references/style-teardown.md`；用户拍板要做同款卡点混剪时，转 `video-content-automation` 的 `references/beat-sync-mashup-pipeline.md` 执行。
用户贴一条 **YouTube 视频**说「对这个项目做深度调研」，而不要复刻内容 → 走 `references/youtube-channel-teardown.md`：yt-dlp 全量扫频道 → 标题聚类切出系列 → 播放列表当课程大纲 → 用搜索位次解释播放量 → 洗自动字幕当证据文件 → 落到机构官方页核履历。这类交付是台账式调研报告（HTML + MD），不是挖掘报告。
用户贴的是**账号主页截图/抖音号**，问"这号做什么、为什么流量大" → 走账号级拆解：`references/douyin-account-teardown.md`（全作品数据 → 抽 1-2 条头部原片验形式 → 流量归因）。用户不要求全量、只指出一项「他封面做得好 / 视觉表现力比我们强，分析原因」→ 同样走账号级拆解，但只做该文件的 2b（`video.cover` 独立封面资产 + 4×4 联系表）和 2c（时间线换挡点），报告直接上「他对 / 我们对」两列差距表 + 按性价比排序的落地顺序；封面与正片视觉公式引用 `vibe-music-only-shorts/references/cover-formula.md`，不要重写一套。
用户是拿**自家已做好的成片**说「视觉冲击力不够 / 太中规中矩 / 要突破，去看看抖音现在的优秀案例」→ 走 `references/visual-impact-benchmark.md`：按话题扫近两周热门 → 头部大号与低粉爆款各挑一半 → 逐条下载 + 4×4 联系表 + vision 四问 + 硬切点数 → 出「他有 / 我们对」六维差距表 + 3 条在自家渲染栈内可直接落地的路线，最后让用户拍板路线与试验田期数，拍板前不重渲。B站 UP 主 / 「B站怎么起号」→ `references/bilibili-account-teardown.md`（公开接口 curl 取数，不用浏览器）。
**TikTok / 海外号**（英文内容、银发/母婴/健身等海外赛道、AI 假人号）→ `references/tiktok-account-teardown.md`：不登录也能从页面源码 `__UNIVERSAL_DATA_FOR_REHYDRATION__` 拿到注册日、改名日、后台语言、完整外链、`aigcLabelType`，抖音那套接口一律不适用。
用户说的是**「调研这个案例 / 这人靠这个号躺赚」**，即要判断真伪而不只是复刻形式 → 先做变现链路审计 `references/monetization-claim-audit.md`（链接参数 → 卖方主体 → 反推销量 → 发帖人动机），再谈能不能抄。这类交付的骨架是「宣称 vs 事实」两列表 + 死坑/可学两栏，不是散文。
用户贴来**第三方给的爆款数据表/截图**（粉丝/点赞/倍数/发布日），问「数据真不真」→ 逐条上平台核对，流程见 `references/platform-landscape-survey.md`「核实第三方爆款数据表」一节；核完通常紧跟「拆这些片怎么做的」→ 走 `references/style-teardown.md` 的批量模式。
用户贴的片子**本身在教人怎么做内容/怎么做事**（怎么提高完播、怎么写开头、怎么起号、怎么谈价），要学的是它的结构与讲法 → `references/talk-method-teardown.md`：跳过出处核查，产出「结构时间码表 + 手法清单 + 迁移到自家选题的四种开头结构表」。这类片只有作者自述、没有一手研究，报告里自述数字一律标「无法验证」。
用户问的是**整个平台最近什么 AI 内容火/哪些账号**（不是单个号）→ `references/platform-landscape-survey.md`（数据源分级、视频号无公开榜的处理），挑出的头部账号再走账号级拆解。
用户说「借鉴抖音爆款重新做选题策划 / 按整个赛道重做起号方案」→ 同一个文件里的**赛道基准库**一节：自己抓 100-200 条同赛道原数据 → 算赞中位/转赞比/画幅时长/小号爆款 → 逆推结构出选题。**不要拿二手榜单转述或几个印象样本当依据**，选题策划必须有一张从自己抓的数据算出来的对标表。
链接是 **X/Twitter 帖子**（带视频或截图）：`curl https://api.fxtwitter.com/<handle>/status/<id>` 一次拿到正文、浏览/赞、视频 mp4 各码率直链和图片原图（`?name=orig`）；下载后按第 2b 步抽帧拆解。
  - **正文只是一个 `x.com/i/article/<id>` 链接时，那是 X 长文**：正文不在 `text` 字段里，先重拉 fxtwitter 看 `tweet.article`（`article.content` 的 Draft.js `blocks` + `entityMap` 才是正文，渲染方法见 `x2doc`）；只有 `article` 缺失才转登录态 handOff，流程见 `xitter` 的「X 长文」一条。评论区（nitter 单帖页）只能当旁证，汇报时必须标「旁证、非正文」，不要让用户以为你已经读过全文。
  - 用户问的是**「这个视频/动画是怎么做的」**，而片子是代码渲染或程序化生成（立体书纸艺、3D 漫游、代码风格动画、程序化弹跳/粒子）→ 答案在**作者开源的 Agent Skill / 仓库**里，不在分镜里：走 `references/code-art-technique-teardown.md`（追基建 → 只读 SKILL.md 硬规则 + `grep -n "^export "` 取 API 清单 → 起服务跑模板 → 抽帧验证 → 「一句话定性 + 链路分步 + 复现入口」报告）。先判清是**一键直出**还是**人带模型迭代数小时**，别把后者写成前者。该文件另附纸艺立体书（three.js pop-up）的完整参数配方，可用于直接复刻。
  - 用户问的是**「这个视频里是什么产品/网站/工具」**而不是要复刻：先做本体识别再谈拆解 → `references/product-identification.md`。顺序是画面字 → 作者自己的回复 → 作者主页另发的链接帖 → 仓库/站点实测；「演示概念 / 作者站点或仓库 / 是否已上线 / 是否已开源」四层分开报，空仓库不能说成已开源。小红书口令链（xhslink）的取数、`__INITIAL_STATE__` 读法与评论区证据层见该文件「小红书（xhslink 口令链）」一节。
  - **先算互动率再动结论**：用 fxtwitter 的 `views` / `likes` / `bookmarks` 算赞/浏览比。能力展示型案例常见「高浏览低互动」（<0.5%），这类帖子火的是题材（AI 能干什么），不是作品本身，报告里要写清，别照着它的数据预期自己的片。
  - **最高码率 mp4 可能下坏**：ffmpeg 报 `Invalid NAL unit size` / `Error splitting the input into NAL units` 时不要排查文件，直接换 720p 变体重下（`formats` 里挑 `1718x720` 那档）再抽帧——高码率那档偶发截断，低档反而完整。
  - 上传版**没有 audio stream 不代表原片没人声**（X 常剥音轨）。要判断有没有口播，只能从作者自述或去平台原帖看，不要凭 ffprobe 写「无人声」。
用户贴一条 X 链接或 @handle，说「分析这个博主所有关于 <某主题> 的推文/帖子」（要的是一个账号的整套观点与数据，不是单条片）→ 账号级全量语料拆解：`references/x-account-corpus-teardown.md`（全 timeline 含回复 + 回复配父帖 + 截图拼带标签联系表喂 vision + 自己反算隐含 RPM + 报告骨架）。
帖子里的涨粉/播放数字是转发者自述，去平台公开数据或媒体报道核一遍再写进报告。
形式拆解的产出要落到「我们怎么做」：参考片的视觉技法逐条对照自家引擎写差距表，再给差异化（常见：参考片只有画面、没有知识 → 每集加一个可核实的知识点）。

## Goal
用户贴来抖音/小红书分享口令或链接并说"帮我挖一下，我想做一期"。产出可直接进入制作的挖掘报告：原片数据与结构、逐字稿、一手出处、逐条证据分级、差异化角度。

## Success
- `~/HermesWork/抖音科普视频/_research/<slug>/` 下有 `挖掘报告.md`、`src.txt`（原片逐字稿）、一手出处文字稿。
- 每个数字都来自本次打开的原文；没打开的标「未核实」。
- 报告末尾给出 1-2 个待用户拍板的选择（角度/期数/首发哪条），然后停，不擅自开始制作。

## Procedure
1. **抓原片（ego-browser，单个 TaskSpace）**
   - 先用 `curl -Ls -o /dev/null -w '%{url_effective}\n' <短链>` 解出 `douyin.com/video/<aweme_id>`。在单个 ego-browser 脚本里**先调 `await page.cdp("Network.enable", {})` 再 `page.goto`**：抖音首次打开视频页就会直接发出 `aweme/v1/web/aweme/detail` 请求，无需二次 reload；遍历 `page.events()` 取该请求的 `Network.getResponseBody` 即可一次拿到完整 `detail.json`（含无水印 `video.play_addr.url_list[0]`、独立原声 `music.play_url.url_list[0]`、四项互动计数、粉丝数与创建时间）。
   - 若首次加载未捕获到 `aweme/detail`，再 `await page.events()` 清缓冲 → `page.reload()` → 等 ~8s 重取。不要自己拼 detail API 请求——缺 a_bogus 签名会返回空体或 HTML。
   - **短链解析出的是 `/note/<id>`（图文/实况）就不要再等 `aweme/detail`**：note 页根本不发这个请求（reload 两次仍是零条），`RENDER_DATA` 里只有 `app` 配置键、没有作品数据。改从 DOM 直取：`page.evaluate` 读 `Array.from(document.querySelectorAll('video')).map(v => v.src || v.currentSrc)` 拿到全部片段直链（末尾那条 `*.mp3` 是原声），再扫 `<script>` 文本里含 aweme_id 的 SSR 脚本、正则抓 `douyinvod.com` 直链（v11/v26 双域名各一套）。逐条 `ffprobe` 读 `duration`/`width`/`height`：各段时长互不相同（如 3.6/3.0/2.6s）且画幅一致 = 多段实况，不是同一镜的重复码流。
   - 下载原片与原声：`curl -sL -A "Mozilla/5.0" -e "https://www.douyin.com/" -o src.mp4 <video_url>`，原声同理存 `music.mp3`。
   - 抓不到可解析的 `aweme/detail`（或 `currentSrc` 为 blob / yt-dlp 报 403 Fresh cookies）时，从性能条目嗅探音视频分轨：`performance.getEntriesByType('resource').map(r => r.name).filter(n => n.includes('media-video') || n.includes('media-audio') || n.includes('video/tos'))`。抖音网页端常分别下发 `media-video-avc1` 与 `media-audio-und-mp4a`，分别带 `-H 'Referer: https://www.douyin.com/' -A 'Mozilla/5.0'` 用 curl 下载后无损合并：`ffmpeg -y -i v.mp4 -i a.mp4 -c copy src.mp4`。页面 innerText 里已有标题、四项计数、发布时间、作者粉丝，够写报告。
   - 多条片子一起抓：同一 TaskSpace 里 `Network.enable` 一次，循环 `page.events()` 清缓冲 → `goto(/video/<id>)` → 等 8s → 取 `aweme/detail`，每条落 `<id>.detail.json`，再用 python 统一读 `statistics.digg/comment/collect/share_count`、`video.width/height`、`duration`(ms)、`music.title` 并 curl 下载。
   - 抖音页面 `page.goto` 常因 load 事件迟迟不来抛 `PageNavigationTimeoutError`（导航其实已提交）：循环里一律 `try { await page.goto(...) } catch(e) {}` 再 `waitForFunction`/`waitForTimeout`，否则一条超时整批中断。
   - 结束 `await task.finish({keep:[]})`。
   - ego-browser nodejs 进程的 cwd 是只读的：`fs.writeFile` 一律用绝对路径（`~/HermesWork/.../_research/<slug>/`），否则 EROFS 且本轮抓到的事件已被 `page.events()` 清空，要 reload 重抓。
2. **先看 `aweme_detail.desc` 再决定要不要转写**：作者自己贴的发布文案常是整篇论证的浓缩版（分段、比喻、数字与「章节要点」时间码对得上），十几分钟的长片可就此写成结构表、省掉 Whisper，报告开头注明「内容依据：作者发布文案（与口播章节一致）+ 自动章节 + 抽帧，未跑逐字稿」；文案只有标题 + 标签时才转写。判断标准与例外见 `references/talk-method-teardown.md` 第 2 节。
2.1 **转写**：`ffmpeg -i src.mp4 -ar 16000 -ac 1 src.wav` → `whisper src.wav --model large-v3-turbo --language zh --output_format txt --initial_prompt "以下是普通话简体中文。<专有名词>"`。十分钟内的片子要几分钟会转后台；等待期间做第 3 步。完成后删 wav。同音错字多，逐字稿只作线索：**专有名词和学科词必错**，用抽帧读到的屏幕字卡/例子截图回校，并在报告里列「误听 → 正字」映射（否则拍板后写脚本的人会把错词抄进成稿）。
   - 先判断有没有人声：只切 20-30s 片段跑 `--model small` 快速探测。Whisper 对纯配乐片会幻觉出歌曲署名（"作词 作曲 XXX"）、字幕组落款（"字幕by…"）、"请不吝点赞订阅"或一两个孤字，这类输出说明原片只有音乐，不是逐字稿，不必再跑全片 large 模型。此时信息在画面字：`analyze_video.py src.mp4 --out ref` 出抽帧拼图看结构，再 `ffmpeg -ss <t> -i src.mp4 -vf crop=W:220:0:20 -frames:v 1` 裁出顶部文字条逐段识读（拼图缩小后小字读不清）。
   - 电影混剪/台词金句片：背景 BGM 极大时 Whisper 会陷入重复 token 幻觉或吞句。此类视频文字已烧录在画面中，直接抽帧做 OCR 是最准的地基：`ffmpeg -y -i src.mp4 -vf "fps=1/2,scale=640:-1" frames/f_%03d.jpg`，再用 `paddleocr`（`PaddleOCR(lang='ch').predict(img)`）识别，可直接一次性提取完整双语台词、出处片名及年份角标（如《银河补习班 (2019)》），再以 ASR 的时间轴作为辅助校验。
2b. **纯配乐片与高燃卡点混剪的形式拆解**
   - **切点用 ffmpeg 量，不要靠肉眼数格子**：`ffmpeg -i src.mp4 -vf "select='gt(scene,0.05)',metadata=print:file=-" -f null -` 输出 `pts_time` 就是镜头切点（CG 漫游/慢转场用 0.05；MV/电影快剪用 0.10–0.20 过滤闪白与全片切点）。有了切点表，分镜表（每镜秒数、硬切还是长镜）一次成文；「每镜 3 秒硬切 + 结尾一个长镜」是 CG 漫游类最典型的节奏，「中位 0.5–0.6s 连切 + 段落呼吸长镜」是卡点混剪的典型节奏。
   - **先判「全帧变形」还是「局部运动」，再定复刻路线**：高质感镜头里最难分辨的一类是「只该动的地方在动、其余像素纹丝不动」（雨丝、水面反光、车灯扫过）——这类是静态插画底 + 合成/代码局部特效，能纯代码复刻，成本极低；全帧都在缓慢蠕动的才是生成式视频，代码只能近似材质，不要答应 1:1。量它：按 8–10 fps 抽 PNG，叠成 (N,H,W) 算逐像素时域标准差，看 `(std>2)` 的像素占比和 std 图上还剩多少成片静态区。局部孤立亮斑 = 插画底 + 特效；连本该不动的天空、墙面、皮肤都有几级抖动、边缘还在蠕动 = 生成式。std 图本身就是运动热图，存成 `motion_heatmap.jpg` 附进报告，比一句「画面很高级」有用得多。阈值只是起点，压缩噪点和胶片颗粒会把占比抬高，下结论看静态区有没有守住。
   - **卡点混剪（Beat-Sync Mashup）的量化拆解**：切点密度高（每镜 <1s）时，不要按固定秒数抽帧（会漏镜或跨镜），改按 `cuts` 时间戳取**每镜中点** `(t[i]+t[i+1])/2` 抽帧拼成 7×7 联系表（`references/style-teardown.md`「高燃卡点混剪拆解与复刻方案」），并用 22.05kHz 单声道 WAV 的 20ms 窗口 RMS 正向差分峰值测算「切点与音频瞬态峰值（Onset Peaks）的中位误差（ms）与 ≤50ms/80ms 咬合率」。
   - **片子若自称真 3D，用「素模 Pass 对齐」验，不靠观感也不听弹幕**：把画面切成灰白白模的那一小段按 0.3s 抽帧放大，看分界线——笔直锐利无羽化、跨边界的树干/车身/地面投影左右轮廓严格对齐 = 同一场景渲两遍（Beauty + Clay override）后期合成；再放大骑手四肢是柱体、头盔是光滑球 = 程序化低中模。AI 视频做不出跨帧完全对齐的素模 pass；评论区高赑「肯定是 AI 做的吧」不构成证据。复刻路线转 `blender-3d-scene-video` 的 `references/photoreal-street-render.md`。
   - **制作证明段 OCR**：作者自证「这是真 3D 不是 AI 生成」的片子，信息公开在结尾几秒的屏幕录制里（Blender 集合面板、代码行数）。单帧看不清就 `ffmpeg -ss <t> -i src.mp4 -frames:v 1 -vf "scale=2400:-1,eq=brightness=0.12:contrast=1.4"` 放大提亮，再 `tesseract img - -l chi_sim+eng --psm 11`——`--psm 11`（稀疏文本）才能读出散在视野里的角标，默认模式全丢。这类 OCR 能直接抄出「集合 1/5 · 55 个物体 · 1,415 个几何节点实例」「14 个脚本，5,077 行」这类硬数字，是报告里最值钱的一行。
   - **有没有烧录字幕，也用 OCR 判**：随机抽 8-10 帧跑 tesseract，输出全是乱码/单字 = 无字幕；有连续中文短句 = 有字卡（再按位置裁条逐段读）。
   - 抽帧拼图：`ffmpeg -vf "fps=1/3,scale=360:-1" frames/f_%03d.jpg` → `ffmpeg -framerate 1 -i frames/f_%03d.jpg -vf tile=8x3 -frames:v 1 sheet1.jpg`（第二张用 `-start_number 25`）。不要在 tile 链里加 drawtext 标帧号——本机 ffmpeg 可能未编译该滤镜；按"第 N 张 × 3s"推时间即可。拼图直接用 vision 看，两张就能读出全片结构和顶部字幕。
   - 配乐识别：在 scratch 建 venv 装 `shazamio`，从 src.mp4 切 3 段（开头/中段/结尾各 15s，`-vn` 存 mp3）分别 `Shazam().recognize()`，取多数结果；单段命中不同曲名标「疑误识/未核实」。
   - 响度曲线：`astats=reset=30` + `ametadata=print:key=lavfi.astats.Overall.RMS_level` 抽样，找配乐抬高点，对齐到画面段落（高潮通常对着反转/结论段）。
   - 计数比例判类型：分享/赞高（≈40%+）= 情绪共鸣转发型；收藏/赞高 = 清单收藏型。
3. **追一手出处**
   - 二手解读片（"看完 XX 两小时访谈"）先定位原访谈：`web_search` 人名+月份+片中论点关键词。YouTube 页用 `web_extract` 自带章节时间码和全文字幕（全文存缓存文件），按 `[h:mm:ss]` 切出各论点原话。
   - 每个论点找原始研究：PubMed 摘要页最省（样本量、效应量、适用人群都在摘要里）。抓取拿到 reCAPTCHA 页时改走 Europe PMC REST：`https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query=EXT_ID:<pmid> AND SRC:MED`（或 `DOI:<doi>`、`TITLE:"..."`）→ `abstractText`，摘要存进 `<期>/sources/`。论文全文 PDF 常挂在作者机构页（researchmap/个人主页），全文里的结果段和表格比摘要多出反直觉数字，值得找。再搜 `<论点> experts skeptical` 找反方采访。
4. **逐条核查表**：论点 / 原话要点 / 一手研究数字 / 证据强度（强·中·弱·无）/ 原片问题。重点标：原片数字与论文不符、漏掉关键条件（时机/人群/样本量）、把"亲测"当证据。
5. **角度与形式**
   - 收藏/赞比高 = 清单收藏型；热评常是"帮我总结成 N 条"。
   - 默认差异化：同一组论点按证据硬度排名 + 点出原片错误（天然反常识钩子），而不是再抄一遍清单。
   - 短视频一期一概念 → 多论点时建议拆系列，首发选证据最硬且最好做代码动画的那条；合集版作备选。
6. 写 `挖掘报告.md`，向用户汇报结论 + 待拍板项 + 文件路径。拍板后转 `science-video-daily`（个人号竖屏）、`health-code-shorts`（公司健康号代码短视频）、`long-form-ai-explainer-film`（横屏长片）、`video-content-automation`（高燃卡点混剪+剪映草稿），或 `blender-3d-scene-video`（真实 3D 场景片：参考片是 Claude Code/Blender 类「AI 造场景」案例时走这条）。
   - 公司号的拆解放 `~/HermesWork/灵知营养短视频/_research/<slug>/`，不放个人号目录。
   - 复刻 = 保留原片骨架（钩子 + N 段 × 秒数 + 每段字卡格式），把原片无出处的功效话术（中医术语、"气血不足"类）换成可核实的动作要点/研究结论；给 2-3 个画面方案 + 推荐，等用户拍板。

## 配乐（用户偏好：知识大赏类只要经典/热门配乐，不配人声）
- 拍板项默认给两个方案：A 成片不带音乐，抖音发布时在 App 曲库挂同款/热门钢琴曲（推荐：版权稳、蹭音乐流量）；B Pixabay 免授权曲（多平台通用，授权摘要存 music/）。不要把 Shazam 识别出的商业曲直接混进成片。
- 用户要求「开头配乐和样片一样」时：从 `aweme/detail` 的 `aweme_detail.music.play_url.url_list[0]` 下载原片抖音原声 mp3（128kbps，时长和原片一样；curl 加 `-e https://www.douyin.com/`），存到 `<期目录>/music/`，只用来在本地对节奏。发抖音时在 App 里打开原片 → 点音乐 →「使用」挂上同一段原声。视频号不能用抖音原声，单独导出一版压入方案 B 的曲子。
- 找原曲完整版：抖音网页搜索要登录 → 开 ego TaskSpace 打开搜索页 → `task.handOff()`，让用户扫码登录 → `takeOverTaskSpace(id)` 接回。登录后搜索：`Network.enable` → `page.events()` 清缓冲 → `goto(/search/<q>?type=general)` → 等 9s → 收集 URL 含 `search` 的响应体 → 在 JSON 里递归找含 `play_url.url_list` + `title` + `author` 的 music 对象（标题/作者/时长/mp3 直链），一次可拿到十几个同曲原声。多换 2-3 个关键词（曲名+slowed/完整版/remix 艺人）。
- 候选去重选版：Shazam 对同一旋律的不同剪辑会报出不同曲名/艺人（如《若如初见》= We Never (Remix) = We Never Beat，曾被误认成 Akinari），曲名以抖音曲库/原声描述里的写法为准，别信单次 Shazam 署名。要判断哪个完整版最接近样片，用 numpy 做 48 段对数频带谱的滑窗余弦相似度（取样片 15s 片段在候选里找最大值）；同一录音会到 0.95+，0.7-0.9 只是同曲不同剪辑。没有候选到 0.95 = 创作者自己剪过，要开头完全一致只能用样片原声。候选同样切 40s 跑 Whisper small 确认无人声（只出 "Thanks for watching" 类幻觉 = 纯音乐）。
- 文件落 `<期目录>/music/`：主用原声 + `cand/` 按「完整版A/B/C_时长_来源_特点」命名，并写 `配乐说明.md`（曲名别名、每个文件用途、抖音/视频号发布方式）。

## Constraints
- **视觉/封面类拆解的交付物是「管线改动 + 一期实测」，不是报告**（用户 11-10 拍板）：交完「他对 / 我们对」差距表后，把每条差距落到自家引擎里（公共组件、封面生成器），再拿刚刚做好的一期当试验田重渲，抽帧摆出 v1/v2 对比才算完。只写「建议借鉴」等于没交付。重渲前先归档旧成片（`cp video.mp4 video_v1_old.mp4`、旧封面/旧预览一并留），汇报里写清哪些是已渲染验证的、哪些还只改了代码。
- 原片的补剂/带货/引流段落不做（个人账号不做健康带货）。
- 不复用原片画面/人声；`src.mp4` 仅作参考，脚本只引一手出处。
- 二手解读里的数字一律不信，以论文摘要为准。

## Pitfalls
- **拼图帧序按字典序排，不按时间序排**：`ffmpeg -pattern_type glob -i 'hi/t*.jpg' -vf tile=` 读入的是文件名字典序，`t0.5` `t108` `t112` … `t2` `t24` 会把 0.5s 与 108s 排在一起。要么文件名补零（`t000.5` `t108`），要么先把顺序写在提示里交给 vision；按「第 N 帧 × 间隔」推时间只在 `f_%03d` 连续编号时成立。
- **口播片切点阈值用 0.15**：`select='gt(scene,0.05)'` 会被口型微动和背景微光刷出几百个假切点，算出的「平均每镜秒数」毫无意义；口播干货片 0.15 起才接近真实剪点。
- **抖音页面 innerText 自带「章节要点」AI 大纲**：可直接当段落骨架省掉手工切段，但它会把原话改写成书面语、也会漏段，必须用逐字稿逐段核对后再写进结构表。
- 抖音/视频号页面一律走 ego-browser（用户已登录的浏览器）；通用 browser_exec 新开的无登录浏览器会直接落到滑块验证码页，不要去解。
- **vision 读联系表报连接错误时，改喂那张表里的单张原图**：同一张大图原样重试会连续失败并触发 loop 警告，小图能过、读到的内容一样；另把联系表控制在 2×2（4 格），格子越多单格分辨率越低，后台 RPM/日期/订阅这类小字先读错。
- X 的会话页/回复页不要 `snapshot({scope: "full_page"})`：Conversation DOM 极大，一次吐几十 KB 的导航与推荐位噪音。用 `page.evaluate` 遍历 `article` 取 `innerText`，一行拿到原帖与全部回复的正文、作者、计数。
- 二手爆款数据表、转发帖、"某人靠这个号赚了多少"类表述，一律先上平台核一手数字；**先看它 bio 外链的完整参数再定性商业模式**：`maas=maas_adg_` + `ref_=aa_maas` 是 Amazon Attribution（品牌备案卖家自建站外归因），不是 Associates 联盟链，把前者说成"个人挂联盟链躺赚"是定性错误。
- 账号级拆解前先 web_search 新榜「涨粉周榜」/媒体报道确认账号确有数据；单条爆款占总赞 >90% 时，报告必须写成「单点爆款而非账号能力」，别把爆款配方当账号稳定公式。
- 视频号助手需「微信快捷登录」时，点按钮后要用户在手机微信确认；它只有本账号数据、没有全站榜，别承诺能从中查爆款账号。

## Stop
- 论点找不到一手研究 → 标未核实，建议不用，不自行补数字。
- 页面要登录/验证码 → `task.handOff()`，告知用户。
