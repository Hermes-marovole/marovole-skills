# Chinese Social-Platform Content Lookup

## When to use

A request to review a 视频号 / 抖音 / 小红书 / 快手 account or its author
("看一下这个号都讲什么", "查一下这个医生"), to enumerate a creator's posts, or to
gather what users say on these platforms for a research deliverable.

Two routes in fixed order: the **user's logged-in browser first** (next section),
the no-account routes below only as fallback. Scope: what a Chinese creator —
doctor, expert, 博主 — actually publishes, what users say underneath it, and where
a credible profile of them lives, when the platform itself is login-walled.

## What is readable without an account

| Target | Public read? | What you actually get |
|---|---|---|
| 微信视频号 | no public path | `channels.weixin.qq.com` lands on `/login.html`; content is not indexed by 百度/必应/搜狗/腾讯视频. Confirm with one navigation, then stop and ask the user for screenshots or share links instead of hunting. |
| 抖音 desktop | partial | `douyin.com/user/<sec_uid>` renders 昵称/认证/粉丝/获赞/作品数, but the work grid throws `服务异常，重新刷新拉取数据` |
| 抖音 mobile share | partial | with an iPhone UA, `m.douyin.com/share/user/<sec_uid>` renders the profile card (bio incl. 微信号/电话, 抖音号, 粉丝指数); the `_ROUTER_DATA` JSON in that page carries `userInfoRes.user_info` — user only, its SSR `renderInSSR` flag never includes the post list |
| 抖音 post API | no | `aweme/v1/web/aweme/post/` needs an `a_bogus` signature; the legacy `iesdouyin.com/web/api/v2/aweme/post/` answers with an empty body |
| 头条搜索 | yes | indexes individual 抖音 videos as discrete cards: title + uploader + date + play count |
| 西瓜 / 快手 / 小红书 search | no | search views are login-gated or error out (`服务器出错`) |
| 百度 / 搜狗 | captcha | 百度 serves a 安全验证 slider, 搜狗 a 点选验证码, under automated traffic |

## Logged in: reading the feed properly

### Adapter login is not the page gate

`opencli <site> login` returning `already_logged_in` plus a username proves the
adapter's cookie jar only. Search and feed routes still render their own gate
("登录后查看搜索结果", "电脑设备登录超限") because the page gate is per-route risk
control, independent of the adapter session. Never conclude a platform is closed
on the adapter's word, and never write "blocked" in a deliverable before
navigating to the exact URL you need and reading its rendered text.

### Passing the gate needs the user, and the code expires

Open the gated URL with `--window foreground`, screenshot it, crop the QR into a
small png, send that path, and wait for confirmation. Re-navigate after they
confirm. If it still shows the gate, capture a fresh QR — a crop from an earlier
failed attempt is already expired, and sending it again wastes the user's scan.

`opencli zhihu login --window foreground --timeout 600` returns `login_complete`
with name/uid, after which adapter search works. 小红书 search stays gated even
when `whoami` reports a logged-in account; treat the QR at the search page as the
real gate.

### Token-bound detail links

Search-card `href` values are bare `/explore/<id>`. Opening one directly lands on
the site's error page ("页面不见了") — the working URL carries an `xsec_token`
query param that only exists inside the live search page. Do not rebuild detail
URLs from card hrefs; click the card.

### Read flow that works (小红书)

Packaged as `scripts/xhs_read_notes.py --keyword "<词>" --out <dir>`, or by hand:

```sh
opencli browser open "https://www.xiaohongshu.com/search_result?keyword=<urlencoded>" \
  --session <s> --window background
opencli browser wait time 2.2 --session <s>
# card list: titles + metrics
opencli browser eval --session <s> '...'   # see extraction below
# body: exact text match on a 4-8 char title fragment
opencli browser click --session <s> --text "<title fragment>"
opencli browser eval --session <s> '...'   # note container innerText
opencli browser keys Escape --session <s>  # back to results
```

- Card list: iterate `document.querySelectorAll('section')`, keep sections that
  contain `a[href*="/explore/"]`; the first line of `innerText` is the title, the
  tail is author / date / like count.
- Body: read `#noteContainer, .note-container, .note-content` innerText. It carries
  author, full body, hashtags and the top comments in one string.
- Write each body to its own JSON file as you go — a long scrape otherwise dies
  with the whole batch in memory.
- One `ask`/AI-answer attempt per site is the ceiling. A `cdp_timeout` means no
  answer came back; go to card clicks immediately instead of raising the timeout.

### Comments outrank the body

For any question about what users think or buy, the comments carry the strongest
signal: they contradict the post with self-reported numbers (dose, months, kilos,
which supplements, side effects that did or did not happen). Quote them as user
self-reports, never as measurement. A post with a handful of likes and a comment
section harvesting "which stage are you at" is a lead-generation post, not a
consensus — say which it is.

## Getting an actual video list

`so.toutiao.com/search?keyword=<name+topic>&pd=video` — run one query per topic
slice (`<name> 营养`, `<name> 减脂 饮食`, `<name> 早餐`), because each query
surfaces a different handful of that creator's videos. The index is thin (roughly
ten per query) and skews old: expect the account's earliest batch plus scattered
recent uploads, not the current feed. Dedupe by title + date.

- `pd=user` looks for a 头条号 for the creator; if one exists its profile page
  lists the whole catalogue, since 头条号 mirrors 抖音 posts. Check this before
  grinding keyword slices.
- Snippets keep `#话题` tags intact — the cheapest read on their 选题 and 标签
  strategy.
- The same query shape works for 视频号 cross-posters who also run a 抖音 account,
  but the result is the 抖音 copy: label it as such.

## Credible Chinese doctor / expert profiles

Source order: 医院官网 → 百度健康 → 平台认证 → 新闻报道.

- 医院官网 科室导航 `…/Department_details/<id>.html` — 职务/职称/业务专长, most
  authoritative.
- 百度健康 `health.baidu.com/doctordec/jianjie/<id>` — fullest 学会兼职 list
  (专委会委员、期刊编委/审稿人、省级学会青委). Its 职称 field goes stale: it can
  say 主治医师 for someone the hospital lists as 副主任医师. Report the hospital's
  and note the discrepancy rather than silently picking one.
- 平台认证 line ("X医院Y科副主任医师 姓名") is what ties the account to the person.
- 事迹: `web_search` 姓名 + 医院 + 主题, then open 新华网 / 人民网科普中国 /
  科技日报 / 健康报 / 光明网 / 省卫健委 and hospital 新闻中心 pages, and quote only
  from the text actually opened.

## 微信公众号 articles

A 公众号 article is the hardest of the lot: not web-indexed, `weixin.sogou.com`
answers with a 点选验证码, and there is no public article list.

1. Search the **exact headline**. Same-topic coverage frequently carries the
doctor's full quotes verbatim — 人民网科普中国 / 科技日报 / 光明网 / 健康报 often
publish the same interview days apart. Cite the outlet you actually opened and
say it is a same-topic report, not the 公众号 post.
2. If nothing turns up, ask for the `mp.weixin.qq.com/...` link (复制链接) or
screenshots. That takes one message and beats any amount of searching.
3. A profile screenshot alone is often enough to answer the real question: a
科室名 as the account name proves it is an institutional account, not the
doctor's personal one — a distinction that changes the whole read.

## Reading a screenshot when the vision tool is unavailable

Screenshots of these apps are the usual fallback, so make them legible locally:

```bash
# install once: brew install tesseract tesseract-lang
tesseract shot.png - -l chi_sim+eng --psm 6
```

Phone screenshots are small and low-contrast; raw OCR returns garbled latin.
Crop into horizontal thirds, upscale 3–4×, boost contrast/sharpen, then OCR each
slice with `--psm 6` and again with `--psm 11` — the two modes disagree in useful
ways (the account name and metrics usually appear in one, the body text in the
other). Numbers (阅读 110 / 赞 1) and account names survive this; image-embedded
title text inside thumbnails usually does not — say so instead of guessing.

## Chinese e-commerce keyword search

- 京东 search redirects to a login page for automated traffic; don't treat it as
  an empty result set.
- 当当 accepts raw Chinese in `?key=`, but a mis-encoded keyword returns
  "抱歉，没有找到与…相关的商品" — a false negative, not an empty catalogue. Append
  `&act=input`, or land on the homepage first and search from the box.
- For a market scan, the 分类/作者 facets on a single broad query (`控糖`, ~9.8k
  items) are more informative than many narrow queries: the author list alone
  reveals which publishers and which 三甲医生 dominate the category.

## Delivering this honestly

Fill each platform's "what I could not get" cell from a live logged-in attempt,
not from an adapter error: distinguish adapter auth failure, page gate, and
content that genuinely is not there. A logged-in run usually closes the gap, so
checking it first is what keeps the report from declaring a platform closed.

Never present another platform's content as "this 视频号's videos". Split the
report into: (a) the specific account that could not be read and why, (b) the
verified identity, (c) titles actually captured, each with platform + date,
(d) topics drawn from opened media articles, (e) an explicit ask for screenshots
or share links to close the gap. Also worth stating: platform-side metrics
observed during the check (作品数/粉丝/获赞) so the user can judge whether the
account is worth benchmarking at all.
