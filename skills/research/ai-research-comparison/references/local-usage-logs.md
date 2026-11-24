# Reading local subscription usage

Use this when a pricing comparison needs to be checked against the user's own accounts instead of a vendor page or a third-party dataset. The rule: measured tokens from the account win over any estimated allowance.

## Factory / Droid

Logs: `~/.factory/logs/droid-log-single.log` plus its rotated siblings `droid-log-single.log.<date>[.<n>]`. They cover only the days the files still exist, so state the date span instead of calling it a month.

Two line shapes, and they must not be added together:

- `INFO: [Agent] Streaming result` — one per request. Fields `inputTokens` (fresh, uncached), `cacheReadInputTokens`, `reasoningTokens`, `outputTokens`. This line has **no model id**.
- `INFO: [Session] Token usage restored from settings` — a **cumulative** total for that `sessionId` (`inputTokens`, `outputTokens`, `cachedTokensWritten`, `cachedTokensRead`). Summing these re-counts the same tokens once per time the session was reopened. Take the max per session, or ignore them and sum the streaming lines.

Join streaming lines to a model by `sessionId`. The model id (`"modelId":"..."`) appears on other lines of the same session, and the last one seen is the model those requests billed against. Then group by day.

Price it at the vendor's own published list rate for that model (fresh input, output, cache read, cache write are four different rates). Cache reads dominate, but a day with heavy fresh input changes the total a lot — report the split, not just one blended number.

Session transcripts under `~/.factory/sessions/**/*.jsonl` are the wrong place: the words "token" and "usage" in them are mostly code the model wrote, not metering.

## Claude Code

`~/.claude/projects/**/*.jsonl`, records whose `usage` object has `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`, next to a `"model"` and a `timestamp`.

Only sessions still on disk are visible. If the newest file predates the window you are comparing, say the local record does not cover that window — do not treat the sum as the week's usage. The Claude desktop app (`~/Library/Application Support/Claude`) stores no metering; its large directories are the bundled runtime, not usage.

A dashboard percentage and a token sum answer different questions. Quote both and show the time window each one actually spans before concluding one plan outlasts another.
