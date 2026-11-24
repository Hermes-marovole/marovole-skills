# Image-only EPUB → PDF, and pulling one table out of a scan

Chinese standard reference books (食物成分表, 食物图谱, 标准汇编) circulate as duxiu/Z-Library
EPUB dumps that are **scans wrapped in an EPUB container**: every "page" is one JPEG and
`index.html` is just a stack of `<img>` tags. There is no text layer anywhere, so search,
quoting and page lookup all fail until you turn it into a PDF you can render pages from.

## 1. Confirm it is an image-only EPUB

```python
import zipfile, re
with zipfile.ZipFile(epub_path) as z:
    html = z.read("index.html").decode("utf-8", errors="ignore")
    idx = [int(x) for x in re.findall(r"index-(\d+)_1\.jpg", html)]
    print(len(idx), idx == list(range(1, len(idx) + 1)))
```

`True` on the second value means zip-entry numbering is reading order — then image N is
printed page N plus a constant offset. If it is `False`, stop and follow the `<img>` order
from `index.html` instead of the numbers.

Don't rely on `ebook-convert` here: Calibre re-lays-out and can drop the page-per-image
correspondence you need. Also do not assume `pip install` options — PyMuPDF (`fitz`),
`pypdf` and `PIL` are the ones reliably present on this machine.

## 2. Rebuild the PDF (keeps the JPEG bytes, no re-encode)

```python
import zipfile, fitz
out = fitz.open()
with zipfile.ZipFile(epub_path) as z:
    for i in range(1, n_pages + 1):
        d = fitz.open(stream=z.read(f"index-{i}_1.jpg"), filetype="jpeg")
        r = d[0].rect
        out.new_page(width=r.width, height=r.height).show_pdf_page(
            r, fitz.open("pdf", d.convert_to_pdf()), 0)
out.save(pdf_path)
```

Wrapping each JPEG in a one-page PDF and placing it with `show_pdf_page` copies the image
stream instead of decoding it, so ~450 pages finishes in about a second and the file size
equals the sum of the originals. Verify with `file <pdf>` and
`python3 -c "import pypdf;print(len(pypdf.PdfReader('<pdf>').pages))"` — the count must equal
the `<img>` count, not just be non-zero.

## 3. Find the one table/chapter the user actually asked for

1. OCR the TOC pages to get printed page numbers for each 表/章 (`scripts/ocr_pages.swift`).
2. Read a page **footer** to get the image-index → printed-page offset — these books print
the page number and the running title in the footer, and the offset is not 0 (front matter
is roman/unumbered).
3. Sweep 3–5 candidate pages with OCR to confirm the table's first and last image index;
the table's own heading ("表六 常见食物嘌呤含量") plus the last page's footnote list give
the exact span.
4. Build the excerpt from that span only, with the same rebuild loop.

## 4. Deliver both

The excerpt answers the question; the whole book is what they will want next week. Hand over
two `MEDIA:` lines — excerpt first, with its page count and the 表 number + printed page
range, then the full book with total pages and size. Name them by subject in the script the
user reads, with edition/表 number in the filename.

## 5. Answer shape

The user names a table, not a work: give 书名 / 主编 / 编著 / 出版社 / 版次 印次 / ISBN / 定价 and
"对应第 X 页·表N", then one short block on provenance (who measured it, by what method, on
which sample regions) taken from the table's own introductory page — not from memory.
