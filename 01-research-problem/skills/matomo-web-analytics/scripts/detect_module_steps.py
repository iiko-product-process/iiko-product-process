#!/usr/bin/env python3
"""Ступенька vs тренд: 14 дней × модули (`Actions.getPageUrls`, non-flat) → ищем шаг в один день.

Зачем: недельная дельта «−17% у модуля» выглядит как уход пользователей, а на деле часто
оказывается шагом в один день (релиз/раскатка/изменение разметки). Скрипт сравнивает Вт–Вс
обеих недель (чтобы понедельник после отчётного дня не раздувал дельту) и печатает дневные
ряды по выбившимся модулям — по ряду видно, ступень это или плавный дрейф.

Проверено 2026-09-21 на iiko prod: нашёл шаг 15.09 (forecast 1 354 → 2 566 визитов/день,
till-shifts 8 233 → 7 065), который в недельной сводке выглядел как «−16,8% у till-shifts».

Запуск (пути внутри абсолютные, cwd любой):
    python3 -u /opt/data/skills/research/matomo-web-analytics/scripts/detect_module_steps.py [дней=14] [порог_%=25]

Читать вывод так:
  * «Вт–Вс: W1 против W2» — устойчивое изменение недели к неделе (база >= 200 визитов за 6 дней).
  * «Дневные ряды» — если значение меняется один раз и держится, это ступень: гипотезу о релизе/
    раскатке надо подтверждать у команды, а не подавать как органический рост/падение.
  * Понедельник в сравнение НЕ входит специально (в W2 там обычно отчётный день месяца).

Токен берётся из env → /opt/data/.env → config.json силами fetch_matomo.py; только POST-параметром.
"""
import os
import importlib.util
import json
import sys
from datetime import date, timedelta

FM = "/opt/data/matomo_weekly/fetch_matomo.py"
CFG = "/opt/data/matomo_weekly/config.json"

NDAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 14
THRESH = float(sys.argv[2]) if len(sys.argv) > 2 else 25.0


def load_fm():
    spec = importlib.util.spec_from_file_location("fm", FM)
    fm = importlib.util.module_from_spec(spec)
    sys.argv = ["fm"]
    spec.loader.exec_module(fm)
    return fm


fm = load_fm()
cfg = json.load(open(CFG))

today = date.today()
days = [(today - timedelta(days=1 + i)).isoformat() for i in range(NDAYS)]
days.reverse()
if len(days) < 14:
    print("ВНИМАНИЕ: дней меньше 14 — сравнение Вт–Вс всё равно, но недели могут быть неполными")

data = {}
for d in days:
    rows = fm.api(cfg, "Actions.getPageUrls", "day", d, {"filter_limit": 200})
    row_map = {}
    for r in rows:
        row_map[r["label"]] = (int(r.get("nb_visits") or 0), int(r.get("nb_hits") or 0))
    data[d] = row_map
    print("fetched %s: %d строк" % (d, len(row_map)), flush=True)

w2_days = days[:7]
w1_days = days[7:]
w1_cmp = w1_days[1:]   # Вт–Вс текущей
w2_cmp = w2_days[1:]   # Вт–Вс предыдущей

mods = set()
for d in days:
    mods.update(data[d].keys())


def total(day_list, mod, idx):
    s = 0
    for d in day_list:
        row = data[d].get(mod)
        if row:
            s += row[idx]
    return s


movers = []
for m in sorted(mods):
    a = total(w1_cmp, m, 0)
    b = total(w2_cmp, m, 0)
    if b < 200:
        continue
    pct = (a - b) / b * 100.0
    if abs(pct) >= THRESH:
        movers.append((m, a, b, pct))

movers.sort(key=lambda x: x[3])

print("\n=== Вт–Вс: W1 (%s…%s) против W2 (%s…%s) — модули с |Δ| >= %.0f%% и базой >= 200 визитов ===" % (
    w1_cmp[0], w1_cmp[-1], w2_cmp[0], w2_cmp[-1], THRESH))
if not movers:
    print("  ничего не выбилось за порог — неделя без значимых изменений по модулям")
for m, a, b, p in movers:
    print("  %-26s %8d vs %8d  %+7.1f%%" % (m, a, b, p))

print("\n=== Дневные ряды выбившихся (ступень = одноразовый сдвиг, который держится) ===")
for m, a, b, p in movers:
    series = []
    for d in days:
        row = data[d].get(m)
        series.append((d, row[0] if row else 0))
    print("  %s" % m)
    print("    " + " ".join("%s:%d" % (d[5:], v) for d, v in series))
    base = [v for d, v in series if d in w2_cmp and v]
    if not base:
        continue
    avg = float(sum(base)) / len(base)
    if avg <= 0:
        continue
    prev = None
    for d, v in series:
        if d not in w1_days:
            continue
        if abs(v - avg) / avg * 100.0 >= 15.0 and prev is not None and (v - avg) * (prev - avg) > 0:
            print("    → похоже на ШАГ %s: в W2 было ~%.0f визитов/день (Вт–Вс), стало %d/день" % (d, avg, v))
            break
        prev = v
