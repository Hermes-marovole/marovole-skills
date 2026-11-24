#!/usr/bin/env python3
"""End-to-end acceptance test for an installed market-intelligence research stack.

Run this instead of asserting "环境已就绪". Every check executes the real code path and
prints what actually came back; a check that cannot prove itself reports FAIL or
FAILOVER, never OK.

Checks:
  1. CLI binaries          opencli / dokobot / tinyfish / uvx
  2. Router key presence   non-empty and not a <YOUR_...> placeholder
  3. Router per engine     compares the returned `engine` field against the one asked
                           for -- an explicit --engine still fails over, so "1 hit"
                           alone proves nothing about that engine
  4. Router extract path   firecrawl, then jina
  5. intent radar          autocomplete + e-commerce buying box
  6. size triangulation    top-down vs bottom-up divergence report

Usage:
    python3 verify_stack.py                 # default probe topic
    python3 verify_stack.py --topic "甘氨酸镁"
    python3 verify_stack.py --json           # machine-readable summary

Exit code is 1 if any REQUIRED check fails, so it can gate a handoff.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
ROUTER_CANDIDATES = [
    HOME / ".config/agent-research-router/search.py",
    HOME / ".hermes/skills/research/web-search/scripts/search.py",
]
MI_TOOL_CANDIDATES = [
    HOME / ".hermes/skills/research/market-intelligence/scripts/market_intel_tool.py",
    HOME / ".claude/skills/market-intelligence/scripts/market_intel_tool.py",
]
ENGINES = ["auto", "exa", "tavily", "serper", "brave", "firecrawl", "ddgs"]
KEYS = [
    "EXA_API_KEY",
    "TAVILY_API_KEY",
    "SERPER_API_KEY",
    "BRAVE_SEARCH_API_KEY",
    "FIRECRAWL_API_KEY",
    "TINYFISH_API_KEY",
]
RESULTS = []


def record(name, status, detail, required=True):
    RESULTS.append({"check": name, "status": status, "detail": detail, "required": required})
    print(f"  [{status:4}] {name:28} {detail}")


def first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def run(cmd, timeout=45):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_binaries():
    print("\n=== 1. CLI binaries ===")
    for cmd in ("opencli", "dokobot", "tinyfish", "uvx"):
        path = shutil.which(cmd)
        record(cmd, "OK" if path else "FAIL", path or "not on PATH")


def check_keys():
    print("\n=== 2. Router key presence ===")
    vals = {}
    env_path = HOME / ".hermes/.env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*)$", line)
            if m:
                vals.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))
    for k in KEYS:
        v = vals.get(k) or os.getenv(k, "")
        v = v.strip()
        # An empty or placeholder value passes every "does the key exist" check and still 401s.
        good = len(v) > 10 and not v.startswith("<YOUR_") and not v.startswith("在这里填")
        record(k, "OK" if good else "EMPTY", f"{len(v)}ch" if v else "missing", required=False)


def check_engines(router, probe):
    print("\n=== 3. Router per engine ===")
    for eng in ENGINES:
        try:
            cp = run([sys.executable, str(router), "search", probe, "--engine", eng, "-n", "1", "--json"], timeout=60)
            payload = json.loads(cp.stdout)
            served = payload.get("engine")
            n = len(payload.get("results") or [])
            if served == eng:
                record(f"engine {eng}", "OK", f"served by {served}, {n} hit(s)")
            else:
                # Requested engine failed over; that engine is NOT verified.
                record(f"engine {eng}", "FAILOVER", f"requested {eng}, served by {served}, {n} hit(s)", required=False)
        except Exception as e:
            record(f"engine {eng}", "FAIL", f"{type(e).__name__}: {e}"[:90], required=False)


def check_extract(router):
    print("\n=== 4. Router extract ===")
    for eng in ("firecrawl", "jina"):
        try:
            cp = run([sys.executable, str(router), "extract", "https://example.com", "--engine", eng, "--json"], timeout=60)
            rows = json.loads(cp.stdout)
            served = rows[0].get("engine")
            chars = len(rows[0].get("markdown") or "")
            if chars > 100 and served == eng:
                record(f"extract {eng}", "OK", f"{chars} chars markdown")
            elif chars > 100:
                record(f"extract {eng}", "FAILOVER", f"served by {served}, {chars} chars", required=False)
            else:
                record(f"extract {eng}", "FAIL", str(rows[0].get("error"))[:90], required=False)
        except Exception as e:
            record(f"extract {eng}", "FAIL", f"{type(e).__name__}: {e}"[:90], required=False)


def check_intent(mi_tool, topic):
    print("\n=== 5. intent radar (autocomplete + buying box) ===")
    if not mi_tool:
        record("intent", "FAIL", "market_intel_tool.py not found")
        return
    try:
        cp = run([sys.executable, str(mi_tool), "intent", topic, "--json"], timeout=60)
        d = json.loads(cp.stdout)
        engines = d.get("search_engines", {})
        baidu = len(engines.get("baidu") or [])
        google = len(engines.get("google") or [])
        buying = (d.get("ecommerce_buying_intent") or {}).get("taobao_tmall") or []
        ok = (baidu + google) > 0
        record("intent autocomplete", "OK" if ok else "FAIL", f"google={google} baidu={baidu} terms")
        record("intent buying box", "OK" if buying else "FAIL", str(buying[:3]), required=False)
    except Exception as e:
        record("intent", "FAIL", f"{type(e).__name__}: {e}"[:90])


def check_size(mi_tool):
    print("\n=== 6. size triangulation self-test ===")
    if not mi_tool:
        record("size", "FAIL", "market_intel_tool.py not found")
        return
    try:
        cp = run([
            sys.executable, str(mi_tool), "size",
            "--tam-total", "200000000000", "--sam-pct", "0.15", "--som-pct", "0.01",
            "--total-customers", "150000000", "--reachable-customers", "10000000",
            "--conv-rate", "0.015", "--acv", "1800",
        ], timeout=30)
        out = cp.stdout.strip()
        ok = "Triangulation" in out
        record("size triangulation", "OK" if ok else "FAIL", out.splitlines()[-1][:80] if out else "no output")
    except Exception as e:
        record("size", "FAIL", f"{type(e).__name__}: {e}"[:90])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="甘氨酸镁", help="probe keyword for the intent radar")
    ap.add_argument("--probe", default="Apple 10-K Gross Margin", help="probe query for the router")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    router = first_existing(ROUTER_CANDIDATES)
    mi_tool = first_existing(MI_TOOL_CANDIDATES)
    print(f"router : {router or 'NOT FOUND'}")
    print(f"mi_tool: {mi_tool or 'NOT FOUND'}")

    check_binaries()
    check_keys()
    if router:
        check_engines(router, args.probe)
        check_extract(router)
    else:
        record("router", "FAIL", "searched: " + ", ".join(str(p) for p in ROUTER_CANDIDATES))
    check_intent(mi_tool, args.topic)
    check_size(mi_tool)

    failed = [r for r in RESULTS if r["required"] and r["status"] == "FAIL"]
    failovers = [r for r in RESULTS if r["status"] == "FAILOVER"]
    print("\n=== Summary ===")
    print(f"required failures: {len(failed)}")
    if failovers:
        print("FAILOVER = asked one engine, answered by another; that engine is NOT verified:")
        for r in failovers:
            print(f"  - {r['check']}: {r['detail']}")
    if args.json:
        print(json.dumps({"ok": not failed, "results": RESULTS}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
