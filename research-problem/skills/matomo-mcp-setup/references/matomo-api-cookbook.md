# Шпаргалка по Reporting API Matomo (что спрашивать и как)

Все вызовы — через инструмент `matomo_raw` (или напрямую `POST <base>/index.php` с `module=API&format=JSON&token_auth=...`).

## Метрики: что чем мерить

| Метрика | Метод | Смысл |
|---|---|---|
| `nb_visits` | `VisitsSummary.get` | визиты (сессии; новый визит после 30 мин неактивности, в полночь, при смене кампании) |
| `nb_uniq_visitors` | `VisitsSummary.get` (day/week) | уникальные посетители по ID визитёра (cookie/устройство) |
| `nb_users` | `VisitsSummary.get` | пользователи — только те, у кого передан User ID (`setUserId`) |
| `nb_actions` | `VisitsSummary.get` | действия: просмотры + скачивания + внешние ссылки + события… |
| `nb_pageviews` | `Actions.get` | просмотры страниц |

Правило: **users ≤ uniq visitors всегда**; users есть только в сводке и в `UserId.getUsers`, в постраничных отчётах их нет.

## Готовые рецепты

```jsonc
// Сводка и разрез по залогиненным
{"method": "VisitsSummary.get", "period": "day", "date": "yesterday"}
{"method": "VisitsSummary.get", "period": "day", "date": "yesterday", "extra": {"segment": "userId!="}}   // с User ID
{"method": "VisitsSummary.get", "period": "day", "date": "yesterday", "extra": {"segment": "userId=="}}   // без User ID

// Страницы: разделы (без flat) vs листовые URL (flat=1)
{"method": "Actions.getPageUrls", "period": "range", "date": "2026-09-01,2026-09-30"}
{"method": "Actions.getPageUrls", "period": "day", "date": "yesterday", "extra": {"flat": 1, "showColumns": "label,nb_visits,nb_uniq_visitors"}}

// События
{"method": "Events.getCategory", "period": "day", "date": "yesterday"}
{"method": "Events.getAction", "period": "day", "date": "yesterday"}
{"method": "Events.getName", "period": "day", "date": "yesterday"}
// только бизнес-события, без технической категории:
{"method": "Events.getCategory", "period": "day", "date": "yesterday", "extra": {"segment": "eventCategory!=Session"}}

// Каналы и кампании
{"method": "Referrers.getChannelType", "period": "range", "date": "2026-09-01,2026-09-30"}
{"method": "Referrers.getAll", "period": "range", "date": "2026-09-01,2026-09-30"}

// Аккаунты (User ID)
{"method": "UserId.getUsers", "period": "day", "date": "yesterday", "extra": {"filter_limit": 50}}

// Живой лог (что происходит прямо сейчас)
{"method": "Live.getLastVisitsDetails", "period": "day", "date": "today", "extra": {"filter_limit": 100}}
{"method": "Live.getCounters", "period": "day", "date": "today", "extra": {"lastMinutes": 60}}

// Цели (если настроены)
{"method": "Goals.getGoals"}
{"method": "Goals.get", "period": "day", "date": "yesterday"}
```

## Сегменты-шпаргалка

| Сегмент | Что фильтрует |
|---|---|
| `userId!=` / `userId==` | сессии с переданным User ID / без него |
| `userId==12345` | конкретный аккаунт |
| `pageUrl=@/navigator` | все URL, содержащие путь (кросс-доменно) |
| `pageUrl==https://host/path` | точный URL |
| `eventCategory==Employees Schedule` | события категории (так же `eventAction==`, `eventName==`) |
| `eventCategory!=Session` | всё, кроме технической категории |
| `visitConvertedGoalId==1` | визиты, сконвертившие цель №1 |
| `deviceType==smartphone` | только смартфоны |
| Комбинация | через `;` (И), через `,` (ИЛИ) |

## Квирки, которые ломают отчёты, если о них не знать

1. `period=range` **не отдаёт** `nb_uniq_visitors` / `nb_users` — вернутся `null`, а в UI покажутся суммы дневных (`sum_daily_nb_uniq_visitors`), которые завышают. Для уникальных — `period=week` или `period=day`.
2. Многоадресные `period=day&date=start,end` возвращают **словарь** `{дата: метрики}` (пустые дни — `[]`/`{}`), а не список строк.
3. `Actions.getPageUrls` в `flat=1`: `label` — путь без хоста; хост (или домен) — в поле `url`. Искать `localhost`/`.test` по `label` бессмысленно.
4. Если задан `idSite`, `SitesManager.getAllSites` возвращает словарь `{idsite: {...}}`, без него — список.
5. `filter_limit=-1` = все строки (по умолчанию 100); `showColumns=...` сильно уменьшает payload.
6. HTTP 404 на метод = плагин не установлен; 400 = модуль есть, но параметры неверные.
7. В отчёте событий «Visits» считается по каждому действию-событию: один визит с 3 событиями попадёт в 3 строки — для людей берите `nb_uniq_visitors`.
8. `userId` переопределяет ID визитёра (настройка `enable_userid_overwrites_visitorid`): у залогиненных `idvisitor = substr(sha1(userId),0,16)`. Это позволяет проверить, доехал ли User ID: если ID не равен sha1 от аккаунта — uid в запросе не было.
