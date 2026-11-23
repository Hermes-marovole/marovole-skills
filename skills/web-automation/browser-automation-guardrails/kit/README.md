# 让 AI 控制浏览器操作商户后台：高敏感按钮防护 Kit

适用于：项目里用 Agent/自动化脚本控制商户后台（电商平台、广告平台、支付后台等），
流程中只需要"看报表、下载数据"之类的读操作，但界面上同时存在退款、改价、
注销、解绑等高危按钮（或高危接口）。目标是：**让 AI 在物理上看不见、点不着、调不通**。

## 0. 核心原则

提示词是防护力最弱的一层。任何配置都必须做到"物理不可达"，而不是"AI 自觉不做"。
可靠性从高到低：

1. **服务端权限降级**：给自动化开只读子账号/角色 → 危险按钮从接口层就不下发，DOM 里不存在。
2. **接口直取**：能 F12 抓到接口的操作直接调 HTTP，把 UI 从流程里拿掉。
3. **DOM 层防护**：敏感元素 CSS 隐藏 + 点击拦截 → AI 看不见也点不动。
4. **网络层掐断**：黑名单请求无论从哪发起都发不出去 → 兜住绕过 UI 的行为。
5. 逐步人工确认 / 提示词约束 → 只能当兜底，不能当防线。

3 层和 4 层各有失效面（3 管不住 Worker 里的请求，4 管不住 AI 看见按钮后的尝试行为），
**必须叠加**。1、2 条可行时优先做，3、4 变成保险。

## 1. Kit 内容与选型

| 文件 | 用它干什么 |
| --- | --- |
| `guard.user.js` | 唯一配置源：按钮/接口黑名单都填在这里；三种接入方式共享它 |
| `playwright-adapter.example.js` | 项目用 Playwright 驱动浏览器时 |
| `ego-adapter.example.js` | 项目用 ego lite 浏览器（Agent 直接控制）时 |
| 本文档 | 填配置的方法、接入示例、验收清单 |

选型：
- 后台支持只读子账号 → **先开子账号**（第 1 层），本 kit 变成第二道保险；
- 流程只是例行抓数据/下载报表 → 先试**接口直取**（§3），报表下载通常只是一个带登录态的 GET；
- 必须走 UI 的流程 → 本 kit 的 3+4 层。
- 人和 AI 共用一个裸浏览器 → 至少把 `guard.user.js` 装进 Tampermonkey（第 3 层单独生效）。

## 2. 填配置（10 分钟，一项一次 F12）

所有黑名单集中在 `guard.user.js` 顶部四组 TODO：

| 配置项 | 怎么填 | 注意 |
| --- | --- | --- |
| `@match` | 后台域名，`https://merchant.example.com/*` | 页面内嵌**其他域名**的 iframe 时，每个 iframe 域名单独加一行 `@match` |
| `SELECTORS` | F12 选中危险按钮 → 右键元素 → Copy → Copy selector | 尽量带父级容器写准；宁可漏不要滥 |
| `TEXTS` | 危险按钮的可见文案 | 默认表已含通用词；只删不加，加多了误伤正常按钮，且误拦比漏拦难排查 |
| `ENDPOINTS` | Network 面板开着，人工走一遍危险操作，Copy as cURL 看路径 | 填**路径子串**即可，如 `refund`、`withdraw/apply`，host 部分不用填 |

文案通用表（已预置）：退款、提现、注销、解绑、下架、清空、转账、改价、删除、作废。

`endpoint` 表填好后**同步**到接入方式的网络黑名单（Playwright 的
`blockSubstrings` / ego 的 `BLOCKED_URLS`）——两张表经常分居两个文件，改一处必须同步另一处。

## 3. 接入方式

### A. Playwright 项目（推荐：document-start 注入，无空窗）

把 `playwright-adapter.example.js` 和 `guard.user.js` 放进项目（同目录）：

```javascript
import { chromium } from "playwright";
import { installGuard } from "./playwright-adapter.example.js";

const browser = await chromium.launch();
const context = await browser.newContext({
  storageState: "merchant-session.json", // 登录态单独维护，复用会话
});
await installGuard(context, {
  blockSubstrings: ["/refund", "/withdraw/apply"], // TODO 与 guard.user.js 的 ENDPOINTS 同表
  allowOnlyGet: true, // 报表场景建议 true：一切非 GET 请求直接拦
});
// 此后 context 里所有 page 自动带防护:按钮隐藏+点击拦截,黑名单请求在 Network 层被 abort。
```

### B. ego lite 浏览器（Agent 直接控制的场景）

见 `ego-adapter.example.js`，要点：
- 网络黑名单用 CDP `Network.setBlockedURLs`，**在 `goto` 进后台之前**装好，从第一秒起生效；
- 页面守卫 `goto()` 后注入，整页导航后要重注入（适配文件已封装成 `armGuard(page)`）；
- 报表下载优先用 `page.fetch(REPORT_API, { saveAs })`——带登录态直接拉接口，不碰 UI（第 2 层）。

### C. 裸浏览器 + Tampermonkey（人和 AI 共用一个浏览器）

Tampermonkey 新建脚本 → 粘贴 `guard.user.js` 全文 → 填 `@match` 和三组黑名单 → 保存。
打开后台按 F12，console 出现 `[guard] 商户后台敏感按钮屏蔽器已生效` 即装好。
此方式只有第 3 层，够日常用；有 harness 时仍建议加网络层。

## 4. 验收清单（接入后逐项打钩，写进项目测试用例）

- [ ] 打开后台全页截图：全部敏感按钮**不可见**（截图型验证）
- [ ] F12 console 里手动对隐藏前的按钮测一次：输出 `[guard] 已拦截敏感按钮点击`，危险操作未触发（DOM 型验证）
- [ ] console 执行 `fetch('/你的黑名单接口').catch(e => e)`：返回 TypeError: Failed to fetch（网络层验证）
- [ **必须**] 完整跑一遍正常业务流程：报表能下载、翻页可用，**没有被误拦**
- [ ] 项目里有两处黑名单（guard + adapter）的，逐字核对同表
- [ ] 把以上各项加进项目的回归测试

## 5. 常见坑（都是原理，不是玄学）

- **删 DOM 节点会让 React/Vue 后台渲染崩溃**（框架还要更新被你删掉的节点），所以本 kit 用
  `display:none` + 属性标记，不删节点。
- **`visibility:hidden` 和遮罩层无效**：DOM 型 Agent 走 accessibility tree 照样"看得到"，
  截图型 Agent 能看穿半透明遮挡。必须真隐藏。
- **捕获阶段拦截挡的是点击事件**——就算 AI 用 `el.click()` 程序化点击（绕开坐标），事件仍在
  document 捕获阶段最先被掐掉，页面监听器根本收不到。
- **网络层是唯一管得住 Worker / 直接调接口的层**：页面里的 fetch/XHR 补丁拦不到 Service
  Worker 里发的请求，所以 Playwright 的 `context.route` / ego 的 `Network.setBlockedURLs`
  必须存在，不能只靠页面注入。
- **黑名单宁可窄不要宽**：把"确认"之类通用词加进 TEXTS 会拦住正常流程，误拦比漏拦难排查得多。
- **Kit 的边界**：它防的是 UI 层误操作，不阻止 AI 在"数据层"做危险操作（比如往正常表单里填
  危险值提交）。若真有此风险，只有服务端只读子账号（第 1 层）是答案——这就是为什么 1 有条件必做。
