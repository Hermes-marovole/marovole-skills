# Apple Mail Fallback for x2doc — Session Notes

## Verified Working Pattern (2026-05-09)

When Resend API and Gmail SMTP are both unconfigured, Apple Mail via `osascript -e` chain is the reliable fallback on macOS.

### The Problem

Writing AppleScript to `.scpt` files (even with UTF-8 encoding) frequently fails with:
```
script error: Expected expression, etc. but found end of line. (-2741)
```

This happens regardless of file encoding or content length. The AppleScript parser in `osascript` appears to have issues with `.scpt` files in headless contexts.

### The Solution: `-e` Flag Chain

```python
import subprocess

cmd = [
    'osascript',
    '-e', 'set mailContent to "Your body here"',
    '-e', 'tell application "Mail"',
    '-e', '    set newMessage to make new outgoing message with properties {subject:"Subject", content:mailContent}',
    '-e', '    tell newMessage',
    '-e', '        make new to recipient with properties {address:"<YOUR_PRIMARY_EMAIL>"}',
    '-e', '        make new attachment with properties {file name:"/path/to/file.md"} at after last paragraph',
    '-e', '        send',
    '-e', '    end tell',
    '-e', 'end tell'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
assert result.stdout.strip().lower() == 'true'
```

### Critical Rules

1. **Body text must be ASCII-only** inside the AppleScript string. Chinese characters cause the same `-2741` error even with `-e` chains if they appear inside the quoted string.
2. **Escape order matters**: `.replace('\\', '\\\\').replace('"', '\\"')` — backslashes first, then quotes.
3. **The actual content lives in the Markdown attachment**, so ASCII body is fine. The user reads the attachment.
4. **Never use `.scpt` files** for this workflow. Always use `-e` chains.
5. **Launch Mail first and give the send ≥120s**: `open -a Mail`, wait a few seconds, then run the chain. `send` inside `tell application "Mail"` must launch Mail.app when it is not running, and a first-run automation-permission dialog blocks the AppleScript until someone clicks it — with `timeout=60` you get `TimeoutExpired` and no signal either way.
6. **A returned `true` is the only success signal, and still not proof**: confirm the message in Mail's Sent mailbox before telling the user it was sent. A timeout means "unknown", never "sent".

   Verify with a subject-substring query, not by eyeballing the app:
   ```bash
   osascript -e 'tell application "Mail" to get subject of (messages of sent mailbox whose subject contains "<subject fragment>")'
   ```
   An **empty result right after a `true` return means still queued / unconfirmed — say "sent but unverified" or "did not confirm", never "邮件已发送"**. Mail syncs the Sent copy asynchronously, so an immediate empty query is ambiguous rather than proof of failure; do not re-send on the strength of it (that risks a duplicate).

### For Chinese Email Body

If Chinese body text is absolutely required, load `macos-mail-utf8` skill which uses Python to generate a UTF-8 encoded `.scpt` file. However, our session showed even this approach can be fragile. The practical workaround is: ASCII body + Chinese content in attachment.

### Account Verification

```bash
osascript -e 'tell application "Mail" to get name of accounts'
# Returns: Google, iCloud, Exchange, etc.
```

The account must already be configured in Mail.app. No additional auth needed.

---

Session: x2doc mlx-audio v0.4.3 post, 2026-05-09
Resolved: yes

### Re-verification
- **2026-05-09 (Ladder + Polymarket x2doc post)**: Same `-e` chain pattern, same ASCII-only body + attachment approach, returned `true`.
- **Later sessions**: the same chain hung past a 60s timeout with Mail.app not running — see Critical Rules 5–6. Treat it as "works when Mail is already running and the automation grant exists", not as unconditionally stable, and never let it hold up delivery.

## Fastest route: the bundled Mail helper

`python3 ~/.hermes/scripts/send-xpulse-daily-email.py <path-to-file>` hands the file to Mail.app in one call and prints `OK emailed via Apple Mail: <subject> -> <to> (cc <cc>)`. Try it as the first Apple Mail attempt when `mail-cli` fails its upstream (`COREMAIL_UPSTREAM_ERROR`): no `-e` chain, no ASCII-body constraint (Chinese body is fine), CC already wired to the secondary mailbox, and the printed OK line is quotable proof of delivery.

Caveat: its subject is pinned to the daily-digest format (`📡 AI/科技日报 | <date>`), not the x2doc subject. If the subject line matters (`x2doc 整理完成 - {topic}`), use the `-e` chain above; otherwise send with the script and report its OK line verbatim.
