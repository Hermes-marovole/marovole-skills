# grounding.py — evidence store, gate, independent review

Path: `~/.hermes/scripts/grounding/grounding.py` (stdlib; PyYAML for review). Store: `evidence/<DATE>/index.json` + `<sha1>.txt` under the HermesWork evidence root (`fetch` prints each text path; use that path rather than assuming one); `check` also looks back 2 days so downstream jobs reuse upstream fetches.

## Commands
```
G=~/.hermes/scripts/grounding/grounding.py
python3 $G fetch  --date D URL...              # OK/BAD, published=, chars, text file path
python3 $G show   --date D URL                 # record + first 1500 chars
python3 $G check  --date D --kind K FILE...    # K: briefing | tietu | longform
python3 $G review --date D --kind K FILE...    # parallel, log -> evidence/D/review.log
```

## Schemas
- briefing sidecar item: `title, summary, date, sources[{label,url}], evidence[{url,quote}], derived[{value,from}]`
- tietu post.json: `evidence`/`derived` at top level; checked text = title+subtitle+hook+facts; review also sees take+caption.
- longform: `<dir>/evidence.json` = `{"a-brief.md": {"evidence": [...], "derived": [...]}, ...}`; every markdown link must be fetched; `a-*` checked for freshness per `###` section.

## What check enforces
- Every evidence/source URL fetched and OK (404/410 recorded dead at fetch time).
- Quote ≥15 chars, found in fetched text after normalization (markdown links stripped, curly quotes/dashes unified, ALL whitespace removed — extracted text drops spaces around links).
- Every ≥2-digit number in the draft appears in the source texts, or is declared in `derived` whose `from` is in the source. Leading `M/D` per field and full dates are exempt.
- Freshness by newest source publish date vs max age; item `date` within 1 day of a source publish date; no determinable source date → error (add a dated source).

## Review
- OpenAI-compatible call to `config.yaml providers.<GROUNDING_REVIEW_PROVIDER>` (default dogbooks) with `GROUNDING_REVIEW_MODEL` (default gpt-6-luna). Must differ from the writer model.
- Output `{ok, issues[{claim,problem,severity}]}`; any high → FAIL, exit 1. Reviewer sees each source truncated to ~20k chars (per-source budget = max(20000, 160000/n_sources)); `check` verifies quotes against the FULL local text, so a long fetched page can pass check but the reviewer still cannot see deep-position content.

### Reviewer returns empty content (`'content'` error)
A FAIL whose message is a bare `'content'` (KeyError on the choices payload) is not a factual verdict: the reviewer model spent the whole `max_tokens` budget on reasoning tokens, so `choices[0].message` carries no `content` and `finish_reason=length`. Confirm in `evidence/D/review.log`, then rerun on the default chain (Neuma-opencode → magpie → dogbooks, all gpt-6-luna-class) — it handles a full ~18k-token long-form draft. Drop any `GROUNDING_REVIEW_MODEL` override first: the variable takes a literal model id, so a retired name fails as a bare `HTTP Error 404: Not Found` that reads like a broken script and sends you hunting through provider configs. Keep an override only after one smoke call returns `{'ok': True, 'issues': []}`. Payload size is not the variable; the model is. Never edit the draft in response to this error.

### Competitor / product comparison pieces
Review checks every attribute asserted about the *other* product against the fetched sources, and brand-level intuition is not a source. Recurring shapes:
- Integration/connector lists must be copied item by item from the source list; never add a service the product "obviously" also supports — a CRM name that appears in no source list is a high-severity FAIL.
- Never state which company's models or infrastructure a competitor runs on unless a source says it; write what the source documents instead (where it runs, what bundle it is sold in).
- Keep directionality honest: a one-way import is 「从 X 导入」, not 「互导」/「互通」.

### Long fetched sources hide numbers from the reviewer
For long pages (full-text papers, position stands) keep the numbers you cite inside the FIRST ~20k chars of the fetched text. Pick quotes that sit in the visible head, or add a shorter dated source (press release, expert reaction, abstract) whose whole text is visible, and lean on that for the numbers. Never assume check-passing quotes are reviewer-readable.

The same budget applies to long LOCAL files cited as evidence (nightly-lessons ledgers, long READMEs, changelog dumps): a quote 40KB into a 50KB file passes `check` (full-text match) and is invisible to `review`, which then reports the claim as unsupported. Quote from the head, or split the needed passage into its own small evidence file and cite that — do not delete an accurate claim merely because the reviewer cannot see that far.

### Unfetchable primary sources (own transcripts, personal measurements)
When a claim's only source is locally produced content (own whisper transcript, own ffprobe measurement), publish the excerpt somewhere fetchable, then cite it like a URL. Working recipe for a talk transcript: strip any copyrighted lines, commit the needed chapter excerpt to the Superpowers repo, push, and `grounding.py fetch` the raw GitHub URL — one fetch covers it. In the article itself label the claims '转写稿' and point readers to the original video; the reviewer will not accept the author's own operations ('我下载了', '我实测 46 分钟') as facts — delete or hedge them. Expect several review→edit→review rounds for a long-form piece with many at-tributed quotes; fix only the exact flagged sentences each round, do not mass-rewrite.

### Translated / paraphrased long-form (English source → Chinese article)
The reviewer checks every Chinese paraphrase against the English text, so drift that reads as harmless still FAILs. Before submitting, check the draft for these:
- Titles and leads must not widen the subject or the claim. If the source says "we keep urging people to be more ambitious", do not write "大多数人野心不够".
- Do not resolve relative time yourself: "this April" must not become "今年 4 月". Attribute it ("原文写的是 this April") or drop it.
- Do not add qualifiers the source lacks: "刚发布时" for "announced as", "本来", "独占 N 天", "拼了命" for "trying really hard". Each one introduces a new claim.
- Hedged suggestions ("it might be useful to…") must stay hedged. Do not turn them into steps ("再组个红队").
- When the author paraphrases a book or study, write "他转述/他提到", not "书里说/研究总结".
- Before translating, re-read the exact source sentence in the local text file. Use precise domain terms (e.g. forensic accountant = 法证会计师).
Check can pass while review still fails, so budget 3–5 review rounds. Fix only the flagged sentences each round.

### Quotes and dates for X posts
- Copy quotes from the local fetched `.txt`, not from web_extract or chat output. Jina renders emphasis as `_x_` and curly apostrophes, so quotes copied from other renderings fail check.
- An x.com status fetched via Jina gets `published=` metadata, but the body text has no date. To cite the post date ("10 月 13 日"), also fetch `https://api.fxtwitter.com/<handle>/status/<id>`. Quote its `"created_at":"Tue Oct 13 15:02:07 +0000` as evidence, and declare the day in `derived` with `from` set to that string.

## Fetch quirks
- r.jina.ai first (clean text + `Published Time:`), but it returns 403 to browser User-Agents — call it with a plain UA. Direct fetch uses a browser UA.
- Jina text drops page headers (date, byline); when direct HTML is available, prepend a `【页眉】` snippet around `<h1>`. Don't skip `<header>` when parsing — dates/h1 often live there.
- Publish date order: jina header → meta (`article:published_time`, `datePublished`) → first date near h1 → first date in text head. Parse RFC-2822 (`Wed, 01 Oct…`) as well as ISO.
- Sites blocking direct fetch where jina gives no date (e.g. openai.com) need a second, dated source.
- Evidence URLs need not be HTML: a raw GitHub blob works and `fetch` stores its text like a page — useful for hosting an excerpt as an evidence source.
- Europe PMC REST endpoints may be fetched directly, but pubmed.ncbi.nlm.nih.gov often returns a cookie/recaptcha wall via jina — prefer Europe PMC or the journal page for abstract-level citations.

## neuma-briefing integration
`scripts/briefing.py leads DATE` → `data/DATE.leads.md` (HN Algolia 48h >100 pts, AI-filtered + official/media RSS). `validate` = schema + link liveness + grounding check; `publish` = validate + review, refuses on any failure. `BRIEFING_GROUNDING_SKIP` / `BRIEFING_REVIEW=0` are manual-emergency only.
