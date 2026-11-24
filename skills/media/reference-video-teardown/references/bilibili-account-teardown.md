# B站账号级拆解（UP 主名 → 全作品数据 → 起号打法）

用户贴 B站 UP 主/说「调研 B站怎么起号」时用。B站公开接口不用登录，curl 就够，不必开浏览器。产出放 `~/HermesWork/抖音科普视频/_research/<slug>/`：`<up>_videos.json` + `调研.md`。

## 1. 取数（curl，带 UA + Referer + 任意 buvid3 cookie，否则搜索接口返回空）
```
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130 Safari/537.36"
curl -s -A "$UA" -e https://search.bilibili.com -b "buvid3=abc123def" <url>
```
- 找 UP：`/x/web-interface/search/type?search_type=bili_user&keyword=<名>` → `mid / fans / videos / usign`。
- 作品列表：`/x/web-interface/search/type?search_type=video&keyword=<名>&page=N`，按 `mid` 过滤，多换 2-3 个关键词补全；`space/arc/search` 需要 wbi 签名，别硬拼。
- 单条详情：`/x/web-interface/view?bvid=` → `title, desc, pubdate, duration, dimension{width,height}, stat{view,like,coin,favorite,share,reply,danmaku}, mission_id, honor_reply`（每周必看/全站排行/热门收录）。
- 标签：`/x/tag/archive/tags?bvid=`。
- 参加的活动：`/x/activity/subject/info?sid=<mission_id>` → 活动名 + `etime`（截止时间戳），起号时可直接跟投仍在进行的活动。
- 每次请求间 sleep 0.4–0.6s。

## 2. 用 Python 汇总
每条算 赞/币/藏/转 ÷ 播放；看画幅（横竖、1080p/4K）、时长分布、发布时间、标题句式、简介长度、标签组合、活动和荣誉。对比自家 B站后台（`member.bilibili.com/platform/home` 和 `upload-manager/article`，ego Profile 6）同期数据。

## 3. 报告
只写能从数据看出的共性（画幅/时长/标题格式/标签/活动），涨粉原因标「推断」；帖子或媒体里的粉丝/播放数字注明来源和抓取时间。末尾给「我们 B站要改的 N 件事」+ 一个待拍板项。
