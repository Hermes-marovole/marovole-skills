# 平台分工（用户 2026-10-07 定的范围）

平台的字数、声明、按钮等操作细节**不在这里重复**，以表中「细节见」的文件为准；那些文件记的是实测过的操作和用户拍板的规则。表里「角色」一列是智子的策略假设，等有数据再修正。

| 优先级 | 平台 | 语言 | 接哪些形态 | 角色（假设） | 细节见 | 自动化程度 |
|---|---|---|---|---|---|---|
| 主力 | YouTube | 英文 | 长视频；短视频英文版投 Shorts | 收入主阵地，美国观众 | youtube-channel-growth-playbook、publishing.md | 制作与 Studio 网页端上传发布均可经 ego-browser 自动完成 |
| 主力 | 微信公众号 | 中文 | 长文章（含代码 GIF） | 深度与信任，中文母稿 | wechat-animated-longform、md2wechat | 建草稿自动；群发和勾原创在公众号助手 App 手动 |
| 主力 | 视频号 | 中文 | 短视频 | 微信生态内的短视频主力 | science-video-daily/references/publishing.md | 浏览器脚本已实测 |
| 主力 | 微信贴图 | 中文 | 图文贴图 | 快节奏触达，引到长文 | cn-social-image-post-publishing/references/platform-quirks.md、ai-tietu | 建草稿自动（tietu_draft.py / md2wechat create_image_post） |
| 主力 | X | 英文或中文（3D拆解/大佬说等视频直发中文） | 长文章的 thread / 长帖，贴图、短片素材 | 海外分发和引流 | science-video-daily/references/publishing.md | ego-browser 网页端自动上传发帖已实测 |
| 次要 | 小红书 | 中文 | 图文、短视频 | 搜索流量，女性受众 | publishing.md、platform-quirks.md | 浏览器脚本已实测 |
| 次要 | B站 | 中文 | 长视频中文版、短视频 | 中文长片的主阵地 | publishing.md（B站一节） | 浏览器脚本已实测（短视频） |
| 同步 | 抖音 | 中文 | **只接视频**（短视频为主，长视频可选） | 视频同步分发，不单独定制 | publishing.md（抖音一节） | 浏览器脚本已实测 |
| 再次 | 微博 | 中文 | 贴图九宫格、长文摘要、短视频 | 热点讨论 | 无 | **缺口**：没有发布技能，只出文案 |
| 再次 | 快手 | 中文 | 短视频 | 下沉市场补量 | publishing.md（快手一节） | 浏览器脚本已实测 |

## 规则
- 一个形态可以投多个平台，但每个平台单独写标题和正文（video-common/references/platform-copy.md）。
- 中美两边不是翻译关系：同一份事实表，切入点和例子按各自观众重选。
- 再次平台只在主力和次要平台做完后补发，不单独占审核时间；审核预算不够时先砍它们。
- 抖音只同步视频（用户 2026-10-07 定），文案沿用视频号版本改字数即可，不单占审核时间。
- X 用英文（用户 2026-10-07 确认）。
- TikTok 不在范围内。
