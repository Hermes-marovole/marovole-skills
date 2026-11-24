# 自测 provider / 中转线路速度

公开榜（Artificial Analysis 的 TPS）是中转商在自己机房跑出来的数字。用户问「我这两个 provider 哪个快」，
要的是**他自己那条链路**现在的表现，唯一可信的做法是在本机网关上对拍。

## 口径：为什么不能用 TPS

带思考的模型（DeepSeek `:1017`、各家 reasoning 变体）在流里先吐 `reasoning_content`，
这段隐藏推理也计入 `completion_tokens`。同一句提示词，思考版可能多算近一倍 token，
于是 `completion_tokens / 时长` 反而给慢的那条算高分。

可比的量只有两个：

1. **首个可见正文字符**（`content` 的第一个 delta，不含 `reasoning_content`）—— 用户真正感知的等待。
2. **到前 N 个可见字符的时间**（100 / 300 字）+ 全文完成时间 —— 用里程碑插值，两边输出长度不同也能比。

同时记 `reasoning_chars` 和 `completion_tokens`：两者一起看才知道「快」是不是靠不思考换来的，
以及同样的可见输出要多花多少 token（成本口径）。

## 操作要点

- **两边都走同一个网关**。本机 magpie 在 `127.0.0.1:3425`，`Authorization: Bearer magpie`；它的
  `~/.config/magpie/providers.json` 把上游 key 打码（`sk-7ac...395b`），去追真 key 只会白费时间，
  而且一边走网关一边直连会把网关开销算到某一边头上。
- **magpie 对未出现在 `/v1/models` 的 `provider/model` 照样路由**。测速不需要改
  `providers.<name>.models`（那是让路由在 Hermes 里可选，属于配置改动，先问用户）。
  先打一条 1-token 请求确认 200，再进正式轮次。
- **交替顺序 + 多轮中位数**：≥4 轮，奇偶轮反转模型顺序，避免预热、缓存、时段噪声全落在一个模型上。
  单次快慢（尤其 3 s 以上的 TTFT 尖峰）不代表线路水平，报中位。
- **用网关自己的账本佐证**：`~/.config/magpie/usage.jsonl` 每行有 `ms`（总时长）、`ttft_ms`
  （**上游首 token，含思考**）、`out`（输出 token）、`status`。若两边 `ttft_ms` 都在 450–650 ms 而客户端
  「首个可见字」差 2 倍，结论就是**模型先想后说**，不是链路快慢——这是最容易误判的一步。
- 同一模型 id 在不同中转上可能**一个带思考、一个不带**（`reasoning_chars` 一边为 0）。
  这不代表它们质量等价，报结论时要说清「快的这条少了推理」。
- **流式响应默认不带 usage。** 要 token 数就加 `stream_options: {"include_usage": true}`，否则成本口径整列是空的，而你还以为那是「没统计」。

## 脚本

`scripts/provider_speed_test.py`：

```bash
python3 scripts/provider_speed_test.py \
  neumaapi/deepseek-v4.1-flash:1017 mistral/deepseek-v4-1-flash-1017 --rounds 6
```

输出逐轮明细 + 中位数表，原始数据落 `~/.hermes/cache/scratch/provider_speed.jsonl`。
换网关：`MAGPIE_URL=http://host/v1/chat/completions MAGPIE_KEY=...`。

## 质量臂：同模型不同 provider，「哪个好」而不只是「哪个快」

同一模型 id 在两条链路上的差异，多半不来自权重，而来自服务层：参数支持、预算饥饿、输出损坏。
速度那套跑完，再补一组机器判分的题。

### 题库（七类，全部可脚本判分）

| 题目 | 判分方式 |
|---|---|
| 严格 JSON 抽取（三字段，其中一个必须整数） | `json.loads` + 字段与类型断言 |
| 代码题 + 隐藏测试（如 `merge_intervals`，自写 7 组：空/单个/相接/包含/乱序/极大/负数） | 子进程跑隐藏用例，全过才算 pass |
| 长上下文埋码（塞 ≥4 万 token，正文里埋 3 个随机码） | 三个码精确匹配 |
| 负约束写作（≤120 字、禁三个词、必含某词、结尾问句） | `len()` + 正则 |
| 多步算术（如 3×24−5、按 7 装箱） | 精确数字 |
| 固定字面量回显（问句里要求「只回 XXXX」） | `text.strip() == 字面量` |
| 400 字写作，跑两个 `max_tokens` 档 | 完成率 + 每字 token 数 |

每格 2–8 次即可看大差异；报的时候写明「样本小，只能看大差异」。

### 预算是最容易错的一个维度

- 质量题的 `max_tokens` 给到 **≥2000**。思考型线路在 900 预算下会把预算全烧在 `reasoning_content` 上，
  `content` 为空、`finish_reason=length`——这在判分表里长得跟「答错」一模一样，实际是预算饥饿。
  同一批题在 2500 预算下复跑，两边都能满分，就证明前面的 0 分不是能力问题。
- 把「紧预算下的完成率」当**独立指标**报（它对定长 agent 步骤很有意义），不要和质量的格子混算。
- **成功率必须按 budget 分开算**。把两个档的通过数加在一起（如 7/11）是最典型的手滑：两个预算测的不是同一件事。

### 解码速度只能逐条算

- 每条请求算 `completion_tokens / (wall − ttft)`，再取中位。**拿两个中位数相减是错的**（分子分母来自不同样本），
  出来的数字可能高出一倍。
- 标签写「粗估，可能偏高」：分子含思考 token，思考流得快会把解码速度抬起来。
- 速度和「谁更好」要拆成三段说：首字、解码、token 开销，三条排序可以完全相反。
  合成一句「A 更快」就是不可证伪的断言，用户按体感一顶就塌。

### 参数差异记 unsupported，不记失败

一条线路返回 422 / 「unknown parameter」（常见于 `think:false`、`reasoning.effort` 这类开关）
说明它不认这个参数，不是答错。判分表里写「422，不支持该参数」，另记一列；把它算成 0 分会让你
得出「这家质量差」的错误结论。

### 交付形状

KPI 卡（两边首字、解码、紧预算完成率）+ 三句话结论（质量 / 速度三段 / 真差异）+ 逐题表 + 速度表 + 局限性
（样本量、单账号单时段、上下文只压到多少 token、代码题是自写用例）。
**页面里每个数字都由脚本从 `raw.jsonl` 算出并渲染**（builder 读原始记录），不要手敲：
手敲的数一旦和表里另一格对不上，整页就作废。`raw.jsonl` 每行一次调用，存 wall、ttft、usage、
finish_reason、正文前 4000 字，报告与复跑都靠它。

## 踩过的坑

- **在 `~/.hermes` 这类大目录里 `grep -rl` 找 key 会挂到超时**：先带 `--include=*.yaml --include=*.json`
  和 `timeout 40`，或者干脆别找——走网关就不需要上游 key。
- `statistics.median()` 遇空列表抛 `StatisticsError`：过滤样本按 `is not None`，不要按真值
  （`reasoning_chars` 为 0 是正常值，被过滤掉就崩在汇总那一步，数据却已经写盘了）。
- **不要拿 `completion_tokens / 总时长` 当解码速度**，也不要把思考 token 当成「模型哆嗦」：
  同一段 400 字，思考版 794 token、非思考版 314 token，是 2.5 倍的账单，不是 2.5 倍的工作量。
- **想只测一家就下归因结论，是最贵的错。** 某条链路把固定字面量切成两截、或在正文里混进无关段落时，
  先用同一个探针打另一条链路：两边都断说明问题在 checkpoint / 推理栈（issue 里常已有人指向 vLLM/spec-decode），
  只测一家就会写出「避开这个渠道」的结论，而它站不住。
- **长任务放到后台会被超时提升。** 一次早早几百秒的批量探测会被转成 tracked background process，
  别重跑，用 `process_manage wait` 等它结束再读落盘结果。
