# 加固 APK（360 加固保）脱壳与离线分析

真机/模拟器上遇到 `com.stub.StubApp` 壳时，JADX 只能看到 5 个类，静态分析等于零。下面是本机验证过的完整路径（macOS + MuMu Pro Android 12）。

## 0. 判定是不是壳

```bash
unzip -p app.apk classes.dex | strings -a | grep -iE "stub|jiagu|packer|shell|decrypt"
# 命中 .jiagu / libjiagu / Lcom/stub/StubApp; 同时 assets/.jgapp 存在 → 360 加固保
```

REA 的 `search-android-classes` 空查询会直接暴露 `total_classes: 5`，比 grep 更快。

## 1. 环境（REA + JADX 桥）

- Node 必须是 22.x ≥22.23.4 / 24.x ≥24.22.1 / 26.12.1+。本机 brew 的 node 26.10.0 **不合格**，用 `~/.hermes/tools/node-26.12.1-darwin-arm64/bin` 前置 PATH。
- JADX 桥 JAR 必须钉 0.7.1（`1013503897/jadx-headless-mcp`），sha256 `6e5eacf5…ff75`，设 `REA_JADX_MCP_JAR`；`Samael-Z/jadx-headless-mcp` v1.x 的包布局不同，REA 会拒。
- 需要完整 JDK 17+（jdk.compiler 模块），`JAVA_HOME=/opt/homebrew/opt/openjdk@21`。
- `REA_APKTOOL_COMMAND=/opt/homebrew/bin/apktool`。

## 2. 取 root

MuMu 的 `adb root` 默认报 `adbd cannot run as root in production builds`，且没有 su。先改 VM 配置：

```bash
mumutool config 0 --setting '{"rootPermission":true}'
sleep 3 && adb -s 127.0.0.1:16384 root && adb -s 127.0.0.1:16384 shell id   # uid=0
```

## 3. frida-server

推 17.x（与本地 frida 同版本），**改名**并绑本地端口，避免被壳的端口/进程名扫描命中：

```bash
adb push frida-server /data/local/tmp/mdservice && adb shell chmod 755 /data/local/tmp/mdservice
adb shell "nohup /data/local/tmp/mdservice -l 127.0.0.1:27042 >/dev/null 2>&1 &"
adb forward tcp:27042 tcp:27042
```

## 4. 关键坑：Java 桥在 MuMu/Android 12 上不可用

现象：原生 attach 正常（`console.log(Process.arch)` 有输出），但 `Java.perform()` 静默无输出、连接被关。对照非加固 App（Keep、系统设置）同样失败 → **不是反调试**，是 Java 桥本身不可用。不要在这上面耗时间判断壳强度。

对策：写纯原生层内存扫描器（`dexdump.js` 见 `references/` 同目录思路），只依赖 `Process.enumerateRanges` + `Memory.scanSync` + `addr.readByteArray(size)`。注意 frida 17 里 `Memory.readByteArray(addr,size)` 已不可用，要用 `NativePointer.readByteArray`。

## 5. 内存扫描要点

- 只扫 `r--` 且跳过 `/system/`、`/apex/` 前缀的 file-backed 段，单段上限 256MB（`partition_alloc` 段可达 16GB 虚拟空间，扫它会卡死）。
- 魔数扫 `64 65 78 0a`，再用头部校验：`header_size@36 == 0x70`、`endian@40 == 0x12345678`、`file_size@32` 在 0x70–80MB 之间。
- 同一个 dex 会在多处出现（原始密文、解密副本、各 ClassLoader），按 sha256 去重。
- **最大的那个 dex 往往不是业务包**：壳会把原 APK 的 `classes.dex` 原样映射进内存（`base.apk` 的 `r--p` 段），扫描器会把它当战利品抓出来——sha256 与原包逐字节相同、`class_defs` 只有 4。排除条件必须包含「映射文件路径本身是 `*.apk`」的段，只跳 `/system/`、`/apex/` 不够；抓完先 `cmp` 一遍原包 `classes.dex` 再编号。
- **按 dex 版本分类再下结论**：`dex\n037` 的匿名段才是壳解密出来的业务代码（本次 16 段 / 85.5MiB，是壳体积的 3.1 倍）；`dex\n035` 里除原包映射外还有第三方 SDK 自己的动态插件包（anythink、zx-core）。报告里写「业务代码体量」只能统计 037 段，混进去会把 35 段的原包映射算成自研代码。
- 磁盘上永远没有明文业务 dex：壳解到匿名内存再交给 `InMemoryDexClassLoader` 一类路径加载，落地只剩 `files/libs/tdata_*` 两枚和 vdex 残留——所以别去 `/data/data/<pkg>` 找 dex，也别假设「解密后的明文会写回某个文件」。

## 6. 修 dex 头部校验（必须按顺序）

内存快照的 dex 头部校验多半是坏的，jadx 会 `Bad dex file checksum` 直接跳过整个 dex。修复顺序不能反——adler32 覆盖范围**包含**签名字段：

```python
size_hdr, = struct.unpack_from('<I', d, 32)
d = bytearray(raw[:size_hdr])                       # 按头部长度截断/补零
d[12:32] = sha1(bytes(d[32:])).digest()             # 先写签名
d[8:12]  = pack('<I', adler32(bytes(d[12:])))       # 再算校验和
```

先算 adler 再写签名 → 17 个 dex 依然全坏，jadx 仍报错。

## 7. 重建可分析 APK

把 `AndroidManifest.xml` + `resources.arsc` + `res/` 从原包解出，替换 `classes*.dex` 为脱壳 dex：

```bash
mkdir apk && cd apk
unzip -q ../../app.apk -x 'classes*.dex' 'META-INF/*'
i=0; for f in ../../fixed/*.dex; do [ $i -eq 0 ] && cp "$f" classes.dex || cp "$f" classes$i.dex; i=$((i+1)); done
zip -q -r ../unpacked.apk .        # 注意：必须在目录内部打包，否则 manifest 带 apk/ 前缀，REA 报 Root AndroidManifest.xml not found
```

REA 对脱壳包的 `class_count` 应从上万级（本次 39,043）体现，仍为个位数说明 dex 没进去。

## 8. 接口图谱的提取口径

jadx `--no-res` 全量反编译后，用正则抓 Retrofit 注解，比手工翻类快一个数量级：

```python
ann = re.compile(r'@(GET|POST|PUT|DELETE|PATCH)\("([^"]+)"\)')
```

统计要区分「唯一路径」和「(方法,路径) 组合」——本次前者 497、后者 513，混用会在报告里自相矛盾。命名空间合计对不上总数时，差额通常来自漏写前导斜杠的路径和完整 URL 写法，逐条列出再解释，不要抹平成「约」。

## 9. 常见事实陷阱

- `targetSdk`/`compileSdk` 只能从 manifest 读，别按 minSdk 推。
- 广告 SDK 的「命中 openai/hunyuan」多半是噪音：`AI_MODE_OPENAI = 1` 是枚举常量，`com.tencent.hunyuan.app.chat` 是广告 SDK 的已装应用映射表。要断言「客户端无 LLM 供应商」必须给出精确检索结果，不能只说「搜不到」。
- 字节数换算：99,070,273 bytes = 94.5 MiB，不是 94.3MB。**MiB 一律自己从各 dex 头部 `file_size` 加总重算**，不要采信核查 agent 给的单位结论（同一批 16 个 037 dex 曾被换算成「91.26 MiB」，按字节实为 85.49MiB，倍数也跟着从 3.16 掉到 3.10）。
- 「加密」先查方向：断言请求体加密前，确认拦截器里有对应的 encrypt 方法且被调用；只做 `content_type==1` 响应的 decrypt 就写「仅下行解密、上行明文 JSON」。方向写反是结论级错误。
- 「信任任意证书」先查调用点：`grep -rn getTrustAllCert()` 无命中、几个 OkHttpClient 都没挂 `sslSocketFactory` → 那是死代码；真正的洞是 `hostnameVerifier.verify()` 恒 `return true` 加全局 `cleartextTrafficPermitted="true"`。半成品安全代码比没有更容易误判，每条漏洞结论都要落到「被谁调用、在哪个 client 上生效」。
- **规模口径三选一并全文统一**：`.java` 文件数 / `class_defs` / dex 描述符引用次数，三者能差三倍以上（本次同一块自有代码 15,823 / 5,618 / 19,340）。SDK 之间比较一律同一个口径，跨口径并列会被一眼看穿。
- 计数类断言用代码数，不靠眼数：grep 字面量会漏掉写成常量的头名（`HttpHeaders.USER_AGENT`），19 个请求头只数出 18 个。
- 组件清单有读取容量上限（本次 512 项触顶），报告里要标「部分覆盖」，不能当全量陈述。
