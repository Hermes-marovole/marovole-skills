# Meta Muse Zero-Cost Registration Transcript (2026-11-08)

Published: 2026-11-08

This is the verified field transcript from our registration session on 2026-11-07 / 2026-11-08 using Hermes Agent (or Claude Code) + ego-lite browser + free Simular Box (`https://box.simular.ai`) to register Meta Muse (`https://muse.ai`) and redeem 1 billion permanent tokens.

## 1. Local ego-lite + Simular Box Setup

- Browser tool: `ego-browser` (`ego-lite` v2.2.0), a Chromium browser designed for human users and AI Agents to share logged-in sessions.
- Command run by Hermes Agent: `npx -y @simular-ai/box connect --client hermes --yes` and `hermes mcp login box` (for Claude Code: `npx -y @simular-ai/box connect --client claude-code --yes`).
- Simular Box Free plan: `1,000 credits left today` (daily model credits that reset at midnight UTC).
- Box environment: 4-core, 8 GB RAM Ubuntu desktop (`cb-f4f6bb771a0b`), Google Cloud US IP `136.71.23.57` (`AS396982 Google LLC`, Council Bluffs, Iowa).
- After finishing tasks, the box is hibernated via `box_hibernate` (`state: hibernated`).

## 2. Muse Registration & Birthday Dropdown Trap

- Direct access from shared datacenter proxy (`179.255.121.235`, `AS906 DMIT Cloud Services`) was routed to the waitlist (`/access`).
- Using a clean Gmail account in Simular Box Chrome at `https://muse.ai/join`, `ego-lite` read the 6-digit confirmation code (`177620`) from the local Gmail tab and filled it into the box browser.
- Birthday page (`What’s your birthday?`): the default date is today (`November 7, 2026`). Submitting without changing the year to an adult year (`1992`) returns:
  `You aren’t able to create an account based on the information you provided.`
- Age verification page (`https://muse.ai/access/verification`):
  `Confirm your age. We use credit card information to verify your age. You may see a temporary authorization on your card.` Or verify with Instagram / Facebook.

## 3. Invite Code Redemption & Referral Code `VPNVCD`

- Invite friends modal text in Muse (`https://muse.ai/?activation_view=setup`):
  `Invite friends — Invite a friend and you'll both get 1 billion Muse tokens when they redeem your code in Settings within 48 hours of joining. VPNVCD`
- Redeem modal text in Muse:
  `Redeem a code — Redeem a friend's code within 48 hours of joining. You'll both get 1 billion Muse tokens.`
  `Congratulations! This invite code has been applied to your account.`
- Settings -> General -> Usage after redemption:
  `Free plan: Weekly limit resets on Nov 14 (0% used)`
  `Additional tokens: Never expires — 0% used (1B tokens left)`
- Generated referral invite code for our account: `VPNVCD`.

## 4. macOS Client Download (`Muse-11.1.dmg`)

- Unauthenticated request to `https://muse.ai/api/hatch/app-download/mac` returns `HTTP/2 403`.
- Homebrew cask `muse` was disabled on `2026-10-01` because it `requires a signed download URL, which is not supported by Homebrew`.
- Clicking `Download apps` inside the authenticated Muse web session redirects `https://muse.ai/api/hatch/app-download/mac` to a signed `fbcdn.net` URL for `Muse-11.1.dmg` (81.2 MB, Bundle ID `com.meta.endo`, version `11.1`).
