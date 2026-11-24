#!/usr/bin/env python3
"""对拍同一个模型在多条 provider 线路上的速度（默认经本机 magpie 网关）。

为什么要里程碑而不是 TPS：带思考的线路把 reasoning_content 也算进 completion_tokens，
同一句提示词它能多算近一倍 token，用 completion_tokens/时长 反而给它算高分。
这里只数**可见正文**的字符，记「首个可见字 / 前 100 字 / 前 300 字 / 全文」。

用法:
  python3 provider_speed_test.py neumaapi/deepseek-v4.1-flash:1017 mistral/deepseek-v4-1-flash-1017
  python3 provider_speed_test.py --rounds 6 --max-tokens 900 A_model B_model

环境变量:
  MAGPIE_URL  默认 http://127.0.0.1:3425/v1/chat/completions
  MAGPIE_KEY  默认 magpie
"""
import argparse
import json
import os
import statistics
import subprocess
import time

GW = os.environ.get("MAGPIE_URL", "http://127.0.0.1:3425/v1/chat/completions")
KEY = os.environ.get("MAGPIE_KEY", "magpie")
PROMPT = ("请直接输出一篇约400字的中文短文，主题：为什么产品经理应该懂一点AI。"
          "不要开场白、不要解释你的思路，直接给正文。")
MILESTONES = [100, 300]
OUT = os.path.expanduser("~/.hermes/cache/scratch/provider_speed.jsonl")


def run(model, max_tokens):
    body = {"model": model, "stream": True, "stream_options": {"include_usage": True},
            "messages": [{"role": "user", "content": PROMPT}], "max_tokens": max_tokens}
    t0 = time.perf_counter()
    p = subprocess.Popen(["curl", "-sN", "-m", "180", GW,
                          "-H", f"Authorization: Bearer {KEY}",
                          "-H", "Content-Type: application/json",
                          "-d", json.dumps(body)],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    marks, usage, chars, reasoning, tf = {}, None, 0, 0, None
    for raw in p.stdout:
        line = raw.decode("utf-8", "ignore").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except Exception:
            continue
        ch = (obj.get("choices") or [{}])[0]
        msg = ch.get("delta") or ch.get("message") or {}
        reasoning += len(msg.get("reasoning_content") or msg.get("reasoning") or "")
        c = msg.get("content") or ""
        if c:
            if tf is None:
                tf = time.perf_counter() - t0
            chars += len(c)
            for m in MILESTONES:
                if chars >= m and m not in marks:
                    marks[m] = time.perf_counter() - t0
        if obj.get("usage"):
            usage = obj["usage"]
    p.wait()
    total = time.perf_counter() - t0
    u = usage or {}
    return dict(total=round(total, 3), ttft_ms=round((tf or 0) * 1000),
                marks={str(k): round(v, 3) for k, v in marks.items()},
                vis_chars=chars, reasoning_chars=reasoning,
                ctok=u.get("completion_tokens"), ptok=u.get("prompt_tokens"),
                cached=(u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                reasoning_tok=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"))


def med(vals):
    vals = [v for v in vals if v is not None]   # 按 None 过滤，不要按真值过滤：0 是合法值
    return statistics.median(vals) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+", help="provider/model 形式的完整路由 id")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=900)
    a = ap.parse_args()

    rows = []
    for r in range(a.rounds):
        order = list(a.models)
        if r % 2:
            order.reverse()          # 奇偶轮反转，抵消预热与网络漂移
        for model in order:
            res = run(model, a.max_tokens)
            res.update(model=model, rnd=r + 1)
            rows.append(res)
            print(f"r{r + 1} {model:44s} ttft={res['ttft_ms']:5d}ms "
                  f"t100={res['marks'].get('100')} t300={res['marks'].get('300')} "
                  f"total={res['total']:.2f}s visch={res['vis_chars']} "
                  f"reason_ch={res['reasoning_chars']} ctok={res['ctok']}", flush=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(json.dumps(x, ensure_ascii=False) for x in rows))

    print("\n=== 中位数 ===")
    for model in a.models:
        rs = [x for x in rows if x["model"] == model]
        t100 = [float(x["marks"]["100"]) for x in rs if "100" in x["marks"]]
        t300 = [float(x["marks"]["300"]) for x in rs if "300" in x["marks"]]
        print(f"{model:44s} TTFT={med([x['ttft_ms'] for x in rs]) or 0:5.0f}ms "
              f"t100={med(t100)} t300={med(t300)} "
              f"total={med([x['total'] for x in rs]) or 0:.2f}s "
              f"visch={med([x['vis_chars'] for x in rs]) or 0:.0f} "
              f"reason_ch={med([x['reasoning_chars'] for x in rs]) or 0:.0f} "
              f"ctok={med([x['ctok'] for x in rs]) or 0:.0f}")
    print(f"\n原始数据: {OUT}")


main()
