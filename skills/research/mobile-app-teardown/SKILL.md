---
name: mobile-app-teardown
description: Use when tearing down mobile apps via emulator and ADB.
version: 1.4.0
author: 智子 (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [mobile-teardown, android-emulator, mumuplayer, adb, agent-device, competitor-analysis, paywall-audit]
    category: research
    related_skills: [market-intelligence, grounded-citations, homebrew-app-management]
---

# Mobile App Teardown (安卓模拟器与真机 Agent 竞品拆解)

Steady, evidence-driven workflow for installing commercial mobile apps on macOS (MuMuPlayer Pro, official AVD, or USB physical phone) and driving them via `agent-device` + `adb` to capture pixel-exact funnels, UI node trees, AI prompt responses, and paywall dark patterns.

## When to Use

- User asks to install/test a mobile App (Android APK or competitor App) on Mac to do product teardown, onboarding/paywall funnel audit, or AI feature benchmarking.
- Desktop web research (`market-intelligence`) cannot reach App-only flows (native onboarding quizzes, mobile paywalls, AI dietitian/coach chats, mini-tools, or WeCom private-domain intercept modals).
- Verifying external user complaints (e.g., Black Cat / App Store 1-star reviews about hidden close buttons, forced upsells, or stripped features) with pixel-level and node-level ground truth.

## Goal

Produce a 100% first-hand mobile product teardown backed by local `.png` screenshots and raw `.json`/`.txt` accessibility node dumps—covering onboarding funnels, generated plan math, core daily loops, AI assistant boundaries, feature gates, and monetization dark patterns—without relying on secondary media summaries.

## Success Criteria

- Emulator/device runs at mainstream smartphone portrait proportions (`1080×2400` `20:9` at `450 dpi`, logical width `384 dp`), never default `3840×2160` 4K tablet mode.
- Official APK is downloaded (bypassing proxy with `--noproxy '*'` for domestic CDNs) and MD5/size-verified before `adb install`.
- Every tested screen saves both `<step>_<tag>.png` and `<step>_<tag>.json` (or `.txt` via `agent-device snapshot --force-full`) into a durable `evidence/` directory.
- Teardown evaluates **6 production stages** (Onboarding → Plan Generation → Core Daily Action → Domain/AI Guidance → Retention/Follow-up → Monetization Gate), pairing every strength ("Where They Win") with its cost or failure mode.
- Pixel measurements of dark-pattern UI (e.g., hidden close icons, overlapping CTAs) convert raw `px` to physical `dp` using actual device density (`dp = px / (dpi / 160)`), checked against Android's `48×48 dp` touch target baseline.

## Constraints

- **Carrier selection by anti-emulator risk** — 先免费后付费:
  0. **Free-first ladder on Apple Silicon**: BlueStacks Air (免费、原生 arm64、Android 13、内置 Google Play，ADB 在 `127.0.0.1:5555`) → Google `arm64-v8a` AVD (免费、快照复位) → USB 真机 + `scrcpy`。多数竞品调研在第一档就能完成，不要默认买 MuMu。MuMu Pro 的 macOS 版是 **7 天试用的订阅制**（连续包月 ¥28/30 天），价格渠道与 App Store 同名陷阱见 `references/emulator-and-agent-device-pitfalls.md` §0。
  1. **Domestic commercial apps** (health, e-commerce, lifestyle): default to **MuMuPlayer Pro** (`mumutool open 0` + `adb connect 127.0.0.1:16384`), which spoofs real phone models (e.g., `SM-S9110`) as `android device`.
  2. **Overseas SaaS/AI apps needing rapid multi-persona state resets**: use Google official `arm64-v8a` AVD (`emulator -avd <name>`) with `adb emu avd snapshot save/load`.
  3. **Hardened super-apps** (WeChat, Xiaohongshu, finance) that crash or ban emulators: plug in a USB physical Android phone + `scrcpy --stay-awake`; drive via the exact same `adb` + `agent-device` commands.
- **Safety & compliance red lines**:
  - Never submit real payment orders (WeChat Pay / Alipay / Apple Pay), medical prescriptions, or public community posts/comments.
  - **Batch every login wall into one hand-off**: domestic apps hard-gate nearly every screen behind phone-OTP login with no usable guest mode. Before driving the first app, resolve and `adb install` the WHOLE product queue, then ask the user once to log into all of them in the desktop emulator window. One OTP round for the queue beats one interruption per product; resume automation only after that confirmation.
- **Queue discipline — one product at a time**: when the user supplies a prioritized competitor queue, drive, evidence and deliver product N's report before touching product N+1. Never interleave two products' evidence directories or batch all reports to the end; every delivery must be independently verifiable on disk at the moment it is announced.
- **One fixed benchmark question set for the whole queue**: before driving product #1, write down the probe questions as exact strings and reuse them byte-identically on every product — typically one *state-creating* prompt (log a meal / log a workout / add a supplement), one prompt whose best answer is only possible if that state carried over, and one domain-safety prompt. A cross-product comparison table is defensible only when every cell came from the same input; free-form "ask something relevant" probes yield quotes that cannot be laid side by side.
- **Accessibility tree discipline (`agent-device`)**:
  - Do not rely solely on `agent-device snapshot -i`: custom Android views often place `clickable=true` on an unlabeled `ImageView` avatar while keeping the sibling `TextView` caption non-clickable (invisible to `-i`).
  - Pass `--force-full` when re-reading (`agent-device snapshot --force-full`) so cached unchanged snapshots are not elided.
  - Use `agent-device snapshot --raw --force-full` (NDJSON) whenever you need **untruncated long text** (AI replies, legal footnotes) or exact `rect` coordinates.
  - When a screen emits `<15` nodes (WebView hero cards, Flutter/Canvas overlays, retention modals), immediately inspect the `.png` with `vision_analyze`.
- **包体本身也是取证对象，模拟器会掩盖兼容缺陷**：装之前 `unzip -l <file>.xapk`（或解包 `.apk`）看 `config.*.apk` 分片，只有 `armeabi_v7a` 没有 `arm64-v8a` 就说明只发 32 位包——在 arm64 模拟器上照装不误，到纯 64 位真机直接 `INSTALL_FAILED_NO_MATCHING_ABIS`。这类「安卓工程粗糙」结论只能从包体读出来，不能从「我这儿跑得很顺」反推兼容性好；顺带把商店页最新评论里的登录/闪退抱怨与原包 ABI 并列写，才构成一条硬证据。
- **Report integration**: when merging an App teardown into an existing company research report (`market-intelligence`), reorder chapters to **Product First, Capital Second**, keep existing `[1]..[N]` citations unshifted, and append new App evidence entries at `[N+1]..`.

## How to Use

1. **Environment & aspect-ratio check**:
   ```bash
   python3 ~/.hermes/skills/research/mobile-app-teardown/scripts/adb_teardown_probe.py check
   # Normalize MuMu VM 0 to 20:9 flagship phone (1080x2400 @ 450dpi) if needed:
   python3 ~/.hermes/skills/research/mobile-app-teardown/scripts/adb_teardown_probe.py resize --index 0 --size 1080x2400 --dpi 450
   ```
2. **Capture evidence per step**:
   ```bash
   python3 ~/.hermes/skills/research/mobile-app-teardown/scripts/adb_teardown_probe.py dump \
     --out-dir ./evidence --tag 01_onboarding_step1
   ```
3. **Probe domain edge cases**:
   - Check pre-sale preview numbers vs post-onboarding home numbers (static template vs real calculation).
   - Compare today vs future/past dates and free vs VIP quota (`0/1` daily locks).
   - Send the fixed benchmark question set to in-app AI assistants and capture verbatim replies via `--raw`. Run the state-creating prompt FIRST, then the follow-up that can only be answered well by reusing that state — that one-two ordering is what exposes genuine cross-turn memory versus a stateless chatbot.
   - **Map the identity gate, not just the paywall**: tap every row under 「我的」 (药箱 / 健康档案 / 设备管理 / 订单 / 客服 / 设置) and every personal-data sub-tab, capturing the intercept modal each one throws. A super-app showing zero price and zero in-chat ads usually monetizes through a real-name / account-binding wall on personal-data modules instead; that entry-point → required-binding → what-unlocks matrix *is* the commercial model and belongs in the report as a table.
4. **Confirm what the user left on screen before announcing a handoff**: `adb -s 127.0.0.1:16384 shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'`. The package + activity it prints is the only proof of which app is actually in the foreground at this moment; naming the wrong app in a "stuck at login, log in please" message costs the user a wasted round.
5. **If the ask is "what data does this app have", go from dex to live API**: harvest the Retrofit annotation paths, read the client class for per-namespace base URLs, replay the interceptor's full header set, and use a guest token rather than the user's session — see `references/api-surface-extraction.md`. A decompiled endpoint list is a hypothesis until a real JSON payload comes back from curl. When the app is a nutrition/diet/tracker product and the ask is about building a dataset, carry the probe over to the `food-composition-database` skill and read its app-nutrient-api-probe reference: the decisive question there is whether the API is a real data source or only a naming/serving-basis reference, settled by counting how many nutrient slots carry data versus placeholder zeros.

See `references/emulator-and-agent-device-pitfalls.md` for APK sourcing recipes, the hard-login-gate evidence protocol, WebView dark-pattern coordinate math, cross-turn AI memory probes, and multi-persona testing patterns. See `references/packed-apk-unpacking.md` for 360-jiagu packed APKs: root on MuMu, renamed frida-server, the sign-then-adler checksum fix order, rebuilding an analyzable APK, and the native-only dex memory scan to use **when the Java bridge returns nothing** (fall back to it rather than concluding the app has anti-debugging). See `references/api-surface-extraction.md` for the step after unpacking: Retrofit endpoint harvesting, the client class's base-URL/SSL/interceptor wiring (and why an unwired `trustAllCerts()` is dead code, not a finding), header-set reconstruction, guest-token auth, and live curl verification. `templates/report_html_builder.py` is the copy-and-edit markdown→single-page-HTML report builder (light theme, KPI cards, verdict cards, citation anchors, evidence galleries, plus a broken-image/anchor/placeholder verification pass) used for every delivered 调研报告.

## Stop Rules

- **Pause for user**: login wall requiring SMS OTP/OAuth, real-name medical verification, or any action with irreversible account/financial side effects. Probe for a guest route at most twice (visible close icon, then `adb shell input keyevent 4`); if the screen survives both, stop hunting and hand off — hidden guest entry points cost many calls and usually do not exist.
- **Stop exploration**: once all 6 production workflow stages and all bottom-bar tabs have verified `.png` + `.json`/`.txt` artifacts on disk. Do not crawl infinite community feeds.

## Verification

Before delivering the teardown report:
1. Confirm `adb shell wm size` and `wm density` match the stated screen spec (`1080x2400`, `450 dpi`), and verify all `dp` calculations use `px / (dpi / 160)`.
2. Verify every verbatim quote in the report matches the raw `label` field in `evidence/*.json` without unannounced edits or added numbering.
3. Verify every `<img src="...">` and `[E*]` / `[n]` citation anchor resolves cleanly on disk with zero `{{...}}` placeholder residue.
4. **独立 subagent 逐条核查 + 自己复算**：把报告里的每个数字、类名、结论列成清单交给一个独立 subagent 对照本地包体与原码核（这是用户的硬红线，不可省）。subagent 报回的修正要再自己验证一遍，尤其单位换算——按原始字节重算，不要直接采信它的 MB/MiB 结论。核查重点永远是**结论级**错误而非措辞：本次 56 条断言里 12 条需改，其中 3 条推翻了结论（所谓「原地加密」并不存在、「信任任意证书」是死代码、AES 只解下行不加上行）。排版和标签检查发现不了这三条。
5. 报告成稿后删掉被取代的旧版本文件，只留当前版本号，避免用户打开带错误数字的那一份。
