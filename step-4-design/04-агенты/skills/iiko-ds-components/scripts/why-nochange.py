#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Разбор полей «Правка», которые ничего не меняют (NOCHANGE).

Копия рабочего скрипта: C:\\Users\\asukharev\\GitHub\\DS\\_audit\\rec\\checks\\why-nochange.py
(менять оба места, если правишь). Требует serve.py на 127.0.0.1:8899.

Для каждой пары slug/поле печатает: найденный элемент (outerHTML, классы, inline-стиль),
вычисленные значения свойств из data-css до и после подстановки, и текст <style id="live"> —
так видно, поле не работает из-за inline-стиля в разметке, из-за короткого селектора или
из-за transition/шорткатов в самой БОНУС-проверке.

Использование: список CASES править под свой разбор (slug, data-id поля, значение).

Запуск: python why-nochange.py
"""
import os
import re
import subprocess
import tempfile
import shutil
import html as _html

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

# slug, data-id поля, значение, которое подставляем (крупное — чтобы эффект был виден)
CASES = [
    ("autocomplete", "min-height", "120"),
    ("stepper", "step-row", "120"),
    ("slide-toggle", "knob-shift", "60"),
]

JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const CASES = %(cases)s;
const OUT = []; let i = 0;
function flush(){ document.getElementById('out').textContent = OUT.join('\n'); }
function next(){
  if (i >= CASES.length){ flush(); return; }
  const [slug, id, val] = CASES[i++];
  const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1200px;border:0';
  f.src = '/iiko-ds-mobile/prototypes/recommendations/' + slug + '.html';
  f.onload = () => setTimeout(() => {
    try {
      const doc = f.contentDocument, win = f.contentWindow;
      const field = doc.querySelector('.edit__input[data-id="' + id + '"]');
      if (!field){ OUT.push('=== ' + slug + ' / ' + id + ': ПОЛЕ НЕ НАЙДЕНО'); f.remove(); flush(); next(); return; }
      const raw = field.getAttribute('data-sel'), css = field.getAttribute('data-css') || '';
      const pseudo = raw.indexOf('::') >= 0 ? raw.slice(raw.indexOf('::')) : '';
      const sel = raw.replace(/::[a-z-]+/, '');
      const ps = css.split(';').map(s => s.split(':')[0].trim()).filter(Boolean);
      const els = [...doc.querySelectorAll('.panel[data-mode="mobile"] ' + sel),
                   ...doc.querySelectorAll('.phone__screen[data-mode="mobile"] ' + sel)];
      OUT.push('=== ' + slug + ' / ' + id + ' | sel ' + raw + ' | css ' + css
               + ' | найдено элементов: ' + els.length);
      const read = () => els.map(el => ps.map(p => win.getComputedStyle(el, pseudo || null).getPropertyValue(p)).join(',')
                                    + ' rect ' + Math.round(el.getBoundingClientRect().height) + 'x'
                                    + Math.round(el.getBoundingClientRect().width)).join(' # ');
      OUT.push('    было:   ' + read());
      els.forEach(el => { if (el.getAttribute('style'))
        OUT.push('    inline:  ' + el.className + ' style=' + el.getAttribute('style')); });
      if (els[0]) OUT.push('    html:    ' + els[0].outerHTML.slice(0, 300).replace(/\s+/g, ' '));
      field.value = val;
      field.dispatchEvent(new win.Event('input', {bubbles: true}));
      OUT.push('    live:    ' + (doc.getElementById('live').textContent || '(пусто)').replace(/\s+/g, ' '));
      OUT.push('    стало:  ' + read());
    } catch (e) { OUT.push('ERR ' + slug + ': ' + e.message); }
    f.remove(); flush(); next();
  }, 320);
  document.body.appendChild(f);
}
next();
</script></body>"""


def main():
    wrapper = r"C:\Users\asukharev\GitHub\DS\iiko-ds-mobile\prototypes\recommendations\_why_nochange.html"
    prof = os.path.join(tempfile.gettempdir(), "udd_why")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"cases": repr([list(c) for c in CASES]).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=120000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_why_nochange.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=300).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    print(_html.unescape(m.group(1)) if m else "нет вывода")


if __name__ == "__main__":
    main()
