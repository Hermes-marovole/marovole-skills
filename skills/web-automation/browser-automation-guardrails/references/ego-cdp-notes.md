# Verified ego lite notes for guarded automation

## Network blocking (the reliable layer)

```js
await page.cdp("Network.enable");
await page.cdp("Network.setBlockedURLs", { urls: ["*refund*", "*withdraw*"] });
```

Substring wildcard patterns, no event handling. Verified: an in-page `fetch` to a blocked URL
rejects with `TypeError: Failed to fetch`; a non-matching URL still returns 200. Install it
**before** the first `goto()` — that removes the window between page load and guard injection and
covers Worker traffic that a page-script patch never sees.

Event interception (`Fetch.enable` + `Fetch.requestPaused`) works but needs a polling loop:
`page.events()` reads and *clears* the page's buffered CDP events, and `page.waitForEvent` only
handles `popup` and `download`. `setBlockedURLs` is the cheaper blacklist.

## Injecting the guard script

`page.evaluate(fn, arg)` accepts a second argument only for a function — a string expression
rejects it (`page.evaluate string expression does not accept an argument`). Embed the source as
JSON and eval indirectly:

```js
const body = (await readFile(GUARD_FILE, "utf8"))
  .split("// ==/UserScript==").slice(1).join("\n").trim();
await page.evaluate("((s) => (0, eval)(s))(" + JSON.stringify(body) + ")");
```

Injection lands after load: it runs the fetch/XHR patch and the dynamic sweep, so re-inject after
every full `goto()`/`reload()`; SPA-internal routing needs only the first pass.

## Locators and long-running page tasks

- **Text locators match hidden duplicates.** `page.click('text=召唤')` fails with
  `matched N elements (3 visible, 7 hidden)` whenever the label also exists in a collapsed
  dropdown, an inactive tab, or a mobile-only copy. Filter for rendered elements yourself:
  `await page.evaluate(() => [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === '召唤' && b.offsetParent)[0].click())`.
  Same trap for nav items and pagination arrows; when a stable attribute exists prefer it
  (`textarea[placeholder=…]`, `button[aria-label=…]`).
- **Poll an async product with short calls.** Each call sleeps then reads once, e.g.
  `sleep 120; ego-browser nodejs <<'EOF' … page.evaluate(() => document.body.innerText.slice(-2500)) EOF`.
  One call that waits minutes loses all progress on timeout; short calls are resumable and each
  result is readable on its own.
- **Judge completion from artifacts, not from the page.** A spinner, a rewritten session title, or
  the product's own "已完成" text are all unreliable; the file/artifact panel listing the output is
  the only signal. Download it and check it opens before reporting success.

## Script mechanics

- `ego-browser nodejs` takes the script on stdin heredoc or with `-e`.
- The script does not inherit shell env or cwd — every path it reads must be absolute.
- `help("page.cdp")` / `help("page.events")` / `help("page.fetch")` print the real signatures;
  `help("events")` answers "Unknown helper" because helpers are namespaced.
- `page.fetch(url, { saveAs: "/abs/path" })` carries the logged-in session — the cheapest way to
  take a report download out of the UI (layer 2) instead of guarding it.
