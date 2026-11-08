# 形态 → 下游技能路由

每个下游任务开头告诉它：事实表在 `<hub>/facts.json`，只能用里面的事实；要新增事实就先 fetch 并补进事实表（编号续上），再用。

| 形态 | 下游技能 | 工作目录 | 门禁 / 交付凭证 |
|---|---|---|---|
| 长视频（YouTube 英文、B站中文） | long-form-ai-explainer-film + youtube-channel-growth-playbook | `~/HermesWork/长片科普/NN-主题/` | 事实表引语校验、剧本 [Fxx] 标注、抽帧检查；交付成片路径 |
| 短视频（视频号、小红书、B站、快手、YouTube Shorts） | science-video-daily | `~/HermesWork/抖音科普视频/NN-主题/{zh,en}/` | `gates.py` 全 PASS；发布后读管理页状态 |
| 短视频·AI 工具实测/复刻（抖音、视频号、小红书） | xilo-opus-video（画面）+ video-common（文案/合规）；先看 `~/HermesWork/抖音科普视频/` 里已有的同类工程（如 `opus-text-motion/`）直接复用脚本和发布文案格式 | `~/HermesWork/抖音科普视频/<slug>/{process,replica}/` | 主片（60–90 秒：原说法→过程录屏→成品→账单→结论）+ 副片（成品或同 brief 对比）；`发布.md` 写标题候选、简介、置顶评论、AI 生成声明、数据抓取日期 |
| 图文贴图·卡片 | ai-tietu 管线（`~/HermesWork/personal/media/ai-tietu/cron-prompt.md` 的步骤） | ai-tietu `posts/` 与 Obsidian queue/tietu | `grounding.py check/review --kind tietu`；`tietu_draft.py` 打印 RECEIPT |
| 图文贴图·字幕长图（素材是英文访谈） | interview-quote-image-posts + native-subtitle-quote-image | `~/HermesWork/字幕长图/NN-讲者-主题/` | 逐句对回原文时间戳；独立模型审核 PASS |
| 图文发布（小红书、微信贴图） | cn-social-image-post-publishing | 同上 | 后台读到帖子和图数 |
| 长文章（公众号） | wechat-animated-longform（排版 md2wechat） | Obsidian `05-Outputs/content-creator/queue/longform/<date-slug>/` | `grounding.py check/review --kind longform`；`article.py draft` 打印 RECEIPT |
| X thread / 长帖 | 无专用技能；按 content-grounding 写，每条带链接 | `<hub>/x/` | 每个事实都有 [Fxx]；交文案文件，用户手动发 |
| 微博 | 无专用技能 | `<hub>/weibo/` | 交文案 + 配图路径 |
| 各平台文案 | video-common/references/platform-copy.md | `<hub>/copy/<平台>.md` | 标题不承诺正文没回答的事 |
| 复盘 | creator-channel-analytics | `<hub>/review-<date>.md` | 数字来自后台，注明抓取时间 |

长片已有自己的 `facts.json`（同一格式）：直接把 hub 的 facts.json 复制过去作为起点，长片里新补的事实也要同步回 hub。
