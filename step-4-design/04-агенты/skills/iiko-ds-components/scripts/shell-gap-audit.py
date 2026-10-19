"""Замер геометрии оболочки recommendations/index.html (headless Chrome).

Что мерит
----------
* высоту документа оболочки и координаты блока «Общее для всех компонентов»;
* отступ от низа фрейма со страницей компонента до этого блока;
* computed `position` карточки блока и её сдвиг при прокрутке страницы (проверка
  на жалобу «блок стал фиксированным / прижат к низу экрана»).

Требования
----------
* сервер запущен в корне DS: `python serve.py 8899`;
* проба кладётся в `_audit/rec/checks/` ВНУТРИ корня DS — иначе её не отдаст serve.py,
  а iframe оболочки окажется чужим origin и метрики из него не прочитать. После прогона
  проба удаляется.

Запуск
------
    python _audit/rec/checks/shell-gap-audit.py badge,logo,divider,autocomplete

Проверено 13.09.2026: `--headless=new --dump-dom --virtual-time-budget=90000`;
переключение компонента — через `contentWindow.location.hash`, потому что смена только
хеша в `src` iframe НЕ вызывает `onload`, прогон повисает и в `<pre id="out">`
остаётся `...` (пустой результат легко принять за «страница пустая»).
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

DS = r"C:\Users\asukharev\GitHub\DS"
PROBE_NAME = "_shell-gap-probe.html"
PROBE_PATH = os.path.join(DS, "_audit", "rec", "checks", PROBE_NAME)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/"
PAGE = "iiko-ds-mobile/prototypes/recommendations/index.html"
PROBE_URL = BASE + "_audit/rec/checks/" + PROBE_NAME

# r""" — сырая строка: иначе \n в JS-литерале join('\n') превратится в реальный перевод
# строки и сломает скрипт пробы.
PROBE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>shell-gap-probe</title>
<style>
html,body{margin:0;background:#fff}
pre{font:15px/20px monospace;margin:10px;white-space:pre-wrap}
#shell{position:fixed;left:-4000px;top:0;width:1920px;height:1080px;border:0}
</style>
</head>
<body>
<pre id="out">...</pre>
<iframe id="shell"></iframe>
<script>
var BASE = '../../../iiko-ds-mobile/prototypes/recommendations/';
var shell = document.getElementById('shell');
var out = document.getElementById('out');
var lines = [];
var SLUGS = ((location.search.match(/slugs=([a-z0-9,-]+)/) || [])[1] || 'badge,logo,divider').split(',');

function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

async function run() {
  await new Promise(function (res) { shell.onload = res; shell.setAttribute('src', BASE + 'index.html'); });
  await wait(3000);
  for (var i = 0; i < SLUGS.length; i++) {
    var slug = SLUGS[i];
    shell.contentWindow.location.hash = slug;   // смена src не даёт onload — только хеш
    await wait(3000);
    var w = shell.contentWindow, d = shell.contentDocument;
    var f = d.getElementById('frame');
    var card = d.querySelector('.kit > div > .card');
    if (!f || !card) { lines.push(slug + ' нет фрейма или блока'); continue; }
    var fr = f.getBoundingClientRect(), cr = card.getBoundingClientRect();
    var cs = w.getComputedStyle(card);
    var before = Math.round(cr.top);
    w.scrollTo(0, 400);
    await wait(200);
    var after = Math.round(card.getBoundingClientRect().top);
    w.scrollTo(0, 0);
    await wait(200);
    lines.push(slug +
      ' frame=' + (f.getAttribute('src') || '').split('?')[0] +
      ' docH=' + d.documentElement.scrollHeight +
      ' до_блока=' + Math.round(cr.top - fr.bottom) +
      ' низ_блока=' + Math.round(cr.bottom + w.scrollY) +
      ' position=' + cs.position +
      ' сдвиг_при_scroll400=' + (before - after));
  }
  out.textContent = lines.join('\n');
}

run().catch(function (e) { out.textContent = 'ERR ' + e.message + '\n' + lines.join('\n'); });
</script>
</body>
</html>
"""


def main():
    slugs = sys.argv[1] if len(sys.argv) > 1 else "badge,logo,divider,autocomplete"
    try:
        urllib.request.urlopen(BASE + PAGE, timeout=5)
    except Exception as exc:  # сервер — предпосылка, а не «сломанный инструмент»
        sys.exit("нет ответа от %s (%s): запусти `python serve.py 8899` в корне DS" % (BASE + PAGE, exc))
    if not os.path.exists(CHROME):
        sys.exit("не нашёл Chrome: %s" % CHROME)

    with open(PROBE_PATH, "w", encoding="utf-8") as fh:
        fh.write(PROBE)
    try:
        prof = os.path.join(tempfile.gettempdir(), "chrome-shell-gap")
        shutil.rmtree(prof, ignore_errors=True)
        proc = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--user-data-dir=" + prof, "--virtual-time-budget=90000",
             "--window-size=1920,1080", "--dump-dom",
             PROBE_URL + "?slugs=" + slugs],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        m = re.search(r'<pre id="out">(.*?)</pre>', proc.stdout, re.S)
        if not m:
            print("не нашёл <pre id=\"out\"> в выводе Chrome; stderr:\n" + (proc.stderr or "")[-800:])
        else:
            text = html.unescape(m.group(1)).strip()
            print(text)
            if text.startswith("..."):
                print("\nВНИМАНИЕ: проба не успела — пустой вывод. Компонент переключается через "
                      "location.hash (не через src), при необходимости подними --virtual-time-budget.")
    finally:
        try:
            os.remove(PROBE_PATH)
        except OSError:
            pass


if __name__ == "__main__":
    main()
