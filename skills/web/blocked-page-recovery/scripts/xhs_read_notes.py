#!/usr/bin/env python3
"""Read 小红书 search results and note bodies through a logged-in browser session.

Why this exists: search-card hrefs are bare /explore/<id> and open the site error
page without the xsec_token that lives only inside the live search page. So this
does not rebuild URLs -- it clicks each card and reads the rendered note container.

Usage:
    python3 xhs_read_notes.py --keyword "GLP-1 营养师" --out ./xhs
    python3 xhs_read_notes.py --keyword "减肥针 营养包" --needles "营养包,订阅" --out ./xhs

Requires: opencli on PATH and a logged-in 小红书 session (the search page may still
show a QR gate -- open it with --window foreground and have the user scan first).
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time
import urllib.parse

SEARCH = "https://www.xiaohongshu.com/search_result?keyword={kw}&source=web_explore_feed"

CARDS_JS = r"""(() => {
  const out = [];
  for (const s of document.querySelectorAll('section')) {
    const a = s.querySelector('a[href*="/explore/"]');
    if (!a) continue;
    const lines = (s.innerText || '').split('\n').map(t => t.trim()).filter(Boolean);
    out.push({title: lines[0] || '', tail: lines.slice(1, 6)});
  }
  return out.slice(0, 30);
})()"""

NOTE_JS = r"""(() => {
  const box = document.querySelector('#noteContainer, .note-container, .note-content');
  const text = (box || document.body).innerText.replace(/\n{2,}/g, '\n').slice(0, 3000);
  return {url: location.href.split('&')[0], title: document.title, text};
})()"""


def run(args, timeout=45):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def parse(raw):
    """opencli prints one JSON envelope, sometimes after log noise."""
    start = raw.rfind('{"ok"')
    if start < 0:
        return {}
    try:
        return json.loads(raw[start:raw.rfind('}') + 1])
    except ValueError:
        return {}


def js(session, expr):
    return parse(run(['opencli', 'browser', 'eval', '--session', session, expr]).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keyword', required=True)
    ap.add_argument('--session', default='xhs')
    ap.add_argument('--out', default='./xhs_notes')
    ap.add_argument('--needles', default='',
                    help='comma-separated title fragments; default = first N card titles')
    ap.add_argument('--limit', type=int, default=8)
    ap.add_argument('--window', default='background', choices=['background', 'foreground'])
    a = ap.parse_args()

    out = pathlib.Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    url = SEARCH.format(kw=urllib.parse.quote(a.keyword))
    run(['opencli', 'browser', 'open', url, '--session', a.session, '--window', a.window])
    run(['opencli', 'browser', 'wait', 'time', '2.5', '--session', a.session])

    cards = (js(a.session, CARDS_JS).get('data') or [])
    if not cards:
        print('NO CARDS - the page is probably showing a login gate; open it with'
              ' --window foreground and have the user scan, then re-run.', file=sys.stderr)
        return 1
    (out / 'cards.json').write_text(json.dumps(cards, ensure_ascii=False, indent=2))
    print(f'{len(cards)} cards')
    for c in cards:
        print(' *', c['title'][:70])

    needles = [n.strip() for n in a.needles.split(',') if n.strip()]
    if not needles:
        needles = [c['title'] for c in cards[:a.limit] if len(c['title']) >= 4]

    saved = 0
    for i, needle in enumerate(needles):
        frag = needle[:14]
        clicked = parse(run(['opencli', 'browser', 'click', '--session', a.session,
                             '--text', frag]).stdout)
        if not (clicked.get('data') or {}).get('clicked'):
            print(f'MISS {frag}', file=sys.stderr)
            continue
        time.sleep(2.0)
        body = js(a.session, NOTE_JS)
        text = (body.get('data') or {}).get('text') or ''
        if len(text) < 80:
            print(f'EMPTY {frag}', file=sys.stderr)
        else:
            (out / f'note_{i:02d}.json').write_text(
                json.dumps(body, ensure_ascii=False, indent=2))
            saved += 1
            print(f'  [{i:02d}] {frag} -> {len(text)} chars')
        run(['opencli', 'browser', 'keys', 'Escape', '--session', a.session])
        time.sleep(0.8)

    print(f'saved {saved}/{len(needles)} bodies to {out}')
    return 0 if saved else 1


if __name__ == '__main__':
    sys.exit(main())
