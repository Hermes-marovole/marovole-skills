# Claude Code 防封实战：十步环境洗白与注册稳定使用全指南 - X2Doc 整理

> 来源：https://x.com/servasyy_ai/status/2120148425744449904
> 作者：@servasyy_ai (huangserva)
> 原文发布：2026-11-10
> 整理时间：2026-11-10
> 来自翡冷翠

---

## TL;DR

- **连环封号的真凶不是“聊天暴露国籍”，而是硬信号残留**：跨账号复用的设备指纹（`~/.claude.json` 中的 `userID`/`machineID`、桌面端 `ant-did`/`ant-device-registry.json`/`ccd-ids.json`）、新号读取旧账号的历史对话 session（`~/.claude/projects`）、泄露真实网络的 DNS/UDP(QUIC)/hCaptcha/Datadog 遥测直连，以及被标记过的脏出口 IP。
- **对照实验证实环境隔离有效**：作者在用了 10 个月的 20X Max 账号被封并遭遇连环封 3 个号后，用 Codex 对整台 Mac 做只读取证与 10 步清理；清理后的 5X 新号稳定运行超过 1 个月未封，而故意放入未清理环境的测试号第二天即被封。
- **注册与 KYC 两道关卡解法**：手机号验证切勿用接码平台，推荐 **RedPocket 美国年付套餐（$30/年，eBay 购买支持国内 PayPal）+ 华强北超雪 BeeSIM 实体写卡（$19.9）**；若订阅升级弹出 Persona KYC 认证，**中国护照可直接通过**（Persona 政策允许中国护照）。
- **网络与代理铁律**：换号必须同时换 IP；代理切忌用 `url-test`/`fallback` 自动切换组，必须用单节点 `select` 锁死独享出口；禁掉 UDP（防 QUIC 绕过）与全局 IPv6；DNS 全面改用经固定代理节点出口的 DoH（清空国内 fallback/direct DNS）；对 `/Applications/Claude.app/Contents/` 做进程级路由兜底（防 hCaptcha 与 Datadog 遥测直连）。
- **最隐蔽的翻车点**：千万不要让新号导入或读取旧账号的 `~/.claude/projects` 历史会话，也不要在全局 `~/.claude/CLAUDE.md` 中保留与被封账号强绑定的个人敏感标识。

---

## 原帖核心内容

### 背景与对照验证

作者（`@servasyy_ai`）使用约 10 个月的 Claude Code（20X Max 账号）被封，随后换新号遭遇连环封杀。到第三个号被封时，停止盲目开号，让 Codex 对整台 Mac 执行**“先只读取证、再备份清理、最后逐项核验”**的系统级排查。

排查挖出的核心问题包括：
1. **跨账号沿用的设备指纹**：`~/.claude.json` 与历史备份对比，`account ID` 变了，但 `userID` 和 `machineID` 完全一致；桌面端 `Application Support/Claude/` 下的 `ant-device-registry.json`、`ant-did`、`ccd-ids.json` 持续保留设备指纹。
2. **后台僵尸进程残留 Token**：界面退出后，底层进程未死，环境变量里仍带着旧 OAuth 凭据。
3. **代理名不副实与协议泄漏**：策略组名称与实际出口国家不符；QUIC（UDP）绕过、系统 DNS 直连国内上游（`223.5.5.5`、`119.29.29.29`）、`hCaptcha` 人机验证与 `datadoghq` 遥测绕过代理直连。
4. **系统时区暴露**：系统时区仍为 `Asia/Shanghai`。

**正反对照结果**：按十步法洗净环境后新开的 5X 账号已稳定运行 1 个月以上（另一台按记录新起的号也已稳定 2 周以上）；而故意放进未整理环境的对照测试号**第二天立刻被封**。

---

### 十步完整实操流程

#### 第一步：注册手机号验证 —— RedPocket + BeeSIM 备一个真实美国号（按需）
- **核心原则**：绝不用公共接码平台（一上来就背负关联风控）。
- **推荐组合**：RedPocket 美国号（eBay 年付 $30，每 30 天含 200MB 流量）+ BeeSIM 实体转换卡（$19.9 买断，华强北超雪团队出品，带可擦写 eSIM 芯片与蓝牙，解决国行 iPhone 无法直接装海外 eSIM 的问题）。
- **操作步骤**：
  1. **eBay 购买套餐**：在 eBay（`https://www.ebay.com/itm/136840233242`）选 `$30/年` 档位，下拉选 `eSIM Phone Kit (Most popular)`，支持中国 PayPal 付款（比官网便宜且无需美卡）；地址填美国免税州地址，电话填国内手机号。
  2. **激活与漫游**：收邮件拿到 Confirmation Code，在手机“设置 → 通用 → 关于本机”查 MEID/IMEI，去 `redpocket.com/activate` 激活；在账户 Roaming 页面开启漫游并选 `CHINA`（若 Roaming Balances 为 0 找客服补回或退换）。
  3. **写入 BeeSIM 实体卡**：插卡后使用官方 App「BeeSIM - eSIM BLE Apdater」（开发者 `BEESIM TECHNOLOGY CO., LIMITED`，黄蜜蜂图标，勿下错成别家的出境旅行 eSIM）、微信小程序「BeeSIM」或网页版 `beeesim.com/ble`，蓝牙连接 BeeSIM 扫 RedPocket 二维码写卡并开启漫游。

#### 第二步：订阅升级弹 KYC？中国护照直接过（按需）
- **升档节奏**：先开 Pro 养号几天再考虑升 Max，切忌新号直接升 Max（极易秒弹 KYC 甚至封号）。
- **KYC 应对**：Anthropic 的 KYC 由第三方身份核验商 **Persona** 承接，其政策允许使用**中国护照**（照顾在美华人与留学生）。弹出 KYC 不是封号判决书，只要网络与设备环境干净，直接用中国护照按流程实名即可正常通过。

#### 第三步：先让 Codex 做只读排查，别急着盲删
动手前先让 Agent 做只读审计并输出证据路径：
```text
我的 Claude Code 账号被封了。先不要改任何东西，只读排查这台 Mac：
1. 对比 ~/.claude.json 和历史备份，看账号标识、userID、machineID 是否跨账号沿用
2. 检查正在运行的 Claude Code 相关进程，环境里是否还带着旧 OAuth token
3. 检查桌面端 Application Support 里的设备标识、Cookie、缓存
4. 检查系统时区、系统 DNS、代理实际出口
每一项给出证据路径，先列清单，我确认后再动手。
```

#### 第四步：本地清理 —— `claude-cleanup` Skill 打底 + 深度补刀
1. **使用 `claude-cleanup` Skill**（`https://github.com/suyuan2022/suyuan-skill/blob/main/claude-cleanup/SKILL.md`）先做只读审计，确认后再执行（自带全量备份校验、白名单+保护区双重检查、移入废纸篓可恢复）。
2. **先停进程再动磁盘**：彻底退出所有 Claude 桌面端、CLI、辅助进程、自启服务、切换器与监控脚本，防止边删边写回。
3. **划定保护区（清理前后做校验）**：
   ```text
   ~/.claude/projects  skills  plugins  file-history
   ~/.claude/CLAUDE.md  settings.json
   Application Support/Claude/claude_desktop_config.json   # MCP 配置
   ```
   *(注：保护区文件先保留不误删，但 `~/.claude/projects` 必须在第十步打包迁出，不能留给新号读)*
4. **清除身份、缓存与设备指纹本体**：
   ```text
   ~/.claude/.credentials.json
   ~/.claude/backups  sessions  session-env  shell-snapshots
   ~/.claude/debug  telemetry  statsig
   ~/.claude.json.backup

   Application Support/Claude/config.json
   Application Support/Claude/Cookies  "Local Storage"  IndexedDB
   Application Support/Claude/ant-device-registry.json  ant-did  ccd-ids.json
   Application Support/Claude/sentry  Cache  Crashpad
   ~/Library/Caches/com.anthropic.claudefordesktop
   ~/Library/HTTPStorages/com.anthropic.claudefordesktop
   ```
   **关键提醒**：只删 Cookie 不删 `ant-did`、`ant-device-registry.json`、`ccd-ids.json` 等于没清；用过桌面端 Cowork 的还需检查清理 `Application Support/Claude/vm_bundles/`。
5. **`~/.claude.json` 字段级白名单清洗**：保留 `projects`、`mcpServers` 等配置键，清除 `userID`、`machineID`、账号缓存等身份标识键。
6. **清理 macOS 钥匙串**：
   ```bash
   security delete-generic-password -s "Claude Safe Storage"
   ```

#### 第五步：浏览器残留清零（一个都别放过）
- 覆盖所有安装的浏览器（Chrome、Safari、Arc、Brave、Edge 等）及所有 Profile。
- 彻底清除以下 4 个域名的 Cookie、Local Storage、IndexedDB 及站点权限，并移除相关浏览器扩展：
  - `claude.ai`
  - `claude.com`
  - `anthropic.com`
  - `claudeusercontent.com`
- 可配合开源审计工具 `Pluviobyte/claude-ban-clean` 定期复查，防止浏览器同步或后台静默长回旧 Cookie。

#### 第六步：代理出口 —— 名字不算数，抓到的真实 IP 才算数
- **四大原则**：
  1. **换号必须同时换 IP**：被封过号的出口 IP 大概率已进风控名单，必须换用未死过号的干净 IP。
  2. **纯净度与类型**：优先独享住宅 IP 或独享自建 VPS，避开千人共用的万人骑机场节点。
  3. **绝对固定（不自动跳）**：策略组必须用 `select` 单节点锁死，**严禁用 `url-test` 或 `fallback`**。
  4. **地区建议**：推荐台湾（TW）或固定美西独享节点（TW 为官方支持区，GMT+8 与北京时间一致，配合台北时区完全自洽）。
- **Mihomo / Clash 核心规则配置（含禁 UDP 防 QUIC 泄露 + 关 IPv6）**：
  ```yaml
  ipv6: false
  dns:
    ipv6: false

  proxy-groups:
    - name: Claude专用
      type: select
      proxies:
        - 你的固定节点        # 没有备选，不会自动跳

  rules:
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,claude.ai)),REJECT
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,anthropic.com)),REJECT
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,claude.com)),REJECT
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,claudeusercontent.com)),REJECT
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,claudemcpcontent.com)),REJECT
    - DOMAIN-SUFFIX,claude.ai,Claude专用
    - DOMAIN-SUFFIX,anthropic.com,Claude专用
    - DOMAIN-SUFFIX,claude.com,Claude专用
    - DOMAIN-SUFFIX,claudeusercontent.com,Claude专用
    - DOMAIN-SUFFIX,claudemcpcontent.com,Claude专用
  ```

#### 第七步：DNS 统一接管（防国内 DNS 抢答泄露）
- 将系统 DNS 指向 `127.0.0.1`，Clash DNS 全部走指定固定节点出口的加密 DoH，清空 `fallback` 与 `direct-nameserver`：
  ```yaml
  dns:
    enable: true
    listen: 127.0.0.1:53
    ipv6: false
    enhanced-mode: redir-host
    nameserver:
      - https://8.8.8.8/dns-query#你的固定节点
    default-nameserver:
      - https://8.8.8.8/dns-query#你的固定节点
    proxy-server-nameserver:
      - https://8.8.8.8/dns-query#你的固定节点
    fallback: []
    direct-nameserver: []
  ```

#### 第八步：进程级路由兜底（堵死验证码与遥测直连）
- 抓包发现桌面端启动时，`hCaptcha` 人机验证和 `datadoghq` 遥测会绕过常规域名规则走直连。直接加进程级规则与 `hcaptcha.com` 规则：
  ```yaml
  rules:
    - PROCESS-PATH-REGEX,^/Applications/Claude[.]app/Contents/,Claude专用
    - DOMAIN-SUFFIX,hcaptcha.com,Claude专用
    - AND,((NETWORK,UDP),(DOMAIN-SUFFIX,hcaptcha.com)),REJECT
  ```

#### 第九步：系统时区改台北（`Asia/Taipei`）
- macOS 系统设置 → 通用 → 日期与时间：关闭“自动设定时区”，手动选**台北**；隐私与安全性 → 定位服务 → 系统服务：关闭“设定时区”。
- 与北京时间同为 GMT+8，日常使用零感知，但消除 `Asia/Shanghai` 硬指纹。
- 核验命令：`readlink /etc/localtime` 应输出 `/var/db/timezone/zoneinfo/Asia/Taipei`。

#### 第十步：旧会话必须迁出，千万别让新号读旧对话（连封 4 号的血泪教训）
- **核心死因**：`~/.claude/projects` 下的历史会话带着老账号的标识和上下文；桌面端首次登录弹出“导入 N 个 CLI 会话”时一旦点击导入，或 CLI 新号直接读取旧项目会话，等于主动向风控自首“我是被封老号换皮”。
- **正确处理**：将 `~/.claude/projects` 打包备份后**移出 `~/.claude` 目录**，确保登录时无导入提示；同时检查全局 `~/.claude/CLAUDE.md`，剥离与老账号绑定的敏感个人特征。

---

### 登录前最终验收清单

```text
□ Claude Code 相关进程和自启服务：已停
□ 保护区文件校验：前后一致
□ 钥匙串：无 Claude 条目
□ 浏览器：四个域名 Cookie 和站点存储为 0
□ 出口 IP：实测属于目标地区，且没被封过号
□ DNS：系统指 127.0.0.1，只有加密 DNS 且经同一出口
□ IPv6：关闭，AAAA 查询返回空
□ 桌面端实际连接：API/验证码/遥测同一节点，无绕代理 TCP
□ 时区：Asia/Taipei
□ 旧会话：已迁出，无导入提示，新号没有读过任何旧对话
```

---

### 社区补充方案（文中汇总的其他博主实测经验）

1. **独享 VPS 自建节点**：使用搬瓦工（BWH）或 DMIT 自建独享出口，核心是保证 IP 与支付卡干净固定。
2. **账号资历**：部分用户倾向购买注册 2 年以上的老 Gmail 授权登录。
3. **支付方式**：
   - **Starryblu 新加坡卡**：账单地址填新加坡，港卡 FPS 充值。
   - **美区 Apple 礼品卡内购 + 封号申诉退款**：走 iOS App Store 订阅可隔离信用卡账单风控，且被封后可向 Apple 申诉退回当月订阅费。
   - **升档与额度留白**：新号先订 Pro 用几天再升 Max；20X Max 每周额度建议留 10%–20% 余量，不要 100% 打满触发自动化滥用风控。
4. **WebRTC 泄露检测与隐私开关**：排查浏览器 WebRTC 真实 IP 泄露；新号注册后先去 `Settings → Privacy` 关闭 `Location`、`Help improve Claude`、`Memory`。

---

## 关键信息与资源

| Type | Name | Link | Why it matters |
|---|---|---|---|
| 原帖 X Article | Claude Code 防封实战（@servasyy_ai） | https://x.com/servasyy_ai/status/2120148425744449904 | 十步完整排查、清理、网络加固与对照验证复盘 |
| GitHub Skill | `suyuan2022/suyuan-skill` (`claude-cleanup`) | https://github.com/suyuan2022/suyuan-skill/blob/main/claude-cleanup/SKILL.md | ★ 481 (MIT)，带备份校验与保护区白名单的 Claude 本地清理 Skill |
| GitHub Tool | `Pluviobyte/claude-ban-clean` | https://github.com/Pluviobyte/claude-ban-clean | ★ 280，用于扫描和审计浏览器及本地残留的防封清理工具 |
| 硬件/套餐 | RedPocket 年付 $30 eSIM (eBay) | https://www.ebay.com/itm/136840233242 | 真实美国手机号低成本长期持有方案，支持国内 PayPal |
| 参考推文 | 余温 (@gkxspace) 防封与美卡实操 | https://x.com/gkxspace/status/2101993381303820704 | 搬瓦工/DMIT 自建节点 + RedPocket 美国号经验源头 |
| 参考推文 | 逸尘 (@gengdaJ) Persona KYC 实测 | https://x.com/gengdaJ/status/2108363527971041650 | 实测用中国护照直接通过 Claude Persona KYC 身份认证 |
| 参考推文 | 泊舟 (@bozhou_ai) 防封补充 | https://x.com/bozhou_ai/status/2109836627539558676 | 苹果礼品卡订阅退款、升档节奏、WebRTC 与隐私开关经验 |

---

## 我的吸收判断（映射到我们现有的本机环境）

结合我们当前 MacBook Pro (M2 Max) 的真实基础设施与账号配置，做如下对比与落地方案：

1. **网络基础设施（我们已经具备天然优势，只需补齐规则细节）**：
   - 我们本机已配置 **FlClash (`Neuma-Personal.yaml` 锁死 LA7 `179.255.121.235`)**，且明确区分了 **Claude 走 BWH（搬瓦工）、其他 AI 走 DMIT** 的分流架构——这比文章里普通用户从零找住宅代理起点高得多。
   - **待加固项**：对照文章第 6–8 步，我们需要检查 FlClash 配置中针对 `claude.ai` / `anthropic.com` / `claude.com` / `claudeusercontent.com` / `claudemcpcontent.com` / `hcaptcha.com` 是否已加 **UDP REJECT（防 QUIC 绕过）**，以及是否已加 **`PROCESS-PATH-REGEX,^/Applications/Claude[.]app/Contents/`** 进程级兜底（防止桌面端 Datadog 遥测与 hCaptcha 直连）。
2. **账号与支付链路（已验证可用）**：
   - 我们目前已有 **Claude Pro（`marovolek@gmail.com`，Stripe 绑定，显示名 Thomas）**，且之前已验证过“国行卡+真实地址或 IDE/App 内购”及 DevinMax ($200) 的 Opus 额度替代路径。
   - 若后续需要把官方 Claude Pro 升级到 Max 或新开备用官方号：遵循**“先 Pro 养号再升 Max、周额度留 10%–20%”**原则；万一弹出 Persona KYC，无需换号，直接用中国护照过审。
3. **本机指纹与新旧号切换红线（最值得警惕）**：
   - 如果这台 Mac 曾经登录过任何被封或异常的 Claude 账号，在登录/切换新官方账号前，**必须做一次只读排查**（重点查 `~/.claude.json` 的 `userID`/`machineID`、`~/Library/Application Support/Claude/ant-did` 等三个指纹文件，以及迁移 `~/.claude/projects` 旧会话）。
   - 如果当前 `marovolek@gmail.com` 账号一直正常使用、从未被封过，**切忌盲目清理当前正在正常工作的登录态和设备指纹**（正常账号突然丢失所有历史设备指纹+跳环境反而可能触发异地盗号风控），优先做**网络层加固（禁 QUIC UDP + 进程兜底 + 时区 `Asia/Taipei`）**即可。

---

## 可执行下一步

- [ ] **只读体检（不改文件）**：对本机当前 Claude 环境（`~/.claude.json`、`Application Support/Claude`、FlClash 规则、系统时区与 DNS）做一次只读审计，确认是否存在 UDP/QUIC 漏网、遥测直连或历史脏指纹。
- [ ] **FlClash 规则补强（经确认后执行）**：在备份配置的前提下，为 Claude 分流组补齐 5 个核心域名 + `hcaptcha.com` 的 UDP REJECT 规则与 `Claude.app` 进程兜底规则。
- [ ] **系统时区无感切换**：在 macOS 系统设置中将时区由 `Asia/Shanghai` 手动改为 `Asia/Taipei`（同为东八区 GMT+8，不影响任何 cron 与日常时间显示）。

---

*来自翡冷翠*
