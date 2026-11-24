"""markdown → single-page HTML report builder (调研报告 浅色一页到底).

Copy this next to the report, edit the CONFIG block, run it. It renders:
  * a header with title / meta lines / KPI card grid (from a table whose first
    column is the metric name)
  * "核心判断" as coloured verdict cards (from N. **bold title** + body lines)
  * every `##` section, `###` subsection, pipe table, blockquote, bullet and
    ordered list
  * inline `[n]` citations as superscript anchors into a numbered 信源台账
  * screenshot galleries injected under chosen `###` headings
  * a final verification pass: missing images, unmatched anchors, leftover
    `{{placeholder}}` residue — all three must be zero before delivery.

Design contract for this user: light background, one page to the end, no dark
mode, no printed meta-narrative labels, generous line-height, tables readable
at 13.6px. Keep the CSS block intact rather than restyling per report.
"""

import html
import os
import re

# --------------------------------------------------------------------------- #
# CONFIG — edit these four things per report
# --------------------------------------------------------------------------- #
ROOT = "/Users/marovole/HermesWork/reports/YYYY-MM-DD-<slug>"
MD_NAME = "<slug>-research-v1.0.md"
HTML_NAME = "<slug>-research-v1.0.html"
EVIDENCE_REL = "evidence"  # dir under ROOT holding the .png evidence

# Galleries keyed by the START of the `###` heading they follow.
# Each value is raw HTML so captions can be written per shot.
GALLERIES = {
    # "1.2 ": f"""
    # <div class="shot-grid">
    #   <div class="shot-card"><img src="{EVIDENCE_REL}/01_launch.png" alt="...">
    #     <div class="shot-cap">what this frame proves</div></div>
    # </div>""",
}

CSS = """
:root {
  --bg:#f8fafc; --card:#fff; --text:#0f172a; --muted:#475569; --light:#64748b;
  --border:#e2e8f0; --accent:#059669; --accent-soft:#ecfdf5; --accent-border:#a7f3d0;
  --blue:#2563eb; --danger:#dc2626; --danger-soft:#fef2f2; --danger-border:#fecaca;
}
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB",
       "Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text);
       line-height:1.72; padding:32px 20px 72px; }
.container { max-width:1040px; margin:0 auto; }
header { background:var(--card); border:1px solid var(--border);
         border-top:4px solid var(--accent); border-radius:12px;
         padding:28px 32px; margin-bottom:24px;
         box-shadow:0 1px 3px rgba(15,23,42,.04); }
h1 { font-size:26px; font-weight:700; letter-spacing:-.01em; margin-bottom:10px; }
.subtitle { color:var(--muted); font-size:14px; line-height:1.65; }
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr));
            gap:14px; margin-top:22px; }
.kpi-card { background:#f8fafc; border:1px solid var(--border);
            border-radius:8px; padding:14px 16px; }
.kpi-label { font-size:12px; color:var(--light); font-weight:600; margin-bottom:4px; }
.kpi-val { font-size:21px; font-weight:700; color:var(--accent); margin-bottom:4px; }
.kpi-sub { font-size:12.5px; color:var(--muted); line-height:1.5; }
section { background:var(--card); border:1px solid var(--border); border-radius:12px;
          padding:26px 32px; margin-bottom:22px;
          box-shadow:0 1px 2px rgba(15,23,42,.03); }
h2 { font-size:20px; font-weight:700; margin-bottom:16px; padding-bottom:10px;
     border-bottom:1px solid var(--border); }
h3 { font-size:16.2px; font-weight:700; margin:20px 0 10px; color:#1e293b; }
p { margin-bottom:12px; font-size:14.8px; color:#1e293b; }
ul,ol { padding-left:22px; margin-bottom:14px; }
li { margin-bottom:8px; font-size:14.6px; color:#1e293b; }
blockquote { background:#f8fafc; border-left:4px solid var(--blue);
             padding:12px 16px; margin:12px 0 16px; color:#334155;
             font-size:14px; border-radius:0 8px 8px 0; }
.verdict-card { background:var(--accent-soft); border:1px solid var(--accent-border);
                border-radius:10px; padding:16px 20px; margin-bottom:14px; }
.verdict-card.warn { background:var(--danger-soft); border-color:var(--danger-border); }
.verdict-card h4 { font-size:15.5px; font-weight:700; margin:0 0 6px; color:var(--text); }
.verdict-card p { margin-bottom:0; font-size:14.3px; color:#334155; }
table { width:100%; border-collapse:collapse; margin:14px 0 18px; font-size:13.6px; }
th,td { border:1px solid var(--border); padding:10px 12px; text-align:left; vertical-align:top; }
th { background:#f1f5f9; font-weight:600; color:#0f172a; }
tr:nth-child(even) td { background:#fcfcfd; }
code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.8px;
       background:#f1f5f9; padding:2px 6px; border-radius:4px; }
a { color:var(--blue); text-decoration:none; }
a:hover { text-decoration:underline; }
a.cite { font-size:11.8px; font-weight:600; vertical-align:super; margin:0 1px; }
.shot-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(205px,1fr));
             gap:14px; margin:16px 0 10px; }
.shot-card { border:1px solid var(--border); border-radius:8px; overflow:hidden;
             background:#f8fafc; }
.shot-card img { width:100%; height:auto; display:block;
                 border-bottom:1px solid var(--border); }
.shot-cap { padding:8px 10px; font-size:12.2px; color:var(--muted); line-height:1.45; }
.ref-item { padding:8px 10px; border-bottom:1px solid var(--border);
            font-size:13px; color:var(--muted); word-break:break-all; }
.ref-item:last-child { border-bottom:none; }
"""


def fmt(text: str) -> str:
    """Inline markdown → HTML. Escapes first, then re-applies only our own tags."""
    text = text.replace("<br>", "\x00BR\x00")
    s = html.escape(text).replace("\x00BR\x00", "<br>")
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`(https?://[^`]+)`", r'<a href="\1" target="_blank">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # [n] → superscript anchor, but never touch the [^n] footnote form
    s = re.sub(r"(?<!\^)\[(\d+)\]", r'<a class="cite" href="#ref-\1">[\1]</a>', s)
    return s


def render_table(lines: list) -> str:
    rows = []
    for i, ln in enumerate(lines):
        if i == 1 and re.match(r"^\|[\s:\-\|]+\|$", ln.strip()):
            continue  # alignment separator
        rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
    if not rows:
        return ""
    out = ["<table><thead><tr>"]
    out += [f"<th>{fmt(h)}</th>" for h in rows[0]]
    out.append("</tr></thead><tbody>")
    for r in rows[1:]:
        out.append("<tr>" + "".join(f"<td>{fmt(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_section(sec_md: str, is_sources: bool = False) -> str:
    lines = sec_md.strip().splitlines()
    out, i, gallery_key = ["<section>"], 0, None
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("## "):
            out.append(f"<h2>{fmt(s[3:])}</h2>")
            i += 1
        elif s.startswith("### "):
            if gallery_key and gallery_key in GALLERIES:
                out.append(GALLERIES.pop(gallery_key))
            title = s[4:]
            gallery_key = next((k for k in GALLERIES if title.startswith(k)), None)
            out.append(f"<h3>{fmt(title)}</h3>")
            i += 1
        elif s.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buf.append(lines[i])
                i += 1
            out.append(render_table(buf))
        elif s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{fmt('<br>'.join(buf))}</blockquote>")
        elif is_sources and re.match(r"^\d+\.\s+\*\[\[?(\d+)\]", s):
            rid = re.search(r"\[(\d+)\]", s).group(1)
            body = fmt(re.sub(r"^\d+\.\s+", "", s))
            body = body.replace(f'<a class="cite" href="#ref-{rid}">[{rid}]</a>', f"[{rid}]", 1)
            out.append(f'<div id="ref-{rid}" class="ref-item">{body}</div>')
            i += 1
        elif s.startswith("- ") or re.match(r"^\d+\.\s+", s):
            is_ol = bool(re.match(r"^\d+\.\s+", s))
            tag = "ol" if is_ol else "ul"
            out.append(f"<{tag}>")
            while i < len(lines):
                li_s = lines[i].strip()
                matches = (re.match(r"^\d+\.\s+", li_s) if is_ol
                           else li_s.startswith("- "))
                if matches:
                    item = re.sub(r"^(?:-\s+|\d+\.\s+)", "", li_s)
                    i += 1
                    while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                        cont = lines[i].strip()
                        item += "<br>" + cont.lstrip(">- ").strip()
                        i += 1
                    out.append(f"<li>{fmt(item)}</li>")
                elif not li_s:
                    i += 1
                    break
                else:
                    break
            out.append(f"</{tag}>")
        else:
            out.append(f"<p>{fmt(s)}</p>")
            i += 1
    if gallery_key and gallery_key in GALLERIES:
        out.append(GALLERIES.pop(gallery_key))
    out.append("</section>")
    return "\n".join(out)


def build():
    md = open(os.path.join(ROOT, MD_NAME), encoding="utf-8").read()
    chunks = re.split(r"\n---\n", md)

    # chunk 0 = title block; chunk 1 = 核心判断 (verdicts + KPI table)
    verdict_md = chunks[1].strip().splitlines()
    tbl_at = next((i for i, l in enumerate(verdict_md) if l.startswith("|")), len(verdict_md))

    kpi_rows = [l for l in verdict_md[tbl_at + 2:] if l.startswith("|")]
    kpi_html = []
    for row in kpi_rows:
        c = [x.strip() for x in row.strip().strip("|").split("|")]
        if len(c) < 3:
            continue
        kpi_html.append(
            f'<div class="kpi-card"><div class="kpi-label">{html.escape(c[0].replace("**", ""))}</div>'
            f'<div class="kpi-val">{html.escape(c[1].replace("**", ""))}</div>'
            f'<div class="kpi-sub">{fmt(c[2])}</div></div>'
        )

    verdicts, cur = [], None
    for line in verdict_md[:tbl_at]:
        m = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s*$", line.strip())
        if m:
            if cur:
                verdicts.append(cur)
            cur = {"n": int(m.group(1)), "t": m.group(2), "body": []}
        elif cur and line.strip():
            cur["body"].append(line.strip())
    if cur:
        verdicts.append(cur)
    verdict_html = [
        f'<div class="verdict-card{" warn" if v["n"] >= 3 else ""}">'
        f'<h4>{v["n"]}. {fmt(v["t"])}</h4><p>{fmt(" ".join(v["body"]))}</p></div>'
        for v in verdicts
    ]

    body = "".join(
        render_section(sec, is_sources=(idx == len(chunks) - 1))
        for idx, sec in enumerate(chunks[2:], start=2)
    )

    title = md.splitlines()[0].lstrip("# ").strip()
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><div class="container">
<header><h1>{html.escape(title)}</h1>
<div class="subtitle">{fmt(' ｜ '.join(x.strip() for x in chunks[0].splitlines()[1:] if x.strip()))}</div>
<div class="kpi-grid">{''.join(kpi_html)}</div></header>
<section><h2>核心判断</h2>{''.join(verdict_html)}</section>
{body}
</div></body></html>"""

    out_path = os.path.join(ROOT, HTML_NAME)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_path


def verify(out_path: str):
    """Block delivery unless images resolve, anchors match, and no placeholders leak."""
    ht = open(out_path, encoding="utf-8").read()
    md = open(os.path.join(ROOT, MD_NAME), encoding="utf-8").read()
    imgs = re.findall(r'src="([^"]+)"', ht)
    missing = [i for i in imgs if not os.path.exists(os.path.join(ROOT, i))]
    hrefs = {int(x) for x in re.findall(r'href="#ref-(\d+)"', ht)}
    ids = {int(x) for x in re.findall(r'id="ref-(\d+)"', ht)}
    residue = re.findall(r"\{\{[^}]+\}\}", md + ht)
    print(f"images={len(imgs)} missing={missing}")
    print(f"anchors={len(ids)} unmatched={hrefs - ids}")
    print(f"placeholders={residue}")
    assert not missing and not (hrefs - ids) and not residue, "report not clean — fix before delivering"


if __name__ == "__main__":
    verify(build())
