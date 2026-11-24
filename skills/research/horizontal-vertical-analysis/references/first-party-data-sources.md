# 一手数据源地图：市场 / 竞品 / 获客

用途：做市场与竞品调研时，先在这里选题源，再去搜。目的不是"找到资料"，而是避免整篇报告建立在自媒体洗稿的二手数字上。

三条铁律：
1. **每个市场规模 / 增速 / CAC 数字，必须能在本次打开过的原文里看到**，否则标"未核实"或不写。二手转述的年份和分母经常被改。
2. 优先"被律所 / 审计审过"的公开一手件（招股书、10-K、监管备案），其次才是付费研报摘要，最后才是媒体。
3. 用户原话（差评、评论区）单独存档——功能决策要的是原句，不是你的转述。

---

## A. 行业基准与市场规模（Top-down）

| 源 | 能拿到什么 | 入口 | 备注 |
|---|---|---|---|
| 港股招股书「行业概览」章节 | 沙利文 / 灼识咨询的付费级 TAM/SAM、CAGR、竞争格局表，且经律所审阅 | `hkexnews.hk` 披露易全文检索 | 最被低估的免费一手件：只要赛道有一家拟上市公司，这章就有整条赛道的数 |
| SEC EDGAR（S-1 / 10-K / 20-F） | 美国上市公司自述市场规模、单位经济、留存率 | `efts.sec.gov/LATEST/search-index?q=` 全文检索 | 原文 PDF/HTML 可直接抓，`Risk Factors` 章常有竞品名单 |
| IQVIA / 艾昆纬 | 药品与保健品渠道规模、品类增速 | 官网白皮书 + 新闻稿 | 完整报告付费，公开摘要常带关键数字 |
| Euromonitor 欧睿 | 消费品分国别零售额 | 官网 summary 页 | 同上，摘要可用，全本订阅 |
| Nutrition Business Journal / SPINS | 美国膳食补充剂分渠道、分品类 | 官网 + 行业新闻引用 | 保健品赛道事实标准 |
| NIH ODS（Office of Dietary Supplements） | 营养素摄入、人群流行病学、成分安全性 | `ods.od.nih.gov` | 免费、可引用，适合做"为什么这个人群需要" |
| a16z / Bessemer / OpenView / ChartMogul | SaaS 与 AI 产品的 benchmark（CAC、留存、NRR、增长） | 各家年度报告页 | 给"产品该怎么定价/怎么获客"提供可比基准 |
| Sensor Tower / data.ai / QuestMobile | App 下载、留存、区域分布 | 官网免费报告页 | 判断赛道是否真有移动端需求 |

## B. 需求与痛点（Voice of Customer）

| 源 | 抓什么 | 方法 |
|---|---|---|
| 京东 / 天猫商品页 | 1–3 星差评、追评、问大家 | 浏览器抓取（登录态）+ 分页；差评里出现"胃反酸/吞不下/能不能和降压药一起吃"这类句子，就是功能缺口 |
| Amazon 商品页 | 差评 + `Top reviews` | 同上；`?filterByStar=critical` 直接定位差评 |
| App Store / Google Play | 长差评 + 版本更新日志 | iTunes Search API（`itunes.apple.com/search`）+ 评论 RSS（`.../rss/customerreviews/page=1/id=<id>/sortby=mostrecent/json`），免爬 |
| G2 / Capterra / Trustpilot | B2B 与 SaaS 的 "Cons"、迁移原因 | 页面直取 | 免费层限制条数，够看模式 |
| 小红书 / 知乎 / Reddit | 求助帖、比价帖、"求推荐" | 站内搜 + `site:` 限定 | 抓原句，别抓摘要 |
| Product Hunt | 发布评论里的"缺什么" | 页面直取 | 早期需求信号 |

## C. 获客与流量拆解（Go-to-market）

| 源 | 回答什么 | 备注 |
|---|---|---|
| Semrush / Ahrefs / DataForSEO | 竞品 Top Pages、keyword gap、搜索量、CPC | CPC 高的词 = 有付费意愿的真痛点；无订阅时用 `serper` 逐词查 SERP 竞争度 |
| SimilarWeb | 流量结构（搜索 / 社交 / 直访 / 投放占比） | 判断对手靠内容还是靠买量 |
| Meta Ad Library | 在投素材、跑了多久 | 跑满 30 天以上的素材通常是正 ROI，钩子可直接拆 |
| TikTok Creative Center | 热门商业素材榜 | 海外短视频获客选题 |
| Google Ads Transparency Center | 竞品投放文案与落地页 | 验证它讲的故事和落地页是否一致 |
| 巨量算数 / 蝉妈妈 / 新红 / 微信指数 | 国内内容侧热度与带货数据 | 需登录或有免费额度 |

## D. 竞品实体发现与表格补全

- `parallel-cli`（已装；`parallel-cli login` 或 `PARALLEL_API_KEY` 鉴权）：`findall` 按自然语言找出一批公司（"北美做个性化营养订阅的 D2C 品牌"），`enrich` 批量补列（客单价、核心 SKU、复购机制、融资）。输出结构化表，直接进横向对比表。
- Exa MCP：`web_search_exa` 找相似公司，`agent_run` 做多步深度调研。
- 公司背景：Crunchbase / LinkedIn（团队履历）/ 官网 About + 定价页；三者交叉再写。

## E. 交付前的核查动作

1. 每个数字回原文一次：`web_extract` 或浏览器打开，确认年份、分母、口径。
2. 把"市场规模"与"我们的可服务市场"分开写——TAM 大不等于能吃到。
3. 差评结论附 3–5 条用户原句，别只给归纳。
4. 输出按用户偏好：浅色简洁、一页到底的 HTML 报告，或 Markdown 台账 + 来源列。
