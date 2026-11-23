// ego lite 浏览器接入(Agent 直接控制浏览器的场景)。
// 把本文件内容粘进 ego-browser nodejs 脚本(heredoc 或 -e),GUARD_FILE 必须是绝对路径
// —— ego 脚本不继承 shell 的环境变量和工作目录。
//
// 顺序很重要:先装 Network 黑名单,再 goto 进后台 —— 注入前的空窗期由网络层兜住,
// 危险请求从第一秒起就发不出去。

const GUARD_FILE = "/absolute/path/to/guard.user.js"; // TODO: 项目里 guard.user.js 的绝对路径
const MERCHANT_HOME = "https://merchant.example.com/"; // TODO: 后台首页
// 网络黑名单:CDP 子串通配,与 guard.user.js 的 ENDPOINTS 同表,如 ["*refund*", "*withdraw/apply*"]
const BLOCKED_URLS = []; // TODO

const { readFile } = await import("node:fs/promises");

async function guardSource() {
  const raw = await readFile(GUARD_FILE, "utf8");
  const body = raw.split("// ==/UserScript==").slice(1).join("\n").trim();
  if (!body) throw new Error("guard.user.js 缺少脚本体,或 ==UserScript== 头未闭合");
  return body;
}

// armGuard(page):一次调用同时装上网络黑名单 + 页面守卫。
// 整页 goto()/reload() 之后要重新调用(SPA 内部跳转不用);内部有防重复注入标记。
async function armGuard(page) {
  await page.cdp("Network.enable");
  if (BLOCKED_URLS.length) {
    await page.cdp("Network.setBlockedURLs", { urls: BLOCKED_URLS });
  }
  const src = await guardSource();
  await page.evaluate("((s) => (0, eval)(s))(" + JSON.stringify(src) + ")");
  return true;
}

// ============ 流程示例 ============
const task = await taskSpace("商户后台报表自动化(带防护)");
const page = (await task.pages())[0] ?? (await task.newPage());

await page.cdp("Network.enable");
if (BLOCKED_URLS.length) await page.cdp("Network.setBlockedURLs", { urls: BLOCKED_URLS });
await page.goto(MERCHANT_HOME);
await page.evaluate("((s) => (0, eval)(s))(" + JSON.stringify(await guardSource()) + ")");
console.log("[guard] 网络黑名单 + 页面守卫均已生效");

// 报表下载优先走第 2 层:page.fetch 带登录态直接调接口,不碰敏感 UI
// const res = await page.fetch(REPORT_API, { saveAs: "/absolute/path/report.csv" });

// 收工
await task.finish({ keep: [] });
