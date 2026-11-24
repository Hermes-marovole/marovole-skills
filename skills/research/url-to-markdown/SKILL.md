---
name: url-to-markdown
description: "Convert URLs, PDFs, or EPUB/DOCX to clean Markdown."
when_to_use: "看链接、读一下、总结网页、fetch、把URL/PDF/EPUB/DOCX转文字、doc2md"
category: research
tags: [fetch, markdown, url, pdf, conversion, reader, doc2md]
---

# URL 一键转 Markdown

## Goal

将用户提供的 URL 或文件路径转换为干净、可读的 Markdown 文本。自动根据来源类型选择最优提取方法，输出带标题、作者、来源的格式化内容。

## Success Criteria

- 提取的正文完整、无导航噪音
- 输出包含 Title、Author（如有）、Source、原始 URL
- Markdown 格式干净，可直接用于笔记或进一步处理
- 不丢失关键信息（图片 alt text 保留，表格保留）

## 路由表

根据 URL/来源类型自动选择提取方法：

| 来源类型 | 方法 | 说明 |
|---|---|---|
| **x.com / twitter.com** | Jina Reader (`r.jina.ai`) | 绕过登录墙，保留图片 URL |
| **微信公众号 (mp.weixin.qq.com)** | Jina Reader 优先；失败则 browser | 微信有反爬，Jina 最稳定 |
| **GitHub (github.com)** | 优先 raw content 或 `gh` CLI | 代码仓库内容直接获取 |
| **任何网页 URL** | web_extract / Jina Reader | 通用网页到 Markdown |
| **本地 PDF / EPUB / DOCX 批量转换** | `doc2md` CLI（优先 Gemini Flash 免费额度） | 详细命令、配额与模式见 `references/doc2md-cli.md` |
| **Publisher PDF endpoint redirects/blocks but public text is indexed** | Jina Reader on the PDF or article URL; save as clearly marked text-derived PDF/Markdown fallback | Example: `https://r.jina.ai/http://https://www.aafp.org/.../article.pdf` can extract public PDF/article text even when direct `requests` follows a redirect to HTML |
| **PMC PDF shows “Preparing to download” / PoW page** | Try Europe PMC `?pdf=render` endpoint | Example pattern: `https://europepmc.org/articles/PMCxxxxxxx?pdf=render` often redirects to `https://europepmc.org/api/getPdf?pmcid=PMCxxxxxxx` and returns a real PDF |
| **OpenAlex/Unpaywall says OA but no `pdf_url`** | Check PubMed/PMC/Europe PMC IDs and fullTextUrlList | OA landing pages may not expose PDF links; Europe PMC API can reveal renderable PDF URLs |

> 遇到以上未列出的来源类型，默认使用 Jina Reader (`https://r.jina.ai/<url>`)，它是最通用的纯文本提取方案。

## 输出格式

```
Title:  {页面标题}
Author: {作者名}（如有）
Source: {平台名称}
URL:    {原始 URL}

Content
{完整 Markdown 正文}
```

## 停止规则

- 提取内容超过 500 行时，先输出前 200 行，询问用户是否需要完整内容
- Jina Reader 失败时，自动降级到 browser_navigate + browser_snapshot
- 连续 2 个方法都失败时，报告失败并告知原因，不无限尝试

## Constraints

- 不修改原文内容（去广告/导航可以，改写不行）
- 保留原始 URL 作为来源引用
- PDF 文件过大（>50 页）时，先提取前 10 页，询问是否继续
- 默认只返回 Markdown，不保存文件（用户要求时再保存）

## 验证

- 提取后检查：输出开头是否有 Title/Author/Source 信息
- 正文第一段是否语义连贯（非导航菜单文本）
- 无残留的 HTML 标签或 CSS 样式文本
