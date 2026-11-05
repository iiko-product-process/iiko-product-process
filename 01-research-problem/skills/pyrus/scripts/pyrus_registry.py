#!/usr/bin/env python3
"""Fetch Pyrus form registry (tasks created in a date range) via direct REST.

Usage:
    python3 pyrus_registry.py <form_id> <start_YYYY-MM-DD> <end_YYYY-MM-DD> [out.json]

Auth: reads PYRUS_TOKEN from /opt/data/.env — it is "login:security_key"
(not a Bearer token). Splits on first ':', POSTs /v4/auth, then queries
POST /v4/forms/{id}/register with created_after/created_before.

Output: JSON array of tasks saved to out.json (default /opt/data/pyrus_form_<id>.json),
plus a printed per-day count.
"""
import os
import json
import sys
import urllib.request
import urllib.error
from collections import Counter

API = 'https://api.pyrus.com/v4'


def load_creds():
    with open(os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env")) as f:
        for line in f:
            if line.startswith('PYRUS_TOKEN='):
                return line.split('=', 1)[1].strip().split(':', 1)
    raise SystemExit('PYRUS_TOKEN not found in /opt/data/.env')


def req(url, method='GET', body=None, token=None, timeout=90):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
               'User-Agent': 'pyrus-api-client'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    form_id = int(sys.argv[1])
    start, end = sys.argv[2], sys.argv[3]
    out = sys.argv[4] if len(sys.argv) > 4 else f'/opt/data/pyrus_form_{form_id}.json'

    login, secret = load_creds()
    st, resp = req(f'{API}/auth', 'POST', {'login': login, 'security_key': secret})
    if not resp.get('access_token'):
        print('AUTH FAIL:', st, resp)
        sys.exit(1)
    token = resp['access_token']

    body = {
        'created_after': f'{start}T00:00:00Z',
        'created_before': f'{end}T00:00:00Z',
        'item_count': 2000,
        'include_archived': True,
    }
    st, resp = req(f'{API}/forms/{form_id}/register', 'POST', body, token)
    if st != 200:
        print('REGISTRY FAIL:', st, resp)
        sys.exit(1)
    tasks = resp.get('tasks', [])
    with open(out, 'w') as f:
        json.dump(tasks, f, ensure_ascii=False, default=str, indent=1)
    print(f'saved {len(tasks)} tasks to {out}')
    print('by date:', dict(sorted(Counter(t['create_date'][:10] for t in tasks).items())))


if __name__ == '__main__':
    main()
