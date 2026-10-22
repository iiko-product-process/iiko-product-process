#!/usr/bin/env python3
"""Сверка «оригинал vs копия»: вычисленные стили в headless Chrome.

Задача, под которую написан: экран-прототип скопирован внутрь другой страницы
с переименованием префикса классов (копия живёт на своём префиксе).
Нужно доказать числами, что копия не поехала.

Запуск:
  python verify-copy-styles.py \
      --orig путь/к/оригиналу.html \
      --copy путь/к/странице-с-копией.html \
      --orig-prefix .src- --copy-prefix '#stage .copy-'

Печатает расхождения «узел.свойство | оригинал | копия» и итог.
Код возврата 1, если есть расхождения, кроме ожидаемых (--expect).

Как читать результат: у копии ожидаемо отличаются те узлы, которые ты сознательно
добавил/переставил (напр. сознательно добавленный элемент или другой порядок)
 Такие расхождения перечисляй в отчёте
словами, а не прячь.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

# Узлы экрана: имя → (суффикс селектора, свойства).
DEFAULT_SPEC = {
    'card':      ('card',                 ['width', 'borderRadius', 'backgroundColor', 'display']),
    'header':    ('card__header',         ['padding', 'gap']),
    'row':       ('row',                  ['backgroundColor', 'borderRadius', 'display', 'alignItems']),
    'rowbody':   ('row__body',            ['minHeight', 'padding', 'display']),
    'label':     ('row__label',           ['fontSize', 'lineHeight', 'letterSpacing', 'color']),
    'name':      ('row__name',            ['fontSize', 'fontWeight', 'lineHeight', 'letterSpacing']),
    'act':       ('act',                  ['width', 'height', 'borderRadius', 'backgroundColor', 'color']),
    'num':       ('num',                  ['fontSize', 'fontWeight', 'lineHeight', 'letterSpacing']),
    'timer':     ('timer',                ['fontSize', 'lineHeight']),
    'status':    ('status',               ['height', 'borderRadius', 'fontSize', 'letterSpacing', 'padding', 'textTransform', 'backgroundColor']),
    'topbar':    ('topbar',               ['top', 'left', 'right', 'height', 'gap']),
    'pill':      ('pill',                 ['height', 'padding', 'borderRadius', 'fontSize', 'backgroundColor']),
    'iconbtn':   ('iconbtn',              ['width', 'height', 'borderRadius', 'backgroundColor']),
    'board':     ('board',                ['top', 'left', 'right', 'height', 'gap', 'display']),
    'screen':    ('screen',               ['width', 'height', 'backgroundColor']),
    'devicebody':('device__body',         ['padding', 'borderRadius', 'backgroundColor', 'borderWidth']),
    'footer':    ('footer',               ['height', 'padding', 'fontSize', 'backgroundColor']),
    'transfer':  ('transfer',             ['height', 'margin', 'fontSize', 'lineHeight', 'position']),
    'scrollbar': ('scrollbar',            ['left', 'right', 'bottom', 'height', 'borderRadius', 'backgroundColor']),
    'comment':   ('comment',              ['padding', 'borderStyle', 'borderWidth', 'borderRadius', 'fontSize']),
    'badge':     ('badge',                ['fontSize', 'padding', 'borderRadius', 'backgroundColor']),
    'sub':       ('sub',                  ['minHeight', 'padding', 'fontSize', 'fontWeight']),
}

PROBE = '''<pre id="probe"></pre>
<script>
window.addEventListener('load', function(){
  setTimeout(function(){
    var spec = __SPEC__;
    var res = {};
    for (var k in spec){
      var el = document.querySelector(spec[k].sel);
      if (!el){ res[k] = 'НЕТ ЭЛЕМЕНТА ' + spec[k].sel; continue; }
      var c = getComputedStyle(el), o = {};
      for (var i = 0; i < spec[k].props.length; i++) o[spec[k].props[i]] = c[spec[k].props[i]];
      res[k] = o;
    }
    document.getElementById('probe').textContent = 'JSON' + JSON.stringify(res) + 'JSON';
  }, 300);
});
</script>
'''


def build_probe(page, prefix, spec, out_path):
    html = open(page, encoding='utf-8').read()
    full = {k: {'sel': prefix + spec[k][0], 'props': spec[k][1]} for k in spec}
    js = PROBE.replace('__SPEC__', json.dumps(full, ensure_ascii=False))
    assert '</body>' in html, 'в файле нет </body>: ' + page
    open(out_path, 'w', encoding='utf-8').write(html.replace('</body>', js + '</body>', 1))


def dump(chrome, probe_path, window, tmpdir, tag):
    profile = os.path.join(tmpdir, 'prof-' + tag)
    cmd = [chrome, '--headless', '--disable-gpu', '--no-first-run',
           '--user-data-dir=' + profile, '--virtual-time-budget=9000',
           '--window-size=' + window, '--dump-dom',
           'file:///' + os.path.abspath(probe_path).replace('\\', '/')]
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    # ВАЖНО: искать именно содержимое <pre id="probe"> — маркер отчёта встречается
    # и в исходнике вставленного скрипта внутри --dump-dom.
    m = re.search(r'<pre id="probe">(.*?)</pre>', r.stdout, re.S)
    if not m or not m.group(1).strip():
        return None
    m2 = re.search(r'JSON(\{.*\})JSON', m.group(1), re.S)
    return json.loads(m2.group(1)) if m2 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orig', required=True)
    ap.add_argument('--copy', required=True)
    ap.add_argument('--orig-prefix', default='.src-')
    ap.add_argument('--copy-prefix', required=True, help="напр. '#stage .copy-'")
    ap.add_argument('--chrome', default=CHROME)
    ap.add_argument('--window', default='1600,1000')
    ap.add_argument('--expect', default='', help='через запятую: узлы/свойства, расхождения которых ожидаемы')
    a = ap.parse_args()
    expect = [x.strip() for x in a.expect.split(',') if x.strip()]
    with tempfile.TemporaryDirectory() as d:
        build_probe(a.orig, a.orig_prefix, DEFAULT_SPEC, os.path.join(d, 'orig.html'))
        build_probe(a.copy, a.copy_prefix, DEFAULT_SPEC, os.path.join(d, 'copy.html'))
        o = dump(a.chrome, os.path.join(d, 'orig.html'), a.window, d, 'o')
        c = dump(a.chrome, os.path.join(d, 'copy.html'), a.window, d, 'c')
    if not o or not c:
        print('НЕТ ЗАМЕРА (оригинал: %s, копия: %s) — смотри stderr chrome' % (bool(o), bool(c)))
        return 2
    bad = 0
    for node in o:
        if isinstance(o[node], str) or isinstance(c[node], str):
            print('!! %s | %s | %s' % (node, o[node], c[node]))
            bad += 1
            continue
        for prop, val in o[node].items():
            if str(val) != str(c[node][prop]):
                key = '%s.%s' % (node, prop)
                mark = ' (ожидаемо)' if any(e in key for e in expect) else ''
                print('расхождение %s: оригинал %s | копия %s%s' % (key, val, c[node][prop], mark))
                if not mark:
                    bad += 1
    total = sum(len(v) if isinstance(v, dict) else 1 for v in o.values())
    print('итог: расхождений %d из %d свойств' % (bad, total))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
