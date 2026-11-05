#!/usr/bin/env python3
"""Замер задержки появления данных в Matomo: сырой слой vs архив отчётов.

Запуск (iiko-инстанс, токен в /opt/data/.env, base_url/idSite из matomo_weekly/config.json):
    cd /opt/data/matomo_weekly && python3 check_archive_freshness.py [минут=15] [интервал_сек=20]

Печатает строку при КАЖДОМ изменении архива: визиты/события за сегодня, последний час,
попавший в архив, время последнего СЫРОГО действия. В конце — список моментов обновления
архива и интервалы между ними. Если за окно наблюдения архив не изменился — это и есть
ответ «пересчёт реже, чем N минут».

Требуется -u (небуферизованный stdout), иначе вывод виден только после выхода процесса:
    python3 -u check_archive_freshness.py 15 20
"""
import os
import json
import sys
import time
import urllib.parse
import urllib.request
import datetime
from pathlib import Path

ENV = Path(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env"))
CFG = Path("/opt/data/matomo_weekly/config.json")


def _cfg():
    try:
        c = json.loads(CFG.read_text(encoding="utf-8"))
    except Exception:
        c = {}
    base = c.get("base_url") or "https://analytics.iiko.services/"
    return base.rstrip("/") + "/index.php", int(c.get("site_id") or 1)


BASE, ID_SITE = _cfg()
TOKEN = next((l.split("=", 1)[1].strip() for l in ENV.read_text(encoding="utf-8").splitlines()
              if l.startswith("MATOMO_TOKEN_AUTH=")), None)
assert TOKEN, "MATOMO_TOKEN_AUTH не найден в /opt/data/.env"


def api(method, **kw):
    data = {"module": "API", "method": method, "format": "json", "token_auth": TOKEN}
    data.update({k: v for k, v in kw.items() if v is not None})
    req = urllib.request.Request(BASE, data=urllib.parse.urlencode(data).encode())
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode()
    try:
        return json.loads(raw)
    except Exception:
        return {"__raw__": raw[:300]}


def now_msk():
    return (datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=3)).strftime("%H:%M:%S")


def measure():
    vs = api("VisitsSummary.get", idSite=ID_SITE, period="day", date="today")
    ev = api("Events.getCategory", idSite=ID_SITE, period="day", date="today",
             filter_limit=-1, showColumns="nb_events")
    ev_total = sum((r.get("nb_events") or 0) for r in ev if isinstance(r, dict)) if isinstance(ev, list) else None
    ht = api("VisitTime.getVisitInformationPerServerTime", idSite=ID_SITE, period="day", date="today")
    last_h = last_v = None
    if isinstance(ht, list):
        nz = [r for r in ht if isinstance(r, dict) and (r.get("nb_visits") or 0) > 0
              and str(r.get("label", "")).split(":")[0].isdigit()]
        if nz:
            last_h, last_v = str(nz[-1]["label"]), nz[-1]["nb_visits"]
    lv = api("Live.getLastVisitsDetails", idSite=ID_SITE, period="day", date="today",
             filter_limit=1, showColumns="lastActionDateTime")
    raw_last = lv[0].get("lastActionDateTime") if isinstance(lv, list) and lv and isinstance(lv[0], dict) else None
    return {"t_msk": now_msk(),
            "arch_visits": vs.get("nb_visits") if isinstance(vs, dict) else None,
            "arch_events": ev_total,
            "arch_last_hour": last_h, "that_hour_visits": last_v,
            "raw_last_action": raw_last}


def main():
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    end = time.time() + minutes * 60
    prev_key = prev_t = None
    changes = []
    while time.time() < end:
        cur = measure()
        key = (cur["arch_visits"], cur["arch_events"], cur["arch_last_hour"])
        if prev_key is None or key != prev_key:
            if prev_key is not None:
                changes.append((prev_t, cur["t_msk"]))
            print(json.dumps(cur, ensure_ascii=False), flush=True)
        prev_key, prev_t = key, cur["t_msk"]
        time.sleep(interval)
    if changes:
        print("ОБНОВЛЕНИЯ АРХИВА:", " | ".join(f"{a}→{b}" for a, b in changes), flush=True)
    else:
        print(f"архив не обновлялся {minutes} мин (сырые данные шли всё время) — пересчёт реже", flush=True)


if __name__ == "__main__":
    main()
