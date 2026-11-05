#!/usr/bin/env python3
"""Когортная сверка двух недель + разложение дельты визитов.

Зачем: недельная дельта визитов/уников почти всегда составная (ядро + приток − отток).
Скрипт отвечает на вопрос «рост/падение — это те же люди работают больше или пришли новые»,
и проверяет арифметику: ядро + только-W1 − только-W2 должно сойтись с фактической дельтой.

Использование (из /opt/data/matomo_weekly, где лежат config.json и fetch_matomo_daily.py):
    python3 -u <skill_dir>/scripts/weekly_cohort_delta.py 2026-10-19,2026-10-25 2026-10-12,2026-10-18

Аргументы: W1-диапазон, W2-диапазон (ISO, через запятую). Без аргументов — две последние
полные недели Пн–Вс относительно сегодняшнего дня.

Ключевая деталь API: `UserId.getUsers` принимает `period=range` и `filter_limit=-1` и отдаёт
по строке на uid с `nb_visits`; `nb_uniq_visitors` в range на этом инстансе НЕ отдаётся,
поэтому считаем визиты. `-u` обязателен, иначе вывод буферизуется до конца процесса.
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, "/opt/data/matomo_weekly")
try:
    import fetch_matomo_daily as fm  # config.json + MATOMO_TOKEN_AUTH
    BASE = fm.CFG.get("base_url", "").rstrip("/")
    SITE = fm.CFG.get("site_id", 1)
    TOKEN = fm.token()
except Exception as exc:  # noqa: BLE001
    sys.exit(f"не смог прочитать config/token из /opt/data/matomo_weekly: {exc}")

if not BASE:
    sys.exit("пустой base_url в config.json")


def call(method, period_range=None, **extra):
    params = {"module": "API", "method": method, "idSite": SITE,
              "format": "JSON", "filter_limit": "-1", "token_auth": TOKEN}
    if period_range:
        params["period"] = "range"
        params["date"] = period_range
    params.update(extra)
    req = urllib.request.Request(BASE + "/index.php",
                                 data=urllib.parse.urlencode(params).encode(),
                                 headers={"User-Agent": "hermes-matomo-cohort/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def last_full_weeks():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    w1_end = monday - timedelta(days=1)
    w1_start = w1_end - timedelta(days=6)
    w2_end = w1_start - timedelta(days=1)
    w2_start = w2_end - timedelta(days=6)
    return f"{w1_start},{w1_end}", f"{w2_start},{w2_end}"


def pct(a, b):
    return None if not b else (a - b) / b * 100


def fmt_pct(a, b):
    p = pct(a, b)
    return "n/a" if p is None else f"{p:+.1f}%"


if len(sys.argv) >= 3:
    W1, W2 = sys.argv[1], sys.argv[2]
else:
    W1, W2 = last_full_weeks()

print(f"W1 = {W1}   W2 = {W2}")

try:
    site = call("SitesManager.getSiteFromId", idSite=SITE)
    if isinstance(site, list):
        site = site[0]
    print(f"timezone сайта: {site.get('timezone')}  main_url: {site.get('main_url')}"
          "  (часы отчётов читаем в этом поясе, а не «серверные вслепую»)")
except Exception as exc:  # noqa: BLE001
    print(f"timezone: ошибка {str(exc)[:120]}")

cols = "nb_uniq_visitors,nb_users,nb_visits,nb_actions,bounce_rate,avg_time_on_site"
tot = {}
for lbl, rng in (("W2", W2), ("W1", W1)):
    tot[lbl] = call("VisitsSummary.get", rng, showColumns=cols)
    t = tot[lbl]
    print(f"{lbl}: уники {t.get('nb_uniq_visitors')}  авториз. {t.get('nb_users')}  "
          f"визиты {t.get('nb_visits')}  действия {t.get('nb_actions')}  "
          f"отказы {t.get('bounce_rate')}  время {t.get('avg_time_on_site')} с")

u1 = {u.get("label"): (u.get("nb_visits") or 0) for u in call("UserId.getUsers", W1)}
u2 = {u.get("label"): (u.get("nb_visits") or 0) for u in call("UserId.getUsers", W2)}
common = set(u1) & set(u2)
only1 = set(u1) - set(u2)
only2 = set(u2) - set(u1)

v_common1 = sum(u1[k] for k in common)
v_common2 = sum(u2[k] for k in common)
v_only1 = sum(u1[k] for k in only1)
v_only2 = sum(u2[k] for k in only2)

print(f"\nuid: W1 {len(u1)}  W2 {len(u2)}  общих {len(common)} "
      f"({len(common)/max(1,len(u1))*100:.0f}% W1, {len(common)/max(1,len(u2))*100:.0f}% W2)")
one1 = sum(1 for k in u1 if u1[k] == 1)
one2 = sum(1 for k in u2 if u2[k] == 1)
print(f"одновизитных: W1 {one1}  W2 {one2} ({fmt_pct(one1, one2)})")
print(f"ядро (общие): визиты {v_common1} vs {v_common2} ({fmt_pct(v_common1, v_common2)})")
print(f"только W1: {len(only1)} uid / {v_only1} визитов   только W2: {len(only2)} uid / {v_only2} визитов")

delta_actual = (tot["W1"].get("nb_visits") or 0) - (tot["W2"].get("nb_visits") or 0)
delta_calc = (v_common1 - v_common2) + v_only1 - v_only2
print(f"\nразложение дельты визитов: ядро {v_common1 - v_common2:+d}  "
      f"новые {v_only1:+d}  ушедшие {-v_only2:+d}  =  {delta_calc:+d}")
print(f"фактическая дельта {delta_actual:+d} — сходится" if abs(delta_calc - delta_actual) <= 0.02 * max(1, abs(delta_actual))
      else f"фактическая дельта {delta_actual:+d} — РАСХОЖДЕНИЕ, проверь диапазоны/период")
print("\nтрактовка: ядро ±<2% = работают как раньше, дельта целиком в притоке/оттоке;"
      " ядро и разовые растут в одну сторону = рост аудитории, в разные = смена состава.")
