---
name: content-grounding
description: "Use when writing any factual content. Fetch, cite, gate."
version: 1.0.0
author: 智子
license: MIT
metadata:
  hermes:
    tags: [grounding, fact-check, news, briefing, content, citations, hallucination]
    related_skills: [grounded-citations, content-creator-pipeline]
---

# Content Grounding（内容依据闸门）

## When to Use
新闻、简报、公众号长文、贴图、digest、研究报告，以及对话里任何事实陈述。所有产出内容的 cron 都挂了本技能。
也包括「别人这条帖子/截图说的是真的吗」——推广帖、宣传截图、二手传言的真假鉴定走同一套闸门（见 `references/product-claim-verification.md`、`references/viral-chart-audit.md`）。
用户硬性红线（2026-10-03 定）：智子输出的一切事实都必须有依据，不能胡说、捏造、幻觉，写文章、做新闻尤其如此。

## Goal
成稿里的每个事实（数字、日期、人名、机构、链接、引语）都能追溯到本次实际抓取的原文，并且过两道机器闸门。

## Success
- `grounding.py check` 输出 GROUNDED OK
- `grounding.py review` 输出 REVIEW PASSED（与写稿模型不同的模型核对）
- **写文章必经独立 Subagent 逐句核查（2026-11-07 用户定）**：任何文章（公众号长文、深度稿、评测、专栏）在推草稿或交付前，除过 `grounding.py check/review` 外，**必须派出独立 subagent（`delegate_task`）对照本地已抓取原文（`evidence/<DATE>/*.txt`）做逐句严苛事实核查**，按【完全准确 / 措辞轻微偏差 / 事实错误】输出英文原句对照，修完所有失真与过度引申后再最终交付。
- 最终回复报告两道机器闸门结果 + Subagent 核查修正项 + 被拦下删掉的条目

## Constraints
- 事实只能来自 `grounding.py fetch` 抓到并读过的原文（或上游已核对条目的 evidence 原句）。web_search 摘要、上游 AI 摘要（x-pulse、简报中文摘要、newsletter 总结）只能当选题线索。
- 禁止凭记忆写链接/日期/数字；禁止按标题拼 URL；禁止补充原文没有的背景（头衔、归属公司、融资史）。对比文（A vs B）尤其严：竞品的连接器/集成清单逐项照抄原文列表，竞品用哪家的模型与基础设施只写原文说过的，方向要写准（单向「从 X 导入」不写「互导」）。
- **给同事同步的调研/评估文档，每个案例都要内嵌原始 URL，文末再列全量出处台账**：案例写成「原始来源：标题 — 完整 URL」，第三方工具/模板条目在表格里单列「原始页面」一栏，附录把官方文档、Marketplace 页、社区帖按编号一起列出。只有名字、没有可点链接的案例等于不可复核，用户会当场打回并重做一版。
- 同一选题的多形态产出（长文、贴图、短视频屏幕字、X/小红书稿）共用一份口径表：同一个数字、同一个限定量（「慢 7 倍」「93.5% vs 65.0%」「285:107」）在四处必须逐字一致。改口径要一次改全，别只改被 review 拦下的那一处——贴图和视频不会被长文的 review 覆盖，改漏了就是对外发了两个版本。**口径表里也要收「动作词」**：谁生成的、谁配音的、谁后期的，用同一个动词（模型出的画面写「生成 / 复现」，绝不写「实拍 / 拍摄 / 亲手拍」）。review 只报其中一处（常是标题），同一个错词还躺在 `digest`、`cover_title`、贴图 `title`/`caption`、小红书与 X thread 里，改一处等于没改。
- 拿不准就不写；条数不够就少发，不凑数。
- 不许设置跳过检查的环境变量（BRIEFING_GROUNDING_SKIP / BRIEFING_REVIEW=0 仅限人工应急）。
- 「判断：」可以是观点，但不能夹带原文没有的事实；观察性研究不写成因果。观点句要真的带上那层字面标记（「判断：」「我的判断是：」），因为 review 把成稿每行都当事实句读，不带标记的推测就是无据陈述；也不要把来源的机制换成相邻概念（原文说官网返回 `Blocked request`，稿子写「Issue 死链」——标签听起来更狠，但原文没说过）。
- 中文稿里引用英文原文要译成中文（英文原句放 evidence.quote 里），不要把英文句子直接夹在正文中。计划/将上市的事不要写成「已推出」。
- 对话里同样适用：没核对的说法要明说「这是推断/记忆，未核实」。

## 工具
```
G=~/.hermes/scripts/grounding/grounding.py   # 本仓库副本随附于 scripts/grounding.py
python3 $G fetch  [--date D] URL ...          # 抓原文 → ~/HermesWork/evidence/<D>/；打印发布日/标题/本地正文路径
python3 $G show   [--date D] URL              # 看抓取记录
python3 $G check  [--date D] --kind K FILE..  # K = briefing | tietu | longform
python3 $G review [--date D] --kind K FILE..  # 独立模型核对（只在 config.yaml 里**实际还配着**的源之间降级，不在代码里写死名单）
python3 $G audit  [--date D] [--n 5]          # 抽查某天已产出内容（晨间复盘用）
```
在 Hermes 会话里按这条跑（系统 python + 清掉 venv 的 `PYTHONPATH`，否则导入/连核对源都会失败）：`env -u PYTHONPATH -u PYTHONHOME GROUNDING_PYTHON=/usr/bin/python3 /usr/bin/python3 ~/.hermes/scripts/grounding/grounding.py review --kind longform A.md B.md`。一次可传多个文件，每个文件单独报 OK/ERROR，不必逐篇起进程。
条目字段：`evidence: [{url, quote}]`（quote 从本地正文逐字复制，≥15 字符）；`derived: [{value, from}]`（换算过的数字，from 必须是原文原话）。longform 用同目录 `evidence.json`：`{"a-brief.md": {"evidence": [...], "derived": [...]}}`。
没有专用 --kind 的产出（digest、报告、笔记）：同样先 fetch 原文、只写原文里有的事实、每条附原文链接；可用 grounded-citations 技能的 sources.py 做逐字引语校验。

## Procedure
1. 选题（线索源随便）→ `fetch` 原文 → BAD 的来源换掉（死链、墙、列表页、付费墙只剩标题的不要用）。
2. `read_file` 读本地正文，写稿；每条 2–4 个 evidence 覆盖核心事实和每个数字。
3. `check` → 按报错改：数字对不上就改或加 derived；quote 对不上就重新复制；旧闻/无日期就换来源或删条。
4. `review` → FAIL 的逐条改写成原文能支持的说法，或删掉。分页主线 / 导语也会被核对，只能复述条目里已有的事实。review 对长文常要多轮（见 references/grounding-tool.md 的 review 截断与不可抓取来源两节）：每轮只改 flagged 句子，别重写整篇；作者自己的操作（下载、实测时长）会被当作不可核事实拦下，删掉或降级为括号说明。英文原文译写成中文长文时，提交前先按 references/grounding-tool.md「Translated / paraphrased long-form」清单自查。这一类常见问题包括：标题扩大主语、把相对时间换算成具体年份、加上原文没有的限定词、把建议写成确定动作。
5. **派独立 Subagent 逐句核查（写文章强制步骤，2026-11-07 定）**：单次 LLM `review` 容易漏掉细微的机制脑补、档位名错配或同一文档不同页面的口径冲突（如官网写 Linux 命令行安装被写成桌面端下载、将状态回退 `flashes Added then reverts` 译成「闪退」、将价格变动通知写成「购物比价」）。在文章初稿完成并通过 `check/review` 后，必须调用 `delegate_task` 派出 1–2 个独立 subagent，传入成稿路径与本地 `evidence/<DATE>/*.txt` 路径，要求逐句比对原文并输出【完全准确 / 措辞轻微偏差 / 事实错误】清单，将所有失真和措辞偏差修完、重跑 `check/review` 通过。派单时必须点名三件事：用代码重算所有 N/M 计数、名次与倍率（不许肉眼读表或数图例）；对标题、KPI 与结论里每个定性形容词指出它靠哪一列支撑；输出不是报错清单而是【判定｜依据原句｜可直接替换的改法】四列，让它给能落笔的改法。
6. **没有专用 `--kind` 的产出（视频剧本、纪录片解说词、多章深度稿、书籍章节）改用事实台账闸门**：先建同目录 `facts.json`，每条 `{id, url, local, quote}`（`local` 指 `fetch` 落地的 evidence 正文），跑 `python3 scripts/facts_check.py --facts facts.json --script 成稿.md`，要求输出 `FACTS OK`；正文里的每个 `[Fxx]` 都必须能在台账查到。换算、加权、倍率比较得到的数另立 `[Dx]`，在稿末附「推算数字说明」逐条写出算式与来源 id，正文与台账一起随项目存档。先过台账再写正文后半段，别等全稿写完才回头对账——改一处口径要连累整篇重对。跑闸门时 `--facts` 和 `--script` 两个参数都要给：只传 `--facts` 只做引语逐字比对，正文里的 `[Fxx]` 有没有台账条目、台账里有没有正文没引的孤儿编号都不查，照样打印 `FACTS OK`。
7. 全部通过后再渲染 / 建草稿（或 `draft/update` 原地更新） / 发布。

## Stop
两道闸门通过并完成交付；或者改不过的条目已删、剩余条数不足时如实报告「今天可信内容不足」，不凑数。

## Verify
- [ ] check = GROUNDED OK，review = REVIEW PASSED（「OK?」= 两次核对一次 FAIL，留意但放行）
- [ ] 成稿链接都能在 `show` 里查到
- [ ] 最终回复列出被删条目和原因

## Pitfalls
- **出版商整站 Cloudflare（thelancet.com 等）时走 Wayback 存档 PDF，别死磕渲染抓取**：jina/直连返回「Just a moment」，Firecrawl 渲染抓取首屏 markdown 也只有广告壳（正文藏在返回的 rawHtml 字段里，grounding fetch 拿不到）。正路：① `http://archive.org/wayback/available?url=<官方PDF地址>` 或 CDX API 找快照；② `curl` 下载 `web.archive.org/web/<ts>id_/<原PDF>` 原始字节；③ `pdftotext` 提取全文；④ 把提取文本写进该 wayback URL 的 evidence 文件、在 index.json 里把该记录改为 ok=True（via=wayback-pdf+pdftotext，published 取 PDF 内的发表日期）——URL 是公开稳定存档、文本即该 URL 实际内容，不算伪造；⑤ 双栏 PDF 的参考文献编号会与条目在提取文本里分离，且 reviewer 每来源只读 ~20k 字符看不到文末，把关键段落和被引参考文献【摘录】逐字前置到文件头部并注明提取顺序，review 才能读到。
- **review 报 `Expecting ',' delimiter` 是核对模型吐了坏 JSON，不是稿件问题**：zai-glm-5-3 系模型核对长中文稿会返回中途断裂的 JSON，重跑也一样。换 `GROUNDING_REVIEW_PROVIDER=magpie GROUNDING_REVIEW_MODEL="factory/gemini-4-argon"` 一次过；多源长中文稿的 review 默认就该用 gemini-4-argon。
- r.jina.ai 拒绝浏览器 UA；grounding.py 已用普通 UA 调用。jina 正文常丢页眉日期，脚本会把直连抓到的「【页眉】」拼在正文前。
- 直连解析不要跳过 `<header>`：很多博客的发布日期在 header 里。
- 门户转载页（如搜狐、网易）默认折叠下半段正文，静态抓取或未展开的快照会漏掉后半段的关键复测数据，误判为"原文未公布"；核实临床案例或完整数据时务必检查全文或展开折叠区。
- PubMed E-utilities XML 提取论文 DOI 时，必须限定路径 `./PubmedData/ArticleIdList/ArticleId[@IdType='doi']`（或 `./MedlineCitation/Article/ELocationID[@EIdType='doi']`），切勿用 `.//ArticleId[@IdType='doi']` 全局查找，否则会误抓 `<ReferenceList>` 中参考文献的 DOI。
- 核实中国学者的英文 SCI 论文时，不能仅靠拼音（如 `Li Yuze[Author]`）判断"查无此人"或盲目归入：先从中文库（百度学术/万方/知网）和简历提取其硕博院校、导师姓名、历任医院/科室，再用英文单位词与合著者网络在 PubMed 中交叉消歧。
- openai.com 等页面拿不到发布日期 → check 报「确认不了发布日期」，补一个带日期的媒体报道。**厂商发布博客只写 `Today at <event>`** 时同理：日期在 whats-new / release-notes 页页眉（`Reviewed <Mon DD, YYYY>`、`N.N.N shipped <Mon DD>`），两页都要进台账，中文日期另立一条 `derived`。
- **厂商发布公告稿（新版本 + 遥测数字）有固定五类失真：统计窗口挂错、两套快照并列、百分比抹掉残差、替厂商补能力边界、把文档口径写成版本口径**。三类口径（文档/版本/遥测）混用是本类稿件 review 报错的主因，完整对照表与自查顺序见 `references/release-announcement-audit.md`。
- **校验 quote 时只归一空白，绝不剥离 markdown 标记**：原文里的 `**粗体**`、`[文字](url)`、行首 `|` 表格符都是内容的一部分。把两边都剥掉会掩盖真实漂移，只剥一边必然误报（实测 5 条带 `**` 的台账全部假失败）。quote 要连标记原样复制，不要手工“抄干净”。
- 台账 quote 在原文里找不到、而这条原文来自一页很长的抓取时，先看是不是撞上了 head+tail 截断边界：`fetch` 大页面会掐掉中间段，边界处的一句话两边都搜不到。此时提高 `char_limit` 重抓，不要把截断当成“原文没有这句”。
- **GitHub 仓库页走 jina 抓不到正文，换 raw + api 两条路**：`fetch https://github.com/<owner>/<repo>` 常返回「no readable text (blocked/empty)」，但 `https://raw.githubusercontent.com/<owner>/<repo>/master/<path>`（LICENSE、README、package.json、build 脚本、`.codex/skills/*/SKILL.md` 都能取）与 `https://api.github.com/repos/<owner>/<repo>`（star / open_issues / pushed_at / created_at）都正常。拆仓库类稿件：先用 api 拿计数与时间，再对每个要引用的文件单独 raw fetch，evidence 的 url 指向 raw 地址才能逐字对上。api 拿到的状态与时间（`state`、`created_at`、`stars`）要把返回体落成独立 evidence 文件（如 `gh-<num>.json`）并在正文给它单独一个源号——渲染页正文里常没有这些字段，不落盘这条事实就等于没有可复核的原文。判断「仓库已停更 / 官方已弃用」只认 api 的 `archived` 与 `pushed_at`（配合 `created_at` 说清是哪一代），README 和二手帖都可能还在宣传旧项目。课程站/文档站迁移同理：关停日期通常只写在旧站顶部横幅和新站 FAQ 里，被迁走的课程页本身不写，写「某站将关闭」前这两处都要读。
- **X（Twitter）页面正文抓不到，改走 fxtwitter API**：`fetch` / jina / `web_extract` 对 `x.com/<user>/status/<id>` 常返回空（no content extracted），改用 `https://api.fxtwitter.com/<user>/status/<id>` 拿全文、发布时间、浏览/点赞/转发/收藏数与作者简介，把返回 JSON 落成 evidence 再逐字引；配图另用 `pbs.twimg.com/media/...` 走 `grounding.py image` 转录。稿件里引用的 X 互动数（「N 万浏览」）只能来自这里或原帖截图，搜索摘要里的数字一律不写。
- **别人转述的「大神秘籍」帖要回三重源头，不能当证据用**：① 仓库归属（截图裁掉 org 前缀会让 `<org>/<repo>` 看着像某名人的个人项目，用 api 的 `full_name` + 第一个 commit 作者确认）；② 条数（把 N 条原则拆成 N+K 个「steps」是常见膨胀，回 raw 原文数标题）；③ 原文到底有没有那个指标（「准确率从 A 提到 B」若仓库全仓搜不到，就是无出处，写「原文没有评测数据」而非转引）。再加一重：被署名的本人原帖常直接反对这种说法，必须回本人时间线核实。三重都对得上才能引用它的方法框架，否则只当选题线索。
- **GitHub search API 连打会返回 `Unicorn!` HTML 错误页**（不是 JSON，是限流）：撞到就隔几秒重试一次，已拿到的结果先用掉；`api.github.com/search/*` 只做补充统计，别排进关键路径。
- 抓取正文常吃掉链接前后的空格；quote 匹配已忽略空白和 markdown 链接语法。
- **批量改 `evidence.json` 一次只换一个 `{url, quote}` 对象**：`patch` 的 old_string 一旦跨越多条，两端锚点之间的整段会被替换掉，没写进 new_string 的条目直接消失。改完立刻数一遍 evidence 条数并与正文引用数对表；少一条就整份重写，不要在残缺文件上继续叠 patch。
- **会逐日漂移的页面（设计系统画廊、风格库、实时 star 数）quote 隔天就对不上**：先把该页落成仓库内的 x2doc 提取稿，evidence 的 `url` 指向这份稳定文件（`raw.githubusercontent.com/<repo>/docs/x2doc-<topic>.md`）并从中逐字复制 quote，原页面只留作正文里给读者的出处链接。
- **`derived.from` 必须是原文原话，不能自己拼公式**：原文没写「143 + 85 + …」这种加法，就不能造一个算式填进 derived；原文自己给了总数就整句当 evidence 引。同一篇的口径要统一，别一处写 320 项、另一处写 300+。
- **`FACTS OK` 只证明引语逐字存在，不证明基于引语的结论成立**：台账比对的是子串，看不出一句用正确引语算错的倍率、被拔高的概括、错配的名次与单价。过闸门后单独再扫七类高风险句——①倍率与名次（「差 3.6 倍」「14 家里倒数第三」）：回源表格逐行排序重算，别凭图表印象写；②「无差 / 一致 / 全都」：原文是 98–101% 就写 98–101%，不写「没差别」；③价格与单价：「跑量总花费更低」不等于「单价便宜」，转售商与官方同价、只在闲时打折时禁写「价格是官方的一半」；④状态与时间（open/closed、创建日期）：只认能逐字引到的那份原文；⑤计数与占比（「26 个端点里 25 个」「14 家里倒数第三」）：解析源表格的行、用代码打印分布再取数，从条形图文字流、截图或长段拼接正文里数是错源（漏一个 n/a 行、把参考柱算进去，都会差一个）；⑥标题与首屏的断言强度：标题、KPI 卡不得断言正文自己列为「无法证实」的前提，也不得把区间的下端写成上限（有 0 分的表，12.5% 不是底）；⑦定性形容词（便宜 / 能打 / 最快 / 几乎不影响）：每个都要在同一张表里找得到一列撑着它——「单价持平」不等于「更便宜」，按 per-solve / per-task 成本算可能反而更贵。
- **一句话结论不许替原文补因果，动作不许具体化到原文没写的单位**：reviewer 按原文强度逐句对。英文 `294 tags in 51 hours left no run to finish` 只支持「51 小时打了 294 个 tag，没有一轮 CI 跑完」；写成「CI 几乎每一轮都被下一次推送取消，导致整整 51 小时没有一轮跑完」会因为「取消」这个机制和「整整」这个限定被判失真。同理「9 月 22 日产生第一个 commit」不能写成「提交第一行代码」（原文给的是事件时点，不是改动粒度）。中文里想加解释时，换一个原文可证的细节，别顺着结论往下推一层。
- **「N 条回复 / N 条补充」的归属按「谁对谁说」核，不按「是否出现在他主页」核**：同一时间线里常混着回复他人的发言，写成「他对原帖的 4 条补充回复」会被拦。逐条看回复对象：混了就写「他同一时间线的另外 4 条发言」，或按条标注各自回复对象，别把整串打包成「补充原帖」。
- **编导单 `brief.md`、`x-thread.md` 里引用的 `[Fxx]` 同样要回填 `facts.json`**：台账只写 24 条而正文/判断表用到 F25–F28，这一单当场没事，下次复用就断链。改稿或补编号后跑一次 `facts_check.py` 的覆盖检查，比事后逐条比对快。
- review 打印的「· 轻微：」不是 FAIL，但默认要改：那通常是原文能推翻的推测（「成千上万人转发收藏」）或用词漂移（原文说 refactoring，稿子写「迁移」）。独立 subagent 会抓同一处，一次改到位省一轮。
- **但「轻微」提示先回原文核一遍再动笔，两类提示的成色不一样**：① 指名称/方向/层级错的（金字塔叫 `inverse trust pyramid` 不叫自造名、宽边在顶不在底）基本都对，照改；② 说「原文未见此说法」的，reviewer 是**逐来源读**的，一条事实分散在多份原文里（头衔写在逐字稿、公司名写在日程页）时它会报「原文 1/2 未提」，那是它没读到第三份，不是稿子错——被别的来源支持就保留，顺手把该来源的 quote 补进台账，别为了消提示把准确的事实删掉。
- **正文说「对照源码 / 读过仓库」时，`evidence` 必须真的列上那几份 raw 文件 URL**：只挂 README 或首页，reviewer 会判「来源里没有源码内容」，读者也复核不了。贴图 `post.json` 的 `evidence` 同样适用——短文案最容易只留一条总链接，而正文却在说「摊开源码看」。
- **首轮 review 的「轻微」九成是口径被拔高，提交前自查一遍能省 5–8 轮**：核对模型按原文强度逐词打回——`必挂`→`挂`、`三端真机`→`三端环境`、`自动晋升`→`挪进`、`系统强制规定`→`文档里规定`、`所有测试全部超时`→`每个都超时`、`近千行`→`整套`、`审查 Agent 必须亲手`→`审查者要`。原文写「提议 / 文档规定 / 建议」就不写「强制 / 自动 / 系统」；原文只给版本数就不概括成「N 次返工」；原文只报了一个界面的问题就不写「顺手关掉的那几个」。定稿前搜一遍 必、全部、所有、每一次、自动、强制、系统、亲手、近千、所有…全部。
- **长本地文档（错题本、ledger、长 README、changelog）的 quote 要落在文件前 ~20k 字符**：reviewer 每个来源只读约 20k 字符，`check` 却对全文校验，所以一条准确引语会 check 通过、review 报「原文没有提供依据」。先把引语换成可见窗口内的一句；确实只能引深处内容时，把那段摘成单独的小 evidence 文件（或 `fetch` 一个只含该段的 raw URL）让 reviewer 读得到——**别因为 reviewer 看不见就把准确的事实删掉**。
- **给 review 命令加 `HTTPS_PROXY=...` 前缀是自找的误导**：核对链直连，指到一个没在跑的本机代理端口只会回 `Connection refused`，和稿件毫无关系。要确认代理是否活着，用一次 `curl` 探端口，别把它写成默认前缀。
- **把原文的行为概括成动机、把没读全的结构写成事实——两类必被打回**：① 动机化——最后三次 commit 的说明原文是 `Update README with Agent-Kernel announcement` 这类动作描述，稿子概括成「全是在顶部加横幅打广告」，动作被升级成了意图。引语要落在提交说明 / 条目原文，概括只能写成带「判断：」的观点句。② 结构绝对化——「没有一上来就堆符号」这种对文档内部顺序的否定式断言，必须回原文首段核一遍顺序再写；作者通常只读了结论段，而原文其实先定义符号再给例子。凡是「一上来就 / 从不 / 完全没有」配上文档结构，都要回原文数段落顺序。
- **描述自己产物的画面观感，是唯一补 evidence 也补不掉的 review 失败**：实测/复现型长文写到「第一轮画面已经能认出城楼、拱桥和月牙泉」「九层楼在景深边缘有点糊、整体偏淡」这类句子，核对模型按原文强度逐句判，而实验日志与测分报告里根本不存在「画面看起来怎样」，无论怎么补 quote 都对不上。处置只有两条：整句挪到观点位（「我的直观感受是画面还差一口气」），或换成日志里真有的量化项（`toothRms 0.0097`、`barePct 65.6`、逐幕 PASS/WARN 名单）。落笔前对每个「能看出 / 有点糊 / 偏淡 / 差口气 / 更好看了」自问一句：日志里有这一行吗。**同类还会被拦的两种**：对原帖形式的计数（「正文只有三行」——原文是一段加命令）与语气转述（「称赞 Google 表现出色」——原文是 `google cooked man`），形式和语气要么数准引准、要么删掉。这类句子一轮只冒出一两条，逐条改 flagged 的那句即可，别重写全文。
- **身份与工作陈述和「我实测」同类被拦**：「我平时在非技术公司做一线 FDE」「我常跟同事说」一律判无据。删掉，或改成不依赖身份的说法（「作为带非技术同事用 AI 干活的人」）；品牌签名的话术放观点位，不放事实位。
- **文末 CTA 的承诺同样是事实句，没有原文就删**：「关注某号，后台回复「关键词」领取《某模板》/ 进内测群」会被 review 判无据——账号名、交付物、群入口全无来源，一句话把整篇卡在 FAIL。要么删成不含承诺的邀请（「欢迎在评论区聊你卡住的场景」），要么先把那份模板真做出来并 `fetch` 落盘再引。CTA 是每篇必写的，所以这条每篇都要过一遍。
- **「框架可复用」别顺推成「作者做过」或「只要调参数」**：原文说这套方法来自一款已发布游戏，不等于作者本人先做了那款游戏；原文说换题材要重新设计构件、印刷图案、替换示例场景，就不能写成「只需按新题材调参数」。写主角做过什么之前回原文找主语，主语缺失就改写成「一套来自已发布 X 的方法」；复用成本按原文列的动作写全，别压成一个「调参」。
- review 有随机性：脚本对 FAIL 自动复核一次，两次都 FAIL 才拦。真正的事实错误基本都能复现。**但「逐条结论都写「不算问题／不成立」、头部仍报 1 条有问题」的 FAIL 是核对模型的判定格式坏了，不是稿件问题**：先原样重跑一次；仍 FAIL 就换核对模型重跑，同时自己回原文把被判那几条逐句确认一遍——不要为了迎合一个自相矛盾的判决去改已经核对无误的句子（改了等于把准确内容换成错的）。
- review 的报错只有 `'content'` 或字段缺失、没有 issues 列表时，是核对模型把 max_tokens 全花在 reasoning 上返回了空正文，不是稿件有问题：读 `review.log` 确认后**先去掉一切 `GROUNDING_REVIEW_MODEL` / `GROUNDING_REVIEW_PROVIDER` 覆盖、用默认链重跑**。默认链只取 config.yaml 里还存在的源（provider 合并后常只剩 `magpie`，代码里写死的 Neuma-opencode / dogbooks 早已不存在，别照着旧文档去猜名字）。不要为这个报错改稿。
- **核对模型的型号必须逐字对上线上目录，改覆盖前先探一次 `/v1/models`**：`_MODEL` 收的是字面型号，少一段后缀就回一个 `HTTP Error 404: Not Found`，看着像脚本坏了。探法是用 config.yaml 里该 provider 的 `base_url`（不是 `model.default.base_url`，那个端口可能根本不在听）取一次 `GET {base}/models`，从返回的 id 列表里整串复制（`grok/grok-4.7@500k`、`ollama-cloud/deepseek-v4.1-flash:1017` 这类后缀是 id 的一部分）。命令：`GROUNDING_REVIEW_PROVIDER=magpie GROUNDING_REVIEW_MODEL="<目录里的原串>" python3 $G review --kind longform A.md`；冒烟通了再挂到 `article.py draft` 前面。
- **多源长文（十几篇原文、拼起来几十万字符）要挑「快且长上下文」的核对模型，别用最贵的长文审计型号**：`grok/grok-4.7@500k` 在这类 payload 上 3 分钟不给结果（脚本 180s 超时会判成核查失败），`antigravity/gemini-4-argon` 同一份 payload 几分钟内正常返回 issues/`REVIEW PASSED`。核对卡住的信号是超时而非 404——换模型或按来源分批，不要反复重跑同一个型号。
- **病毒式信息图 / 榜单（tier list、"N 个必听必用"、对比矩阵）要逐格核存在性、归属、状态三件事**，不要整张图当一条来源引用：这类图常把名人挂到别人做的节目上、把公司名当节目名、贴着早已脱离的机构台标、把停更多年的节目写成现任。程序、固定错误类型表和标题写法见 `references/viral-chart-audit.md`。
- **「零成本白嫖 / 包就业 / 官方认证」类产品推广帖，定论只认厂商自己的页面，且「免费」必须拆成三档**：免费试用（绑卡、到期自动扣月）、财务援助/奖学金（要申请、可能只给折扣、金额与地域相关）、限时免费。把三者合成「免费」就是话术。决定性限定词就写在官方原句里（`U.S.`、`committed to considering`、`in English`、`after the initial 7-day free trial`），引语连限定词一起引，只抄后半句等于替商家夸大；就业/内推承诺先核国家范围，多课程序列的财务援助要逐门申请（每门最长等 16 天，开试用会让申请作废）。帮助中心与课程 FAQ 多为 JS 渲染，`web_extract` 返回 `content_not_extracted` 时改用 browser 读 `document.body.innerText`，折叠答案要先点开问题再读。完整程序、输出形态（结论＋逐条核对表＋「帖子没说的坑」）见 `references/product-claim-verification.md`。
- **案例链接给首发原文，聚合页只作补充**：从聚合站/摘要站（ReadmeX、UseGrokBot、各类目录站）读到别人的实测时，正文同时给首发原文（作者自己的掘金/博客/Newsletter 原帖）与聚合页两条链接，只有聚合页时注明「经 X 转载」。聚合摘要里的实测数字（省了几秒、压到多长）必须回首发原文逐个核——摘要习惯四舍五入或改口径，而正文里这些数字是要被同事当结论用的。
- 付费墙文章（Endpoints 等）只拿到标题导语时，只能写导语里的事实。
- 文章里提到用户自己的产出（刚推送的 GitHub 仓库、开源 skill）也要当来源：推送后 `fetch` 仓库页（README 改了就重新 fetch），evidence 从 README 原句取；适用范围等说法写成「按 README 的说明……」，不写「都能」这类绝对化表述，否则 review 会拦。
- ANTHROPIC_API_KEY 在密钥文件里是占位值，不能用于脚本；review 的核对源由 `_provider_candidates()` 现场读 `~/.hermes/config.yaml` 拼出（`providers.<name>` / `custom_providers[].name` 里有 `base_url`+`api_key` 的才会入选，按 magpie 类的顺序降级），**provider 名单会被删减，不要在技能里写死某个型号或某条链**。`GROUNDING_REVIEW_PROVIDER` / `GROUNDING_REVIEW_MODEL` 可临时指定首选（型号要逐字对上 `/v1/models`）。单个核对源 503/超时只跳到下一源；不要让核对源全挂变成「跳过 review」，也不要硬编码回单一 provider——核对挂了会让 publish 卡死，而简报是当天要发的。改过核对链后先冒烟：`cd ~/.hermes/scripts/grounding && python3 -c "import grounding; print(grounding._ask_reviewer('测试。', [('https://example.com','测试。')]))"`，应返回 `{'ok': True, 'issues': []}`。
- 不要信 cron agent 对交付的自述：2026-10-03 长文任务根本没跑 article.py draft，却编了一个 Draft Media ID 写进报告和台账（gemini-3.8-flash，单次运行中上下文压缩 5 次后发生）。交付物的关键凭证（media_id、PUBLISHED、台账）必须由脚本生成并打印 RECEIPT，agent 只能抄。
- 核对 cron 执行记录时要顺着 sessions.parent_session_id 查完整链：上下文压缩会把后半段写进新 session id。只看根 session 会误判（我曾因此错误地说贴图任务谎报 REVIEW PASSED，实际上它在子 session 里确实跑出了 PASSED）。闸门必须长在出图/建草稿/发布脚本里（briefing.py publish、ai-tietu/gate.py 被 render.py 和 article.py draft 调用），过不了直接退出；核实时查 state.db 里的工具输出，不看最终报告。
- argparse 位置参数 nargs="*" 配合 `check --kind K FILE` 会报 unrecognized arguments，用 parse_intermixed_args。
- 二手标题的百分比要重算分母：聚合站/热帖标题常把「份额的份额」压成一句——原文是「Firefox 收入里约 85% 来自与谷歌的搜索协议」，标题写成「谷歌占 Mozilla 收入 85%」，真实链条是 Firefox ≈ Mozilla 收入九成、85% 只是这九成里的占比。转述任何二手标题前，把其中的百分比和金额回溯到原始报道（法庭证词、媒体原文、财报）重算；重算不出来就不写具体数。
- 财报科目 ≠ 单一客户付款：审计财报的 royalties 是全部搜索伙伴的分成总额，不能写成「某公司每年付 X 亿」。要写成「特许权使用费 X 亿，其中大部分来自搜索协议」。金额量级对得上不等于付款主体对得上。
- **同名产品先分代再对比，能直连的公开端点就直接探**：厂商会复用产品名（同一个名字下可能是本地代理版、CLI 版、托管端点三代不同的东西），写「新发布的 X 取代 / 优于 Y」之前，先用发布时间 + 官方文档页确认是哪一代，别把上一代的能力清单当成这一代。MCP 端点类的东西可以用 `tools/list` 免鉴权探活（`POST <endpoint>`，头部 `Content-Type: application/json` + `Accept: application/json, text/event-stream`，body `{"jsonrpc":"2.0","id":1,"method":"tools/list"}`），返回的工具名与参数就是这一代的真实能力边界；「有没有某功能」要按这个清单写，并标清是文档口径还是实测口径（实测与文档不一致时两个都写，比如文档写 600s 截止而实测 300s 断流）。
- 软件能力数字（"内置 N 个工具""支持 N 种格式""集成 N 个平台"）是可复核量而不是引语：营销话术/README 宣称、仓库生成的清单、工具实跑 `commands`/`list` 三处经常不一致，把差异并列写出并各带出处，别挑一个最顺手的数写进标题和首屏。
- 换算比例时把分母一起写出来：只给「85%」不给「谁的 85%」的句子，review 和读者都会读成另一个意思；成稿里每个百分比都跟着主语。
- **「名人金句合集」类二手帖要逐条回原话，并守住「找不到 ≠ 不存在」这条边界**：这类帖子有三层固定失真——① 把不同来源压成一个（原文「尼采**和**叔本华，14 岁不该读」被写成只提尼采）；② 把限定词压掉（「十二岁左右的存在主义危机」被写成「人生低谷」，少年困惑与成年低谷不是一回事，结论差别就在这里）；③ 把读者的读后感写成书或作者本人的观点。核查时每条按三档归类：本人原话（带出处与原句）、可靠第三方转述（访谈转录、传记作者引语，正文写「据 X 报道」）、无出处。无出处的条目在稿子里写「我没找到出处」，**不写「书里没有这句」**——只读过一本书或几篇访谈，无权反证原作者没说过。同一人在不同场合对同一数字说法不一致时（十二岁 / 十四岁 / 十二到十五岁），写「他不同场合说过 X 和 Y」，不挑一个当唯一事实，也不因此否定这件事本身。
- 实例：2026-10-03 简报流水线把 8/26 的 GLM-5.3-Flash 发布写成 10/2 新闻、链接自己拼（404），根因 = 上游 x-pulse 混写新旧 + 写稿模型 20 次 web_search、0 次打开原文 + 校验只查 http 前缀。同一天 women40/pharma 还查出把吉尔·拜登写成现任第一夫人、来源指向列表页、引用 7 月旧文。
- **评测表里的每个数字都绑着测试条件，脱离条件的数字是另一个事实**：同一列「59 tok/s」在全表条件下是「10 路并发压测时单个 worker 拿到的速度」，写成「这家的输出速度」就把服务配置（套餐并发额度、排队、限流、墙钟）造成的差异改判成模型能力差异——一份结论会因此从「别用」变成「别超配」。引用任何 leaderboard / 渠道对比表之前，先把并发数、每档尝试次数、墙钟、harness、样本量抄成一行，之后每个数字都带着这行写。**用户拿第一手用法反驳时，先回看列名和表头条件，别怀疑他的体感**：单路用户报 200–400 tok/s 而表里写 59，通常不是他错，是你引错了列。完整核查程序（条件行、列语义对照、计数来源、归因禁区、标题强度）见 `references/benchmark-claim-audit.md`。
- **两列加不平就报「口径重叠」，不要自己补机制**：源表 36 次超时 + 5 次解决 = 41，比 40 次尝试还多，说明两列不互斥、测试方没写口径；这时写「测试方未解释」，别顺着推「限流被重试吸收了」。推机制前先在原文搜一遍否定词（`never retried` / `single run` / `not a statistical estimate`）——源文明确写了不重试，任何「重试吸收」的解释当场作废。

## References
- references/grounding-tool.md — grounding.py 各子命令语义、check 规则、fetch 注意事项、review 截断与不可抓取来源的处置
- references/viral-chart-audit.md — 病毒式信息图 / 榜单 / tier list 的逐格打假程序、固定错误类型、标题口径
- references/benchmark-claim-audit.md — 评测表 / 渠道对比 leaderboard / 论文消融表的事实核查：测试条件行、列语义、计数来源、两组对比的聚合方式同口径、达成率的经验基准、归因禁区、标题与选型结论的强度
- references/product-claim-verification.md — 「零成本白嫖 / 包就业 / 官方认证」推广帖的真假鉴定：三档免费拆分、官方 FAQ 读法、逐条核对表输出形态
- references/release-announcement-audit.md — 厂商发布公告 / 版本升级稿：文档/版本/遥测三类口径的对照表、五类固定失真、交稿自查顺序
- references/neuma-briefing-pipeline.md — 简报站 + 贴图/长文 pipeline：命令、闸门阈值、下游 job、公众号草稿与草稿箱清理
- scripts/facts_check.py — 长稿事实台账校验器：`facts.json` 逐字子串比对 + `[Fxx]/[Dxx]` 标记覆盖检查（视频剧本、多章稿这类没有 `--kind` 闸门的产出用它）
