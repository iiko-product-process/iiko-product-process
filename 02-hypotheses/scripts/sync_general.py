#!/usr/bin/env python3
"""Держит общий список гипотез полным: копирует в него гипотезы из списков по проблемам.

Правило простое: общий список = реестр всех гипотез.
- свои гипотезы общего списка (без поля srcList) не трогаем;
- копии из списков по проблемам обновляем из источника;
- если копию правили в интерфейсе ПОЗЖЕ источника (поле upd — время правки), правку копии не затираем.

Запускается автоматически из aggregate.py (его вызывает и сервис при каждом сохранении).
"""
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LISTS = ROOT / "data" / "lists"
GENERAL = LISTS / "obshiy-spisok.json"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    general = load(GENERAL)
    items = general.get("items") or []
    manual = [it for it in items if not it.get("srcList")]
    copies = {it.get("id"): it for it in items if it.get("srcList")}

    # список существующих списков по проблемам — копии удалённых списков из реестра убираем
    alive = {f.stem for f in LISTS.glob("*.json") if f.stem != GENERAL.stem}
    copies = {k: v for k, v in copies.items() if v.get("srcList") in alive}

    result, added, refreshed, kept = list(manual), 0, 0, 0
    for f in sorted(LISTS.glob("*.json")):
        if f.stem == GENERAL.stem:
            continue
        data = load(f)
        meta = data.get("list") or {}
        for it in data.get("items") or []:
            item = dict(it)
            item["srcList"] = f.stem
            item["srcListTitle"] = meta.get("title") or f.stem
            old = copies.get(item.get("id"))
            if old is None:
                result.append(item)
                added += 1
            elif not old.get("upd") or (item.get("upd") or 0) > (old.get("upd") or 0):
                result.append(item)
                refreshed += 1
            else:
                result.append(old)
                kept += 1

    general["items"] = result
    meta = general.setdefault("list", {})
    meta["updated"] = datetime.date.today().isoformat()
    meta.setdefault("problem", None)
    GENERAL.write_text(json.dumps(general, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"общий список: {len(result)} гипотез (своих {len(manual)}, копий +{added}/~{refreshed}, правок сохранено {kept})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
