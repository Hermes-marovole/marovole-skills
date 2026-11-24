#!/usr/bin/env python3
"""
adb_teardown_probe.py — CLI helper for mobile-app-teardown skill.
Supports:
  check  : Verify adb, mumutool, agent-device, connected devices, screen size & density (px + dp).
  resize : Stop MuMu VM, apply mainstream 20:9 phone resolution (default 1080x2400 @ 450dpi), restart & reconnect adb.
  dump   : Save <tag>.png + <tag>.txt + <tag>.json (filtered visible nodes + full NDJSON) and print compact summary.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

EXTRA_PATHS = [
    str(Path.home() / ".local" / "bin"),
    str(Path.home() / ".npm-global" / "bin"),
    "/opt/homebrew/bin",
    "/opt/homebrew/share/android-commandlinetools/platform-tools",
    "/Applications/MuMuPlayer.app/Contents/MacOS",
]


def build_env() -> dict:
    env = os.environ.copy()
    cur = env.get("PATH", "")
    parts = [p for p in EXTRA_PATHS if os.path.isdir(p)] + [cur]
    env["PATH"] = ":".join(parts)
    return env


def run_cmd(cmd: list[str], timeout: int = 60, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=build_env(), capture_output=True, text=True, timeout=timeout, check=check)


def cmd_check(args: argparse.Namespace) -> int:
    env = build_env()
    for tool in ("adb", "mumutool", "agent-device", "scrcpy"):
        loc = shutil.which(tool, path=env["PATH"])
        print(f"[bin] {tool:14s}: {loc or 'MISSING'}")

    devs = run_cmd(["adb", "devices", "-l"]).stdout.strip()
    print(f"\n[adb devices]\n{devs}")

    serial_args = ["-s", args.serial] if args.serial else []
    m_all = re.findall(r"^(\S+)\s+device\b", devs, flags=re.M)
    target = args.serial or (m_all[0] if m_all else None)
    if not target:
        print("\n[warn] No active ADB device connected. Run `mumutool open 0 && adb connect 127.0.0.1:16384`.")
        return 1

    sz = run_cmd(["adb", "-s", target, "shell", "wm", "size"]).stdout.strip()
    dn = run_cmd(["adb", "-s", target, "shell", "wm", "density"]).stdout.strip()
    print(f"\n[display] ({target}) {sz} | {dn}")

    m_sz = re.search(r"(\d+)x(\d+)", sz)
    m_dn = re.search(r"(\d+)", dn)
    if m_sz and m_dn:
        w, h = int(m_sz.group(1)), int(m_sz.group(2))
        dpi = int(m_dn.group(1))
        scale = dpi / 160.0
        dp_w, dp_h = round(w / scale, 1), round(h / scale, 1)
        ratio = round(max(w, h) / min(w, h), 2)
        print(f"[logical] {dp_w} x {dp_h} dp (scale={scale:.3f}x, aspect={ratio}:1)")
        if w > h or ratio < 1.85 or w > 1440:
            print("[warn] Non-standard phone aspect/resolution detected! Recommend `resize --size 1080x2400 --dpi 450` (20:9 FHD+).")
        else:
            print("[ok] Mainstream smartphone portrait proportions verified.")
    return 0


def cmd_resize(args: argparse.Namespace) -> int:
    idx = str(args.index)
    print(f"[1/4] Stopping MuMu device {idx}...")
    run_cmd(["mumutool", "close", idx], timeout=30)
    time.sleep(3)

    setting = json.dumps({"resolutionWidthHeight": args.size, "resolutionDPI": args.dpi})
    print(f"[2/4] Applying config: {setting}")
    res = run_cmd(["mumutool", "config", idx, "--setting", setting], timeout=30)
    if res.returncode != 0:
        print(res.stderr or res.stdout, file=sys.stderr)
        return 1

    print(f"[3/4] Booting MuMu device {idx}...")
    run_cmd(["mumutool", "open", idx], timeout=30)
    time.sleep(args.wait)

    info_out = run_cmd(["mumutool", "info", idx], timeout=15).stdout
    port = 16384
    try:
        port = json.loads(info_out).get("return", {}).get("adb_port", 16384)
    except Exception:
        pass

    serial = f"127.0.0.1:{port}"
    print(f"[4/4] Connecting ADB to {serial}...")
    run_cmd(["adb", "connect", serial], timeout=15)
    args.serial = serial
    return cmd_check(args)


def cmd_dump(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = args.tag

    png_path = out_dir / f"{tag}.png"
    txt_path = out_dir / f"{tag}.txt"
    json_path = out_dir / f"{tag}.json"

    # Capture screenshot via raw ADB screencap first — immune to animated carousel UI-idle hangs
    env = build_env()
    with open(png_path, "wb") as pf:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], env=env, stdout=pf, timeout=20, check=False)

    try:
        txt_out = run_cmd(["agent-device", "snapshot", "--force-full"], timeout=25).stdout
    except subprocess.TimeoutExpired:
        txt_out = "[timeout] Animated carousel prevented UI idle; inspect PNG directly with vision_analyze.\n"
    txt_path.write_text(txt_out, encoding="utf-8")

    nodes = []
    try:
        raw_out = run_cmd(["agent-device", "snapshot", "--raw", "--force-full"], timeout=25).stdout
        for line in raw_out.splitlines():
            s = line.strip()
            if s.startswith("{") and s.endswith("}"):
                try:
                    n = json.loads(s)
                    if n.get("visibleToUser"):
                        nodes.append(n)
                except Exception:
                    pass
    except subprocess.TimeoutExpired:
        print(f"[warn] snapshot --raw timed out on {tag} (live carousel/animation); PNG saved cleanly.")
    json_path.write_text(json.dumps(nodes, ensure_ascii=False, indent=2), encoding="utf-8")

    labeled = [n for n in nodes if n.get("label") and n.get("bundleId") != "com.android.systemui"]
    print(f"[saved] {png_path.name}, {txt_path.name}, {json_path.name} ({len(nodes)} visible nodes, {len(labeled)} labeled app nodes)")
    for n in labeled[:35]:
        ident = (n.get("identifier") or "").split("/")[-1]
        r = n.get("rect", {})
        rect_s = f"({r.get('x')},{r.get('y')},{r.get('width')}x{r.get('height')})"
        lbl = (n.get("label") or "").replace("\n", " ⏎ ")
        print(f"  [{n.get('ref','')}:{ident}] {rect_s} {lbl[:120]}")
    if len(labeled) < 5:
        print("[hint] Sparse text nodes (<5) — likely WebView image banner, modal overlay, or Canvas. Inspect PNG with vision_analyze!")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="ADB + agent-device mobile app teardown helper")
    sub = p.add_subparsers(dest="sub", required=True)

    p_chk = sub.add_parser("check", help="Check binaries, ADB connection, and phone aspect ratio / DPI")
    p_chk.add_argument("--serial", default=None, help="Optional ADB serial (e.g. 127.0.0.1:16384)")
    p_chk.set_defaults(func=cmd_check)

    p_rsz = sub.add_parser("resize", help="Set MuMu VM to mainstream 20:9 portrait phone resolution")
    p_rsz.add_argument("--index", type=int, default=0, help="MuMu VM index (default: 0)")
    p_rsz.add_argument("--size", default="1080x2400", help="Portrait WxH (default: 1080x2400, 20:9 FHD+)")
    p_rsz.add_argument("--dpi", type=int, default=450, help="Screen DPI (default: 450 -> 384dp width)")
    p_rsz.add_argument("--wait", type=int, default=12, help="Seconds to wait after boot")
    p_rsz.set_defaults(func=cmd_resize)

    p_dmp = sub.add_parser("dump", help="Capture PNG screenshot + text tree + raw JSON nodes")
    p_dmp.add_argument("--out-dir", required=True, help="Output evidence directory")
    p_dmp.add_argument("--tag", required=True, help="Step filename prefix (e.g. 01_onboarding)")
    p_dmp.set_defaults(func=cmd_dump)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
