#!/usr/bin/env python3
"""Матричный аудит мобильного слоя iiko DS.

Зачем: после правки мобильного слоя (или отката iiko-ds-web) часть правил перестаёт
применяться молча — в мобильной панели остаются десктопные числа. Глазами это не видно,
а по одному элементу за прогон проверять долго. Скрипт берёт список ожиданий
(page, selector, property, expect[, pseudo]) и на каждой странице рекомендаций
читает в ОБЕИХ панелях реальное computed-значение, печатает таблицу и список СЛОМАНО.

Запуск:
    python audit-mobile-values.py                     # встроенный набор (41 проверка)
    python audit-mobile-values.py --checks my.json    # свой набор
    python audit-mobile-values.py --base-url http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations
    python audit-mobile-values.py --json out.json     # сложить результат

Формат --checks: [{"page": "button", "selector": ".ds-btn--m", "prop": "height",
                   "expect": 44, "pseudo": "::after"}, ...]
  expect — число (сравнение с допуском 0.6 px) или строка (точное совпадение, напр. "auto"/"column").
  pseudo  — необязательно: "::after", "::before" (слой тач-зоны).

Требует: локальный сервер DS без кэша (serve.py в корне DS) и свежий профиль Chrome
на каждый прогон — иначе измеряется старый CSS. Код возврата 1, если есть сломанные проверки.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEFAULT_BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations"
# Копия страницы с драйвером должна лежать рядом с оригиналом — её URL считается
# от base_url. Если положить её в профиль Chrome, сервер отдаст 404 и ВСЕ замеры
# придут пустыми (весь прогон выглядит как «40 проверок сломано»).
ROOT_DS = r"C:\Users\asukharev\GitHub\DS"

# Встроенный набор: то, что на страницах заявлено как мобильное значение.
DEFAULT_CHECKS = [
    ("button", ".ds-btn--m", "height", 44), ("button", ".ds-btn--s", "height", 44),
    ("button", ".ds-btn--xs", "height", 44), ("button", ".ds-btn--m", "min-height", 48, "::after"),
    ("button-icon", ".ds-btn-icon--m", "height", 40), ("button-icon", ".ds-btn-icon--s", "height", 40),
    ("button-icon", ".ds-btn-icon--xs", "height", 40), ("button-icon", ".ds-btn-icon--m", "min-height", 48, "::after"),
    ("button-toggle", ".ds-button-toggle", "height", 52),
    ("button-toggle", ".ds-button-toggle .ds-btn", "height", 44),
    ("slide-toggle", ".ds-slide-toggle__track", "width", 52), ("slide-toggle", ".ds-slide-toggle__track", "height", 32),
    ("slide-toggle", ".ds-slide-toggle", "min-height", 48),
    ("stepper", ".ds-stepper--vertical .ds-step", "min-height", 48),
    ("form-field", ".ds-input--m .ds-input__frame", "height", 56),
    ("checkbox", ".ds-checkbox", "min-height", 48), ("radio", ".ds-radio", "min-height", 48),
    ("textarea", ".ds-textarea__input-frame", "min-height", 104),
    ("input-number", ".ds-input-number__frame", "height", 56),
    ("list", ".ds-list-item", "min-height", 72),
    ("expansion-panel", ".ds-expansion__header", "min-height", 48),
    ("icon-size", ".ds-arrow", "min-height", 48, "::after"),
    ("chips", ".ds-chips", "min-height", 48, "::after"), ("chips", ".ds-chips-group", "overflow-x", "auto"),
    ("chips-input", ".ds-chips-input__frame", "padding-left", 16),
    ("banners", ".ds-banner", "padding-top", 16), ("snackbar", ".ds-snackbar", "min-height", 48),
    ("tabs", ".ds-tab", "height", 48),
    ("select", ".ds-select-item", "min-height", 48), ("select", ".ds-select-form__input-frame", "height", 56),
    ("autocomplete", ".ds-autocomplete-form__input-frame", "height", 56),
    ("datepicker", ".ds-input-datepicker__frame", "height", 56),
    ("timepicker", ".ds-elements-2", "min-height", 48), ("timepicker", ".ds-input-timepicker__frame", "height", 56),
    ("menu", ".ds-menu-item", "min-height", 72),
    ("dialog", ".ds-dialog-view__action", "flex-direction", "column"),
    # Ширину drawer 360 px в панели шириной 375 с паддингом 12 измерить нельзя:
    # max-width:100% подрезает элемент до 349. Проверяем само правило (тянется
    # на всю ширину панели), а не число, которое в этом харнессе недостижимо.
    ("sidenav", ".ds-sidenav-view", "max-width", "100%"),
    ("table", ".ds-table-content-cell", "min-height", 52),
    ("tree", ".ds-tree-item", "min-height", 48),
    ("text-ui", ".ds-text-ui__list-item", "font-size", 16),
]

# JS-драйвер держим ASCII: кириллица в аргументах Chrome на этом хосте ломается.
INJECT = """<script>window.addEventListener('load',function(){var o={},sp=%(spec)s;
document.querySelectorAll('.panel').forEach(function(pan){var m=pan.getAttribute('data-mode'); o[m]=o[m]||{};
sp.forEach(function(p,i){var e=pan.querySelector(p[0]); if(!e){o[m][i]='-';return;}
var cs=getComputedStyle(e,p[2]||null); o[m][i]=cs.getPropertyValue(p[1]).trim();});});
document.title='AUDIT '+JSON.stringify(o);});</script>"""


def as_number(value):
    try:
        return float(str(value).replace("px", "").strip())
    except ValueError:
        return None


def matches(expect, mobile):
    if isinstance(expect, (int, float)):
        got = as_number(mobile)
        return got is not None and abs(got - float(expect)) < 0.6
    return str(mobile) == str(expect)


def measure(page, checks, base_url, profile_dir):
    url = "%s/%s.html?v=%d" % (base_url.rstrip("/"), page, int(time.time()))
    out_dir = os.path.join(ROOT_DS, base_url.replace("http://127.0.0.1:8899/", "").replace("/", os.sep))
    if not os.path.isdir(out_dir):
        out_dir = profile_dir
    tmp_page = os.path.join(out_dir, "_audit_%s.html" % page)
    # spec для драйвера: [селектор, свойство, псевдоэлемент]. Раньше сюда шли
    # c[2],c[3],c[4] — то есть СВОЙСТВО вместо селектора: querySelector('min-height')
    # ничего не находил и все строки печатались прочерками.
    inject = INJECT % {"spec": json.dumps([[c[1], c[2], c[4]] for c in checks])}

    # Страницу берём из уже собранных рекомендаций, добавляя драйвер копией рядом.
    src_path = os.path.join(base_url.replace("http://127.0.0.1:8899/", "").replace("/", os.sep), page + ".html")
    if os.path.exists(src_path):
        body = open(src_path, encoding="utf-8").read().replace("</body>", inject + "</body>")
    else:
        body = "<html><body>%s</body></html>" % inject
    with open(tmp_page, "w", encoding="utf-8") as fh:
        fh.write(body)
    local_url = "%s/_audit_%s.html?v=%d" % (base_url.rstrip("/"), page, int(time.time()))

    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           "--user-data-dir=" + profile_dir, "--virtual-time-budget=6000", "--window-size=1920,1700",
           "--dump-dom", local_url or url]
    proc = subprocess.run(cmd, capture_output=True, timeout=240)
    dom = proc.stdout.decode("utf-8", "replace")
    hit = re.search(r"<title>AUDIT (.*?)</title>", dom, re.S)
    if os.path.exists(tmp_page):
        os.remove(tmp_page)
    return json.loads(hit.group(1)) if hit else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checks")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--json")
    args = ap.parse_args()

    if args.checks:
        raw = json.load(open(args.checks, encoding="utf-8"))
        checks = [(c["page"], c["selector"], c["prop"], c["expect"], c.get("pseudo", "")) for c in raw]
    else:
        checks = [(c[0], c[1], c[2], c[3], c[4] if len(c) > 4 else "") for c in DEFAULT_CHECKS]

    by_page = {}
    for c in checks:
        by_page.setdefault(c[0], []).append(c)

    profile_dir = os.path.join(tempfile.gettempdir(), "udd_audit_%d" % int(time.time()))
    os.makedirs(profile_dir, exist_ok=True)

    rows, broken = [], []
    for page, page_checks in by_page.items():
        data = measure(page, page_checks, args.base_url, profile_dir)
        for idx, (pg, selector, prop, expect, pseudo) in enumerate(page_checks):
            desktop = (data.get("desktop") or {}).get(str(idx), "-")
            mobile = (data.get("mobile") or {}).get(str(idx), "-")
            ok = matches(expect, mobile)
            row = {"page": pg, "element": selector + (" " + pseudo if pseudo else ""), "prop": prop,
                   "expect": expect, "desktop": desktop, "mobile": mobile, "ok": ok}
            rows.append(row)
            if not ok:
                broken.append(row)

    width = 40
    print("%-15s %-*s %-13s %-7s %-10s %-10s %s" % ("page", width, "element", "prop", "expect", "desktop", "mobile", "result"))
    for row in rows:
        print("%-15s %-*s %-13s %-7s %-10s %-10s %s" % (row["page"], width, row["element"][:width], row["prop"],
              row["expect"], row["desktop"], row["mobile"], "OK" if row["ok"] else "BROKEN"))
    print("\nchecks: %d | broken: %d" % (len(rows), len(broken)))
    if broken:
        pages = ", ".join(sorted({b["page"] for b in broken}))
        print("pages with broken values:", pages)
    if args.json:
        json.dump(rows, open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
