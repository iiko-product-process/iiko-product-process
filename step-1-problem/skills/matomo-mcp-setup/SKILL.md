---
name: matomo-mcp-setup
description: "Use when connecting Hermes to Matomo (MCP bridge setup)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [matomo, mcp, setup, onboarding, analytics, api]
    category: research
---

# Подключение Hermes к Matomo (MCP-мост)

Разворачивает доступ агента Hermes к Reporting API Matomo через локальный stdio-MCP-сервер.
Скилл самодостаточный: можно передать коллеге, у которого есть свой Hermes и доступ к Matomo.

## Когда использовать

- Нужно, чтобы агент читал данные Matomo (визиты, пользователи, страницы, события, каналы) инструментами MCP.
- Настройка на новой машине/у нового сотрудника.
- Диагностика: «инструменты matomo не появились», «Authentication required», пустые ответы.

## Что понадобится (5 минут)

1. **URL инстанса Matomo** — например `https://analytics.example.com/`.
2. **idSite** (номер сайта; видно в URL или через `SitesManager.getAllSites`). Обычно `1`.
3. **Токен (token_auth)** с правом **view** (для чтения) или **write/admin** (если агент будет создавать цели, сегменты, отчёты). Где взять:
   - Личный токен: Администрирование → Personal → Security → *Create new token* (свой токен = свои права, отзывается без последствий для других).
   - Либо попросить у админа инстанса «токен для чтения отчётов».
   Токен **нельзя** коммитить в git и нельзя класть внутрь скилла/скрипта.

## Шаги установки

```bash
# 1. Куда положить мост (любой путь; ниже — рекомендуемый)
mkdir -p ~/.hermes/scripts
cp <путь_скилла>/scripts/mcp_matomo_server.py ~/.hermes/scripts/

# 2. Настройки — через переменные окружения Hermes (лежат в конфиге/профиле)
#    MATOMO_URL=https://analytics.example.com/
#    MATOMO_SITE_ID=1
#    MATOMO_TOKEN_AUTH=<токен>
#    (можно положить в файл ~/.hermes/.env в виде строк MATOMO_TOKEN_AUTH=... — мост его прочитает)

# 3. Проверка без Hermes (самодиагностика моста)
python3 ~/.hermes/scripts/mcp_matomo_server.py --selftest

# 4. Регистрация в Hermes (тот же вызов, что и в конфиге: mcp_servers.matomo)
hermes mcp add matomo --command /usr/bin/python3 --args ~/.hermes/scripts/mcp_matomo_server.py
#    На вопрос «Enable all N tools?» ответить Y.
#    Вручную то же самое в конфиге:
#      mcp_servers:
#        matomo:
#          command: /usr/bin/python3
#          args:
#            - /home/<user>/.hermes/scripts/mcp_matomo_server.py
#          enabled: true

# 5. Перезапустить процесс Hermes (инструменты MCP подхватываются только на старте)
```

## Проверка, что всё работает

1. `--selftest` печатает версию Matomo и список сайтов — значит URL и токен верны.
2. В новой сессии Hermes вызвать инструмент `matomo_sites` → должен вернуться список сайтов.
3. `matomo_totals` с `period=day, date=yesterday` → визиты/уники/пользователи за вчера.

Если инструменты не видны — процесс Hermes не перезапускался (см. ниже).

## Что даёт мост (инструменты)

| Инструмент | Что возвращает |
|---|---|
| `matomo_sites` | список сайтов (id, название, url, таймзона) |
| `matomo_totals` | `VisitsSummary.get` за период: визиты, уникальные посетители, **пользователи**, действия, время, отказы |
| `matomo_daily` | разбивка по дням за диапазон `start,end` |
| `matomo_devices` | типы устройств (Desktop/Smartphone/Tablet…) |
| `matomo_resolutions` | разрешения экранов |
| `matomo_hourly` | почасовая активность (по серверному времени инстанса) |
| `matomo_pages` | топ страниц (`flat=1` — листовые URL, `segment` — фильтр, напр. `pageUrl=@/navigator`) |
| `matomo_events` | события: `what=category|action|name`, с опциональным `segment` |
| `matomo_raw` | произвольный вызов Reporting API: `method` + `period`/`date`/`extra` (сегменты, `flat=1`, `showColumns` и т.д.) |

Через `matomo_raw` доступно всё остальное API: `Actions.getPageUrls`, `Events.getCategory/getAction/getName`,
`Referrers.getChannelType`, `UserId.getUsers`, `Goals.get`, `Live.getLastVisitsDetails` и т.п.
Недельные срезы — `matomo_totals` с `period=week` и датой начала недели (в этом периоде `nb_uniq_visitors` и `nb_users` отдаются).

## Подводные камни (проверено на практике)

1. **Токен только POST-параметром формы.** Некоторые инстансы (в т.ч. iiko) отклоняют `token_auth` в query-строке и в заголовке: `Unable to authenticate ... required to be sent as a POST parameter`. В мосте это уже учтено — все запросы идут `POST /index.php` с `application/x-www-form-urlencoded`.
2. **Удалённый MCP-эндпоинт Matomo (`?module=API&method=McpServer.mcp`) не подходит**: он авторизуется только POST-параметром, а стандартный MCP-транспорт шлёт токен иначе → всегда `Authentication required`. Поэтому используется локальный stdio-мост.
3. **Инструменты MCP грузятся только при старте процесса** Hermes. После добавления/правок сервера — перезапуск (в Docker/s6: рестарт сервиса; в десктопе — перезапуск приложения).
4. **`hermes mcp login`** (OAuth-серверы) падает на коллизии callback-порта — не относится к этому мосту, но не путайте.
5. **Пустой ответ вместо данных**: чаще всего неверный `idSite`, период в будущем или сегмент. Диагностика — `matomo_raw` с `method=API.getReportMetadata` и `method=SitesManager.getAllSites`.
6. **HTTP 404 на методе** = плагин/модуль не установлен (в Matomo 5 премиум-плагины отвечают именно так); **400** = модуль есть, неверные параметры.
7. **Уникальные метрики**: `nb_uniq_visitors` есть в дневных и недельных отчётах, но **отсутствует в `period=range`** (там — `sum_daily_nb_uniq_visitors`, сумма дневных, завышает). `Actions.getPageUrls` без `flat=1` = разделы (агрегация по всем доменам), с `flat=1` = листовые URL.
8. **Токен в открытом виде**: держите его в env/`.env`, не в скрипте и не в конфиге скилла.

## Проверка на конкретном инстансе (пример iiko)

- base: `https://analytics.iiko.services/`, idSite=1 «iiko prod», tz Europe/Moscow.
- Токен лежит в `/opt/data/.env` (`MATOMO_TOKEN_AUTH`), мост — `/opt/data/matomo_weekly/mcp_matomo_server.py`, регистрация — блок `mcp_servers.matomo` в `/opt/data/config.yaml`.
- Детали инстанса и его квирки: скилл `matomo-web-analytics` → `references/iiko-instance-access.md`, `references/matomo-api-quirks.md`.

## Еженедельная cron-джоба по разделам сотрудника (предложить после настройки)

После подключения сразу предложите поставить регулярный отчёт — по образцу рабочего недельного отчёта
(две последние полные недели Пн–Вс, сравнение WoW + день-к-дню, аналитическое сообщение + вложение).

**1. Спросите у сотрудника:**
- **по каким разделам собирать** (список модулей/экранов, за которые он отвечает). Подсказать варианты можно так:
  - `matomo_pages` с `flat=false` — верхнеуровневые разделы сайта;
  - `python3 <скилл>/scripts/pages_tree.py --date <последняя_полная_неделя> --depth 1 --limit 50` — все разделы с визитами/униками;
- **куда доставлять** (Telegram-чат/топик, e-mail, или просто в текущий чат);
- **когда** (день и время; по умолчанию — понедельник утром, когда неделя уже закрыта).

**2. Проверьте перед созданием:** `MATOMO_URL`/`MATOMO_TOKEN_AUTH` доступны процессу, `pages_tree.py` печатает дерево по выбранным разделам:
`python3 <скилл>/scripts/pages_tree.py --date <W2start>,<W1end> --sections <разделы> --depth 3 --limit 10`.

**3. Создайте джобу** (пример: понедельник 06:00 UTC = 09:00 МСК; подставьте нужные чат и разделы):

```
cronjob(action="create",
        name="Matomo · недельный отчёт по разделам",
        schedule="0 6 * * 1",
        skills=["matomo-mcp-setup"],
        deliver="telegram:<chat_id>:<thread_id>",
        enabled_toolsets=["terminal", "file"],
        prompt="<текст из templates/weekly_job_prompt.md с подставленными SECTIONS и периодом>")
```

- `skills=["matomo-mcp-setup"]` — обязательно: иначе у джобы не будет доступа к Matomo и понимания квирков.
- `deliver` можно не указывать — тогда отчёт придёт в текущий чат/топик.
- `enabled_toolsets` — по желанию, снижает расход токенов.

**4. Проверьте, не дожидаясь понедельника:** `cronjob(action="run", job_id="...")` → в чат должно прийти сообщение с инсайтами и **деревом разделов**.

**Требование к блоку «Страницы»:** древовидная структура «раздел → подроут → экран», постранично, с визитами/уникальными/просмотрами
(скрипт `scripts/pages_tree.py` строит её из `Actions.getPageUrls&flat=1`, суммирует метрики по ветвям и печатает с отступами —
вставлять в сообщение моноширинным блоком). Шаблон промпта: `templates/weekly_job_prompt.md`.

## Как передать коллеге

1. Отдать архив скилла (`matomo-mcp-setup_<дата>.tar.gz`) + токен отдельным защищённым каналом.
2. Коллега распаковывает в `~/.hermes/skills/` (или в `<профиль>/skills/`), открывает SKILL.md и идёт по шагам.
3. Проверка — шаг «--selftest» из SKILL.md, затем `matomo_sites` в своей сессии.
4. После настройки — предложить недельную cron-джобу (раздел выше): спросить разделы, доставку и время,
   создать джобу по `templates/weekly_job_prompt.md`, проверить прогоном `cronjob(action="run")`.
   В архиве для коллеги уже лежат: `scripts/mcp_matomo_server.py` (мост), `scripts/pages_tree.py` (дерево разделов),
   `references/matomo-api-cookbook.md` (рецепты API), `templates/weekly_job_prompt.md` (шаблон джобы).
