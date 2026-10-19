#!/usr/bin/env python
"""Проба страницы-прототипа в headless Chrome одной командой.

usage:
    python probe_page.py <source.html> <probe.js> [--name NAME] [--shot out.png] [--size 1700x1200]

Что делает:
  1) собирает копию <source.html> с внедрённым probe.js перед </body>
     -> $LOCALAPPDATA/Temp/p-<NAME>.html  (ВСЕГДА из актуального исходника!)
  2) запускает headless Chrome с --dump-dom (+ --screenshot, если задан) и уникальным профилем
  3) печатает только содержимое <pre id="probe"> из полученного DOM

probe.js — фрагмент, который сам пишет результат в <pre id="probe">:

    <pre id="probe"></pre><script>
    var err=[]; window.addEventListener('error', function(e){ err.push(e.message); });
    window.addEventListener('load', function(){ setTimeout(function(){
      var o=[];
      try{
        /* состояние можно выставлять НАПРЯМУЮ до paint(): переменные прототипа доступны в window
           как глобалы (pressed, timeOn, elapsedMin, uiMode, screenVariant) и работают —
           pressed={warm:['cold']}; timeOn=true; elapsedMin=10; paint();
           клик из пробы иногда не успевает к кадру, поэтому прямой state надёжнее и годится для карточки.
           Видимость вкладки — тоже статикой: перенос класса is-on у [data-vpanel]/[data-vtab].
           Вариант с готовыми --state/--shot: scripts/probe-page.sh; подробности —
           references/kds-prototype-verification.md */
        document.querySelector('[data-vtab="2"]').click();
        var chk=document.querySelector('[data-time-chk]'); if(chk && !chk.checked) chk.click();
        var chip=[].filter.call(document.querySelectorAll('.chip'), function(x){
          return x.textContent.trim()==='20 мин'; })[0];
        if(!chip){ o.push('ЧИП НЕ НАЙДЕН — шаг пропущен, вывод недостоверен'); } else { chip.click(); }
        o.push('класс строки: '+document.querySelector('.kds-row').className);
        o.push('shadow: '+getComputedStyle(document.querySelector('.kds-row')).boxShadow);
        o.push('ошибки JS: '+(err.length? err.join(' | ') : 'нет'));
      }catch(e){ o.push('ОШИБКА: '+e.message); }
      document.getElementById('probe').textContent='START\\n'+o.join('\\n')+'\\nEND';
    }, 600); });
    </script>

Грабли (проверено на практике):
  * уникальный --user-data-dir на каждый запуск, иначе Chrome иногда отдаёт пустой DOM;
  * --virtual-time-budget нужен, чтобы сработал setTimeout внутри пробы;
  * пути для Chrome — только C:/… (MSYS-пути /c/… он не понимает);
  * проба ВСЕГДА собирается заново из актуального файла: старая заготовка даёт ложную картину
    (уже приводило к тому, что владельцу ушёл снимок прошлого состояния);
  * ВСЕГДА печатать в выводе «ошибки JS» (window.onerror) и «переполнение»
    (scrollWidth − clientWidth): без них «всё хорошо» ничего не проверяет;
  * цвета замерять равенством строк — 'совпадает: '+(getComputedStyle(a).color===getComputedStyle(b).color)
    — и В ОБОИХ местах (панели цехов и скопированный экран живут на разных палитрах --kds-*/--kdsx-*).
"""

import argparse
import os
import re
import subprocess
import sys
import html as html_mod

CHROME_CANDIDATES = [
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_chrome():
    env = os.environ.get("CHROME")
    if env and os.path.exists(env):
        return env
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    sys.exit("Chrome не найден: задай переменную CHROME=/путь/к/chrome")


def tmp_dir():
    for key in ("TEMP", "TMP"):
        v = os.environ.get(key)
        if v and os.path.isdir(v):
            return v.replace("\\", "/")
    d = os.path.join(os.environ.get("LOCALAPPDATA", "/tmp"), "Temp")
    return (d if os.path.isdir(d) else "/tmp").replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("probe")
    ap.add_argument("--name", default="probe")
    ap.add_argument("--shot")
    ap.add_argument("--size", default="1700x1200")
    ap.add_argument("--budget", default="9000")
    a = ap.parse_args()

    src = open(a.source, encoding="utf-8").read()
    code = open(a.probe, encoding="utf-8").read()
    if "</body>" not in src:
        sys.exit("в исходнике нет </body> — проба не собрана")
    if 'id="probe"' not in code:
        sys.exit('в probe.js нет <pre id="probe"> — некуда писать результат')

    t = tmp_dir()
    page = f"{t}/p-{a.name}.html"
    open(page, "w", encoding="utf-8").write(src.replace("</body>", code + "</body>", 1))
    print(f"# проба собрана из {a.source} -> {page}", file=sys.stderr)

    w, h = a.size.split("x")
    args = [find_chrome(), "--headless", "--disable-gpu", "--no-first-run",
            f"--user-data-dir={t}/chr-{a.name}-{os.getpid()}",
            f"--virtual-time-budget={a.budget}", f"--window-size={w},{h}"]
    if a.shot:
        args.append(f"--screenshot={a.shot}")
    args += ["--dump-dom", "file:///" + page]
    dom = subprocess.run(args, capture_output=True, text=True, errors="replace").stdout

    m = re.search(r'<pre id="probe">(.*?)</pre>', dom, re.S)
    print(html_mod.unescape(m.group(1).strip()) if m else "нет <pre id=probe> в DOM — проба не отработала")
    if a.shot:
        print(f"# screenshot: {a.shot}", file=sys.stderr)


if __name__ == "__main__":
    main()
