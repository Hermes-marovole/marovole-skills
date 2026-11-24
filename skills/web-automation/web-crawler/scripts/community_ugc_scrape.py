#!/usr/bin/env python3
"""Community UGC deep scraper for walled-garden platforms.

Scrapes Reddit, Zhihu, Quora, Xiaohongshu using DDG site: search
to discover threads + Jina Reader for content extraction where accessible.

Usage:
    python3 community_ugc_scrape.py --platform all
    python3 community_ugc_scrape.py --platform reddit
    python3 community_ugc_scrape.py --platform zhihu --max-results 15

Output:
    {outdir}/reddit_deep_scrape.md
    {outdir}/zhihu_deep_scrape.md
    {outdir}/quora_deep_scrape.md
    {outdir}/xiaohongshu_deep_scrape.md
    {outdir}/all_community_ugc.json

Tested 2026-06: Reddit/Quora block all anonymous access (403/CAPTCHA).
Zhihu zhuanlan articles accessible via Jina. 小红书 blocks scraping.
DDG site: search snippets (200-300 chars) are the reliable fallback for all platforms.
"""
import argparse, time, os, re, json, requests
from ddgs import DDGS

def ddg_search(query, max_results=10):
    try:
        with DDGS(verify=False) as d:
            return list(d.text(query, max_results=max_results))
    except Exception as e:
        print(f"  [!] Search error: {e}")
        return []

def jina_scrape(url, timeout=20, cap=8000):
    try:
        r = requests.get(f"https://r.jina.ai/{url}", timeout=timeout)
        if r.status_code == 200 and len(r.text) > 200:
            blocked = any(x in r.text[:500] for x in
                          ["403", "Forbidden", "blocked by", "CAPTCHA", "security verification"])
            if blocked:
                return None
            return r.text[:cap]
        return None
    except:
        return None

def save_md(filename, header, items):
    md = header
    for item in items:
        md += f"### {item['title']}\n"
        md += f"**URL:** {item['url']}\n"
        md += f"**Query:** `{item.get('query','')[:80]}`\n"
        md += f"**Snippet:** {item.get('snippet','')}\n\n"
        if item.get("full_content"):
            md += f"**Full Content:**\n{item['full_content'][:6000]}\n\n"
        md += "---\n\n"
    with open(filename, "w") as f:
        f.write(md)
    print(f"  Saved: {filename} ({len(md)} bytes)")

# --- Query templates by platform ---
# Customize these for your research topic. The pattern is:
#   site:<platform-domain> <topic keywords> "quoted phrases" OR "alternative phrases"
#
# Key principles:
# 1. Use site: operator to restrict to one platform
# 2. Use OR + quoted phrases to match user's actual language
# 3. Cover all pain dimensions (health, career, family, financial, emotional, etc.)
# 4. Run 15-30 queries per platform for comprehensive coverage
# 5. DDG returns 200-300 char snippets containing actual user content

REDDIT_QUERIES = [
    # r/Menopause — physical symptoms
    'site:reddit.com r/Menopause "joint pain" OR "body pain" OR "muscle pain" women',
    'site:reddit.com r/Menopause "hot flashes" OR "night sweats" OR "vasomotor" severe',
    'site:reddit.com r/Menopause "sleep" OR "insomnia" OR "can\'t sleep" suffering',
    'site:reddit.com r/Menopause "weight gain" OR "belly fat" OR "can\'t lose weight"',
    'site:reddit.com r/Menopause "brain fog" OR "memory" OR "can\'t concentrate" scared',
    'site:reddit.com r/Menopause "anxiety" OR "depression" OR "crying" OR "mood swings"',
    'site:reddit.com r/Menopause "doctor" OR "dismissed" OR "not taken seriously" OR "gaslit"',
    'site:reddit.com r/Menopause "HRT" OR "hormone" OR "treatment" struggle access',
    'site:reddit.com r/Menopause "work" OR "career" OR "job" OR "can\'t work" menopause',
    'site:reddit.com r/Menopause "relationship" OR "marriage" OR "husband" OR "divorce"',
    # r/AskWomenOver40
    'site:reddit.com r/AskWomenOver40 menopause OR perimenopause symptoms',
    'site:reddit.com r/AskWomenOver40 "over 40" health OR body OR aging changes',
    'site:reddit.com r/AskWomenOver40 "over 40" career OR workplace OR discrimination',
    'site:reddit.com r/AskWomenOver40 "over 40" lonely OR invisible OR struggling',
    # r/Perimenopause
    'site:reddit.com r/Perimenopause symptoms OR suffering OR "falling apart"',
    # Add more queries for your specific topic...
]

ZHIHU_QUERIES = [
    'site:zhihu.com 更年期 症状 痛苦 经历',
    'site:zhuanlan.zhihu.com 更年期 女性 身体变化',
    'site:zhihu.com 中年女性 健康问题 困扰',
    'site:zhuanlan.zhihu.com 中年女性 焦虑 抑郁 心理',
    'site:zhihu.com 45岁 女性 身体 疼痛 不适',
    'site:zhihu.com 围绝经期 潮热 失眠 骨质疏松',
    'site:zhuanlan.zhihu.com 更年期 骨骼 关节 疼痛',
    'site:zhihu.com 中年女性 职场 歧视 困境',
    'site:zhihu.com 中年女性 婆媳 家庭 矛盾 压力',
    'site:zhihu.com 中年女性 养老 经济 焦虑 退休',
    # Add more queries for your specific topic...
]

QUORA_QUERIES = [
    'site:quora.com women 40-60 menopause symptoms pain',
    'site:quora.com perimenopause women "joint pain" OR "body pain"',
    'site:quora.com menopause "weight gain" women struggle',
    'site:quora.com menopause "brain fog" OR "memory loss" women',
    'site:quora.com menopause "depression" OR "anxiety" women midlife',
    'site:quora.com women over 40 health problems aging body',
    # Add more queries for your specific topic...
]

XIAOHONGSHU_QUERIES = [
    '小红书 更年期 症状 痛苦',
    '小红书 中年女性 身体变化 焦虑',
    '小红书 围绝经期 潮热 失眠',
    '小红书 45岁 女性 疼痛 关节',
    '小红书 中年女性 容貌焦虑 抗衰',
    '小红书 更年期 情绪 崩溃 哭',
    # Add more queries for your specific topic...
]

PLATFORMS = {
    "reddit": (REDDIT_QUERIES, "reddit_deep_scrape.md"),
    "zhihu": (ZHIHU_QUERIES, "zhihu_deep_scrape.md"),
    "quora": (QUORA_QUERIES, "quora_deep_scrape.md"),
    "xiaohongshu": (XIAOHONGSHU_QUERIES, "xiaohongshu_deep_scrape.md"),
}

def run_platform(name, queries, outpath, max_results=10, try_scrape=True):
    """Run DDG site: search + optional Jina scrape for one platform."""
    all_items = []
    seen_urls = set()

    for i, q in enumerate(queries):
        print(f"  [{i+1}/{len(queries)}] {q[:70]}...")
        results = ddg_search(q, max_results=max_results)
        time.sleep(0.3)
        for r in results:
            url = r.get("href", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            all_items.append({
                "query": q,
                "title": r.get("title", ""),
                "url": url,
                "snippet": r.get("body", ""),
            })

    # Try Jina scrape (works for zhihu zhuanlan, fails for reddit/quora/xhs)
    if try_scrape:
        scrape_limit = min(40, len(all_items))
        scraped = 0
        for item in all_items[:scrape_limit]:
            content = jina_scrape(item["url"])
            if content and len(content) > 300:
                item["full_content"] = content
                scraped += 1
            time.sleep(0.2)
        print(f"  Scraped {scraped}/{scrape_limit} pages via Jina")

    header = f"# {name} Deep Scrape\n> Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} UTC\n"
    header += f"> Queries: {len(queries)} | Items found: {len(all_items)}\n\n## Items\n\n"
    save_md(outpath, header, all_items)
    return all_items


def main():
    ap = argparse.ArgumentParser(description="Community UGC deep scraper")
    ap.add_argument("--platform", default="all", choices=["all"] + list(PLATFORMS.keys()))
    ap.add_argument("--outdir", default=".", help="Output directory")
    ap.add_argument("--max-results", type=int, default=10, help="Max DDG results per query")
    ap.add_argument("--no-scrape", action="store_true", help="Skip Jina scrape attempts")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    targets = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]
    combined = {}

    for plat in targets:
        queries, filename = PLATFORMS[plat]
        outpath = os.path.join(args.outdir, filename)
        print(f"\n=== {plat.upper()} ===")
        items = run_platform(plat, queries, outpath,
                             max_results=args.max_results,
                             try_scrape=not args.no_scrape)
        combined[plat] = items
        print(f"  {plat}: {len(items)} items")

    # Save combined JSON
    json_path = os.path.join(args.outdir, "all_community_ugc.json")
    with open(json_path, "w") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\n=== SUMMARY ===")
    total = sum(len(v) for v in combined.values())
    for plat, items in combined.items():
        scraped = sum(1 for i in items if i.get("full_content"))
        print(f"  {plat:15s}: {len(items):4d} items ({scraped} full scrapes)")
    print(f"  {'TOTAL':15s}: {total:4d} items")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()