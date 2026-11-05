#!/usr/bin/env python3
"""
Древовидная структура разделов сайта (разделы → подроуты → страницы) с метриками.

Использование:
    python3 pages_tree.py --site 1 --date 2026-09-22,2026-09-28
    python3 pages_tree.py --date yesterday --sections purchase,employees --depth 3
    python3 pages_tree.py --date 2026-09-22,2026-09-28 --sort uniq --limit 40

Что делает: берёт Actions.getPageUrls (flat=1, все строки), собирает из путей дерево
(узел = сегмент пути), суммирует визиты/уникальных/просмотры по ветвям и печатает
дерево с отступами — готово для вставки в сообщение cron-джобы (моноширинный блок).

Конфиг Matomo: как в mcp_matomo_server.py (env MATOMO_URL/MATOMO_SITE_ID/MATOMO_TOKEN_AUTH,
matomo-mcp.config.json рядом со скриптом или .env-файл).
"""
import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _cfg():
    p = HERE.parent / "scripts" / "matomo-mcp.config.json"
    if not p.exists():
        p = HERE / "matomo-mcp.config.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _token_from_env_file():
    for p in [Path(os.environ.get("MATOMO_ENV_FILE", "")) if os.environ.get("MATOMO_ENV_FILE") else None,
              Path.home() / ".hermes" / ".env", Path("/opt/data/.env")]:
        if not p:
            continue
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("MATOMO_TOKEN_AUTH="):
                    return line.strip().split("=", 1)[1]
        except Exception:
            continue
    return ""


CFG = _cfg()
BASE_URL = (os.environ.get("MATOMO_URL") or CFG.get("base_url") or "").rstrip("/")
TOKEN = os.environ.get("MATOMO_TOKEN_AUTH") or CFG.get("token_auth") or _token_from_env_file()


def api(site, method, **params):
    p = {"module": "API", "method": method, "idSite": site, "format": "JSON",
         "filter_limit": -1, "token_auth": TOKEN}
    p.update(params)
    req = urllib.request.Request(BASE_URL + "/index.php",
                                 data=urllib.parse.urlencode(p).encode(),
                                 headers={"User-Agent": "hermes-pages-tree/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read().decode())


def build_tree(rows, keep_sections=None):
    root = {}
    for r in rows:
        label = str(r.get("label") or "")
        if not label.startswith("/") or label.endswith("not defined") or "не определено" in label:
            continue
        parts = [p for p in label.split("/") if p]
        if not parts:
            continue
        if keep_sections and parts[0] not in keep_sections:
            continue
        level = root
        v = int(r.get("nb_visits") or 0)
        u = int(r.get("nb_uniq_visitors") or r.get("sum_daily_nb_uniq_visitors") or 0)
        h = int(r.get("nb_hits") or 0)
        for i, seg in enumerate(parts):
            node = level.setdefault(seg, {"v": 0, "u": 0, "h": 0, "kids": {}, "leaf": False})
            node["v"] += v
            node["u"] += u
            node["h"] += h
            if i == len(parts) - 1:
                node["leaf"] = True
            level = node["kids"]
    return root


def render(node, key, depth, max_depth, limit, sort_key, prefix="", is_last=True, out=None):
    kids = sorted(node["kids"].items(), key=lambda kv: -kv[1][sort_key])[:limit]
    mark = "" if depth == 0 else ("└── " if is_last else "├── ")
    label = (f"/{key}" if depth == 0 else key)
    out.append(f"{prefix}{mark}{label}  visits={node['v']} uniq={node['u']} hits={node['h']}")
    child_prefix = prefix + ("" if depth == 0 else ("    " if is_last else "│   "))
    if depth + 1 >= max_depth:
        rest = len(node["kids"]) - len(kids)
        if rest > 0:
            out.append(f"{child_prefix}└── … ещё {rest} веток")
        return
    for i, (k, v) in enumerate(kids):
        render(v, k, depth + 1, max_depth, limit, sort_key, child_prefix, i == len(kids) - 1, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=os.environ.get("MATOMO_SITE_ID") or CFG.get("site_id") or 1)
    ap.add_argument("--date", default="yesterday", help="'yesterday' | '2026-09-22,2026-09-28' | 'today'")
    ap.add_argument("--period", default="range" if "," in os.environ.get("_", "") else "day")
    ap.add_argument("--sections", default="", help="список разделов через запятую (первый сегмент пути)")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--limit", type=int, default=15, help="сколько дочерних веток показывать на уровень")
    ap.add_argument("--sort", default="v", choices=["v", "u", "h"], help="v=визиты, u=уникальные, h=просмотры")
    ap.add_argument("--json", action="store_true", help="вывести дерево в JSON вместо текста")
    a = ap.parse_args()

    period = a.period
    if "," in a.date:
        period = "range"
    rows = api(a.site, "Actions.getPageUrls", period=period, date=a.date, flat=1,
               showColumns="label,nb_visits,nb_uniq_visitors,nb_hits,sum_daily_nb_uniq_visitors")
    if not isinstance(rows, list):
        print("Ошибка API:", json.dumps(rows, ensure_ascii=False)[:300])
        return 1
    keep = [s.strip().strip("/") for s in a.sections.split(",") if s.strip()] or None
    tree = build_tree(rows, keep)
    if a.json:
        print(json.dumps(tree, ensure_ascii=False, indent=1))
        return 0
    print(f"# Дерево разделов · сайт {a.site} · {period} {a.date} "
          f"· сортировка по {'визитам' if a.sort == 'v' else ('уникальным' if a.sort == 'u' else 'просмотрам')}")
    if period == "range":
        print("# uniq — сумма дневных уникальных (Matomo не отдаёт уникальных за диапазон)")
    out = []
    for k, v in sorted(tree.items(), key=lambda kv: -kv[1][a.sort]):
        render(v, k, 0, a.depth, a.limit, a.sort, out=out)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
