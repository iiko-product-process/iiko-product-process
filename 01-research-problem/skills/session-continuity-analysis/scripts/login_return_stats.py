#!/usr/bin/env python3
"""Разлогины и возврат на экран по журналу визитов.

Вход: JSONL, по строке на визит: {"u": "<user_id>", "s": [["/route", 1], ...]}
(второй элемент пары — число действий, можно опустить).

Пример:
  python login_return_stats.py visits.jsonl --login /navigator/auth/login --home /navigator/home
"""
import argparse
import collections
import json
import sys


def module(route):
    return route.strip("/").split("/")[0] if route else None


def load(path, login):
    events = []
    users = collections.defaultdict(list)
    visits = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            visits += 1
            obj = json.loads(line)
            uid = str(obj.get("u", ""))
            screens = []
            for item in obj.get("s", []):
                route = item[0] if isinstance(item, (list, tuple)) else item
                if screens and screens[-1] == route:
                    continue
                screens.append(route)
            for i, route in enumerate(screens):
                if route != login:
                    continue
                prev = screens[i - 1] if i > 0 else None
                nxt = screens[i + 1] if i + 1 < len(screens) else None
                events.append((uid, prev, nxt))
                users[uid].append((prev, nxt))
    return visits, events, users


def event_stats(ev, home):
    n = len(ev)
    home_n = sum(1 for _, p, x in ev if x == home)
    same = sum(1 for _, p, x in ev if x == p)
    same_mod = sum(1 for _, p, x in ev if x and p and module(x) == module(p))
    return {
        "events": n,
        "home": home_n,
        "home_%": round(100 * home_n / n, 1) if n else 0,
        "same_screen": same,
        "same_screen_%": round(100 * same / n, 1) if n else 0,
        "same_module": same_mod,
        "same_module_other_%": round(100 * (same_mod - same) / n, 1) if n else 0,
        "other_module": n - home_n - same_mod,
        "other_module_%": round(100 * (n - home_n - same_mod) / n, 1) if n else 0,
    }


def user_stats(users, home, login, exclude_home=True):
    rows = {}
    for uid, evs in users.items():
        evs = [(p, x) for p, x in evs if p and p != login and x and (not exclude_home or p != home)]
        if evs:
            rows[uid] = evs
    n = len(rows)
    first_home = sum(1 for evs in rows.values() if evs[0][1] == home)
    any_home = sum(1 for evs in rows.values() if any(x == home for _, x in evs))
    never_same = sum(1 for evs in rows.values() if not any(x == p for p, x in evs))
    never_mod = sum(1 for evs in rows.values() if not any(module(x) == module(p) for p, x in evs))
    return {
        "users": n,
        "first_home": first_home,
        "first_home_%": round(100 * first_home / n, 1) if n else 0,
        "any_home": any_home,
        "any_home_%": round(100 * any_home / n, 1) if n else 0,
        "never_same_screen": never_same,
        "never_same_screen_%": round(100 * never_same / n, 1) if n else 0,
        "never_same_module": never_mod,
        "never_same_module_%": round(100 * never_mod / n, 1) if n else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("visits")
    ap.add_argument("--login", default="/navigator/auth/login")
    ap.add_argument("--home", default="/navigator/home")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    visits, events, users = load(args.visits, args.login)
    logout = [e for e in events if e[1] and e[1] != args.login]
    both = [e for e in logout if e[2]]
    nonhome = [e for e in both if e[1] != args.home]
    out = {
        "visits": visits,
        "login_events": len(events),
        "logout_events": len(logout),
        "logout_with_next": len(both),
        "logout_nonhome_with_next": len(nonhome),
        "events": event_stats(nonhome, args.home),
        "users": user_stats(users, args.home, args.login),
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print(f"визитов: {visits}")
    print(f"событий логина: {len(events)}; разлогинов: {len(logout)}; с next: {len(both)}; не с главной: {len(nonhome)}")
    e = out["events"]
    print(f"по событиям: home {e['home_%']}% · same screen {e['same_screen_%']}% · same module/other {e['same_module_other_%']}% · other module {e['other_module_%']}%")
    u = out["users"]
    print(f"по пользователям: first home {u['first_home_%']}% · any home {u['any_home_%']}% · never same screen {u['never_same_screen_%']}% · never same module {u['never_same_module_%']}%")


if __name__ == "__main__":
    sys.exit(main())
