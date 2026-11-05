# Reporting API quirks — iiko Matomo (analytics.iiko.services), verified 2026-09

Instance: `https://analytics.iiko.services/`, idSite **1 «iiko prod»** (main_url analytics.iiko.ru, tz Europe/Moscow).
Token lives in `$HERMES_HOME/.env` as `MATOMO_TOKEN_AUTH` (file chmod 600). Never put it in config.yaml / URLs.

## Auth: POST-form only

The instance refuses `token_auth` in GET query, Bearer header, X-Auth-Token, custom `token_auth` header,
and JSON-body members — every variant returns "Unable to authenticate… required to be sent as a POST
parameter" (core API) or JSON-RPC `-32600 Authentication required` (MCP plugin). Working call pattern:

```python
params = {"module":"API","method":m,"idSite":1,"period":p,"date":d,"format":"JSON","filter_limit":"-1","token_auth":TOKEN}
req = urllib.request.Request(base + "/index.php", data=urllib.parse.urlencode(params).encode(),
                             headers={"User-Agent":"hermes-matomo/1.0"})
json.load(urllib.request.urlopen(req, timeout=60))
```

## Periods and uniques

- `VisitsSummary.get period=range` → NO `nb_uniq_visitors` key at all.
- `VisitsSummary.get period=week date=<week-start>` → full set incl. `nb_uniq_visitors`, `nb_users` (user_id uniques).
- DevicesDetection/Resolution/VisitTime per week → `nb_uniq_visitors` null → use `nb_visits` and say so.
- `period=day date=start,end` → either list or dict `{date: metrics}`; empty days appear as `[]`/`{}`.
- Day with literally zero data can be absent from the response entirely (2026-08-17 was missing → 13 rows, not 14).

## Tracking-start partial weeks

Full tracking began 2026-08-20 (Aug 17 empty, 18–19 single-digit visits). Comparing an incomplete week to a
full one inflates WoW ~2x. Rules refined by the first clean-pair report (2026-09-03, W1 24–30.08 vs W2 17–23.08):

1. **Day-pairs** only for weekdays with full tracking in BOTH weeks. In the rollout case that was Пт/Сб/Вс
   (Чт 20.08 excluded — launch day may itself be partial; check: if a day's visits sit far below its own
   week's neighbours, treat it as suspect).
2. **Don't compare "7-day average of W1 vs 4-day average of W2"** — that mixes weekday composition
   (weekend days are ~25% quieter) and understates W2. Instead sum/compare the IDENTICAL weekday set in both
   weeks (e.g. Σ Пт–Вс: 96 017 vs 86 466 = +11.0%). This is the honest WoW figure when one week is partial.
3. **Device/resolution share shifts need their own matched-range fetch** — whole-week shares are confounded
   (weekdays desktop-heavier: adding Mon–Wed to Fri–Sun raised Desktop share 49.3%→53.7% in W1). Fetch both
   weeks over identical day-ranges:
   `DevicesDetection.getType period=range date=2026-08-28,2026-08-30` vs `date=2026-08-21,2026-08-23`
   → Desktop 47.8%→49.3%, Smartphone 49.0%→47.4% (this refuted an earlier "mobile trend" guess made from
   whole-week shares). Same rule applies to Resolution.getResolution shares.
4. Site tz check: `SitesManager.getSiteFromId` returns `timezone` (iiko prod = Europe/Moscow → hourly
   VisitTime data is already MSK; no conversion before interpreting "working day").

## Remote MCP endpoint → local stdio bridge

`.../index.php?module=API&method=McpServer.mcp&format=mcp` answers JSON-RPC but authenticates ONLY via
POST form param — standard MCP clients (Hermes included) send JSON bodies/headers, so it can never
authenticate. Fix: run a **local stdio MCP bridge** that speaks MCP on stdin/stdout and calls the Reporting
API via POST form. Working implementation: `$HERMES_HOME/matomo_weekly/mcp_matomo_server.py`
(8 tools: matomo_sites / matomo_weekly_snapshot / matomo_totals / matomo_daily / matomo_devices /
matomo_resolutions / matomo_hourly / matomo_raw). Register:

```bash
printf 'Y\n' | hermes mcp add matomo --command /usr/bin/python3 --args $HERMES_HOME/matomo_weekly/mcp_matomo_server.py
/command/s6-svc -r /run/service/gateway-default   # new sessions (cron/TG) pick it up
```

MCP servers register per-session: THIS session keeps old tools; new sessions get `mcp__matomo__*`.
Self-test without Hermes: pipe `initialize` / `tools/list` / `tools/call` JSON lines into the script.

## Page rows (Actions.getPageUrls) semantics

`nb_visits` on a page row = visits in which that page was opened at least once. A visit that opens several
pages is counted in EVERY matching row, so Σ over rows can exceed the week's total visits (top-5 rows summed
to 305k vs 242k visits). Never present page rows as shares of a total; phrase as "% of visits that included
page X" (e.g. /navigator in 48% of visits). `nb_hits` = raw pageviews; per-row `nb_uniq_visitors` needs a
segment query (`VisitsSummary.get` + `segment=pageUrl=@<path>`, one call per row).

## Page titles

`Actions.getPageTitles` period=day: rows carry `nb_hits` etc.; don't assume `nb_uniq_pageviews` is present.
Reads as data-quality: "Page Name not defined" = SPA routes without document.title (~30% of hits);
module-level titles (Purchase / Till shifts / Inventory) collapse many routes into one row.

## Restaurant × module data model (flat vs hierarchy) — ИСПРАВЛЕНО 2026-09-21

One idSite aggregates ALL restaurants, НО `Actions.getPageUrls` НЕ разбивает строки по поддоменам:
строки — уровня ПУТИ, агрегированные по всем ресторанам (~185 путей за день, ~106 за неделю;
пример URL одного ресторана лежит в поле `url`). Замер 16.09: flat и non-flat дают одинаковые
Σ визитов (75 092) и Σ хитов (208 870); строка `/navigator/index.html` = 18 534 визита, сегмент
`pageUrl=@/navigator` = 17 317, а сегмент по хосту `pageUrl=@sedelice-co.iikoweb.ru` = 511.
Прежний вывод «~200 строк = host×module» был ошибкой чтения (200 = столько путей с трафиком).

- `flat=1` меняет только ФОРМУ: плоский список путей (`label` = `/navigator/index.html`, с ведущим `/`, + поле `url` с примером хоста). Явной ошибки в цифрах не даёт, но и разбивки по ресторанам не даёт.
- **Без `flat`** верхний уровень — дерево модулей, labels БЕЗ ведущего `/`
  (`navigator`, `purchase`, `till-shifts`…), агрегировано по всем ресторанам. Узлы несут int
  `idsubdatatable` и НЕ несут уников.
- Разбивка по хосту/ресторану — **только сегментом**: `segment=pageUrl=@<host>` (+ `VisitsSummary.get`/`Actions.*`). Перечислить хосты через `getPageUrls` нельзя (в поле `url` — один пример на путь, ~59 хостов в день). Негативные выводы («домена X нет») через `getPageUrls` недоказуемы.
- Module uniques + devices: one `VisitsSummary.get` + one `DevicesDetection.getType`, both with
  `segment=pageUrl=@/<module>` (daily job does this for every module row, ~30–60 calls — fine).
- Exact-page segments use `pageUrl==` + the FULL URL from the row's `url` field (path-only `==` never matches).
- Utility rows that really exist in data: `Page URL not defined`, `/`, `localhost:4200` (dev) — don't filter them out silently; mention in insights if relevant.
