#!/usr/bin/env python3
"""Детектор смены базы идентичности в Matomo (iiko).

Печатает по дням nb_users / nb_uniq_visitors / nb_visits / nb_actions с дельтами и помечает
дни, где уники или визиты упали >25%, а пользователи и действия остались в пределах ±10%
— признак склейки сессий (раскатка uid), а не потери трафика. Затем раскладывает два
последних дня сегментами userId!= / userId==.

Использование:
    cd /opt/data/matomo_weekly && python3 -u \
        /opt/data/skills/research/matomo-web-analytics/scripts/detect_identity_step.py [дней=14]

`-u` обязателен (иначе вывод буферизуется до конца процесса).
Запускать через terminal: `execute_code` в cron-профиле заблокирован.

Подтверждённый кейс 2026-10-01: uniq 21 323 → 11 248 (−47%), visits 44 054 → 22 788 (−48%),
users 4 660 → 4 573 (−1,9%), actions 223 274 → 220 246 (−1,4%) → склейка uid, не потеря трафика.
"""
import sys
from datetime import date, timedelta

sys.path.insert(0, "/opt/data/matomo_weekly")
import fetch_matomo_daily as fm  # noqa: E402

COLS = "nb_uniq_visitors,nb_users,nb_visits,nb_actions"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 14


def get(dt, extra=None):
    """VisitsSummary.get за день; None при ошибке."""
    r = fm.api("VisitsSummary.get", dt, dict({"showColumns": COLS}, **(extra or {})))
    if isinstance(r, dict) and "__error__" in r:
        return None
    return r


def pct(new, old):
    return 100.0 * (new - old) / old if old else 0.0


def main():
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(DAYS, 0, -1)]
    print(f"{'дата':11s} {'users':>7s} {'uniq':>8s} {'visits':>8s} {'actions':>9s}  "
          f"{'Δusers':>7s} {'Δuniq':>7s} {'Δvisit':>7s} {'Δact':>7s}  флаг")
    prev = None
    for dt in days:
        r = get(dt)
        if not r or not r.get("nb_uniq_visitors"):
            print(f"{dt:11s}  — нет данных")
            prev = None
            continue
        u, nu, v, a = r["nb_users"], r["nb_uniq_visitors"], r["nb_visits"], r["nb_actions"]
        if prev:
            du, dnu, dv, da = pct(u, prev[0]), pct(nu, prev[1]), pct(v, prev[2]), pct(a, prev[3])
            flag = ""
            if (dnu < -25 or dv < -25) and abs(du) < 10 and abs(da) < 10:
                flag = "◀ СМЕНА БАЗЫ ИДЕНТИЧНОСТИ?"
            print(f"{dt:11s} {u:7d} {nu:8d} {v:8d} {a:9d}  "
                  f"{du:+7.1f} {dnu:+7.1f} {dv:+7.1f} {da:+7.1f}  {flag}")
        else:
            print(f"{dt:11s} {u:7d} {nu:8d} {v:8d} {a:9d}")
        prev = (u, nu, v, a)

    print("\nразложение по uid (два последних дня с данными):")
    for dt in days[-2:]:
        w, wo = get(dt, {"segment": "userId!="}), get(dt, {"segment": "userId=="})
        if w and wo:
            print(f"  {dt}  с uid:  u={w['nb_uniq_visitors']:6d} v={w['nb_visits']:6d} "
                  f"a={w['nb_actions']:8d}   без uid: u={wo['nb_uniq_visitors']:6d} "
                  f"v={wo['nb_visits']:6d} a={wo['nb_actions']:8d}")


if __name__ == "__main__":
    main()
