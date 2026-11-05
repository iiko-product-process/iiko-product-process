#!/usr/bin/env python3
"""«Дверь» приложения и подстраницы модуля — сегментами Matomo.

usage: python3 -u door_probe.py <ГГГГ-ММ-ДД> [module]     # по умолчанию navigator

Печатает:
  • итог модуля и точки входа /<module>/auth/login, /<module>/home
    (сегмент pageUrl=@<подпуть> — строка getPageUrls такого разбиения не даёт);
  • топ-12 подстраниц модуля (flat=1 + showColumns — без showColumns ответ в разы толще).

Проверено 13.10.2026 (iiko prod): /navigator/auth/login 2 715 уник. / 5 416 виз. = 95% уников
navigator, /navigator/home 2 241 / 4 136, модуль целиком 2 853 / 5 840.

ВАЖНО: token_auth уходит POST-ом. При GET инстанс отвечает
'Unable to authenticate with the provided token. It is either invalid, expired or is
required to be sent as a POST parameter.' — не принимать это за протухший токен.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "/opt/data/matomo_weekly"
CFG = json.load(open(f"{BASE}/config.json")) if os.path.exists(f"{BASE}/config.json") else {}


def token():
    t = os.environ.get("MATOMO_TOKEN_AUTH")
    if t:
        return t
    try:
        for line in open(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env"), encoding="utf-8"):
            if line.startswith("MATOMO_TOKEN_AUTH="):
                return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass
    return ""


def api(method, date_str, extra=None):
    params = {"module": "API", "method": method, "idSite": CFG.get("site_id", 1),
              "period": "day", "date": date_str, "format": "JSON",
              "filter_limit": "-1", "token_auth": token()}
    if extra:
        params.update(extra)
    req = urllib.request.Request(
        CFG.get("base_url", "https://analytics.iiko.services/").rstrip("/") + "/index.php",
        data=urllib.parse.urlencode(params).encode(),  # POST — GET не проходит авторизацию
        headers={"User-Agent": "hermes-matomo-door/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ds = sys.argv[1]
    mod = "/" + (sys.argv[2] if len(sys.argv) > 2 else "navigator").strip("/")

    for sub in ("", "/auth/login", "/home"):
        r = api("VisitsSummary.get", ds, {"segment": "pageUrl=@" + mod + sub})
        if isinstance(r, dict):
            print(f"{mod + sub:32s} uniq={r.get('nb_uniq_visitors')} "
                  f"visits={r.get('nb_visits')} actions={r.get('nb_actions')}")
        else:
            print(f"{mod + sub:32s} {r}")

    r = api("Actions.getPageUrls", ds, {"segment": "pageUrl=@" + mod, "flat": "1",
                                        "filter_limit": "12",
                                        "showColumns": "nb_uniq_visitors,nb_visits,nb_hits"})
    print(f"\nflat {mod} (топ подстраниц):")
    for x in (r if isinstance(r, list) else []):
        print(f"  {x.get('label')}  u={x.get('nb_uniq_visitors')} "
              f"v={x.get('nb_visits')} h={x.get('nb_hits')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
