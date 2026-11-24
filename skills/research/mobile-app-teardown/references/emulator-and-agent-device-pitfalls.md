# Emulator & `agent-device` Field Pitfalls (实机拆解避坑手册)

## 0. 载体选择与授权成本（先定模拟器，再谈拆解）

M 系列 Mac 上的安卓载体按 **免费优先** 排序，绝大多数竞品调研在前两档就能做完，不要默认买 MuMu：

| 档位 | 载体 | 免费? | M 芯片 / Android | 什么时候用 |
| --- | --- | --- | --- | --- |
| 1 | **BlueStacks Air**（蓝叠 Mac 版，`bluestacks.com/mac`） | 免费 | 原生 arm64 / Android 13 | 免费平替 MuMu：内置 Google Play、可直接拖 `.apk` 安装、支持多开；启动器有推广位 |
| 2 | **Google `arm64-v8a` AVD**（cmdline-tools / Android Studio） | 免费 | 原生 arm64 / 最新 API | 需要 `adb emu avd snapshot save/load` 秒级复位新用户态、或多轮 A/B 时 |
| 3 | **USB 真机 + `scrcpy --stay-awake`** | 一次性硬件成本 | 真机 | 强风控（微信/小红书/金融/部分健康大厂）识别模拟器时，100% 过风控，命令与模拟器完全一致 |
| 4 | **MuMuPlayer Pro**（macOS） | 订阅制 | arm64 / Android 12 | 只有需要真机机型伪装（`SM-S9110`）+ 国内桌面体验时才付费 |

### 0.1 BlueStacks Air 的 ADB 入口

- 端口固定 `127.0.0.1:5555`：`adb connect 127.0.0.1:5555`。与 MuMu 的 `16384` 不同，**换载体后先改 `adb -s` 目标**，否则命令会静默打到上一个实例上。
- 开关在 `设置 → 高级 → Android 调试（ADB）`。第三方自动化文档与 MAA 官方文档对此**互相矛盾**（前者称 Air 的设置里没有 ADB 开关）：以当前安装的那一版实测为准，不要据任何一边的文档下结论。
- App 包内自带 adb 与磁盘工具：`/Applications/BlueStacks.app/Contents/MacOS/hd-adb`、`qemu-img`；配置在 `/Users/Shared/Library/Application Support/BlueStacks/bluestacks.conf`（键名与 Windows 版一致）。系统无 `adb` 时 `brew install --cask android-platform-tools`。
- 各实例监听各自端口，其余实例从 `5555` 起顺延（`5625`…）；按固定顺序启动实例，端口才稳定。

### 0.2 MuMu Pro 的真实价格与渠道（报价必须带渠道）

- **国区 Mac 客户端（微信/支付宝扫码）**：官方唯一写死的价格是 **连续包月 ¥28 / 30 天**，到期前 24 小时自动扣款；取消要去微信/支付宝的「自动续费/免密支付」里关，**App 内没有取消入口**。30 / 90 / 365 天单期档只在客户端「个人中心 → 购买/续费」里报，官网帮助页不写死金额；社区可查的年卡在 **¥239–279 / 年**（周年活动叠优惠码可到 ¥258 上下）。
- **掌上 MuMu（iOS App Store 远程控制端）**：`¥18/月`、`¥50/90 天`、`¥178/365 天`。**这是另一个产品，不能用于 Mac 模拟器**，但大量第三方「价格说明」站点把它当成 Mac 版报价抄。看到这几个数字先追问「哪个渠道」。
- **国际版 MuMuPlayer Pro**：`$10 / 30 天`、`$27 / 90 天`、`$72 / 年`，比国区贵约一倍，别给国内用户推荐。
- **一个账号约 5 台设备**（客服口径 + 社区多人实测），每次登录要手机验证码。这正是 V2EX / PTT 长期拼车帖的成因，均摊 **¥47–56 / 年**；用户问「最划算的订阅方式」时，拼车是必须并列给出的选项，并说明中转验证码的麻烦。
- Genymotion Desktop 的 Personal 免费授权在 M 芯片上仍需 Rosetta，且条款不含商业用途；公司调研不要把它列成免费方案。

> 价格结论必须落在「渠道 + 是否自动续费 + 起算周期」三件事上，并标明来源类型（官方帮助页 / 客户端实读 / 社区帖）。只给一个裸数字，等于给了一个随时会错的说法；官网未写死的档位宁可写「需在客户端实读」，也不要从二手站点补全。

## 1. Window Aspect Ratio & Resolution Normalization

MuMuPlayer Pro on macOS defaults new VMs to `3840×2160` (`16:9` 4K landscape, or `2160×3840` `9:16` fat tablet-like portrait when auto-rotated) at `540 dpi`. That causes two problems:
1. Screenshots bloat to 2–3 MB per frame and distort modern `20:9` mobile responsive layouts;
2. `9:16` hides less vertical scroll context than real smartphones (`19.5:9`–`20:9`).

**Standard Phone Spec**: `1080×2400` (`20:9` FHD+) at `450 dpi` → logical viewport `384 × 853 dp` (`scale = 450 / 160 = 2.8125`), matching Samsung Galaxy S23 (`SM-S9110`), Xiaomi/Huawei flagships, and iPhone Pro logical widths (`390–393 pt`).

Always convert pixel hitboxes to physical `dp` using actual `wm density`:
```
dp = px / (density_dpi / 160)
```
Compare close buttons / secondary opt-out links against Android Material Accessibility minimum touch target (`48 × 48 dp`). Never guess `dp` without reading `adb shell wm density`.

## 2. Domestic APK Sourcing on macOS (Proxy & Bot-Gate Bypass)

- **Bypass proxy for domestic CDNs**: curl/python requests through overseas clash/surge proxies slow down or trigger 403/567 blocks on Tencent (`imtt2.dd.qq.com`) and Qihoo (`s.shouji.qihucdn.com`). Always pass `--noproxy '*'` for domestic CDN downloads.
- **Tencent Yingyongbao (`sj.qq.com`) EdgeOne JS challenge**: direct `curl` on `imtt2.dd.qq.com` returns a 988-byte HTML `<script>` setting `__tst_status` + `EO_Bot_Ssid` cookies or an EdgeOne `567` page.
- **Fast clean alternative**: scrape the app detail page on 360 Mobile Assistant (`https://app.so.com/detail/index?id=<id>` or search by package name `com.xxx.xxx`), extract the signed `https://s.shouji.qihucdn.com/<yymmdd>/<md5>/<pkg>_<ver>.apk?...` URL, download with `curl -L --fail --noproxy '*'`, and verify `md5 <file>.apk` against the `<md5>` path segment before `adb install`.
- **Never retype the APK URL**: that 32-hex path segment *is* the integrity hash, so one hand-copied character 404s the request and the file silently never lands. Re-resolve the URL from the detail page inside the same command that downloads it, then print `expected` (path md5) vs `actual` (`md5 -q`) plus `ls -lh` before installing — `curl -s` leaves no visible trace of a failed fetch.
- **One app per download command**: `?curpage=&exp=...` URLs are `&`-heavy, and a long multi-app shell block mixing several of them can be rejected by the shell tool as backgrounding. Keep fetch → md5 verify → `adb install` to a single package per call and re-send a slimmer command if the tool refuses.
- **Read the package before trusting the install**: `unzip -l <pkg>.xapk` lists per-ABI splits (`config.arm64_v8a.apk`, `config.armeabi_v7a.apk`). A publisher shipping only `armeabi_v7a` still installs fine on arm64 emulators/phones that keep 32-bit support, but fails on 64-bit-only devices with `INSTALL_FAILED_NO_MATCHING_ABIS` — so a clean run locally is not evidence of device compatibility. Pair the package inventory with Play Store reviews complaining about installs/crashes on newer phones to make it a reportable finding instead of a hunch.

## 3. Four `agent-device` Traps & Solutions

1. **`snapshot -i` misses custom-view options**:
   Many Chinese apps build gender/goal cards as a clickable `ImageView` (no `contentDescription`) stacked above a non-clickable `TextView` (`"女性"`). `snapshot -i` outputs only `@e1 [image]` and hides `"女性"`. Use full `agent-device snapshot --force-full` or `--raw` to see both the `ImageView` hitbox and its adjacent `TextView` label.
2. **Cached snapshot elision**:
   Calling `agent-device snapshot` twice within a few seconds prints `Snapshot unchanged since previous read...` instead of nodes. Always pass `--force-full` in automation scripts.
3. **Truncated long labels in text view**:
   Standard `agent-device snapshot` truncates long paragraphs (`[preview:"..."] [truncated]`), cutting off AI chat answers and legal disclaimers. Run `agent-device snapshot --raw --force-full` and read `node["label"]` from the NDJSON lines for the 100% unedited string.
4. **WebView image banners & overlays (`<15` nodes)**:
   Promotional paywall cards (e.g., `买1年送1年 ¥128`), retention modals, and WeCom coupon popups are often rendered as full-bleed `<img>` assets inside a WebView. Whenever `dump` reports `<5` labeled app nodes, inspect the `.png` with `vision_analyze` (noting `vision_analyze`'s downscale multiplier, e.g., `2.0x` on `1080×2400`).
5. **Non-ASCII / Chinese input on spoofed real devices (`--test-ime`)**:
   Because MuMuPlayer Pro spoofs a real phone (`SM-S9110`, `android device`), `agent-device` does not auto-enable its Unicode test IME on custom `EditText` controls (such as Ant Afu's `v_text_input`). Always open sessions with `agent-device open <pkg> --platform android --test-ime` so `agent-device fill @ref "中文..."` works reliably, and re-read the Send button's dynamic `rect` after multiline text wraps.
6. **Multi-step first-login coach-mark overlays**:
   Super-apps like JD Health stack 2–3 full-screen transparent `PopupWindow` tooltips on first login, causing both `agent-device` and `uiautomator dump` to report `0` labeled nodes underneath. Tap neutral upper-screen coordinates (e.g., `100, 250`) 1–3 times and re-dump until the main layout tree unlocks.

## 4. Hard Login Gates & The Guest-Mode Contradiction

Chinese health/commerce apps routinely declare in the privacy dialog that products and services are browsable before registration, then drop the user into a full-screen login page with no close affordance and a disabled hardware back key. Treat that contradiction as first-hand compliance evidence rather than an annoyance: keep the privacy dialog dump and the post-consent login dump as an adjacent labeled pair (e.g. `01_launch_privacy` → `02_home_initial`) and quote both verbatim in the report's funnel/acquisition section.

Do not spend calls hunting for a bypass. Confirm in at most two probes — tap the top-left back box (an `rlBackBox`-style `ImageView`, typically around `(28,68)` at `1080×2400`) and press `adb shell input keyevent 4` — then hand the emulator window to the user for login. Both probes returning to the same login screen is the signal to stop, not to try a third route.

## 5. 混淆包静态分析的五类假阳性（每条都真的骗过我）

### 5.1 单点像素采样会骗人
只采一个坐标点判断「这块区域画的是什么」不可靠：按钮中央正好是白色文字，`getpixel((540,2129))` 会返回 `(250,215,182)` 的浅橙抗锯齿像素，让人误判成「浅色卡片」。
**做法**：整行扫描再统计众数——`Counter(im.getpixel((x,y)) for x in range(45,1036,5)).most_common(3)`。上例整行 199 个采样里 195 个是 `(237,114,0)`，一眼就能看出那是橙色药丸按钮。
**推论**：`uiautomator` 的 bounds 只说明布局意图，不说明最终绘制。要断言「A 挡住了 B」，必须同时有 (a) 坐标重叠、(b) 整行像素众数指向 A、(c) 截图肉眼确认。三者缺一就不要写进报告。

### 5.2 混淆后的 Retrofit 注解不能靠猜
`@mxh` 长得像 `@Header`，实际是 **`@Query`**。判据不在调用处，在 Retrofit 自己的 `RequestFactory`（本例 `p000/gtj.java`）的 `annotation instanceof` 分派表里：
```java
if (annotation instanceof mxh) { ... mxhVar.encoded() ... }        // @Query
if (annotation instanceof a7a) { ... a7aVar.allowUnsafeNonAsciiValues() ... }  // @Header
```
**做法**：先 grep `annotation instanceof` 找到分派表，再看每个注解类自己声明了哪些方法——有 `encoded()` 的是 `@Query`/`@Field`/`@Path`，有 `allowUnsafeNonAsciiValues()` 的是 `@Header`/`@HeaderMap`。猜错的代价是整段安全结论作废（本例把 Query 误读成 Header，凭空造出一条「越权」风险）。

### 5.3 域名和职责经常是反的
`gateway.loseit.com` 挂的是同步（`user/loseItTransactionBundle`），`sync.loseit.com` 挂的是账号（`/account/login`）。凭域名语义下结论必错。
**做法**：对每个 Retrofit 接口，回溯到 `Retrofit.Builder().baseUrl(...)` 那一行，看它注入的是哪个 URL 常量函数；再看接口实现类有没有重写父类的 URL 拼接方法（本例四个同步类都继承 `ug9` 且都不重写 `mo73266e()`，所以全部走父类的 `fr0.m54589o()`）。

### 5.4 「打不通」之前先换兄弟域名试
在 `gateway.loseit.com` 上测 `/account/login` 拿到企业站 404，据此写「账号 API 打不通」——实际那个接口在 `sync.loseit.com` 上，裸 curl 就返回标准 OAuth2 错误体。
**做法**：一个 App 有多个自有域名时，把同一组路径在**每个**候选域名上各跑一遍，再下「开放/关闭」的结论。边缘策略是按 host 配的，不是按 App 配的。

### 5.5 jadx 会把别的类的常量替换进来，导致归属误判
`p000/bc3.java` 里出现 `com.singular.sdk.internal.Constants.RequestParamsKeys.SDK_VERSION_KEY`，看着像 Singular SDK 的类——实际是 **Firebase Crashlytics** 的 `CommonUtils`，原代码是 `Build.PRODUCT.contains("sdk")`，jadx 把字面量 `"sdk"` 替换成了同值的常量引用。
**做法**：判断一个混淆类属于哪个 SDK，看它**自己的** import 和字符串常量（本例该类有 6 处 `com.google.firebase` / crashlytics 标识），不要看某一个被替换进来的常量。

## 6. 从 FileDescriptorProto 还原 .proto（两个必踩的编码坑）

protobuf-java 把描述符以 `new String[]{...}` 形式编进类里，`internalBuildGeneratedFileFrom` 消费它。还原时有两处会静默出错，症状都是「解析能跑但字段名带乱码、message 数量偏少」：

1. **jadx 双重转义**：源码里出现的是 `\\u0012`（两个反斜杠），不是 `\u0012`。先 `c.replace("\\\\", "\x00")` 占位，再解其余转义，最后把占位还原成单个反斜杠。
2. **描述符字节是 ISO-8859-1，不是 UTF-8**：`chr(0xA6).encode("utf-8")` 会产出 2 字节 `C2 A6`，把 varint 长度读成 21314 而不是 166，整个解析从此错位。必须 `.encode("latin-1")`。

自检方法：解析出的顶层 message 数量应该和 `grep -c '^message'` 对得上；`LoseItGatewayTransaction` 这种大 message 的字段号应该连续（1..31 缺 19 是正常的，缺一大片就是错位了）。

## 7. High-Yield Product Audit Checklists

- **Pre-sale vs Post-onboarding Math Check**: Record BMR, target calories, meal count, and macro grams shown on the pre-paywall "Personalized Plan Preview" page, then compare against the actual budget ring after closing the paywall and entering the free Home tab. Static sales templates routinely contradict the user's selected fasting mode or BMR.
- **Hidden Footnote Mining**: Scroll WebView plan/paywall pages to the bottom (`y > 5000`) via `--raw`—companies frequently disclose cumulative VIP counts, cutoff dates, and survivor-biased "average weight loss" denominators in `18px` grey footnotes.
- **Temporal & Quota Gate Diffing**: Copy the exact same logged data (e.g., `1012 kcal` meals) into **Today** vs **Tomorrow** to catch stripped pre-planning entries and `0/1` daily free-trial locks.
- **Clinical / Domain Safety Probe**: Ask in-app AI assistants a multi-constraint real user question (age + symptoms + 3–4 concurrent supplements/medications with exact mg doses) to test whether the product enforces dose-disambiguation, empty-stomach GI warnings, mineral competition, or follow-up memory. Grade the reply against the national reference intake (e.g. China DRIs zinc RNI for adult women `8.5 mg/d`) rather than a vague "is it sensible" judgement — a product that states the RNI, names the absorption mechanism, and flags the downstream deficiency is in a different class from one that answers in generalities.
- **Cross-turn State Carry-Over Probe**: send a state-creating prompt first (log a real meal / workout / supplement stack), then a second prompt in the SAME conversation whose ideal answer must reuse that state (ask about protein intake, supplement timing, or training load). Quote the sentence that proves reuse, or record its absence as a statelessness finding. Grade on: does it reference the earlier numbers verbatim, does it warn against double-dosing on top of what was just logged, and does it keep the same persona across turns.
- **Identity-Gate Matrix (zero-price products)**: for a product with no paywall and no in-chat ads, the monetization question is answered by tapping every personal-data entry — 「我的」 rows (药箱 / 健康档案 / 设备管理 / 订单), plus any 名医 / 专家 / 智能体 directory — and recording which account binding each one demands. Capture each intercept modal as its own labeled dump so the report can show the same wall recurring across unrelated features; a phone-OTP login that still blocks every data module is the tell that the free chat layer is bait and the real product is the identity/insurance/payment graph behind the binding.
- **Multi-Intent Probe (one sentence, three actions)**: send a single sentence that carries 3 independent intents (a meal + a walk + water intake) and count how many the assistant actually records. Sub-agent architectures split `记饮食` / `记运动` / `记睡眠` into mutually exclusive skills with a single top-level router, so the reply looks excellent (itemised meal card, correct kcal, save button) while the exercise and water intents are silently dropped. This failure is invisible to any single-intent prompt and to the product's own marketing, and it is one of the most reportable engineering findings. Grade on: intents acknowledged ÷ intents sent, plus whether the drop was announced or silent.
- **Tap every tab of the membership centre, not just the landing card**: paywall pages increasingly ship multiple tiers behind horizontal tabs (e.g. `会员 / 超级 AI 会员 / 更多`). The landing view shows only the cheap tier; the expensive tier (often 3–5× the price, e.g. `¥19/mo` vs `¥68/mo`, `¥648/yr`) sits one tap to the side. Record each tab's full SKU ladder and its exact pay-button string (`确认协议并以 ¥X 元开通`) in separate dumps — quoting only the first screen understates monetisation by an order of magnitude.
- **New-feature entry points may be placeholder posters**: for any AI feature the changelog and press releases brag about, tap into it and read the screen instead of trusting the announcement. "Coming soon" splash art for the flagship model while the actually-working assistant hides behind an unrelated floating button is a standard gap between宣传 and 落地 — capture it verbatim as the finding, then continue testing whichever entry point really works.
- **Hardware Lock-In Check**: when the app ships or subsidises a device (scale, band, cuff), click through the binding flow to see whether the peripheral is usable outside the app. Proprietary-协议-only accessories that refuse third-party software are a switching-cost finding, and the BIA-vs-clinical (InBody) measurement gap is worth a footnote whenever the product sells body-composition claims.
