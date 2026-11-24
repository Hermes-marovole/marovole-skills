#!/usr/bin/env python3
"""
cf_crawl.py — Cloudflare Browser Rendering 全站爬取工具

两阶段策略：/links 发现页面 → /markdown 逐页提取
Free 计划速率限制：~1 req/10s，含 429 指数退避重试
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import time
import sys
import argparse
from datetime import datetime

# ─── 认证 & CLI ──────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="使用 Cloudflare Browser Rendering 爬取网站并输出 Markdown"
    )
    p.add_argument("--url",        required=True,  help="起始页 URL（如 https://example.com）")
    p.add_argument("--account-id", required=True,  help="Cloudflare Account ID")
    p.add_argument("--email",      required=True,  help="Cloudflare 账号邮箱（Global API Key 认证）")
    p.add_argument("--api-key",    required=True,  help="Cloudflare Global API Key")
    p.add_argument("--output",     default=None,   help="输出文件路径（默认输出到 stdout）")
    p.add_argument("--limit",      type=int, default=0, help="最多爬取页面数（0=不限）")
    p.add_argument("--delay",      type=float, default=2.0, help="每次请求间隔秒数（默认 2s）")
    p.add_argument("--max-chars",  type=int, default=8000, help="每页最多保留字符数（默认 8000）")
    p.add_argument("--mode",       choices=["crawl", "single", "links"], default="crawl",
                   help="crawl=全站爬取(默认) | single=单页 | links=只列链接")
    return p.parse_args()


def make_headers(email: str, api_key: str) -> dict:
    return {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json",
    }


# ─── HTTP 工具 ────────────────────────────────────────────────────────────────

def cf_post(endpoint: str, payload: dict, account_id: str, headers: dict,
            retries: int = 3, base_delay: float = 10.0) -> dict:
    """带 429 指数退避重试的 Cloudflare API 调用"""
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        f"/browser-rendering/{endpoint}"
    )
    data = json.dumps(payload).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = base_delay * (attempt + 1)
                print(f"  ⏳ 429 限流，{wait:.0f}s 后重试 (attempt {attempt+1}/{retries})...",
                      file=sys.stderr)
                time.sleep(wait)
            elif e.code == 524:                 # Cloudflare timeout
                wait = 5 * (attempt + 1)
                print(f"  ⏳ 524 超时，{wait:.0f}s 后重试...", file=sys.stderr)
                time.sleep(wait)
            else:
                body = e.read().decode(errors="replace")[:200]
                return {"success": False, "error": f"HTTP {e.code}: {body}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": f"超过最大重试次数 ({retries})"}


# ─── 链接发现 ─────────────────────────────────────────────────────────────────

def discover_links(start_url: str, account_id: str, headers: dict) -> list[str]:
    """调用 /links 端点，返回同域名过滤后的页面链接列表"""
    print(f"🔗 发现链接: {start_url}", file=sys.stderr)
    res = cf_post("links", {"url": start_url}, account_id, headers)
    if not res.get("success"):
        print(f"  ❌ /links 失败: {res.get('error', res.get('errors', '?'))}", file=sys.stderr)
        return [start_url]

    raw_links: list = res.get("result", [])
    domain = urllib.parse.urlparse(start_url).netloc
    SKIP_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".zip", ".mp4", ".webp"}

    filtered = list(set(
        link for link in raw_links
        if isinstance(link, str)
        and urllib.parse.urlparse(link).netloc == domain
        and not any(link.lower().endswith(ext) for ext in SKIP_EXT)
        and not link.startswith("mailto:")
    ))

    # 确保起始页在列表中
    if start_url not in filtered:
        filtered.insert(0, start_url)

    print(f"  ✅ 发现 {len(filtered)} 个页面", file=sys.stderr)
    return sorted(filtered)


# ─── 单页抓取 ─────────────────────────────────────────────────────────────────

def fetch_markdown(page_url: str, account_id: str, headers: dict,
                   max_chars: int = 8000) -> str:
    """调用 /markdown 端点，自动剥离顶部导航菜单"""
    res = cf_post("markdown", {"url": page_url}, account_id, headers)
    if not res.get("success"):
        err = res.get("error", res.get("errors", "unknown"))
        return f"*抓取失败: {err}*"

    md = res.get("result", "")

    # 跳过导航区域：寻找第 20 行后的第一个 # 标题
    lines = md.split("\n")
    start = 0
    for j, line in enumerate(lines):
        if line.startswith("# ") and j > 20:
            start = j
            break

    content = "\n".join(lines[start:]) if start else md
    return content[:max_chars]


# ─── 输出格式化 ───────────────────────────────────────────────────────────────

def build_output(start_url: str, results: dict) -> str:
    domain = urllib.parse.urlparse(start_url).netloc
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    output = f"# {domain} — 完整网站内容\n\n"
    output += f"> **爬取时间**: {ts}  \n"
    output += f"> **起始 URL**: {start_url}  \n"
    output += f"> **页面总数**: {len(results)}  \n"
    output += f"> **工具**: Cloudflare Browser Rendering `/links` + `/markdown`\n\n"
    output += "---\n\n"

    for url, content in sorted(results.items()):
        slug = url.replace(f"https://{domain}/", "").replace(f"http://{domain}/", "").strip("/") or "home"
        output += f"## 📄 {slug}\n\n"
        output += f"> 来源: {url}\n\n"
        output += content.strip()
        output += "\n\n---\n\n"

    return output


# ─── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    headers = make_headers(args.email, args.api_key)

    # ── 单页模式 ──
    if args.mode == "single":
        print(f"📄 单页抓取: {args.url}", file=sys.stderr)
        content = fetch_markdown(args.url, args.account_id, headers, args.max_chars)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 已写入 {args.output}", file=sys.stderr)
        else:
            print(content)
        return

    # ── 链接发现模式 ──
    links = discover_links(args.url, args.account_id, headers)

    if args.mode == "links":
        for link in links:
            print(link)
        return

    # ── 全站爬取模式 ──
    pages = links[:args.limit] if args.limit > 0 else links
    print(f"🕷️  开始爬取 {len(pages)} 个页面 (delay={args.delay}s)...", file=sys.stderr)

    results = {}
    for i, page_url in enumerate(pages):
        print(f"  [{i+1}/{len(pages)}] {page_url}", file=sys.stderr)
        results[page_url] = fetch_markdown(page_url, args.account_id, headers, args.max_chars)
        if i < len(pages) - 1:
            time.sleep(args.delay)

    success_count = sum(1 for v in results.values() if not v.startswith("*抓取失败"))
    print(f"\n✅ 完成: {success_count}/{len(pages)} 页成功", file=sys.stderr)

    output = build_output(args.url, results)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"📝 已写入 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
