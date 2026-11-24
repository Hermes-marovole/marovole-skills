#!/usr/bin/env python3
"""修内存 dump 出来的 dex 头部校验，并去重。

顺序不能反：adler32 覆盖范围包含签名字段（12:32），必须先把 sha1 写进去再算 adler。

用法：python3 fix_dex_headers.py <dump目录> <输出目录>
"""
import os, sys, struct, zlib, hashlib, shutil

src = sys.argv[1] if len(sys.argv) > 1 else "./dumped"
out = sys.argv[2] if len(sys.argv) > 2 else "./fixed"
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out, exist_ok=True)

seen, kept, bad = {}, 0, 0
for f in sorted(os.listdir(src)):
    if not f.endswith(".dex"):
        continue
    raw = open(os.path.join(src, f), "rb").read()
    if raw[:4] != b"dex\n":
        bad += 1
        continue
    h = hashlib.sha256(raw).hexdigest()
    if h in seen:
        continue
    (size_hdr,) = struct.unpack_from("<I", raw, 32)
    d = bytearray(raw[:size_hdr])
    if len(d) < size_hdr:
        d += b"\x00" * (size_hdr - len(d))
    d[12:32] = hashlib.sha1(bytes(d[32:])).digest()
    d[8:12] = struct.pack("<I", zlib.adler32(bytes(d[12:])) & 0xFFFFFFFF)
    seen[h] = f
    open(os.path.join(out, f), "wb").write(d)
    kept += 1

print(f"[*] 保留 {kept} 个唯一 dex，丢弃 {bad} 个非 dex → {out}")
