# 抖音账号级拆解（主页截图/抖音号 → 全作品数据 → 流量归因）

用户问"这个号做什么、为什么流量大"时用。产出放 `~/HermesWork/抖音科普视频/_research/<账号slug>/`：`posts.json`、`profile.json`、1-2 条头部原片、`挖掘报告.md`。

## 1. 找主页（截图里只有抖音号时）
`page.goto("https://www.douyin.com/search/<抖音号>?type=user")` → 等 6s → 取 `a[href*="/user/MS4w"]` 中 innerText 含该抖音号的那条，`href.split('?')[0]` 即主页（sec_uid）。不要拼 user API。

## 2. 全作品数据：拦 aweme/post 接口
- `Network.enable` → `page.events()` 清缓冲 → goto/reload 主页 → 等 6s。
- 每次滚动后**立刻 drain**：过滤 `Network.responseReceived` 且 URL 含 `aweme/v1/web/aweme/post`（作品）或 `user/profile/other`（资料：signature/follower_count/total_favorited/aweme_count/user_age），逐个 `Network.getResponseBody`。攒到最后一次性取 body 会报 "No resource with given identifier"——requestId 很快失效。
- 字段：`aweme_id, desc, create_time, video.duration(ms), statistics.{digg,comment,collect,share}_count, is_top, music.title, video.play_addr.url_list[0]`。按 id 去重写 `posts.json`。
- 滚动用 `page.mouse.move(600,600)` + `mouse.wheel(0,2500)` × 8，每次等 2.5s。通常能拿到 ~20 条；再滚不出时不硬磨，报告里注明"抓到 N/总数，缺最早几条"，可用主页截图补充标题。DOM 的 `a[href*="/video/"]` 末尾会混入推荐视频，不要当作者作品。

## 2b. 封面是独立资产：抓 `video.cover`，不要拿 `origin_cover` 充数
用户说「他封面做得好」时，关键事实是**主页 3:4 封面 ≠ 视频首帧**：`video.origin_cover` 是第一帧，`video.cover` 才是主页九宫格展示的那张，好账号会单独出一张海报。
- 从已存的 `posts_full.json` 拿 `video.cover.url_list[0]` 批量 curl（带 UA + Referer），存 `covers/<aweme_id>.jpg`；一次抓 12–16 张足够看出套版规律。
- 拼成 4×4 联系表（每格约 300×400，留 2px 缝隙）一次交给 vision：**一张图就能读出「版式（左对齐/居中）、文字层级、主色数量、主图是具象还是抽象、落款位置」五件事**，比逐张看快。按 `create_time` 排序，第 1–3 行放最近 12 条、末行放历史爆款，可同时看迭代方向。
- 自己的封面也要取同一张对比图放报告里（`cover/preview.jpg`）：**差距表必须是「他对 / 我们对」两列**，只说人家好、不说自己哪一步做错，用户无法据此改模板。
- 封面差距的可复用判据：文字左对齐 vs 居中、一张封面几种主色、主图能不能一句话说出「这是什么」（抽象点阵 = 不行）、封面上印没印网址/日期。成体系的公式已沉淀到 `vibe-music-only-shorts/references/cover-formula.md`，报告里直接引用、不要重写。

## 2c. 先拉时间线找「换挡点」，再谈流量归因
账号流量阶跃几乎总是跟着**形式变更**走，而不是内容变好。按 `create_time` 升序打一行一条的时间线（日期 / 画幅 / 时长 / 有无口播 / 主要话题标签 / 三项计数），肉眼就能看出分段：
```python
for i,p in enumerate(sorted(posts, key=lambda x: x['create_time']), 1):
    v=p['video']; print(i, datetime.fromtimestamp(p['create_time']).date(), f"{v.get('width')}x{v.get('height')}", (v.get('duration') or 0)//1000, p['statistics']['digg_count'], p['desc'][:40])
```
- 画幅（1920×1080 ↔ 1440×2560）、时长（4–8 分钟 ↔ 145–215s）、有无口播、标签体系（是否挂 `#vibe知识大赏` 这类扶持话题）四列变化对齐日期，报里写成「第 N 期起换挡 → 此后 M 条里出了哪几个爆款」。
- 只在最新一段里取「日常款」中位赞当账号当前水位，**不要用全号均值**——被 1–2 条百万赞拉高的均值会把结论带偏；同时点明是否单点爆款（单条占总赞 >50% 就要写）。
- 数据里看不出换挡原因时（如为什么 4 分钟长片变 150s），标「推断」，不要写成作者自述。

## 3. 用 Python 汇总（别心算）
按赞排序；算总赞、中位数、平均时长、前 3 条占比、收藏/赞、转发/赞；按日期看更新频率和近期是否回落。

## 4. 抽 1-2 条头部原片验形式
- 进 `/video/<id>`，同样拦 `comment/list`（热评 text/digg_count）和 `aweme/detail`（music、play_addr）；没有就读 `<video>.currentSrc`。curl 带 UA+Referer 下载。
- `ffprobe` 看横竖屏/时长；`ffmpeg -vf "fps=1/8,scale=360:-1,tile=6x3" -frames:v 1 grid.png` 出拼图（**必须 `-frames:v 1`**，否则 image2 报重复文件名），再截 1-2 张全尺寸帧，用视觉判断：代码渲染动画 vs AI 生图 vs 实拍，字幕位置。
- 人声探测按 SKILL.md 第 2 步（短片段 + small 模型，看是否幻觉）。

- **无口播长片（5 分钟级、字幕+配乐）还原结构**：`ffmpeg -vf "fps=1/6,crop=1920:300:0:700,eq=brightness=0.1:contrast=1.5"` 裁底部字幕条 → `tesseract -l chi_sim --psm 6` 逐 6s 出文，再用 `fps=1/5` 的 6x5 拼图看画面段落；OCR 错字多，按文意校正、只当结构依据。写成「时间段 → 讲什么 → 用的类比」的分段表，并记录每段信息点间隔、公式出现次数、开头/结尾是否同一钩子闭环。切点用 `scene>0.15`，长镜头动画片只有个位数切点是正常的。
- 热评抓取：同一 TaskSpace 打开 `/video/<id>`，拦 `comment/list`，滚 4 次并每次 drain，可得 ~180 条；按赞排序读前 25，统计「BGM/音效像X」类评论条数，作为配乐是情绪核心的证据。
- 头部原片 4K/60fps 可达 200MB，curl 直接下即可，无需转码。

## 4b. 话题级对标（不是某个账号，而是「某话题下谁起号成功」）
- `Network.enable` → 依次 goto `douyin.com/search/<话题词>?type=video&sort_type=1`（换 2-3 个关键词），每次等 7s + 滚 5 次、每次 drain，过滤 URL 匹配 `search/(item|general)/` 的响应；JSON 里 `data[].aweme_info` 即视频（含 `author.follower_count`、`statistics`）。一轮可得 ~180 条/150 个账号。
- 汇总时**同时按单条赞和按账号累计赞排序**，并把「现粉丝数」放进表：粉丝 <1 万而单条 50 万+ 赞的号 = 爆款靠内容不靠账号的证据；同一账号多条上榜才是可复制的能力。注意粉丝数是现在的，不是起号时的，幸存者偏差要写进报告。
- 取 Top10-12 原片逐条 curl 下载；**先判有没有人声**：对每条只切 5–35s 跑 `whisper --model small`，一条超过 60s 就 `timeout 60` 包住，别把整批串在一个 terminal 调用里（会撞 420s 上限被杀）；出现歌词署名/字幕组落款/重复单字 = 纯配乐。转写没出结果的不要下「无人声」结论，写「未测」。
- 画面拼图：每条 `fps=1/9,scale=200:-1,tile=8x2` 一张，再逐张 vision；一次只下 4–6 条别全量。

## 5. 话题/扶持核查
对文案里的话题标签 `web_search "#<标签>" 抖音`，确认是不是多账号共用的赛道话题、官方活动（如新星计划类）。查不到官方规则的扶持，写"可能，未核实"。

## 6. 报告结构（中文、纯文本给用户）
账号概况 → 数据（头部集中度、收藏/转发率、近期趋势）→ **形式时间线与换挡点** → 视频形式（画幅/时长/人声/BGM/画面技术）→ **封面横向对比表（他对/我们对）** → 选题公式（题材 + 钩子写法）→ 流量原因（标明"推断"）→ 风险与未覆盖项 → 对用户自己号的可借鉴点（按性价比排序，先改不碰时间轴的那项）+ 一个待拍板的下一步。热评里关于 BGM、"高智感"、同类博主增多的评论是归因的直接证据，引用它们。
用户只问「分析下为什么他的封面/视觉更好」时，报告不必从账号概况写起：直接上「他对 / 我们对」差距表 + 落地顺序，把数据与素材路径放到附录。

## 7. 用户说"照这种方式出一期"
- 先 `ls ~/HermesWork/抖音科普视频/` 读已有各期 episode.json 首句，排除自己做过的和对标号做过的题，再一次 clarify 同时问：选题（4 个候选，带生活钩子、可动画化）+ BGM 来源（对标号的版权曲有静音/限流风险，推荐免版权曲）。
- 把对标号与已发片的差异点列成实验变量（画幅、有无人声、配色、时长、钩子类型），转 science-video-daily 的 vibe-landscape「无配音·纯音乐变体」执行。
