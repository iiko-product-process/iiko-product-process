#!/usr/bin/env python3
"""
Локальный stdio-MCP-мост Hermes ↔ Matomo Reporting API.

Зачем мост: MCP-эндпоинт Matomo (?module=API&method=McpServer.mcp) принимает token_auth
ТОЛЬКО POST-параметром формы, что несовместимо со стандартным MCP-транспортом. Поэтому здесь
MCP-сервер на stdio (JSON-RPC построчно), а в Matomo запросы идут POST-form.

Конфигурация (в порядке приоритета):
  1) переменные окружения: MATOMO_URL, MATOMO_SITE_ID, MATOMO_TOKEN_AUTH
  2) файл matomo-mcp.config.json рядом со скриптом: {"base_url": "...", "site_id": 1, "token_auth": "..."}
  3) .env-файл: путь из MATOMO_ENV_FILE, иначе ~/.hermes/.env, иначе /opt/data/.env
     (строка вида MATOMO_TOKEN_AUTH=xxxx)

Запуск как MCP:
    hermes mcp add matomo --command /usr/bin/python3 --args <путь>/mcp_matomo_server.py
Проверка без Hermes:
    python3 mcp_matomo_server.py --selftest
Ручной JSON-RPC тест:
    echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' | python3 mcp_matomo_server.py
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _cfg_file():
    p = HERE / "matomo-mcp.config.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _env_token_from_file():
    paths = []
    if os.environ.get("MATOMO_ENV_FILE"):
        paths.append(Path(os.environ["MATOMO_ENV_FILE"]))
    paths += [Path.home() / ".hermes" / ".env", Path("/opt/data/.env")]
    for p in paths:
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("MATOMO_TOKEN_AUTH="):
                    return line.strip().split("=", 1)[1]
        except Exception:
            continue
    return ""


CFG = _cfg_file()
BASE_URL = (os.environ.get("MATOMO_URL") or CFG.get("base_url") or "").rstrip("/")
SITE_ID = os.environ.get("MATOMO_SITE_ID") or CFG.get("site_id") or 1
TOKEN = os.environ.get("MATOMO_TOKEN_AUTH") or CFG.get("token_auth") or _env_token_from_file()


def api(method, period="day", date_str="today", extra=None):
    if not BASE_URL or not TOKEN:
        raise RuntimeError(
            "Matomo не сконфигурирован: задайте MATOMO_URL и MATOMO_TOKEN_AUTH "
            "(env, matomo-mcp.config.json рядом со скриптом или .env-файл)"
        )
    params = {"module": "API", "method": method, "idSite": SITE_ID,
              "period": period, "date": date_str, "format": "JSON", "filter_limit": "-1"}
    if extra:
        params.update(extra)
    params["token_auth"] = TOKEN  # только POST-параметром!
    req = urllib.request.Request(BASE_URL + "/index.php",
                                 data=urllib.parse.urlencode(params).encode(),
                                 headers={"User-Agent": "hermes-matomo-mcp/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def prev_full_weeks():
    today = date.today()
    this_m = today - timedelta(days=today.weekday())
    w1e = this_m - timedelta(days=1)
    w1s = w1e - timedelta(days=6)
    w2e = w1s - timedelta(days=1)
    w2s = w2e - timedelta(days=6)
    return (w1s.isoformat(), w1e.isoformat()), (w2s.isoformat(), w2e.isoformat())


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def norm_rows(rows):
    if isinstance(rows, list):
        return rows
    if isinstance(rows, dict):
        out = []
        for k, v in rows.items():
            if isinstance(v, dict) and v:
                r = dict(v)
                r.setdefault("label", k)
                out.append(r)
        return out
    return []


def clean(r):
    if isinstance(r, list):
        return [clean(x) for x in r]
    if isinstance(r, dict):
        return {k: (clean(v) if isinstance(v, (dict, list))
                    else (num(v) if isinstance(v, str) and v.replace(".", "", 1).isdigit() else v))
                for k, v in r.items() if k != "idsubdatatable"}
    return r


TOOLS = [
    {"name": "matomo_sites", "description": "Список сайтов Matomo (id/название/url/таймзона)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "matomo_totals", "description": "Сводка VisitsSummary за период: визиты, уникальные посетители, пользователи, действия, отказы, время",
     "inputSchema": {"type": "object", "properties": {"period": {"type": "string", "description": "day|week|month|range"},
                                                      "date": {"type": "string", "description": "'today'/'yesterday', дата или 'start,end'"}}}},
    {"name": "matomo_daily", "description": "Визиты/уники/пользователи по дням за диапазон 'start,end'",
     "inputSchema": {"type": "object", "properties": {"date": {"type": "string"}}}},
    {"name": "matomo_devices", "description": "Типы устройств (Desktop/Smartphone/Tablet/...) за период",
     "inputSchema": {"type": "object", "properties": {"period": {"type": "string"}, "date": {"type": "string"}}}},
    {"name": "matomo_resolutions", "description": "Разрешения экранов за период",
     "inputSchema": {"type": "object", "properties": {"period": {"type": "string"}, "date": {"type": "string"}}}},
    {"name": "matomo_hourly", "description": "Почасовая активность (по серверному времени инстанса)",
     "inputSchema": {"type": "object", "properties": {"period": {"type": "string"}, "date": {"type": "string"}}}},
    {"name": "matomo_pages", "description": "Страницы: топ URL за период (flat=1 — листовые URL с хостом; segment — фильтр, напр. pageUrl=@/navigator)",
     "inputSchema": {"type": "object", "properties": {"period": {"type": "string"}, "date": {"type": "string"},
                                                      "segment": {"type": "string"}, "flat": {"type": "boolean"},
                                                      "limit": {"type": "integer"}}}},
    {"name": "matomo_events", "description": "События: категории/действия/имена (what: category|action|name) за период",
     "inputSchema": {"type": "object", "properties": {"what": {"type": "string"},
                                                      "period": {"type": "string"}, "date": {"type": "string"},
                                                      "segment": {"type": "string"}}}},
    {"name": "matomo_raw", "description": "Произвольный вызов Reporting API: method + period/date/extra (segment, flat, showColumns, filter_limit и т.д.)",
     "inputSchema": {"type": "object", "properties": {"method": {"type": "string"}, "period": {"type": "string"},
                                                      "date": {"type": "string"}, "extra": {"type": "object"}},
                     "required": ["method"]}},
]


def call_tool(name, args):
    a = args or {}
    period = a.get("period", "day")
    date_s = a.get("date", "today")
    if name == "matomo_sites":
        # при заданном idSite Matomo отдаёт словарь {idsite: {...}}, без него — список
        return clean(norm_rows(api("SitesManager.getAllSites")))
    if name == "matomo_totals":
        return clean(api("VisitsSummary.get", period, date_s))
    if name == "matomo_daily":
        return clean(norm_rows(api("VisitsSummary.get", "day", date_s)))
    if name == "matomo_devices":
        return clean(norm_rows(api("DevicesDetection.getType", period, date_s)))
    if name == "matomo_resolutions":
        return clean(norm_rows(api("Resolution.getResolution", period, date_s)))
    if name == "matomo_hourly":
        return clean(norm_rows(api("VisitTime.getVisitInformationPerServerTime", period, date_s)))
    if name == "matomo_pages":
        extra = {"flat": 1 if a.get("flat", True) else 0,
                 "showColumns": "label,nb_visits,nb_uniq_visitors,nb_hits"}
        if a.get("segment"):
            extra["segment"] = a["segment"]
        if a.get("limit"):
            extra["filter_limit"] = a["limit"]
        return clean(norm_rows(api("Actions.getPageUrls", period, date_s, extra)))
    if name == "matomo_events":
        what = (a.get("what") or "category").lower()
        meth = {"category": "Events.getCategory", "action": "Events.getAction", "name": "Events.getName"}.get(what)
        if not meth:
            return {"error": "what должен быть category|action|name"}
        extra = {"segment": a["segment"]} if a.get("segment") else None
        return clean(norm_rows(api(meth, period, date_s, extra)))
    if name == "matomo_raw":
        return clean(api(a["method"], period, date_s, a.get("extra")))
    return {"error": "unknown tool " + name}


def handle(msg):
    mid = msg.get("id")
    method = msg.get("method")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
            "serverInfo": {"name": "matomo-bridge", "version": "1.1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        p = msg.get("params", {})
        try:
            res = call_tool(p.get("name", ""), p.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": mid,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": str(e)}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}


def selftest():
    print(f"base_url={BASE_URL or '(не задан)'} | idSite={SITE_ID} | token={'задан' if TOKEN else 'НЕ задан'}")
    if not BASE_URL or not TOKEN:
        print("ОШИБКА: задайте MATOMO_URL и MATOMO_TOKEN_AUTH (env, matomo-mcp.config.json или .env)")
        return 1
    try:
        ver = api("API.getMatomoVersion").get("value")
        print("Matomo version:", ver)
        sites = norm_rows(api("SitesManager.getAllSites"))
        for s in sites:
            print(f"  [{s.get('idsite')}] {s.get('name')} — {s.get('main_url')} (tz={s.get('timezone')})")
        tot = api("VisitsSummary.get", "day", "yesterday")
        print("Вчера:", {k: tot.get(k) for k in ("nb_visits", "nb_uniq_visitors", "nb_users", "nb_actions")})
        tools = [t["name"] for t in TOOLS]
        print(f"MCP-инструментов: {len(tools)} — {', '.join(tools)}")
        return 0
    except Exception as e:
        print("ОШИБКА вызова API:", e)
        print("Проверьте: URL инстанса, idSite, токен (только POST), права токена (view).")
        return 2


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if not TOKEN:
        sys.stderr.write("MATOMO_TOKEN_AUTH не найден (env / matomo-mcp.config.json / .env)\n")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        out = handle(msg)
        if out is None:
            continue
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
