# TikTok / 海外账号级拆解（@handle → 后台字段 → 全量作品 → 流量断崖归因）

抖音拆解走 `douyin-account-teardown.md`；TikTok 的接口与字段完全不同，且不登录也能拿到大量「后台才会显示」的元数据。用户贴 X 帖/截图问「这个号是怎么做的、为什么火」时用本文。

## 1. 定位账号：不靠搜索页，先批量试 handle
TikTok 搜索页对未登录会话经常直接给验证码。已知昵称/画面文字时，先拼候选 handle 批量探活——一次 terminal 跑几十个，比开浏览器快一个量级：

```python
# 每个候选：GET https://www.tiktok.com/@<handle>，UA 用桌面 Chrome
# 解析 <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"> 里的 JSON
scope = d["__DEFAULT_SCOPE__"]["webapp.user-detail"]
u, s = scope["userInfo"]["user"], scope["userInfo"]["stats"]
# 命中判据：uniqueId 存在且 followerCount > 100 或 bioLink 非空
```

命中的 handle 会直接带出 `signature`、`bioLink.link`、`language`、`followerCount`——比截图信息多得多。别猜「看起来像官方号」的名字就停，先用 bioLink 里出现的域名/ASIN 反查一次确认是同一个主体。

## 2. 账号后台字段（页面源码里全都有）
`webapp.user-detail.userInfo.user`：

| 字段 | 用途 |
|---|---|
| `createTime` / `nickNameModifyTime` | 注册日 vs 改名日。差几个月 = 洗号/买号重定位，不是「新起号」 |
| `language` | 操盘团队的语言（`ru`/`pt` 等）。英文内容 + 俄语后台 = 跨境矩阵号 |
| `commerceUser` | 是否商业号 |
| `bioLink.link` | 完整外链，**含全部归因参数**，不要只记域名 |
| `signature` | 原始换行，比页面上看到的完整 |
| `stats.followerCount / heartCount / videoCount` | 实时快照，用来纠正转发者截图里的旧数 |

拿到数字后一定和推文/截图里的数字对一遍：涨粉类帖子的截图常滞后一两个月，报告里要写「截图 N 万粉为旧数，现为 M 万」。

## 3. 拿 userId（要给 API 传 targetUserId 时）
未登录页面上点粉丝/关注数会发出 `https://www.tiktok.com/api/user/list/?...&targetUserId=<id>&scene=151&count=30`。做法：`Network.enable` → `goto(/@handle)` → 点 `[data-e2e="following-count"]`（`following-count` 比 follower 弹窗更少隐私拦截）→ 遍历 `page.events()` 找 URL 含 `user/list` 的响应，`Network.getResponseBody` 一次拿到 `userList`（含每人 `stats` 完整数）。URL 里自带 `targetUserId`，就是你要的 id。

这个接口的 `userList[].stats` 是**全精度**数字（`followerCount` 26400000 vs `statsV2.followerCount` 26448998），报告用高精度那个。

## 4. 全量作品与逐条数据
- 主页首屏 JSON 里已有作品列表；不足时 `page.evaluate` 滚 2-3 屏再 drain 一次。
- 视频页 `webapp.video-detail.itemInfo.itemStruct` 给 `stats.playCount`、`music.title`、`createTime`；页面 `innerText` 只按序给点赞/评论/收藏/分享四个数，**不含播放量**，播放量必须从 JSON 取。
- 汇总一律用 Python 写表，不要心算：总播放、总赞、粉丝、逐条播放、逐条收藏率。

## 5. AI 标签：查整数，不要只查对象
```python
it.get("aigcLabelType")   # 1 = 已标 "Creator labeled as AI-generated"
it.get("aigcInfo")       # 可能整段为 None，同时 aigcLabelType 已为 1
```
只判断 `aigcInfo` 会漏判。页面 `innerText` 里出现 `Creator labeled as AI-generated` 是同一事实的可视证据，两者对得上再下结论。

**为什么必须查**：AI 标签是这类账号流量曲线的断点。把 14 条按时间排开、标出「无标签 / 有标签」两段，再算两段的播放中位数——「打标后跌 95%+ 并停更」这类结论只有这张表能支撑，也直接决定「这套打法能不能抄」的答案。

## 6. 归因框架：播放量不是可转化流量
把全量作品按「内容阶段」切段（试水 / 情绪起号 / 软植入 / 硬导流），逐段算：条数、总播放、播放占比、评论率、是否带 CTA。

典型形状：两三条「求鼓励」的同情心起号帖吃掉全号 80%+ 播放，且**完全没有带货内容**；真正挂 CTA 的那几条播放只有中位数级别。报告必须写成「单点爆款 + 泛流量，不是带货能力」，并明确：给「励志老人」点赞的路人和愿意付 $50+ 买补剂的人不是同一批。

## 7. 形式与穿帮点（用于判断生产方式，不用于复刻）
- 时长集中在 6-12 秒、**全片零口播**（配乐 + 画面白字 + 长文案）是这类 AI 号的通用配比：用户读文案时视频已自动循环 2-3 次，完播率白送。判断有没有人声按 SKILL.md 第 2 步短片段探测。
- 早期几条常在角落留着原片的分屏动作参考小窗——AI 重绘真人底片没裁边，是「不是原创拍摄」的直接证据，写进报告。
- 批量套模板会出现**人设自相矛盾**（同一号依次自称 60/70/75/77 岁）。这种不一致是最硬的「非真人」证据，比画面质感判断可靠，务必逐条抄下原文。

## 8. 报告结构（沿用账号级拆解的骨架）
结论先行（这个号到底是谁在运营、赚不赚钱）→ 原帖宣称 vs 后台事实对照表 → 账号后台画像（注册/改名/语言/外链）→ 全量作品表（按时间正序，标 AI 标签与 CTA）→ 漏斗还原 → 变现审计（转 `monetization-claim-audit.md`）→ 我们能学 / 不能学。

宣称 vs 事实一定做成**两列表**，逐条给「属实 / 定性错误 / 严重失实」判定——这是用户要的核心产出，不要写成散文。
