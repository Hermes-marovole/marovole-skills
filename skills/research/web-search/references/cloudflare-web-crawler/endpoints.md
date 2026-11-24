# Cloudflare Browser Rendering — REST API 端点参考

> Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/`

## 认证

两种方式，任选其一：

**Global API Key（推荐，权限全）**
```
X-Auth-Email: user@example.com
X-Auth-Key: <global_api_key>
Content-Type: application/json
```

**API Token（最小权限）**
```
Authorization: Bearer ***
Content-Type: application/json
```

获取方式：Cloudflare Dashboard → My Profile → API Tokens

---

## 核心端点

### POST /markdown
将网页渲染后转换为 Markdown 文本。**最常用，效果最稳定。**

```json
{ "url": "https://example.com/page" }
```

响应：
```json
{ "success": true, "result": "# 页面标题\n\n正文内容..." }
```

注意：返回内容包含完整页面（含导航菜单）。正文通常从第 20+ 行的 `# 标题` 开始。

---

### POST /links
提取页面所有链接（渲染后）。**全站爬取第一步。**

```json
{ "url": "https://example.com" }
```

响应：
```json
{ "success": true, "result": ["https://example.com/page1", "https://example.com/page2", ...] }
```

返回的是渲染后页面中所有 `<a href>` 的 href 值，含站内和站外链接，需自行过滤同域名页面。

---

### POST /content
获取渲染后的完整 HTML 源码。

```json
{ "url": "https://example.com" }
```

响应：
```json
{ "success": true, "result": "<html>...</html>" }
```

---

### POST /screenshot
截取页面截图，返回 base64 编码的 PNG。

```json
{
  "url": "https://example.com",
  "screenshotOptions": { "fullPage": true, "type": "png" },
  "viewport": { "width": 1280, "height": 800 }
}
```

响应：
```json
{ "success": true, "result": "data:image/png;base64,iVBOR..." }
```

---

### POST /pdf
将页面渲染为 PDF，返回 base64 编码。

```json
{
  "url": "https://example.com",
  "pdfOptions": { "format": "A4", "printBackground": true }
}
```

响应：
```json
{ "success": true, "result": "JVBERi0x..." }
```

---

### POST /scrape
按 CSS 选择器提取指定元素。适合精准抓取结构化数据。

```json
{
  "url": "https://example.com",
  "elements": [
    { "selector": "h1" },
    { "selector": ".product-price" },
    { "selector": "table.data-table" }
  ]
}
```

响应：
```json
{
  "success": true,
  "result": [
    { "selector": "h1", "results": [{ "text": "页面标题", "attributes": {} }] }
  ]
}
```

---

### POST /json
AI 驱动的结构化数据提取（消耗更多算力）。

```json
{
  "url": "https://example.com/product",
  "prompt": "Extract: product name, price, description, specifications"
}
```

响应：
```json
{
  "success": true,
  "result": { "product_name": "...", "price": "...", "description": "..." }
}
```

---

### POST /crawl ⚠️ 异步，Free 计划不稳定
异步全站爬取，返回 crawlId，需轮询状态。

**已知问题**：Free 计划下 `/crawl/status/{id}` 状态查询不稳定，容易返回空结果。**推荐替代方案：`/links` + `/markdown` 组合**。

```json
{
  "url": "https://example.com",
  "limit": 10
}
```

启动响应：
```json
{ "success": true, "result": { "id": "crawl_abc123" } }
```

状态查询（GET）：
```
GET /crawl/{crawlId}/status
```

---

## 速率限制

| 计划 | 限制 | 建议间隔 |
|------|------|---------|
| Free | ~1 req/10s（实测约 1-2s 可过，但偶发 429） | 2s |
| Workers Paid | 更高（具体见官方文档） | 0.5s |

**429 错误处理**：收到 429 后等待 10s 再重试，最多 3 次（10s / 20s / 30s 指数退避）。

**524 错误**：Cloudflare 超时（页面加载超 100s），通常是目标站点响应慢，可重试。

---

## 通用请求选项

所有端点均支持以下可选参数（在请求 body 中）：

```json
{
  "url": "https://example.com",
  "waitForSelector": ".main-content",
  "waitUntil": "networkidle0",
  "timeout": 30000,
  "cookies": [{ "name": "session", "value": "xxx", "domain": "example.com" }],
  "headers": { "Accept-Language": "zh-CN" },
  "userAgent": "Mozilla/5.0 ..."
}
```
