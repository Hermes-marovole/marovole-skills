# Citation formats per output target

The ledger is format-agnostic: `sources.py render --style ...` emits the block,
this file says where it goes and what the inline marker looks like.

## Markdown / chat answers

Inline `[n]` immediately after the sentence. Block at the end:

```
## Sources

[1] https://example.com/a — Page title
[2] https://example.com/b
```

`--style plain` gives a bare `Sources:` header for chat replies where a
markdown heading would be noise.

## PDF via LaTeX (`latex-pdf-report` skill)

Use `--style footnotes` and map each id to `\footnote{}` at first use, or keep
numeric markers and emit an endnotes section. For a bibliography-shaped report,
`--style bibtex` writes `@misc` entries keyed `source<N>`; cite them with
`\cite{source3}` and let BibTeX render the list.

Do not mix: either numeric `[n]` + a Sources section, or `\cite{}` + BibTeX.
Two numbering systems in one document is worse than none.

## Word (.docx, `microsoft-office` skill)

Real footnotes are preferred over inline brackets in prose documents intended
for human editing — reviewers expect Word footnotes. Keep the ledger ids as the
footnote numbers so `verify` still works on a markdown source-of-truth, and
generate the .docx from that markdown.

## Slides (.pptx, `microsoft-office` skill)

Inline `[n]` in the bullet, one "Sources" slide at the end rendered with
`--style plain`. Never put a URL in a body bullet — it wrecks the layout and
can't be clicked in a projected deck.

## Spreadsheets (.xlsx)

Add a `source` column holding the id, plus a `Sources` sheet built from
`render --style plain`. Do not paste URLs into data cells.

## Wiki / multi-page output (`llm-wiki`, Obsidian)

Per-page Sources block, ids shared across pages from one ledger. Because ids
are ledger identities, `[7]` means the same page everywhere in the wiki — that
consistency is the reason not to reset the ledger between pages of one build.

## Research papers

Hand off to the `grounded-citations` skill. Export with
`--style bibtex` into `references.bib`, then follow that skill's citation
verification (it greps `\cite{...}` against the .bib). The ledger's job ends at
producing verified URL entries; venue formatting is that skill's domain.

## Styled HTML → A4 PDF (the usual report deliverable)

Build the HTML from the markdown draft so the prose stays the source of truth,
print with Chrome headless (`--no-pdf-header-footer`), and keep three
placeholders that are filled *after* citations are converted to anchors:

| Placeholder | Filled with | Why after, not before |
|---|---|---|
| `__BODY__` | prose with `[n]` → `<a class="cite" href="#ref-n">` | the id list must come from the ledger |
| `__SOURCES__` | `sources.py render --cited-in draft.md` | ids stay ledger identities |
| `__HEADING__` | `参考来源与原文引用（共 N 项）` | literal `[1]` in a heading becomes a link |

Verify the HTML before printing — a broken anchor is invisible in the PDF, it
just silently drops the click target:

```python
html = open("report.html", encoding="utf-8").read()
ids = re.findall(r'href="#ref-(\d+)"', html)
refs = set(re.findall(r'id="ref-(\d+)"', html))
print("cites", len(ids), "unique", len(set(ids)), "refs", len(refs))
print("dangling", sorted(set(ids) - refs), "orphan", sorted(refs - set(ids)))
print("placeholders", re.findall(r'__[A-Z]+__', html))
```

Then, after `--print-to-pdf`, confirm the page count matches the section budget
and that no page is blank — Chrome will happily emit a page whose content was
clipped away:

```bash
pdfinfo report.pdf | grep -E "Pages|Page size"
for p in $(seq 1 $N); do
  echo "page $p chars=$(pdftotext -f $p -l $p report.pdf - | tr -d '[:space:]' | wc -c)"
done
```

Any page under ~300 chars on a page-per-topic layout means the section was
swallowed by a `page-break` or an `overflow` — not that the section was short.

Keep the PDF text-extractable: no text baked into background images, no
`overflow:hidden` on a fixed-height page container (it truncates instead of
overflowing to the next page).

## Code and config artifacts

No citations inside generated code. If provenance matters, put it in the
commit message, the PR body, or a doc header — not in comments scattered
through source.
