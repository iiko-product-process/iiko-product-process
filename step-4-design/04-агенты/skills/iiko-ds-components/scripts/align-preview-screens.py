#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«Два экрана — один интерфейс»: второй экран превью := первый.

Зачем
-----
Патчи превью приходят от исполнителей (`out/previews/<slug>.json`), и часть из них
моделировала второй вариант *между* экранами: на первом компонент в теле, на втором
тело заменено текстовыми строками, а компонент уехал в шторку. Владелец это запретил
(2026-09-13): «на 2 экранах мобилы в превью должны быть одинаковые интерфейсы» —
правая мобилка отличается только подписью под экраном и тем, что в неё попадают
правки из колонки «Правка». Проверка страниц это правило несёт как PREV-SAME
в `checks/check-patch.py`; этот скрипт — ремонт и разовая проверка состояния.

Что делает
----------
Второй экран заменяется копией первого, подпись второго — CAP2. Если экраны уже
совпадают, трогается только подпись второго (если она не про «правки»).

Запуск (из любого места; корень репозитория берётся из --root или IIKO_DS_ROOT)
    python scripts/align-preview-screens.py --check
    python scripts/align-preview-screens.py                  # починить out/previews
    python scripts/align-preview-screens.py --data           # починить data/*.json
    python scripts/align-preview-screens.py --data --build   # и пересобрать страницы

Код возврата: 0 — расхождений нет, 1 — есть (или --check что-то нашёл).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

CAP2 = "Тот же экран, с правками из таблицы справа"
ITEM = '<div class="phones__item">'
CAP_RE = re.compile(r'<p class="phone__caption">.*?</p>', re.S)
HEAD = '<p class="phone__caption">'


def caption(html):
    m = CAP_RE.search(html)
    return m.group(0)[len(HEAD):-len('</p>')] if m else ""


def with_caption(html, text):
    if CAP_RE.search(html):
        return CAP_RE.sub(HEAD + text + '</p>', html, count=1)
    return html + HEAD + text + '</p>'


def without_caption(html):
    return CAP_RE.sub("", html)


def split_screens(preview):
    """(префикс, первый экран, второй экран, хвост) либо None.

    Хвост — закрытие обёртки .phones: оно есть только у последней части, и без его
    снятия сравнение экранов не сойдётся никогда.
    """
    marks = [m.start() for m in re.finditer(re.escape(ITEM), preview)]
    if len(marks) != 2:
        return None
    prefix, i1, i2 = preview[:marks[0]], marks[0], marks[1]
    rest = preview[i2:]
    tail = "</div>" if rest.endswith("</div>") else ""
    item2 = rest[:-len(tail)] if tail else rest
    return prefix, preview[i1:i2], item2, tail


def same_interface(a, b):
    return " ".join(without_caption(a).split()) == " ".join(without_caption(b).split())


def normalize(preview):
    """→ (новое превью, что сделано). ValueError, если экранов не два."""
    parts = split_screens(preview)
    if not parts:
        raise ValueError("экранов не два")
    prefix, item1, item2, tail = parts
    if same_interface(item1, item2):
        if "правк" in caption(item2):
            return preview, "уже одинаково"
        return prefix + item1 + with_caption(item2, CAP2) + tail, "подпись второго экрана"
    return prefix + item1 + with_caption(item1, CAP2) + tail, "второй экран скопирован с первого"


def save(path, obj, crlf):
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("IIKO_DS_ROOT", r"C:\Users\asukharev\GitHub\DS"))
    ap.add_argument("--check", action="store_true", help="только отчёт, ничего не писать")
    ap.add_argument("--data", action="store_true", help="править data/*.json, а не out/previews")
    ap.add_argument("--build", action="store_true", help="после правки data запустить apply_out.py --build")
    args = ap.parse_args()

    rec = os.path.join(args.root, "_audit", "rec")
    if args.data:
        files, crlf = sorted(glob.glob(os.path.join(rec, "data", "*.json"))), True
    else:
        files, crlf = sorted(glob.glob(os.path.join(rec, "out", "previews", "*.json"))), False
    if not files:
        print("не найдено файлов в", rec)
        return 2

    problems, fixed = [], []
    for path in files:
        slug = os.path.basename(path)[:-5]
        obj = json.load(open(path, encoding="utf-8"))
        preview = obj.get("preview_html") or ""
        if not preview:
            problems.append((slug, "нет preview_html"))
            continue
        try:
            new_preview, what = normalize(preview)
        except ValueError as e:
            problems.append((slug, str(e)))
            continue
        if new_preview == preview:
            continue
        if args.check:
            problems.append((slug, what))
        else:
            obj["preview_html"] = new_preview
            save(path, obj, crlf)
            fixed.append((slug, what))

    mode = "data" if args.data else "out/previews"
    print("файлов: %d | %s | чинено: %d | расхождений: %d" % (len(files), mode, len(fixed), len(problems)))
    for slug, what in problems[:40]:
        print("   РАЗНОЕ | %s | %s" % (slug, what))
    for slug, what in fixed[:40]:
        print("   чинено | %s | %s" % (slug, what))

    if fixed and args.build:
        subprocess.run([sys.executable, os.path.join(rec, "apply_out.py"), "--build"], cwd=rec)
    return 1 if (problems or (args.check and fixed)) else 0


if __name__ == "__main__":
    sys.exit(main())
