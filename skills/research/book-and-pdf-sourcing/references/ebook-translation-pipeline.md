# Building a Chinese EPUB from a verified English original

For the case where the user wants a Chinese version no publisher ships (or one
that is years behind) and asks for the original translated. Assumes step 4 of the
parent skill already produced a **verified** EPUB whose page count and size are
sane — never translate an unverified file.

Runnable worker: `scripts/translate_epub.py`. Everything below is why it is
shaped the way it is.

## 1. Inspect the EPUB before writing any code

```bash
python3 -c "
import zipfile
z = zipfile.ZipFile('book.epub')
print(sum(1 for n in z.namelist() if n.endswith(('.html','.xhtml'))), 'html files')
print(z.read([n for n in z.namelist() if 'page_33' in n][0]).decode()[:600])
"
```

Publisher-produced academic EPUBs (Elsevier/Morgan Kaufmann, Pearson, Springer)
are almost always **one HTML file per printed page** (`EPUB/page_NNNN.html`), text
in plain `<p>` elements, figures as `<img src="image_00NN_00.jpeg">`. That is the
ideal input: paragraph structure and figure placement survive translation
untouched because you never touch the markup.

Count how many pages actually carry text before estimating time — covers, part
titles and blank pages translate to nothing:

```bash
python3 -c "
import zipfile, re
z = zipfile.ZipFile('book.epub')
n = [x for x in z.namelist() if x.endswith('.html')]
ok = sum(1 for x in n if len(re.sub(r'<[^>]+>', ' ', z.read(x).decode('utf-8','ignore')).strip()) > 30)
print(ok, 'with text of', len(n))
"
```

## 2. Translate at paragraph granularity

Per file: regex the `<p ...>…</p>` blocks, then split each inner HTML on
`(<[^>]+>)`. Send only the text runs; pass tags back through verbatim. This is
what keeps `<img>`, inline math and cross-reference anchors intact — rebuilding a
page from model output silently deletes figures.

Skip runs under ~12 chars (page numbers, figure numbers, list markers) so the
model does not spend a call turning `12` into `12`.

## 3. The translation contract that produced usable textbook prose

- Role: top-tier academic translator; target register is a published Chinese
textbook, not conversational Chinese.
- **Terminology-consistency clause is the one that matters.** Without it the
model alternates between 缓存/高速缓存, 流水线/管线, 分支预测/转移预测 within a
single chapter and the book reads like three translators fought over it.
- Keep formulas, numerals, identifiers, code and English acronyms (ISA, RISC-V,
TLB, DSA) as-is — they are the reader's index into the literature.
- "Output only the translation, no preamble." Otherwise every paragraph gains a
leading "以下是翻译：" that gets written into the book.
- `temperature` 0.2.

## 4. Package the EPUB correctly

- `mimetype` **first entry, `ZIP_STORED`**, everything else `ZIP_DEFLATED`. Wrong
order or compression and Apple Books / Calibre refuse a file that `unzip -t`
says is fine.
- Rewrite `lang` and `xml:lang` to `zh-CN` on every page, or readers apply
English hyphenation and a Latin-first font stack.
- Leave `style/style.css`, `content.opf` and the images byte-identical.
- Repackage to the final path every ~100 pages so the user always holds an
openable, partially translated book instead of nothing until the end.

## 5. Run it as a resumable background job

Measured on a ~1500-page textbook: ~10 s per page single-threaded, so a few
workers bring the whole book to about an hour. Launch with
`terminal(background=true, notify=true)` and tell the user three things: the log
tail command, that progress is on disk in `progress.json` (resumable after an
interrupt), and the current page/time estimate. Do not sit in the foreground
waiting on it.

## 6. QA before calling it a book

- Read the **first paragraph of one translated page**: the printed page number
and running head sit at the start of it, and a naive send fuses
"2 Chapter One Fundamentals 1.1 Introduction" into the translated sentence.
- Confirm an image-bearing page still contains its `<img>` tag.
- Confirm `zipfile.ZipFile(out).namelist()[0] == 'mimetype'`.
- Say plainly that this is machine translation of a named source edition, with
terminology following a glossary rather than a human translator.

## Limits to state up front

- Index, bibliography and reference lists translate badly — hundreds of short
fragments and proper nouns. Leaving them in English usually makes a better book.
- Tables live in `<table>`, which the `<p>` pass never touches: they stay English
unless you write a second pass over `<td>`.
- Figure images keep their original-language labels; no text pass fixes a
rasterized figure.
