#!/usr/bin/env python3
"""Разбор daily.json (ежедневный дайджест iiko) в цифры для отчёта.

Использование:
    python3 daily_digest_stats.py [/opt/data/matomo_weekly/daily.json]

Печатает: сверку полноты дня, резюме, топ-12 модулей с соотношениями и раскладом
устройств, возвратность, мобильные/десктопные модули, пик/минимум часа, вечернее окно,
концентрацию от totals.visits и служебные/dev-строки.

Запускать из cron-сессии через terminal (не execute_code — в cron-профиле заблокирован).
"""
import json
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "/opt/data/matomo_weekly/daily.json"
SHORT = {"Desktop": "D", "Smartphone": "M", "Tablet": "T", "Phablet": "P"}


def devmap(page):
    return {d["label"]: d["pct"] for d in page.get("devices") or []}


def devstr(devs, order=("Desktop", "Smartphone", "Tablet", "Phablet")):
    parts = [f"{SHORT.get(k, k[:1])} {v}%" for k, v in devs.items()]
    return " / ".join(parts)


def main():
    with open(PATH) as f:
        d = json.load(f)
    # Квирк инстанса: у мелких модулей uniq/visits/hits приходят как null (01.10.2026 —
    # recipe-manage, kiosk-management, payment-gateways, purchase-mobile, error).
    # Без нормализации скрипт падает на сортировке: TypeError: bad operand type for unary -: 'NoneType'.
    null_uniq = [p["module"] for p in d["pages"] if p.get("uniq") is None]
    for p in d["pages"]:
        for k in ("uniq", "visits", "hits"):
            if p.get(k) is None:
                p[k] = 0.0
    pages = sorted(d["pages"], key=lambda p: -p["uniq"])
    tot = d["totals"]

    print(f'ДАННЫЕ: {d.get("date")} ({d.get("weekday")}) | модулей: {len(pages)}')
    if null_uniq:
        print(f'  ↳ uniq=null в источнике (обнулены для расчётов): {", ".join(null_uniq)}')

    s = sum(h["visits"] for h in d["hourly"])
    ok = abs(s - tot["visits"]) < 1
    print(f'ПОЛНОТА ДНЯ: Σ по 24 часам {int(s)} vs totals.visits {int(tot["visits"])} → '
          f'{"ОК (день полный)" if ok else "НЕ СХОДИТСЯ — день неполный!"}')

    print(f'\nРЕЗЮМЕ: уники {int(tot["uniq"])} · визиты {int(tot["visits"])} · '
          f'действия {int(tot["actions"])} · отказы {tot.get("bounce")}%')
    print(f'Устройства дня: {devstr({x["label"]: x["pct"] for x in d.get("devices_total") or []})}')
    print(f'Глубина: {tot["actions"] / tot["uniq"]:.2f} действия/уника · '
          f'{tot["actions"] / tot["visits"]:.2f} на визит · {tot["visits"] / tot["uniq"]:.2f} визита/уника')
    print('  ↳ «на визит» = (действия/уника) / (визиты/уника): если «на визит» упало, а «на уника» нет — '
          'это больше коротких возвратов, а не меньше работы (питфолл 26.09: 5,11 → 4,80 при 10,86 → 10,84)')

    hz = d["hourly"]
    mx = max(hz, key=lambda h: h["visits"])
    mn = min(hz, key=lambda h: h["visits"])
    ev = sum(h["visits"] for h in hz if 18 <= h["hour"] <= 23)
    night = sum(h["visits"] for h in hz if h["hour"] <= 5)
    plateau = [h["visits"] for h in hz if 10 <= h["hour"] <= 15]
    print(f'Часы: пик {mx["hour"]:02d}:00 ({int(mx["visits"])}), минимум {mn["hour"]:02d}:00 ({int(mn["visits"])}); '
          f'плато 10–15ч {int(min(plateau))}–{int(max(plateau))}; '
          f'18–23ч {100 * ev / tot["visits"]:.1f}% суток; 00–05ч {100 * night / tot["visits"]:.1f}%')

    print("\nТОП-12 (uniq/visits, ratio, hits, устройства):")
    for p in pages[:12]:
        r = p["visits"] / p["uniq"] if p["uniq"] else 0
        print(f'  {p["module"]:20s} {int(p["uniq"]):6d} / {int(p["visits"]):6d}  r={r:4.2f}  '
              f'hits={int(p["hits"]):7d}  {devstr(devmap(p))}')

    vsum = sum(p["visits"] for p in pages)
    small = [p["module"] for p in pages if p["uniq"] < 20]
    print(f'\nХВОСТ: модулей с <20 уников {len(small)}' + (f' — {", ".join(small)}' if small else ''))
    print(f'МОДУЛЕЙ С ТРАФИКОМ: {len(pages)} (в выходной обычно ~50, в будни ~60 — это норма, не потеря)')
    top2 = sum(p["visits"] for p in pages[:2])
    print(f'\nКОНЦЕНТРАЦИЯ: top-2 {100 * top2 / tot["visits"]:.1f}% визитов дня (от totals.visits), '
          f'top-5 {100 * sum(p["visits"] for p in pages[:5]) / tot["visits"]:.1f}%')
    print(f'  Σ визитов по модулям {int(vsum)} (двойной счёт кросс-доменно) — долю от неё НЕ считать; '
          f'Σ уников {int(sum(p["uniq"] for p in pages))} vs итог {int(tot["uniq"])}')

    big = [p for p in pages if p["uniq"] >= 100]
    print("\nВОЗВРАТНОСТЬ (visits/uniq, uniq>=100) — макс:")
    for p in sorted(big, key=lambda x: -x["visits"] / x["uniq"])[:6]:
        print(f'  {p["module"]:20s} {p["visits"] / p["uniq"]:.2f}  (uniq {int(p["uniq"])})')
    print("  мин (почти разовые):")
    for p in sorted(big, key=lambda x: x["visits"] / x["uniq"])[:6]:
        print(f'  {p["module"]:20s} {p["visits"] / p["uniq"]:.2f}  (uniq {int(p["uniq"])})')

    print("\nРАСКЛАД УСТРОЙСТВ (uniq>=200):")
    mob = [p for p in pages if p["uniq"] >= 200 and devmap(p).get("Smartphone", 0) >= 60]
    dsk = [p for p in pages if p["uniq"] >= 200 and devmap(p).get("Desktop", 0) >= 90]
    print("  мобильные-первые (M>=60%): " + (", ".join(
        f'{p["module"]} M{devmap(p)["Smartphone"]}%' for p in sorted(mob, key=lambda x: -devmap(x)["Smartphone"])) or "нет"))
    print("  десктопные (D>=90%):      " + (", ".join(
        f'{p["module"]} D{devmap(p)["Desktop"]}%' for p in sorted(dsk, key=lambda x: -devmap(x)["Desktop"])) or "нет"))

    print("\nСЛУЖЕБНЫЕ / DEV-СТРОКИ (uniq<=3) и прочее:")
    for p in pages:
        if p["uniq"] <= 3:
            print(f'  {p["module"]:24s} u={int(p["uniq"])} v={int(p["visits"])} h={int(p["hits"])}')
    for p in pages:
        if p["module"] in ("Page URL not defined", "/index", "/nomenclature", "ru-RU"):
            print(f'  {p["module"]:24s} u={int(p["uniq"])} v={int(p["visits"])}')
    print(f'\nnote: {d.get("note")}')


if __name__ == "__main__":
    main()
