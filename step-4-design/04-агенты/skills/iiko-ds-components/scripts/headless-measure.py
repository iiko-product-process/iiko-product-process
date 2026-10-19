#!/usr/bin/env python3
"""Render a local HTML page in headless Chrome and read its own measurements.

Why: pages can measure themselves (getBoundingClientRect / getComputedStyle) and stash
the result in an attribute, e.g.

    document.body.setAttribute('data-measure', JSON.stringify(rows));

so the numbers come from a real engine instead of from reading CSS by eye. Needs no
Chrome remote-debugging approval, unlike an interactive browser tool.

Usage
-----
    python headless-measure.py <page.html|file-url|http-url> [--attr data-measure]
                               [--json out.json] [--screenshot out.png]
                               [--width 1440] [--height 2600]
    python headless-measure.py --diff old.json new.json

`--diff` compares two runs item-wise on the `id` key (falls back to index) and prints only
the changed fields - the honest regression check when refactoring a component's CSS.

Note: extract() deliberately slices the RAW dom up to the next plain quote (inner quotes
are `&quot;`) and unescapes afterwards - unescaping first makes the slice ambiguous.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome",
    "chromium",
    "chrome",
    "msedge",
]


def find_browser(explicit=None):
    if explicit:
        return explicit
    for cand in CHROME_CANDIDATES:
        if os.path.isabs(cand):
            if os.path.exists(cand):
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    sys.exit("no Chrome/Edge binary found - pass --chrome <path>")


def to_url(target):
    if target.startswith(("http://", "https://", "file://")):
        return target
    return "file:///" + os.path.abspath(target).replace("\\", "/")


def render(url, browser, width, height, budget, screenshot=None, extra=()):
    profile = os.path.join(tempfile.gettempdir(), "headless-measure-profile")
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--user-data-dir=" + profile,
           "--virtual-time-budget=%d" % budget, "--window-size=%d,%d" % (width, height)]
    cmd += list(extra)
    if screenshot:
        cmd += ["--screenshot=" + screenshot]
    else:
        cmd.append("--dump-dom")
    cmd.append(url)
    proc = subprocess.run(cmd, capture_output=True, timeout=180)
    return proc.stdout.decode("utf-8", errors="replace")


def extract(dom, attr):
    """Pull JSON out of an HTML attribute, tolerating quotes escaped as &quot;."""
    marker = attr + '="'
    i = dom.find(marker)
    if i < 0:
        sys.exit("attribute %r not found in the rendered DOM" % attr)
    start = i + len(marker)
    end = dom.find('"', start)
    return json.loads(html.unescape(dom[start:end]))


def diff(old, new, key="id"):
    changed = 0
    by_id = {}
    for row in new:
        by_id[row.get(key, str(new.index(row)))] = row
    for i, o in enumerate(old):
        k = o.get(key, str(i))
        n = by_id.get(k)
        if n is None:
            print("removed:", k)
            changed += 1
            continue
        for field in sorted(set(o) | set(n)):
            if o.get(field) != n.get(field):
                print("  %-22s %-14s %r -> %r" % (k, field, o.get(field), n.get(field)))
                changed += 1
    print("changed fields:", changed)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="page path or URL")
    ap.add_argument("--attr", default="data-measure")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--screenshot")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=2600)
    ap.add_argument("--budget", type=int, default=5000)
    ap.add_argument("--chrome")
    ap.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"),
                    help="compare two saved JSON runs instead of rendering")
    args = ap.parse_args()

    if args.diff:
        old = json.load(open(args.diff[0], encoding="utf-8"))
        new = json.load(open(args.diff[1], encoding="utf-8"))
        sys.exit(0 if diff(old, new) == 0 else 1)

    if not args.target:
        sys.exit("give a page path/URL, or use --diff")

    browser = find_browser(args.chrome)
    url = to_url(args.target)
    if args.screenshot:
        render(url, browser, args.width, args.height, args.budget, screenshot=args.screenshot)
        print("screenshot:", args.screenshot)  # then look at it with vision
        return

    rows = extract(render(url, browser, args.width, args.height, args.budget), args.attr)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)
        print("saved:", args.json_out, file=sys.stderr)


if __name__ == "__main__":
    main()
