# Google Colab Hosted MCP Endpoint vs Colab CLI 本机实测报告（2026-11-19）

> 测试日期：2026-11-19 22:00–22:13 CST（UTC+08:00）
> 测试环境：macOS 27.0.1（Apple M2 Max, 64 GB RAM），固定美国出口 IP，Python 3.13（`google-colab-cli v0.7.4` 虚拟环境）
> 测试账号等级：`SUBSCRIPTION_TIER_PRO_PLUS`（Colab 付费算力单元初始余额 `4459.60 compute units`，测试前后 `Active assignments: 0`）
> 测试对象：
> 1. Google Colab 官方托管 Remote MCP Endpoint：`https://colaboratory.googleapis.com/mcp`（2026-11-17 发布，底层为 Colab REST API `v1beta`）
> 2. Google Colab 官方命令行工具：`google-colab-cli v0.7.4`（`colab` CLI）
> 3. 对照参考：2026-03-17 开源的本地浏览器代理仓库 `googlecolab/colab-mcp`

---

## 一、端点探测与鉴权接入实测

### 1.1 未鉴权直连 `tools/list`

向 `https://colaboratory.googleapis.com/mcp` 发送标准 JSON-RPC `tools/list` 请求（不带 `Authorization` 头），返回 `HTTP 200`，直接列出全部 **10 个 MCP 工具**：

1. `create_runtime`（参数：`requestId`, `runtime`, `runtimeId`）
2. `create_session`（参数：`parent`, `session`, `sessionId`）
3. `delete_session`（参数：`name`）
4. `execute_code`（参数：`code`, `executionId`, `runtime`, `session`）
5. `get_subscription`（参数：无）
6. `list_sessions`（参数：`parent`）
7. `delete_runtime`（参数：`allowMissing`, `name`）
8. `get_runtime`（参数：`name`）
9. `list_runtimes`（参数：无）
10. `list_runtime_specs`（参数：无）

### 1.2 接入实测复现的 3 个真实报错（原始日志）

- **报错 1：复用了 `colab-cli` 已有的 OAuth token（已包含 `https://www.googleapis.com/auth/colaboratory` 与 `cloud-platform` scope），但未带 `x-goog-user-project` 请求头**
  - 调用 `get_subscription` 与 `list_runtime_specs` 均返回 `HTTP 403`：
  - `Your application is authenticating by using local Application Default Credentials. The colaboratory.googleapis.com API requires a quota project, which is not set by default.`
- **报错 2：补上 `x-goog-user-project` 后，目标 GCP 项目尚未启用 `colaboratory.googleapis.com`**
  - 调用 `get_subscription` 返回 `HTTP 403`：
  - `Colab API has not been used in project <project-id> before or it is disabled.`
  - 通过 Service Usage API 在个人 GCP 项目启用 `colaboratory.googleapis.com` 后，等待 5 秒再次调用 `get_subscription` 和 `list_runtime_specs` 返回 `HTTP 200`；但在启用后约 3 分钟调用 `create_runtime` 时，仍命中一次未完成全局传播的边缘节点返回 `HTTP 403`（同一句 `has not been used in project ... or it is disabled`，耗时 `0.63s`），再等待约 1 分钟后重试恢复 `HTTP 200`。
- **报错 3：G4 GPU 临时缺货时，MCP 与 CLI 的报错信息对比**
  - 22:08 CST 同分钟分别用 MCP 和 CLI 申请 `G4`（`VARIANT_GPU`, `SHAPE_STANDARD`）：
  - MCP `create_runtime` 等待 `32.87s` 后返回 `HTTP 200`、`isError: true`，报错文本仅一句：`Precondition check failed.`（无法直接判断是库存不足、配额耗尽还是并发超限）。
  - `colab-cli`（`colab new --gpu G4`）等待 `31.29s` 后退出码 `1`，报错明确输出：`POST https://colab.research.google.com/tun/m/assign?...&variant=GPU&accelerator=G4: Service Unavailable`。

---

## 二、订阅与硬件规格查询实测（0 CU 消耗）

- `get_subscription` 返回：
  `{"name": "subscription", "tier": "SUBSCRIPTION_TIER_PRO_PLUS"}`
  仅包含订阅档位，**不返回剩余算力单元（CU）余额，也不返回每小时扣费速率**。
- `colab usage` 同期返回：
  `Current balance: 4459.60 compute units` / `Usage rate: 0.00/hr` / `Active assignments: 0`。
- `list_runtime_specs` 返回 **11 种硬件规格**，该 Pro+/Ultra 账号全部为 `eligible: true`：
  - CPU（2 种）：`VARIANT_CPU` + `NONE`（`SHAPE_STANDARD`、`SHAPE_HIGHMEM`）
  - GPU（7 种）：`T4`（Standard / HighMem）、`L4`（Standard）、`A100`（Standard / HighMem）、`G4`（Standard）、`H100`（Standard）
  - TPU（2 种）：`V5E1`（Standard）、`V6E1`（Standard）

---

## 三、同款 L4 GPU 端到端对比实测（Hosted MCP vs `google-colab-cli v0.7.4`）

测试硬件：两路均分配到 `NVIDIA L4, 23034 MiB`（驱动 `580.82.07`，PyTorch `2.14.1+cu130`，位于 `asia-southeast1` 节点）。
测试负载：执行 `nvidia-smi` 检查 + 20 次 BF16 4096×4096 矩阵乘法（`torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)`）+ 读写 `/content/` 文件。

| 实测项 | Hosted MCP (`colaboratory.googleapis.com/mcp`) | `google-colab-cli v0.7.4` |
|---|---|---|
| 创建 L4 运行时 | `create_runtime` 耗时 `4.52s` + `create_session` 耗时 `2.16s`（合计 `6.68s` 就绪） | `colab new -s bench-l4-1119 --gpu L4` 耗时 `24.85s` |
| 首次代码执行（含 GPU 矩阵乘法） | `execute_code` 耗时 `7.83s`（GPU 内 20 次 BF16 4096 矩阵乘 `266.4 ms`） | `colab exec` 耗时 `8.37s`（GPU 内 20 次 BF16 4096 矩阵乘 `234.2 ms`） |
| 二次同 session 状态保持验证 | `execute_code` 耗时 `2.38s`，成功读取上次变量 `bench_state`（长度 `35`） | 需 `colab repl` 或重新传入脚本执行 |
| 图片输出（`display(Image(...))`） | stdout 仅返回纯文本 `<IPython.core.display.Image object>`，不返回图片本身 | CLI 同样为纯文本输出，但可一条 `colab download` 拉回本地 |
| 文件下载（拉回 `/content/` 产物） | 无原生 MCP 文件工具；需从 `connectionInfo` 取 URL 与约 1 小时过期的 `X-Colab-Runtime-Proxy-Token` 手写 HTTP `GET /files/content/mcp_plot.png`（10,255 字节，耗时 `8.5s`） | 原生命令 `colab download`（耗时 `1.39s`） |
| 文件上传（写入 `/content/`） | 无原生 MCP 文件工具；手写 HTTP `PUT /api/contents/content/uploaded_via_mcp_http.txt` 返回 `HTTP 201`（耗时 `1.03s`），随后 `execute_code` 读取验证成功（`2.4s`） | 原生命令 `colab upload` |
| 挂载 Google Drive / SSH / 实时费率 | 均无原生工具 | 原生 `colab drivemount` / `colab ssh` / `colab usage` |
| 双向运行时可见性 | MCP 开出的 L4 实例，CLI `colab sessions` 可直接看到，且 `colab usage` 实时显示 `Usage rate: 1.94/hr`、`Active assignments: 1` | CLI 开出的 L4 实例，MCP `list_runtimes` 在 `0.67s` 内可查到完整名称与 `connectionInfo` |
| 释放运行时 | `delete_runtime` 耗时 `0.83s` | `colab stop` 耗时 `1.21s` |
| 收尾余额与活跃实例核对 | 余额 `4459.60 compute units`，`Active assignments: 0`，`list_runtimes` 返回 `{}` | 余额 `4459.60 compute units`，`Active assignments: 0` |

---

## 四、测试结论摘要

1. 2026-11-17 发布的托管 MCP 端点（`https://colaboratory.googleapis.com/mcp`）与 2026-03-17 开源的本地浏览器代理（`googlecolab/colab-mcp`）是两套不同架构：前者纯无头远程 HTTP、暴露 10 个固定工具，不需要打开浏览器标签页，也不依赖客户端支持 `notifications/tools/list_changed`。
2. 托管 MCP 与 `google-colab-cli` 共享同一底层 Colab 运行时池（双向可见），冷启动与同 session 有状态多步执行更快更干净（本次实测 L4 开机+建会话合计 `6.68s`，对比 `colab new` `24.85s`），但在**文件传输、Google Drive 挂载、CU 余额/费率监控、SSH 控制台、报错可读性**五个维度明显弱于 `colab-cli`。
3. 生产级重型 GPU 流水线（大模型权重拉取、ComfyUI 视频生成、音色克隆、严格 CU 成本核算）继续使用 `google-colab-cli` 更稳妥；托管 MCP 与底层 `v1beta` REST API 更适合给无终端/轻量 AI Agent 临时挂接云端算力沙盒，以及做标准化后端编排。
