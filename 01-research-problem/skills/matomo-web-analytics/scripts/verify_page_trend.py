#!/usr/bin/env python3
"""Verify a page's metrics across several periods — for checking claims inherited
from earlier reports before repeating them in a new one.

WHY: recurring reports (weekly/daily) reuse numbers from the previous run
("hits/visit 5,33 → 6,86 → 4,47"). A claim spanning 3+ weeks cannot be verified
from the current run's data.json alone — data.json only holds W1 and W2. Query the
older period directly against the API first; an unverifiable claim must not ship.

USAGE
    python3 verify_page_trend.py /navigator /inventory
    python3 verify_page_trend.py /navigator --weeks 4
    python3 verify_page_trend.py /navigator --periods 2026-09-07,2026-09-13 2026-09-14,2026-09-20

Token: env MATOMO_TOKEN_AUTH, else the MATOMO_TOKEN_AUTH= line in /opt/data/.env.
NOTE: token is sent as a POST form field (this instance rejects token_auth in the URL).

LABEL MATCHING — the classic time-waster: `Actions.getPageUrls` WITHOUT `flat=1`
returns tree rows whose label is a bare segment ("navigator"); WITH `flat=1` the
same rows come back as paths ("/navigator/index.html"). This script always sends
`flat=1` and matches on the raw label, so pass the SHORT page name (/navigator)
and let it build the raw label. Matching the short label against a flat response
silently yields "нет данных" for every period.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta

ENV_PATH = os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env")
API_URL = "https://analytics.iiko.services/index.php"
SITE_ID = 1


def get_token():
    tok = os.environ.get("MATOMO_TOKEN_AUTH")
    if tok:
        return tok
    try:
        with open(ENV_PATH, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MATOMO_TOKEN_AUTH="):
                    return line.strip().split("=", 1)[1]
    except OSError:
        pass
    sys.exit("нет MATOMO_TOKEN_AUTH (env или %s)" % ENV_PATH)


def api(method, period, date_str, extra=None):
    params = {
        "module": "API", "method": method, "idSite": SITE_ID,
        "period": period, "date": date_str, "format": "JSON",
        "filter_limit": "-1", "token_auth": get_token(),
    }
    if extra:
        params.update(extra)
    body = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body,
                                 headers={"User-Agent": "hermes-matomo-verify/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def last_full_weeks(count, today=None):
    """Последние `count` полных недель Пн–Вс, старые первыми."""
    today = today or date.today()
    monday = today - timedelta(days=today.weekday())
    out = []
    end = monday - timedelta(days=1)
    for _ in range(count):
        start = end - timedelta(days=6)
        out.append("%s,%s" % (start.isoformat(), end.isoformat()))
        end = start - timedelta(days=1)
    return list(reversed(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pages", nargs="+", help="короткие имена, напр. /navigator /inventory")
    ap.add_argument("--periods", nargs="*", help="'YYYY-MM-DD,YYYY-MM-DD' (порядок произвольный)")
    ap.add_argument("--weeks", type=int, default=3, help="сколько последних полных недель (по умолчанию 3)")
    args = ap.parse_args()

    periods = args.periods or last_full_weeks(args.weeks)
    wanted = {}
    for p in args.pages:
        raw = p if p.endswith(".html") else p.rstrip("/") + "/index.html"
        wanted[raw] = p

    for period in periods:
        rows = api("Actions.getPageUrls", "range", period, {"flat": "1"})
        if isinstance(rows, dict) and "__error__" in rows:
            print("--- %s  ОШИБКА: %s" % (period, rows["__error__"]))
            continue
        found = {r["label"]: r for r in rows
                 if isinstance(r, dict) and r.get("label") in wanted}
        print("--- %s  (строк: %d)" % (period, len(rows)))
        for raw, short in wanted.items():
            row = found.get(raw)
            if not row:
                print("   %-22s нет данных (проверь метку: нужен сырой вид %s)" % (short, raw))
                continue
            visits, hits = num(row.get("nb_visits")), num(row.get("nb_hits"))
            hpv = (hits / visits) if visits else 0.0
            print("   %-22s visits=%8.0f hits=%9.0f hits/visit=%5.2f avg_time=%ss bounce=%s"
                  % (short, visits, hits, hpv, row.get("avg_time_on_page"), row.get("bounce_rate")))


if __name__ == "__main__":
    main()
