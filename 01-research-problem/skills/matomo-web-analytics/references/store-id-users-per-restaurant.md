# Выгрузка «ресторан (Store ID) → пользователи»

Задача: «сколько пользователей на каждом ресторане, который пользуется продуктом». Источник — Custom Dimension #1
«Store ID» (idcustomdimension=1, scope=**action**, name «Store ID», описание «Идентификатор ресторана»; значение пишется
фронтом через `setCustomDimension`, а не URL-extraction — `extractions` имеет пустой pattern).

## Метод: bulk Live, НЕ per-store сегменты

Per-store сегментные запросы (`UserId.getUsers&segment=dimension1==<id>` или `VisitsSummary.get&segment=dimension1==<id>`)
стоят **~22 с каждый** — при 1000+ ресторанах это часы (проверено: 999 ресторанов ≈ 6 ч). Правильный путь — один сквозной
проход по сырому слою:

1. `Live.getLastVisitsDetails` по дням (`period=day`), пагинация `filter_limit=100` + `filter_offset` (до страницы <100 строк).
   `showColumns="userId,actionDetails"` отсекает гео/устройство/реферер (~половину payload). Итог: 13 дней ≈ 165 тыс. визитов, ~15–20 мин в фоне.
2. Из каждого визита: `userId` + `dimension1` из `actionDetails[i].dimension1` (только `type=="action"`).
   У одного визита бывает НЕСКОЛЬКО Store ID (сетевой админ/аудитор переключает рестораны — до 8 за визит) → собирать set.
3. Агрегировать: `user → set(store)`, `store → set(user)`, `store → host` (из первого `actionDetails.url`).

`filter_limit=-1` на Live за полный день тоже работает, но возвращает гигантский единый JSON — пагинация по 100 надёжнее.

## Квирки

- **`CustomDimensions.getCustomDimension idDimension=1` flat=0** — список Store ID, но **обрезается ~999–1000 строк даже с
  `filter_limit=-1`**. Реальное число ресторанов на порядок больше (iiko 13.10.2026: 20 025). Полноту даёт только bulk Live.
- **flat=1** — строки «store × page», `label` вида `"173518 - amore-picca.iikoweb.ru/external-menu/index.html"` → распарсить
  `store_id` (до ` - `) + `hostname` (слаг ресторана). Отсюда же map store→host.
- **Store ID бывает UUID** у франчайзи (хосты `web-franchise-*`, `*-franchis.`, `*-franch.*`). Не фильтровать только числа.
- **У части действий `dimension1` отсутствует** (логин, общие экраны) — ~3,8% пользователей не получают разрез (11 189 против 11 631 в реестре).
- `bounce_rate` приходит строкой `"7 %"` с неразрывным пробелом `\xa0` → `float(str(v).replace("%",""))` (иначе `ValueError: could not convert string to float`).

## Находки (iiko, 01–13.10.2026)

- 20 025 ресторанов (Store ID), 11 189 пользователей, 20 045 пар «ресторан × пользователь».
- **1–2 пользователя на ресторан**: 20 005 ресторанов с одним, 20 с двумя, **0 с 3+**. iikoWeb — инструмент управляющего:
  один аккаунт ведёт закупки + меню + документы + инвентаризацию. Это объясняет «многомодульность» прошлых отчётов — не команда,
  а один человек на ресторан, делающий всё.
- 1 956 пользователей (17,5%) работают в 2+ ресторанах (сети) — отсюда и «1 пользователь» в нескольких Store ID.
- Часть «1 пользователь на ресторан» — роботы/мониторинг (см. класс «автомат» в `matomo-user-paths`), их стоит вычесть
  (uid из `users_segments_v2.csv`), чтобы оставить живых.

Скрипт: `$HERMES_HOME/scripts/store_users_bulk.py`. Выход: `store_user_map_<дата>.csv` (store_id; hostname; user_id) и
`stores_users_summary_<дата>.csv` (store_id; hostname; users_count).
