#!/usr/bin/env python3
"""选题中心工具：init / check / set / status。

hub 根目录：~/HermesWork/media-hub/（可用环境变量 MEDIA_HUB 覆盖）
"""
import argparse, csv, datetime as dt, json, os, re, shutil, sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.expanduser(os.environ.get("MEDIA_HUB", "~/HermesWork/media-hub"))
LEDGER = os.path.join(HUB, "ledger.csv")
FIELDS = ["id", "created", "topic", "status", "lead", "go_formats", "review_hours", "updated", "note"]
FORMATS = ["long_video", "short_video", "image_post", "article"]
DECISIONS = {"GO", "LATER", "SKIP"}
PLATFORMS = {"YouTube", "YouTube Shorts", "公众号", "视频号", "微信贴图", "X",
             "小红书", "B站", "微博", "快手", "抖音"}
VIDEO_ONLY = {"抖音", "视频号", "快手", "YouTube", "YouTube Shorts"}  # 只能挂在视频形态上
TEXT_ONLY = {"公众号", "微信贴图"}
WEEKLY_BUDGET = 10.0


def read_ledger():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_ledger(rows):
    os.makedirs(HUB, exist_ok=True)
    with open(LEDGER, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def resolve(d):
    if os.path.isdir(d):
        return os.path.abspath(d)
    p = os.path.join(HUB, d)
    if os.path.isdir(p):
        return p
    sys.exit(f"ERR 找不到目录 {d}")


def cmd_init(a):
    today = dt.date.today().strftime("%Y%m%d")
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", a.slug or a.topic).strip("-")[:40]
    hid = f"{today}-{slug}"
    d = os.path.join(HUB, hid)
    if os.path.exists(d):
        sys.exit(f"ERR 已存在 {d}")
    os.makedirs(os.path.join(d, "copy"))
    brief = open(os.path.join(SKILL_DIR, "templates/brief.md"), encoding="utf-8").read()
    brief = brief.replace("{topic}", a.topic).replace("{dir}", d).replace("{date}", dt.date.today().isoformat())
    open(os.path.join(d, "brief.md"), "w", encoding="utf-8").write(brief)
    dec = json.load(open(os.path.join(SKILL_DIR, "templates/decision.json"), encoding="utf-8"))
    dec["topic"] = a.topic
    json.dump(dec, open(os.path.join(d, "decision.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump([], open(os.path.join(d, "facts.json"), "w"))
    rows = read_ledger()
    now = dt.datetime.now().isoformat(timespec="minutes")
    rows.append({"id": hid, "created": now, "topic": a.topic, "status": "research", "updated": now})
    write_ledger(rows)
    print(f"HUB {d}")


def norm(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # markdown 链接只留文字
    return re.sub(r"\s+", "", s)


def cmd_check(a):
    d = resolve(a.dir)
    errs, warns = [], []
    facts = json.load(open(os.path.join(d, "facts.json"), encoding="utf-8"))
    ids = set()
    cache = {}
    for f in facts:
        fid = f.get("id")
        if not fid or not f.get("url") or not f.get("quote") or not f.get("local"):
            errs.append(f"事实缺字段：{fid or f}")
            continue
        if fid in ids:
            errs.append(f"事实编号重复：{fid}")
        ids.add(fid)
        loc = os.path.expanduser(f["local"])
        if not os.path.exists(loc):
            errs.append(f"{fid} 本地原文不存在：{loc}")
            continue
        if loc not in cache:
            cache[loc] = norm(open(loc, encoding="utf-8", errors="ignore").read())
        if norm(f["quote"]) not in cache[loc]:
            errs.append(f"{fid} 引语在本地原文里找不到")
    if len(facts) < 3:
        errs.append(f"事实只有 {len(facts)} 条（<3，按 Stop 规则告诉用户选题撑不起来）")

    dec = json.load(open(os.path.join(d, "decision.json"), encoding="utf-8"))
    for k in ["angle"]:
        if not dec.get(k):
            errs.append(f"decision.{k} 为空")
    for k, v in dec.get("scores", {}).items():
        if k == "ip_fit" and v is None:
            continue
        if not isinstance(v, (int, float)) or not 0 <= v <= 5:
            errs.append(f"scores.{k} 应为 0-5，现为 {v}")
    ip = dec.get("ip")
    if ip is None:
        warns.append("decision.json 没有 ip 字段（11-08 前的旧选题）：新选题按 templates/decision.json 补 IP 对齐")
    ip = ip or {}
    personal = "account" in ip and ip.get("account") == "personal"
    ipfit = (dec.get("scores") or {}).get("ip_fit")
    if personal:
        if ipfit is None:
            errs.append("scores.ip_fit 为空：个人号选题必须按 ip-principle.md 打分（公司号把 ip.account 设为 company）")
        for k in ["real_question", "step", "line", "slogan_tie"]:
            if not ip.get(k):
                errs.append(f"ip.{k} 为空：个人号选题必须写清 IP 对齐")
        if ip.get("step") and ip["step"] not in {"说清需求", "拆成步骤", "验收结果", "无"}:
            errs.append("ip.step 只能是 说清需求/拆成步骤/验收结果/无")
        sv = (dec.get("formats") or {}).get("short_video", {})
        if sv.get("decision") == "GO" and isinstance(ipfit, (int, float)) and ipfit < 4:
            errs.append(f"short_video 是 GO 但 ip_fit={ipfit}<4：先补并排实测，或改为 LATER/长文")
        if sv.get("decision") == "GO" and not ip.get("demo"):
            errs.append("short_video 是 GO 但 ip.demo 为空：写清并排实测方案")
    for fid in dec.get("hook_fact_ids", []) or [None]:
        if fid is None:
            errs.append("hook_fact_ids 为空：钩子必须有事实支撑")
        elif fid not in ids:
            errs.append(f"钩子引用了不存在的事实 {fid}")
    go_hours = 0.0
    fm = dec.get("formats", {})
    for name in FORMATS:
        x = fm.get(name)
        if not x:
            errs.append(f"缺少形态 {name}")
            continue
        if x.get("decision") not in DECISIONS:
            errs.append(f"{name}.decision 必须是 GO/LATER/SKIP")
        if not x.get("reason"):
            errs.append(f"{name} 没写理由")
        if x.get("decision") == "GO":
            if not x.get("platforms"):
                errs.append(f"{name} 是 GO 但没写平台")
            if not x.get("fact_ids"):
                errs.append(f"{name} 是 GO 但没引用事实编号")
            go_hours += float(x.get("review_hours") or 0)
        for p in x.get("platforms", []):
            if p not in PLATFORMS:
                errs.append(f"{name} 的平台「{p}」不在用户定的范围内")
            elif p in VIDEO_ONLY and name not in ("long_video", "short_video"):
                errs.append(f"{name} 不能投「{p}」：该平台只接视频")
            elif p in TEXT_ONLY and name in ("long_video", "short_video"):
                errs.append(f"{name} 不能投「{p}」：该平台不接视频")
        if "X" in x.get("platforms", []) and x.get("lang") and "en" not in x.get("lang", []):
            errs.append(f"{name} 投 X 但语言没有 en（用户定 X 用英文）")
        for fid in x.get("fact_ids", []):
            if fid not in ids:
                errs.append(f"{name} 引用了不存在的事实 {fid}")
    gos = [n for n in FORMATS if fm.get(n, {}).get("decision") == "GO"]
    order = dec.get("order", [])
    if gos and not order:
        errs.append("order 为空：要写清先做哪个")
    for n in gos:
        if n not in order:
            warns.append(f"GO 的 {n} 没出现在 order 里")

    week = committed_hours(exclude=os.path.basename(d))
    if go_hours + week > WEEKLY_BUDGET and not dec.get("budget_note"):
        errs.append(f"审核小时超预算：本题 {go_hours}h + 本周其他 {week}h > {WEEKLY_BUDGET}h，降级为 LATER 或在 budget_note 写明理由")

    brief = open(os.path.join(d, "brief.md"), encoding="utf-8").read()
    head = brief.split("## 交付")[0]
    for pat in [r"\d+\s*倍", "百倍"]:
        for m in re.finditer(pat, head):
            warns.append(f"brief 出现倍数说法「{m.group(0)}」：只能用本期实测数字，确认有事实编号或实测记录")
    n_todo = head.count("TODO")
    if n_todo:
        errs.append(f"brief.md 还有 {n_todo} 处 TODO")

    for w in warns:
        print("WARN", w)
    for e in errs:
        print("FAIL", e)
    print(f"facts={len(facts)} go={gos} go_hours={go_hours} week_other={week}")
    if errs:
        print("HUB FAIL")
        sys.exit(1)
    rows = read_ledger()
    for r in rows:
        if r["id"] == os.path.basename(d):
            r["go_formats"] = "+".join(gos)
            r["review_hours"] = str(go_hours)
            r["lead"] = order[0] if order else ""
            if r["status"] == "research":
                r["status"] = "judged"
            r["updated"] = dt.datetime.now().isoformat(timespec="minutes")
    write_ledger(rows)
    print("HUB OK")


def committed_hours(exclude=""):
    """本周（周一起）创建、状态为 judged/approved/producing/drafted 的选题的审核小时之和。"""
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    tot = 0.0
    for r in read_ledger():
        if r["id"] == exclude:
            continue
        try:
            c = dt.date.fromisoformat(r["created"][:10])
        except ValueError:
            continue
        if c >= monday and r["status"] in {"judged", "approved", "producing", "drafted"}:
            tot += float(r.get("review_hours") or 0)
    return tot


def cmd_set(a):
    d = resolve(a.dir)
    hid = os.path.basename(d)
    rows = read_ledger()
    hit = False
    for r in rows:
        if r["id"] == hid:
            for kv in a.kv:
                k, _, v = kv.partition("=")
                if k not in FIELDS:
                    sys.exit(f"ERR 未知字段 {k}")
                r[k] = v
            r["updated"] = dt.datetime.now().isoformat(timespec="minutes")
            hit = True
    if not hit:
        sys.exit(f"ERR ledger 里没有 {hid}")
    write_ledger(rows)
    print("SET OK", hid, a.kv)


def cmd_status(a):
    rows = read_ledger()
    for r in rows[-a.n:]:
        print(f"{r['id']} | {r['status']} | lead={r.get('lead','')} | go={r.get('go_formats','')} | {r.get('review_hours','')}h")
    print(f"本周已承诺审核：{committed_hours()}h / {WEEKLY_BUDGET}h")


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("init"); x.add_argument("topic"); x.add_argument("--slug"); x.set_defaults(f=cmd_init)
    x = s.add_parser("check"); x.add_argument("dir"); x.set_defaults(f=cmd_check)
    x = s.add_parser("set"); x.add_argument("dir"); x.add_argument("kv", nargs="+"); x.set_defaults(f=cmd_set)
    x = s.add_parser("status"); x.add_argument("-n", type=int, default=20); x.set_defaults(f=cmd_status)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
