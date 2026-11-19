#!/usr/bin/env python3
"""Проверка формата и стабильности идентификатора посетителя (user_id) в Matomo.

Зачем: когда визиты/уники за неделю прыгают в 1,5–2,5 раза, а действия (nb_actions)
почти не меняются — это смена базы идентичности, а не трафик. Самый быстрый признак:
формат `label` в UserId.getUsers. Пример 10.11.2026 (iiko): числовой user_id → UUID,
уники +131,9% при действиях +9,2%.

Запуск (нужен рабочий config Matomo, как у fetch_matomo_daily):
    python3 -u detect_uid_format.py 2026-11-02,2026-11-08 2026-11-09,2026-11-15
    python3 -u detect_uid_format.py --days 2026-11-08 2026-11-09 2026-11-10 2026-11-11

Печатает по каждому периоду: сколько id, разбивка numeric/UUID/прочее, визиты по форматам,
сколько idvisitor (cookie) и сколько cookie с несколькими uid. Плюс пересечение наборов id
соседних дней — падает ли узнаваемость (тогда виноваты cookie, а не формат).
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

sys.path.insert(0, "/opt/data/matomo_weekly")
import fetch_matomo_daily as fm  # noqa: E402

BASE = fm.CFG.get("base_url", "https://analytics.iiko.services/").rstrip("/")
SITE = fm.CFG.get("site_id", 1)
TOKEN = fm.token()
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def call(method, date, period="range", **extra):
    p = {"module": "API", "method": method, "idSite": SITE, "period": period, "date": date,
         "format": "JSON", "filter_limit": "-1", "token_auth": TOKEN}
    p.update(extra)
    rq = urllib.request.Request(BASE + "/index.php", data=urllib.parse.urlencode(p).encode(),
                                headers={"User-Agent": "hermes-matomo-probe/1.0"})
    return json.loads(urllib.request.urlopen(rq, timeout=300).read().decode())


def rows(date, period):
    r = call("UserId.getUsers", date, period=period, showColumns="nb_visits,nb_actions")
    return r if isinstance(r, list) else []


def report(label, date, period="range"):
    rs = rows(date, period)
    fmt, visits_fmt = Counter(), Counter()
    by_vis = defaultdict(set)
    ids = set()
    for x in rs:
        uid = str(x.get("label") or "")
        ids.add(uid)
        n = int(x.get("nb_visits") or 0)
        kind = "uuid" if UUID.match(uid) else ("num" if uid.isdigit() else "other")
        fmt[kind] += 1
        visits_fmt[kind] += n
        if x.get("idvisitor"):
            by_vis[x["idvisitor"]].add(uid)
    multi = sum(1 for v in by_vis.values() if len(v) > 1)
    print(f"{label} [{date}/{period}] ids={len(rs)} fmt={dict(fmt)} visits_fmt={dict(visits_fmt)} "
          f"idvisitors={len(by_vis)} idv_with_many_uids={multi}")
    return ids


def overlap(a, b):
    A, B = report(a, a, "day"), report(b, b, "day")
    inter = len(A & B)
    print(f"  пересечение {a} vs {b}: {inter} "
          f"({inter / len(A) * 100:.0f}% от A, {inter / len(B) * 100:.0f}% от B)" if A and B else "  нет данных")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--days"]
    if not args:
        print(__doc__)
        sys.exit(0)
    for a in args:
        report("period", a)
    if "--days" in sys.argv or len(args) > 1:
        seq = [a for a in args if "," not in a]
        for x, y in zip(seq, seq[1:]):
            overlap(x, y)
