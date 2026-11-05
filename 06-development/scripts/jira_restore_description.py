#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Возврат описания задачи Jira из файла-бэкапа.

    python3 jira_restore_description.py PB-7065 backups/PB-7065-description-...txt          # проверка, ничего не пишем
    python3 jira_restore_description.py PB-7065 backups/PB-7065-description-...txt --apply   # заменить описание

Печатает, чем текущее описание отличается от файла, и пишет только с явным --apply.
После записи читает описание обратно и сверяет с файлом побайтово.
Нужны JIRA_URL (по умолчанию https://jira.iiko.ru) и JIRA_TOKEN.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

JIRA_URL = os.environ.get("JIRA_URL", "https://jira.iiko.ru").rstrip("/")
TOKEN = os.environ.get("JIRA_TOKEN", "")


def api(path, payload=None, params=None):
    url = JIRA_URL + path + ("?" + urllib.parse.urlencode(params) if params else "")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method="PUT" if data else "GET")
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(body) if body.strip().startswith(("{", "[")) else body)
    except urllib.error.HTTPError as e:
        raise RuntimeError("Jira %s: HTTP %s %s" % (path, e.code, e.read().decode("utf-8", "replace")[:200])) from None
    except urllib.error.URLError as e:
        raise RuntimeError("Jira недоступна: %s" % e.reason) from None


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_backup(path):
    """Читает файл-бэкап как есть: без перевода переводов строк, с понятной ошибкой вместо трейсбека."""
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except OSError as e:
        raise SystemExit("Не читается файл-бэкап (%s): %s" % (path, e)) from None


def main():
    ap = argparse.ArgumentParser(description="Вернуть описание задачи Jira из бэкапа")
    ap.add_argument("task", help="ключ задачи (PB-7065) или ссылка")
    ap.add_argument("file", help="файл-бэкап с описанием")
    ap.add_argument("--apply", action="store_true", help="действительно записать (без флага — только проверка)")
    args = ap.parse_args()

    if not TOKEN:
        raise SystemExit("Не задан JIRA_TOKEN (source /opt/data/.env)")
    m = re.search(r"([A-Z][A-Z0-9_]+-\d+)", args.task.upper())
    if not m:
        raise SystemExit("Не понял задачу: %r" % args.task)
    key = m.group(1)

    want = read_backup(args.file)
    _, current = api("/rest/api/2/issue/" + key, params={"fields": "description,summary"})
    have = current["fields"].get("description") or ""

    print("задача:      %s — «%s»" % (key, current["fields"]["summary"]))
    print("в Jira:      %d символов, sha %s" % (len(have), sha(have)))
    print("в бэкапе:    %d символов, sha %s  (%s)" % (len(want), sha(want), args.file))

    if have == want:
        print("описания совпадают — менять нечего")
        return 0

    a, b = have.splitlines(), want.splitlines()
    print("отличие: в Jira %d строк, в бэкапе %d" % (len(a), len(b)))
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            print("первое расхождение, строка %d:" % i)
            print("  в Jira:  " + x[:120])
            print("  в бэкапе:" + y[:120])
            break

    if not args.apply:
        print("\nэто проверка: ничего не записано. Чтобы заменить описание — повторить с --apply")
        return 0

    api("/rest/api/2/issue/" + key, payload={"fields": {"description": want}})
    _, after = api("/rest/api/2/issue/" + key, params={"fields": "description"})
    got = after["fields"].get("description") or ""
    ok = got == want
    print("\nзаписано: %d символов, sha %s | совпадает с бэкапом: %s" % (len(got), sha(got), ok))
    if not ok:
        print("ПРОВЕРКА НЕ ПРОШЛА — описание в Jira отличается от файла, разбирать вручную", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
