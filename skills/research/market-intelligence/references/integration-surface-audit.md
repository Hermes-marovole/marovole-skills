# 第三方集成面审计：有没有 API / SDK / MCP，能不能接

触发场景：用户问「这个产品有 API 吗 / 他们有 MCP 吗 / 能不能接进 Claude 或我们的 Agent」，或竞品档案需要补「开放平台」一节。

交付物是一张**三态结论表 + 一手实测响应原文**，不是一句「看起来有」。三态必须分开写，混为一谈就是错答案：

| 事实层级 | 判据 | 常见误判 |
|---|---|---|
| 接口存在 | 真实路径 401、伪造路径 404，`/health` 有响应 | 拿浏览器能打开官网当「有 API」 |
| 文档在线 | 文档站域名当前有 A 记录且能渲染 | 搜索结果里还有索引摘要，就以为站点还在 |
| 官方支持 | 有自助发 key 的入口 + 定价 + 维护迹象 | 后台登录页还在，就以为在正常发 key |

---

## Step 0：先做同名消歧（最容易让整份答案作废的一步）

同名不同公司的产品极多：一个域名是消费级 App，另一个是同名的 B 端 SaaS；同一家公司的「AI」也可能同时指官网产品线、语音 Agent 和一个 `.ai` 域名。用户给的文档链接，指向的公司常常不是他上一句问的那个产品。

开工前核三件事，任一对不上就在**回答第一句**纠正，不要埋在文末：

1. **域名**：文档主机、API 主机、官网是不是同一注册域名或子域。
2. **法律主体**：抓 `/terms`、`/privacy`，看公司名与注册地（`Delaware` / `LLC` / `Ltd` / `GmbH`），与 App Store 的 seller name 对照。
3. **业务**：文档里的端点名、参数、计费单位，描述的是不是同一个产品在做的事。

```bash
curl -s https://<host>/terms | tr -d '\n' | grep -oiE '[A-Z][A-Za-z. ]{2,40}(Inc\.|LLC|Ltd\.|GmbH)' | head -20
```

只凭名字相同就认定「他们有 MCP」，整份技术判断会建立在本不属于它的文档上。

---

## Step 1：判「路由真的存在」——401 必须配 404 对照

对受保护的 API，孤立的 401 **不能**证明路径存在：一层全局鉴权中间件会让任何路径都回 401。必须打一条同前缀的伪造路径做对照。

```bash
H=https://api.<host>
for p in v4/scanImage v4/notarealendpoint nonsense; do
  code=$(curl -s -o /tmp/e -w '%{http_code}' -m 15 -X POST "$H/$p" \
    -H 'Content-Type: application/json' -d '{}')
  echo "$p -> $code $(head -c 100 /tmp/e)"
done
```

读法：

- 真实路径 **401** + 伪造路径 **404** → 路由确实存在，被鉴权挡住。这才算「有接口」。
- 全部 401（含 `nonsense`）→ 全局中间件兜底，什么都没证明，换个探测方式（`GET`、`OPTIONS`、真实前缀）。
- 全部 404 → 版本号或前缀猜错，别急着说「没有 API」。

顺手探三个免费的元信息：`/health`（服务活着吗）、根路径（框架指纹、`{"name":"..."}` 之类）、`OPTIONS`（`Allow` 头能一次列出该路径支持的方法）。

---

## Step 2：判文档站死活——DNS 一票定生死，再走归档

站点「打不开」分两种：域名还在但 404，和域名已经拔掉。后者用公网 DoH 一问就知道，不用猜。

```bash
curl -s "https://cloudflare-dns.com/dns-query?name=docs.<host>&type=A" \
  -H 'accept: application/dns-json'
# Answer 为空、只有 SOA → 域名没有 A 记录，站点已下线（不是 404、不是墙）
```

确认下线后到 Wayback 取最后一份可用快照：

```bash
# 先列快照，挑一个 200 的时间戳
curl -s "https://web.archive.org/cdx/search/cdx?url=docs.<host>/*&output=json&limit=20&filter=statuscode:200"
# 再取正文（必须 --compressed）
curl -sL --compressed -m 45 "https://web.archive.org/web/<TIMESTAMP>/https://docs.<host>/api-reference/introduction"
```

坑：`/web/<TIMESTAMP>id_/<url>` 这种 raw 变体对 gzip 内容会返回 `SIZE:0`（HTTP 200 但空文件），看起来像归档不存在——去掉 `id_` 重取，并带 `--compressed`。

从快照里要抄下来的东西，比端点列表更值钱：

- **鉴权方式**（Bearer / OAuth / key 前缀）与 key 的申请入口；
- **限流与计费单位**（每分钟/每天配额、每类端点扣几个 token）；
- **「未来会做」的条目**（SDK、webhook 常写「will be released」），这是官方成熟度的直接证据；
- **被注释掉的段落**：Mintlify 类文档里 `{/* ... */}` 包住的「自助获取 API Key」区块，等于「当时就已经在收口」。原文里搜 `{/*` 能一眼看出来。

---

## Step 3：SPA 后台 bundle 侦察

`dashboard.` / `app.` / `console.` 这类子域常是 Vite/CRA 单页，HTML 只有 500 字节。抓首页的 asset 清单，再下楼 bundle 里的关键字。

```bash
curl -s https://dashboard.<host>/ | grep -oE 'assets/[A-Za-z0-9._-]+\.js' | head
curl -s https://dashboard.<host>/assets/index-*.js -o /tmp/app.js
python3 - <<'PY'
import re
t=open('/tmp/app.js',encoding='utf-8',errors='ignore').read()
for kw in ['firebase','supabase','clerk','auth0','stripe','/api/','apiKey','pricing','signup']:
    hits=[m.start() for m in re.finditer(kw,t,re.I)][:3]
    print(kw, len(hits), [t[max(0,h-80):h+100].replace('\n',' ') for h in hits[:2]])
PY
```

能读出：用的是哪家托管鉴权（决定「注册能不能自助」）、是否挂了支付、前端直接调的 API 主机名。**用浏览器把登录/注册页渲染一次**确认表单真实存在（`page_info()` + 取 `input,button,a` 的 `innerText`/`placeholder`），比读 bundle 里的字符串硬。

---

## Step 4：MCP 端点探针（有没有 MCP 一句话证伪）

MCP 服务对未授权的 `initialize` 会回 401，但响应头会暴露它到底是 MCP、以及要什么鉴权。这一条探针同时回答了「在不在线」和「要不要 OAuth」。

```bash
curl -s -i -m 20 -X POST https://mcp.<host>/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' | head -25
```

- `401` + `www-authenticate: Bearer resource_metadata="https://.../.well-known/oauth-protected-resource/mcp"` → 服务在线，走 OAuth 2.0/2.1，客户端连上去会自动弹授权，**不需要 API key**。
- `404` / 连接重置 → 该主机没有 MCP。再搜 MCP 目录（smithery、glama、Claude 连接器目录）和 npm 上的官方包名（`@<vendor>/<x>-mcp`）双重确认，别只看官网有没有提。
- 官方 npm 包还在更新（查 registry 的 `time.modified`）但官网没宣传，是常见状态：能用，但属于「没人维护的公开秘密」。

---

## Step 5：把结论写成能拍板的样子

1. **三态表**（见上）逐行给「探测项 / 实测结果 / 说明」，响应体截断到 80–100 字符，保留原文。
2. **解释 posture，而不是替它下判决**：文档站被拔、后台还开着、团队很小、公司刚被收购或创始人已离职——把这些摆出来，结论是「能接，但不该当稳定依赖」，不是「他们的 API 是假的」。
3. **写明没测过什么**：「未注册账号，因此无法确认现在是否还发新 key」这类边界必须写。**不要用自造邮箱注册去验证发 key**——那既越界，结果也不可复现。
4. **给替代路线**：同类里 MCP 优先的、或大厂封闭 API 的真实状态（很多健身/记账类大厂的 API 至今只对审核合作方开放，网页明写「not accepting requests」），一并说清，用户才有的选。

## Step 6：把在线接口当一手证据源（agent-native 竞品的取证顺序）

当竞品本身对外开 API/MCP（补剂评分库、设备数据平台、AI 助手服务商越来越多属于此类），接口返回的 JSON 就是**比网页文案高一个证据等级**的一手数据：字段级、可复现、能逐条引用。取证顺序固定如下，不要跳到最后一步才开始。

**① 三个机器可读清单，先全部落盘**

```bash
EV=./evidence; mkdir -p $EV
curl -sL https://<host>/llms.txt -o $EV/llms.txt
curl -sL https://<host>/.well-known/mcp/server-card.json -o $EV/mcp_server_card.json
curl -sL https://<host>/openapi.json -o $EV/openapi.json
```

- `llms.txt` 通常是厂商写给 AI 读的**方法论自述**：评分维度与权重、认证流程判定阈值（「含量达标示值 ≥95% 才发证」）、以及哪些指标明确不计入（如价格）。这是引用厂商规则最干净的出处。
- `server-card.json` 给 `tools[]`（名称 + 描述 + 鉴权分层）、`prompts`、`resources`；**按「公开读 / 授权读写 / 交易结算」三层读完工具清单，本身就是产品战略证据**（有 `save_memory` = 有跨会话记忆；有 `add_to_cart`/`get_checkout_url` = 已把 Agent 当销售渠道）。
- `openapi.json` 的 `paths` 是 REST 面：能数出「N 个 MCP 工具 + M 个公开端点」，并看 `servers[].url` 确认真实 API 主机。

**② JSON-RPC 直调，拿真实业务数据（不需要 key）**

```bash
call() {  # call <tool> <json-args> <outfile>
  curl -sL -X POST https://<host>/mcp \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":$2}}" \
    -o "$3"; head -c 600 "$3"; echo;
}
call suppco_get_nutrient_info '{"nutrient_name":"Zinc"}' $EV/mcp_zinc.json
```

响应体里 `result.structuredContent` 是逐字段的机器可读数据，`result.content[0].text` 是同一份数据的人读摘要——**引用时取 `structuredContent`，摘要只用来快速扫读**。每条响应原样存 `evidence/`，报告引标指向该文件。

**③ 参数名从 `inputSchema` 抄，不要凭直觉拼**

`Missing required arguments: products` / `nutrient_name` 这类报错是**参数名猜错**，不是接口故障：同一工具在不同产品的命名风格差异极大（`nutrient` vs `nutrient_name`、`product_ids_or_slugs` vs `products`）。先看 server-card 里该工具的 `inputSchema.required`，或直接打一次带空 `arguments` 的调用，让服务端把缺的参数名念出来。

**④ 同一事实要在两层对撞，冲突才是最高价值的发现**

结构化库的**全局规则字段**与**单品页/包装标签**经常对不上。把同一个问题分别问「全局营养素接口」和「具体产品页」，逐字比对：

- 全局 `nutrient` 词条写「上限 50 mg/天、空腹服」，同一站的单品页标签写「随餐服用」、且 `40 mg/天` 才是主流安全上限 → 这类矛盾（剂量上限放宽 + 服用条件写反 + 缺长期拮抗提示）比任何营销描述都更能证明对手的知识库是人工赶工出来的。
- 评分体系与商业收入撞车时同理：早期公开承诺「不靠卖货盈利」，后来上线自营商城返积分——把两段原文并列，就是信任风险的实证，不需要自己下判断。

**⑤ 收尾纪律**：报告里每条接口结论都写「工具名/端点 + 参数 + 落盘文件名」，并明确哪些工具因需 OAuth 未能实测（`未授权，未测`），不要用公开工具的返回推断授权工具的行为。

## Pitfalls

- **孤立的 401 不是存在性证据**，必须配一条同前缀伪造路径的 404。
- **搜索索引里有摘要 ≠ 站点还在**：摘要能留几个月，DNS 早拔了。
- **Wayback 的 `id_` raw 变体对 gzip 返回 0 字节**，别据此判「没归档」。
- **别把 App 的内部端点当公开 API**：拆包看到几十个 `/v4/*` 路由，多数只服务自家客户端（Stripe、社交、家庭共享），能列出来不等于对外开放。
- **别把「厂商没写 MCP」写成「不支持 MCP」**：区分「没有」和「没搜到」，后者要给出搜过的目录与包名。
- **同名产品**：核对域名 + TOs 主体 + 业务一致性，纠正放在回答第一句。
- **公开工具能调通 ≠ 授权工具也能用**：读到 `get_my_stack`、`get_checkout_url` 这类签名工具时，写清「需 OAuth 2.1，未授权未测」，不要拿公共工具的成功经验类推。
- **接口返回空数组时先换查询词，再下「库里没有」的结论**：长 query（品牌+品类+剂型）常直接零命中，短 query 才走模糊检索。
- **`content[0].text` 是摘要不是事实源**：引用剂量、价格、评分必须回到 `structuredContent` 或对应的单品页字段，摘要里的单位换算偶有错位。
