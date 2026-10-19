#!/usr/bin/env python3
"""Check that a component's CSS is really loaded and its mobile values apply.

Why this exists
---------------
On 12.09.2026 a mobile rule (min-height: 48px for .ds-checkbox) measured 48 px in
one example and 19 px in another. The rule was fine, the cache was fine: the
aggregator iiko-ds-web/components/index.css never imported the component's own CSS,
so .ds-checkbox stayed display:inline - and min-height does not apply to
non-replaced inline elements (it does apply once the element is a flex item).

What it does
------------
1. --component <Folder_DS>: lists the CSS files of that folder, which of them
   iiko-ds-web/components/index.css imports, and which are missing.
2. --url <page>: renders the page in headless Chrome with a FRESH profile (no
   cache) and reports, per [data-mode] panel, for every match of --selector: the
   measured size, the computed display, the marker size (--marker) and a resolved
   token (--token).

The probe page is written NEXT TO the original file (so relative CSS links keep
resolving) and deleted afterwards. Copying a page into a temp dir breaks its CSS
links and silently measures an unstyled page.

--harness <markup.html> is the other half: it renders a markup fragment TWICE
(desktop block + mobile block) on a page in the DS root that links BOTH mobile
layers - iiko-ds-mobile/modes.css AND iiko-ds-mobile/components/index.css. Use it
instead of hand-rolling a test page: a harness that links only modes.css loses
every *-mobile.css / *-touch.css silently and prints desktop numbers, and swapping
the markup between the before/after runs fakes a regression.

  # 1) put the element markup in /tmp/checkbox.html, then compare the two panels:
  python verify-mobile-values.py --harness /tmp/checkbox.html \
      --selector .ds-checkbox --marker .ds-checkbox__box --token --ds-space-2x
  # 2) regression against the previous CSS: same --harness file, old vs new file,
  #    markup untouched (copy the file twice if needed - never edit it between runs).

Exit code 1 when a component file is missing from the aggregator, or when every
panel shows the same sizes - so this can be used as a gate.

Examples (run from the DS root)
-------------------------------
  python verify-mobile-values.py --component Checkbox_DS \
      --url iiko-ds-mobile/prototypes/recommendations/checkbox.html \
      --selector .ds-checkbox --marker .ds-checkbox__box

  python verify-mobile-values.py --url http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/button.html \
      --selector .ds-btn --token --ds-button-m-size-pad-top
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_DS_ROOT = r"C:\Users\asukharev\GitHub\DS"


def find_chrome():
    env = os.environ.get("CHROME")
    if env and os.path.exists(env):
        return env
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ("google-chrome", "chromium", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def check_component(ds_root, component):
    folder = os.path.join(ds_root, "iiko-ds-web", "components", component)
    agg = os.path.join(ds_root, "iiko-ds-web", "components", "index.css")
    if not os.path.isdir(folder):
        return None
    files = sorted(f for f in os.listdir(folder) if f.endswith(".css"))
    text = ""
    if os.path.exists(agg):
        with open(agg, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    imported = [f for f in files if "%s/%s" % (component, f) in text]
    missing = [f for f in files if f not in imported]
    return files, imported, missing


def build_probe(selector, marker, token):
    js = [
        "<script>window.addEventListener('load',function(){var out=[];",
        "document.querySelectorAll(" + json.dumps(selector) + ").forEach(function(e){",
        "var panel=e.closest('[data-mode]');",
        "var mode=panel?panel.getAttribute('data-mode')"
        ":(document.documentElement.getAttribute('data-mode')||'none');",
        "var r=e.getBoundingClientRect(), cs=getComputedStyle(e);",
        "var row={mode:mode,size:Math.round(r.width)+'x'+Math.round(r.height)"
        ",display:cs.display,cls:(e.className||'').slice(0,70)};",
    ]
    if marker:
        js.append(
            "var mk=e.querySelector(" + json.dumps(marker) + ");if(mk){"
            "var mr=mk.getBoundingClientRect();"
            "row.marker=Math.round(mr.width)+'x'+Math.round(mr.height);}"
        )
    if token:
        js.append(
            "row.token=getComputedStyle(panel||e).getPropertyValue("
            + json.dumps(token) + ").trim();"
        )
    js.append("out.push(row);});document.title='MEASURE '+JSON.stringify(out);});</script>")
    return "".join(js)


def resolve_target(url, ds_root):
    """Return (local_path, page_url_for_chrome)."""
    m = re.match(r"^https?://[^/]+/(.*)$", url)
    if m:
        rel = m.group(1).replace("/", os.sep)
        local = os.path.join(ds_root, rel)
        return local, url
    local = url if os.path.isabs(url) else os.path.join(ds_root, url)
    return local, "file:///" + local.replace("\\", "/")


def measure(chrome, page_url, probe_html, selector, marker=None, token=None,
            width=1600, height=1400, budget=8000):
    profile = tempfile.mkdtemp(prefix="udd_verify_")
    try:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--user-data-dir=" + profile,
            "--virtual-time-budget=%d" % budget,
            "--window-size=%d,%d" % (width, height), "--dump-dom",
            page_url + (("?v=%d" % int(time.time())) if page_url.startswith("http") else ""),
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=180)
        dom = proc.stdout.decode("utf-8", "replace")
        m = re.search(r"<title>MEASURE (.*?)</title>", dom, re.S)
        if not m:
            return None
        return json.loads(m.group(1))
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def print_rows(rows, selector):
    """Print per-mode measurements; return 1 when every panel shows the same sizes."""
    print("\nmeasured %d element(s) for %s" % (len(rows), selector))
    by_mode = {}
    for row in rows:
        by_mode.setdefault(row.get("mode"), []).append(row)
    for mode, items in sorted(by_mode.items()):
        print("  [%s]" % mode)
        seen = []
        for it in items:
            line = "    %-11s display=%-12s %s" % (it.get("size", "?"), it.get("display", "?"), it.get("cls", ""))
            if "marker" in it:
                line += "  marker=%s" % it["marker"]
            if "token" in it:
                line += "  token=%s" % (it["token"] or "(empty)")
            if line in seen:
                continue
            seen.append(line)
            print(line)
    sizes = {m: sorted({i.get("size") for i in v}) for m, v in by_mode.items()}
    if len(by_mode) > 1:
        same = len({tuple(v) for v in sizes.values()}) == 1
        if same:
            print("\n! every panel shows the same sizes: %s" % json.dumps(sizes))
            print("  check in this order: (1) component CSS imported by the aggregator,")
            print("  (2) display of the element (inline ignores min-height/height),")
            print("  (3) token really overridden in modes.css, (4) browser cache,")
            print("  (5) box-sizing (content-box adds padding + border on top of height).")
            return 1
        print("\nmode differs across panels: %s" % json.dumps(sizes))
    return 0


def harness_page(ds_root, body, selector, marker=None, token=None):
    """Write a page that renders the SAME markup twice, in both mobile layers.

    Two traps this exists to avoid, both hit for real on 12.09.2026:
      * a harness that links only modes.css (tokens) and forgets
        iiko-ds-mobile/components/index.css silently loses every *-mobile.css /
        *-touch.css file and measures desktop numbers;
      * changing the markup between the before/after runs fakes a regression.
    The page is written in the DS ROOT so the relative CSS links resolve.
    """
    layers = (
        '<link rel="stylesheet" href="iiko-ds-web/font.css">'
        '<link rel="stylesheet" href="iiko-ds-web/tokens.css">'
        '<link rel="stylesheet" href="iiko-ds-mobile/modes.css">'
        '<link rel="stylesheet" href="iiko-ds-mobile/components/index.css">'
        '<link rel="stylesheet" href="iiko-ds-web/styles.css">'
        '<link rel="stylesheet" href="iiko-ds-web/components/index.css">'
    )
    html = (
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">' + layers +
        '<style>body{margin:0;padding:16px;font-family:Roboto,Arial}'
        '[data-mode="mobile"]{background:#f7f8fa}</style></head><body>'
        '<div data-mode="desktop">' + body + '</div>'
        '<div data-mode="mobile">' + body + '</div>'
        + build_probe(selector, marker, token) + '</body></html>'
    )
    page = os.path.join(ds_root, "_probe_harness_%d.html" % int(time.time()))
    with open(page, "w", encoding="utf-8") as fh:
        fh.write(html)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ds-root", default=os.environ.get("DS_ROOT", DEFAULT_DS_ROOT))
    ap.add_argument("--component", help="component folder, e.g. Checkbox_DS")
    ap.add_argument("--url", help="page path (relative to DS root, absolute, or http URL)")
    ap.add_argument("--harness", help="markup fragment: rendered twice (desktop + mobile) on a page that links BOTH mobile layers")
    ap.add_argument("--selector", default=".ds-checkbox", help="CSS selector to measure")
    ap.add_argument("--marker", help="inner selector whose size is the marker/box")
    ap.add_argument("--token", help="custom property to resolve, e.g. --ds-button-m-size-pad-top")
    args = ap.parse_args()

    rc = 0

    if args.component:
        res = check_component(args.ds_root, args.component)
        if res is None:
            print("! folder not found: iiko-ds-web/components/%s" % args.component)
            rc = 1
        else:
            files, imported, missing = res
            print("component: %s" % args.component)
            print("  files    : %s" % (", ".join(files) or "-"))
            print("  imported : %s" % (", ".join(imported) or "NONE"))
            if missing:
                print("  MISSING  : %s" % ", ".join(missing))
                print("  -> add to iiko-ds-web/components/index.css, otherwise the")
                print("     control renders unstyled and min-height/height are ignored")
                rc = 1

    if args.harness:
        chrome = find_chrome()
        if not chrome:
            print("! chrome not found - set CHROME=/path/to/chrome")
            return 1
        frag = args.harness if os.path.isabs(args.harness) else os.path.join(args.ds_root, args.harness)
        if not os.path.exists(frag):
            print("! markup file not found: %s" % frag)
            return 1
        with open(frag, encoding="utf-8", errors="replace") as fh:
            body = fh.read()
        page = harness_page(args.ds_root, body, args.selector, args.marker, args.token)
        try:
            rows = measure(chrome, "file:///" + page.replace("\\", "/"), None,
                           args.selector, args.marker, args.token)
        finally:
            try:
                os.remove(page)
            except OSError:
                pass
        if rows is None:
            print("! no measurements - selector not found in the markup file")
            return 1
        rc = print_rows(rows, args.selector) or rc

    if args.url:
        chrome = find_chrome()
        if not chrome:
            print("! chrome not found - set CHROME=/path/to/chrome")
            return 1
        local, page_url = resolve_target(args.url, args.ds_root)
        if not os.path.exists(local):
            print("! page not found: %s" % local)
            return 1
        probe = os.path.join(os.path.dirname(local),
                             "_probe_verify_%d.html" % int(time.time()))
        with open(local, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write(src.replace("</body>", build_probe(args.selector, args.marker, args.token) + "</body>"))
        probe_url = page_url.replace(os.path.basename(local), os.path.basename(probe))
        try:
            rows = measure(chrome, probe_url, probe, args.selector, args.marker, args.token)
        finally:
            try:
                os.remove(probe)
            except OSError:
                pass
        if rows is None:
            print("! no measurements - selector not found or page did not finish loading")
            return 1
        rc = print_rows(rows, args.selector) or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
