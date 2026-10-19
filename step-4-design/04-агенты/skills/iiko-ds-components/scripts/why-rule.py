#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Показывает, какое правило CSS побеждает на элементе мобильной панели.

Для пары slug/селектор/свойство печатает все подходящие правила из таблиц стилей
страницы в порядке специфичности и признак !important — так видно, почему правило
из колонки «Правка» не срабатывает (проигранная специфичность, порядок, inline-стиль)
быстрее, чем гадать про каскад. Работает вместе с why-nochange.py:
сначала он показывает элемент и текст <style id="live">, потом этот — кто перебивает.

Запуск: python why-rule.py     (кейсы правятся в CASES ниже)
Требует запущенного serve.py 8899.
"""
import os
import re
import shutil
import subprocess
import tempfile
import html as _html

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

CASES = [
    ["stepper", ".ds-step", "min-height"],
    ["slide-toggle", ".ds-slide-toggle__track", "transform"],
    ["autocomplete", ".ds-menu-item", "min-height"],
]

JS = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const CASES = %(cases)s, OUT = []; let i = 0;
function flush(){ document.getElementById('out').textContent = OUT.join('\n'); }
function spec(sel){
  const id = (sel.match(/#[\w-]+/g)||[]).length;
  const cl = (sel.match(/\.[\w-]+/g)||[]).length + (sel.match(/\[[^\]]+\]/g)||[]).length
           + (sel.match(/:(?!:)[\w-]+/g)||[]).length;
  const el = (sel.match(/(^|[\s>+~])[a-zA-Z][\w-]*/g)||[]).length;
  return id*100 + cl*10 + el;
}
function next(){
  if (i >= CASES.length){ flush(); return; }
  const [slug, sel, prop] = CASES[i++];
  const f = document.createElement('iframe');
  f.style.cssText = 'width:1600px;height:1200px;border:0';
  f.src = '/iiko-ds-mobile/prototypes/recommendations/' + slug + '.html';
  f.onload = () => setTimeout(() => {
    try {
      const doc = f.contentDocument;
      const el = doc.querySelector('.panel[data-mode="mobile"] ' + sel);
      if (!el){ OUT.push('=== ' + slug + ' | элемент ' + sel + ' НЕ НАЙДЕН'); f.remove(); flush(); next(); return; }
      OUT.push('=== ' + slug + ' | ' + sel + ' | ' + prop
               + ' | вычислено: ' + f.contentWindow.getComputedStyle(el).getPropertyValue(prop));
      const found = [];
      [...doc.styleSheets].forEach(sheet => {
        let rules; try { rules = sheet.cssRules; } catch(e){ return; }
        const walk = list => [...list].forEach(r => {
          if (r.cssRules){ walk(r.cssRules); return; }
          if (!r.selectorText || !r.style || !r.style.getPropertyValue(prop)) return;
          r.selectorText.split(',').forEach(s => {
            s = s.trim();
            let hit = false;
            try { hit = el.matches(s.replace(/::[a-z-]+/g, '')); } catch(e){}
            if (hit) found.push(spec(s) + ' | ' + (r.parentRule ? 'nested ' : '')
                                 + s + ' { ' + r.style.getPropertyValue(prop)
                                 + (r.style.getPropertyPriority(prop) ? ' !important' : '') + ' }');
          });
        });
        walk(rules);
      });
      found.sort();
      found.forEach(x => OUT.push('    ' + x));
      if (!found.length) OUT.push('    (правил со свойством ' + prop + ' нет)');
    } catch(e){ OUT.push('ERR ' + slug + ': ' + e.message); }
    f.remove(); flush(); next();
  }, 320);
  document.body.appendChild(f);
}
next();
</script></body>"""


def main():
    wrapper = r"C:\Users\asukharev\GitHub\DS\iiko-ds-mobile\prototypes\recommendations\_why_rule.html"
    prof = os.path.join(tempfile.gettempdir(), "udd_rule")
    shutil.rmtree(prof, ignore_errors=True)
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS % {"cases": repr(CASES).replace("'", '"')})
    try:
        dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                              "--virtual-time-budget=120000", "--user-data-dir=" + prof,
                              "--dump-dom", BASE + "_why_rule.html"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=300).stdout
    finally:
        os.remove(wrapper)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    print(_html.unescape(m.group(1)) if m else "нет вывода")


if __name__ == "__main__":
    main()
