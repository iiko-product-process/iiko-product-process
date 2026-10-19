#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the «Примерные паттерны поведения» example plates on the recommendation pages.

Why this exists: the plates are the third container for DS markup on those pages, and each
new container silently loses the page framework's fixes. Two defects cost real time here:

  INVISIBLE  a text leaf whose computed `background-color` is opaque AND equal to its own
             `color`. The DS autogen writes `background: <text token>` on ~23 classes
             (`.ds-list-item__text`, `.ds-menu-item__label-up`, `.ds-dialog-header__description`,
             `.ds-text-ui__label-up`, `.ds-sidenav-item__l3`, ...), so the text draws as a
             solid black/grey rectangle. `.panel`, `.phone` and `.pat__panel` neutralise it
             in build.py; any other wrapper does not get the fix.
  OVERFLOW   an example whose inner box is wider than its plate — the DS fixes some widths in
             px (dialog 500, single-line snackbar 370) while the example body is 343.
  NO-EXAMPLE patterns missing `example_html` / `example_ru` (data mode).

Usage (from anywhere):

    python example-plates-audit.py                     # data only, no browser
    python example-plates-audit.py --chrome            # render every page and tab
    python example-plates-audit.py --chrome --slug button --slug list
    python example-plates-audit.py --root D:\\DS --chrome

The --chrome mode needs the pages served on 127.0.0.1:8899 (`python serve.py 8899` from the
repo root, which is the project's usual setup) plus Google Chrome. It writes a short-lived
wrapper HTML into the repo root so its iframes stay same-origin with the pages, and removes
it in a `finally`. Exit code is 1 when anything is reported, 0 otherwise.
"""

import argparse
import glob
import html as html_mod
import json
import os
import re
import subprocess
import sys
import tempfile

DEFAULT_ROOT = r"C:\Users\asukharev\GitHub\DS"
PORT = 8899
PAGES = "iiko-ds-mobile/prototypes/recommendations"
CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# The card heading the plates live in; passed into JS as a JSON string so the file stays
# plain ASCII (Cyrillic piped through a shell/CLI has bitten this project before).
NEEDLE = "паттерны"

WRAPPER = "_example-plates-probe.html"

PROBE_JS = r"""
const SLUGS = %(slugs)s, NEEDLE = %(needle)s, OUT = [];
let i = 0;
function next() {
  if (i >= SLUGS.length) { document.getElementById('out').textContent = OUT.join('\n'); return; }
  const slug = SLUGS[i++];
  const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1200px;border:0;position:absolute;left:-99999px';
  f.src = '/%(pages)s/' + slug + '.html';
  f.onload = () => setTimeout(() => {
    try {
      const d = f.contentDocument, w = f.contentWindow;
      const card = [...d.querySelectorAll('.card')].find(
        x => x.querySelector('h2') && x.querySelector('h2').textContent.includes(NEEDLE));
      if (!card) { OUT.push(slug + ' | NO-BLOCK'); }
      else {
        const plates = [...card.querySelectorAll('.pat__panel .pat__ex')];
        plates.forEach((plate, pi) => {
          const inner = plate.querySelector('.ex__inner') || plate;
          const over = Math.round(inner.scrollWidth) - Math.round(inner.clientWidth);
          if (over > 2) OUT.push(slug + ' | tab ' + (pi + 1) + ' | OVERFLOW ' + over + 'px');
          [...plate.querySelectorAll('*')].forEach(n => {
            const t = (n.textContent || '').trim();
            if (!t || n.children.length) return;
            const s = w.getComputedStyle(n);
            const bg = s.backgroundColor, col = s.color;
            const opaque = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
            if (opaque && bg === col)
              OUT.push(slug + ' | tab ' + (pi + 1) + ' | INVISIBLE ' + n.className +
                       ' | \u00ab' + t.slice(0, 24) + '\u00bb | bg=color=' + bg);
          });
        });
        const tallest = plates.reduce((m, p) => Math.max(m, Math.round(p.getBoundingClientRect().height)), 0);
        OUT.push(slug + ' | plates ' + plates.length + ' | tallest ' + tallest + 'px');
      }
    } catch (e) { OUT.push(SLUGS[i - 1] + ' | ERROR ' + e.message); }
    f.remove();
    next();
  }, 320);
  document.body.appendChild(f);
}
next();
"""


def read_data(root, only=None):
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "_audit", "rec", "data", "*.json"))):
        slug = os.path.basename(path)[:-5]
        if only and slug not in only:
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        pats = data.get("patterns_ru") or []
        rows.append({
            "slug": slug,
            "patterns": len(pats),
            "examples": sum(1 for p in pats if p.get("example_html")),
            "captions": sum(1 for p in pats if p.get("example_ru")),
            "sources": sum(1 for p in pats if p.get("src")),
        })
    return rows


def data_report(rows):
    problems = []
    print("%-18s %8s %8s %8s %7s" % ("component", "patterns", "examples", "captions", "src"))
    for r in rows:
        print("%-18s %8d %8d %8d %7d" % (r["slug"], r["patterns"], r["examples"], r["captions"], r["sources"]))
        if not 3 <= r["patterns"] <= 6:
            problems.append("%s | patterns %d (need 3-6)" % (r["slug"], r["patterns"]))
        if r["examples"] != r["patterns"]:
            problems.append("%s | %d examples for %d patterns" % (r["slug"], r["examples"], r["patterns"]))
        if r["captions"] != r["patterns"]:
            problems.append("%s | %d captions for %d patterns" % (r["slug"], r["captions"], r["patterns"]))
        if r["sources"] != r["patterns"]:
            problems.append("%s | %d sources for %d patterns" % (r["slug"], r["sources"], r["patterns"]))
    return problems


def chrome_path():
    for c in CHROME:
        if os.path.exists(c):
            return c
    for c in ("google-chrome", "chromium", "chrome"):
        try:
            subprocess.run([c, "--version"], capture_output=True, timeout=20)
            return c
        except Exception:
            continue
    return None


def chrome_report(root, rows, budget_pad=20000):
    chrome = chrome_path()
    if not chrome:
        return ["Chrome not found — pass --chrome only where it is installed"], []
    slugs = [r["slug"] for r in rows]
    wrapper = os.path.join(root, WRAPPER)
    body = ("<!doctype html><meta charset=\"utf-8\"><body><pre id=\"out\">pending</pre>\n<script>"
            + PROBE_JS % {"slugs": json.dumps(slugs), "needle": json.dumps(NEEDLE), "pages": PAGES}
            + "</script></body>")
    budget = budget_pad + 3000 * len(slugs)
    tmp = tempfile.mkdtemp(prefix="plates_probe_")
    try:
        with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        out = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--user-data-dir=" + tmp, "--virtual-time-budget=%d" % budget,
             "--dump-dom", "http://127.0.0.1:%d/%s" % (PORT, WRAPPER)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120 + 3 * len(slugs),
        ).stdout
    finally:
        if os.path.exists(wrapper):
            os.remove(wrapper)          # keep the repo root clean
    m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
    if not m:
        return ["probe produced no output — is the page server running on %d?" % PORT], []
    lines = [html_mod.unescape(x).strip() for x in m.group(1).split("\n") if x.strip()]
    problems = [l for l in lines if "INVISIBLE" in l or "OVERFLOW" in l or "ERROR" in l or "NO-BLOCK" in l]
    return problems, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--chrome", action="store_true", help="render the pages (headless Chrome)")
    ap.add_argument("--slug", action="append", default=None, help="limit to these components")
    a = ap.parse_args()

    rows = read_data(a.root, set(a.slug) if a.slug else None)
    if not rows:
        print("no data found under %s — pass --root" % a.root)
        return 1
    problems = data_report(rows)
    if a.chrome:
        print("\n-- rendered checks --")
        chrome_problems, lines = chrome_report(a.root, rows)
        for line in lines:
            print("   ", line)
        problems += chrome_problems

    print("\ncomponents: %d | problems: %d" % (len(rows), len(problems)))
    for p in problems:
        print("   ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
