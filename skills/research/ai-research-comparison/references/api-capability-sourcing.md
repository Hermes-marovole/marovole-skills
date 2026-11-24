# 第三方能力选型：API / MCP 采购对比

用于「有没有 API 能做 X」这类问题。核心是先把需求拆成层，再看每家填哪一层，最后才谈价。

## 1. 三层拆解（任何感知类需求都适用）

| 层 | 输入 → 输出 | 谁来填 | 常见陷阱 |
|---|---|---|---|
| 感知 | 原始信号（图/音频/视频）→ 实体 + 数量 | 专用视觉 API，或通用多模态模型 | 多数「识别」API 只给实体，不给数量/份量 |
| 数据 | 实体 → 结构化数值 | 营养库、词典、价格库、法规库 | 返回单位常是「每 100 g / 每单位」，不是你需要的总量 |
| 编排 | 数值 → 业务动作（记账、下单、告警） | 宿主 Agent 或专用 MCP | MCP 通常只做这层，被误当成感知层 |

判定厂商填哪层，只看它返回的字段：有 `weight_g` / `portion` 才算做了份量；只有 `calorie_per_100g` / `per_unit` 就是没做，必须自己乘。

## 2. 计费单位归一（跨厂商比价的唯一正确姿势）

```
按 token 计价:   单次成本 = (厂商公布的每次典型 token 数 / 1e6) × 单价
按次 / 资源包:   单次成本 = 包价 ÷ 包内可用次数        # 「豆」「credit」先换算成次数
按月档位:        单次成本 = 月费 ÷ 该档包含的次数      # 注意档位内视觉次数常单列，比总调用数少很多
```

- **必须用厂商自己给的 token 数**。同一家的不同档位、不同模型路由给的典型值能差 3–4 倍，直接决定「贵不贵」的结论。
- **档位内的「总调用数」和「视觉调用数」是两个数**。低价档常给几十万次普通查询、只给几百次视觉，折算时用后者。
- **按次数包卖的接口要注意有效期**（常见一年/两年），过期浪费等于实际单价上浮。
- 折算完再排序；同时给出「每次动作成本」和「一个月 10 万次的账单」，后者才是用户真正在意的数字。

## 3. 探测托管 MCP（不花钱、不注册就能看清它有什么）

```bash
# 1) 握手：证明服务在线、拿到 serverInfo/version
curl -s -i -m 20 -X POST https://mcp.example.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'

# 2) 列工具：多数托管服务对 tools/list 不做鉴权，可以直接看到工具名 + inputSchema
curl -s -m 25 -X POST https://mcp.example.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'Mcp-Session-Id: probe-1' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

读结果：响应是 SSE，正文在 `data: ` 前缀的行里，先剥前缀再 `json.loads`。工具数、每个工具的 `description` 与 `inputSchema` 就是选型证据——比官网营销文案可靠。**只有 `tools/call` 需要凭据**，所以「能不能做这个能力」和「要不要付费」可以分开验证。

接入 Hermes 的配置写法、OAuth 服务器、注册前调用，见 `native-mcp` skill。

## 4. 精度基线（用于压住厂商宣传值）

写入结论前先复查引文，下列数字来自公开评测，只用于说明**量级**和**为什么单图方案有下限**：

| 方案 | 量级 | 来源方向 |
|---|---|---|
| 通用 VLM 单图直出 | 热量 MAPE 30% 上下，克重误差极大 | 受控称重餐食数据集（Purdue ACETADA 类） |
| 商业 App 盲测 | 每餐系统性低估数百 kcal | 代谢厨房受控餐（NIH/NIDDK 类） |
| 单图 + 食材/烹调/份量上下文 | MAPE 降到 15–25% | 上下文注入类实验 |
| 离散份量分类 + 权威库查表 | 热量误差几十 kcal 级 | Nutrition5k 类 |
| 单目深度 + 尺度校准 | 中餐数据集热量误差 10% 以内 | OmniFood8K 类 |
| 深度/LiDAR 硬件 | 10–15% | SNAQ 类 |

三条可以拿去怼宣传的规则：

1. 单图端到端方案的物理下限在 20% 以上；宣称个位数百分比误差的，要求方法论，否则按不可信处理。
2. 「每 100 g」接口必须乘份量，并在后端处理生熟比、可食部——按生重算熟食会直接翻倍，是最伤信任的错误。
3. 隐形烹调油要显式加固定补偿，不要留给模型猜；这是商业 App 集体低估的主因。

## 5. 采购清单（交付前自查）

- [ ] 需求已拆成 感知 / 数据 / 编排 三层，并标明哪层要自建
- [ ] 候选厂商各自填哪层、返回粒度是否匹配（有 `weight_g`/`portion` 吗）
- [ ] 单价已归一到「一次用户动作」，并附月账单量级
- [ ] 声称免费的额度写清是「永久」还是「试用」、单日限额多少
- [ ] 至少一个候选被打过真实请求（不是只读了官网）
- [ ] 精度宣称已降级，并给出该方案的下限与自建补偿成本
- [ ] 价格页面已标注「写入时点，用前重查」

## 6. 领域速查：食物/营养识别

这一类的厂商分层比较典型，可作为其他感知类选型的模板。

| 定位 | 代表 | 该去哪个页面看价格 |
|---|---|---|
| 视觉 + 数据一站（且有官方 MCP） | Edamam（Food Database API / Vision / Food MCP） | `developer.edamam.com/food-database-api` 的档位表 |
| 全链（分割→配料→份量→记录） | LogMeal | 无公开价目，走试用 + 询价 |
| 按 token 卖、带 SDK | Passio Nutrition-AI | 官网 pricing 的 token 包 + 文档里的「典型 token/次」 |
| 中式菜品分类 | 百度智能云「菜品识别」 | `cloud.baidu.com/product-price/imagerecognition.html` |
| 中式 + 自带 MCP、可小量试 | 天聚数行（菜品热量 / 食物营养两个接口） | 接口文档页底部「接口价格」 |
| 中文营养库（不开视觉） | cn-food-mcp、foodcalorie-mcp、Kolo | 开源仓库 / PyPI |
| 通用多模态兜底 | Gemini Flash / Qwen-VL / 豆包 / GLM-V | 各家 model pricing 页 |

要点：**中餐菜名识别便宜的都有，份量层基本都要自建**；做产品时用「分类 API 打底 + 自建中式份量阶梯 + VLM 兜长尾」，比买单图端到端便宜且误差可控。
