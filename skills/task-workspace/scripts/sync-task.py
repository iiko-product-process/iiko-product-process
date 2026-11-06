#!/usr/bin/env python3
"""Синхронизация рабочей папки задачи в хранилище артефактов (Hermes wiki).

Рабочая папка (`~/iiko_process/ARTIFACTS/<слаг>`) — временная: там идёт работа.
Источник правды — `ARTIFACTS/<слаг>/` в вики. Скрипт копирует артефакты из рабочей папки
в папку задачи по правилам раскладки, не перезаписывая расхождения молча.

    python3 sync-task.py --from ~/iiko_process/ARTIFACTS/pb-7105-nacenka-v-prikazah \
                         --task <клон>/ARTIFACTS/pb-7105-price-orders --dry-run
    python3 sync-task.py --from … --task … --journal

Коды возврата: 0 — синхронизировано, 2 — есть конфликты (файл уже лежит с другим содержимым),
1 — ошибка входа.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

# Правила раскладки: префикс в рабочей папке → путь внутри папки задачи (вики).
# Порядок важен: длинные префиксы проверяются раньше.
RULES: list[tuple[str, str]] = [
    ("confluence/", "01-проблема/исследования/confluence/"),
    ("prototypes/", "04-дизайн/prototypes/"),
    ("references/", "04-дизайн/references/"),
    ("исследования/", "01-проблема/исследования/"),
    ("ARTIFACTS/", "материалы/ARTIFACTS/"),
    ("материалы/", "материалы/"),
    ("встречи/", "встречи/"),
    ("context.md", "01-проблема/context.md"),
    ("spec.md", "05-спека/spec.md"),
    ("system-spec.md", "05-спека/system-spec.md"),
    ("decisions.md", "05-спека/decisions.md"),
    ("open-questions.md", "03-требования/open-questions.md"),
    ("assumptions.md", "03-требования/assumptions.md"),
    ("code-analysis.md", "06-реализация/code-analysis.md"),
]
CANON_OWNED = {"README.md", "журнал.md"}  # карточка и журнал: правит человек, не синхронизация
FALLBACK = "материалы/"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def target_for(rel: Path) -> tuple[Path, bool]:
    """Возвращает путь назначения и признак «правило не нашлось, положено в материалы»."""
    posix = rel.as_posix()
    for prefix, dest in RULES:
        if posix == prefix.rstrip("/") or posix.startswith(prefix):
            tail = posix[len(prefix):] if prefix.endswith("/") else ""
            return Path(dest) / tail if tail else Path(dest), False
    return Path(FALLBACK) / rel, True


def journal_row(count: int, new: int, folder: str) -> str:
    return (f"| {date.today():%d.%m.%Y} | Синхронизировано из рабочей папки `{folder}`: "
            f"{count} файлов ({new} новых) | — | Hermes |")


def main() -> int:
    ap = argparse.ArgumentParser(description="Синхронизация рабочей папки задачи в папку задачи вики")
    ap.add_argument("--from", dest="src", required=True, help="рабочая папка задачи")
    ap.add_argument("--task", required=True, help="папка задачи в репозитории (ARTIFACTS/<слаг>)")
    ap.add_argument("--dry-run", action="store_true", help="только показать план")
    ap.add_argument("--overwrite", action="store_true", help="перезаписывать расходящиеся файлы")
    ap.add_argument("--journal", action="store_true", help="дописать строку в журнал задачи")
    ap.add_argument("--json", action="store_true", help="план в JSON")
    args = ap.parse_args()

    src, task = Path(args.src).expanduser().resolve(), Path(args.task).expanduser().resolve()
    if not src.is_dir() or not task.is_dir():
        print(f"нет папки: {src if not src.is_dir() else task}", file=sys.stderr)
        return 1

    plan, conflicts, unmapped = [], [], []
    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = path.relative_to(src)
        if rel.as_posix() in CANON_OWNED:
            continue
        dest_rel, is_fallback = target_for(rel)
        dest = task / dest_rel
        status = "new"
        if dest.exists():
            status = "same" if sha256(dest) == sha256(path) else "conflict"
        if status == "conflict":
            conflicts.append(str(dest_rel))
        if is_fallback:
            unmapped.append(rel.as_posix())
        plan.append({"src": str(rel), "dst": str(dest_rel), "size": path.stat().st_size, "status": status})

    new = sum(1 for p in plan if p["status"] == "new")
    if args.json:
        print(json.dumps({"plan": plan, "conflicts": conflicts, "unmapped": unmapped}, ensure_ascii=False, indent=2))
    else:
        for item in plan:
            mark = {"new": "+", "same": "=", "conflict": "!"}[item["status"]]
            print(f"{mark} {item['src']:<60} → {item['dst']:<55} {item['size']:>8} б")
        print(f"\nвсего: {len(plan)}, новых: {new}, уже совпадает: "
              f"{sum(1 for p in plan if p['status'] == 'same')}, конфликтов: {len(conflicts)}")
        if unmapped:
            print("не размечено правилами, уходит в материалы/: " + ", ".join(unmapped))

    if args.dry_run:
        return 2 if conflicts else 0

    for item in plan:
        if item["status"] == "same":
            continue
        if item["status"] == "conflict" and not args.overwrite:
            continue
        dest = task / item["dst"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / item["src"], dest)

    if args.journal:
        journal = task / "журнал.md"
        row = journal_row(len(plan), new, src.name)
        if journal.exists():
            text = journal.read_text(encoding="utf-8").rstrip("\n") + "\n" + row + "\n"
        else:
            text = ("# Журнал задачи\n\nЗаписи добавляются вниз, старые не удаляются. "
                    "Каждое действие по задаче — строка.\n\n"
                    "| Дата | Что сделали | Артефакты | Кто |\n|---|---|---|---|\n" + row + "\n")
        journal.write_text(text, encoding="utf-8")
        print(f"журнал: добавлена строка в {journal}", file=sys.stderr if args.json else sys.stdout)

    if conflicts and not args.overwrite:
        print("расхождения не перезаписаны: " + ", ".join(conflicts), file=sys.stderr)
        print("разобрать вручную или повторить с --overwrite", file=sys.stderr)
        return 2
    if not args.json:
        print(f"синхронизировано: {new} новых файлов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
