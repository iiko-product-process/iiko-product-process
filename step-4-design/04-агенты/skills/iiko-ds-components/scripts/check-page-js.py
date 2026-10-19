#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка JS сгенерированных страниц рекомендаций.

Зачем: `_audit/rec/build.py` — Python-`%`-шаблон, поэтому `'\n'` внутри JS-строки
попадает в файл реальным переводом строки и скрипт падает с
`SyntaxError: Invalid or unexpected token`. Страница при этом открывается, но
молча ничего не правит (`#live` пустой, колонка «Правка» не работает) — без этой
проверки дефект легко уходит владельцу.

Что делает: для каждого `.html` в папке страниц берёт последний блок `<script>`,
кладёт во временный файл и прогоняет `node --check`.

Запуск:
    python check-page-js.py [папка-страниц]
    (по умолчанию iiko-ds-mobile/prototypes/recommendations в рабочей копии DS)

Код возврата: 0 — все скрипты валидны, 1 — есть сломанные, 2 — нет node.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_DIR = os.path.join(
    "C:", "Users", "asukharev", "GitHub", "DS",
    "iiko-ds-mobile", "prototypes", "recommendations",
)


def last_script(html):
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    return blocks[-1] if blocks else None


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    if not os.path.isdir(folder):
        print("нет папки: %s" % folder)
        return 2
    if not shutil.which("node"):
        print("node не найден в PATH — проверка невозможна (поставь Node.js)")
        return 2

    checked, broken = 0, []
    tmpdir = tempfile.mkdtemp(prefix="page-js-")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8", errors="replace") as fh:
            script = last_script(fh.read())
        if not script or not script.strip():
            continue
        checked += 1
        tmp = os.path.join(tmpdir, name.replace(".", "_") + ".js")
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(script)
        res = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        if res.returncode != 0:
            first = (res.stderr or res.stdout or "").strip().splitlines()
            broken.append((name, first[0] if first else "?",
                           first[1].strip() if len(first) > 1 else ""))

    print("страниц со скриптом: %d, сломано: %d" % (checked, len(broken)))
    for name, line1, line2 in broken:
        print("  %-24s %s %s" % (name, line1, line2))
    if broken:
        print("\nПочинка: в build.py заменить '\\n' внутри JS на String.fromCharCode(10).")
        return 1
    print("все скрипты валидны")
    return 0


if __name__ == "__main__":
    sys.exit(main())
