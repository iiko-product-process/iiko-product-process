#!/usr/bin/env python3
"""Спрос и пересечения аудиторий по списку экранов (Matomo Reporting API).

Класс задач: «сколько людей и визитов у каждой локации из UI-аудита» + «кто с кем
пересекается» (переносится ли навык между экранами).

Использование:
    python3 -u section_demand_overlap.py targets.json [--range 2026-09-29,2026-10-28] [--out DIR] [--base "Имя"]

targets.json — объект {"Название локации": "/path/без/сегмента", ...}; сегмент
строится как pageUrl=@/<path>. Ключ с именем из --base используется как «базовый»
раздел для колонки «доля зашедших в базу».

Токен: /opt/data/.env → MATOMO_TOKEN_AUTH (только POST-параметром).
Почему так: compound-сегменты (`a;b`) стоят ~60 с и часто дают 0 — здесь множества
uid снимаются по одной локации, а все пересечения считаются локально.
"""
import argparse
import csv
import itertools
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://analytics.iiko.services/index.php"
IDSITE = 1
ENV_PATH = os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env")


def token() -> str:
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("MATOMO_TOKEN_AUTH="):
                return line.strip().split("=", 1)[1]
    sys.exit(f"MATOMO_TOKEN_AUTH не найден в {ENV_PATH}")


TOK = token()


def api(method, **extra):
    params = {"module": "API", "method": method, "format": "JSON",
              "token_auth": TOK, "idSite": IDSITE}
    params.update({k: str(v) for k, v in extra.items()})
    req = urllib.request.Request(BASE_URL, data=urllib.parse.urlencode(params).encode(),
                                 headers={"User-Agent": "hermes-section-demand/1.0"})
    with urllib.request.urlopen(req, timeout=280) as r:
        return json.loads(r.read().decode("utf-8"))


def demand(item, date_range):
    name, path = item
    seg = f"pageUrl=@/{str(path).lstrip('/')}"
    try:
        vs = api("VisitsSummary.get", period="range", date=date_range, segment=seg)
        us = api("UserId.getUsers", period="range", date=date_range, segment=seg,
                 filter_limit=-1, showColumns="nb_visits")
        ids = {u.get("label") or u.get("userId") for u in us} if isinstance(us, list) else set()
        ids.discard(None)
        return {"name": name, "path": path,
                "visits": vs.get("nb_visits", 0) or 0,
                "actions": vs.get("nb_actions", 0) or 0,
                "users": len(ids), "uids": ids}
    except Exception as ex:  # noqa: BLE001 — одна локация не должна ронять прогон
        return {"name": name, "path": path, "error": str(ex)[:160], "uids": set()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", help="JSON {название: путь}")
    ap.add_argument("--range", default="", help="ГГГГ-ММ-ДД,ГГГГ-ММ-ДД (30 дней по умолчанию)")
    ap.add_argument("--out", default=".")
    ap.add_argument("--base", default="", help="имя локации, считающейся базовой")
    args = ap.parse_args()

    targets = json.load(open(args.targets, encoding="utf-8"))
    if not isinstance(targets, dict) or not targets:
        sys.exit("targets.json должен быть непустым объектом {название: путь}")

    if args.range:
        date_range = args.range
    else:
        from datetime import date, timedelta
        d_to = date.today() - timedelta(days=1)
        date_range = f"{d_to - timedelta(days=29)},{d_to}"

    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda it: demand(it, date_range), targets.items()))

    ok = [r for r in res if "error" not in r]
    base_name = args.base or ok[0]["name"] if ok else ""
    base = next((r for r in ok if r["name"] == base_name), None)

    print(f"# период {date_range}, idSite {IDSITE}")
    print(f"{'Локация':38s} {'visits':>8} {'users*':>7} {'actions':>9} {'vis/чел':>8}  {'в базе':>7}")
    for r in sorted(ok, key=lambda x: -x["visits"]):
        per = r["visits"] / r["users"] if r["users"] else 0
        share = f"{100 * len(r['uids'] & base['uids']) / r['users']:.1f}%" if base and r["users"] and base is not r else "—"
        print(f"{r['name'][:38]:38s} {r['visits']:>8} {r['users']:>7} {r['actions']:>9} {per:>8.1f}  {share:>7}")
    for r in res:
        if "error" in r:
            print(f"{r['name'][:38]:38s} ERROR {r['error']}")

    print("\n# пересечения (общие uid; %от A / %от B)")
    pairs = sorted(((a, b) for a, b in itertools.combinations(ok, 2)),
                   key=lambda p: -len(p[0]["uids"] & p[1]["uids"]))
    for a, b in pairs[:20]:
        inter = len(a["uids"] & b["uids"])
        if not inter:
            continue
        print(f"{a['name'][:26]:26s} {b['name'][:26]:26s} {inter:>6} "
              f"{100 * inter / len(a['uids']):>6.1f}% {100 * inter / len(b['uids']):>6.1f}%")

    everything = set().union(*[r["uids"] for r in ok]) if ok else set()
    dist = Counter(sum(1 for r in ok if uid in r["uids"]) for uid in everything)
    print(f"\n# всего уникальных людей: {len(everything)}")
    print("# поверхностей на человека: " + ", ".join(f"{k}→{v}" for k, v in sorted(dist.items())))
    print(f"# 3+ поверхностей: {sum(v for k, v in dist.items() if k >= 3)}")

    os.makedirs(args.out, exist_ok=True)
    out_csv = os.path.join(args.out, "section_demand_overlap.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["локация", "путь", "визиты", "пользователи_uid", "действия",
                    "визитов_на_человека", f"доля_в_{base_name or 'базе'}", "ошибка"])
        for r in sorted(res, key=lambda x: -x.get("visits", 0)):
            per = round(r["visits"] / r["users"], 1) if r.get("users") else ""
            share = (round(100 * len(r["uids"] & base["uids"]) / r["users"], 1)
                     if base and r.get("users") and r is not base else "")
            w.writerow([r["name"], r["path"], r.get("visits", ""), r.get("users", ""),
                        r.get("actions", ""), per, share, r.get("error", "")])
    print(f"\nCSV: {out_csv}")
    print("* users = аккаунты с uid; визиты без uid не учитываются")


if __name__ == "__main__":
    main()
