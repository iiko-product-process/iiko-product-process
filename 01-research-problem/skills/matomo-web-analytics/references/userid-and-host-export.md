# Выгрузка «раздел × поддомен × uid» + какие идентификаторы пользователя есть в Matomo

Класс задач: «выгрузи по разделу X конкретные поддомены и uid, с которыми заходят»,
«какой id пользователя я получу», «есть ли у нас CRM-идентификаторы / что приходит по авторизованным».
Проверено на iiko prod (Matomo 5.11, idSite=1, `analytics.iiko.services`), октябрь 2026.

## 1. Инвентарь идентификаторов: что есть и чего нет

Есть по каждому авторизованному визиту (`Live.getLastVisitsDetails`):

| Поле | Пример | Смысл |
|---|---|---|
| `userId` | `84694`, `87049`, `104927` | **числовой** id пользователя — единственный бизнес-ключ (фронт зовёт `setUserId`) |
| `visitorId` | `339f73a8fe286078` | технический ID браузера; у залогиненных = `sha1(userId)[:16]` |
| `visitIp` | `10.206.0.0` | IP (внутренняя сеть iiko ⇒ `city`/`country` пустые) |
| `idVisit` | `1568938` | id визита (для склейки с логом) |
| `dimension1` (в каждом действии) | `117311` | **CD1 «Store ID»** — id ресторана, action-scope, значения из JS (у CD1 `extractions.pattern` пустой) |
| устройство/ОС/браузер/рейтинг | `deviceType`, `browserName` | техданные визита |

Чего НЕТ и это надо отвечать прямо: **никаких CRM-идентификаторов** (id клиента, id заказа, карта лояльности), а также ФИО, e-mail, логина, роли/должности, названия ресторана (только числовой Store ID) и названия компании. Custom variables в Matomo 5 отсутствуют; свободны слоты CD ≥ 2 (занят только CD1).

Команды разведки (быстрые, без сегментов):

```
CustomDimensions.getConfiguredCustomDimensions                    # список CD, scope, extractions
CustomDimensions.getCustomDimension&idDimension=1&period=range&date=…&showColumns=label,nb_visits   # значения CD (за 30 дней iiko: 1000 значений)
UserId.getUsers&period=range&date=…&filter_limit=-1               # колонки: label(uid), nb_visits, nb_actions, bounce_count, max_actions, sum_visit_length, idvisitor, sum_daily_*
Live.getVisitorProfile&visitorId=<idvisitor>                      # профиль: first/last visit, totalVisits, totalActions, devices, countries, customDimensions
Live.getLastVisitsDetails&date=today&filter_limit=1               # полный набор полей визита/действия (искать dimension*, custom*, userId)
```

Роль/должность косвенно видны только через активность (события `Employees Schedule`, доступ к `/configuration`), надёжно — лишь новым CD. Если просят «подписать uid именами» — нужен справочник id→ФИО/ресторан от заказчика (в Matomo его нет).

## 2. Логины: как измерять

- Экран логина `/navigator/auth/login` трекается и **уже 100% с uid** (замер 05.10.2026: 5 925 визитов, все с uid) ⇒ «сколько пользователей залогинилось» ≈ `nb_users` за день, «кто именно» — `UserId.getUsers` с сегментом `pageUrl=@/navigator/auth/login`.
- Целью можно повесить «визит на экран логина» (URL-цель, без разметки), но это заход, а не факт успешного входа.
- Чистый вариант — событие `login_success` из кода (запрос к фронту): даст и конверсию, и per-user counts.

## 3. Выгрузка host × uid: рабочий метод (Live day-chunks)

Агрегатные отчёты НЕ дают пару «поддомен × uid»:
- `Actions.getPageUrls` даёт строки уровня пути, `url` в строке — ОДИН примерный хост (проверка: `label=/internal-couriers/index.html` → `url=…frank-co…`, но живых хостов оказалось **129**, а первый наивный вывод «5 хостов» был получен именно из этого поля);
- per-host сегменты (`pageUrl=@<section>;pageUrl=@<host>`) дают точные цифры, но **каждый такой запрос ≈60 с** — на десятки хостов не годится (упирается в таймаут).

Рабочая схема — сырой слой, по дням (проверено: 179 визитов/день ⇒ 3,5 МБ, 3 с; 30 дней ≈ 2 мин):

```python
Live.getLastVisitsDetails
  period=day, date=<день>, segment="pageUrl=@<раздел>", filter_limit=-1
  showColumns="userId,visitServerDate,visitLocalTime,actions,actionDetails"
```

`showColumns` на Live работает и оставляет вложенный `actionDetails` (в нём `url`, `pageTitle`, `type`, `dimension1`).
Из каждого визита: `userId`, хост из URL каждого действия, содержащего имя раздела, число просмотров раздела и `actions` (всего действий в визите). Агрегаты: пары (host, uid), сводка по хостам, сводка по uid; визиты без uid считать отдельной колонкой (в сентябре в iiko их было ~60%, после раскатки uid 02.10 — ~0%).

Готовый скрипт: `scripts/export_section_host_uid.py` (см. ниже) — пишет три CSV с датой в имени.

**Кросс-чек** (один-два хоста, сегментами): `VisitsSummary.get` c `pageUrl=@<раздел>;pageUrl=@<host>` — iiko hatimaki: 847 визитов против 814 в выгрузке (Δ≈4% — визиты, затронувшие два хоста, считаются в обоих). Итог сверки: метод валиден, расхождение объяснимо — указывать в тексте отчёта.

Ограничения метода: визит, работавший в двух ресторанах, попадёт в оба; «нет URL раздела» (визит только с событиями) помечается отдельно; период брать «до вчера» включительно, иначе сегодняшний неполный день раздувает цифры.

## 4. Кейс iiko: раздел `/internal-couriers` (30 дней, 06.09–05.10.2026)

14 088 визитов, 54 575 просмотров раздела, 40% отказов, 11,8 действий/визит, дневной ряд 528 → 179 визитов.
**129 поддоменов, 307 uid-пользователей, 322 пары (host, uid)**; 14 пользователей работают более чем в одном ресторане (⇒ uid — персональный, не привязан к точке). Топ-страницы: `index.html` 13 076, `map` 911, `couriers` 402, `orders` 216, `fuel-compensation` 167, `routes` 106, `payments` 64, `autoassignment` 16. Топ-хосты: verona-co (293 визита / 6 uid), bruce-lee-cafe (257/1), fishka-co-co (246/7), shaurma-echte-doner-co (242/6), sushiboks-co (225/3).
Урок: раздел, который по одному дню выглядит «нашим» (5 хостов), в реальности используется сотней ресторанов — прежде чем делать вывод о масштабе, тянуть сырой слой.

## 5. Побочные находки про идентификаторы и разметку

- `UserId.getUsers` **принимает сегменты** (с `pageUrl=@/internal-couriers` — 309 строк против 15 103 без сегмента), но метрики внутри строки (`sum_daily_nb_users`) считаются шире сегмента — для per-user цифр брать `nb_visits`/`nb_actions` строки и не смешивать с site-wide.
- Compound-сегменты (`a;b`) медленные: держать таймаут ≥300 с и не строить на них массовые циклы; в диалоге с нетерпеливым пользователем предупреждать, что сверка идёт минутами (кейс: «10 минут уже думаешь!!» — это были сверочные сегментные запросы).
- Matomo Tag Manager (если спросят про «прикрутить события без релиза»): в контейнере iiko (`TagManager.getContainer*`) тег «Matomo Аналитика» умеет `trackingType` pageview/goal/event, `customUrl`, `documentTitle`, `customDimensions` (+`areCustomDimensionsSticky`), `idGoal`, но **поля User ID в теге нет** — `setUserId` ставится Custom HTML-тегом (`_paq.push(['setUserId', …])`). В инстансе 16.09.2026 контейнер `I5llzxeu` оставался версией «0.1.0 — Создано автоматически» (автотег pageview + триггер + переменная), на фронте `mtm.js` не встречался — трекинг шёл кодом.
- Премиум-плагины в меню видны как промо-заглушки (`ProfessionalServices.promo*`), а из API отвечают 404 (Funnels, Custom Reports, Media, Heatmaps, Session Recordings, A/B, Forms, Crash) — «что реально включено» надёжнее проверять 404-ками API, а не скриншотом меню.
