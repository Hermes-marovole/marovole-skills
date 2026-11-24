# Has this Chinese book / volume actually been printed?

For "第N册 / 第N版 / 续编 / 全N册 — does it exist?" questions. Work the ladder top-down and stop at the first authoritative hit. Retail presence is the **weakest** witness, not the strongest: a listing can be a bundle, a pre-order, a pirated scan of volume 1 under a volume-3 title, or 内容简介 boilerplate frozen since the first edition.

The answer the user wants is a verdict plus its evidence, not a search log. When the volume does not exist, say that in the first line and then hand over what does exist.

## Ladder

### 1. The publisher's own downloadable catalog — decisive

Chinese academic and medical presses publish their full backlist as a spreadsheet, and a full backlist keeps decade-old titles, so **absence is real absence**, not pruning. Zero rows for the volume settles it.

北京大学医学出版社 (pumpress.com) — index of catalog downloads:

```
https://www.pumpress.com/download/booklist/%e4%b9%a6%e7%9b%ae/
```

Fetch the index, pull every `.xls` href, take the newest by the date embedded in the filename (`北医社书目全（更新至YYYY.M.D).xls`). Then confirm the file's real currency — the internal save date and the filename date can differ by days, and both should be recent:

```bash
file pumpress_all.xls   # → "Last Saved Time/Date: Mon Nov  9 ..."
```

Legacy BIFF `.xls` needs `xlrd` (not `openpyxl`):

```bash
python3 -m pip install --quiet xlrd
```

```python
import xlrd
sh = xlrd.open_workbook("pumpress_all.xls").sheet_by_index(0)
print(sh.nrows, [str(sh.cell_value(0, c)).strip() for c in range(sh.ncols)])
for r in range(1, sh.nrows):
    line = " | ".join(str(sh.cell_value(r, c)).strip() for c in range(sh.ncols))
    if "食物成分表" in line:
        print(r, line[:300])
```

Columns are 书名 / 版次·装帧 / ISBN / 作者 / 社内分类1-3 / 定价 / 出版时间 / 开本 / 册包 / 中图分类号 — so one query yields the whole authoritative row set (volume, ISBN, year, price) for the answer table.

Search the **series title**, then a second pass on the content-type keyword the missing volume would be named for (加工食品, 水产, 碘…) to catch a differently-titled replacement.

### 2. Publisher's monthly 新书单 — good negative evidence

`bynews.bjmu.edu.cn` and `chyb.bjmu.edu.cn`, "北医新书单│<月>，这些新著与您相见". The retrospective issues that re-introduce a house's classic series enumerate its volumes explicitly; a series retrospective that lists volumes and omits the one in question is real evidence. These also reveal **what the press published instead** — a 专题册 (single-topic monograph) appearing where a planned 分册 was expected is the signal that the 分册 was replaced, not delayed.

### 3. Institutional award / grant disclosures — enumerations of 专著

`chinacdc.cn` 中华预防医学会科学技术奖 project 公示 PDFs carry a "主要支撑材料目录" table that itemises "专著 N 部" by title. A team's own complete monograph list, filed to claim credit, that omits the volume is strong negative evidence — stronger than anything retail says.

### 4. Library / union catalogue — CIP-grade metadata

- NDL `ndlsearch.ndl.go.jp` — good for Chinese medical/technical books, and the 一般注記 field often records *which printing* the record describes ("記述は第7次印刷 (2024.3)による"), which dates the run.
- University OPACs and 网上馆配会 (`tsxcfw.com`) — 题名/责任者, ISBN, 定价, 版次, 中图法分类号, 附注.
- 缺书网 (`queshu.com`) — existence and price history when a title looks out of print.

### 5. 豆瓣 丛书 field — fast count check

A douban series box prints `中国食物成分表(共2册)`. Useful as a one-second sanity check on how many 分册 the series actually contains; not authoritative alone.

## Traps that manufacture false positives

- **Frozen 内容简介 boilerplate.** The blurb is written for volume 1 and copied verbatim into every sibling listing forever. "共三个分册…第三册也即将与大家见面，敬请期待！" appearing on a page is evidence the page was written years ago, **not** evidence of an imminent third volume. Same for 页数/印张/字数/定价 quoted off a listing.
- **"全N册" on 淘宝/天猫 is usually a bundle.** Read the long detail-page title or the 苏宁/京东 copy for what is actually inside — "全3册" routinely decomposes into 《中国居民膳食指南》 plus the two volumes you were already going to buy. A bundle does not add a volume to the series.
- **AI-generated aggregators fabricate editions and years.** Sites that exist to farm ebook-download keywords (baidu health answer pages, `onlinetoolsland`, `qciss.net`, and 加速器/keyword-spam domains with the book title in the URL path) invent "第6版（2023年更新）", invent a split like "标准版 and 深加工食品版", and reflow the real blurb into plausible prose. Never cite them for edition, year, or volume count.
- **A forum thread asking where volume N is** is a legitimate signal — the answer usually names the current substitute (an official database, a 专题册) and dates the question. Cite the answer, not the question.
- **"No scan found" is not "not published".** Absence from libgen/Anna's/archive.org is the normal state for a recent Chinese print reference. Answer the publication question from the catalog ladder above and keep the file-sourcing answer separate.

## Answer shape

Lead with the verdict in one line (published / not published / published but not as a separate volume). Then the evidence as a compact table or numbered list, strongest witness first, each with the file or URL you actually opened. Then the two or three things that made the web look otherwise (stale boilerplate, bundle listings, AI aggregators), then the practical substitute if the volume is missing. Do not narrate the search.
