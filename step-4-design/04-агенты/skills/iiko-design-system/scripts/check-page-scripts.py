#!/usr/bin/env python3
"""Проверка, что скрипты собранных страниц вообще исполняются: `node --check` по каждому <script>.

Зачем: в генераторе `_audit/rec/build.py` страница — %-шаблон, и `\\n`, записанный в исходнике
одним слэшем, разворачивается в настоящий перевод строки. Скрипт страницы после этого падает на
синтаксисе ЦЕЛИКОМ и молча: меню паттернов не переключает, плашка описания и строка прогресса пустые,
в консоли ничего. Симптом легко принять за «мой код не подключился» и искать не там.
Проверка занимает секунды и ловит это до того, как страницу увидит владелец.

Запуск:
    python scripts/check-page-scripts.py                       # страницы рекомендаций
    python scripts/check-page-scripts.py <файл.html|папка> …     # любые страницы

Выход: 0 — все скрипты валидны, 1 — есть мёртвый <script> (или не найден node).
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_DIR = "C:/Users/asukharev/GitHub/DS/iiko-ds-mobile/prototypes/recommendations"
SCRIPT_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.S)


def collect(targets):
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(glob.glob(os.path.join(t, "*.html")))
        elif os.path.exists(t):
            files.append(t)
    return files


def check(path, tmpdir):
    with open(path, encoding="utf-8", newline="") as f:
        html = f.read()
    blocks = SCRIPT_RE.findall(html)
    if not blocks:
        return "no-script", ""
    # каждый блок проверяем отдельно: мёртвый <script> не мешает соседним, но именно он и важен
    for i, block in enumerate(blocks):
        js = os.path.join(tmpdir, "%s-%d.js" % (os.path.basename(path).replace(".", "_"), i))
        with open(js, "w", encoding="utf-8", newline="") as f:
            f.write(block)
        r = subprocess.run(["node", "--check", js], capture_output=True, text=True)
        if r.returncode != 0:
            first = [ln for ln in (r.stderr or "").splitlines() if ln.strip()]
            return "fail", "блок %d: %s" % (i, " / ".join(first[:3]))
    return "ok", "%d блок(ов)" % len(blocks)


def main():
    targets = sys.argv[1:] or [DEFAULT_DIR]
    if not shutil.which("node"):
        print("нет node — проверка невозможна (нужен node в PATH)")
        return 1
    files = collect(targets)
    if not files:
        print("не найдено .html в: %s" % ", ".join(targets))
        return 1
    bad = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for path in files:
            status, info = check(path, tmpdir)
            name = os.path.relpath(path, os.path.dirname(DEFAULT_DIR))
            print("%-58s %-10s %s" % (name, status, info))
            if status == "fail":
                bad += 1
    print("\nпроверено страниц: %d · с мёртвым скриптом: %d" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
