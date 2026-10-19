#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка блока «На экране»: три экрана, главный компонент на каждом, ничего не сломано.

Для каждой страницы рекомендаций, по каждому из трёх экранов в корпусе телефона:

  COUNT      экранов в блоке не три;
  NOCOMP     на экране нет ни одного класса главного компонента страницы
             (классы берём из CSS самого компонента: components/<ds_page>/*.css);
  DUP        экраны повторяют друг друга (одинаковая разметка) — владелец просил
             три разных экрана, «чем разнообразнее тем лучше»;
  OVERFLOW   элемент вылезает за границы экрана телефона;
  CLIPPED    у текстового элемента содержимое срезано (scroll > client);
  EMPTY      экран почти пустой: меньше 6 видимых элементов или занято < 35 % высоты.

Ловушка: getBoundingClientRect отдаёт layout-бокс даже у обрезанного ребёнка.
Поэтому элемент пропускается, если его обрезает контейнер ВНУТРИ экрана
(overflow: auto|scroll — прокрутка; overflow: hidden — если он целиком в его боксе),
и НЕ пропускается вылезание за сам .phone__screen (без этого правила
прокручиваемые табы и чипы дают ложные, а настоящее вылезание смазывается).

Запуск: python audit-preview.py [slug ...]   (без аргументов — все страницы)
Требует запущенного serve.py 8899 (страницы отдаются по http, iframe — same-origin).
"""
import glob
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DS = r"C:\Users\asukharev\GitHub\DS"
REC = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
DATA = os.path.join(DS, "_audit", "rec", "data")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"


def component_classes(ds_page):
    """Классы, объявленные в CSS самого компонента (и в его мобильном слое)."""
    out = set()
    for root in (os.path.join(DS, "iiko-ds-web", "components", ds_page),
                 os.path.join(DS, "iiko-ds-mobile", "components", ds_page)):
        for p in glob.glob(os.path.join(root, "*.css")):
            s = open(p, encoding="utf-8", errors="replace").read()
            out |= set(re.findall(r"\.(ds-[a-z0-9_-]+)", s))
    return sorted(out)


JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const CASES = %(cases)s, OUT = []; let i = 0;
function flush(){ document.getElementById('out').textContent = OUT.join('\n'); }
function vis(el, win){ const c = win.getComputedStyle(el);
  return c.display !== 'none' && c.visibility !== 'hidden' && c.opacity !== '0'; }
function scanScreen(doc, win, page, n, cls){
  const box = doc.querySelectorAll('.phones__item')[n];
  const inner = box.querySelector('.phone__screen');
  const r = inner.getBoundingClientRect();
  const all = [...inner.querySelectorAll('*')];
  const shown = all.filter(el => vis(el, win) && el.getBoundingClientRect().height > 0);
  const own = cls.filter(c => inner.querySelector('.' + c));
  if (!own.length) OUT.push('NOCOMP | ' + page + ' | экран ' + (n + 1) + ' | ни одного класса компонента');
  let filled = 0;
  shown.forEach(el => { const b = el.getBoundingClientRect();
    filled = Math.max(filled, b.bottom - r.top); });
  if (shown.length < 6 || filled < r.height * 0.35)
    OUT.push('EMPTY | ' + page + ' | экран ' + (n + 1) + ' | элементов ' + shown.length
             + ', занято ' + Math.round(filled) + ' из ' + Math.round(r.height));
  /* Переполнение не дефект, если элемент обрезает контейнер внутри экрана:
     прокручиваемые полосы (табы, чипы), шторки и корпуса с overflow: hidden.
     Сам экран в этот список не входит — вылезать за него нельзя. */
  const clippedByInner = el => {
    const b = el.getBoundingClientRect();
    for (let n = el.parentElement; n && n !== inner; n = n.parentElement){
      const c = win.getComputedStyle(n);
      if (/auto|scroll/.test(c.overflowX + c.overflowY)) return true;
      if (/hidden/.test(c.overflowX + c.overflowY)) {
        const cb = n.getBoundingClientRect();
        if (b.right <= cb.right + 1 && b.bottom <= cb.bottom + 1) return true;
      }
    }
    return false;
  };
  shown.forEach(el => {
    const b = el.getBoundingClientRect();
    if (!clippedByInner(el) && (b.right > r.right + 1 || b.bottom > r.bottom + 1 || b.left < r.left - 1))
      OUT.push('OVERFLOW | ' + page + ' | экран ' + (n + 1) + ' | '
               + (el.className || el.tagName).toString().slice(0, 40)
               + ' | правый край ' + Math.round(b.right - r.left) + ' из ' + Math.round(r.width));
    if (el.children.length === 0 && el.textContent.trim() && el.clientHeight > 0
        && (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1))
      OUT.push('CLIPPED | ' + page + ' | экран ' + (n + 1) + ' | '
               + (el.className || el.tagName).toString().slice(0, 40) + ' | '
               + el.textContent.trim().slice(0, 30));
  });
  return inner.innerHTML;
}
function next(){
  if (i >= CASES.length){ flush(); return; }
  const c = CASES[i++]; const page = c[0], cls = c[1];
  const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1400px;border:0';
  f.src = '/iiko-ds-mobile/prototypes/recommendations/' + page + '.html';
  f.onload = () => setTimeout(()=>{
    try {
      const doc = f.contentDocument, win = f.contentWindow;
      const boxes = doc.querySelectorAll('.phones__item');
      if (boxes.length !== 3){ OUT.push('COUNT | ' + page + ' | экранов ' + boxes.length + ' вместо 3'); }
      const htmls = [];
      for (let n = 0; n < boxes.length; n++) htmls.push(scanScreen(doc, win, page, n, cls));
      if (htmls.length === 3 && htmls[0] === htmls[1]) OUT.push('DUP | ' + page + ' | экран 1 и 2 одинаковы');
      if (htmls.length === 3 && htmls[1] === htmls[2]) OUT.push('DUP | ' + page + ' | экран 2 и 3 одинаковы');
      if (htmls.length === 3 && htmls[0] === htmls[2]) OUT.push('DUP | ' + page + ' | экран 1 и 3 одинаковы');
    } catch(e){ OUT.push('ERR | ' + page + ' | ' + e.message); }
    f.remove(); flush(); next();
  }, 350);
  document.body.appendChild(f);
}
next();
</script></body>"""


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    cases = []
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        slug = d["slug"]
        if want and slug not in want:
            continue
        if not d.get("preview_html"):
            continue
        cases.append([slug, component_classes(d["ds_page"])])
    wrapper = os.path.join(REC, "_live_preview.html")
    prof = os.path.join(tempfile.gettempdir(), "udd_prev")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"cases": repr(cases).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=180000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_live_preview.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=400).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    if not m:
        print("WARNING: нет вывода")
        return 2
    lines = [l for l in _html.unescape(m.group(1)).splitlines() if l.strip()]
    print("страниц проверено: %d" % len(cases))
    for k in ("COUNT", "NOCOMP", "DUP", "OVERFLOW", "CLIPPED", "EMPTY", "ERR"):
        found = [l for l in lines if l.startswith(k + " |")]
        print("-- %s: %d" % (k, len(found)))
        for l in found[:300]:
            print("     ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
