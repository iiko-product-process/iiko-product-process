#!/usr/bin/env python3
"""Headless-проба страницы ДС: числа из iframe → stdout, скриншот отдельным прогоном.

Повторяет ровно те команды, которыми мерились страницы рекомендаций (Windows,
git-bash, сервер `serve.py`/`python -m http.server 8899` на 127.0.0.1:8899),
чтобы не собирать пробу заново каждую сессию.

Почему так, а не одной командой
-------------------------------
* `sed -n '/<pre id="out">/,/<\\/pre>/p'` по потоку `--dump-dom` матчит ещё и исходник
  инлайнового скрипта страницы-пробы и печатает мусор → дамп сохраняем в файл и
  разбираем регуляркой в Python.
* `--screenshot` в одном запуске с `--dump-dom` снимает кадр раньше, чем проба
  досчитает (проверено на кружке тача: на кадре его не было) → скриншот отдельным
  прогоном (режим `--shot`).
* каждый прогон — свежий `--user-data-dir`, иначе Chrome отдаёт закэшированный CSS.

Использование
-------------
    # js-файл содержит тело пробы: она получает A (iframe) и w (его window)
    python probe-page.py --slug button --js-file probe.js
    python probe-page.py --slug button --js-file probe.js --shot result.png
    python probe-page.py --url iiko-ds-mobile/prototypes/button-modes.html --js-file m.js

--js-file — необязателен: без него проба просто печатает базовые числа
(сколько экранов/слотов, ширины кнопок в слотах).

Печатает: путь к странице-пробе, путь к дампу, содержимое <pre id="out">.
Скриншот кладёт в указанный файл (по умолчанию %LOCALAPPDATA%/Temp/ds-probe/shot.png).
"""

import argparse
import os
import re
import subprocess
import tempfile
import time
import uuid

ROOT = "C:/Users/asukharev/GitHub/DS"
CHECKS = os.path.join(ROOT, "_audit/rec/checks")
CHROME = os.environ.get("CHROME", "C:/Program Files/Google/Chrome/Application/chrome.exe")
BASE = "http://127.0.0.1:8899"

DEFAULT_JS = """
var d = A.contentDocument, w = A.contentWindow, L = [];
L.push('экранов: ' + d.querySelectorAll('.phone__screen').length);
var slots = d.querySelectorAll('[data-buttons]');
L.push('слотов кнопок: ' + slots.length);
[].forEach.call(slots, function (s, i) {
  var w0 = Math.round(s.getBoundingClientRect().width);
  var bw = [].map.call(s.querySelectorAll('.ds-btn'), function (b) {
    return Math.round(b.getBoundingClientRect().width * 10) / 10; });
  L.push('  слот ' + i + ' [' + s.getAttribute('data-buttons') + ']: ' + w0 + ' px, кнопки: ' + (bw.join(' + ') || '—'));
});
o.textContent = L.join('\\n');
"""

PAGE = """<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>probe</title>
<style>html,body{margin:0}pre#out{font:12px/17px monospace;margin:8px;white-space:pre-wrap}
iframe{width:1500px;height:%(h)dpx;border:0;display:block}</style></head>
<body><pre id="out">…</pre><iframe id="a" src="%(src)s"></iframe>
<script>
var A = document.getElementById('a'), o = document.getElementById('out');
A.onload = function () { setTimeout(function () {
  try { var w = A.contentWindow; %(js)s } catch (e) { o.textContent += 'ERR ' + e.message; }
}, 2500); };
</script></body></html>
"""


def run_chrome(url, extra, profile):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--user-data-dir=" + profile, "--virtual-time-budget=25000",
           "--window-size=1600,2600"] + extra + [url]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="страница компонента в recommendations/<slug>.html")
    ap.add_argument("--url", help="свой путь от корня DS (вместо --slug)")
    ap.add_argument("--js-file", help="файл с телом пробы (получает A и w)")
    ap.add_argument("--mobile", action="store_true", help="страница в iiko-ds-mobile/")
    ap.add_argument("--shot", nargs="?", const="", help="сделать скриншот отдельным прогоном")
    ap.add_argument("--iframe-height", type=int, default=2200)
    args = ap.parse_args()

    if args.url:
        target = "/" + args.url.lstrip("/")
    else:
        root = "iiko-ds-mobile/prototypes/recommendations" if (args.slug or args.mobile) else "iiko-ds-prototypes"
        target = "/%s/%s.html" % (root, args.slug)
    os.makedirs(CHECKS, exist_ok=True)
    src = "../../../" + target.lstrip("/")
    js = open(args.js_file, encoding="utf-8").read() if args.js_file else DEFAULT_JS
    probe = os.path.join(CHECKS, "_probe-%s.html" % uuid.uuid4().hex[:6])
    open(probe, "w", encoding="utf-8").write(
        PAGE % {"src": src, "js": js, "h": args.iframe_height})
    url = "%s/_audit/rec/checks/%s" % (BASE, os.path.basename(probe))
    print("проба:", url)

    with tempfile.TemporaryDirectory() as prof:
        res = run_chrome(url, ["--dump-dom"], prof)
    dump = os.path.join(tempfile.gettempdir(), "ds-probe-dump.html")
    open(dump, "w", encoding="utf-8", errors="replace").write(res.stdout)
    m = re.search(r'<pre id="out">(.*?)</pre>', res.stdout, re.S)
    print("дамп:", dump)
    print(m.group(1).strip() if m else "<pre id=\"out\"> не найден — проба не досчитала")

    if args.shot is not None:
        shot = args.shot or os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()),
                                         "Temp", "ds-probe", "shot.png")
        os.makedirs(os.path.dirname(shot), exist_ok=True)
        with tempfile.TemporaryDirectory() as prof:
            run_chrome(url, ["--screenshot=" + shot.replace("/", "\\")], prof)
        time.sleep(0.2)
        print("скриншот (отдельный прогон):", shot)
    print("файл пробы оставлен для разбора:", probe)


if __name__ == "__main__":
    main()
