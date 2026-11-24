---
name: x2doc
description: Use when turning X posts/videos into grounded docs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [x, twitter, documentation, curation, markdown, superpowers]
    related_skills: [link2doc, url-to-markdown, dokobot, xurl]
---

# X2Doc

## When to Use

- 用户发来 X 帖 / 长文 / 视频，要"学一下 / 整理成文档"。
- 用户说「调研一下这个博主说的是什么」「他这套是不是真的」——走下面的**轻量调研模式**：在聊天里交付拆解，不写 doc、不推仓、不发邮件。
- 帖子里转述的是一项**研究**（论文 / 预印本 / 「某公司最新研究证明…」）→ 轻量调研模式 + `references/paper-claim-teardown.md`：一手源是论文，逐条对账推文结论与论文 Limitations。
- 用户把链接和「学习 / 研究 / 了解一下这个」写在同一句里（没有「存：」「做：」前缀）→ 交付**超集**：完整文档 + 推仓 + `raw-sparks.md` 归档 + 30 秒编导判断单 + 邮件通知，一次给全。不要退化成只回聊天摘要，也不要直接开到「做：」管线的成品草稿。
- ⚠️ **与自媒体「存 / 做」全局暗号的分界（最高优先级）**：
  - 若用户输入以 **「存：…」** 开头（或只丢链接不说话）：必须同时加载 `content-creator-pipeline`，除抓取原文外，必须写入 `raw-sparks.md` 并输出 **【30秒编导判断单（含 A/B/C/D 排产勾选单）】**。
  - 若用户输入以 **「做：…」** 开头（如 `做 @url:https://x.com/...`，且未要求“先给方向”）：代表用户已拍板进入**自媒体生稿管线**！**严禁只写一篇 X2Doc 文档或只回一张判断单就停下**——必须加载 `content-creator-pipeline`，走完 Grounding + 独立 Subagent 逐句事实核查，直接把成品（公众号深度长文 + 微信贴图 3 卡入草稿箱 + X/小红书稿）端到草稿箱/预览界面等用户点头。
- 帖子里推荐的是一个**开源仓库、Agent Skill 或工具**而不是一套方法，用户想知道"能不能用在我们这儿" → 读 `references/external-engine-fit.md`，产出的必须是取舍报告不是功能复述。
- 帖子教的是**海外 AI 账号的注册 / 过 KYC / 防封 / 代理与设备指纹加固** → 文档照常整理，同时加载 `overseas-ai-account-hardening` 出"对我们这台机器做/不做"的落地方案，尤其是**绝不给正在正常使用的账号洗设备指纹**这条（Mode A/B 分流）。
- 帖子在吹一个软件/仓库的**能力数字**（"内置 320+ 工具""什么都能干""一键 XX"）→ 读 `references/tool-claim-audit.md`：官方审计表 + 数量三处对账 + 本机集成取舍。
- 帖子吹的是**「开源免费 / 一句话全自动 / 人工成本归零」**这类说法（尤其是 Agent Skill 仓）→ 同一文件 §6「薄壳判定」：先分清营销仓与执行仓，再去执行仓的 `docs/` 翻被 CI 同步进来的内部运营 / 销售 / FinOps 手册——那里写着真实的服务上限和对外话术落差，是全篇最硬的证据。
- 需要把 X 内容落成 Obsidian 方向指导、Superpowers 公共文档或邮件通知。
- 用户说「学这个博主」「同样方法再拆一篇」——要的是可复用的方法论归档：走 `references/cn-creator-method-sourcing.md`（中文博主取材路径 + Space 逐字稿站 + 双笔记交付结构）。

## Goal

Convert high-signal X/Twitter content into a durable, useful Markdown document instead of a shallow summary.

Default destination for personal knowledge/public curation is:
`/Users/marovole/Workspace/playground/HermesWork/marovole-Superpowers/docs/`

## Success Criteria

- Captures the original X URL, author/handle, date when available, and extraction date.
- Preserves the core argument, links, quoted posts, tools, repositories, and claims.
- Adds enough context for future reuse: why it matters, applicable scenarios, limitations, and next actions.
- Uses personal attribution: `来自翡冷翠`; never signs as Neuma, Neumina, 智子, or AI Agent.
- If committed to Superpowers, returns both local path and GitHub blob URL.
- Stops when the document is useful and source-grounded; does not over-crawl unrelated replies.

## Constraints

- Do not read or print X API credential files such as `~/.xurl`.
- Do not mutate X state unless explicitly asked: no likes, replies, reposts, follows, unfollows, or DMs.
- Linear is only for company projects. Personal Superpowers docs are not synced to Linear.
- Prefer low-risk incremental writes. Do not overwrite existing docs unless the user asked for an update.
- For X content behind login walls, use available extraction routes and clearly mark unavailable parts instead of hallucinating.

## Source Extraction Strategy

Use the cheapest reliable route that can capture the content:

| Source type | Preferred route | Fallback |
|---|---|---|
| Single public tweet (incl. its quoted post, stats, video URLs) | `web_extract` / curl `https://api.fxtwitter.com/<handle>/status/<id>` — one call returns full text of the post AND the quoted post, author, timestamps, and mp4 variants | Jina Reader, then browser |
| Public thread | `https://r.jina.ai/http://x.com/...` via curl | If this returns 403, retry Jina with the `http://https://x.com/...` form; then browser snapshot, then Dokobot |
| X Article / long-form post | fxtwitter JSON `tweet.article.content` (Draft.js `blocks` + `entityMap`) — see the Article rendering pitfall below; Jina Reader on original status URL as fallback | If standard Jina form is blocked, retry `https://r.jina.ai/http://https://x.com/...`; browser full snapshot + scroll |
| JS/login-walled or Chinese/complex pages | Dokobot local Chrome | browser snapshot |
| Need official API data and xurl is configured | `xurl read`, `xurl user`, `xurl search` | Jina/browser |
| X Article names projects but Jina strips link text or leaves blank references | Supplement with targeted GitHub/web searches for named projects before writing the resource table | Mark unresolved links as unavailable instead of inventing |
| 中文博主的方法论（长文 / Space / 直播） | 先找"文章归档站"和 Space 逐字稿站，别翻时间线：`web_search "<handle> <主题> 逐字稿"` 常直接命中 `jxxy.net/ai/articles/`、`zhongwenx.com/creators/`、`xbangdan.com/account/` 等镜像，以及 `audio.eatmoreduck.com/space/<id>/` 这类带说话人和时间戳的转写页 | 镜像站（teapawt 等）可按 cursor 逐页 curl，不烧 Firecrawl 额度，但几十页后限流且到不了最早期帖子——翻不动就换搜索/归档 |
| User pasted text/screenshots | Use provided content as primary source | Ask only if essential data is missing |

### Locating a post the user saw but cannot link ("我记得看过一个帖子…")

1. Query local browser history first — it is the only reliable index of what the user actually viewed. web_search on X post content mostly returns spam `x.com/search?q=` pages. Copy each `History` DB before reading (the live file is locked), then filter by URL and title. Chromium-family titles contain the post text, so you can usually spot the match from the list without opening anything:
   ```bash
   for f in ~/Library/Application\ Support/{Arc/User\ Data,Google/Chrome,BraveSoftware/Brave-Browser,Microsoft\ Edge}/*/History; do
     [ -f "$f" ] && cp "$f" h.db && echo "== $f" && sqlite3 h.db "select datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime'),url,title from urls where url like '%x.com/%status%' or url like '%twitter.com/%status%' order by last_visit_time desc limit 80;"
   done
   ```
   Safari keeps history in `~/Library/Safari/History.db` (history_items join history_visits). The user's main X profile is Arc `Default`.
2. The user's paraphrase is often a loose translation of the post's key term (e.g. "野性" for "ambitious"). Match on topic and author, not on literal keywords. Give the best match with its visit time, list near-misses in one line, and point out where the user's memory differs from the original.
3. Confirm the match with fxtwitter (exact text, `created_at`, expanded links), then read the linked article in full before summarizing. If the extract was truncated, read the omitted middle from the saved file before claiming you know what the source says.

Stop searching when:
- the main post/thread/article content is captured, and
- external links or quoted posts needed to understand the claim are captured, and
- images containing data, charts, or rankings are captured and transcribed, and
- further replies are mostly commentary/noise.

Continue searching only if:
- the post explicitly says essential content is in replies/comments,
- a referenced tool/repo/article is needed to make the doc actionable,
- images contain essential data that the text alone does not convey,
- the extracted content is incomplete/truncated.

## 轻量调研模式：博主/推文说法核查（「调研一下这个博主说的是什么」）

交付形态是聊天里的一条结构化答复，不是文档：**他在说什么（一句话）→ 逐环节拆链 → 硬数字 → 水分与边界 → 对我们值不值得抄**。

1. **先分句拆链，再评价**：把文案里的每个名词（模型、第三方产品、自建工具、口号）分别落到「真产品 / 自建开源仓库 / 只是他的语境」，再判断哪一环是新信息。整段转述他的原话等于没调研。
2. **每个工具名都要落地取证**：官网 docs + pricing（能不能装、多少钱、免费额度），GitHub `api.github.com/repos/<owner>/<repo>` 读 `created_at / pushed_at / stargazers_count / license`。**仓库当天才建、0 star 就是「发布帖」，不是「已验证方案」**，必须写进结论。
3. **加总口径自己算一遍**：「全网 6w 粉」这类成果数字按平台逐项相加核对（六平台合计 60,175 才撑得起「6w」），并注明是加总而非单平台；对不上就直接判夸大。
4. **配图里的数字用 OCR 读，不许从文案推**：数据大屏、后台表格截图跑 `scripts/ocr.swift`（本地 Vision，逐字带坐标，再把坐标按版式拼回语义），`vision_analyze` 用来判断「这是什么界面」。
5. **区分「自动」与「自动填表」**：声称自动发布时去 README 找那句限制（国内平台填完停手、要人点发布、平台改版就碎），把残留的人工环节写清楚。
6. **结尾必须给取舍**：借哪个机制（数据结构、复盘口径、转化漏斗）而不是换整套栈；能不能直接装、和他自己现有管线（目录规范、各平台发布规则）冲突在哪。
7. **转述的是一项研究（论文/预印本/「某公司最新研究」）时，一手源是论文不是推文**：数字只从论文表格抄，推文只当索引；逐条标注论文 Section 号，并把 Limitations 段的自认边界引用出来。完整流程：`references/paper-claim-teardown.md`。

## Document Shape

Use this structure for Superpowers docs:

```markdown
# {title} - X2Doc 整理

> 来源：{x_url}
> 作者：@handle
> 整理时间：YYYY-MM-DD
> 来自翡冷翠

---

## TL;DR

3-5 bullets explaining the signal and why it matters.

## 原帖核心内容

Preserve the original argument faithfully. Quote short key phrases when helpful.

## 关键信息与资源

| Type | Name | Link | Why it matters |
|---|---|---|---|

## 我的吸收判断

- 可复用能力：
- 值得沉淀到 skill / workflow 吗：
- 对 AI × Product × Biohacking / Super Individual 的价值：
- 风险或待验证点：

## 可执行下一步

- [ ] ...

---

*来自翡冷翠*
```

## Output Destinations

### Superpowers GitHub doc

Use when the user says “整理成文档”, “提交到 Superpowers”, “放到仓库”, or this is a reusable public knowledge artifact.

- Repo: `/Users/marovole/Workspace/playground/HermesWork/marovole-Superpowers`
- Before writing, `ls docs | grep x2doc` for an earlier doc on the same topic; link or extend it instead of duplicating.
- Default directory: `docs/`
- Filename: lowercase keywords + date, e.g. `x2doc-{topic}-2026-05-10.md`
- Commit message: `docs: add {topic} X2Doc 整理 ({date})`

Before writing:
- `git status --short --branch`
- If there are unrelated uncommitted changes, avoid touching them.

After writing:
- commit only the new/updated doc file unless asked otherwise.
- push to origin main if this is a finished Superpowers doc.
- after push, verify the raw GitHub URL contains the source URL and `来自翡冷翠` before reporting completion.

When writing the doc, include an `我的吸收判断` section for durable takeaways:
- 帖子自带后台 / 监控大屏 / 数据表截图时，必写「正文宣称 vs 配图实测」对账：把截图里的总数、拆解项和「正常 / 成功」数算成通过率（216 项任务里只有 75 项最近正常 = 34.7%）并点明与正文的落差；配图角落的小字（「完成证据见详情；调度与业务分别记录」）逐字引用——它是判断作者真跑过生产还是只搭了 demo 的最硬证据，也常是全文最值得做的那条选题;
- reusable capability;
- whether this should become/patch a skill or cron;
- relevance to AI × Product × Biohacking / Super Individual;
- risks and validation gaps.

### Obsidian note

Use when the user asks to save into second brain / Obsidian.

- Vault: `/Users/marovole/Library/CloudStorage/Dropbox/Obsidian Vault`
- Use controlled tags only: `type/*`, `area/*`, `status/*`.
- Avoid noisy tags from HTML/CSS/design snippets.

### Learning / direction-guide doc ("学一下，写成文档作为后续 X 工作的方向指导")

When the user wants a tutorial/talk absorbed as standing guidance for their own work (not public curation):

- Save to Obsidian `03-Areas/<领域>/` (e.g. `03-Areas/自媒体/`), tags `type/guide`, `area/*`, `status/active`; transcript as a sibling note tagged `type/source`. Not Superpowers, no push, unless asked.
- Two parts, clearly separated: (1) 课程内容 — faithful to the source, chapter-ordered, no added claims; (2) 落到我们的执行准则 — explicitly labelled as my inference, mapped onto the user's current positioning from memory (platforms, monetization path, weekly hours, red lines), with concrete per-item checklists and a first-week action.
- Map each method in the source to skills already installed that implement it (check `skills_list`; e.g. a creator's open-source skill pack may already be installed locally) instead of telling the user to go find tools.
- Point out when the source creator is themselves a direct benchmark for the user's plan.
- Frame a success story as ONE case, not a recipe: put a 定位 caveat at the top (sample size, self-reported numbers, survivorship — failed attempts never get written up; cite the author's own weaker results if given), and title part (2) "如果要试：低成本验证方案" with success criteria like "N tries, how many hit, does each cover its cost" — never "照做就能出单" or the case's headline number. The user rejects guides that read as a guarantee.
- Before writing part (2), check whether the user ALREADY runs this format (grep their skills + project `_research/` data reviews). If so, build a side-by-side metric table (source's numbers vs ours on the same rates) — it often shows which of our earlier conclusions targeted the wrong lever. Frame such findings as hypotheses; never silently override a standing user decision (list it as a test to propose).
- If the source links an open-source repo, shallow-clone it read-only to `~/Workspace/playground/<repo>` (no install) and read its skills/references; cite the commit hash. Borrow workflow, do not switch the user's stack.
- If the method conflicts with the user's existing account/brand positioning (e.g. burner-account or broad-niche tactics vs a personal brand), say so and propose running it on a separate asset. Make it a named section **「冲突点（明确不抄）」**: each tactic plus the user red line it breaks. A guide with no visible exclusions reads as an endorsement of the whole method.
- 源作者本人在卖"教你做这件事"的课/社群/付费观看位时，把这一层写进文件头的**定位警告**：公开的方法就是他的引流款，越关键（导流、投流、起量细节）越会被扣住——把"披露深度有限"写成结论的一部分，而不是当成自己没查全。取材路径与交付配方：`references/cn-creator-method-sourcing.md`。
- End with 待验证/风险: speaker self-claims, transcription caveats, capacity mismatch between speaker and user, copyright/compliance lines the source glosses over.

### Local scratch

Use `~/Workspace/playground/HermesWork/reports/` when the user only wants a temporary report, or to keep a full verbatim copy of a long Article (prompts/code) alongside a condensed Superpowers doc. Never leave the only copy in the scratch dir — it is pruned after 24h.

## Verification

Before final delivery:

- Check the source URL is included and not malformed.
- Check no fabricated claims, metrics, repo names, or dates were added.
- Check the document has `来自翡冷翠` attribution.
- If saved to git, verify `git status`, latest commit, and GitHub URL.
- If extraction was incomplete, state exactly what was unavailable.

## Delivery

After the document is verified and pushed (or saved to local/Obsidian), send an email notification to the user's primary mailbox with the secondary mailbox in CC:

- **To**: `<YOUR_PRIMARY_EMAIL>`
- **CC**: `<YOUR_CC_EMAIL>`
- **From**: `<YOUR_AGENT_EMAIL>` (via ClawEmail / mail-cli)
- **Subject**: `x2doc 整理完成 - {topic}`

Email body should include:
- Document title and one-line summary
- Local file path
- GitHub blob URL (if applicable)
- Key takeaways (TL;DR bullets)
-宝玉风格 Quote 转发文本（如果适用）

Send command:

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
mail-cli compose send \
  --to <YOUR_PRIMARY_EMAIL> \
  --cc <YOUR_CC_EMAIL> \
  --subject "x2doc 整理完成 - {topic}" \
  --body-file /tmp/x2doc-email-body.txt
```

### Email is a notification, not the deliverable

- **Never report "邮件已发送" without proof**: a `mail-cli` success envelope or the message visible in Mail's Sent mailbox. A send call that returns nothing / times out is "unknown", and you say so.
- **Don't block the handoff on email**: if neither channel confirms delivery, finish the task in chat with the local path + GitHub blob URL and state plainly that the email did not go out and why. The doc is already verified and pushed; the mail is optional.
- **Don't retry the same failing channel more than once**: one `mail-cli` attempt, one Apple Mail attempt (`open -a Mail` first, ≥120s timeout), then stop and tell the user — see `references/apple-mail-fallback.md`.
- **One-call Mail helper**: `python3 ~/.hermes/scripts/send-xpulse-daily-email.py <doc.md>` 用 Apple Mail 直接把文件当附件发走，打印 `OK emailed via Apple Mail: … -> to (cc …)`，中文正文无限制、CC 已配好。`mail-cli` 上游报错时先用它；但它的主题固定成日报格式（`📡 AI/科技日报 | <date>`），要 `x2doc 整理完成 - {topic}` 这类主题就得走 `-e` 链。
- **Use a fresh body-file path per send** (`.../x2doc-email-{topic}.txt`): reusing a fixed path like `/tmp/x2doc-email-body.txt` gets refused by write_file's stale-write guard once the file exists from an earlier run.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Treating X replies as mandatory and crawling forever | Stop when the main argument and essential linked resources are captured. |
| 调研类提问（「这个博主说的是什么」）只复述了他用了哪些工具 | 走「轻量调研模式」：工具逐个落到官网 pricing + `api.github.com/repos/...`（created_at / stars / license）、加总口径自己相加、截图 OCR 取数，最后给「值不值得抄」而不是「他在用什么」。 |
| Losing useful context from a link card | Resolve `t.co` redirects with `curl -L -I`, then fetch the target README/API metadata directly when it is central to the post. |
| Resolved `t.co` link lands on a truncated 404 (`github.com/Breakthrough/P`, `github.com/heygen-com/hyp`) and several rows of a "N 个开源仓库" list are dead | 发帖人复制的是带省略号的截断文本，短链本身没坏。按工具真名回推 `<owner>/<repo>`，逐条 `gh api repos/<owner>/<repo> --jq '"\(.full_name) | ★ \(.stargazers_count) | \(.license.spdx_id)"'` 验证存在之后才写表；表里显式标注"已修复原帖截断"。修好链接这件事本身就是最有价值的交付物——转发量高的帖子里死链常无人点开。 |
| Directly visiting `/i/article/...` and getting 404 | Fetch the original status via fxtwitter (`tweet.article`), Jina Reader as fallback. |
| 推文 `text` 只是一个 `x.com/i/article/<id>` 链接，就下结论「长文必须登录才能读」 | **错在只打印了 `text`**：这类帖的 `text` 本来就是那串 URL，正文在同一个 JSON 的 `tweet.article.content` 里。把整个 fxtwitter JSON 落盘后判三个字段：`article` 存在 → 按 entityMap 配方渲染全文；`article` 为 null → 再转登录态（`handOff` 让用户登一次，登录后自跳回文章页）。用户说「研究一下这个 <链接>」时这个判定必须在第一次抓取就做完，不要先跑一轮 nitter/curl/登录试探再回头补。 |
| 帖子只看赞数就判断值不值得拆 | 看**收藏/赞比**：收藏远高于赞（如 300 赞 / 500 收藏）= 「要回看的实操清单」，值得完整渲染正文并给可落地清单；赞高收藏低 = 情绪共鸣，拆完形式就停。 |
| `git push origin main` 被拒（non-fast-forward） | 这台机器不是唯一写入者（另一台机器 / 定时任务会提交 README、backlinks 之类）。先 `git fetch origin main && git log HEAD..origin/main --oneline` 看清对方改了什么，再 `git merge --no-edit origin/main` 重推；**永不 `--force`**，也别为了线性历史 rebase 掉别人的提交。合并后仍要按 Verification 重验远端 raw URL 含源链接与 `来自翡冷翠`。 |
| Losing quoted-post context | Capture quote chain only until the argument is understandable. |
| User's link is a short recommendation/repost ("强烈安利…") and the body has no method | The tutorial is usually the quoted post's X Article: read `tweet.quote.url` from the fxtwitter JSON, re-fetch `api.fxtwitter.com/<quote handle>/status/<quote id>` and render `tweet.article` via the entityMap recipe below. Also resolve the post's `t.co` link (`curl -sIL`) and read that product/install page, and `web_search` the named repo; the recommender's own add-ons (e.g. a packaged agent) are a separate layer from the original author's method — report both. |
| 原帖吹"内置 N 个工具""什么都能干"，评论区却有人说"用过一次就删" | 先读仓库的 `docs/STATUS.md` / `docs/tool-status.md` 审计表：`Unverified` / `simulated in source` / `early alpha` 的行就是评论区的真实来源。工具数按 README 宣称 / 生成清单 / 实跑 `commands` 三处对账，差异并列写出各带出处，不挑一个。取舍先查本机是否已有插件覆盖，别为一个工具把上百个工具挂进全局 MCP。完整流程：`references/tool-claim-audit.md`。 |
| 作者在文末承诺"阅读过十万就更新 XX 教程"，于是花几十次调用翻他全部时间线去找那篇 | 承诺的后续篇常常根本没发。先在作者的文章归档站核对篇目清单再决定要不要找；同一博主更完整、更晚的版本往往在 **Space / 直播 / 播客逐字稿**里（一场 90 分钟分享的机制密度远超一篇长文），搜 `"<handle> <主题> 逐字稿"` 比翻时间线便宜一个数量级。确实没发就直说"他承诺的那篇没发"，并把找到的更优源作为替代交付。 |
| 机器转写的 Space/播客逐字稿里出现"举证""获克""小用书""支付费""嫌疑""网牌""变线" | 同音错字固定映射：举证=矩阵、获克=获客、小用书=小红书、支付费=知识付费、嫌疑=闲鱼、网牌=网盘、变线=变现。按上下文校读后再写，文件头标注"机器转写、未人工校对、同音错字已按上下文校读"；引用数字和原话前先过一遍这张表。 |
| Writing AI/company attribution | Always sign personal docs as `来自翡冷翠`. |
| Syncing personal curation to Linear | Do not use Linear for Superpowers personal docs. |
| Using X write actions during extraction | Read-only unless explicitly instructed. |
| `dokobot read` returning empty on X pages | Dokobot device IDs drift; skip quickly to browser snapshot or Jina Reader. |
| vision_analyze failing with "Invalid image source" on HTTP URLs | Download image locally with `curl -sL <url> -o /tmp/...` first, then pass the local path. |
| Jina returns 403 AbuseAlleviationError for x.com | Use `curl https://api.fxtwitter.com/<handle>/status/<id>` (JSON: text, stats, media URLs, article). |
| Post body is just a caption; content is a long video | Download 480p mp4 → whisper transcript in background → chapter table from tiled top-strip frames → fix whisper loops by re-running a time window. Full recipe: `references/long-video-transcription.md`. |
| X Article text renders but every code block / prompt / table shows as an empty `atomic` block | Article code, prompts and tables live in `entityMap`, not block text. Resolve each atomic block's `entityRanges[].key` against `entityMap` (a LIST of `{key, value}`; index by `str(key)`): `MARKDOWN` → `value.data.markdown` (fenced code/tables, the most valuable part), `TWEET` → `value.data.tweetId` (embedded post), `MEDIA` → `value.data.mediaItems[].mediaId`, resolved via `tweet.article.media_entities` (`media_id` → `media_info.original_img_url`) — curl each to a local dir in order and transcribe data images (charts, tables, backend screenshots) with vision_analyze; they often hold the real numbers, `LINK` → `value.data.url` (the only place the article's cited source tweets, repos and product pages are reliably enumerated — block text sometimes drops or truncates them, so grep the entity dump before building the resource table), `DIVIDER` → `---`. Map block types `header-two`→`##`, `unordered-list-item`→`-`, `ordered-list-item`→`1.`, `blockquote`→`>`. Skipping this loses roughly half of a tutorial-style Article. |
| 原帖推荐的是一个开源仓库 / Agent Skill（"学一下这个项目，我想用它做视频"）而不是一套方法 | 只复述 README 等于没做。浅克隆只读 → 跑它自带的门禁脚本拿真实输出 → **原帖附带的成品视频下载下来用同一套门禁反测**（作者的"全自动出片"必须被数字证实，不能只被引用）→ 写"形态映射 + 对现有栈的取舍表 + 中文落地必改项 + 三栏成本"，默认结论是借 2–3 个机制而不是换栈，且**借形态不借赛道**。完整模板与可借机制清单：`references/external-engine-fit.md`。 |
| `mail-cli` returns `COREMAIL_UPSTREAM_ERROR` (persists on retry) | Fall back to Apple Mail `-e` chain (`references/apple-mail-fallback.md`): ASCII body + doc attached, add `make new cc recipient` for the CC address. Launch Mail first and allow ≥120s — the `send` call blocks while Mail.app starts or an automation-permission dialog waits, so a short timeout tells you nothing. Confirm in Sent before claiming delivery; otherwise hand over the path + GitHub URL in chat. |
| Talk transcript ends with song lyrics / quoted copyrighted text | Replace with a one-line placeholder in the saved transcript; never put full talk transcripts in the public Superpowers repo (Obsidian only). |
| Derived content built FROM a talk (article/doc citing the transcript as evidence) | A chapter excerpt of the transcript may go to `docs/transcripts/` in Superpowers so grounding.py can fetch it as an evidence URL — keep it excerpt-only and lyric-free. Full transcripts stay Obsidian-only. |
| Writing a health/longevity post from a talk's supplement or protocol list | Verify the speaker's recommendations against primary literature before drafting (load content-grounding skill); mark speaker self-claims (body age, records, personal test results) as unverifiable, distinguish 'studies support the general mechanism' from 'studies support this exact usage', and route the piece through the two grounding gates. |
| 推文宣称「某公司/某实验室最新研究证明 AI 能替代 XX」（研究型转述，不是工具推荐） | 先落一手论文再评价：论文标题精确短语 `web_search` → 读 `arxiv.org/html/<id>vN` 全文；核首版/修订日期（「最新发布」常是翻红旧文）、作者里甲方数据方与乙方咨询方混编、Limitations 段原句。推文典型偷换是把「问卷打分意图」说成「真实购买/销量」、把事后挑出的最佳子集说成方法通用、把「相对重测信度上限的比值」说成「准确率」。完整流程：`references/paper-claim-teardown.md`。 |
| 只看主实验最好看的两行就下结论 | 按论文原表全量搬，**消融与基线行不能丢**：常见「去掉某关键约束后分布相似度反而更高、但排序能力崩掉」的假象行，单看那个指标会被骗。 |
| Jina Reader truncating quoted-post content inside a tweet | Fetch the quoted post directly via its own `https://r.jina.ai/http://x.com/<handle>/status/<id>` URL. |

## Relationship to link2doc

Use `x2doc` for X/Twitter-native sources. Use `link2doc` for broader multi-source curation, YouTube, GitHub lists, newsletters, or non-X resource collections. If a task starts from X but expands into a broad resource compilation, load both and use `link2doc` as the broader publishing workflow.
