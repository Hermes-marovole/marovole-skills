# 识别演示视频里的产品（「这个视频里是什么产品 / 什么网站」）

用户贴来一条炫技视频帖（多是 X，也见于抖音/小红书），问的是**本体是谁**，不是要复刻、不是要写稿。目标：给出可核实的结论 + 可直接打开的一手链接，并把「已确认」和「未核实」分开。

## 判读顺序（从省到贵，命中即停）

1. **帖子正文与 link card**：很多只是标题党，产品名藏在正文的 `t.co` 里（`curl -sIL <t.co>` 解短链）。
2. **抽帧读画面上的字**——最硬的证据。UI 演示片里品牌名、域名、地址栏、侧栏导航、按钮文案、代码编辑器文件名、终端里的 `git remote` 全在画面上。
   ```bash
   ffmpeg -y -i src.mp4 -vf "fps=1/2,scale=1280:-1" frames/f_%03d.jpg   # 1 帧/0.5s 起步
   ffmpeg -y -ss <t> -i src.mp4 -frames:v 1 -vf "crop=W:H:X:Y,scale=2400:-1" zoom.jpg  # 小字读不清就裁局部放大
   ```
   逐张 `vision_analyze`，按「这一帧能证明什么」记录，不要凭感觉类比成某知名产品。
3. **读作者自己的回复**——决定性的那一步。作者几乎总在评论区自答本体与去向：这是什么（"这只是一群 agent 在把网站搭出来"）、是否有链接（"soon on this page"）、是否开源（"Yes"）、以及一句"只是好玩"的定性。第三方猜测、媒体转述都只是线索，作者的回复才是口径来源。
4. **看作者主页时间线**：同一个人常在另一条帖里直接贴域名（正文里常是裸域名，不带 https://）。
5. **仓库 / 站点实测**：
   ```bash
   curl -s https://api.github.com/repos/<owner>/<repo> | jq '{created_at,size,pushed_at,stargazers_count,description}'
   curl -sIL <domain> | head -20     # 是否 200、跳到哪里
   ```
   `size: 0` + `pushed_at` 等于 `created_at` = 刚建的空仓库，**不要说成「已开源」**。站点能开还要看线上版是否真包含视频里那条效果（多数情况是：视频炫的是未合并的实验分支）。

## 报告口径（用户的红线）

- 把四层分开写，它们经常不一致：**演示的概念** / **作者自己的站点或仓库** / **是否已上线** / **是否已开源**。
- 每条结论后面挂依据（第几秒哪一帧、哪条回复原文、哪个 API 字段），不写「看起来像 XX 产品」。
- 查不到的一律标「未核实」；宁可少写一层，不要用推断填空。
- 结尾给可直接访问的链接（站点 / 仓库 / 作者主页）——用户下一个动作通常是打开它。

## X 页面抓取（ego-browser，省上下文的写法）

- 会话页、回复页**不要** `snapshot({scope:'full_page'})`：X 的 Conversation DOM 极大，一次输出几十 KB，绝大部分是 nav / footer / 推荐位噪音。只取正文：
  ```js
  Array.from(document.querySelectorAll('article'))
    .map(a => a.innerText.replace(/\n+/g, ' | '))
  ```
  一次拿到原帖 + 全部回复的作者、时间、正文、计数，够做判断。
- 取作者自答：`goto('https://x.com/<handle>/with_replies')`，同样用上面的一行 evaluate。作者的回复与被回复者成对相邻，扫一遍就能看出他确认了什么。
- 找作者另发的带链接帖：`goto('https://x.com/<handle>')` 再取 `article` 文本，正文里的裸域名直接可读。
- 视频本身用 fxtwitter 拿直链最省：`curl -s https://api.fxtwitter.com/<handle>/status/<id>` 取 `media.videos[]` 的 mp4 各码率；高码率那档偶发截断，抽帧报 `Invalid NAL unit size` 就换 720p 变体重下。
- 帖子的互动数据用 fxtwitter 或页面文本核一遍再引用，别凭截图印象写。

## 小红书（xhslink 口令链 + PC 网页取数）

小红书的信息分布和抖音不同：**正文常只有一句标题 + 话题标签，全部内容在画面 UI 和口播里**，也没有抖音那种「章节要点」AI 大纲可抄，所以这个平台基本一定要跑逐字稿 + 逐帧读界面。

1. **落地**：`xhslink.cn/o/<id>` 是分享口令短链，在 ego-browser 里直接 `goto` 让它自己跳（落到 `xiaohongshu.com/explore/<note_id>`）；要判重定向再用 `curl -Ls -o /dev/null -w '%{url_effective}'`。
2. **取原片**：`<video>` 的 src 在 PC 端多数拿不到可直连的地址，直链从 `Network.enable` 后 `page.events()` 里筛 `sns-video` 类 CDN 请求、或从 `__INITIAL_STATE__` 的 note 数据里取。拿到后 `curl -sL -A '<UA>' -e 'https://www.xiaohongshu.com/' -o src.mp4 <url>`。原片实在拿不到时退化为「关键帧截图 + 评论区口径」，仍足以答「这是什么产品」。
3. **抽帧与逐字稿**
   ```bash
   ffmpeg -y -i src.mp4 -vf "fps=1/2" frames/f_%03d.jpg                  # 原始帧，留全分辨率
   ffmpeg -framerate 1 -i frames/f_%03d.jpg -vf tile=6x3 -frames:v 1 sheet1.jpg  # 联系表定结构
   ffmpeg -y -i src.mp4 -ar 16000 -ac 1 src.wav
   whisper src.wav --model small --language zh --output_format txt \
     --initial_prompt "以下是普通话简体中文。<产品名/专有名词>"
   ```
   **拼图只能看结构，读字必须回单帧**：vision 会把 1080×1920 降到 540×960，导航项、卡片标题、表单项、说明弹窗全糊成一片；凡是要抄进报告的文案（模块名、导航 Tab、指标名）一律对 `frames/f_00N.jpg` 单帧读，小字再 `crop` 放大。
   60–90s 口播用 `--model small` 足够且几十秒出稿，不必上 large-v3-turbo。`whisper` 不在 PATH 时用用户级安装的绝对路径 `~/Library/Python/3.9/bin/whisper`（CPU 上打 FP16 警告可忽略）。
4. **作者主页 / 置顶 / 相邻作品**：`goto('https://www.xiaohongshu.com/user/profile/<user_id>')`，从 `window.__INITIAL_STATE__` 只挑叶子字段：
   ```js
   const u = window.__INITIAL_STATE__?.user;
   return {
     basicInfo: u?.userPageData?.basicInfo,      // nickname / desc / redId / ipLocation
     notes: (u?.notes?.[0] || []).map(n => ({    // 笔记列表：标题 / 类型 / 赞数 / xsecToken
       id: n.id, title: n.noteCard?.displayTitle,
       type: n.noteCard?.type, likes: n.noteCard?.interactInfo?.likedCount })),
     text: document.body?.innerText?.slice(0, 3500)
   };
   ```
   **不要 `JSON.parse(JSON.stringify(window.__INITIAL_STATE__))`**：store 里挂着框架响应式对象（`deps`/`sub` 互相引用），序列化直接抛 `TypeError: Converting circular structure to JSON`，整次 evaluate 白跑。只挑叶子路径、在 evaluate 内新建对象返回。
   置顶帖与相邻作品标题本身就是口径（如「给 XX 私人医生设计 IP」「某工具小捷径更新预告」），能一眼看出作者是在做课程/卖货还是真做产品，比正文可靠。
5. **评论区是第二证据层，必须抓**
   - 作者的实质回答几乎只在评论区，而且常分几条给完：成品状态、什么时候放出来、收不收费、数据从哪来。
   - 高赞质疑往往直接点破产品硬伤（合规、专业性、数据可采性），是报告「风险」段的现成材料。
   - 抓取：`Network.enable` → goto 笔记页 → `page.events()` 里找 URL 含 `/comment/page` 的响应体落 `comments.json` → 脚本扁平化打印父评 `content`/`likeCount` 与 `subComments[].content`（作者回复多在子评里，只读父评会漏掉最关键的定性）。
   - 解析脚本写成临时 `.py` 文件，别用 `python3 -c '...'`：f-string 里嵌 `"` 转义在单引号外壳下直接 `SyntaxError`；先赋 `nick = c.get(...)` 也照样被引号绊住。
6. **未登录也能判本体，扫码是最后手段**：PC 端即使弹「电脑设备登录超限，请重新登录」并出现扫码框，`document.body.innerText` 与 `__INITIAL_STATE__` 里的公开主页/笔记数据通常仍读得到，够答「这是什么、做没做出来、开没开源」。先把能读的读完，再决定要不要 `task.handOff()`。

## 常见误判

| 误判 | 纠正 |
|---|---|
| 把作者的个人作品集演示当成某个 SaaS 产品 | 先看域名归属：作者自己的 `xxx.me` 作品集 ≠ 商业产品。作者回复里说「just for fun」基本可以定性为炫技 demo。 |
| 只建了仓库就报「开源」 | 查 `size`/`pushed_at`；空仓库要写「仓库已建、代码未推」。 |
| 视频里的效果 = 线上站点的效果 | 单独打开站点确认；未合并的实验动效很常见。 |
| 用第三方转述（其他账号的 quote、媒体报道）当结论 | 只当线索，结论必须落在帧/回复/API 三个一手来源上。 |
| 小红书 UI 精致就当成成熟产品 | UI 精致可能只来自作者的设计能力；功能与数据管线常是手工喂的，先看评论区里作者说的成品状态与数据来源。 |
| 只读小红书正文和作者主帖回复 | 小红书作者的自答、上线/开源口径几乎全在评论区子评里，正文往往只有标题 + 标签，不抓评论必然误判进度。 |
