# Where full-text books and course resources actually live

Condensed source directory. Each entry is a shape that reliably serves real files — verify every download (SKILL.md step 4) because availability changes.

## Internet Archive (best for English originals)

Item page: `https://archive.org/details/<item-id>`

Direct download: `https://archive.org/download/<item-id>/<filename>` — `<filename>` must match the item's own filename exactly, including spaces, colons and edition words. Copy it from the item page's file list rather than guessing.

Behaviour to expect:

- `/download/` answers `302` to a `dn<number>.<region>.archive.org` node; the final response is the file itself. `curl -L` handles it.
- Both `.pdf` and `.epub` are usually present for the same item and both are complete. Deliver both when the user may want to read on an e-reader.
- Full technical books run 30-40 MB and 700-1500+ pages. Use those numbers as the sanity band.

Discover item ids by searching `site:archive.org <title> <edition>`. The item id is a slug of the title, so near-miss ids are common — confirm the id against the search result URL, never from memory of a similar book.

## University course-resource repos (best for Chinese editions + extras)

The `icicles`-style repos (e.g. Zhejiang University's course-sharing project) archive per course: the textbook in English **and** the published Chinese translation, the solution manual, every appendix as a separate PDF, the official per-chapter slide decks, past exams and student summary sheets.

Shape: a published HTML index page lists `github.com/<org>/<repo>/raw/master/<percent-encoded path>` links grouped by edition. Fetch that index page and read the link list — it is the fastest complete inventory of editions 3/4/5/6 plus appendices in one place.

- Chinese filenames arrive percent-encoded; use the href verbatim.
- `raw` redirects to `raw.githubusercontent.com`; `curl -L` follows it.
- These are large: a Chinese scan of a 600-page textbook is ~25 MB.

Search `site:github.com/<org>/<repo> "<chinese title>"`, or the rendered index domain (`<org>.github.io/<repo>/<path>/`) when the repo README does not enumerate files.

## Community appendix translations

Technical books often ship appendices online-only, and Chinese editions cut them. Look for a GitBook + GitHub pair translating the online appendices (search `<english title> appendix 中文`). Cite both the reading link and the repo. Useful because the printed Chinese edition is legitimately incomplete.

## Library Genesis (`libgen.bz`) — fastest route to a Chinese 读秀 scan

Four requests, no countdown, no account, no mirror roulette. It indexes the same 读秀 corpus as Anna's Archive and reports the **same MD5**, so a hash taken here is a cross-check against that page and vice versa.

1. **Search**, title URL-encoded: `https://libgen.bz/index.php?req=<urlencoded 中文书名>`
   The results table carries one row per file: title link → `edition.php?id=<n>`, plus 作者 / 出版社 / 年份 / 页数 / 大小 / 格式. A multi-volume work shows one row per 分册 — pick by 分册 + 年份 + page count, never the first hit.
2. **Edition page** → MD5: `https://libgen.bz/edition.php?id=<n>`
   The page repeats `ads.php?md5=<md5>` several times and also carries `file.php?id=<file id>`. Any of those links yields the hash.
3. **Ads page** → the key: `https://libgen.bz/ads.php?md5=<md5>`
   The only useful content is one `get.php?md5=<md5>&key=<KEY>` href. The key is per-file and short-lived — re-fetch this page instead of reusing an old one.
4. **Download** through the machine's HTTP proxy, with a desktop UA and the ads page as Referer:

```bash
curl -fL -x "$HTTP_PROXY" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36" \
  -e "https://libgen.bz/ads.php?md5=<md5>" \
  -o "$HOME/Downloads/<书名>_<版次>_<分册>_<年>.pdf" \
  "https://libgen.bz/get.php?md5=<md5>&key=<KEY>"
```

Behaviour:

- Send the Referer and a desktop UA; bare requests get bounced back to the ads page.
- **`Content-Type` is `application/octet-stream`**, not `application/pdf` — step 4's content-type check cannot be satisfied here, so lean on `file` + the page count read from the PDF library.
- `file` frequently prints `PDF document, version 1.5` with **no page count** for these CJK scans; read `page_count` via `fitz`/`pypdf` instead of concluding the file is a stub.
- **A row is not a file.** `get.php` redirects to a `cdn5.booksdl.lc`/`booksdl` node that answers `500` with `File not found in DB` when the record outlived its file — every libgen family mirror (`.bz/.li/.la/.vg`) shares that CDN, so sweeping mirrors reproduces the same failure. Take the row's MD5 to Anna's Archive, where the site's own direct/zlib source usually still hosts it.
- One streaming `curl`, no resume and no parallel connections — 70–90 MB lands in well under a minute at 2–7 MB/s.
- Mirrors are CN-blocked; without the proxy the request dies at connect, not at the file.

## Recognising a 读秀 scan before you commit to it

`fitz.open(f).metadata` reporting `creator: Pdg2Pic` and `producer: FreePic2Pdf_Lib` is the exact signature of a 读秀 image dump (one JPEG per page, often post-processed by `FreePic2Pdf`). Consequences, all of which shape the plan:

- `page.get_text()` returns 0 characters on **every** page — no grep, no quoting, no table extraction without OCR. Detect this before promising the user either.
- Verification = render the CIP page and TOC and OCR them (`swift scripts/ocr_pages.swift <file.pdf> 1 18`), then read every digit and ISBN off the rendered image rather than off the OCR text.
- The PDF page count runs ~5–10 above the printed 页数 (front matter), so a scan whose count looks "too long" against the listing is usually correct — compare printed 页数 from the CIP page, not the raw PDF count.

## Anna's Archive (best for Chinese 读秀 scans)

Mainland academic/textbook scans (read from 读秀, the `SS-152字段`-style dumps) live here and nowhere else. Search the Chinese title on the site or via `site:annas-archive.gl "<chinese title>"`; the `/md5/<hash>` page is the hub.

URL shape: `https://<mirror>/slow_download/<md5>/0/<serverIndex>` for index `0`–`9`. Each page runs its own countdown (12–25 s) and then exposes two links — take the **`annas-arch-<md5>.pdf` "Download with short filename"** one for `curl`, and read the sibling filename line to confirm the exact title/ID before downloading (it prints the real filename, e.g. `回顾性膳食调查辅助估量食物图谱-15233723.pdf`).

**DDoS-Guard fronts every official mirror** (`.gl/.pk/.gd`) and holds an unfamiliar exit IP in a check loop: a text or checkbox CAPTCHA that mints a fresh Request ID after each pass, so plain CDP automation never gets past it. `ego-browser` clears the shield on the first navigation and then carries `/md5/` and `/slow_download/` normally; type captcha answers with real key events (`Input.insertText` or coordinate clicks), because framework-bound inputs ignore `el.value = …`.

After the countdown the page becomes `Download from partner website` — **no button, no anchor**: it prints the partner URL and the short-filename URL as plain text next to `copy` buttons. Read it out of the text; when the accessibility snapshot truncates it mid-path (`…__K5...`), regex `document.body.innerText` rather than re-typing:

```js
[...new Set(document.body.innerText.match(/http:\/\/\d+\.\d+\.\d+\.\d+:\d+\/[^\s"']+/g) || [])]
```

The partner host is a bare `IP:port` over plain HTTP and is often reachable **without** the proxy at full speed — try direct `curl -fL` first, add `-x` only if it stalls. Always take the `annas-arch-<hash>.<ext>` short-filename URL; the long one only adds the full title and 200-character paths.

Rules that decide whether the download takes 20 seconds or 2 hours:

- **Mirror tier is in the path.** `/200/` in the URL is the throttled tier (~20 KiB/s, multi-hour ETA); `/1000/` is the fast tier (~10–15 MB/s). Pick a server whose short-filename link carries `/1000/` — index 9 is usually the slow one.
- **Countdowns run per page, so open several in parallel tabs** (`…/0/1`, `…/0/2`, `…/0/3`) and collect whichever finishes first. Only one download per server at a time; parallel tabs are fine, parallel requests per server are not.
- **One connection only.** Partner mirrors ignore `Range`, so `aria2c -x/-s` or any resume attempt fails with `Invalid range header … Response: 0-<size>`. `curl -fL -o <name> <url>` streams the whole file at full speed; there is no partial-resume, so a failure restarts.
- **Verify identity with the MD5 in the filename.** `md5 <file>` must equal the hash in `annas-arch-<hash>.pdf` and in the `/md5/` URL — that hash is the page's own record, so a match proves you got the file the page advertises (not that it is the edition you want; check the CIP page for that).
- The `外部下载 / external downloads` links (IPFS, libgen) often render empty on the `/md5/` page; do not spend turns on them when a `/1000/` partner link is available.

## When the book is a recent release (roughly the last 12 months)

The corpora above are uploads by readers, so the newest titles are often missing — but "recent" is not "absent": trade nonfiction reaches them within months, so check whether a row exists and how recently it was uploaded before declaring the book unavailable. What is common in that window is a **dead row**: the record is there with the right MD5 and the file host no longer has the bytes (libgen 500s), while Anna's own source still serves. Route the purchase answer only after the file actually failed.

When it genuinely is not there, stop searching them and route to what exists:

- **Official free chapters.** Academic, indie and university-press authors publish sample chapters as PDFs/HTML on the book's own site — often the preface plus several complete chapters. Find it from the tweet/article that named the book, or `<title> official site`. This is frequently the whole legitimate answer to "let me read it", and it is quotable.
- **Digital editions with the identifier you need.** Kindle (ASIN, e.g. `B0…`) and Kobo (ISBN-13 + Adobe DRM) both publish the epub before any scan circulates. Quote the ASIN/ISBN from a listing you opened, name the DRM state plainly, and offer the Calibre + DeDRM route for a copy the user has bought.
- **Grey aggregators that mirror the retail epub** (oceanofpdf-style "pdf-epub-<title>-download" pages) are gated by Cloudflare and often serve nothing but sponsored host links. Treat a page that only proves the file *exists* as no evidence of a download (see SKILL.md step 3 end).
- **File-host free tiers on those pages are captcha-gated.** Rapidgator and relatives use Cloudflare Turnstile, not hCaptcha: the form holds a `.cf-turnstile` div with `data-sitekey` and a hidden token input named `cf-chl-widget-<id>_response`, and the site key is only rendered on a fresh visit to `/download/captcha`. Probe the token input's `value` for a few seconds — if it stays empty, the free tier is not something you can drive, and the honest move is to stop and give the purchase answer rather than burning turns on screenshot-guessing which captcha it is. Clicknupload-class links on the same pages are usually already dead.

## Print / bookstore answer

Always resolve, since a download may not exist legally or at all:

- Chinese edition: publisher + translator + ISBN from a bookseller listing.
- English edition: the domestic 影印版 (photocopy reprint) publisher + ISBN, or the original publisher + ISBN.

Take these from a listing opened this session; never reconstruct an ISBN from a similar book's number.

## What not to bother with

- "金币 / download-credit" aggregator sites: they show a description and a size, then require an account. Only useful as evidence the file exists.
- Search-result titles alone: they resolve to nothing without a file probe.
