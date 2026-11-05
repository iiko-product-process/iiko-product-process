#!/usr/bin/env python3
"""
Выгрузка «раздел × поддомен × uid» (partners: host×user, hosts, users) через сырой слой Live.

Проверенная схема: агрегатные отчёты пару «поддомен × uid» не дают
(в Actions.getPageUrls поле url — один примерный хост на путь), а per-host сегменты
слишком медленные (~60 с на запрос). Поэтому идём Live.getLastVisitsDetails по дням.

Запуск:
    python3 -u export_section_host_uid.py --section internal-couriers --days 30
    python3 -u export_section_host_uid.py --section purchase --days 7 --out /opt/data/exports

Что пишет (в --out, имена с датой последнего дня периода):
    <section>_host_uid_<date>.csv   hostname; user_id; визиты; просмотры раздела; действия; первый/последний день
    <section>_hosts_<date>.csv      hostname; визиты с разделом; уникальных uid; просмотры; визиты без uid; первый/последний
    <section>_users_<date>.csv      user_id; визиты; просмотры; действия; число хостов; список хостов; первый/последний

Конфиг Matomo: env MATOMO_URL / MATOMO_SITE_ID / MATOMO_TOKEN_AUTH, либо
/opt/data/matomo_weekly/config.json + /opt/data/.env (как у остальных скриптов iiko).
Период = от (сегодня − days) до ВЧЕРА включительно (сегодняшний неполный день не берём).
"""
import argparse
import collections
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse


def _token():
    t = os.environ.get("MATOMO_TOKEN_AUTH")
    if t:
        return t
    for p in (Path(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env")), Path.home() / ".hermes" / ".env"):
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("MATOMO_TOKEN_AUTH="):
                    return line.strip().split("=", 1)[1]
        except Exception:
            continue
    return ""


def _base_url():
    if os.environ.get("MATOMO_URL"):
        return os.environ["MATOMO_URL"].rstrip("/")
    try:
        cfg = json.load(open("/opt/data/matomo_weekly/config.json"))
        return str(cfg.get("base_url", "")).rstrip("/")
    except Exception:
        return ""


BASE = _base_url()
TOKEN = _token()
SITE = os.environ.get("MATOMO_SITE_ID") or 1


def api(**p):
    p.setdefault("module", "API")
    p.setdefault("format", "JSON")
    p.setdefault("idSite", SITE)
    p["token_auth"] = TOKEN
    req = urllib.request.Request(BASE + "/index.php",
                                 data=urllib.parse.urlencode({k: str(v) for k, v in p.items()}).encode(),
                                 headers={"User-Agent": "hermes-section-export/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read().decode())


def host_of(u):
    return urlparse(u).hostname or "(без хоста)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default="internal-couriers", help="имя раздела/подстрока URL (segment pageUrl=@...)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default="/opt/data/exports")
    ap.add_argument("--site", default=SITE)
    a = ap.parse_args()

    if not BASE or not TOKEN:
        print("Нет конфига Matomo (MATOMO_URL/MATOMO_TOKEN_AUTH или /opt/data/matomo_weekly/config.json)")
        return 2

    seg = f"pageUrl=@{a.section}"
    safe = a.section.strip("/").replace("/", "_")
    now = datetime.now(timezone.utc) + timedelta(hours=3)
    d2 = (now.date() - timedelta(days=1)).isoformat()
    d1 = (now.date() - timedelta(days=a.days)).isoformat()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    print(f"раздел={a.section} | период: {d1} → {d2} | сайт {a.site}")

    pair = collections.defaultdict(lambda: {"visits": 0, "sec_pv": 0, "actions": 0, "first": "9", "last": "0"})
    host_agg = collections.defaultdict(lambda: {"visits": 0, "sec_pv": 0, "users": set(), "first": "9", "last": "0"})
    user_agg = collections.defaultdict(lambda: {"visits": 0, "sec_pv": 0, "actions": 0, "hosts": set(), "first": "9", "last": "0"})
    anon = collections.defaultdict(int)
    total = 0

    day = datetime.fromisoformat(d1).date()
    while day <= datetime.fromisoformat(d2).date():
        ds = day.isoformat()
        rows = None
        for attempt in range(3):
            try:
                rows = api(method="Live.getLastVisitsDetails", period="day", date=ds, segment=seg,
                           filter_limit=-1,
                           showColumns="userId,visitServerDate,visitLocalTime,actions,actionDetails")
                break
            except Exception as e:
                print(f"  {ds}: ошибка {e}, повтор {attempt + 1}")
                time.sleep(2)
        if not isinstance(rows, list):
            print(f"  {ds}: пропущено"); day += timedelta(days=1); continue
        total += len(rows)
        for v in rows:
            uid = str(v.get("userId") or "").strip()
            date_s = str(v.get("visitServerDate") or ds)
            acts = v.get("actionDetails") or []
            hosts, sec_pv = set(), 0
            for act in acts:
                u = str(act.get("url") or "")
                if a.section.lower() in u.lower():
                    sec_pv += 1
                    hosts.add(host_of(u))
            n_acts = int(v.get("actions") or len(acts) or 0)
            if not hosts:
                hosts = {"(нет URL раздела)"}
            if uid:
                for h in hosts:
                    k = (h, uid); p_ = pair[k]
                    p_["visits"] += 1; p_["sec_pv"] += sec_pv; p_["actions"] += n_acts
                    p_["first"] = min(p_["first"], date_s); p_["last"] = max(p_["last"], date_s)
                    hh = host_agg[h]
                    hh["visits"] += 1; hh["sec_pv"] += sec_pv; hh["users"].add(uid)
                    hh["first"] = min(hh["first"], date_s); hh["last"] = max(hh["last"], date_s)
                uu = user_agg[uid]
                uu["visits"] += 1; uu["sec_pv"] += sec_pv; uu["actions"] += n_acts; uu["hosts"] |= hosts
                uu["first"] = min(uu["first"], date_s); uu["last"] = max(uu["last"], date_s)
            else:
                for h in hosts:
                    anon[h] += 1
        print(f"  {ds}: визитов={len(rows)}")
        day += timedelta(days=1)

    f1 = out / f"{safe}_host_uid_{d2}.csv"
    with f1.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["hostname", "user_id", "visits", "section_pageviews", "actions_in_visit", "first_seen", "last_seen"])
        for (h, u), x in sorted(pair.items(), key=lambda kv: (-kv[1]["visits"], kv[0][0])):
            w.writerow([h, u, x["visits"], x["sec_pv"], x["actions"], x["first"], x["last"]])
    f2 = out / f"{safe}_hosts_{d2}.csv"
    with f2.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["hostname", "visits_with_section", "unique_users", "section_pageviews", "visits_without_uid", "first_seen", "last_seen"])
        for h, x in sorted(host_agg.items(), key=lambda kv: -kv[1]["visits"]):
            w.writerow([h, x["visits"], len(x["users"]), x["sec_pv"], anon.get(h, 0), x["first"], x["last"]])
    f3 = out / f"{safe}_users_{d2}.csv"
    with f3.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["user_id", "visits", "section_pageviews", "actions", "hosts_count", "hostnames", "first_seen", "last_seen"])
        for u, x in sorted(user_agg.items(), key=lambda kv: -kv[1]["visits"]):
            w.writerow([u, x["visits"], x["sec_pv"], x["actions"], len(x["hosts"]), " ".join(sorted(x["hosts"])), x["first"], x["last"]])

    print(f"\nвизитов={total} | пар(хост,uid)={len(pair)} | хостов={len(host_agg)} | uid={len(user_agg)}")
    for p_ in (f1, f2, f3):
        print(" ", p_, f"({p_.stat().st_size / 1024:.0f} КБ)")
    print("\nтоп-10 поддоменов:")
    for h, x in sorted(host_agg.items(), key=lambda kv: -kv[1]["visits"])[:10]:
        print(f"  {h:<45} визиты={x['visits']:<6} uid={len(x['users']):<5} без uid={anon.get(h, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
