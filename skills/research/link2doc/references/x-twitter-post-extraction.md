# X/Twitter 普通帖子 / 聚合帖提取

## 首选方案：Jina Reader

Jina Reader (`https://r.jina.ai/http://x.com/{user}/status/{id}`) 是目前提取 X/Twitter 帖子最可靠的方式，无需浏览器 daemon，能绕过登录墙和大部分反爬限制。

```bash
curl -sL "https://r.jina.ai/http://x.com/vikingmute/status/2061979261637181775"
```

**输出内容**：
- 帖子完整正文（含短链接解析后的真实 URL）
- 作者信息（@handle、bio）
- 互动数据（likes、reposts、bookmarks、views）
- 图片链接（pbs.twimg.com）
- 引用/回复中的子帖子链接

**什么时候用 Jina Reader 失败**？
- 帖子被删除或账号被限制
- 极少数情况下 X 对 Jina 返回空内容
- 这时候 fallback 到 browser_navigate

## 备选方案：browser_navigate

```python
browser_navigate(url="https://x.com/{user}/status/{id}")
browser_snapshot(full=true)
```

要求 agent-browser daemon 已启动（`AGENT_BROWSER_HOME` 环境变量正确设置）。如果 daemon 未启动，直接回退到 Jina Reader，不要浪费时间尝试修复 daemon。

## 聚合帖链接提取流程

1. **Jina Reader 提取帖子正文**
2. **从正文中提取所有外部链接**（t.co 短链已被 Jina 解析为真实 URL）
3. **判断帖子类型**：
   - 有外部子链接 → 进入 delegate_task 并行研究（Step 3）
   - 无外部链接（纯文本推荐清单）→ 场景 A-0（自包含帖）处理

## 单篇文章深度整理变体

当用户提供的是 1 个长篇文章链接（非聚合帖）时：

1. 用 Jina Reader 提取完整文章内容
2. 识别文章中引用的所有外部资源/工具/API
3. 对关键资源做并行深度调研（delegate_task + terminal）
4. 输出结构：文章摘要 → 核心系统拆解 → 工具链汇总 → 可复制检查清单

示例产出：
- yage.ai AI 托管增长复盘 → 528 行文档，含 5 大系统详解、R/T/N 框架、UTM 模板、复制检查清单
