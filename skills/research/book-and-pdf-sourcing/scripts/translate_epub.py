#!/usr/bin/env python3
"""Resumable per-page EPUB translator (source language -> Chinese).

Translates paragraph text in place inside each page's HTML, keeps every tag
(<img>, <span>, math, anchors) untouched, writes state to disk after each page
so an interrupted run resumes, and repackages the EPUB periodically.

Usage:
    python3 translate_epub.py --src book.epub --out book_zh.epub \
        --endpoint http://127.0.0.1:3425/v1/chat/completions \
        --model auto/gemini-3.8-flash --workers 4

Confirm the model id first: curl -s <base>/models | head -c 200
Run it with terminal(background=true, notify=true).
"""

import argparse
import json
import os
import re
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

PROMPT = (
    "你是顶尖的学术翻译专家。将下面的英文教材片段翻译为严谨、权威、符合中文学术习惯的专业中文。\n"
    "要求：\n"
    "1. 专业术语准确规范，同一术语全篇保持同一译法。\n"
    "2. 公式、数字、标识符、代码、英文缩写原样保留。\n"
    "3. 只输出译文，不要任何说明、提示语或前后缀。\n\n"
    "待翻译内容：\n{text}"
)

SKIP_NAME = re.compile(r"(nav|toc|cover|titlepage|copyright|colophon)", re.I)
LEAD_PAGE_NO = re.compile(r"^\s*\d{1,4}\s+")


def log(msg, log_path):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def translate(text, endpoint, model, retries=3):
    text = LEAD_PAGE_NO.sub("", text.strip())
    if len(text) < 12:
        return text
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT.format(text=text)}],
        "temperature": 0.2,
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer local"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            if attempt == retries - 1:
                return text  # keep source text rather than lose the paragraph
            time.sleep(2 ** attempt)


def translate_page(path, endpoint, model):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    def repl(m):
        open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
        out = []
        for part in re.split(r"(<[^>]+>)", inner):
            if part.startswith("<") and part.endswith(">"):
                out.append(part)
            elif part.strip():
                out.append(translate(part, endpoint, model))
            else:
                out.append(part)
        return "%s%s%s" % (open_tag, "".join(out), close_tag)

    new = re.sub(r"(<p[^>]*>)(.*?)(</p>)", repl, content, flags=re.DOTALL)
    new = re.sub(r'lang="[^"]*"', 'lang="zh-CN"', new)
    new = re.sub(r'xml:lang="[^"]*"', 'xml:lang="zh-CN"', new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def package(build, out, log_path, skip):
    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        mt = os.path.join(build, "mimetype")
        if os.path.exists(mt):
            z.write(mt, "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, _dirs, files in os.walk(build):
            for name in files:
                if name == "mimetype" or name in skip or name.endswith(".tmp"):
                    continue
                full = os.path.join(root, name)
                z.write(full, os.path.relpath(full, build))
    os.replace(tmp, out)
    log("packaged %s (%s bytes)" % (out, format(os.path.getsize(out), ",")), log_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--repack-every", type=int, default=100)
    a = ap.parse_args()

    build = os.path.splitext(a.src)[0] + "_build"
    os.makedirs(build, exist_ok=True)
    log_path = os.path.join(build, "translation.log")
    state_path = os.path.join(build, "progress.json")
    skip = {"progress.json", "translation.log", ".extracted"}

    if not os.path.exists(os.path.join(build, ".extracted")):
        with zipfile.ZipFile(a.src) as z:
            z.extractall(build)
        open(os.path.join(build, ".extracted"), "w").close()
        log("extracted -> %s" % build, log_path)

    done = set()
    if os.path.exists(state_path):
        try:
            done = set(json.load(open(state_path, encoding="utf-8")))
        except Exception:
            done = set()

    pages = []
    for root, _dirs, files in os.walk(build):
        for name in files:
            if name.lower().endswith((".html", ".xhtml")) and not SKIP_NAME.search(name):
                pages.append(os.path.relpath(os.path.join(root, name), build))
    pages.sort()
    todo = [p for p in pages if p not in done]
    log("pages=%d done=%d todo=%d" % (len(pages), len(done), len(todo)), log_path)

    if todo:
        t0 = last_pack = time.time()
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(translate_page, os.path.join(build, p),
                              a.endpoint, a.model): p for p in todo}
            for i, fut in enumerate(as_completed(futs), 1):
                p = futs[fut]
                try:
                    fut.result()
                    done.add(p)
                except Exception as e:
                    log("FAIL %s: %s" % (p, e), log_path)
                if i % 5 == 0:
                    json.dump(sorted(done), open(state_path, "w", encoding="utf-8"))
                if i % 20 == 0:
                    rate = i / max(time.time() - t0, 1) * 60
                    log("%d/%d %.0f p/min eta %.0f min" %
                        (i, len(todo), rate, (len(todo) - i) / max(rate, 1e-6)), log_path)
                if i % a.repack_every == 0 or time.time() - last_pack > 600:
                    json.dump(sorted(done), open(state_path, "w", encoding="utf-8"))
                    package(build, a.out, log_path, skip)
                    last_pack = time.time()

    json.dump(sorted(done), open(state_path, "w", encoding="utf-8"))
    package(build, a.out, log_path, skip)
    log("done", log_path)


if __name__ == "__main__":
    main()
