---
name: web-crawler
description: 当用户需要抓取网页数据、竞品信息收集、批量爬取网站内容、从页面提取结构化数据或爬取搜索引擎结果时自动触发。关键词：爬取、爬虫、抓取、scrape、crawl、数据采集、页面解析、web scraping、竞品数据。
version: 1.0.0
author: 翡冷翠
---

# Web Crawler 三合一 Skill

## 使用场景
- 竞品信息收集（价格、功能、文案）
- 行业报告和资讯整理
- 为 RAG 系统准备训练数据
- 产品评论和社交媒体舆情监控
- 客户教育内容的自动化采集

## 三引擎架构 → 四引擎

```
页面是普通 HTML（没有大量 JS 渲染）？→ 用 Jina AI 或 DuckDuckGo
页面是单页应用或动态加载？→ 用 Browserbase (Hermes内置) 或 Playwright/CDP
页面有登录墙、Cloudflare防护、或被bot检测拦截？→ 用 Dokobot（真实Chrome浏览器）
需要全站爬取？→ 用 Crawl4AI 或 FireCrawl
不确定？→ 默认用 Jina AI → 失败用 Browserbase → 再失败用 Dokobot
```

## 工具选择指南

### 方案 A：轻量级单页抓取

**工具 1：Jina AI Reader（无需 API Key，最快）**

```bash
# 在任意 URL 前加 r.jina.ai/
curl https://r.jina.ai/https://example.com/article
```

- **优点**：无需注册、无费用、极快
- **输出**：干净的 Markdown，适合直接喂给 LLM
- **局限**：只能抓单页，不支持 JS 渲染

**工具 2：DuckDuckGo 搜索抓取（Hermes 内置）**

- 使用 `duckduckgo_search` 工具搜索并取得结果
- 适合：快速获取搜索结果的摘要和链接

### 方案 B：浏览器自动化

**工具：Playwright / CDP / Puppeteer**

```python
# 示例：用 Playwright 抓取 JS 渲染页面
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    # 等待 JS 渲染完成
    page.wait_for_selector(".content")
    text = page.inner_text(".content")
    browser.close()
```

- **适用**：单页应用、动态加载、需要交互的页面
- **优势**：能抓到真实渲染后的内容

### 方案 D：真实浏览器（登录态 + 反检测）— Dokobot

**Dokobot — 用你自己的 Chrome 浏览器读取页面**

```bash
# 安装（一次性）
npm i -g @dokobot/cli@latest
dokobot install-bridge --browser chrome
# + Chrome Web Store 安装 Dokobot 扩展

# 本地模式（免费无限量）
dokobot read --local <url>                    # 读取页面 → 结构化 Markdown
dokobot read --local --device <id> <url>      # 多设备时指定 Chrome 实例
dokobot search --local <query>                # 联网搜索
dokobot doko list                             # 查看已连接设备
```

- **优势**：用你的真实 Chrome（含登录态、Cookie），免疫 bot 检测，免费无限量
- **输出**：列感知结构化 Markdown，链接编号引用，比原始 HTML 省 99% token
- **局限**：需要 Chrome 保持运行，有多个 Chrome Profile 时需用 `--device` 指定
- **适用场景**：登录墙页面、Cloudflare 防护站、小红书/知乎等国内平台、内部站点

**多设备处理**：
```bash
# 列出所有 Chrome 实例
dokobot doko list
# 输出示例：
#   5652f81d-... (pid 68773)
#   81a69071-... (pid 12052)

# 指定设备读取
dokobot read --local --device <YOUR_CHROME_DEVICE_ID> <url>
```

**与 Hermes 集成**：
- Hermes skill 已安装：`~/.hermes/skills/dokobot/`（自动由 `dokobot install-skill --agent hermes-agent` 安装）
- 通过 terminal 工具直接调用，输出直接喂给 LLM
- 作为 Browserbase + Jina Reader 之后的第三级 fallback

**工具 1：FireCrawl（全站专家）**

```bash
# 单页抓取
curl -X POST https://api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# 全站爬取
curl -X POST https://api.firecrawl.dev/v1/crawl \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "limit": 50}'
```

- **优势**：在线平台可视化操作，支持 PDF 处理
- **需要 API Key**

**工具 2：Crawl4AI（开源本地化）**

```bash
pip install crawl4ai

# 快速开始
crawl4ai https://example.com -o output.md
```

- **优势**：本地运行，无 API Key，可自定义 JS 脚本
- **局限**：需要本地 Python 环境

**工具 3：AnyCrawl（三引擎合一）**

```bash
# Docker 一键部署
git clone https://github.com/any4ai/anycrawl.git && cd anycrawl
docker compose up -d

# 单页抓取
curl -X POST https://api.anycrawl.dev/v1/scrape \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "engine": "cheerio"}'

# 全站爬取
curl -X POST https://api.anycrawl.dev/v1/crawl \
  -H "Authorization: Bearer ***" \
  -d '{"url": "https://example.com", "engine": "playwright", "max_depth": 2, "limit": 10}'

# 搜索引擎结果
curl -X POST https://api.anycrawl.dev/v1/search \
  -H "Authorization: Bearer ***" \
  -d '{"query": "keywords", "limit": 10, "engine": "google", "lang": "zh"}'
```

- **特点**：支持 LLM 结构化提取、多引擎自动切换

## 工作流程

### Step 1：确认抓取目标
1. URL 是什么？单页还是多页？
2. 页面是静态 HTML 还是 JS 渲染？
3. 需要什么格式的输出？Markdown / JSON / 纯文本
4. 是否需要结构化提取（如产品名、价格、描述）？
5. 数量级？单页 / 十页 / 百页+

### Step 2：选择工具组合

**快速决策树：**

```
只有几个 URL，且页面简单→ Jina AI（无需 API Key）
只有几个 URL，但是 JS 渲染→ Browserbase / Playwright
页面有登录墙或Cloudflare→ Dokobot --local（真实Chrome）
需要搜索 + 页面抓取→ DuckDuckGo + Jina AI
需要批量抓取数百页→ FireCrawl / Crawl4AI
需要全站爬取 + 结构化提取→ AnyCrawl / FireCrawl
```

### Step 3：执行抓取

**使用 Hermes 工具执行：**

```bash
# 方式 1：Jina AI（无需认证）
curl -s https://r.jina.ai/https://example.com

# 方式 2：自定义脚本（用 execute_code 或 terminal）
python3 -c "
import requests
resp = requests.get('https://r.jina.ai/https://example.com')
print(resp.text)
"

# 方式 3：Hermes 内置 web_extract（少数场景）
web_extract(url="https://example.com")
```

**如果需要登录态：**

首选 Dokobot（你的 Chrome 自带登录态，无需额外配置）：
```bash
dokobot read --local <url>
```

备选 Playwright 手动登录：

```python
# 使用 Playwright 处理登录态
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 非无头模式便于登录
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.com/login")
    # 手动登录后，保存 storage_state
    context.storage_state(path="auth.json")
    # 后续用 auth.json 自动登录
```

### Step 4：数据清洗与结构化

**如果需要提取结构化数据：**

```python
# 示例：从 Markdown 中提取产品信息
import re

def extract_products(text):
    # 用正则或简单字符串匹配提取
    # 实际中建议用 LLM 做结构化提取
    return structured_data
```

**或用 LLM 进行提取：**

```
从下面的 Markdown 内容中，提取所有产品信息，输出 JSON：
{
  "products": [
    {"name": "...", "price": "...", "description": "..."}
  ]
}
```

### Step 5：验证与存储
1. **验证完整性**：检查是否有缺失页面或缺失字段
2. **验证准确性**：随机抽样几条数据与原始页面对比
3. **存储**：
   - 小量数据 → Markdown / JSON 文件
   - 大量数据 → SQLite / CSV
   - 持久化 → 项目目录下的 data/ 文件夹
   - **要交付「全量数据集」时**（用户要 CSV+JSON 双格式）：按 `references/bulk-dataset-export.md` 的目录契约产出 —— 同 stem 成对的 JSON/CSV（utf-8-sig）、宽表+长表、`dataset_manifest.{json,csv}`、README 清单表、`_scripts/`+`_cache/` 随数据一起留。

## 实战案例

### 案例 1：抓取单篇文章

```bash
curl -s https://r.jina.ai/https://jina.ai/news/jina-embeddings-v3 | head -100
```

### 案例 2：批量搜索竞品

```python
# 用 DuckDuckGo 搜索，再用 Jina AI 抓取每个结果
# 注意：新包名是 ddgs（pip install ddgs），旧名 duckduckgo_search 已拆分弃用
from ddgs import DDGS
import requests

def search_and_scrape(query, max_results=10):
    with DDGS(verify=False) as ddgs:  # verify=False 避免 macOS LibreSSL TLS 错误
        results = list(ddgs.text(query, max_results=max_results))
    
    for r in results:
        url = r['href']
        try:
            resp = requests.get(f"https://r.jina.ai/{url}", timeout=30)
            print(f"=== {url} ===")
            print(resp.text[:2000])
        except Exception as e:
            print(f"Failed: {url} - {e}")

search_and_scrape("probiotics supplement brand comparison 2025", 5)
```

### 案例 3：爬取整个知识库

```bash
# 使用 Crawl4AI
crawl4ai https://docs.example.com --max-depth 3 --limit 50 -o output/

# 或 FireCrawl API
curl -X POST https://api.firecrawl.dev/v1/crawl \
  -H "Authorization: Bearer ***" \
  -d '{"url": "https://docs.example.com", "limit": 50}'
```

### 案例 4：结构化数据提取

```bash
# 使用 AnyCrawl 的 LLM 提取
curl -X POST "https://api.anycrawl.dev/v1/scrape" \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "json_options": {
      "schema": {
        "type": "object",
        "properties": {
          "company_mission": {"type": "string"},
          "is_open_source": {"type": "boolean"},
          "employee_count": {"type": "number"}
        },
        "required": ["company_mission"]
      }
    }
  }'
```

## 四种方案横向对比

| 特性 | AnyCrawl | Jina AI | FireCrawl | Crawl4AI | Dokobot |
|---|---|---|---|---|---|---|
| 部署方式 | Docker / 云端 | 云端（无需部署） | 云端 API | Python pip | Chrome扩展 + CLI |
| API Key | 需要 | 不需要 | 需要 | 不需要 | 不需要（本地） |
| 全站爬取 | ✅ | ❌ | ✅ | ✅ | ❌ |
| SERP 爬取 | ✅ | ❌ | ❌ | ❌ | ✅ |
| LLM 提取 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 登录态/真实浏览器 | ❌ | ❌ | ❌ | ❌ | ✅（你的Chrome） |
| 过Cloudflare | ❌ | ❌ | ❌ | ❌ | ✅ |
| 开源 | ✅ | ❌ | ✅ | ✅ | ❌ |
| 价格 | 付费 | 免费 | 付费 | 免费 | 本地免费 |
| 适用场景 | 通用型 | 快速单页 | 全站转Markdown | 本地定制 | 登录墙/反检测站 |

## 常见问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 抓取结果为空或不完整 | 页面是 JS 渲染，用了静态工具 | 切换到 Playwright 或 Puppeteer |
| 被目标网站封禁 IP | 请求频率过高 | 使用代理或降低请求频率 |
| 页面有登录墙/需Cookie | Jina AI / Browserbase 无用户登录态 | 切换到 Dokobot（用真实 Chrome） |
| Cloudflare / bot 检测拦截 | 目标站识别 headless 浏览器 | 切换到 Dokobot --local（真实浏览器不被拦） |

## 登录态批量抓取的人机验证铁律（2026-09 实测 Web.Cafe/Cloudflare）

用真实浏览器（ego lite / Dokobot）慢速抓登录墙后的付费内容时：

1. **区分失败类型再重试**——把"页面无正文"细分为 CHALLENGE / NOT_LOGGED_IN / RATE / NO_BODY。通用"无正文就重试"会在验证页上死循环，实测 1 小时内连撞 ~20 次验证页，是在主动喂风控信号。
2. **一遇人机验证立即停，绝不自动重试（严禁对 Turnstile/CAPTCHA 复选框调用 click()，自动化点击必报 Verification failed）**。验证框留给用户点（`handOff()`）；刚验证完 ≠ 安全，实测验证通过后 2 分钟内再弹——Cloudflare 是按行为模式识别批量翻页，不是按速率。
3. **降速换不来通行证**。连续翻页被标记后，5s/篇 和 60s/篇 一样会拦。付费账号场景的正确姿势：核心专栏 + 真人阅读节奏（1–2 min/篇、每天 ≤70 篇、多天完成），或放弃全量改按需抓取。
4. **断点续跑是底线**：记录已下清单、跳过已完成；遇到验证写标记文件等待人工，不反复试探。
| 搜索结果不准确 | 区域限制或验证码 | 使用代理或更换搜索引擎 |
| 全站爬取超出限制 | limit/max_depth 设置不当 | 调整参数，使用 exclude_paths 过滤 |
| LLM 提取结果不准确 | schema 定义不清晰 | 精确定义字段类型和 required |

## 大规模多维度研究抓取（Search × Scrape 管线）

当需要抓取大量数据（如多维度研究报告、全行业竞品分析）时，单个 `execute_code` 脚本会在 5 分钟超时被杀。正确做法：

### Pitfall：execute_code 5 分钟超时

`execute_code` 有 300 秒硬超时。一个 8 维度 × 5 关键词 × 3 页面抓取的完整管线（≈120 次 HTTP 请求）需要 15-25 分钟，远超限制。

**绝不能**把完整抓取管线塞进一个 `execute_code` 调用。

### 正确模式：脚本文件 + terminal 后台分批

1. **写脚本到文件**（`write_file`），不内联到 `execute_code`
2. **脚本接受 `--country` / `--dims` 参数**，可按维度分片执行
3. **用 `terminal(background=True, notify_on_complete=True)` 并行启动多个批次**，每批 3-4 个维度（约 3-5 分钟可完成）
4. 完成后自动通知，无需轮询

```python
# scrape_all.py — 参数化抓取脚本模板
# 用法: python3 scrape_all.py --country china --dims 0,1,2,3
#       python3 scrape_all.py --country us --dims all
import argparse, time, os, requests
from ddgs import DDGS

def search_ddg(query, max_results=6):
    with DDGS(verify=False) as ddgs:          # verify=False 避免 macOS LibreSSL TLS 错误
        return list(ddgs.text(query, max_results=max_results))

def scrape_jina(url, timeout=20, cap=6000):
    resp = requests.get(f"https://r.jina.ai/{url}", timeout=timeout)
    if resp.status_code == 200 and len(resp.text) > 300:
        return resp.text[:cap]
    return None

def process_dim(country, dim_name, keywords, outdir):
    parts = [f"# {country} — {dim_name}\n## Search Keywords\n"]
    for kw in keywords:
        parts.append(f"- `{kw}`")
    parts.append("\n## Sources\n")
    for kw in keywords:
        results = search_ddg(kw)
        time.sleep(0.3)
        scraped = 0
        for r in results[:5]:
            if scraped >= 2: break              # 每关键词最多抓2页，控制总时长
            url = r.get("href", "")
            content = scrape_jina(url)
            if content and len(content) > 400:
                parts.append(f"\n### {r['title']}\n**Source:** {url}\n\n{content}\n---\n")
                scraped += 1
                time.sleep(0.2)
        # Fallback: 如果 Jina 抓取全失败，保留搜索摘要
        if scraped == 0 and results:
            for r in results[:3]:
                parts.append(f"\n### {r['title']}\n**Source:** {r.get('href','')}\n**Snippet:** {r.get('body','')[:400]}\n---\n")
    with open(os.path.join(outdir, f"{dim_name}.md"), "w") as f:
        f.write("\n".join(parts))
```

```bash
# 并行启动4个后台批次（每批3-4维度，约3-5分钟完成）
terminal(background=true, notify_on_complete=true):
  cd ~/project && python3 scrape_all.py --country china --dims 0,1,2,3
terminal(background=true, notify_on_complete=true):
  cd ~/project && python3 scrape_all.py --country china --dims 4,5,6
terminal(background=true, notify_on_complete=true):
  cd ~/project && python3 scrape_all.py --country us --dims 0,1,2,3
terminal(background=true, notify_on_complete=true):
  cd ~/project && python3 scrape_all.py --country us --dims 4,5,6,7
```

### 关键要点

| 要点 | 说明 |
|------|------|
| `ddgs` 库（新） | `pip install ddgs`；旧名 `duckduckgo_search` 已拆分。`max_results` 必须用 keyword 参数 |
| `DDGS(verify=False)` | macOS LibreSSL TLS 兼容；不传会在某些环境下报错 |
| Jina Reader cap | `resp.text[:6000]` 截断每页内容，避免单文件过大 |
| Snippet fallback | Jina 抓取失败时保留 DDG 搜索摘要（`r['body']`），不至于完全空文件 |
| 每关键词抓 2 页 | 平衡覆盖率和时间；5 关键词 × 2 页 = 10 来源/维度 |
| `time.sleep(0.3)` | 搜索间加 0.3s 延迟，避免 DDG 速率限制 |
| 分批并行 | 4 个 `terminal(background=True)` 同时跑，总时间 ≈ 单批时间而非 4 倍 |

### 子Agent 委派 vs 脚本分批

`delegate_task` 派出的子Agent 也可执行抓取，但存在风险：
- 子Agent 进程可能被 SIGTERM 杀掉（本session中发生过），导致只完成部分维度
- 子Agent 产出的文件质量不一致（有的写了完整正文，有的只写了搜索关键词没抓到内容）

**推荐**：用 `delegate_task` 做研究规划/数据分析等推理任务；用**脚本文件 + terminal 后台分批**做确定性抓取，更可控、可恢复、可检查中间结果。

## 社区UGC平台反爬攻略（Walled-Garden Community Scraping）

当需要从社交媒体/社区平台抓取一手用户声音（UGC）时，几乎所有主流平台都有反爬措施。以下是经过实测验证的平台攻略表（2026-06 实测）：

### 平台反爬状态表

| 平台 | Jina Reader | curl/requests | Reddit JSON API | DDG `site:` 搜索 | Dokobot（真实Chrome） | 最佳策略 |
|------|:-----------:|:------------:|:--------------:|:---------------:|:-------------------:|----------|
| Reddit | ❌ 403 | ❌ 403 | ❌ 403 | ✅ 摘要 200-300字 | ✅ 需登录态 | DDG site: 摘要 + Dokobot |
| Quora | ❌ CAPTCHA | ❌ CAPTCHA | N/A | ✅ 摘要 200-300字 | ✅ 需登录态 | DDG site: 摘要 |
| 知乎 | ✅ zhuanlan文章 | ⚠️ 部分可访问 | N/A | ✅ 摘要+URL发现 | ✅ | Jina on zhuanlan + DDG |
| 小红书 | ❌ 反爬 | ❌ 反爬 | N/A | ✅ 摘要 100-200字 | ✅ 需登录态 | DDG site: 摘要 |
| 微信视频号 | ❌ 无公开网页 | ❌ 无公开网页 | N/A | ❌ 不索引 | ✅ 借公众号后台 | 登 `mp.weixin.qq.com` 调 `/cgi-bin/videosnap` |
| 抖音个人主页 | ❌ 登录墙 | ❌ 接口签名 | N/A | ⚠️ 仅头条收录部分 | ✅ 滚内部容器 | 真实浏览器滚 `overflowY:auto/scroll` 容器 |

### 策略 4：微信视频号与抖音个人主页全量作品抓取（真实浏览器 `ego-browser`）

1. **微信视频号全量列表（无需视频号作者本人扫码）**：
   - 视频号网页端只有创作者登录页，对外无个人主页。但**任何已登录的微信公众号后台（`mp.weixin.qq.com`）图文编辑器都内置了「插入视频号动态」接口**，可免验证码检索并拉取任意公开视频号的全量作品列表：
   - 先搜账号获取 `finder_username`（形如 `v2_...@finder`）：
     `GET /cgi-bin/videosnap?action=search&scene=1&buffer=&query=<视频号名>&count=21&token=<mp_token>&lang=zh_CN&f=json&ajax=1`
   - 再用 `last_buff` 循环翻页拉全量视频（每页 15 条，含 `desc` 完整文案、`export_id`、封面与时长）：
     `GET /cgi-bin/videosnap?action=get_feed_list&username=<finder_username>&buffer=<last_buff>&count=15&scene=0&token=<mp_token>&lang=zh_CN&f=json&ajax=1`
2. **抖音个人主页全量作品与无水印原片批量下载（突破首屏 29 条限制 + `opencli` 同源接口）**：
   - **DOM 滚动兜底**：抖音用户主页作品网格挂载在内部虚拟滚动容器上，在 `page.evaluate` 中筛选 `/(auto|scroll)/.test(getComputedStyle(el).overflowY) && el.scrollHeight - el.clientHeight > 400` 的最大容器循环滚动。
   - **页内同源 API 分页拉取直链（推荐，直接拿 `play_url` 原片地址）**：在已打开抖音主页（`https://www.douyin.com/user/<sec_uid>`）的 `ego-browser` 页面内调用 `fetch("https://www.douyin.com/aweme/v1/web/aweme/post/?sec_user_id=<sec_uid>&max_cursor=<cursor>&count=20&aid=6383&device_platform=webapp", {credentials: "include"})`，循环 `max_cursor` 即可一次拿齐全部作品的 `aweme_id`、`desc`、点赞/评论/收藏数及 `video.play_addr.url_list[0]`；随后用 `curl -sL -H "Referer: https://www.douyin.com/" -H "User-Agent: Mozilla/5.0 ..." "<play_url>" -o video.mp4` 即可高速下载 `.mp4` 原片并交由本地 Whisper（`/Users/marovole/Library/Python/3.9/bin/whisper --model large-v3-turbo --language zh`）转写逐字稿。
3. **中国临床医生 SCI 论文精准归属检索（PubMed E-utilities + 百度学术交叉法）**：
   - 中文姓名拼音（如 `Li Yuze`）在 PubMed 常命中上百篇同名学者论文。先在百度学术按 `姓名 + 现就职医院` 查出中文核心/会议论文，提取其**硕博就读院系、导师姓名、早期就职医院及固定合著者**；
   - 再用 `efetch.fcgi?db=pubmed&retmode=xml` 批量拉取同名候选论文 XML，按 `AffiliationInfo`（早期单位/高校院系/现医院）与合著者网络过滤，即可 0 误差锁定本人 SCI 论文；
   - **Pitfall（PubMed XML 提取 DOI）**：解析 PubMed XML 时，必须只读取 `<MedlineCitation>/<Article>/<ELocationID EIdType="doi">` 或 `<PubmedData>/<ArticleIdList>/<ArticleId IdType="doi">`，切勿用 `.findall(".//ArticleId")` 遍历全树——因为 `<ReferenceList>` 下的参考文献也包含 `<ArticleId IdType="doi">`，全树遍历会用最后一篇参考文献的 DOI 覆盖正文 DOI。

### 策略详解

**策略 1：DDG `site:` 搜索摘要采集（通用 fallback）**

当平台全面封锁直接抓取时，DuckDuckGo 的 `site:domain.com` 搜索是获取一手用户内容的最可靠方式。DDG 索引了平台页面的标题和正文摘要（通常 200-300 字符），包含用户原话。

```python
from ddgs import DDGS
import time, json

# Reddit: 29个精准查询覆盖6个子版块，发现187个帖子
REDDIT_QUERIES = [
    'site:reddit.com r/Menopause "joint pain" OR "body pain" women',
    'site:reddit.com r/Menopause "hot flashes" OR "night sweats" severe',
    'site:reddit.com r/Menopause "brain fog" OR "memory" scared',
    'site:reddit.com r/Menopause "doctor" OR "dismissed" OR "gaslit"',
    'site:reddit.com r/AskWomenOver40 menopause OR perimenopause',
    # ... 按痛点维度展开 20-30 个查询
]

all_items = []
seen_urls = set()
for q in queries:
    with DDGS(verify=False) as d:
        results = list(d.text(q, max_results=10))
    for r in results:
        url = r.get("href", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        all_items.append({
            "query": q,
            "title": r.get("title", ""),
            "url": url,
            "snippet": r.get("body", ""),  # 200-300 chars of actual content
        })
    time.sleep(0.3)  # avoid rate limit
```

**关键要点：**
- DDG 摘要 `r["body"]` 通常包含帖子正文的前 200-300 字符，是用户原话
- 某些 Reddit 结果显示 "The site owner hides the web page description" — DDG 对部分 Reddit 页面无摘要
- `site:zhihu.com` 搜索发现 `zhuanlan.zhihu.com` 专栏文章 URL 后，可再用 Jina Reader 抓取全文
- 去重很重要：不同搜索查询会发现同一帖子/文章，用 URL 去重

**策略 2：知乎专栏文章全文抓取**

知乎的 `zhuanlan.zhihu.com` 专栏文章页面可以通过 Jina Reader 成功抓取全文（约 5000-6000 字符/篇）。但 `zhihu.com/question/` 页面抓取效果不稳定。

```python
# 先用 DDG 发现 zhuanlan 文章 URL
results = ddg_search('site:zhuanlan.zhihu.com 更年期 女性 身体变化')
# 再用 Jina 抓取全文
for r in results:
    content = jina_scrape(r["href"])  # ~6KB per article
```

实测：20 个搜索查询发现 159 个知乎页面，其中 29 个成功抓取全文（274KB 内容）。

**策略 3：Reddit 全文获取（需要登录态）**

Reddit 2024+ 全面封锁了匿名访问（Jina/curl/JSON API 全部 403）。获取 Reddit 帖子全文的唯一方式：
1. **Dokobot**（`dokobot read --local <reddit_url>`）— 用你登录的 Chrome 抓取
2. **Reddit API with OAuth** — 需要 `client_id` + `client_secret`，注册 Reddit app
3. **Pushshift API** — 第三方 Reddit 数据 API（可能不稳定）

### Pitfall：不要浪费时间尝试以下方法

| 方法 | 结果 | 时间浪费 |
|------|------|---------|
| `curl -H "User-Agent: ..." reddit.com/r/X.json` | 403 | ~2min |
| Jina Reader on `old.reddit.com` | 403 | ~1min |
| Jina Reader on `www.reddit.com/r/X` | 403 | ~1min |
| Jina Reader on Reddit thread URLs | 403 | ~5min (30 URLs) |
| Google Cache `webcache.googleusercontent.com` | 空响应 | ~1min |
| Web Archive `web.archive.org` via Jina | 451 blocked | ~1min |
| Reddit JSON API with browser User-Agent | 403 | ~3min |

**结论：** Reddit 全线封锁匿名程序化访问。直接用 DDG `site:reddit.com` 搜索摘要，或用 Dokobot 真实浏览器。

### 社区UGC抓取脚本模板

```python
# scrape_community.py — 多平台社区UGC抓取
# 用法: python3 scrape_community.py
# 输出: reddit_deep_scrape.md, zhihu_deep_scrape.md, quora_deep_scrape.md, xiaohongshu_deep_scrape.md
#
# 核心逻辑：
# 1. 每个平台 15-30 个 site: 搜索查询（按痛点维度展开）
# 2. DDG 搜索 → 收集 URL + 标题 + 摘要（去重）
# 3. 对可抓取的平台（知乎 zhuanlan）用 Jina 抓全文
# 4. 对封锁平台（Reddit/Quora/小红书）只保留 DDG 摘要
# 5. 输出 Markdown + 合并 JSON
#
# 预期产出（实测）：
# Reddit: ~187 帖子（75KB 摘要）
# 知乎: ~159 页面，~29 篇全文（274KB）
# Quora: ~15 Q&A（8KB 摘要）
# 小红书: ~143 条目（63KB 摘要）
# 总计: ~504 条目，~420KB Markdown + 477KB JSON
```

## 实践建议

1. **先用 Jina AI 快速验证**：不需要 API Key，直接在浏览器试 `r.jina.ai/https://xxx`
2. **建立模板库**：
   - 单页文章抓取模板（文章提取 schema）
   - 产品信息抓取模板（产品字段提取）
   - 搜索监控模板（SERP + 定时任务）
   - **大规模多维度研究抓取模板** → 见 `scripts/multi_dim_scrape.py`（参数化脚本，接受 `--config keywords.json --country china --dims 0,1,2,3` 分批执行）
   - **全量数据集交付契约** → 见 `references/bulk-dataset-export.md`（双格式配对、manifest、README、断点续跑）
   - **社区UGC抓取模板** → 见上方策略 1-3，按平台反爬状态表选择策略
3. **结合工作流**：
   - 竞品分析前：用 SERP 搜索 + 页面抓取获取对手信息
   - 内容营销前：用全站爬取整理行业报告素材
   - AI 训练前：用爬取工具准备高质采集数据
   - 用户研究：用 DDG `site:` 搜索采集社区UGC一手用户声音
4. **遵循准则**：
   - 检查 robots.txt，尊重网站爬取规则
   - 控制请求频率，避免对目标网站造成压力
   - 敏感数据加密存储，遵循数据保护法规