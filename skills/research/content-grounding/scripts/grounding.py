#!/usr/bin/env python3
"""grounding.py — 内容依据闸门（简报 / 贴图 / 长文共用）。

原则：成稿里的每个事实都要追溯到「本次真正抓到的原文」。模型只能引用证据库里的原文，
不能凭记忆写链接、日期、数字。本脚本负责把这条规则变成机器检查。

  grounding.py fetch  [--date D] URL [URL ...]   抓原文入证据库，打印 发布日/标题/本地文件
  grounding.py show   [--date D] URL             看某个 URL 在证据库里的记录
  grounding.py check  [--date D] --kind K FILE   硬检查（K = briefing | tietu | longform）
  grounding.py review [--date D] --kind K FILE   独立模型核对（与写稿模型不同），有问题就非 0 退出
  grounding.py audit  [--date D] [--n 5]         抽查某天已产出的简报/贴图/长文（晨间复盘用）

证据库：~/HermesWork/personal/hermes/evidence/<DATE>/index.json + <sha1>.txt（DATE 默认今天，Asia/Shanghai）。
check 时会同时查 DATE 及前 2 天的证据库，方便下游任务复用上游抓过的原文。

每条内容需要的字段（briefing 条目 / tietu post.json；longform 用同目录 evidence.json）：
  "evidence": [{"url": "<已 fetch 的原文 URL>", "quote": "<从原文逐字复制的一句或几句>"}]
  "derived":  [{"value": "1 亿美元", "from": "$100 million"}]   # 可选：换算过的数字，from 必须在原文里
"""
import argparse
import datetime as dt
import hashlib
import html
import html.parser
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TZ = dt.timezone(dt.timedelta(hours=8))
ROOT = pathlib.Path(os.environ.get("GROUNDING_ROOT", pathlib.Path.home() / "HermesWork/personal/hermes/evidence"))
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
MAX_AGE = {"briefing:ai": 3, "briefing:pharma": 7, "briefing:women40": 90, "tietu": 3, "longform": 3}
MIN_QUOTE = 15
LOOKBACK_DAYS = 2


# ------------------------------------------------------------------ helpers
def today():
    return dt.datetime.now(TZ).strftime("%Y-%m-%d")


def norm_url(u):
    p = urllib.parse.urlsplit(u.strip())
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith(("utm_", "ref"))]
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower().removeprefix("www."), path,
                                    urllib.parse.urlencode(q), ""))


def norm_text(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)              # images
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)            # [text](url) -> text
    s = s.replace("\\", "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-"), ("\u00a0", " "),
                 ("，", ","), ("：", ":"), ("；", ";"), ("（", "("), ("）", ")")):
        s = s.replace(a, b)
    s = re.sub(r"[*_`#>|]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _squash(s):
    """匹配用：规范化后去掉所有空白（抓取的正文常把链接前后的空格吃掉）。"""
    return re.sub(r"\s+", "", norm_text(s))


NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")


def numbers(s):
    out = set()
    for m in NUM_RE.findall(s):
        n = m.replace(",", "")
        if n.endswith(".0"):
            n = n[:-2]
        out.add(n)
    return out


def text_numbers(text):
    """原文里出现的数字（去掉千分位逗号），用于"数字必须出自原文"检查。"""
    return numbers(text)


# ------------------------------------------------------------------ store
def store_dir(date):
    return ROOT / date


def load_index(date):
    p = store_dir(date) / "index.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_index(date, idx):
    d = store_dir(date)
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")


def lookup(url, date):
    """在 DATE 及前 LOOKBACK_DAYS 天的证据库里找 URL，返回 (record, text)。"""
    key = norm_url(url)
    d0 = dt.date.fromisoformat(date)
    for back in range(LOOKBACK_DAYS + 1):
        d = (d0 - dt.timedelta(days=back)).isoformat()
        rec = load_index(d).get(key)
        if rec:
            f = store_dir(d) / rec["file"]
            return rec, (f.read_text(encoding="utf-8") if f.exists() else "")
    return None, ""


class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "form"}

    def __init__(self):
        super().__init__()
        self.out, self.depth, self.meta, self.title = [], 0, {}, ""
        self._in_title = False
        self.h1, self._in_h1 = "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.depth += 1
        if tag == "meta":
            k = a.get("property") or a.get("name") or a.get("itemprop") or ""
            if a.get("content"):
                self.meta[k.lower()] = a["content"]
        if tag == "time" and a.get("datetime"):
            self.meta.setdefault("time", a["datetime"])
        if tag == "title":
            self._in_title = True
        if tag == "h1" and not self.h1:
            self._in_h1 = True
        if tag in ("p", "br", "li", "h1", "h2", "h3", "h4", "tr", "div"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        if tag == "title":
            self._in_title = False
        if tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_h1:
            self.h1 += data
        if not self.depth:
            self.out.append(data)


def _published_from_html(raw, meta):
    for k in ("article:published_time", "datepublished", "publishdate", "pubdate", "date", "dc.date",
              "sailthru.date", "parsely-pub-date", "time"):
        if meta.get(k):
            return _parse_date(meta[k]) or meta[k][:10]
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw)
    return m.group(1)[:10] if m else ""


def _parse_date(s):
    import email.utils
    s = s.strip()
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    try:
        return email.utils.parsedate_to_datetime(s).date().isoformat()
    except (TypeError, ValueError):
        return _date_in_text(s)


MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                       "nov", "dec"], 1)}


def _date_in_text(text, anchor=""):
    """meta 缺失时的兜底：取标题附近（没有标题就取正文开头）出现的第一个日期。"""
    i = text.find(anchor) if anchor else -1
    head = text[max(0, i - 1500):i + 1500] if i >= 0 else text[:3000]
    pats = [
        (r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}),? (20\d\d)\b",
         lambda m: (int(m[3]), MONTHS[m[1].lower()[:3]], int(m[2]))),
        (r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? (20\d\d)\b",
         lambda m: (int(m[3]), MONTHS[m[2].lower()[:3]], int(m[1]))),
        (r"\b(20\d\d)-(\d\d)-(\d\d)\b", lambda m: (int(m[1]), int(m[2]), int(m[3]))),
        (r"(20\d\d)年(\d{1,2})月(\d{1,2})日", lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    ]
    for pat, conv in pats:
        m = re.search(pat, head)
        if m:
            try:
                return dt.date(*conv(m)).isoformat()
            except ValueError:
                continue
    return ""


def _get(url, timeout=40, ua=None):
    req = urllib.request.Request(url, headers=ua or UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def fetch_one(url):
    """先走 r.jina.ai（干净正文 + Published Time），失败再直连解析 HTML。"""
    rec = {"url": url, "fetched_at": dt.datetime.now(TZ).isoformat(timespec="seconds")}
    # 直连先探一次状态码，404/410 直接记死链
    direct_status, direct_body = None, ""
    try:
        direct_status, direct_body = _get(url, 30)
    except urllib.error.HTTPError as e:
        direct_status = e.code
    except Exception as e:  # noqa: BLE001
        direct_status = f"ERR {type(e).__name__}"
    rec["status"] = direct_status
    if direct_status in (404, 410):
        rec.update(ok=False, via="direct", reason=f"dead link {direct_status}")
        return rec, ""
    text, title, published, via = "", "", "", ""
    try:
        st, body = _get("https://r.jina.ai/" + url, 60, ua={"User-Agent": "grounding/1.0"})  # jina 拒浏览器 UA
        m = re.search(r"^Title:\s*(.*)$", body, re.M)
        title = m.group(1).strip() if m else ""
        m = re.search(r"^Published Time:\s*(.+)$", body, re.M)
        published = _parse_date(m.group(1)) if m else ""
        i = body.find("Markdown Content:")
        text = body[i + len("Markdown Content:"):].strip() if i >= 0 else body
        via = "jina"
        if re.search(r"(?i)(404|page not found|access denied|just a moment)", title or "") and len(text) < 1500:
            text = ""
        # jina 可能缓存了页面上线前的 404（标题 Page not found，但正文是长导航）；直连 200 时以直连为准
        elif re.search(r"(?i)page not found", title or "") and direct_status == 200:
            text, title = "", ""
    except Exception:  # noqa: BLE001
        text = ""
    if direct_body and (not published or len(text) < 400):
        p = _Text()
        try:
            p.feed(direct_body)
        except Exception:  # noqa: BLE001
            pass
        published = published or _published_from_html(direct_body, p.meta)
        title = title or html.unescape(p.title.strip())
        direct_h1 = html.unescape(p.h1.strip())
        direct_text = re.sub(r"\n\s*\n+", "\n\n", html.unescape("".join(p.out))).strip()
        if len(text) < 400 and len(direct_text) > len(text):
            text, via = direct_text, "direct"
    else:
        direct_text, direct_h1 = "", ""
    published_src = "meta" if published else ""
    if not published:
        anchor = (direct_h1 or re.split(r"\s+[|\\–-]\s+", title)[0]).strip()[:60] if (direct_h1 or title) else ""
        published = _date_in_text(text) or _date_in_text(direct_text, anchor)
        published_src = "text" if published else ""
    # jina 正文常丢掉页眉（标题、作者、日期）；直连能拿到时，把标题附近一段补在正文前
    if via == "jina" and direct_text:
        a = (direct_h1 or "").strip()[:60]
        i = direct_text.find(a) if a else -1
        if i >= 0:
            text = "【页眉】" + direct_text[max(0, i - 600):i + 900].strip() + "\n\n【正文】\n" + text
    ok = len(text) >= 300
    rec.update(ok=ok, via=via or "direct", title=title[:200], published=published, published_src=published_src,
               chars=len(text),
               reason="" if ok else "no readable text (blocked/empty) — 换一个可访问的来源")
    return rec, text


def cmd_fetch(date, urls):
    idx = load_index(date)
    d = store_dir(date)
    d.mkdir(parents=True, exist_ok=True)
    bad = 0
    for u in urls:
        rec, text = fetch_one(u)
        fname = hashlib.sha1(norm_url(u).encode()).hexdigest()[:16] + ".txt"
        if text:
            (d / fname).write_text(text, encoding="utf-8")
        rec["file"] = fname
        idx[norm_url(u)] = rec
        save_index(date, idx)
        flag = "OK " if rec["ok"] else "BAD"
        bad += not rec["ok"]
        print(f"{flag} published={rec.get('published') or '?'} chars={rec.get('chars', 0)} via={rec.get('via')} "
              f"{u}\n    title: {rec.get('title', '')[:120]}\n    text:  {d / fname}"
              + (f"\n    reason: {rec['reason']}" if rec.get("reason") else ""))
    return 1 if bad else 0


def cmd_image(date, url, text_file, published):
    """图片来源：先确认图片 URL 真实可下载，再把（视觉模型/人工）逐字转录存成证据正文。
    正文开头标注【图片转录】，review 能看到这是转录而非网页原文。"""
    try:
        st, _ = _get(url, 30)
    except Exception as e:  # noqa: BLE001
        print(f"BAD image not reachable: {url} ({e})")
        return 1
    body = pathlib.Path(text_file).read_text(encoding="utf-8").strip()
    text = "【图片转录：以下为该图片中可见的文字与图形描述，逐字转录，非网页正文】\n" + body
    idx = load_index(date)
    d = store_dir(date)
    d.mkdir(parents=True, exist_ok=True)
    fname = hashlib.sha1(norm_url(url).encode()).hexdigest()[:16] + ".txt"
    (d / fname).write_text(text, encoding="utf-8")
    idx[norm_url(url)] = {"url": url, "fetched_at": dt.datetime.now(TZ).isoformat(timespec="seconds"),
                          "status": st, "ok": True, "via": "image-transcript", "title": "图片转录",
                          "published": published or "", "published_src": "manual" if published else "",
                          "chars": len(text), "file": fname, "reason": ""}
    save_index(date, idx)
    print(f"OK  image-transcript chars={len(text)} {url}\n    text:  {d / fname}")
    return 0


def cmd_show(date, url):
    rec, text = lookup(url, date)
    print(json.dumps(rec, ensure_ascii=False, indent=1) if rec else "NOT FETCHED")
    if text:
        print(text[:1500])
    return 0 if rec else 1


# ------------------------------------------------------------------ checks
def _days(a, b):
    try:
        return (dt.date.fromisoformat(a[:10]) - dt.date.fromisoformat(b[:10])).days
    except ValueError:
        return None


def check_unit(label, texts, evidence, derived, date, max_age, item_date=None, extra_urls=()):
    """一条内容（简报条目 / 贴图 / 长文一节）的依据检查。返回错误列表。"""
    errs = []
    evidence = evidence or []
    if not evidence:
        return [f"{label}: 没有 evidence（每条至少 1 个 {{url, quote}}）"]
    corpus, published = "", []
    urls = [e.get("url", "") for e in evidence] + list(extra_urls)
    seen = set()
    for u in urls:
        if not u or norm_url(u) in seen:
            continue
        seen.add(norm_url(u))
        rec, text = lookup(u, date)
        if not rec:
            errs.append(f"{label}: 来源没抓过（先 grounding.py fetch）: {u}")
            continue
        if not rec.get("ok"):
            errs.append(f"{label}: 来源不可用（{rec.get('reason')}）: {u}")
            continue
        corpus += "\n" + text
        if rec.get("published"):
            published.append((rec["published"], u))
    ncorpus = norm_text(corpus)
    for e in evidence:
        q = (e.get("quote") or "").strip()
        if len(q) < MIN_QUOTE:
            errs.append(f"{label}: quote 太短（<{MIN_QUOTE} 字符）: {q!r}")
            continue
        rec, text = lookup(e.get("url", ""), date)
        if rec and rec.get("ok") and _squash(q) not in _squash(text):
            errs.append(f"{label}: quote 在原文里找不到（必须逐字复制，不能改写）: {q[:80]!r}")
    # 数字：成稿里的每个数字都要在原文出现，或在 derived 里声明来源
    allowed = text_numbers(corpus)
    for d in derived or []:
        if _squash(d.get("from", "")) and _squash(d.get("from", "")) in _squash(corpus):
            allowed |= numbers(d.get("value", ""))
        else:
            errs.append(f"{label}: derived.from 不在原文里: {d.get('from')!r}")
    # 每个字段开头的「M/D 来源：」前缀是日期，不当数字查（日期另有时效检查）；
    # 链接地址里的数字（文章 ID 等）和「AI 早知道 · MM.DD」栏目日期也不是事实
    body = " ".join(re.sub(r"^\s*\d{1,2}/\d{1,2}", " ", t) for t in texts if t)
    body = re.sub(r"\]\([^)]*\)", "]", body)
    body = re.sub(r"https?://\S+", " ", body)
    body = re.sub(r"早知道\s*·\s*\d{1,2}\.\d{1,2}", " ", body)
    body = re.sub(r"\d{4}[-./年]\d{1,2}[-./月]\d{1,2}日?", " ", body)  # 完整日期
    if item_date:
        allowed |= numbers(item_date.replace("-", " "))
    missing = sorted(n for n in numbers(body) - allowed if len(n.replace(".", "")) >= 2)
    if missing:
        errs.append(f"{label}: 这些数字在原文里找不到（编造/算错/没换算声明）: {', '.join(missing[:8])}")
    # 时效：以原文发布日为准，不信模型填的 date
    if not published and max_age < 10**6:
        errs.append(f"{label}: 所有来源都确认不了发布日期 — 补一个带日期的来源（官方公告/媒体报道）")
    if published:
        newest = max(p for p, _ in published)
        age = _days(date, newest)
        if age is not None and age > max_age:
            errs.append(f"{label}: 原文发布于 {newest}，距 {date} 已 {age} 天（上限 {max_age}）— 旧闻")
        if item_date:
            diff = _days(item_date, newest)
            if diff is not None and abs(diff) > 1 and all(abs(_days(item_date, p) or 99) > 1 for p, _ in published):
                errs.append(f"{label}: date={item_date} 与原文发布日 {sorted(p for p, _ in published)} 对不上")
    return errs


def check_briefing(path, date):
    sec = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    sid = sec.get("id", "?")
    max_age = MAX_AGE.get(f"briefing:{sid}", 3)
    errs = []
    for n, it in enumerate(sec.get("items") or [], 1):
        src_urls = [s.get("url", "") for s in it.get("sources") or []]
        ev_urls = {norm_url(e.get("url", "")) for e in it.get("evidence") or []}
        for u in src_urls:
            if norm_url(u) not in ev_urls:
                rec, _ = lookup(u, date)
                if not rec:
                    errs.append(f"{sid}[{n}]: sources 里的链接没抓过: {u}")
        errs += check_unit(f"{sid}[{n}]", [it.get("title", ""), it.get("summary", "")], it.get("evidence"),
                           it.get("derived"), date, max_age, it.get("date"), extra_urls=src_urls)
    # 分页主线 summary：只能复述条目里已有的事实，数字必须出现在条目里
    item_text = " ".join(f"{it.get('title', '')} {it.get('summary', '')} " +
                         " ".join(d.get("value", "") for d in it.get("derived") or [])
                         for it in sec.get("items") or [])
    extra = sorted(n for n in numbers(re.sub(r"^\s*\d{1,2}/\d{1,2}", " ", sec.get("summary", "")))
                   - numbers(item_text) if len(n.replace(".", "")) >= 2)
    if extra:
        errs.append(f"{sid}.summary: 主线里的数字在条目中找不到: {', '.join(extra[:8])}")
    return errs


def check_tietu(path, date):
    p = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    texts = [p.get("title", ""), p.get("subtitle", ""), p.get("hook", "")] + list(p.get("facts") or [])
    texts += [r.get("note", "") for c in (p.get("line_cards") or []) for r in c.get("rows", [])]
    # evergreen: 非新闻类（一张图/老知识），不做时效检查，但来源必须仍是本次抓取的原文
    max_age = 10**6 if p.get("evergreen") else MAX_AGE["tietu"]
    return check_unit(p.get("id", "post"), texts, p.get("evidence"), p.get("derived"), date, max_age)


def _md_body(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    return re.sub(r"```.*?```", " ", md, flags=re.S)


def check_longform(path, date):
    """path = 长文 .md；同目录 evidence.json = {"<文件名>": {"evidence": [...], "derived": [...]}}。"""
    path = pathlib.Path(path)
    ev_all = json.loads((path.parent / "evidence.json").read_text(encoding="utf-8")) \
        if (path.parent / "evidence.json").exists() else {}
    ev = ev_all.get(path.name) or {}
    body = _md_body(path.read_text(encoding="utf-8"))
    links = [u for u in re.findall(r"\]\((https?://[^)\s]+)\)", body) if not re.search(r"\.(png|jpe?g|gif|webp)$", u)]
    errs = []
    for u in links:
        rec, _ = lookup(u, date)
        if not rec:
            errs.append(f"{path.name}: 文中链接没抓过: {u}")
        elif not rec.get("ok"):
            errs.append(f"{path.name}: 文中链接不可用（{rec.get('reason')}）: {u}")
    errs += check_unit(path.name, [body], ev.get("evidence"), ev.get("derived"), date, 10**6, extra_urls=links)
    # 简报头条：每个 ### 小节按自己的来源单独查时效
    if path.name.startswith("a-"):
        for sec in re.split(r"\n(?=### )", body)[1:]:
            head = sec.splitlines()[0][4:40]
            dates = [lookup(u, date)[0].get("published") for u in re.findall(r"\]\((https?://[^)\s]+)\)", sec)
                     if lookup(u, date)[0]]
            dates = [d for d in dates if d]
            if dates and (_days(date, max(dates)) or 0) > MAX_AGE["longform"]:
                errs.append(f"{path.name} 「{head}」: 来源发布于 {max(dates)} — 旧闻")
    return errs


CHECKERS = {"briefing": check_briefing, "tietu": check_tietu, "longform": check_longform}


def cmd_check(date, kind, files):
    errs = []
    for f in files:
        errs += CHECKERS[kind](f, date)
    print("\n".join(errs) if errs else f"GROUNDED OK: {', '.join(map(str, files))}")
    return 1 if errs else 0


# ------------------------------------------------------------------ independent review
# 独立核对用的模型：必须与写稿模型异构（避免同模型自审盲区）
REVIEW_MODEL = os.environ.get("GROUNDING_REVIEW_MODEL", "gpt-4.1")
REVIEW_PROVIDER = os.environ.get("GROUNDING_REVIEW_PROVIDER", "")
REVIEW_PROMPT = """你是事实核查员，只做一件事：判断【成稿】里的每个事实性说法，是否能被【原文】直接支持。
规则：
- 只看原文，不要用你自己的知识补充或纠正。原文没说的，就是"无依据"。
- 重点抓：数字/日期/人名/机构写错或张冠李戴；原文没有的说法；把旧事写成新发生；夸大（"首个""全面超越"等原文没有的程度词）；把预告/传闻写成事实。
- 评论性判断不算事实，跳过：以「判断：」「我的判断是」开头的句子、趋势预测、建议，都是作者观点；只核其中夹带的具体事实（数字、名称、事件）。
- 日期：每篇原文开头的【元数据】给出了抓取时识别的发布日期，成稿的「日期」和「M/D 来源：」前缀以它为准，相差 1 天以内算正确。
- 原文是网页抓取的，可能截断或缺页眉；某说法在任何一篇原文里都找不到，才算无依据。
- 轻微意译、合理概括、通俗换算（"快了一倍"对应原文 2x）不算问题。
- 口语化的场景引子（如「最近和朋友聊到…」）、提问、话题标签不算事实，跳过；但不能编造产品体验（"我试了…"）。
- 原文的标题、导语、副标题都算原文内容。
- severity 分级：high = 事实错误（数字/日期/主体写错、张冠李戴、原文完全没有的说法、把旧事写成新事、把传闻/计划写成已发生）；low = 措辞不够精确、省略了不改变结论的限定语、概括略有偏差。拿不准就判 low。
只输出 JSON：{"ok": true/false, "issues": [{"claim": "成稿原句片段", "problem": "哪里不对", "severity": "high|low"}]}
有任何 high 就 ok=false。"""


def _provider_candidates():
    """返回可用核对源列表 [(base_url, api_key, model)]（不打印密钥）。
    优先读取环境变量 GROUNDING_REVIEW_BASE_URL + GROUNDING_REVIEW_API_KEY（或 OPENAI_BASE_URL + OPENAI_API_KEY），
    其次读取 ~/.hermes/config.yaml 中由 GROUNDING_REVIEW_PROVIDER 指定的 provider 或任意带 base_url+api_key 的 provider。"""
    out = []
    env_mod = os.environ.get("GROUNDING_REVIEW_MODEL") or REVIEW_MODEL
    env_base = os.environ.get("GROUNDING_REVIEW_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    env_key = os.environ.get("GROUNDING_REVIEW_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if env_base and env_key:
        out.append((env_base.rstrip("/"), env_key, env_mod))
    cfg_path = pathlib.Path.home() / ".hermes/config.yaml"
    if cfg_path.exists():
        try:
            import yaml
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
        except ImportError:
            cfg = {}
        env_prov = os.environ.get("GROUNDING_REVIEW_PROVIDER") or REVIEW_PROVIDER
        provs = cfg.get("providers") or {}
        cprovs = {cp.get("name"): cp for cp in (cfg.get("custom_providers") or []) if isinstance(cp, dict)}
        if env_prov:
            p = provs.get(env_prov) or cprovs.get(env_prov) or {}
            base = p.get("api") or p.get("base_url")
            if base and p.get("api_key"):
                out.append((base.rstrip("/"), p["api_key"], env_mod))
        for p in list(cprovs.values()) + list(provs.values()):
            if not isinstance(p, dict):
                continue
            base = p.get("api") or p.get("base_url")
            key = p.get("api_key")
            if base and key:
                cand = (base.rstrip("/"), key, env_mod)
                if cand not in out:
                    out.append(cand)
    if not out:
        raise RuntimeError("无可用核对源：请设置 GROUNDING_REVIEW_BASE_URL + GROUNDING_REVIEW_API_KEY 或配置 ~/.hermes/config.yaml")
    return out


def _ask_reviewer(draft, sources):
    per = max(20000, 160000 // max(1, len(sources)))  # 原文常带大段 cookie/导航，给足长度，避免把正文后半截掉
    src = "\n\n".join(f"=== 原文 {i + 1}: {u}\n【元数据】发布日期：{(lookup(u, _REVIEW_DATE)[0] or {}).get('published') or '未知'}"
                        f"\n{t[:per]}" for i, (u, t) in enumerate(sources))
    last_err = None
    for base, key, model in _provider_candidates():
        body = {"model": model, "max_tokens": 2000,
                "messages": [{"role": "system", "content": REVIEW_PROMPT},
                             {"role": "user", "content": f"【原文】\n{src}\n\n【成稿】\n{draft}"}]}
        req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                              "User-Agent": "hermes-agent"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                out = json.loads(r.read().decode())
            txt = out["choices"][0]["message"].get("content") or ""
            m = re.search(r"\{.*\}", txt, re.S)
            if m:
                return json.loads(m.group(0))
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    if last_err:
        raise last_err
    return {"ok": False, "issues": [{"claim": "", "problem": "核查输出无法解析", "severity": "high"}]}


def _units(kind, path, date):
    """把文件拆成 (label, 成稿文本, [(url, 原文)])。"""
    path = pathlib.Path(path)
    data = path.read_text(encoding="utf-8")
    units = []

    def srcs(urls):
        out, seen = [], set()
        for u in urls:
            if u and norm_url(u) not in seen:
                seen.add(norm_url(u))
                rec, t = lookup(u, date)
                if t:
                    out.append((u, t))
        return out

    if kind == "briefing":
        sec = json.loads(data)
        digest = "\n\n".join(f"条目{n}（{it.get('date')}）：{it.get('title')}\n{it.get('summary')}"
                               for n, it in enumerate(sec.get("items") or [], 1))
        wd = "一二三四五六日"[dt.date.fromisoformat(date).weekday()]
        digest = f"本期简报日期：{date}（周{wd}）。主线开头的「周X主线」指本期日期。\n\n" + digest
        units.append((f"{sec.get('id')}.summary", sec.get("summary", ""), [("（本分页已核对过的条目）", digest)]))
        for n, it in enumerate(sec.get("items") or [], 1):
            urls = [e.get("url") for e in it.get("evidence") or []] + [s.get("url") for s in it.get("sources") or []]
            units.append((f"{sec.get('id')}[{n}]", f"日期：{it.get('date')}\n{it.get('title')}\n{it.get('summary')}",
                          srcs(urls)))
    elif kind == "tietu":
        p = json.loads(data)
        draft = "\n".join([p.get("title", ""), p.get("subtitle", ""), p.get("hook", "")] + list(p.get("facts") or [])
                          + [json.dumps(p.get("take"), ensure_ascii=False), p.get("caption", "")])
        units.append((p.get("id"), draft, srcs([e.get("url") for e in p.get("evidence") or []])))
    else:
        body = _md_body(data)
        ev = {}
        if (path.parent / "evidence.json").exists():
            ev = json.loads((path.parent / "evidence.json").read_text(encoding="utf-8")).get(path.name) or {}
        urls = [e.get("url") for e in ev.get("evidence") or []] + re.findall(r"\]\((https?://[^)\s]+)\)", body)
        units.append((path.name, body, srcs(urls)))
    return units


_REVIEW_DATE = today()


def cmd_review(date, kind, files):
    global _REVIEW_DATE
    _REVIEW_DATE = date
    from concurrent.futures import ThreadPoolExecutor
    units = [u for f in files for u in _units(kind, f, date)]

    def one(unit):
        label, draft, sources = unit
        if not sources:
            return False, f"FAIL {label}: 没有可用原文，无法核对"
        try:
            res = _ask_reviewer(draft, sources)
        except Exception as e:  # noqa: BLE001
            return False, f"ERROR {label}: 核对调用失败 {e}"
        highs = [i for i in res.get("issues") or [] if i.get("severity") == "high"]
        if highs or not res.get("ok", False):
            return False, f"FAIL {label}:" + "".join(f"\n    - 「{i.get('claim', '')[:60]}」{i.get('problem')}"
                                                   for i in (highs or res.get("issues") or []))
        lows = res.get("issues") or []
        return True, f"OK   {label}" + ("".join(f"\n    · 轻微：{i.get('problem')}" for i in lows) if lows else "")

    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(one, units))
        # 核对模型有随机性：FAIL 的单元再独立核一次，两次都 FAIL 才算失败（真错误基本都能复现）
        again = [i for i, (ok, line) in enumerate(results) if not ok and line.startswith("FAIL")]
        for i, res in zip(again, ex.map(one, [units[i] for i in again])):
            if res[0]:
                results[i] = (True, results[i][1].replace("FAIL", "OK? ", 1) + "\n    （复核通过：第一次判 FAIL，第二次判 OK，按通过处理但请留意）")
    bad = sum(1 for ok, _ in results if not ok)
    report = [line for _, line in results]
    log = store_dir(date) / "review.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## {dt.datetime.now(TZ).isoformat(timespec='seconds')} {kind} {' '.join(map(str, files))}\n"
                 + "\n".join(report) + "\n")
    print("\n".join(report))
    print(f"REVIEW {'FAILED' if bad else 'PASSED'}: {bad} 条有问题（日志 {log}）")
    return 1 if bad else 0


QUEUE = pathlib.Path.home() / "Library/CloudStorage/Dropbox/Obsidian Vault/05-Outputs/content-creator/queue"
BRIEFING_DATA = pathlib.Path.home() / "HermesWork/personal/news/neuma-briefing/data"


def cmd_audit(date, n=5):
    """事后抽查：从 DATE 已产出的简报条目 / 贴图 / 长文里随机抽 n 个单元，重跑硬检查 + 独立核对。"""
    import random
    pool = []  # (kind, file, label)
    for sid in ("ai", "women40", "pharma"):
        f = BRIEFING_DATA / f"{date}.{sid}.json"
        if f.exists():
            for i, _ in enumerate(json.loads(f.read_text(encoding="utf-8")).get("items") or [], 1):
                pool.append(("briefing", f, f"{sid}[{i}]"))
    for f in sorted((QUEUE / "tietu" / date).glob("*/post.json")):
        pool.append(("tietu", f, json.loads(f.read_text(encoding="utf-8")).get("id", f.parent.name)))
    for d in sorted((QUEUE / "longform").glob(f"{date}*")):
        for f in sorted(d.glob("[abc]-*.md")):
            pool.append(("longform", f, f"{d.name}/{f.name}"))
    if not pool:
        print(f"AUDIT {date}: 没有可抽查的产出")
        return 0
    random.seed(f"audit-{date}")
    picks = random.sample(pool, min(n, len(pool)))
    lines, bad = [f"# 依据抽查 {date}（{len(picks)}/{len(pool)} 个单元）", ""], 0
    for kind, f, label in picks:
        if kind == "briefing":
            errs = [e for e in check_briefing(f, date) if e.startswith(label + ":")]
            units = [u for u in _units(kind, f, date) if u[0] == label]
        elif kind == "tietu":
            errs, units = check_tietu(f, date), _units(kind, f, date)
        else:
            errs, units = check_longform(f, date), _units(kind, f, date)
        rev = []
        for lab, draft, sources in units:
            if not sources:
                rev.append("无可用原文，无法核对")
                continue
            try:
                r = _ask_reviewer(draft, sources)
                rev += [f"{i.get('severity')}: 「{i.get('claim', '')[:50]}」{i.get('problem')}" for i in r.get("issues") or []
                        if i.get("severity") == "high"]
            except Exception as e:  # noqa: BLE001
                rev.append(f"核对调用失败 {e}")
        ok = not errs and not rev
        bad += not ok
        lines.append(f"- {'OK  ' if ok else 'FAIL'} [{kind}] {label}")
        lines += [f"    · 硬检查：{e}" for e in errs[:5]] + [f"    · 核对：{x}" for x in rev[:5]]
    lines.append(f"\n结论：{bad}/{len(picks)} 个单元有问题")
    out = store_dir(date) / "audit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines) + f"\n（报告 {out}）")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["fetch", "image", "show", "check", "review", "audit"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--date", default=today())
    ap.add_argument("--kind", choices=list(CHECKERS))
    ap.add_argument("--text", help="image: 转录文本文件")
    ap.add_argument("--published", default="", help="image: 图片发布日期 YYYY-MM-DD（有可查依据时才填）")
    a = ap.parse_intermixed_args(argv)
    dt.date.fromisoformat(a.date)
    if a.cmd == "fetch":
        return cmd_fetch(a.date, a.args)
    if a.cmd == "image":
        if not (a.args and a.text):
            ap.error("image 需要 URL 和 --text")
        return cmd_image(a.date, a.args[0], a.text, a.published)
    if a.cmd == "audit":
        return cmd_audit(a.date, a.n)
    if not a.args:
        ap.error("需要 URL 或文件参数")
    if a.cmd == "show":
        return cmd_show(a.date, a.args[0])
    if not a.kind:
        ap.error("check/review 需要 --kind")
    return (cmd_check if a.cmd == "check" else cmd_review)(a.date, a.kind, a.args)


if __name__ == "__main__":
    sys.exit(main())
