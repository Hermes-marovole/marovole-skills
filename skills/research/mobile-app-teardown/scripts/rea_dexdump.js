// 纯原生层 dex 内存扫描器（不依赖 Java 桥）
// 用法见 scripts/dexdump_client.py
var seen = {}, total = 0, hits = 0;

function okHeader(addr) {
  try {
    var fileSize = addr.add(32).readU32();
    var headerSize = addr.add(36).readU32();
    var endian = addr.add(40).readU32();
    if (headerSize !== 0x70) return 0;
    if (endian !== 0x12345678 && endian !== 0x78563412) return 0;
    if (fileSize < 0x70 || fileSize > 80 * 1024 * 1024) return 0;
    return fileSize;
  } catch (e) { return 0; }
}

Process.enumerateRanges("r--").forEach(function (r) {
  var label = r.file ? r.file.path : "";
  if (label.indexOf("/system/") === 0 || label.indexOf("/apex/") === 0) return;
  if (r.size > 256 * 1024 * 1024) return;
  total += r.size;
  var cursor = r.base, remaining = r.size;
  while (remaining > 0x1000) {
    var chunk = Math.min(remaining, 8 * 1024 * 1024);
    var found;
    try { found = Memory.scanSync(cursor, chunk, "64 65 78 0a"); } catch (e) { break; }
    found.forEach(function (m) {
      var addr = m.address, size = okHeader(addr);
      if (!size) return;
      var key = addr.toString();
      if (seen[key]) return;
      seen[key] = true; hits++;
      var ver = String.fromCharCode(addr.add(4).readU8(), addr.add(5).readU8(), addr.add(6).readU8());
      try {
        send({ t: "dex", addr: key, size: size, ver: ver }, addr.readByteArray(size));
      } catch (e) { console.log("[!] read fail " + key + " " + e); }
    });
    cursor = cursor.add(chunk); remaining -= chunk;
  }
});
send({ t: "done", hits: hits, scanned: total });
