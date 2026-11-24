# Decompiled Sources → Live HTTP API

Use after the dex is unpacked (see `packed-apk-unpacking.md`). Goal: turn 30k+ java files into a verified endpoint map, a reconstructed header set, and a callable request — without touching the user's account.

## 1. Harvest endpoints from Retrofit annotations

The interfaces are declarative, so plain text scans beat class-by-class reading:

```bash
grep -rhoE '@(GET|POST|PUT|DELETE|PATCH)\("[^"]+"\)' work/src/sources --include=*.java \
  | sed -E 's/@[A-Z]+\("//; s/"\)//' | sort -u > endpoints.txt
```

Then attribute each path to its defining interface for a real map:

```bash
grep -rn '@GET("\|@POST("' work/src/sources --include=*.java \
  | sed 's#.*sources/##' > api_map.tsv    # path + defining class/module
```

Counts drift by one depending on trailing newline — `wc -l` vs `sort -u | wc -l` disagree; report the counted number, not the eyeball.

Namespace grouping (`/meta-interface/`, `/app-interface/`, `/shop-interface/`, `/ai-interface/`, `/open-interface/`) is the fastest way to present a 500-endpoint surface: one table row per namespace with a representative path beats a flat list dump.

## 2. Map the client class for base URLs

Find the singleton/`Client` class that builds Retrofit; it usually hardcodes one base URL per subdomain (`api`, `food`, `passport`, `record`, `sleep`, …) plus per-environment suffixes (`api{env}.domain.com`). Read it before assuming a single host. Same class is where `SSLSocketFactory`, `hostnameVerifier`, and the interceptor chain are wired — **that wiring, not the presence of a helper class, is what decides whether a security finding is real** (a `trustAllCerts()` method that is never passed to `sslSocketFactory` is dead code; do not report it as a live vulnerability).

## 3. Reconstruct the request header set from the interceptor

A network interceptor that appends 15–20 duplicate-case headers (`token` and `Token`, `User-Agent` and `UserAgent`) is normal in CN apps — replay the exact set rather than the "sensible" minimum, since server-side risk control often reads the odd one. Record it in one place (a `HEADERS` dict in the probe script) so curl reproductions match the app.

Signing: look for `rule`, `sign`, `nonce`, `timestamp` in the interceptor. When the "signature" turns out to be `base64(f"{unix}{constant}")`, say so plainly — it is obfuscation, not cryptography, and that distinction is a finding.

## 4. Prefer guest auth over the user's credentials

When the app has an anonymous/guest login, use it. Do not pull the user's token out of MMKV/prefs, and never print any token. Guest login is also the honest way to prove an endpoint is reachable by anyone with the APK.

## 5. Verify against the live server before writing anything down

```bash
curl -s -o /dev/null -w '%{http_code}\n' '<endpoint>?q=test'
```

- `405` on a HEAD request means the route exists.
- A 200 with an empty `data` array is not proof of an endpoint — re-test with a known-good query string.
- Only after a real JSON payload comes back do the field names belong in a report or a mapping doc.

## 6. SSE / streaming endpoints

Look for `EventSource`, `RealEventSource`, or a `<something>Stream` path. Those endpoints do not answer to plain curl-with-JSON — grep the response consumer to see the event names and payload shape instead of guessing from the URL.

## Compliance line

Sampling ~20 rows to learn field names and units is teardown. Harvesting a catalogue through an authenticated API at scale is not, and should be declined with the public-data alternative offered instead.
