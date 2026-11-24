# x-pulse 浏览器直采兜底记录（2026-07-12）

## 触发条件

`x_search` 和 `web_search`（xAI backend）均返回 HTTP 403：

```json
{
  "code": "personal-team-blocked:spending-limit",
  "error": "You have run out of credits or need a Grok subscription."
}
```

## 替换数据路径

正常路径：`x_search` → Grok synthesis + post citations
兜底路径：`browser_navigate` → 站点直采 → manual curation

## 直采站点及信息密度评估

| 站点 | URL | 获取内容 | 信息密度 | 注意事项 |
|------|-----|---------|---------|---------|
| Hacker News | `https://news.ycombinator.com/` | 社区投票 top 30 | ★★★★高 | AI 帖通常在前 15 条；滚动获取更多 |
| The Verge AI | `https://www.theverge.com/ai-artificial-intelligence` | 发布型媒体头条 | ★★★★高 | LATEST IN AI 区块含完整摘要 |
| Anthropic Newsroom | `https://www.anthropic.com/news` | 官方产品/政策公告 | ★★★★高 | 精确日期+分类，适合快速扫描 |
| AI News | `https://www.artificialintelligence-news.com/` | 产业落地案例 | ★★★中高 | 药物研发、企业 AI 案例多 |

## 直采流程（此运行实测）

1. `browser_navigate('https://news.ycombinator.com/')` → 获取前 12 条
2. `browser_scroll('down')` + `browser_snapshot(full=True)` → 获取完整 30 条
3. `browser_navigate('https://www.theverge.com/ai-artificial-intelligence')` → LATEST IN AI 区块
4. `browser_snapshot(full=True)` → 展开所有文章摘要
5. `browser_navigate('https://www.anthropic.com/news')` → 获取当天及近期公告列表
6. `browser_navigate('https://www.artificialintelligence-news.com/')` → LATEST 区块

## 此次运行捕获的关键信号

1. Apple 诉 OpenAI 窃取硬件机密（The Verge, Jul 11）
2. OpenAI 安全主管 Heidecke 离职（The Verge, Jul 11）
3. Brockman 集权 + IPO 叙事（The Verge/CNBC, Jul 11）
4. ChatGPT 5.6 + ChatWork + Codex 三分产品线（The Verge, Jul 11）
5. Anthropic Bernanke 进入治理信托 + Claude Science（Anthropic News, Jul 9）
6. GPU 循环融资争议（HN, io-fund.com, Jul 12）
7. Mesh LLM 分布式 AI 计算（HN, Jul 12）

## 直采 vs 搜索的数据差异

| 维度 | xAI 搜索 | 浏览器直采 |
|------|---------|-----------|
| X 实时讨论热度 | ✅ 有 | ❌ 无 |
| 帖子引用链接 | ✅ 有 | ❌ 无 |
| 深度内容 | ❌ 较浅（Grok 合成摘要） | ✅ 完整的文章摘要/标题 |
| 产业落地新闻 | ❌ 偏少 | ✅ 较多（AI News 源） |
| 社区评论内容 | ❌ 无 | ✅ 有（HN 评论计数+热度） |
| 时效性 | 实时 | 取决于页面刷新频率 |

## 分节/段落格式

浏览器直采的内容结构应为：

1. **Top 5 Signals**（不变，是标准格式）
2. **热议话题**（取代"X 热议"——不存在 X 帖子引用，改成"浏览器直采综合"）
3. **Web 头条**（不变）
4. **选题建议**（不变）
5. Frontmatter 中标注 `tools` 字段列出实际使用的浏览器工具

## 构建日报时的检查清单

- [ ] Frontmatter 中标注数据源限制：xAI quota exhausted
- [ ] 数据源说明段落解释替代方案
- [ ] 不编造 X 帖子引用——不存在的就明说"本期无 x_search"
- [ ] 关键 URL 指向原文来源（可能需从页面文本中提取/推断 URL）
- [ ] 选题建议基于真实内容，不凭空想象
