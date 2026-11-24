---
name: book-and-pdf-sourcing
description: "Find books; verify files; deliver PDF, EPUB or 中文版."
version: 1.6.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [books, textbooks, pdf, ebook, internet-archive, sourcing, download]
    category: research
---

# Book & PDF Sourcing

## When to Use

Load when the user names a book and wants it: "帮我找一下这本书", "find this book", "get me the PDF of X", a bare textbook title with no author or edition, or a request for the Chinese translation of a technical classic. Also load when a download card must be handed over and its completeness has to be proven.

The ask often escalates one turn at a time — find it → "我要 epub 版本的" → "用英文原版翻译成中文的 epub 版本给我". Sourcing is only steps 1–5; when no acceptable Chinese edition exists, step 6 is to build one from the original yourself instead of re-searching for a translation.

User names a book (often a Chinese-rendered title, often abbreviated, no author). Goal: identify the work, pick the right edition, put full-text files on disk, verify they are real, and hand over paths — not links the user has to chase.
## Procedure

### 1. Resolve the title to the canonical work

Chinese users cite the *literal translation*, which is frequently not the published Chinese title. Map three things before searching:

- **English original** + authors (the actual searchable key).
- **Official Chinese edition** (publisher, translator, ISBN) — needed for the print/bookstore answer.
- **Colloquial names** — many classics are referred to by author pair ("Hennessy and Patterson") or by the literal translation.

Confirm with one search of the Chinese string plus the likely English title; a single hit on a course-resource page or a bookseller listing gives you authors, translator, ISBN and edition in one shot.

**A title that reads like a table is a table inside a bigger reference book.** "<subject> <count> 种" (490种食物嘌呤含量, 800种野菜图谱…) is a 表/章 of a standard work, not a standalone title — resolve which book's table that count belongs to, answer with 书名/主编/出版社/ISBN plus the exact 表 number and printed page range, and deliver that page range as its own small PDF next to the whole book. Someone asking for one table will not scroll a 450-page scan to find it.

**A planned 分册 is not a published 分册.** Series blurbs, douban 内容简介 and every retail page copy the plan as first written and never revise it, so "共三个分册…第三册也即将与大家见面，敬请期待" keeps circulating a decade after two volumes shipped and the third was abandoned. When the user names a volume or an edition number, prove it is in print against the publisher's own catalog before sourcing anything or listing it as purchasable — ladder, sources and commands: `references/chinese-book-publication-status.md`. "I found no scan of it" is not an answer to "has it been printed?"; when the answer is no, lead with that, then hand over the volumes that exist.

### 2. Decide which editions to deliver

Deliver **latest original-language edition** + **latest available Chinese translation**, and say plainly what differs (revision, changed ISA/spec, added chapters). Do not silently hand over an old edition when a newer one exists — but do hand over the older one if that is the only translation: a translated edition one revision behind beats no Chinese at all.

### 3. Search order for full text

**Check the publication date first, before any searching.** Shadow-library corpora are user-uploaded and lag the market by months to years: a title published this year — new trade nonfiction, an indie or university press book, a fresh edition — is usually not there at all, and three empty searches tell you nothing about whether the book exists. One look at the publisher/bookseller listing gives the release date and, for a digital-first release, the ASIN/ISBN/ISBN-13 you need for the answer anyway. When the date is recent, say so up front — but recent is not the same as absent. Retail EPUBs of trade titles reach libgen/Anna's within months, so check whether the row exists (and its upload date) before routing to the purchase answer. A row that exists is still not a file: libgen's CDN routinely `500`s on indexed records ("File not found in DB") while the same-MD5 copy on Anna's serves fine, so a dead libgen download goes to step 6, never to "not available".

1. `site:archive.org <english title> <edition>` — item pages expose direct file downloads.
2. `site:github.com "<chinese title>"` and university course-resource mirrors ("课程攻略", "icicles" style) — these carry the textbooks *plus* official slides, appendices and solution manuals.
3. Community translation projects for appendices the print edition cut (GitBook/GitHub).
4. `filetype:pdf` on the bare title.
5. `libgen.bz` for Chinese scans — 读秀 (duxiu) dumps of mainland textbooks that archive.org never holds. Four requests, no countdown, no account: `index.php?req=` → `edition.php?id=` → `ads.php?md5=` → `get.php?md5=&key=`. It indexes the same files as Anna's Archive (identical MD5), so take whichever serves. Chain, headers and per-step commands: the Library Genesis section of `references/full-text-book-sources.md`.
6. Anna's Archive `/md5/<hash>` for the same 读秀 corpus when libgen is down or a title only appears there. Mirror tiers and the file-identity check: see the Anna's Archive section of the reference below.

Source-specific URL shapes and what each one actually contains: `references/full-text-book-sources.md`.

Do **not** stop at a search-result description. A result describing a book proves the book exists, not that the file downloads.

### 4. Download, then verify the file is real

```bash
curl -I -L -s "<url>" | grep -Ei '(HTTP/|content-type|content-length)'
curl -L -s -o "$HOME/Downloads/<Title>_<Edition>_<lang>.pdf" "<url>"
file "$HOME/Downloads/<Title>_<Edition>_<lang>.pdf"
```

Three checks, all required before saying it worked:

- **`content-type`** on the final 200 must be `application/pdf` / `application/epub+zip` — an HTML content type means you downloaded a landing page or login wall.
- **`file` reports a page count** — e.g. `PDF document, version 1.4, 1527 pages`. A single-digit page count is a cover scan or preview stub, not the book.
- **Size sanity** — a full technical textbook is tens of MB. A few hundred KB is a stub.

For anything whose page count matters (is the appendix in there? is the scan complete?), read it rather than trusting `file`:

```bash
python3 -c "import pypdf,sys; print(len(pypdf.PdfReader(sys.argv[1]).pages))" file.pdf \
  || python3 -c "import fitz,sys; print(len(fitz.open(sys.argv[1])))" file.pdf
```

Compare against the known print page count before calling it complete.

An EPUB has no page count, so "is the whole book here" is four structural assertions read off the zip — file size proves nothing and a 700 KB retail EPUB can be the complete book:

```bash
md5 "$HOME/Downloads/<Title>.epub"   # must equal the hash in annas-arch-<hash>.epub / the /md5/ URL
python3 - <<'EOF'
import zipfile, re
z = zipfile.ZipFile(P)
print(z.namelist()[0], z.read('mimetype')[:20])          # mimetype first, application/epub+zip
print([n for n in z.namelist() if n.endswith('.opf')])    # then <dc:title>/<dc:creator>/<dc:publisher>/<dc:language>
ncx = z.read([n for n in z.namelist() if n.endswith('.ncx')][0]).decode('utf-8','ignore')
print('TOC', len(re.findall(r'<text[^>]*>', ncx)))        # compare to the real chapter list
EOF
```

- **MD5 equals the record hash** — for a retail EPUB that hash *is* the publisher's file, so a match proves identity, not just plausibility (unlike re-saved PDFs).
- **TOC entry count matches the published chapter list**, and the last spine document ends with acknowledgements/about-the-authors, not a stylesheet or license page.
- **Hundreds of thousands of characters of text** across the HTML files — a real text layer. An image-only `<img>` EPUB measures near zero; that is the scan case, not a stub.
- `dc:creator`/`dc:publisher` name the authors and press you are claiming in the handover.

**Take that page count from the book's own CIP page, not from a listing.** Publisher storefronts, library records and FAO catalogues disagree badly on Chinese multi-volume references — a publisher page can claim 229 页 for a 445-page volume — so 页数 / 印张 / 字数 / 定价 all get quoted off the CIP page you rendered, and a listing's number is never cited as the book's.

For a Chinese scan, "is it real" also means "is it the edition the user named". Open the copyright page (CIP 数据 / ISBN / 印次 / 定价) and the table of contents and quote them from the file itself: 著 vs 主编, the 印次 and the chapter list all differ between a 内部印本 and the 正式出版 edition, and the title the user hands you is frequently the wrong role or an abbreviated name. When the scan has no usable text layer, run `swift scripts/ocr_pages.swift <file.pdf> 1 18` — PDFKit + Vision, zh-Hans, no installs — instead of reaching for OCR tooling or eyeballing a contact sheet. `fitz.open(f).metadata` reporting `creator: Pdg2Pic` / `producer: FreePic2Pdf_Lib` identifies a 读秀 image dump outright: expect `get_text()` to return 0 chars on every page and plan the OCR before promising grep or quoting off the PDF. Use that OCR to **locate** pages, never to transcribe them: Vision mangles ordinary hanzi (的→前, 营养→营乔), so every number, ISBN digit and title you quote gets read off the rendered image yourself.

An EPUB whose pages are `<img>` tags and whose images are `index-N_1.jpg` inside the zip is a scan in a container, with no text layer at all; rebuild it to PDF first and pull the excerpt the user actually asked for — recipe, offsets and delivery shape: `references/scanned-epub-rebuild.md`.

### 5. Deliver as local files

- Save to `~/Downloads/`, name `Title_Edition_language.pdf` (title in the script the user reads; ASCII-only for the English original). No "终版/final/copy" suffixes — the filename already encodes edition and language.
- Hand over with `MEDIA:/absolute/path` so it renders as a card in the desktop app, one line per file, each with its page count and which edition it is.
- Attach the supplementary material the same way when it exists: solution manual, appendices, official slides — and say explicitly when the print edition *omits* something the community has translated.
- Close with the purchase options, and treat that as a real deliverable rather than an apology. Four lines, verified from listings you actually opened: **Kindle/Kobo** (ASIN or ISBN-13, and whether the EPUB carries Adobe DRM), **official free chapters** — academic and indie authors routinely publish 2–4 whole chapters free on their own site, which is often the only legitimate full text that exists and satisfies a "let me read it" ask, **publisher print page**, and **library**. Then ask which account to buy on instead of guessing. If the user wants an un-DRMed copy of a book they bought, Calibre + the DeDRM plugin converts an Adobe-DRM EPUB.
- **Name what you checked and that it came up empty, one clause each.** "Anna's/LibGen don't have it yet (published this year); the aggregator page exists but its file host is captcha-gated" is worth more than a bare "couldn't find it" — it tells the user the negative was established, not assumed.

### 6. When the user wants a Chinese version that does not exist: translate the original

If the only Chinese edition is years behind, or the user explicitly asks for the English original translated, do not keep hunting for a translation — build one from the EPUB you already verified. Full pipeline, prompt, packaging rules and QA checklist: `references/ebook-translation-pipeline.md`, runnable worker: `scripts/translate_epub.py`.

Shape of the job, in order:

1. **Work on the EPUB, not a PDF.** One HTML file per printed page keeps paragraphs, figure references and image links intact, so translation never has to re-flow layout. A PDF forces OCR + re-layout and loses fidelity for no gain.
2. **Translate at `<p>` granularity, never at file granularity.** Split each paragraph's inner HTML on tags and send only the text runs, so `<img>`, `<span>`, math and anchors survive untouched. Reassembling the whole file from the model's output is what destroys figures.
3. **Query the endpoint for a real model id before the batch.** Hit `/v1/models` on the local aggregator and use an id it actually lists; a guessed id fails on page 1 of 1500, mid-run.
4. **State on disk after every page.** A JSON progress set plus per-page writes means an interrupted 1500-page run resumes instead of restarting. Repackage the EPUB every ~100 pages so the user always holds a partially translated, openable book.
5. **Run it in the background and hand over the observability.** `terminal(background=true, notify=true)`, then give the log path and the `tail -f` command plus the current ETA. A single-page call is ~10 s; state the page count and the parallelism so the wait is legible.
6. **Spot-check one translated page before promising the whole book.** Read a translated file back and look for header bleed and dropped figures (see pitfalls), then decide.

## Pitfalls

- **Never OCR a Chinese number into your answer.** Vision output is good enough to find a page and useless as a transcription (的→前/韵, 营养→营乔); quotable text and every digit comes off the image you rendered, or off `pdftotext` on a real text layer.
- **An "EPUB" that is only `<img>` tags is a scan.** No text layer means no search, no grep, no quoting — rebuild to PDF (`references/scanned-epub-rebuild.md`) before promising a page range or a table extraction.
- **A 4-page or 1-page "PDF" means you got a stub.** `curl -I` showing `application/pdf` is not enough — check the page count every time. Silent delivery of a stub is the worst failure here because the card renders and looks fine.
- **Search snippets describing a book are not a download.** Resolve a real file URL and probe it with `curl -I` before writing anything to `~/Downloads`.
- **Non-ASCII GitHub raw paths must be percent-encoded.** `curl -L` follows the `raw.githubusercontent.com` redirect fine, but a hand-typed UTF-8 path 404s — use the encoded URL the rendered page gives you.
- **The literal Chinese title is usually not the published title.** Searching the official translated title plus the English original in one query finds edition metadata fastest; the literal translation alone drowns in forum noise.
- **Name the edition delta in the answer.** For technical classics the revision changes foundational content (instruction set, added chapters). "6th, adds a domain-specific-architecture chapter, moves to RISC-V" is the difference between a useful handover and a file dump.
- **Do not split an Anna's Archive partner-mirror download across connections.** The mirrors ignore `Range` and answer with the whole body, so `aria2c -x/-s` (or any multi-URL resume) dies on `Invalid range header … Response: 0-<size>`; delete the partial file *and* its `.aria2` control file, then stream it with a single `curl -fL`. There is no resume — a retry restarts from zero.
- **On the paper-copy fallback, distinguish the 正式出版 edition from the 内部印本 of the same work.** Chinese academic atlases and manuals are often first circulated as a non-ISBN 内部印本 under a near-identical title ("辅助参照食物图谱" vs the later "辅助估量食物图谱") and resold on 孔夫子旧书网 at full price; give the ISBN with the purchase line so the user cannot land on the earlier, thinner edition.
- **Do not present an unverified ISBN or translator.** Take publisher, translator and ISBN from a bookseller/catalog listing you actually opened; mark anything unconfirmed as such.
- **EPUB `mimetype` must be the first entry and STORED uncompressed.** Write it first with `zipfile.ZIP_STORED`, then everything else `ZIP_DEFLATED`. Compress it or reorder it and readers refuse the book even though the zip is valid.
- **The first `<p>` of every page carries the printed page number and running head.** Sending it verbatim makes the model fuse "2 Chapter One Fundamentals… 1.1 Introduction" into the first translated sentence. Strip the leading page number before sending and check the opening sentence of a sample page.
- **Set `lang`/`xml:lang` to `zh-CN` on every page.** Left as the source language, readers apply the wrong hyphenation and font stack and the book looks broken before it reads badly.
- **Audit a finished EPUB translation for four artifact classes before delivery; tags-passthrough leaks them systematically.** (a) Italic emphasis words in the source (`<span class="italic">scarce</span>`) are tags, so a run-splitting translator passes them through untranslated — they end up glued inside Chinese sentences ("还剩下什么scarce当…", 27+ hits in one book); fix by re-translating the whole paragraph with a gloss rule（中文译名（English）), not by bare word swap. (b) Model output leaves Markdown asterisks (`*Management Science*`) inside body text — sweep `\*[A-Za-z]`. (c) The model inserts literal "……" placeholders mid-sentence when it cannot resolve clause order — scan `……</p>` and 中文……<span class="italic">[a-z]`. (d) Splitting on tags can drop a verb (`told…that` 谓语漏译) or leave orphan fragments (`hemselves.` before `</p>`) — scan `[a-z]\.</p>`. A mechanical scan for all four plus an independent subagent sentence-level back-check against the source (α≙55 paragraphs) catches reflow-同时 hiding fidelity errors (术语同名异译, 人名前后不一).
- **Extending the `<p>` translation regex to `h1-h6`/`li` shifts the group indices.** A `(p|[hH][1-6]|li)` capture group with a `</\2>` backreference makes the tag *name* `group(2)`, inner HTML `group(3)`, closer `group(4)`; reading `group(2)` as inner sends the literal tag name to the model, the short-run skip returns it verbatim, and the run "finishes" at 1000 pages/min with zero translated output and no error. After any regex change, assert one translated page contains >200 hanzi before launching the batch.
- **A machine translation is not an edition.** Say so: name the source edition it was translated from, and that terminology follows a glossary, not a human translator's choices.
- **A multi-volume reference is cited by series title, never by edition number.** "第 6 版" is not a title — the published name is 《… 标准版》 split into 第一册/第二册/… by content type, so search the series title and match on 分册 + 年份; the edition number alone returns 前版 and sibling volumes interleaved. Read the 版次表 page of any volume already in hand — it lists the other volumes and their years, which beats searching for each one. Do not assume the split runs to the count the blurb promised: a 分册 that was announced and later dropped leaves every listing still describing it as imminent.
- **Equal page count and equal file size do not prove two PDFs are the same file.** MD5 changes on any re-save, and rendered pages shift when front matter is offset. Hash a low-dpi pixmap of ≥4 pages spread across the book before calling a copy redundant — page 1 is shared cover boilerplate and matches across genuinely different scans.
- **A shadow-library mirror behind DDoS-Guard is a browser choice, not a dead end.** Every official Anna's domain (`.gl/.pk/.gd`) fronts the same shield, and its text/checkbox CAPTCHA issues a fresh Request ID after each pass, so plain CDP automation loops forever on a page that looks broken. `ego-browser` clears it on the first navigation; then drive the countdown page and pull the partner URL out of `document.body.innerText` when the accessibility snapshot truncates it mid-path.
- **A shadow-library domain answering `200` proves nothing.** Dead/ghost mirrors stay resolvable and serve a JS redirect stub — real `200`, `<title>Redirecting...</title>`, a `POST` form plus obfuscated redirect script, zero results markup. Grep the body for what a working results page must contain (the `/md5/<hash>` links, the results table) before reading "no hits" as "the book is not indexed". The same care in the other direction: an interstitial or bot-wall page means the site refused you, which is not evidence the file is absent.
- **A 读秀 scan answers `Content-Type: application/octet-stream` and `file` often prints no page count.** Neither is a defect and neither is a reason to re-download: get the count from the PDF library, and let the `Pdg2Pic`/`FreePic2Pdf` producer string tell you what you actually got.

## Cross-References

- `web-search` — backend routing and fallbacks when a search engine returns nothing
- `blocked-page-recovery` — when the item page or download is 403/429/behind a bot wall
- `url-to-markdown` — turning a fetched chapter/PDF into readable text for the user
- `references/ebook-translation-pipeline.md` — building a Chinese EPUB from a verified English original
- `scripts/translate_epub.py` — resumable per-page EPUB translation worker
- `scripts/ocr_pages.swift` — render + OCR a page range of any PDF, or one image (Chinese-capable, no installs) to verify CIP/TOC content and find a table's page span
- `references/scanned-epub-rebuild.md` — image-only EPUB → PDF, locating one 表/章, excerpt delivery
- `references/full-text-book-sources.md` — source directory + the new-release branch (why a recent book has no free full text, and the legit answer to give instead)
- `references/chinese-book-publication-status.md` — is this volume/edition actually printed? Publisher catalog xls, award-disclosure and 丛书-count witnesses, and the stale-boilerplate traps
