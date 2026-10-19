#!/usr/bin/env python3
"""Собирает сводный файл всех гипотез: data/hypotheses.json из data/lists/*.json.

Списки в data/lists/ — источник истины (по одной проблеме = один файл +
общий список). hypotheses.json — производный: все гипотезы одним файлом.
Запускать после каждой правки списков.
"""
import datetime
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LISTS = ROOT / "data" / "lists"
OUT = ROOT / "data" / "hypotheses.json"


def main() -> int:
    # 1) общий список — реестр: подтягиваем копии из списков по проблемам
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_general.py")],
                       check=True, capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001
        print(f"внимание: синхронизация общего списка не прошла ({exc})")

    # 2) сводный файл всех гипотез
    lists, items = [], []
    for f in sorted(LISTS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        meta = d.get("list") or {}
        lid = meta.get("id") or f.stem
        for it in d.get("items") or []:
            if it.get("srcList"):
                continue      # копия в общем списке: первоисточник — список по проблеме
            row = dict(it)
            row["list"] = lid
            items.append(row)
        lists.append({
            "id": lid,
            "title": meta.get("title") or f.stem,
            "type": meta.get("type") or "general",
            "problem": meta.get("problem"),
            "file": f"data/lists/{f.name}",
            "count": len(d.get("items") or []),
            "updated": meta.get("updated"),
        })
    out = {"updated": datetime.date.today().isoformat(), "count": len(items), "lists": lists, "items": items}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"hypotheses.json · списков {len(lists)} · гипотез {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
