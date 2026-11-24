# YouTube 频道 / 创作者「项目」深调研（yt-dlp 全量扫 + 台账式报告）

用户贴一条 YouTube 视频说「对这个项目做深度调研」时，「项目」通常不是那一条片，而是它背后的**系列 / 课程 / 人**。先摸清三层结构再动笔，否则会把一条教程写成孤立案例分析。

## 1. 频道全量落盘（先数清楚，再筛）

```bash
OUT=~/.hermes/cache/scratch/<slug>_research
yt-dlp --flat-playlist --print "%(id)s\t%(title)s\t%(duration)s\t%(view_count)s" \
  "https://www.youtube.com/@<handle>/videos" > $OUT/channel_all.tsv
wc -l $OUT/channel_all.tsv
```

`--flat-playlist` 不解析每条页面，千条量级也在十几秒内完成；但 **`view_count` / `duration` 在 flat 模式下常为空或过期**，凡要写进报告的数字，必须再用逐条模式补一遍：

```bash
yt-dlp --skip-download --print "%(id)s|%(title)s|%(upload_date)s|%(duration)s|%(view_count)s|%(like_count)s|%(comment_count)s" <url1> <url2> ...
```

结果追加进一个 `yt-meta-summary.txt`，报告里的每个播放量/日期都从这个文件里取，不要回读 flat 文件。

## 2. 用标题正则切出「系列」

对全量标题跑一次聚类（`ORIENTATION|EPIC|DAX|RESIDENCY|<主题词>`），看命中条目的 `upload_date` 是否成簇（同一天/相邻两天批量上传 = 一套课程被一次性搬上来）。这一簇才是「项目」的本体，目标视频只是其中一集。同时算一下：簇内播放量第一名 ÷ 第二名，倍数 >10 说明流量来自单条被搜索命中，而不是频道整体势能。

## 3. 播放列表 = 课程大纲（比视频标题信息量大）

```bash
yt-dlp --flat-playlist --print "playlist: %(playlist_title)s | id: %(playlist_id)s | n: %(playlist_count)s" \
  "https://www.youtube.com/@<handle>/playlists" > $OUT/playlists-summary.txt
```

播放列表名会直接暴露身份：培训住院医的「RESIDENCY HUB」、按技术分的「HVLA / OCS / 等速测力」模块、以及独立的「AI in Clinical Practice」。把这些名字里的机构名、技术名当成关键实体，回头去搜机构官网与作者履历。

## 4. 流量归因：用搜索位次解释播放量

小频道（几千订阅）单条几十万播放，几乎只有一个来源——被搜索命中。取证方式：对核心词跑两次不同表述的搜索（例：`<主题词> tutorial`、`<主题词> for new nurse`），把结果顺序写进 `ytsearch-summary.txt`，记录目标视频排第几、榜首是谁、榜首播放量多少。**这比「算法推荐」这类猜测可靠**：位次是第一手观测，推荐是推断。两份快照互相印证后再写进报告。

## 5. 字幕当证据文件，先洗再引

yt-dlp 自动字幕的 VTT 带内嵌时间标签，且同一句会因逐词时间轴重复多次：

```bash
yt-dlp --skip-download --write-auto-subs --sub-langs "en.*" --convert-subs srt -o "$OUT/src" <url>
# 洗：去 <00:00:01.234> 类标签、去行号箭头、按行去重后合并成 transcript-clean.txt
```

洗过的 `transcript-clean.txt` 才是 `sources.py quote --from` 的证据文件；直接拿原始 vtt/srt 当证据，逐字校验会因时间标签与重复词全部失败。逐字稿只用于引语与结构，**专有名词仍要回机构官网核对**（自动字幕把品牌名、药名、技术名写错是常态）。

## 6. 作者履历要落到机构官方页

顺序：频道 about 页 → 所属机构团队页（大学住院医项目 / 医院医生目录）→ 论文 / 会议演讲页 → 个人 LinkedIn（常撞登录墙，拿不到就写「未取到」，不要用二手简介顶上）。机构页能同时给出职称、认证、出版物列表与会议演讲，是最硬的一层；用它的时间线去校准视频里「我最近在做 X」这类自述。

## 7. 交付形状

深层结构（人 → 频道/课程 → 工作流本身 → 生态背景）写成一章一节，不做工具流水账；所有数字与引语进 `sources.py` 台账，HTML 从台账机械装配（流程见 `market-intelligence` Step 6 与 `grounded-citations`）。数据包（channel_all.tsv、各 summary、字幕、评论）留同一 scratch 目录，报告里写明路径。

## 常见坑

- **把目标视频当项目本身**：没读播放列表就写「这是一个教学视频」，漏掉它其实是一整套住院医课程的入职模块。先跑第 3 步。
- **拿 flat-playlist 的播放量写报告**：该字段在 flat 模式下缺失或陈旧，且所有播放量都是快照；报告须写「快照日期」。
- **播放量对比不标注同批上传**：同一天批量上传的一组视频，播放量差距主要反映搜索命中率，不反映质量差异，写「第二名只有它的 1/16」时必须补一句「同批同日上传」，否则读者会误读为质量判据。
- **评论区样本少就当没数据**：教程类视频评论常个位数（观众是搜到即用的从业者），这不是抓取失败，如实写条数与内容即可。
- **自动字幕直接进台账**：不洗时间标签与重复词，`quote` 全部报 `not found verbatim`。
