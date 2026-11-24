# X2Doc Image Extraction Techniques

Trigger: the post's image carries the real payload — data dashboard, backend table, chart, ranking. The body text is usually just a caption.

## Problem: Tweet contains data-rich image (chart/ranking)

When a tweet embeds an image with tables, charts, or benchmark rankings, the text extraction (Jina/browser) captures the alt text or image link but not the actual data. You must extract and transcribe the image.

## Routes

### Route 1: Direct vision_analyze with HTTP URL
Try first:
```
vision_analyze image_url="https://pbs.twimg.com/media/XXXX.jpg"
```
Pitfall: may fail with `Invalid image source` on some HTTPS URLs.

### Route 2: Download locally then vision_analyze (reliable fallback)
```bash
curl -sL "https://pbs.twimg.com/media/XXXX.jpg?format=jpg&name=large" -o /tmp/x-img.jpg
```
Then:
```
vision_analyze image_url="/tmp/x-img.jpg" question="Transcribe all text, tables, charts..."
```
Use `?format=jpg&name=large` for highest resolution.

### Route 3: 本地 macOS Vision OCR（数字密集截图的默认路线）

后台截图、数据大屏、表格这类**以数字和标签为主**的图，本地 OCR 比视觉模型更可靠：逐字输出、带坐标、不会把 19,247 读成 19,247 万。脚本在 `scripts/ocr.swift`：

```bash
cd <skill_dir> && swiftc -O scripts/ocr.swift -o /tmp/ocrbin && /tmp/ocrbin /tmp/x-img.jpg
# 每行输出 "y\tx\ttext"，已按从左到右、从上到下排序
```

- 中文默认 `zh-Hans,en-US`，第二参数可覆盖：`/tmp/ocrbin img.jpg zh-Hans,en-US,ja-JP`
- **坐标就是版式信息**：同一 `y` 的一组文本是同一行（卡片标题、指标名），把 `x` 接近的列对齐就能还原「平台 → 播放 → 粉丝」这种表格，别按输出顺序硬读
- 只用来取字；「这是什么界面、这个人在证明什么」仍交给 `vision_analyze` 或人判断
- `swiftc` 不可用时先 `xcode-select --install`，或退回 Route 1/2

### Route 4: Browser snapshot

If neither vision nor OCR is available, open the tweet in the browser and read the image area — least reliable for dense data, use only to confirm layout.

## When to stop

- All visible text in the image has been transcribed
- Rankings/tables are captured in structured markdown
- No fabricated numbers or model names were added

## Related

- x2doc SKILL.md "Stop searching when" includes: "images containing data, charts, or rankings are captured and transcribed"
