#!/usr/bin/env python3
"""Attach a verbatim Chinese quote to a sources.py ledger entry.

Why this exists: `sources.py quote` rejects any quote with fewer than three
whitespace-separated tokens, and a whole Chinese sentence is usually ONE token.
Hand-inserting spaces after full-width punctuation does not fix it — the
matcher collapses whitespace to a single space rather than deleting it, so a
space that is absent from the evidence text makes the quote stop being a
verbatim substring (`not found verbatim`).

Strategy: locate the phrase with all whitespace stripped, map the hit back to
the original character indices, then widen to WHOLE sentence/line boundaries
(`。！？\n`) until the span has >= 3 tokens. Sentence-aligned spans carry the
newlines/numbers the token counter needs, and never cut a markdown link
(`[![Image`, `[text](url)`) in half.

Usage:
  python3 attach_cjk_quote.py --id 12 --from evidence/page.txt --ledger ledger.json \
      "个人主体，暂不支持选择文化互动"
  # add --dry to print the span without touching the ledger
  # add --sources-py /path/to/sources.py if the skill moved
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

DEFAULT_SOURCES = os.path.expanduser(
    "~/.hermes/skills/research/grounded-citations/scripts/sources.py"
)
SENT_END = "。！？\n"


def locate_span(evidence: str, phrase: str, max_chars: int = 600) -> str | None:
    """Return a sentence-aligned verbatim slice containing `phrase`."""
    chars, idx = [], []
    for i, ch in enumerate(evidence):
        if not ch.isspace():
            chars.append(ch)
            idx.append(i)
    norm_e = "".join(chars)
    norm_q = re.sub(r"\s+", "", phrase)
    pos = norm_e.find(norm_q)
    if pos < 0:
        return None

    start = idx[pos]
    end = idx[pos + len(norm_q) - 1] + 1

    k = start - 1
    while k > 0 and evidence[k] not in SENT_END:
        k -= 1
    if evidence[k] in SENT_END:
        start = k + 1

    k = end
    while k < len(evidence) and evidence[k] not in SENT_END:
        k += 1
    end = k + 1 if k < len(evidence) else k

    while len(evidence[start:end].split()) < 3 and end < len(evidence) and end - start < max_chars:
        k = end
        while k < len(evidence) and evidence[k] not in SENT_END:
            k += 1
        end = k + 1 if k < len(evidence) else k

    while len(evidence[start:end].split()) < 3 and start > 0 and end - start < max_chars + 300:
        k = start - 2
        while k > 0 and evidence[k] not in SENT_END:
            k -= 1
        start = k + 1 if evidence[k] in SENT_END else 0

    return evidence[start:end]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phrase", help="distinctive substring of the sentence you want to cite")
    ap.add_argument("--id", type=int, required=True, help="ledger source id")
    ap.add_argument("--from", dest="evidence_file", required=True)
    ap.add_argument("--ledger", default=os.environ.get("HERMES_CITATION_LEDGER"))
    ap.add_argument("--sources-py", default=DEFAULT_SOURCES)
    ap.add_argument("--dry", action="store_true", help="print the span only")
    args = ap.parse_args()

    evidence = open(args.evidence_file, encoding="utf-8", errors="ignore").read()
    span = locate_span(evidence, args.phrase)
    if span is None:
        print("NOT FOUND: phrase is not in the evidence text (check copy/paste and the right file)")
        return 2

    span = " ".join(span.split())
    print("SPAN:", span)
    if args.dry:
        return 0

    # --ledger is a TOP-LEVEL flag on sources.py: argparse rejects it when it
    # trails the subcommand ("unrecognized arguments: --ledger"). Emit it first.
    cmd = [sys.executable, args.sources_py]
    if args.ledger:
        cmd += ["--ledger", args.ledger]
    cmd += ["quote", str(args.id), "--text", span, "--from", args.evidence_file]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
