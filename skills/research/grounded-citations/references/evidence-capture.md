# Capturing evidence from pages that resist extraction

The ledger only proves what it can match: `quote --from <file>` checks the quote
against a text file you saved. So the whole game is getting a faithful text file
out of a page that does not want to give you one.

**Hard rule: the evidence file is fetched text, never a transcription.** If you
read a number off an image or a screenshot, that image is the evidence — the
text file you build from it is a *derived* artifact and must be labeled as such
in the report, not passed off as the page's own wording.

## Image-format tables (official yearbooks, scanned statistics)

Government statistical yearbooks routinely publish tables as `.jpg`/`.png`:
`web_extract` returns a caption and nothing else, and the search snippet carries
only fragments.

1. Download the table image into the evidence directory (`curl -o`).
2. Read it with vision for the specific rows and the column you need — name the
   column in the question, and re-read a crop when a digit is ambiguous.
3. Get the same table as text from a **second, independent path**: a third-party
   mirror that transcribes the table, or an author who quotes it row by row.
4. Require the two to agree cell by cell before the number enters the report.
   Disagreement is not resolved by averaging or by picking the prettier one —
   re-read the crop; if it stays unresolved, drop the row or mark it.
5. Write the agreed rows into an evidence `.txt` (one row per line) and attach
   quotes from that file. In the report, state the chain: original table image
   plus mirror transcription, cross-checked.

If the vision read and the mirror disagree on a whole total, trust neither and
find a third path (a second author quoting the same table, or the same figure
restated in an official bulletin).

## JS-rendered pages

`web_extract` and search snippets give only the fragments the crawler saw. Open
the page with `browser_exec`, then `js('document.body.innerText')`, filter the
lines you need in Python, and save those lines verbatim as the evidence file.
That innerText *is* the fetched page text, so quotes drawn from it are
legitimate — but keep the third-party framing: a mirror page is evidence of what
the mirror says, corroboration for a primary table, not a substitute for it.

## Extractor quota or failure

Fall back to `curl -sL <url> -o evidence/evNN.txt` (or a stdlib `urllib` fetch)
and strip tags if needed. Register the same URL in the ledger either way: the
source is the page, not the transport. Record which transport produced each
evidence file when the report's credibility depends on it.

## Cross-check discipline

- Two independent paths to one number is corroboration; one path is a claim.
  Say which you weight and why when they differ.
- Series that differ in level but agree in trend (census-derived vs UN
  estimates) are both worth reporting, each with its own id.
- Never mix time points: census is a zero-hour snapshot, annual bulletins are
  year-end, sampling surveys have their own reference date. Label each figure's
  time point or the whole table is unreadable.
- A number that only exists as a projection gets an explicit `[unverified]` or
  "本报告推算" label plus the method (e.g. linear extrapolation from the last
  five years) — never presented in the same voice as a measured figure.
