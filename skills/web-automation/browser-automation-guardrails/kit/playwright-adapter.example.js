// Playwright 接入:复制本文件和 guard.user.js 到项目同一目录。
// 两道机制:
//   1) context.addInitScript():document-start 注入守卫,整页 + iframe,无导航空窗
//   2) context.route():Network 层黑名单,兜住 Worker 里发的请求和绕过 UI 的直接调用
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export async function installGuard(context, opts = {}) {
  const {
    guardFile = path.join(__dirname, "guard.user.js"),
    blockSubstrings = [],      // TODO: 路径子串,与 guard.user.js 的 ENDPOINTS 同表,如 ["/refund", "/withdraw/apply"]
    allowOnlyGet = false,      // 报表类流程建议 true:一切非 GET 请求直接拦(后台连查询都用 POST 时改回 false)
  } = opts;

  // 1) 页面守卫:剥掉 ==UserScript== 头,注入函数体
  const raw = await readFile(guardFile, "utf8");
  const body = raw.split("// ==/UserScript==").slice(1).join("\n").trim();
  if (!body) throw new Error("guard.user.js 缺少脚本体,或 ==UserScript== 头未闭合");
  await context.addInitScript({ content: body });

  // 2) Network 层黑名单
  if (blockSubstrings.length || allowOnlyGet) {
    await context.route("**/*", (route) => {
      const req = route.request();
      const url = req.url();
      const blocked =
        (allowOnlyGet && req.method() !== "GET") ||
        blockSubstrings.some((p) => url.includes(p));
      if (blocked) {
        console.warn("[harness-guard] 拦截请求:", req.method(), url);
        return route.abort("blockedbyclient");
      }
      return route.continue();
    });
  }
}

// ============ 用法 ============
// import { chromium } from "playwright";
// import { installGuard } from "./playwright-adapter.example.js";
//
// const browser = await chromium.launch();
// const context = await browser.newContext({ storageState: "merchant-session.json" });
// await installGuard(context, { blockSubstrings: ["/refund"], allowOnlyGet: true });
// 此后 context 内所有 page 自动带防护;登录态过期时只需重新维护 storageState,不经过 AI。
