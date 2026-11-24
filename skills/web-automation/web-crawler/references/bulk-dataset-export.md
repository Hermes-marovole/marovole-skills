# Bulk dataset export: handing over all the data as a directory

Triggered when a crawl or reverse-engineering result must be delivered as files rather than described (「所有的数据都要，CSV 和 JSON 都要」). The unit of delivery is a directory with paired formats, a generated manifest, and a README that explains each table.

## Layout

```
<dataset>/
  README.md                      # inventory table + per-library notes + licence line
  dataset_manifest.json          # machine-readable inventory
  dataset_manifest.csv           # same inventory, for Excel
  01_<source-library>/<name>.json
  01_<source-library>/<name>.csv
  02_<source-library>/...
  _scripts/                      # the extractors, kept with the data
  _cache/                        # JSONL checkpoints for resume
```

Number the library directories in the order the site exposes them (`01_`, `02_`) so the tree matches how a reader navigates the source. Keep `_scripts/` and `_cache/` inside the dataset so a future run is reproducible, and drop `.metadata_never_index` in each so Spotlight does not chew through 300 MB.

## Rules

1. **One stem, two formats.** Every table gets `X.json` and `X.csv` produced from the same records — never JSON only, never CSV only. The user opens CSVs in Excel and feeds JSON to code; both must exist for every table.
2. **CSV in `utf-8-sig`.** Plain UTF-8 Chinese in Excel is mojibake on Windows and in many macOS Excel builds; the BOM is what makes it open correctly. Read it back with `encoding="utf-8-sig"` too.
3. **Flatten before serialising so both formats agree.** If the JSON stays nested while the CSV is flattened, the manifest reports two different widths for the same table (13 keys vs 197 columns) and every reader distrusts the whole export. Build one list of flat dicts, then write JSON and CSV from that same list.
4. **Ship wide + long for anything with a variable field set.** Wide (one row per record) is what humans filter in Excel; long (one row per observation: `record_id, nutrient, value, unit`) is what goes into SQL or a vector store and survives schema changes. Both, from the same source.
5. **Generate the manifest by reading the finished files, not from counters inside the extractor.** Walk the tree and record path, format, record count, field/column count, and size per file. Hand-maintained totals drift the moment a stage re-runs; file-derived ones cannot.
6. **Build the README inventory table from the manifest.** Same loop, same numbers — the only way prose and data stay consistent. State total file count and total size at the top.
7. **Verify every count against the source total and report the residual.** Row counts matching the source does not mean the rows are full: newly ingested records often carry only an id, a name and a barcode. Report completeness per field with percentages (barcode / manufacturer / ingredients / nutrients) and say how many records are shells, instead of presenting the export as uniformly complete.
8. **Distinguish derived fields from observed ones.** Recomputed values (NRV%, unit conversions, decoded encodings) get their own column plus a README note; inferred labels get an `inferred_*` prefix. A reader must be able to tell what the source said from what you computed.
9. **Close with the licence line.** One sentence naming the data owner and restricting reuse to internal research. The export is a copy of someone else's database; say so.

## Long extractions

Anything past a few thousand records will be killed mid-run, so the extractor is resumable by construction (see `reverse-engineering` → `references/server-rendered-legacy-apis.md` §11): append JSONL per record, resume from the cache, re-invoke until the residual is zero, then compile both formats once. Call `csv.field_size_limit(20_000_000)` before reading back — long text columns overflow the default 131072 limit and raise `_csv.Error: field larger than field limit`.

## Reporting back

The chat message is a map of the directory, not a log: one line per library saying what it holds and how complete it is, the absolute path, the manifest attached as `MEDIA:<path>/dataset_manifest.csv`, and the auth-walled sibling hosts you deliberately did not touch. Counts in prose must match the manifest.
