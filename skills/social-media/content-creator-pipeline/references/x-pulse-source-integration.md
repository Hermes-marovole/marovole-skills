# x-pulse 作为选题源 + 日报运维（更新于 2026-07-22）

## Why

每日 **xAI X+Web AI/科技日报**（x-pulse 系列）是情报层，不是发帖层；与 content-creator-pipeline 的接点是 `ideas/inbox.md`。用户要「每天 X 科技资讯日报」时 **update 既有 job**，禁止重复 create。

## Paths / Job

| 用途 | 路径 / 值 |
|------|------|
| 日报目录 | `VAULT/AI-Newsletter-Second-Brain/x-pulse/` |
| 命名 | `YYYY-MM-DD-xai-ai-tech-daily.md` |
| 选题写入 | `05-Outputs/content-creator/ideas/inbox.md` →「待筛选」（标注 `x-pulse YYYY-MM-DD`） |
| Prompt 备份 | `~/.hermes/scripts/xai-ai-tech-daily-prompt.md` |
| 邮件脚本 | `~/.hermes/scripts/send-xpulse-daily-email.py` |
| Cron | `2fab94f5879a` · `15 9 * * *` · deliver `local` |
| Model pin | `provider=xai-oauth` · `model=grok-4.5`（必 pin） |
| Toolsets | `web, browser, terminal, file, skills` |
| Workdir | `/Users/marovole` |
| 邮件 To/CC | `<EMAIL>` / `<EMAIL>` |

## 早间顺序

```
07:00  X 草稿（可消费昨日 x-pulse 选题）
08:00  Daily Brief
08:30  AI Newsletter
09:00  Smol AI News
09:15  x-pulse 日报 + 补 inbox + Apple Mail 推送
```

## 运维清单（修/改任务时）

1. `cronjob action=list` → 定位 `2fab94f5879a`，**不要 create 新 job**
2. update：schedule / prompt / pin model / toolsets
3. `hermes cron run 2fab94f5879a` 只排队到下一 tick；等 `last_status=ok` + 当日 vault md
4. 邮件：`python3 ~/.hermes/scripts/send-xpulse-daily-email.py <md>`，成功串 `OK emailed via Apple Mail`
5. 重叠的旧「科技日报」`a2c541cbfcb0`（deliver=email）保持 **paused**

## 消费规则（生成 X/公众号草稿时）

1. 读 inbox 时，注意带 `x-pulse YYYY-MM-DD` 标注的条目。
2. **不要**把 AI 热点默认当天发出——兴趣优先级仍是 游戏 > 硬件 > 美学 > 文化；AI 须有 **产品/工程判断** 才入队。
3. x-pulse 的「不建议追」列表要尊重。
4. 若 `queue/x/` 积压闸门触发，优先消化草稿，不追更日报热点。

## xAI 配额耗尽时的 fallback

**web_search (xai) 与 x_search 共享配额池**；403 / spending-limit / 空结果时立刻 fallback，禁止空转重试。

| 源 | 工具 | 可靠度 |
|----|------|--------|
| Hacker News | `browser_navigate` 或 HN Algolia `front_page` API | ✅ |
| VentureBeat AI | `browser_navigate` → snapshot | ✅ |
| TechCrunch / Reuters | browser | ❌ 超时/反爬 |
| web_extract (Tavily) | 常被 Surge Fake-IP 拦 | ❌ 勿作主路径 |

报告中标注「xAI 配额耗尽 / 浏览器直采」与 X 层缺失。

## 邮件推送

- **不用** Hermes `deliver=email`（EMAIL_* 未配 → `no delivery target resolved`）
- **不用** 默认依赖 ClawEmail（可能 `COREMAIL_UPSTREAM_ERROR`）
- **用** Apple Mail 脚本：ASCII 摘要正文 + 中文 MD 附件
- 通道细节见 skill `email-clients`（x-pulse / cron digest push）

## 已知故障模式

| 症状 | 原因 | 处理 |
|------|------|------|
| 连续多日 `last_status=error`，无新 md | 模型未 pin + 全局 provider 漂移 | update pin `xai-oauth`/`grok-4.5` 后 run |
| `deliver=email` 失败 | 无 EMAIL_HOME / platform | 改 local + 邮件脚本 |
| 空报告 | 配额耗尽仍只打 x_search | prompt 强制 browser fallback |
| 邮件无中文 | AppleScript `-e` 限制 | 预期行为；看附件 |
