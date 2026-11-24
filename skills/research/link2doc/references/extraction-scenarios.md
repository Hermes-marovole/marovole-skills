# 内容提取场景完全指南

## X/Twitter Article（长文/长帖）

X 的长文功能有特殊处理方式：

1. **识别 Article**：URL 格式为 `/article/xxxx` 或推文中有 "Focus mode" 链接
2. **首选方案：Jina Reader** — 绕过登录墙和 404
   ```bash
   curl -sL "https://r.jina.ai/http://x.com/{user}/status/{status_id}"
   ```
3. **备选：浏览器方案** — Jina Reader 失效时使用
   ```
   browser_navigate → browser_snapshot(full=true) → browser_scroll(down) 加载更多
   ```

## X/Twitter Quote Chains（引用链）

Quote Chain = 帖子 A 引用帖子 B，B 又引用 C，形成多层内容。

**处理**：逐层 browser_click 引用链接 → browser_snapshot 提取 → 递归直到无更多引用。通常 3-8 层。超时时用 Content-First Fallback。

## GitHub 仓库内容获取

GitHub 有严格反爬限制，**最可靠方案是直接下载 raw 文件**：

```bash
# 获取 README
curl -sL "https://raw.githubusercontent.com/{user}/{repo}/main/README.md"

# 获取子目录文件
curl -sL "https://raw.githubusercontent.com/{user}/{repo}/main/{path}"

# 获取特定语言版本
curl -sL "https://raw.githubusercontent.com/{user}/{repo}/main/README_zh.md"
```

**不推荐**：Jina Reader 提取 github.com 页面 → 返回导航结构而非内容。

### GitHub 仓库元数据提取

访问仓库主页获取统计信息：

```python
browser_navigate(url="https://github.com/{user}/{repo}")
browser_snapshot(full=true)

# 提取字段：
# - Stars, Forks, Watchers
# - Issues, Pull Requests
# - Commits 数量和最近更新日期
# - License 类型
# - Description
```

**必记字段**：
| 字段 | 位置 | 用途 |
|------|------|------|
| Stars | 页面顶部 | 社区关注度 |
| Forks | 页面顶部 | 代码复用度 |
| Issues | 导航栏 | 项目健康度 |
| Pull Requests | 导航栏 | 社区贡献活跃度 |
| Commits | 文件列表区域 | 开发活跃度 |
| Last update | 文件列表区域 | 维护状态 |
| License | 页面中部 | 使用权限 |
| Description | 页面顶部 | 项目简介 |

**404/403 处理：**
- 404: 记录为"已下架"，尝试搜索镜像/替代
- 403: 可能变为私有，记录并告知用户无法访问
- 200: 正常 clone 分析

## Showcase/Demo 帖子

作者展示自己做的东西（非教程）。信息量小但示范价值高。

**策略**：深度补充调研
1. 提取核心工具/项目名称
2. 搜索项目官网获取详细信息
3. 调研作者的其他项目 → 构建「工具矩阵」
4. 输出 → 案例研究报告

## X/Twitter 工具推荐帖

作者分享第三方工具的帖子（如 AI 工具、开源项目）。典型结构：痛点描述 → 工具介绍 → 核心功能 → 资源链接。

**提取策略**：
```python
# Step 1: 访问 X 帖子获取完整内容
browser_navigate(url="https://x.com/{user}/status/{id}")
browser_snapshot(full=true)

# Step 2: 提取关键字段
# - 帖子正文（工具名称、核心卖点、适用场景）
# - 作者信息（@handle, bio）
# - 互动数据（likes, reposts, bookmarks, views）
# - 链接列表（GitHub、官网、社区）
```

**必提取字段**：
| 字段 | 位置 | 示例 |
|------|------|------|
| 工具名称 | 帖子正文 | "Voquill" |
| 核心功能 | 正文或截图 | "语音转文字，比打字快4倍" |
| GitHub 链接 | 推文中的短链接 | github.com/voquill/voquill |
| 官网链接 | 推文中的短链接 | voquill.com |
| 社区链接 | 推文或评论 | Discord, Slack |
| 作者身份 | @handle bio | "AI 程序员，分享高质量工具" |
| 互动数据 | 帖子底部 | "216 likes, 249 bookmarks" |

**后续深度调研**：
1. 访问 GitHub 获取仓库元数据（stars, forks, commits, license, update date）
2. 访问官网获取功能详情、定价、下载量
3. 整合构建完整工具文档

## 工具官网内容提取

访问项目官网获取功能、定价、下载信息：

```python
browser_navigate(url="https://{domain}.com")
browser_snapshot(full=true)

# 通常包含：
# - Hero 区域：一句话描述和 CTA
# - Features 区域：功能列表
# - Pricing 区域：定价方案
# - Download 区域：安装包链接
# - FAQ 区域：常见问题
```

**必记字段**：
| 字段 | 位置 | 示例 |
|------|------|------|
| Tagline | Hero 区域 | "Your keyboard is holding you back" |
| 核心功能 | Features 区域 | 列表或卡片形式 |
| 支持平台 | Download 区域 | macOS/Windows/Linux/iOS |
| 定价方案 | Pricing 区域 | 免费/付费/企业定制 |
| 下载量 | 页面统计 | "60K+ downloads" |
| 社区链接 | Footer/Contact | Discord, GitHub, X |

## Technical Observation 帖子

作者分享对技术的观察和判断（非展示自己作品）。1-2 句话但包含多个技术概念。

**策略**：并行深度调研
1. 解析帖子中所有技术术语
2. 并行搜索所有概念（不要串行！）
3. Jina Reader 提取关键页面
4. 输出 → 深度分析报告（单篇 10,000+ 字）
5. 结构：执行摘要 → 概念解析 → 协同分析 → 应用场景 → 风险

## 评论区内容获取（登录受阻时）

X 帖子常采用「主贴引流 + 评论区放干货」模式。遇到登录墙时：

1. 提取帖子核心主题词
2. 搜索引擎找第三方镜像站点（提示词库、技术社区、AI 工具导航站）
3. 访问镜像获取完整内容
4. 验证镜像完整性

搜索关键词组合：`{主题} + prompt`、`{主题} + 提示词`、`{作者} + {关键词} + prompt`

## Publisher Insight 提取

发布者的个人体验比工具功能描述更有价值：

| 维度 | 示例 |
|---|---|
| 个人体验 | "用了三个月" |
| 核心优势 | "手动 2 小时 → 现在 5 分钟" |
| 推荐理由 | "线程互动率提升 40%" |
| 直接引用 | 完整原话，保留发布者语气 |

## Content-First Fallback

当子代理超时、GitHub 被拦截或浏览器受限时：

直接使用 X 帖子中已有的描述构建文档：
- 从快照提取：项目名称、描述文本、作者、核心优势
- X 聚合帖的描述已提炼核心亮点，足够构建高质量文档
- GitHub 链接保留原始 URL（即使未访问）
