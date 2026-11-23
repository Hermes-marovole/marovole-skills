---
name: browser-automation-guardrails
description: Harden AI browser automation against dangerous buttons.
version: "1.0.0"
author: Hermes Agent
license: MIT
metadata:
  version: "1.0.0"
  hermes:
    tags: [browser-automation, security, guardrails, merchant-backend]
    related_skills: [ego-browser, coding-agents]
---

# Browser automation guardrails

## When to Use

- An agent or automation script must operate a production console (merchant, admin, ad, payment)
  where the flow needs only reads but the UI also exposes refund / withdraw / delete / repricing.
- A project asks how to keep an AI-controlled browser away from high-risk buttons, or wants a
  reusable guard kit handed to several projects or colleagues.
- Not for scraping public pages, and not a substitute for server-side permission design.

When an agent drives a production backend (merchant / admin / ad console) whose flow only
needs reads — reports, exports, status checks — but the same UI ships refund, withdraw,
delete, edit-price buttons, the goal is a **minimal visibility surface**, not a well-behaved
agent. Never rely on the prompt to keep an agent away from a button it can see.

## Layer stack — build from the top, always stack the last two

1. **Server-side permission downgrade** — a read-only sub-account/role, so dangerous controls
   are never even served. Do this first when the backend supports it.
2. **Interface direct fetch** — if the operation is "download yesterday's report", grab the
   endpoint in F12 Network and call it with the session; the UI leaves the flow entirely.
3. **DOM guard** — CSS-hidden + capture-phase click interception in the page.
4. **Network blocklist** — dangerous path substrings aborted at the network layer.
5. Prompt constraints / step confirmations — the weakest layer. Never the only layer.

3 alone cannot stop requests a page script never sees (Service Workers); 4 alone cannot stop
an agent that keeps trying to click. Layers 3 and 4 are always installed together, and 1/2
replace rather than supplement them when available.

## Procedure

1. Ask two routing questions: does the backend support read-only sub-accounts? is the routine
   flow just "fetch data"? Either answer routes to layer 1 or 2 and demotes the rest to insurance.
2. Otherwise install the guard kit — `kit/` in this skill directory (README tutorial,
   `guard.user.js`, Playwright and ego adapters, all placeholder-parameterized). The same guard
   script is also at `templates/guard.user.js`.
3. Fill the guard's three blacklists: `@match` (one line per domain, **each embedded iframe
   domain needs its own line**), `SELECTORS` (F12 → Copy selector), `TEXTS` (universal corpus,
   delete-only — adding broad words like 确认 blocks normal flows), `ENDPOINTS` (while a human
   clicks the dangerous action once, record the path substring from Network — host not needed).
4. Mirror `ENDPOINTS` into the adapter's blocklist (`blockSubstrings` / `BLOCKED_URLS`). The two
   lists live in different files and drift silently; the acceptance checklist re-checks them.
5. Install per harness:
   - Playwright: `context.addInitScript({content: body})` (document-start, all frames, no
     gap window) + `context.route('**/*', …)` aborting on method/substring.
   - ego lite: `Network.setBlockedURLs` **before** the first `goto()`, then inject the guard
     after each full navigation. See `references/ego-cdp-notes.md` for the verified calls and
     the `page.evaluate` string-argument quirk.
6. Run the acceptance checklist and give it to the project as regression tests.

## Mechanics rules (mechanism stated, because each one was a real failure mode)

- Hide with `display:none` + an attribute flag, never `removeChild` — the framework (React/Vue)
  still holds a reference to that node and crashes on its next update.
- `visibility:hidden` and overlay masks are NOT protection: a DOM-driven agent reads the
  accessibility tree, a screenshot-driven agent sees through translucent overlays.
- Intercept clicks in the capture phase (`addEventListener('click', fn, true)`) walking
  `e.composedPath()` — this is the only way to also stop `el.click()` from a script, which skips
  coordinates and would otherwise reach page listeners first.
- Re-sweep after dynamic rendering (MutationObserver + interval) — SPAs render the dangerous
  button long after `DOMContentLoaded`.
- Document the kit's boundary explicitly: it stops UI-level misclicks, not an agent typing a
  dangerous value into a normal form. That residual risk is answered only by layer 1.

## Acceptance checklist (deliver with the guard)

- Screenshot of the backend after install: no sensitive button visible.
- Manual click attempt on a sensitive control: guard log line prints, nothing fires.
- In-page `fetch` of a blacklisted endpoint returns `TypeError: Failed to fetch`.
- The normal business flow still completes, un-blocked (a wrongly hidden button is harder to
  debug than a missed one, so err narrow).
- Both blacklist copies (guard file + adapter) are identical.

## Delivering to projects

A tutorial for other projects is a kit, not a message: README with the layer table, F12
config-filling steps, copy-pasteable adapter examples for each harness, and the acceptance
checklist. All project-specific values are placeholders (`merchant.example.com`) — strip
personal absolute paths before handing a file out; a hand-out copy keeps its own guard script
and the two copies must be re-synced after any blacklist edit.

Attach files with `MEDIA:` pointing at a **file**. A directory path produces a card that cannot
be downloaded — zip the folder first (`zip -r kit.zip kit/`) and send the zip plus individual
file cards.
