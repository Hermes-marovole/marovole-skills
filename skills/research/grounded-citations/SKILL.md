---
name: grounded-citations
description: "Ground answers and documents in cited, verifiable sources."
version: 1.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Citations, Grounding, Sources, Web, Reports]
    category: research
    related_skills: [arxiv, pdf, reddit-reading, rss-feeds, youtube-content]
---

# Grounded Citations

Every claim taken from an outside source gets an inline numbered citation and a
`Sources:` list, Perplexity-style. A ledger script owns the `url → [n]` mapping
so the numbers and URLs come from retrieval, never from memory — the model only
ever emits small integers it was handed.

For high-stakes work the same ledger doubles as a fact-checking chain: verbatim
quotes are attached to each source (rejected unless they literally appear in
the fetched page text), claims from model knowledge are flagged `[unverified]`,
and `verify --evidence` fails any draft whose cited sources carry no evidence.

This skill covers answers in chat, written documents (markdown, PDF, docx,
slides), and research reports. It does not cover academic BibTeX pipelines —
for conference papers use the `arxiv` skill, which this skill
feeds (see `references/citation-formats.md`).

## When to Use

Use whenever an answer or artifact rests on information you fetched rather than
knew:

- Research, comparisons, news summaries, "what is the current state of X"
- Any deliverable you write to disk that quotes, paraphrases, or reports
  outside facts — reports, briefs, docs, decks, wiki pages
- Fact-finding where the user will want to check your work
- Multi-source synthesis where conflicting sources must be attributed

Skip inline citations when the retrieval is incidental to another task — a
quick syntax/version lookup mid-coding, casual conversation, creative writing.
Mention a URL only if the user would plausibly want the link.

## Prerequisites

None beyond the standard toolset. `scripts/sources.py` is stdlib-only Python 3.
Retrieval comes from whatever is configured: `web_search`, `web_extract`,
`browser_exec`, or `terminal` (curl, CLIs).

Ledger location: `$HERMES_HOME/cache/citations/ledger.json` (profile-aware).
Override per task with `--ledger <path>` or `HERMES_CITATION_LEDGER`.

**`--ledger` is a top-level flag — it must come *before* the subcommand.**
`sources.py --ledger X quote 3 --text … --from …` parses; appending it
(`quote 3 --text … --ledger X`) exits
`unrecognized arguments: --ledger /Users/…/ledger.json` while the command
otherwise looks correct. The same trap hits any helper script that shells out
to `sources.py` and concatenates `--ledger` onto the end of the argv — build the
helper's argv as `[sources.py, "--ledger", path] + [subcommand, …]`.

## How to Run

```bash
S=~/.hermes/skills/research/grounded-citations/scripts/sources.py

python "$S" reset                                  # start a clean ledger
python "$S" add https://example.com/a --title "A"  # prints: [1] https://example.com/a
python "$S" add https://example.com/b --title "B"  # prints: [2] https://example.com/b
python "$S" list                                   # ledger table
python "$S" render                                 # Sources: block
python "$S" verify draft.md                        # catch bad citations
```

`add` is idempotent and URL-normalized: the same page always returns the same
id within a ledger, so ids stay stable across many search/extract rounds.

## Quick Reference

| Action | Command |
|---|---|
| Fresh ledger for a new task | `sources.py reset` |
| Register a source, get its id | `sources.py add <url> [--title T]` |
| Register several at once | `sources.py add <url1> <url2> ...` |
| Register from JSON tool output | `sources.py ingest results.json` |
| Attach verbatim evidence to a source | `sources.py quote <id> --text "exact wording" --from page.txt` |
| Show ledger | `sources.py list [--json]` |
| Render the Sources block | `sources.py render [--style markdown\|plain\|footnotes\|bibtex\|evidence] [--only 1,3]` |
| Render only what a draft cites | `sources.py render --cited-in draft.md` |
| Rewrite a draft's Sources block in place | `sources.py render --replace-in draft.md` |
| Check a draft's citations | `sources.py verify draft.md [--strict] [--min-coverage 0.6] [--evidence]` |

## Procedure

① **Reset the ledger** at the start of a task that will produce a grounded
answer or document. Skip the reset when continuing work whose ids are already
in a draft — reusing the ledger keeps the numbering stable.

② **Register every source at retrieval time.** After each `web_search` /
`web_extract` / `browser_exec` / fetch, pass the URLs to `sources.py add`
(or pipe the raw JSON through `sources.py ingest`). Do this *before* writing
prose. Registering later, from memory, is the failure mode this skill exists to
prevent.

③ **Write cite-while-drafting.** Place the bracketed id(s) immediately after
each sentence the source supports:

```
Ice floats because it is less dense than liquid water.[1][2]
```

- No space before the bracket; each id in its own brackets.
- Max 3 ids per sentence. Cite per sentence, not one dump at the end.
- Only ids the ledger returned. Never invent an id or a URL.
- Claims from your own knowledge get no citation.
- Conflicting sources: present both readings, each with its own id.
- Quote exact figures, dates, and names as the source states them; flag gaps
  explicitly ("no source found for X") instead of smoothing them over.
- **Never quote a number out of a results table without re-reading its column.**
  Benchmark tables put several near-identical percentages side by side (calorie
  vs mass vs carb error), and a figure lifted while reading the row instead of
  the column survives into the deliverable and into every later summary of it.
  Write the value with its column label (`热量 PMAE 8.8%，质量 4.5%`) and
  re-check the row against the table image before delivering.
- **Take licenses from the repo's LICENSE field, not from a paper abstract or a
  blog summary.** "Open source" routinely means CC BY-NC weights that cannot be
  used in a product; reading the actual license file is the difference between a
  viable recommendation and one the user discovers at deploy time.

④ **Append the Sources block** with `sources.py render --cited-in <draft>` so
the id → URL mapping is generated mechanically from the ledger, not retyped.
For non-markdown targets pick the matching `--style` and follow
`references/citation-formats.md` for placement (footnotes in docx, endnotes in
PDF/LaTeX, a Sources slide in decks, per-page source lists in wiki output; the
styled HTML → A4 PDF recipe with its link/placeholder checks is in the same
file).

⑤ **Verify before delivering** — `sources.py verify <draft>` exits non-zero on
unknown ids, on a Sources block that disagrees with the ledger, or (with
`--min-coverage`) on prose that is too thinly cited. Fix and re-run.

⑥ **Chat answers** follow the same steps with the draft in your reply: register
sources, cite inline, end with the rendered `Sources:` list. For a short answer
you may render the block from `sources.py render --only <ids>` instead of
writing to a file.

## Multi-Platform Sweeps

"What are people saying about X" / "research X across the web" is not one
`web_search`. Fan out across source types, collect in parallel, then synthesise
with every claim attributed to the platform it came from:

| Source type | Route | What it adds |
|---|---|---|
| Open web | `web_search` → `web_extract` | official docs, articles, announcements |
| Community discussion | `reddit-reading` (`search`, `thread`) | real user experience, complaints, workarounds |
| Blogs / releases / changelogs | `rss-feeds` (`read`, `discover`) | dated primary posts, version history |
| Video | `youtube-content` | walkthroughs, demos, talks |
| Code | `terminal` with `gh search repos` / `gh search issues` | implementations, open bugs |
| X/Twitter | `xurl` (needs API access) | announcements, developer chatter |

The `reddit-reading` and `rss-feeds` skills are optional. If absent, install with
`hermes skills install official/social-media/reddit-reading` or
`hermes skills install official/research/rss-feeds` before using them.

Register every URL from every route in the ledger as it arrives (step ②). Keep
opinion and measurement apart: a Reddit thread is evidence that users *report*
something, not that it is true; pair it with a primary source or label it as
sentiment. Report per-platform coverage gaps ("Reddit search returned nothing
newer than March") rather than silently narrowing to what worked.

## Fact-Checking Mode

For work where the reader must be able to check the chain — medical, legal,
financial, safety, disputed claims, or when the user asks for fact-checking —
upgrade from citations to evidence:

① **Attach a verbatim quote per source.** After extracting a page, save its
text to a file and attach the sentence(s) that carry each claim:

```bash
python "$S" quote 1 --text "Ice is about 9% less dense than liquid water." --from page1.txt
```

When the page resists extraction — image-format statistical tables, JS-rendered
mirrors, an extractor whose credits ran out — the capture routes and the
cross-check discipline are in `references/evidence-capture.md`. The evidence
file must always be text you actually fetched, never a transcription you typed
from looking at a picture.

The quote is rejected unless it appears verbatim in the evidence text
(insensitive to whitespace, case, and markdown markup — inline links like
`_[ERAP1](https://…)_` in extracted text match the plain prose a reader sees),
so a paraphrase or misremembered figure cannot masquerade as evidence.
Copy-paste from the fetched text; never retype. Quote the sentence as the
reader sees it — the matcher sees through the extractor's markup for you, so
you don't have to reproduce link syntax or escaped asterisks in your quote.

② **Flag model-knowledge claims with `[unverified]`.** A load-bearing claim
you could not source gets an explicit marker instead of a citation:

```
The refactor likely predates the 2.0 release.[unverified]
```

`verify --min-coverage` counts `[unverified]` sentences as covered — the goal
is declared provenance for every claim, not a citation on every sentence.
If a key claim can be checked, check it; `[unverified]` is for what genuinely
cannot be, and a fact-check deliverable dominated by `[unverified]` markers
should say so in its summary.

③ **Cross-check disputed facts against a second independent source.** When two
sources disagree, cite both readings with their own ids and quotes, and say
which you weight and why. One source is reporting; two independent sources are
corroboration.

④ **Verify with the evidence gate and render the evidence block:**

```bash
python "$S" verify report.md --evidence --min-coverage 0.5
python "$S" render --style evidence --replace-in report.md
```

`--evidence` fails the draft if any cited source has no attached quote. The
`evidence` render style prints each source's quotes beneath its URL, so the
deliverable shows claim → source → exact supporting text with nothing taken on
faith. Use `--replace-in <draft>` to rewrite an existing Sources block in place
(idempotent — safe to re-run after attaching more quotes); `--cited-in` prints
to stdout instead. Both emit the heading `## Sources` (`--style plain` emits
`Sources:`).

**What `--min-coverage` counts.** Coverage is
`sentences with declared provenance / prose sentences`. A prose sentence is a
non-empty line fragment of 4+ words after the Sources block, headings (`#`),
table rows (`|`), and fenced code are dropped; blockquote markers are stripped.
Provenance is declared by either a `[n]` citation or an `[unverified]` marker,
so a sentence carrying both counts once. Run `verify` without a threshold first
and read the `info: stats:` line to see the counts before picking a number.

**On Chinese drafts the coverage ratio is meaningless — do not gate on it.**
The sentence splitter only breaks on ASCII `.!?` followed by whitespace, so a
whole Chinese paragraph counts as one sentence, and the 4-word minimum is
whitespace-tokenized while a CJK sentence is one token. A multi-thousand-
character Chinese report therefore reports a handful of "prose sentence(s)" and
a coverage figure computed from that handful. Read the stats line as evidence of
the collapse, not as a quality score, and gate on `--evidence` (every cited
source carries a verbatim quote) instead of `--min-coverage`.

## Pitfalls

- **Registering after writing.** The ledger must be populated from tool output,
  not reconstructed from the draft — that reintroduces exactly the hallucinated
  -URL risk the numbering removes.
- **Renumbering mid-task.** Never hand-edit ids in a draft. Ids are ledger
  identities; if a draft cites `[4]`, `[4]` must stay that source. Run `reset`
  only between tasks.
- **Retyping URLs into the Sources block.** Always `render`. A hand-typed URL
  is an unverified claim.
- **Converting `[n]` to anchors across the whole document also rewrites the
  Sources heading.** A heading written as `Sources [1]–[30]` has its `[1]`
  turned into a link to the first source, so the delivered header reads
  `Sources [1]–30` with a clickable fragment in the middle. Build the heading
  from a placeholder substituted *after* the citation pass
  (`__HEADING__` → `参考来源与原文引用（共 30 项）`), or keep it outside the region
  you convert. Same trap for any prose line that legitimately contains
  bracketed digits.
- **The `more than 3 citations in one sentence` warning fires on markdown
  tables.** With no `。` inside a table, every row plus the trailing Sources
  block becomes one "sentence" carrying a dozen ids, and a clean draft looks
  over-cited. Before editing prose, print the flagged chunk and check it starts
  with `|` (table row) or `[N] https://` (Sources block) — if so the warning is
  an artifact of the split, not a defect; split on `。！？` yourself to see the
  real per-sentence counts.
  **Under `--strict` that warning is a hard exit 1**, so on a Chinese deliverable
  it has to be *repaired* before delivery, not just explained away — and it fires
  on long prose paragraphs too, not only on tables (the splitter only breaks on
  ASCII `.!?` + whitespace, so a 200-character Chinese paragraph citing six
  sources is one "sentence"). Two mechanical fixes, both safe to run over the
  whole draft:
  1. **Table rows** — strip every inline `[n]` from the cells, then re-attach at
     most 3 unique ids once at the end of the row: `re.sub(r'\s*\[\d+\]', '', line)`
     and append `''.join(dict.fromkeys(ids)[:3])` to the last cell before the
     trailing `|`. Cell-level repetition of the same id in 8 columns is what
     inflates the count.
  2. **Long paragraphs** — reflow at `。` into separate lines until each line
     carries ≤3 ids. Keep the prose, change only the line breaks.
  Either edit rewrites the row/line text, so re-run `render --replace-in` before
  `verify`; verifying the old Sources block against edited prose renumbers drift.
- **A second, caption-only row under a table header renders as a broken row.**
  `| 15M+ | $30M+ | ... |` followed by `|---|---|` and then `| 累计下载 | 年收入
  | ... |` (labels instead of values) is not a valid markdown table — one side
  gets swallowed as body cells. Put KPI numbers and their labels in a bullet
  list, or repeat the labels in the header row.
- **Hand-building `ledger.json` instead of going through `add`.** `add` normalizes
  the URL (drops `#fragment` and the trailing slash); a ledger file written by
  hand keeps URLs verbatim, and `verify` then fails with
  `Sources block URL for [N] does not match the ledger (block: <url> / ledger: <url>)`
  where both sides print identically — the invisible difference is the trailing
  slash. Either register through `add`/`ingest`, or apply the same
  strip-fragment-then-strip-trailing-slash normalization to every URL before
  writing the file, then `render` again. When a verify message shows two
  identical strings, suspect invisible normalization, not a wrong source.
- **Quote from the cache file that actually contains the text, not the one you
  assume.** Fetched pages land under `$HERMES_HOME/cache/web/`; a mirror host
  caches several pages per domain, so the file you extracted last is not
  necessarily the one holding the post you want to cite — pointing `--from` at
  the wrong one yields `not found verbatim` on text you can plainly see on
  screen. Grep the whole cache dir for a distinctive token (status/post id,
  headline) and quote from the hit:
  `grep -l "<post-id>" $HERMES_HOME/cache/web/*.md`. Pick a single-line
  substring as the needle: a multi-line post is several non-contiguous runs and
  cannot be attached as one quote.
- **Citing a search snippet as if you read the page.** A `web_search`
  description supports only what it literally says. Cite the extracted page
  when the claim needs the body — `web_extract` it first.
- **Over-citing.** Three ids on a sentence is the ceiling; a citation on every
  clause makes text unreadable and hides which source carries the load.
- **Grouped citations `[1, 2, 3]` are invisible to `verify`.** The scanner reads
  one integer per bracket, so a comma list counts as zero citations: coverage
  comes back far below what you wrote and `verify` warns
  `registered in the ledger but not cited: [7], [8]` for sources you know you
  cited. Never conclude the draft is under-cited from that warning alone —
  expand the groups mechanically first, then re-verify:
  `re.sub(r"\[(\d+(?:\s*,\s*\d+)+)\]", lambda m: "".join(f"[{n.strip()}]" for n in m.group(1).split(",")), body)`.
  Run the expansion **before** `render --replace-in`: the Sources block is
  regenerated either way, but coverage is counted on the prose.
- **Citing the ledger in code/config artifacts.** Source comments belong in
  prose deliverables and doc headers, not inside generated code.
- **Parallel subagents.** Each subagent has its own working directory; point
  them all at one ledger with `--ledger` (or `HERMES_CITATION_LEDGER`) if their
  outputs get merged, otherwise their ids will collide.
- **Quoting from a snippet instead of the page.** Evidence quotes must come
  from the extracted page text, not a search-result description — `web_extract`
  first, save the text, then `quote --from` that file.
- **Paraphrasing into `quote --text`.** The verbatim check will reject it; the
  fix is to find the actual sentence, not to reword until something matches.
- **Short CJK quotes get rejected as "too short"; widen to the whole sentence,
  do not insert spaces.** The length guard counts whitespace-separated tokens,
  so a substantive Chinese sentence with no spaces counts as one token. Padding
  the `--text` value with spaces after `，。；：、` does **not** make it pass: the
  matcher collapses a whitespace run to a single space rather than deleting it,
  so a space the page never had stops the quote from being a verbatim substring
  and the rejection flips from `too short` to `not found verbatim`. The reliable
  move is to widen the span to sentence/line boundaries (`。！？\n`) in the
  evidence file — those already carry newlines and digits, so the token count
  clears the guard on its own. Run
  `~/.hermes/skills/research/market-intelligence/scripts/attach_cjk_quote.py
  --id N --from ev.txt --dry "distinctive phrase"` to get the sentence-aligned
  `SPAN:` verbatim, then pass that span to `sources.py --ledger X quote N
  --text "<span>" --from ev.txt`. Locate the phrase with all whitespace
  stripped and map the hit back to the original indices — that is what makes it
  immune to `\u3000`/`\u2002` vs half-width mismatches. **Never edit the
  evidence file to make a quote fit**, and never pad the phrase with invented
  words: both defeat the check the guard exists to pass.
- **Slice CJK quotes out of the evidence file instead of retyping them.** The
  matcher normalizes whitespace, case, and markdown but not character width: an
  extractor that emits `\u2002`/`\u3000` or full-width punctuation where you
  typed half-width (or the reverse) fails with `quote not found verbatim` on
  two strings that look identical. Read the file and pass the exact line or a
  `re.search` span (`open(f).read().splitlines()[-1]`); retyping is how
  invisible-width mismatches get in.
- **A quote must be contiguous in the page text.** A passage that reads as one
  block in the report but is interrupted by table rows, headings, or captions in
  the fetched file cannot be quoted as one string. Quote the longest unbroken
  run, or attach two quotes — concatenating sentences across a table is the
  usual cause of "not found verbatim" on a passage you can plainly see.
  Extracted web text inserts markup into what reads as one sentence — inline
  links `[electronic health records](https://…)` and Wikipedia footnote anchors
  `.[[4]](https://…#cite_note-4)` — so a regex pre-selecting that sentence from
  the evidence file must tolerate `\[…\]\(…\)` spans, and a sentence visibly
  continuing after a footnote anchor is **not** one contiguous run: quote up to
  the anchor, which is where the fetch actually breaks.
- **Short structured lines fail the 3-token guard; widen the span, do not pad.**
  A quote like `playlists_total: 108` or `n: 7` is two tokens and gets rejected.
  Extend it backwards to the last contiguous full line (e.g. the preceding
  `playlist: <title> | id: <id>` line) so the quote is a real run of the file;
  padding with words the page never had defeats the verbatim check it exists to
  pass.
- **`add` prints `[n] <url>`, not a bare id.** Capturing its stdout and passing
  that line straight back as an id makes the next `quote` / `render --only`
  fail argument parsing on the leading bracket and URL. In scripts use
  `add --json` and read the id field, or regex `^\[(\d+)\]` out of the plain
  output. `add --json` emits a **JSON list** (`[{"id": 1, …}]`), not a single
  object — `json.loads(out)["id"]` raises
  `TypeError: list indices must be integers or slices, not str`; index `[0]`.
  `add` also takes several URLs at once, so one extraction round can be
  registered in a single call.
- **Never `subprocess.run(..., check=True)` on `quote` inside a registration
  loop.** One rejected quote (short, paraphrased, or pointed at the wrong
  evidence file) aborts the whole batch and leaves every later source
  unregistered. Collect failures, finish the loop, then retry only the failed
  ids — accepted quotes stay in the ledger, so re-running is idempotent.
- **Using `[unverified]` as an escape hatch.** It marks the rare claim that
  genuinely cannot be sourced; if most sentences carry it, the task needed more
  retrieval, not more markers.
- **Hand-editing the Sources block.** Use `render --replace-in <draft>`; slicing
  the file yourself risks a stale or duplicated block that `verify` then flags.

## Verification

```bash
python "$S" verify report.md --strict --min-coverage 0.5
```

Green means: every `[n]` in the draft exists in the ledger, the Sources block
lists exactly the cited ids with the ledger's URLs, and the cited share of
source-bearing sentences meets the threshold. Read the warnings even when the
exit code is 0 — uncited registered sources usually mean a claim lost its
attribution during editing.
