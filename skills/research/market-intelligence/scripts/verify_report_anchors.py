#!/usr/bin/env python3
"""报告交付前的机械闭合校验：正文引用标记 <-> HTML 锚点 <-> 图片路径 <-> 占位残留。

用法：
    python3 verify_report_anchors.py <report.md|report.html> [more files...]
    python3 verify_report_anchors.py --base <dir> report.html     # 解析相对图片路径的基准目录

支持两种引用形态：数字 [1][2]（配 id="ref-1"）与 [E1][E2]（配 id="ref-E1"）。
任一断言失败即 exit 1；这类错误（漏锚点、引了台账里没有的号、图片 404、{{占位}} 残留）
肉眼扫几百个标记扫不出来，脚本秒级给结论。
"""

import argparse
import os
import re
import sys

CITE_RE = re.compile(r"\[((?:E)?\d{1,3})\]")
ANCHOR_RE = re.compile(r"id=\"ref-((?:E)?\d{1,3})\"|id='ref-((?:E)?\d{1,3})'")
IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]{0,80}\}\}")


def _anchors(text: str) -> list:
    """取 id=\"ref-N\" / id='ref-N' 两种引号下的编号。"""
    out = []
    for m in ANCHOR_RE.finditer(text):
        out.append(m.group(1) or m.group(2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--base", default=None, help="相对图片路径的基准目录（默认取报告文件所在目录）")
    args = ap.parse_args()

    failures = []

    for path in args.files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()

        cites = sorted(set(CITE_RE.findall(text)), key=_sort_key)
        anchors = sorted(set(_anchors(text)), key=_sort_key)

        # 只在 HTML 里做锚点闭合断言；Markdown 没有锚点，单独看引用数
        if path.endswith((".html", ".htm")):
            dangling = [c for c in cites if c not in anchors]
            orphan = [a for a in anchors if a not in cites]
            if dangling:
                failures.append(f"{path}: 正文引用了台账里没有的号 -> {dangling}")
            if orphan:
                failures.append(f"{path}: 台账有号但正文没引（孤儿锚点）-> {orphan}")

        base = args.base or os.path.dirname(os.path.abspath(path))
        missing = []
        for src in IMG_RE.findall(text):
            if src.startswith(("http://", "https://", "data:")):
                continue
            if not os.path.exists(os.path.join(base, src)):
                missing.append(src)
        if missing:
            failures.append(f"{path}: 图片路径不存在 -> {missing}")

        residue = PLACEHOLDER_RE.findall(text)
        if residue:
            failures.append(f"{path}: 占位符残留 -> {residue[:5]}")

        print(f"{path}: cites={len(cites)} anchors={len(anchors)} imgs={len(IMG_RE.findall(text))}")

    if failures:
        print("\nFAIL")
        for f in failures:
            print(" -", f)
        return 1

    print("\nOK: 引用/锚点/图片/占位符全部闭合")
    return 0


def _sort_key(token: str):
    return (0, int(token[1:])) if token.startswith("E") else (1, int(token))


if __name__ == "__main__":
    sys.exit(main())
