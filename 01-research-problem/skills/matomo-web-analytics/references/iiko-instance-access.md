# Корпоративный инстанс iiko — доступ и причуды Reporting API

Проверено 2026-09-03 на https://analytics.iiko.services (Matomo, сайт iiko prod).

## Доступ

- base: `https://analytics.iiko.services/` (API: `/index.php`, POST form)
- idSite = 1 «iiko prod», main_url `https://analytics.iiko.ru`, timezone `Europe/Moscow`
- Токен: `$HERMES_HOME/.env` → `MATOMO_TOKEN_AUTH` (секрет; в config-файлы не класть)
- **Токен принимается ТОЛЬКО POST-параметром формы.** Query-строка и заголовок
  `Authorization: Bearer` отклоняются: `Unable to authenticate ... required to be sent as a POST parameter`.
  Все запросы — `POST /index.php` c `application/x-www-form-urlencoded`, токен в теле.
- urllib: `Request(url, data=urlencode(params).encode())`.

## Что реально включено в инстансе (проверено 2026-09-16)

- Ядро 5.11.0 + TagManager, UserId, CustomDimensions (CD1 «Store ID», action), BotTracking/AIAgents, PagePerformance, Transitions, SegmentEditor, Dashboard, Annotations, ScheduledReports, Marketplace, AI Assistants.
- Premium НЕ куплены: Funnels, CustomReports, MediaAnalytics, HeatmapSessionRecording, AbTesting, FormAnalytics, CrashAnalytics — в меню это промо-страницы `ProfessionalServices.promo*`, а их API отвечает 404 («модуль не найден»). Так же отсутствуют CustomAlerts, ActivityLog, MarketingCampaignsReporting, Cohorts, UsersFlow.
- Диагностика «есть ли плагин»: вызвать любой API-метод модуля — 404 = плагина нет, 400 = модуль есть, но параметры не те. Список страниц для UI: `API.getReportPagesMetadata` (промо-заглушки видны там как `ProfessionalServices.promo*`).
- Настроено: 20 пользователей, 1 дашборд, 4 сегмента (Phone visits, Purchase, user profile, /marketplace/), целей 0, запланированных отчётов 0, аннотаций 0.
- **MTM**: контейнер `I5llzxeu` «Контейнер по умолчанию» (web), версия 2 «0.1.0 — Создано автоматически»: тег «Matomo Аналитика» (pageview), триггер «Просмотр страницы», переменная «Конфигурация Matomo» (`//analytics.iiko.services/`, idSite 1). Ссылок на `mtm.js`/`_mtm` в HTML/бандлах магазина нет → контейнер, похоже, не развёрнут на фронте. У тега Matomo **нет поля User ID** (только Custom Dimensions со «sticky»); user id задаётся Custom HTML-тегом с `_paq.push(['setUserId', …])`.
- Скрипты разведки в `$HERMES_HOME/scripts/`: `matomo_capabilities_probe*.py` (что включено), `mtm_*` (поля тегов MTM), `anon_by_browser.py`, `login_theory_check*.py`, `channel_type_check.py`, `pages_with_users.py`.
- Готовые HTML-отчёты собираются скриптами в `$HERMES_HOME/matomo_weekly/`: `build_pages_userid.py` (страницы × User ID), `build_study_plan.py` (план изучения функционала).

## Причуды метрик

- **`period=range` НЕ отдаёт `nb_uniq_visitors`** (нет ключа). То же: DevicesDetection/Resolution/
  VisitTime-отчёты — уники `null`, только `nb_visits`.
- **`period=week` отдаёт и `nb_uniq_visitors`, и `nb_users`** → недельные уники брать отсюда.
- **`period=day` за диапазон дат возвращает JSON-словарь `{дата: метрики}`**, а не список строк
  (у строк формат был бы `label=дата`). Пустые дни — `[]`/`{}`, пропускать.
- **`Actions.getPageTitles`: в строках нет `nb_uniq_pageviews`.** Цифра «Уникальные просмотры»
  из UI == сумме `nb_visits` по строкам (за день 75 330 при 204 227 hits). При сверке с UI
  говори «просмотры (hits)» vs «уникальные просмотры (=сумма nb_visits)» — разные метрики.
- Доля «Page Name not defined» ~30% pageviews: SPA-экраны без `document.title` — чувствительный
  индикатор качества разметки (см. marketplace-funnel-example про читаемые title).

## Скрипты аудита в `$HERMES_HOME/matomo_weekly/` (2026-09)

Все читают токен из `$HERMES_HOME/.env`, ходят POST-формой, печатают готовый вердикт — запускать вместо
ручных запросов:

- `check_events.py [дней=30] [подстрока]` — категории событий, действия, имена, доля `nb_events_with_value`,
  поиск по `segment=eventCategory=@…`, разбивка по дням.
- `check_events_by_host.py --days 7 <хост> [хост…]` — события по конкретным хостам (сегмент
  `pageUrl=@<хост>`): визиты/действия/события, категории, действия, имена, по дням. Отвечает на вопрос
  «с каких доменов приходят события».
- `check_test_traffic.py [idSite=1] [дней_от=24] [дней_до=0]` — все хосты, похожие на тестовые/dev
  (`localhost:42xx`, `127.0.0.1`, `192.168.*`, `10.*`, `vm-*`, `*.iwr.lan`, `*-demo*`, `*test*`, `:порт`),
  с «первый/последний раз» и разбивкой по дням. Отвечает на «доработку выкатили — тестовые данные
  больше не идут?». Питфол: перебор хостов идёт по полю `url`, а это ОДИН пример хоста на путь —
  список хостов из `getPageUrls` заведомо неполный, поэтому вывод «такого хоста нет» недоказуем;
  положительные находки подтверждать сегментом `pageUrl=@<хост>` (см. SKILL.md → Pitfalls).
- `check_stand_traffic.py <base_url> <token> <подстрока_хоста> [дней]` — то же для чужого инстанса
  Matomo (например, тестового): перечисляет сайты, ищет URL/заголовки/события по подстроке.

Питфол окружения: писать файлы можно только под `$HERMES_HOME` (`HERMES_WRITE_SAFE_ROOT`) — скрипты
класть в `$HERMES_HOME/scripts/` или `$HERMES_HOME/matomo_weekly/`, `/tmp` отклоняется.

## MCP-эндпоинт и почему нужен мост

`/index.php?module=API&method=McpServer.mcp&format=mcp` — настоящий MCP-эндпоинт, но авторизуется
тоже только POST-параметром формы. Стандартный MCP-транспорт (JSON-RPC телом / заголовки / query)
несовместим → любые попытки дают `Authentication required` (проверены все варианты).

Рабочее решение — **локальный stdio MCP-мост**: `$HERMES_HOME/matomo_weekly/mcp_matomo_server.py`
(говорит MCP 2025-03-26 по строкам stdin/stdout, в Matomo ходит POST-form; токен сам читает из
`$HERMES_HOME/.env`; 8 инструментов: matomo_sites / matomo_weekly_snapshot / matomo_totals /
matomo_daily / matomo_devices / matomo_resolutions / matomo_hourly / matomo_raw).
Регистрация: `hermes mcp add matomo --command /usr/bin/python3 --args $HERMES_HOME/matomo_weekly/mcp_matomo_server.py`
(интерактивный запрос «Enable all 8 tools?» → ответить `Y`). Инструменты появляются в НОВЫХ
сессиях; gateway перезапустить для cron (`/command/s6-svc -r /run/service/gateway-default`).

## Еженедельный пайплайн

`$HERMES_HOME/matomo_weekly/`: `fetch_matomo.py` (POST-выгрузка 2 полных недель → data.json),
`dashboard_template.html` + `build_dashboard.py` (статический no-JS рендер → dashboard.html),
`config.json` (base_url + site_id, без токена). Cron `2c3c00bd38fa`, пн 06:00 UTC,
доставка в топик 25 группы Hermes. Скилл процедуры — `matomo-weekly-report`
(он **user-owned**: автономная курация его не правит — улучшения по пайплайну копить здесь).

### Эксплуатация пайплайна (проверено 2026-09-14)

- **`fetch_matomo.py` наружу отдаёт только `api(cfg, method, period, date_str, extra=None)`** —
  все аргументы позиционные, функции `load_config()` нет (config читается внутри `main()`).
  Рабочий вызов произвольного отчёта из скрипта:
  ```python
  import importlib.util, json, sys
  spec = importlib.util.spec_from_file_location('fm', 'fetch_matomo.py')
  fm = importlib.util.module_from_spec(spec); sys.argv = ['fm']; spec.loader.exec_module(fm)
  cfg = json.load(open('config.json'))
  fm.api(cfg, 'SitesManager.getSiteFromId', 'day', '2026-09-13')['timezone']  # Europe/Moscow
  ```
  ⚠️ `SitesManager.getSiteFromId` возвращает **СЛОВАРЬ**, а не список: запись `[0]['timezone']`
  падает с `KeyError: 0` (проверено 2026-09-21). Словарная форма — единственная проверенная:
  оттуда же `keep_url_fragment` (2026-09-21 было значение **2**, ранее отмечали 0 — не полагаться
  на зафиксированное значение, читать заново).
  Токен подставляется сам (env → `$HERMES_HOME/.env` → config.json) и только POST-параметром.
- `data.json` (недельный прогон) = `meta`, `totals`, `days` (14 строк), `devices`, `resolutions`,
  `hourly`, `pages`, **`hourly_by_day`** = `{день недели: [24 значения визитов]}` — именно он нужен
  для «просадок по часам»: чипы просадок в `dashboard.html` строятся по дню × часу, поэтому вывод
  по суммарному часу легко противоречит картинке.
- Имя вложения: считать `D=$(date -d yesterday +%F)` (воскресенье W1) и копировать
  `dashboard.html → reports/matomo_weekly_$D.html`. Правило пользователя «дата в имени файла»
  важнее дословного текста крон-инструкции (`MEDIA:.../dashboard.html`) — в чат уходит датированная
  копия, а `dashboard.html` остаётся каноническим рабочим файлом. Копию сверять `cmp` (размер,
  который печатает `build_dashboard.py`, и `ls` сразу после сборки могут отставать от итогового файла).
- После сборки открыть `file://$HERMES_HOME/matomo_weekly/dashboard.html` и проверить консоль
  (`js_errors=0`): текст инсайтов вшит статически, поэтому в Telegram-предпросмотре без JS виден,
  а графики — нет; в сообщении инсайты должны быть самодостаточными (цифры + вывод), без опоры на картинку.
- **Проверка `#dip-chips` в браузере обманчива**: статически в HTML лежат строки по всем 7 дням,
  но JS страницы при загрузке перезаписывает `innerHTML` контейнера представлением для выбранного
  в `#hour-day-seg` дня (по умолчанию Пн). Если смотреть `outerHTML`/snapshot в браузере, видно
  один день, и легко решить, что остальные просадки потерялись. Проверять двумя способами:
  `document.querySelectorAll('.insight li')` для инсайтов и **чтение самого файла** (region
  `<!--BLOCK:dips-->`) для чипов; либо отключить JS. Реальная просадка 2026-09-21 была именно
  в статическом HTML (4 дня), а в браузере показывался только Пн.
- **Ступенька ≠ тренд: искать шаг в один день.** Недельные −16,8% у модуля легко принять за «уход
  пользователей», хотя это шаг: у till-shifts 14.09 было 8 233 визита/день (уровень W2), а с 15.09
  — 7 065 и стабильно 6,6–6,9 тыс. Одновременно в тот же день вверх шагнули forecast (1 354 → 2 566),
  lite-stock, inventory, configuration, «Справочники», «Планы подготовки», workflow-config,
  marketplace, abc-xyz. Синхронный шаг в один день по многим модулям = релиз/раскатка или изменение
  разметки; это надо называть гипотезой и просить команду сверить выкатку, а не подавать как рост.
  Готовый разбор: `scripts/detect_module_steps.py` (снимает 14 дней × модули, гасит эффект «понедельника
  после отчётного дня» сравнением Вт–Вс и печатает ряды по выбившимся модулям).
