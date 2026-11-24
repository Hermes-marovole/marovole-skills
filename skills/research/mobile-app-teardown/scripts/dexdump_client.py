#!/usr/bin/env python3
"""把 rea_dexdump.js 注入目标进程，落盘 dex。

前提：设备已 root，frida-server 已推送并监听 127.0.0.1:27042，且已 adb forward。

用法：
  python3 dexdump_client.py <包名或PID> [输出目录] [frida地址]
  默认 frida 地址 127.0.0.1:27042，默认输出 ./dumped

落盘后 dex 头部校验多是坏的，跑 fix_dex_headers.py 修完再交给 jadx/REA。
"""
import os, sys, time, hashlib
import frida

HOST = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1:27042"
target = sys.argv[1] if len(sys.argv) > 1 else None
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "./dumped")
if not target:
    print(__doc__); sys.exit(1)
os.makedirs(OUT, exist_ok=True)

dev = frida.get_device_manager().add_remote_device(HOST)
pid = int(target) if target.isdigit() else next(
    (p.pid for p in dev.enumerate_processes() if p.name.startswith(target)), None)
if pid is None:
    print("[-] 找不到进程:", target); sys.exit(1)

print(f"[*] attach pid={pid}")
session = dev.attach(pid)
script = session.create_script(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 "rea_dexdump.js")).read())
state = {"done": False, "n": 0}


def on_message(msg, data):
    if msg["type"] == "send":
        p = msg["payload"]
        if p.get("t") == "dex":
            name = f"dex_{p['size']:08x}_{p['addr'].replace('0x', '')}.dex"
            open(os.path.join(OUT, name), "wb").write(data)
            state["n"] += 1
            print(f"[+] {name}  {p['size']/1048576:.2f}MB  sha256:{hashlib.sha256(data).hexdigest()[:16]}")
        elif p.get("t") == "done":
            state["done"] = True
            print(f"[*] 扫描 {p.get('scanned', 0)/1048576:.0f}MB，命中 {p.get('hits')}")
    elif msg["type"] == "error":
        print("[-]", msg.get("description"), (msg.get("stack") or "")[:400])


script.on("message", on_message)
script.load()
deadline = time.time() + 300
while time.time() < deadline and not state["done"]:
    time.sleep(1)
print(f"[*] 共 {state['n']} 个 dex → {OUT}")
try:
    session.detach()
except Exception:
    pass
