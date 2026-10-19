#!/usr/bin/env python3
"""Замер страницы ДС в headless Chrome: впрыснуть JS-пробу и напечатать её результат.

Зачем: прототипы ДС проверяются числами (getComputedStyle, размеры, состояния после кликов),
а не «на глаз». Скрипт делает временную копию страницы, вставляет <pre id="probe"> и <script>,
прогоняет Chrome с --dump-dom и печатает содержимое #probe.

Использование:
    python probe-headless.py --page C:/p/DS/KDS/multi-shop.html --js probe.js
    python probe-headless.py --page ... --js probe.js --window 1600,1000 --shot block.png
    python probe-headless.py --page ... --js -            # проба из stdin

Проба — обычный JS, который в конце кладёт результат в #probe, например:
    window.addEventListener('load', function(){ setTimeout(function(){
      var out=[]; out.push('k: ' + getComputedStyle(el).backgroundColor);
      document.getElementById('probe').textContent = 'START\\n' + out.join('\\n') + '\\nEND';
    }, 400); });
setTimeout нужен, чтобы успели примениться авто-масштаб и отрисовка страницы.

Важно: --shot снимает состояние ДО кликов из setTimeout (Chrome делает кадр раньше), поэтому
поведение доказывать дампом, а скриншотом — только вид. Для «после нажатий» кликать
синхронным <script> в конце <body>.
"""

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    os.environ.get("CHROME"),
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chrome"),
]


def find_chrome():
    for c in CANDIDATES:
        if c and Path(c).exists():
            return str(c)
    sys.exit("Chrome не найден: задай переменную окружения CHROME")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True, help="html-страница прототипа")
    ap.add_argument("--js", required=True, help="файл с JS-пробой или '-' для stdin")
    ap.add_argument("--window", default="1600,1000")
    ap.add_argument("--budget", type=int, default=9000, help="--virtual-time-budget, мс")
    ap.add_argument("--shot", help="куда сохранить скриншот (вид, не поведение)")
    ap.add_argument("--keep", action="store_true", help="не удалять временную папку")
    a = ap.parse_args()

    js = sys.stdin.read() if a.js == "-" else Path(a.js).read_text(encoding="utf-8")
    page = Path(a.page).read_text(encoding="utf-8")
    if "</body>" not in page:
        sys.exit("в странице нет </body>")
    wrapper = '<pre id="probe"></pre>\n<script>\n' + js + "\n</script>\n"
    probe_page = page.replace("</body>", wrapper + "</body>", 1)

    tmp = tempfile.mkdtemp(prefix="ds-probe-")
    target = Path(tmp) / "probe.html"
    target.write_text(probe_page, encoding="utf-8")

    cmd = [find_chrome(), "--headless", "--disable-gpu", "--no-first-run",
           "--user-data-dir=" + str(Path(tmp) / "prof"),
           "--virtual-time-budget=" + str(a.budget),
           "--window-size=" + a.window]
    if a.shot:
        cmd.append("--screenshot=" + str(Path(a.shot).resolve()))
    cmd += ["--dump-dom", target.as_uri()]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    m = re.search(r'<pre id="probe">(.*?)</pre>', res.stdout or "", re.S)
    if not m:
        print("--dump-dom без #probe; размер вывода:", len(res.stdout or ""))
        print((res.stderr or "")[-800:])
    else:
        text = html.unescape(m.group(1)).strip()
        if not text:
            print("#probe пуст: проба упала или не успела (увеличь --budget, проверь JS)")
            print((res.stderr or "")[-800:])
        else:
            print(text)

    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("временная папка:", tmp)


if __name__ == "__main__":
    main()
