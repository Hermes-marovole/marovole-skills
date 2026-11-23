// ==UserScript==
// @name         商户后台危险按钮屏蔽器
// @namespace    local.merchant.guard
// @version      0.1.0
// @description  唯一配置源。三层防护:CSS隐藏(截图型看不见)+捕获阶段点击拦截(DOM型点不动)+接口黑名单(绕过UI也发不出)。
// @match        https://merchant.example.com/*   // TODO: 改成真实后台域名;内嵌其他域名 iframe 时每个域名加一行
// @run-at       document-start
// @all_frames   true
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  // ===== 按你的后台实际情况修改这三组配置 =====
  // 1) 选择器黑名单:命中即隐藏 + 拦截。尽量写准,避免误伤正常按钮
  const SELECTORS = [
    // '#btn-refund',
    // '.order-table .action-delete',
  ];
  // 2) 文案黑名单:按钮可见文本命中即隐藏 + 拦截。只删不加,宁窄勿宽
  const TEXTS = [
    '退款', '提现', '注销', '解绑', '下架', '清空', '转账', '改价', '删除', '作废',
  ];
  // 3) 接口黑名单(路径子串):无论从哪发起都掐断。
  //    填完后须同步到接入方式的网络黑名单(Playwright 的 blockSubstrings / ego 的 BLOCKED_URLS)
  const ENDPOINTS = [
    // '/api/refund',
  ];
  // ===========================================

  // --- 1. CSS 隐藏:截图型 Agent 看不见 ---
  // 故意用 display:none 而不是删节点:删 React/Vue 托管的节点会导致框架渲染崩溃。
  const style = document.createElement('style');
  style.textContent =
    SELECTORS.map(s => s + '{display:none !important;}').join('\n') +
    '\n[data-ai-guard-hidden]{display:none !important;}';
  (document.head || document.documentElement).appendChild(style);

  // --- 2. 捕获阶段点击拦截:DOM 型 Agent 用 .click() 程序化点击也点不动 ---
  function hit(el) {
    if (!(el instanceof Element)) return false;
    if (SELECTORS.length && SELECTORS.some(s => (el.matches && el.matches(s)) || (el.closest && el.closest(s)))) return true;
    const t = ((el.innerText || el.value || '') + '').trim().slice(0, 30);
    return TEXTS.some(x => t && t.includes(x));
  }
  document.addEventListener('click', (e) => {
    for (const node of e.composedPath()) {
      if (hit(node)) {
        e.preventDefault();
        e.stopImmediatePropagation();
        console.warn('[guard] 已拦截敏感按钮点击:', node);
        return;
      }
    }
  }, true); // true = 捕获阶段,先于页面任何监听器

  // --- 3. 接口黑名单:页面内 fetch/XHR 兜底(Worker 需网络层) ---
  const origFetch = window.fetch;
  window.fetch = function (input) {
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    if (url && ENDPOINTS.some(ep => url.includes(ep))) {
      console.warn('[guard] 已掐断敏感请求:', url);
      return Promise.reject(new DOMException('blocked by guard', 'AbortError'));
    }
    return origFetch.apply(this, arguments);
  };
  const origOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    if (typeof url === 'string' && ENDPOINTS.some(ep => url.includes(ep))) {
      console.warn('[guard] 已掐断敏感请求(XHR):', url);
      throw new Error('[guard] blocked sensitive request: ' + url);
    }
    return origOpen.apply(this, arguments);
  };

  // --- 4. 动态渲染兜底:SPA 后渲染出的敏感按钮也藏掉 ---
  const FLAG = 'data-ai-guard-hidden';
  function sweep() {
    document.querySelectorAll('button, a, [role="button"], input[type="button"], input[type="submit"], .btn').forEach(el => {
      if (el.hasAttribute(FLAG)) return;
      if (hit(el)) el.setAttribute(FLAG, '1');
    });
  }
  let timer = null;
  new MutationObserver(() => {
    if (timer) return;
    timer = setTimeout(() => { timer = null; sweep(); }, 500);
  }).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', sweep);
  setInterval(sweep, 5000);

  console.info('[guard] 商户后台敏感按钮屏蔽器已生效');
})();
