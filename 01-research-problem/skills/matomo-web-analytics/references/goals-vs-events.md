# Цели (Goals) vs события (Events) в Matomo

Проверено 2026-09 на инстансе iiko (Matomo 5.11, `analytics.iiko.services`, idSite=1) и по исходникам
`matomo-org/matomo@5.x-dev` + matomo.org FAQ.

## Разница по смыслу

- **Событие** — сырой факт взаимодействия: 4 поля Category / Action / Name / Value. Никакой настройки в
  интерфейсе не требует, живёт в Behaviour → Events, иерархический drill-down Категория → Действие → Имя,
  высокая кардинальность, числовой value.
- **Цель** — KPI: «конверсия произошла». Настраивается вручную в Goals → Manage Goals (нужно право Write),
  даёт `nb_conversions`, `conversion_rate`, `revenue`, конверсии по каналам/новым/вернувшимся, попадает в
  дашборды, email-отчёты, Custom Alerts и в сегменты.
- **Связь**: цель типа *«Send an event»* вешается на уже отправляемое событие — события повышаются до
  конверсий без правок фронта. Обратное неверно: цель по URL/титулу/времени живёт вообще без событий.
  Одна цель ≠ одно событие (можно одну цель на группу событий и наоборот).
- Оба плагина — ядро Matomo: `Plugins[] = Events`, `Plugins[] = Goals` в `config/global.ini.php`.
  Включать нечего; в UI отчёты появляются сами.

## Триггеры целей

Автоматические (кода не требуют): Visit a given URL (contains / is exactly / regex), Visit a given Page Title,
**Send an event**, Download a file, Click on a link to external website, Stay for a certain amount of time.
Ручные/кодовые: e-commerce (заказ, товары, выручка), `_paq.push(['trackGoal', id])` с доп. данными.

Опции цели: чувствительность к регистру, «Allow multiple conversions per visit» (по умолчанию — **не более
одной конверсии на визит**), value/revenue. Источник: `matomo.org/faq/reports/create-a-goal-in-matomo/`.

## Цели НЕ ретроактивны

Конверсия фиксируется трекером в момент обработки запроса:
`plugins/Goals/Tracker/GoalsRequestProcessor.php` (пишет метаданные `goalsConverted` / `visitIsConverted`)
→ `core/Tracker/GoalManager.php`: `detectGoalsMatchingUrl()` → `detectGoalMatch()` → `recordGoals()`.
Никакого пересчёта истории нет: цель, созданная сегодня, наберёт конверсии только с сегодняшнего дня,
прошлые визиты конверсиями не станут (в CR и атрибуцию не попадут). Аппроксимация «задним числом» —
обычный отчёт по страницам/событиям, но это не конверсии.

## Метрики и сегменты

- Сегменты (проверено `API.getSegmentsMetadata`, idSite=1): `visitConverted` (сконвертил хоть одну),
  `visitConvertedGoalId`, `visitConvertedGoalName`.
- Метрики (`Goals.get`): `nb_conversions`, `conversion_rate`, `revenue`, `nb_conversions_new_visit`,
  `nb_conversions_returning_visit` (+ revenue/CR-варианты). Конверсии могут быть дробными (FAQ Matomo).
- В отчёте **Events** метрика Visits считается по каждому действию-событию (визит с 3 событиями попадает
  в 3 строки) — для «сколько людей» брать `nb_uniq_visitors`/уники. У целей такого дублирования нет.
- События архивируются с лимитом `datatable_archiving_maximum_rows_events = 500` строк на уровень за
  период (недельные/месячные срезы при высококардинальных именах режутся); у целей лимита нет.

## Что можно завести БЕЗ участия фронта

Стандартный JS-трекер сам отправляет downloads и outlinks (опция `enableLinkTracking`), поэтому цели
«скачал файл» и «клик на внешнюю ссылку» создаются в ЛК и начинают считать сразу. На iiko это подтверждено
данными: за 90 дней `Actions.getDownloads` — 18 файлов, `Actions.getOutlinks` — 224 хоста, топ
`m1.iiko.cards` (274), `iiko.ru` (245), `iiko.cards` (223), `play.google.com` (151), `apps.apple.com` (141)
→ готовый KPI «установка приложения из стора» без разметки.

Ограничение для iiko: URL-цели на внутренних экранах бесполезны, пока все экраны раздела склеены в
`/<module>/index.html` (см. `spa-hash-routing.md`) — по URL ловится только «вход в модуль»
(`URL contains /marketplace/`), а не «нажал кнопку на экране». ~30% просмотров без `document.title`
делают title-цели такими же хрупкими.

## Проверка в ЛК (рецепт для пользователя)

1. Сайт → Behaviour → Events; включить сегмент (иконка воронки / Add new segment) → измерение
   **Page URL** → оператор **contains** → значение (`localhost:4200`, `order-demo.iikoweb.ru`, …) → Save.
2. Событие привязано к URL страницы, где сработало, поэтому сегмент по pageUrl фильтрует и отчёт Events.
   События, отправленные без pageview (SPA-экран без URL), в такой сегмент не попадут — их искать в
   Visits Log по визиту с этим хостом.
3. Несколько хостов одним сегментом: `pageUrl=@localhost,pageUrl=@.iwr.lan,pageUrl=@-demo-,pageUrl=@testov`
   (запятая = OR, `;` = AND, негативные операторы `!@` / `!~`).
4. Цели: Goals → Overview (эволюция, CR, revenue, sparkline по каждой цели), детали — Goals → Goals;
   проверка «сработало ли сейчас» — Visits Log, по клику на конверсию видно goal.
5. Ссылкой на отчёт с сегментом получается не всегда — надёжнее селектор сегмента в UI; API-путь
   (`Events.getCategory&segment=pageUrl=@<хост>`) даёт те же цифры для сверки.

## Состояние инстанса iiko (2026-09)

- Целей не заведено: `Goals.getGoals&idSite=1` → `[]`, конверсии/выручка нулевые → отчёт Goals пуст.
- События: единственная категория за всю историю — `Session` (`bounce_pagehide`, `bounce_visibilitychange`),
  без имён и значений → строка «Event Name not defined».
- Плагины: `Funnels` и `CustomReports` не установлены (`Funnels.*` / `CustomReports.*` → 404),
  `Diagnostics.*` → «API module Diagnostics not found» (конфиг инстанса по API не прочитать).
  Бесплатные пути без этих плагинов: отчёт Events + сегменты + Custom Dimensions (CD1 «Store ID»,
  action-scope).
