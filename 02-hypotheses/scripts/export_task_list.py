#!/usr/bin/env python3
"""Экспорт списка гипотез из прототипа в читаемый markdown-дубль внутри папки задачи.

Использование:
    python3 scripts/export_task_list.py <list_id> Задачи/<слаг>/02-гипотезы/список-гипотез.md

  - <list_id> без префикса пути: например problema-proekt-produkty
  - относительный путь вывода разрешается от корня репозитория iiko-product-process
  - если у задачи несколько списков: имя файла список-гипотез-<id>.md

Дубль не правится вручную: источник истины — data/lists/<list_id>.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 02-hypotheses/
REPO = ROOT.parent                             # iiko-product-process/
PROTO = "http://hermes.iiko.ru:8330"           # запасной адрес — http://10.10.8.10:8330


def score(item, gmap):
    g = sum(a * gmap.get(gid, 1.0) for gid, a in item.get("goals", []))
    return round(item["I"] * item["C"] * item["E"] * g)


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    list_id, out_arg = argv[0], argv[1]
    out_path = Path(out_arg)
    if not out_path.is_absolute():
        out_path = (REPO / out_path).resolve()
    data = json.loads((ROOT / "data" / "lists" / f"{list_id}.json").read_text(encoding="utf-8"))
    lst = data["list"]
    gmap = {g["id"]: g["g"] for g in data["goals"]}
    items = sorted(data["items"], key=lambda it: score(it, gmap), reverse=True)

    L = [f"# Список гипотез — {lst['title']}", ""]
    L.append(f"**Синхронизировано с прототипом:** {lst.get('updated', '')} · список `{lst['id']}`")
    L.append(f"**Прототип:** {PROTO}/?list={lst['id']} (запасной: http://10.10.8.10:8330/?list={lst['id']})")
    L.append("**Оценка:** ICE — балл = I × C × E × G (G — вес целей из файла списка; веса не меняем).")
    L.append("")
    for n, it in enumerate(items, 1):
        sc = score(it, gmap)
        gs = " · ".join(f"{gid}×{a}" for gid, a in it.get("goals", []))
        L.append(f"### {n} — балл {sc} (I{it['I']}·C{it['C']}·E{it['E']}, {gs})")
        L.append(f"**Гипотеза:** {it['name']}")
        L.append(f"**Метрика:** {it['metric']}")
        L.append(f"**Источник:** {it['src']}")
        L.append("")
    low = [it for it in items if it["C"] <= 4]
    if low:
        L.append("**Кандидаты в research (C ≤ 4 — без пользовательских данных):** "
                 + ", ".join(f"«{it['id']}»" for it in low) + ".")
        L.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"OK: {out_path} — гипотез {len(items)}, топ: {items[0]['id']} ({score(items[0], gmap)})")


if __name__ == "__main__":
    main(sys.argv[1:])
