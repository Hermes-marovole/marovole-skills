#!/usr/bin/env python3
"""number_audit.py — 把帧里读到的每个数字，回原文批量找出处与上下文。

用法:
    python3 number_audit.py paper.html 47.2 49.0 "1.04" "4.4"
    python3 number_audit.py paper.html --window 120 "10 22"   # 查剥标签后被打散的上标
    cat frame_numbers.txt | python3 number_audit.py paper.html -   # 从 stdin 读待查串，一行一个

原文可以是 HTML（arXiv / alphaxiv / docs 页）、markdown 或纯文本。HTML 会先剥
script/style 与标签、反转义实体、压平空白，所以 LaTeX 里的 `10^{22}` 会变成 `10 22`，
`\\times` 会变成 `×`——查询里带空格时脚本按「空白任意」匹配。

判读（三条，别只看条数）:
  * 命中 0 次  -> 这个数来自别处，或量级写错了（最先怀疑后者）
  * 命中多次   -> 要挑对是哪一节的表，摘要里的同一个数常常不是图表里的那个数
  * 命中但措辞不符 -> 改写失真（原文 approximately three times，画面画 4.4x），不算数据错误

退出码: 0 = 全部命中; 1 = 有未命中（未命中本身就是结论）。
"""

import argparse
import html
import re
import sys


def load(path: str) -> str:
    raw = open(path, encoding="utf-8", errors="ignore").read()
    if "<" in raw and ">" in raw:
        raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw)


def pattern_for(query: str, loose: bool) -> str:
    parts = [re.escape(tok) for tok in query.split()]
    body = r"\s*".join(parts)
    if loose:
        return body
    # 默认挡住数字内部的误命中: "4.4" 不应命中 "44.4"
    return rf"(?<![\d.]){body}(?![\d])"


def main() -> int:
    ap = argparse.ArgumentParser(description="把帧里读到的数字回原文对账")
    ap.add_argument("source", help="原文文件（HTML / md / txt）")
    ap.add_argument("queries", nargs="*", help="待查的数字；单个 '-' 表示从 stdin 逐行读")
    ap.add_argument("--window", type=int, default=90, help="上下文宽度（字符，前后各一半）")
    ap.add_argument("--max-hits", type=int, default=3, help="每个查询最多打印几处上下文")
    ap.add_argument("--loose", action="store_true", help="关掉数字边界保护（查子串时用）")
    args = ap.parse_args()

    queries = args.queries
    if queries == ["-"]:
        queries = [line.strip() for line in sys.stdin if line.strip()]
    if not queries:
        ap.error("至少给一个待查数字")

    text = load(args.source)
    print(f"# source={args.source} chars={len(text)} queries={len(queries)}", file=sys.stderr)

    missing = []
    for query in queries:
        hits = [m.start() for m in re.finditer(pattern_for(query, args.loose), text, re.IGNORECASE)]
        print(f"=== {query!r} : {len(hits)} hit(s)")
        if not hits:
            missing.append(query)
            continue
        for pos in hits[: args.max_hits]:
            lo = max(0, pos - args.window)
            hi = min(len(text), pos + args.window)
            print(f"  [{pos}] …{text[lo:hi]}…")
        if len(hits) > args.max_hits:
            print(f"  (+{len(hits) - args.max_hits} more not shown)")

    if missing:
        print(
            f"\nUNMATCHED ({len(missing)}): {missing}"
            "  -> 优先怀疑量级写错或数字取自别处，回画面改数，不要改报告",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
