# Следы автогена в CSS `iiko-ds-web` и как с ними жить

Разбор 12.09.2026, когда владелец сказал «Там жесть во многих компонентах» и прислать скрин не мог —
искать пришлось самому, скринами всех 38 страниц + тремя детекторами (`scripts/audit-page-render.py`).
Ни одна из находок ниже **не правится в библиотеке**: дефекты отданы владельцу как находки, а на страницах
рекомендаций нейтрализованы каркасом.

## 1. «Плашки»: `background` = `color` у текстовых классов

Автоген Figma писал заливку текстового узла в `background` элемента, а цвет — тем же токеном. Итог: текст
рисуется сплошным прямоугольником (чёрным или белым). Детектор — точный: элемент с **собственным текстом**,
у которого `getComputedStyle().backgroundColor === .color` (собственный текст = прямой текстовый потомок,
иначе обёртки-контейнеры дают ложные срабатывания).

Найдено **23 класса** (28 правил) в 19 файлах; сначала было 26 невидимых фрагментов на страницах, после
нейтрализации — 0:

| Компонент | Классы |
|---|---|
| List | `.ds-list-item__text`, `__label-up`, `__label-down` |
| Menu | `.ds-menu-item__text`, `__label-up`, `__label-down` |
| Select | `.ds-select-item__subtitle`, `__label-up`, `__label-down` |
| Sidenav | `.ds-sidenav-item__l3` (+ `__label` — тёмный токен на тёмной панели) |
| UI: text-ui | `.ds-text-ui__list-item`, `__label-up`, `__label-down` |
| Datepicker | `.ds-control-panel__month`, `.ds-elements__date` |
| Timepicker | `.ds-control-panel-2__month` |
| Hint/Tooltip | `.ds-hint-header__title` (белая полоса внутри тёмного контейнера) |
| Dialog | `.ds-dialog-header__description` |
| Chips, Search, Status | `.ds-chips__chip-text`, `.ds-search__text`, `.ds-status__content` |
| Checkbox / Radio / Input number | `*-label__support-text`, `input-number-but-icon__support-text` |

Файлы автогена видны и по именам классов: `.ds-radio-button-label__цвет-и-палитра`,
`.ds-sidenav-control__свернуть-меню`, `.ds-sidenav-footer__ver-7-8-6-29440` — имена узлов Figma стали классами.

**Ловушка сканера.** Парный регексп (`background: var(--tok, #hex)` + `color: var(--tok…)` с тем же токеном)
надо писать с учётом фолбэка — `var\((--ds-color-[a-z0-9-]*)(?:\s*,[^)]*)?\)`, иначе первый прогон
возвращает **0 классов** и выглядит как «дефекта нет». Вторая волна поиска — правила, где фоном стоит
текстовый токен (`background: var(--ds-color-text-primary…)`) без парного `color`: нашлась ещё тройка
`.ds-control-panel__month`, `.ds-control-panel-2__month`, `.ds-elements__date`.

## 2. Прочие дефекты того же происхождения

- **`white-space: nowrap` у ~60 `__label`-классов.** Длинная подпись не переносится и уходит за карточку
  (замер: `.ds-dialog-content__label` выступал на 421 px за панель). В примере с длинным текстом перенос
  разрешён каркасом.
- **Обёртка кнопки диалога залита акцентом.** `.ds-dialog-footer__button { background: var(--ds-color-button-accent-filled-default-background, #448aff); box-shadow: … }` — вокруг каждой кнопки синяя рамка.
- **Фиксированная высота блока действий.** `.ds-dialog-view__action` / `.ds-dialog-footer__action` —
  `height: 68px` при `flex-direction: column`: две кнопки по 44 с паддингами не влезают, вторая выходит
  за карточку (и на десктопе тоже).
- **Светлый снекбар — белое на белом.** `.ds-snackbar__label { color: …dark-text-color, #ffffff }` жёстко
  белый, а `.ds-snackbar--single.ds-snackbar--light` даёт белый фон. Контраст 1.00.
- **Подписи сайденава тёмные на тёмной панели.** Пункты `#263136`, а токены подписей
  `--ds-color-sidenav-item-l3-text-color: #333333` → контраст 1.06.
- **`.ds-elements-2__label` белый** (это цвет **выбранной** строки) — в невыбранных строках текст
  становится белым по белому. В примере обычные строки — обычный `<span>`, выбранная —
  `.ds-elements-2--selected`.
- **Контейнеры ДС без класса варианта ведут себя как строка.** `.ds-hint-container` — `display: flex;
  align-items: center` без направления; колонкой его делают варианты (`--default`, `--up`, `--down`).
  В примере вариант забыли — подвал (250 px) уехал на 83 px за панель.
- **Два вопроса палитры, не режима:** счётчик `.ds-badge--warning` (жёлтый фон + белый текст, контраст ≈ 1.9)
  и плейсхолдерный цвет `.ds-search__label` = `--ds-color-search-default-text-color` (#d6d6d6, контраст 1.38).

## 3. Как это живёт в каркасе страниц (библиотеку не трогаем)

Всё нейтрализуется в `_audit/rec/build.py` — константа `CSS` (уходит в `rec.css`) правилами, привязанными
к панели, то есть работают и на десктопной, и на мобильной панели:

```css
.panel .ds-list-item__text, .panel .ds-menu-item__text, … {background:none}          /* 23 класса плашек */
.panel .ds-snackbar--light .ds-snackbar__label{color:var(--ds-color-snackbar-complex-light-text-color,#333)}
.panel .ds-sidenav-item__label,.panel .ds-sidenav-item__l3{color:var(--ds-color-text-inversive,#fff)}
.panel .ds-dialog-footer__button{background:none;box-shadow:none}
.panel .ds-dialog-view__action,.panel .ds-dialog-footer__action{height:auto;min-height:68px}
.panel .ds-dialog-content__label,…{white-space:normal;overflow-wrap:anywhere}
```

Плюс карточка **«Найдено в ДС (в библиотеке не правим)»** — функция `found_card()` в `build.py`, поле
`found_html` в `_audit/rec/data/<slug>.json`. Заполнено на 13 страницах: autocomplete, badge, datepicker,
dialog, hint-tooltip, list, menu, search, select, sidenav, snackbar, text-ui, timepicker.
Текст карточки называет **конкретные классы, замер и причину** («у `.ds-select-item__subtitle` фон = цвет
текста, след автогена»), а не «что-то не работает». На оболочке (`index.html`) — один абзац, объясняющий
принцип: каркас нейтрализует, библиотека не правится, перечисленное отдано владельцу как находки.

Правило, к которому пришлось прийти: **лейбл и структуру примеров можно править (это страница), поведение
и цвета библиотеки — нет.** Поэтому «строка запроса в поиске» в примере — обычный `<span>` с токеном
текста (плейсхолдерный класс #d6d6d6 остался для плейсхолдера), а не правка `.ds-search__label`.

## 4. Порядок приёмки, которым это найдено

1. `python build.py` в `_audit/rec` (пересборка страниц + `?v=`).
2. Скрины всех страниц headless Chrome → PIL режет на мобильные половины (`crop((960, 90, 1920, …))`) и
   собирает листы 2×2…2×4 с подписью страницы → просмотр через vision (38 страниц ≈ 10 листов вместо 38 вызовов).
3. `python scripts/audit-page-render.py` — плашки / контраст / выход за границы по всем страницам.
4. Починка → повтор детекторов до нуля → повторный скрин изменённых страниц.
5. В отчёте разделять «починил» и «найдено в ДС» — владелец читает второе как результат, а не как отписку.
