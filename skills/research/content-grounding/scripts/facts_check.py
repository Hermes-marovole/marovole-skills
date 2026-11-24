#!/usr/bin/env python3
"""facts_check.py — 长稿事实台账的逐字校验器。

用途：当产出不是 grounding.py 的 briefing/tietu/longform 三类（视频剧本、
纪录片解说词、多章深度稿、书籍章节），没有现成 --kind 闸门时，先把每一个要用
的事实做成一份 facts.json 台账，再用本脚本对照【本地已抓取的原文】逐字校验，
通过后才允许正文继续写下去。

facts.json 格式（list，或 {"facts": [...]}）：
[
  {
    "id": "F01",
    "url": "https://...",            # 可选，溯源用
    "local": "/abs/path/evidence/2026-01-01/abcd1234.txt",  # grounding.py fetch 落地的正文
    "quote": "原文逐字片段",         # 连 markdown 标记一起复制，见下
    "kind": "fact"                  # 可选：fact | derived（derived 不校验本地原文）
  }
]

derived（换算/加权出来的数）没有本地原文可对，写进单独字段并在正文用 [D1]
这类标记，本脚本只统计、不校验。

关键规则（踩过坑）：
  归一化【只折叠空白】，绝不剥离 markdown 标记。原文里的 `**粗体**`、
  `[文字](url)` 是内容的一部分；把两边都剥掉会掩盖真实漂移，只剥一边
  必然误报。quote 要连标记原样复制粘贴，不要手工“抄干净”。

用法：
  python3 facts_check.py --facts facts.json
  python3 facts_check.py --facts facts.json --script script_zh_v1.md
  python3 facts_check.py --facts facts.json --script s.md --require-all

退出码：0 全部通过（且 --require-all 时台账每条都被引用）；1 有失败。
"""

import argparse
import json
import os
import re
import sys

WS = re.compile(r"\s+")
TAG = re.compile(r"\[(F\d+|D\d+)\]")


def norm(s: str) -> str:
    """只折叠空白。不要加 markdown 剥离，理由见文件头。"""
    return WS.sub("", s)


def load_facts(path: str):
    data = json.load(open(path, encoding="utf-8"))
    facts = data.get("facts") if isinstance(data, dict) else data
    if not isinstance(facts, list):
        sys.exit(f"facts 文件结构不对：{path}")
    return facts


def cache():
    store = {}

    def get(p):
        if p not in store:
            if not os.path.exists(p):
                store[p] = None
            else:
                store[p] = norm(open(p, encoding="utf-8", errors="replace").read())
        return store[p]

    return get


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", required=True)
    ap.add_argument("--script", help="正文文件，用来核对 [Fxx]/[Dxx] 标记")
    ap.add_argument("--require-all", action="store_true",
                    help="台账每条都必须被正文引用，否则失败")
    a = ap.parse_args()

    facts = load_facts(a.facts)
    get = cache()
    failed, checked, derived = [], 0, 0
    ids = set()

    for f in facts:
        fid = str(f.get("id"))
        ids.add(fid)
        if f.get("kind") == "derived" or fid.startswith("D"):
            derived += 1
            continue
        local, quote = f.get("local"), f.get("quote", "")
        if not local or not quote:
            failed.append((fid, "缺 local 或 quote"))
            continue
        body = get(local)
        if body is None:
            failed.append((fid, f"本地原文不存在：{local}"))
            continue
        checked += 1
        if norm(quote) not in body:
            failed.append((fid, f"quote 在原文中找不到：{quote[:70]}… ({local})"))

    print(f"台账 {len(facts)} 条：校验 {checked} 条原文事实，{derived} 条 derived 跳过")

    rc = 0
    for fid, msg in failed:
        print(f"  FAIL {fid}: {msg}")
        rc = 1

    if a.script:
        text = open(a.script, encoding="utf-8").read()
        used, order = set(TAG.findall(text)), []
        for t in TAG.findall(text):
            if t not in order:
                order.append(t)
        missing = [t for t in order if t not in ids]
        unused = [i for i in sorted(ids) if i not in used]
        print(f"正文引用 {len(used)} 个标记；未定义 {len(missing)} 个；台账未引用 {len(unused)} 条")
        for t in missing:
            print(f"  FAIL [{t}]: 正文引用但台账里没有这个 id")
            rc = 1
        if unused:
            print(f"  WARN 未被正文引用：{', '.join(unused)}")
            if a.require_all:
                rc = 1

    print("FACTS OK" if rc == 0 else "FACTS FAILED")
    return rc


if __name__ == "__main__":
    sys.exit(main())
