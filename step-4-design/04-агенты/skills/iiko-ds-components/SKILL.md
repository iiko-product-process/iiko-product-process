---
name: iiko-ds-components
description: "Use when editing iiko DS components (CSS, tokens, modes)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-system, css, tokens, mobile, figma, iiko, frontend]
    related_skills: [hermes-desktop-backend-diagnostics]
---

# iiko DS — components, tokens, platform modes

## Overview

Дневная работа владельца — **iiko Web DS**: CSS-компоненты из переменных Figma + растущий мобильный слой. Карта и token-first порядок правки компонента — ниже. Workspace: `C:\Users\asukharev\GitHub\DS`.

**Страницы рекомендаций** → `references/`: `recommendation-pages.md`, `rec-screens-block.md` («На экране»), `rec-sheet-markup.md` (шторки и правка `data/*.json`), `iiko-real-ui-screens.md` (реальные экраны iiko = дефолт), `shell-page-and-shared-notes-block.md`. `rec.css` — из `build.py`.
**Два правила:** дефолт компонента — как правдоподобный
интерфейс (не свалка всех вариантов подряд — «такого не может быть в реальном интерфейсе»),
и пункт «Что делают системы» из текста паттернов **не показывать нигде** (в генераторе он
отфильтрован, из уже собранных страниц удалён).
Что владелец считает паттерном поведения, какие темы писать нельзя, правило «дописывать,
а не заменять» и разбор провала с массовым вливанием превью —
`references/behavior-pattern-research.md`.
The «Примерные паттерны поведения» block needs **cited** sources: fetch routes, a verbatim
quote bank and the grep-the-quote-first protocol are in `references/ds-source-quotes.md`.
`scripts/rework-status.py [repo_root]` prints where a rework stopped (missing patterns,
un-merged `out/` patches) — run it after any interruption before promising anything.

## When to Use

- Build/refactor a component in `iiko-ds-web` (Button, Input, Banner, …).
- Produce the mobile (or tablet) version of a desktop component, or touch the
  desktop/mobile split at all.
- Answer "what does the DS say about X" / assemble a prototype on DS components.
- Anything that touches `iiko-ds-spec.md`, `tokens.css`, `modes.css`, prototypes.
- The **recommendation pages** — the generated «desktop → mobile» pages, one per
  component: `_audit/rec/data/*.json` → `_audit/rec/build.py` →
  `iiko-ds-mobile/prototypes/recommendations/`. Details (pipeline, checks, content rules)
  — `references/recommendations-pages.md`.

## Recommendation pages — the short version

- Source of truth is `_audit/rec/data/<slug>.json`. Do not hand-edit the generated HTML
  and do not touch `iiko-ds-web` — fix the generator (`build.py`, `mock.py`) or the data.
- Bulk content (previews, rows, platform columns) goes to subagents as **patch files** in
  `_audit/rec/out/<kind>/<slug>.json`; they must self-check with
  `python checks/check-patch.py <slug>` (0 problems) and never touch `data/`. Merge with
  `python apply_out.py --build`, then run the live audits (`checks/audit-edits.py`,
  `checks/audit-preview.py`) yourself — a child's "done" is a self-report, not proof.
- Layout change across all pages: redo **one** page first, verify it, let the owner look,
  then roll out. A wrong reading otherwise costs a full second round over 38 pages.
- Content rules the owner insists on: the Mobile column carries **numbers, never
  «то же / та же / те же»** (unchanged = repeat the desktop numbers); the two preview
  screens show the *same* interface with the studied component in exactly one place per
  screen (body on screen 1, sheet/header on screen 2, elsewhere the same rows without the
  control); edits apply only to the second screen; two buttons that fit stay in a row.
- Answer his «задача понятна?» by restating the task in his words first; a question is
  not permission, and nothing beyond the named scope gets changed.

## Repos — what lives where

| Path | What it is |
|---|---|
| `iiko-ds-web/` | The library. **Own git repo** (origin `github.com/Anders7Rusk/iiko-ds-web`, branch `main`, published as `anders7rusk.github.io/iiko-ds-web`). |
| `iiko-ds-web/tokens.css` | **Generated** from Figma variables (~1743 vars; collections Base Size, Base Color, Space, Radius, Base Stroke, Shadows, Base Typography, Typography, Color, **Component**). Never hand-edit. |
| `iiko-ds-web/styles.css` | Generated Figma text/shadow/colour styles. `font.css` = Roboto 400/500 inlined base64 → works offline, load it first. |
| `iiko-ds-web/components/<Name>_DS/*.css` | One folder per component; `components/index.css` aggregates them with `@import`. |
| `iiko-ds-web/iiko-ds-spec.md` | ~700 KB single source of truth written to be pasted into any AI: general rules, class map, token tables, full component CSS. Mostly generated. |
| `iiko-ds-mobile/` | The **mobile layer** (not a git repo), structure mirrors `iiko-ds-web`: `modes.css` (the mode axis), `components/index.css` (aggregator; a `components/<Name>_DS/` file appears only when a real `*_mob` component exists), `prototypes/` (demo pages, e.g. `prototypes/button-modes.html` — desktop and mobile side by side + measurements). Plus the plan docs: `desktop-to-mobile-plan.md` (classification A–D + how Material/Angular solve each), `mobile-mode-notes.md`, `mobile-workflow.md`, `mobile-steps.md`, `mobile-block-schemes.md`. |
| `iiko-ds-prototypes/` | HTML prototypes (not a git repo). Comparison pages such as `compare-button-mob.html` hold values transcribed from Figma — a legitimate source when the canvas itself is unreachable. |

## Проверки (обязательные, все лежат в `_audit/rec/checks/`)

- `_boxes.html` — «задано → на экране»: сверяет **рендер** (getBoundingClientRect) с объявленной высотой.
  ⚠️ Нельзя мерить только `getComputedStyle().height` — оно возвращает *заданное* значение и «съедает» дефект:
  кадр поля 48 px рисовался как 74, а проверка показывала 48. Именно из-за этого баг жил долго.
- `_plates.html` — текст-плашки (background == color у автогена).
- `_contrast.html` — невидимый текст (контраст < 2).
- `_overflow.html` — выход элементов за границы панели.
- `_values.html` — мобильные значения против заявленных на странице.
- В CSS библиотеки **нет `box-sizing: border-box`** ни у одного класса с объявленной высотой (44 класса):
  паддинги и рамка прибавляются сверху. Патчится в каркасе `_audit/rec/build.py` (`.panel <sel>`) и в
  `iiko-ds-mobile/components/box-sizing.css` — НЕ в библиотеке. В прототипах ДС то же лечат на странице.
- **Десктопные детекторы (12.09.2026, живут в `_audit/rec/checks/`)**: `audit-desktop.py` (системные
  контролы `NATIVE`, content-box `CONTENTBOX`, пустые элементы) и `audit-live-desktop.py` (`CLIPPED`
  scrollHeight > clientHeight, `OVERLAP` пересечение листовых подписей, `VOID` пустота в контейнере,
  `STATE` disabled = enabled). Оба ходят по обеим панелям, читают `getComputedStyle`/`getBoundingClientRect`,
  требуют `serve.py 8899` и свежий профиль. Рядом `shoot.py` (скрин + кроп половины) и `sheets.py`
  (листы 2×2 по 4 страницы — все 38 страниц разбираются за 10 вызовов vision).
  Ловушка самих детекторов: внутри JS-шаблона писать `OUT.join(String.fromCharCode(10))`, а не `'\n'` —
  Python-строка съедает экранирование, в файл попадает реальный перевод строки и JS падает с
  `SyntaxError`, а скрипт печатает «no output -- server up?» (ложный вывод «сервер виноват»).

## Non-negotiables (spec, «Общие правила»)

- **⛔ Скриншот или замечание владельца — это НЕ задание.** 12.09.2026 он пометил красным пять абзацев
  пояснений на странице-оглавлении; я прочитал пометки как «убрать», убрал и получил: «Ничего убирать не
  надо. Я не просил. Никогда ничего не делай сам без моего ведома. Кажется, уже был такой разговор».
  Правило: правку текстов, каркаса и данных начинать ТОЛЬКО после явного «сделай / убери / поменяй».
  Скрин, пометка, жалоба, вопрос — материал для разговора, а не разрешение; если пометка читается как
  указание, задать один короткий вопрос и дождаться ответа. Если самодеятельность всё же случилась —
  первым действием откатить (восстановить текст в `build.py`/`data/*.json`, пересобрать, показать
  проверку «вернулось»), а не объяснять, почему так вышло.
  **Это не только про содержимое страниц.** После отката он добавил: «Ты уже заебал так делать… Уже не в
  первый раз и постоянно так делаешь что не просят» — то есть самодеятельность накапливается и перечитывается
  как система, а не как случайность. Ждать «да» до: правок текстов/каркаса/`data/*.json`, добавления
  карточек «Найдено в ДС» на страницы, массовых правок после жалобы на «ошибок полно», запуска фоновых
  процессов, создания новых папок, удаления или перемещения любых файлов (включая свои же тестовые
  артефакты и дубли), изменений в системе (автозапуск, задачи). Одно «делай» = одно действие: следующий
  шаг снова требует слова. Когда он сам просит фикс — делать можно, но найденное рядом «заодно» не чинить,
  а вынести списком и спросить.
  Практический выход для любой такой развязки: сначала откат, потом три строки отчёта «что было изменено →
  что вернул → чем проверил» и один вопрос, что делать дальше. Объяснения и оправдания он не читает.
- **⛔ Вопрос в чате — это НЕ разрешение к действию (12.09.2026).** Он спросил: «Я могу запретить вообще лезть
  в моё окружение кроме acp и тех файлов что есть в папке Git?» — вместо ответа я полез в исходники Hermes,
  качал документацию, запускал проверки. Реакция: «Это был вопрос, а не разрешение к действию», затем
  «Ты не ответил на вопрос». Правило: на вопрос — ответ **текстом в том же сообщении, без единого вызова
  инструментов**; никаких «сначала я посмотрю/проверю», никаких скачиваний и запусков «для полноты ответа».
  Если вопрос пришёл в новую сессию (ACP заводит новую на уточнение, история остаётся в предыдущей) — сначала
  поднять сам вопрос из `state.db` (`session-store-forensics`, раздел про потерянный вопрос), потом ответить.
  На вопрос «можно ли тебя ограничить» отвечать рычагами Hermes, а не обещаниями: **списка разрешённых папок
  в Hermes нет**; инструменты выключаются целиком (`agent.disabled_toolsets` / `hermes tools`),
  `terminal.backend: docker` изолирует только команды (правки файлов идут мимо контейнера),
  `approvals.mode manual` — гейт только на команды, правки файлов его не проходят; по-настоящему закрывает
  лишь отдельная учётка Windows с правами только на `C:\Users\asukharev\GitHub`. Цитаты и грепы —
  `hermes-desktop-backend-diagnostics`, `references/restricting-agent-access.md`.
- **⛔⛔ НИКОГДА не править файлы в `iiko-ds-web` без прямого разрешения владельца.** Ни токенизацию,
  ни формулы высот, ни «очевидные фиксы» (box-sizing, порядок состояний, импорты в агрегаторе) — даже
  когда они явно сломаны. Задача «сделай мобильные компоненты» НЕ даёт права на десктоп: у него любая
  правка библиотеки = сломанный источник истины (Figma-автоген + выверенные вручную файлы), а откат —
  один `git checkout`. Реакция на самовольные правки — ярость и требование откатить всё.
  Как делать мобильное без библиотеки: явные значения в `iiko-ds-mobile` (`modes.css` + файлы
  `iiko-ds-mobile/components/<Имя>_DS/*.css`, в том числе `height`/`padding` руками, если десктопный CSS
  держит высоту числом). О найденном дефекте библиотеки — только сообщить, не чинить.
- **⛔ НЕ ГАДАТЬ.** Every value comes from a source: Figma export, `iiko-spec.md`, a
  plan doc, or a prototype comparison file. No source for a value → stop, ask, and
  propose the nearest DS component. "I'll check" followed by a guess is a violation.
- **Tokens only** — `var(--ds-*)`, no px/hex literals in component CSS.
- **Naming** — `.ds-<component>` + modifiers `--<value>` (`--m`, `--accent`, `--filled`)
  + elements `__label`, `__icon`.
- **No `--mobile` modifiers**, no second "mobile component set". One markup, one set of
  classes; platform differences arrive through tokens.
- Own classes are allowed **only** for page/shell layout (grid, toolbar, footer).
- **Иконки — только Material Icons лигатурой**: `<span class="material-icons" style="font-size:20px">имя</span>`
  внутри слота ДС (`__icon` / `ds-arrow` / `ds-arrow-select`), размер — через `font-size` (16 / 20 / 24 из
  токенов слота). Своих SVG-заглушек, «похожих» самодельных иконок и PNG не рисовать: обязательного списка
  имён нет, берём из каталога Google. Строка спеки «SVG 20×20» устарела 11.09.2026 — владелец переписал её на
  Material Icons по имени (тогда же `font.css` поехал в онлайн-`@import` Roboto, сеть в проекте допускается).
  Рецепт, карта «слот → имя иконки» и ловушка проверки шрифта: `references/icons-material-ligatures.md`.

## The platform mode axis (desktop ↔ mobile)

Two independent axes: **theme** = colour (`data-theme`, `themes.css`), **mode** = size
(`data-mode`, `modes.css`). Never mix them in one token.

- `iiko-ds-mobile/modes.css` holds `[data-mode="mobile"] { … }` overrides of only the tokens
  that differ. No attribute = Desktop default, so old prototypes stay as they were.
  (The file lives in the mobile folder, NOT in `iiko-ds-web` — a demo page inside
  `iiko-ds-mobile/prototypes/` links it as `../modes.css`, the library as `../../iiko-ds-web/…`.)
- **Load order is mandatory**: `font.css → tokens.css → modes.css → themes.css →
  components/index.css`. `[data-mode="mobile"]` and `:root` have equal specificity, so
  document order decides — modes.css must come after tokens.css.
- Scope the attribute to a block (`<div data-mode="mobile">`) to show desktop and mobile
  **side by side** — Figma cannot do this (its mode is file-global, needing per-instance
  overrides).
- Classify before coding: **values only** → mode override; **different composition** →
  separate `-mob` component; **hidden/replaced** → layout rule, not a component.
- `modes.css` is a bridge: once the Figma exporter emits modes for the `Component`
  collection as `[data-mode="…"]` blocks, its content moves into `tokens.css`.

### Structural variants (category 2) — separate file, not a mode

When the plan row says «Структура» (layout/composition changes, not numbers), the variant does **not**
belong in `modes.css`: it is a file in the mobile layer, `iiko-ds-mobile/components/<Name>_DS/<variant>.css`,
registered in the mobile aggregator `iiko-ds-mobile/components/index.css` (Stepper 11.09.2026 was the first
real one). Two traps, both hit for real:

- **Specificity, not order.** The documented order links the mobile layer *before*
  `iiko-ds-web/components/index.css`, so a variant class with equal specificity loses on every property the
  base also sets (`flex-direction` applied from `.ds-stepper--vertical`, but `align-items` stayed from
  `.ds-stepper` and the vertical line drifted to the centre). Write `.ds-stepper.ds-stepper--vertical` (0,2,0)
  instead of reordering; and measure `align-items`/`gap`/divider orientation, not just the direction.
- **The recommendations page must link `../../components/index.css`.** Without it the structural file never
  loads on the page and the Mobile panel silently renders the desktop layout (measurements said `row` / `8×1`
  while the class was in the markup). The link is in `page()` in `_audit/rec/build.py`.

Show the difference on the page with per-example `html_mobile` (+ `stack: true`), not a `data-mode` rule —
orientation is composition, the way Angular's `orientation` attribute is. Full recipe, numbers and the
Stepper case study: `references/mobile-structural-components.md`.

### Мобильный слой, когда библиотека «заморожена» (12.09.2026)

Владелец однажды потребовал откатить **все** правки в `iiko-ds-web` («Какого хера ты полез в iiko-ds-web???»)
— и был прав: откат делается одной командой `git checkout -- .` в репозитории и проверяется `git status`
(пусто) + `git diff --quiet HEAD` (код 0). После отката десктопный CSS снова держит размеры **числами**
(`.ds-btn--m { height: 36px }`, `.ds-input--m .ds-input__frame { height: 48px }`, трек тумблера 34 × 20),
поэтому режимные токены его не двигают, и мобильные значения надо задавать **явными правилами**
в `iiko-ds-mobile/components/<Имя>_DS/*.css`.

Разделение труда внутри мобильного слоя:

| Что | Где живёт |
|---|---|
| Токены, которые компонентный CSS **читает** (паддинги полей, gap, типографика) | `modes.css`, блок `[data-mode="mobile"]` |
| Всё, что десктопный CSS задаёт числом (высоты, ширины, трек тумблера, ход ручки) | файл компонента в `iiko-ds-mobile/components/<Имя>_DS/…` |

Порядок работы после любого отката библиотеки: (1) **сначала аудит** — прогнать матрицу ожидаемых мобильных
значений (`scripts/audit-mobile-values.py`, 41 проверка по 24 страницам; после отката 12.09.2026 из них было
сломано **17 на 11 страницах**), (2) починить только в мобильном слое, (3) повторить аудит до нуля,
(4) проверить, что каждая из 38 страниц вообще отрисовалась в обоих режимах (считать элементы в панелях —
пустая панель читается как «компонент сломан»), (5) сверить числа на страницах с замерами и поправить текст,
если он утверждал то, чего больше нет (например «высота приходит сама из паддингов»).
Десктопное число при этом никто не двигает: мобильные файлы не влияют на `data-mode` без атрибута.
Разбор случая и таблица «что было сломано → где починено»: `references/mobile-layer-frozen-library.md`.

### Визуальная приёмка: скрины всех страниц + три детектора (12.09.2026)

Владелец потребовал: «Снимай скриншоты с каждой страницы и смотри что происходит» — и добавил, что сам скрин
прислать не может. Значит **верификация целиком на агенте**: партия страниц не считается готовой, пока он их
не увидел. При этом автооткрытие страниц в браузере владельца по-прежнему запрещено — это разные вещи.

Порядок приёмки:

1. `python build.py` в `_audit/rec` (пересборка страниц + `?v=`).
2. Скрины всех страниц headless Chrome (`--window-size=1920,<h> --screenshot=…`). PIL режет каждую на
   **обе** половины (`crop((0, 0, 960, …))` и `crop((960, 0, 1920, …))`), собирает листы 2×2…2×4 с подписью
   страницы — 38 страниц разбираются за ~10 вызовов vision вместо 38. Смотреть обе панели: 11.09.2026 «жесть»
   жила в мобильной (иконки), 12.09.2026 — в десктопной (системные чекбоксы, пустые контейнеры, disabled =
   активной). Лист на четыре страницы читается, а «смотреть только мобильную» — нет.
3. `scripts/audit-page-render.py` — три объективных детектора по DOM всех страниц (то, что на уменьшенном
   листе не видно): **плашки** (у элемента с собственным текстом `background-color` равен `color` — след
   автогена), **контраст** ниже 2.0 к эффективному фону, **выход за границы панели** (предки с
   `overflow != visible` пропускаются, иначе скроллы дают ложные). Приём исполнения: страница-обёртка с
   iframe на каждую страницу и выводом в `<pre id="out">` — `--dump-dom` сам JS на целевой странице не
   исполняет, а `contentDocument` требует same-origin, поэтому всё через локальный сервер.
4. Починка → повтор детекторов до нуля → повторный скрин изменённых страниц → только потом отчёт.
5. В отчёте разделять **«починил»** и **«найдено в ДС, не правим»**: второе для него результат, а не отписка.

#### Десктопная половина — такой же объект приёмки (12.09.2026)

Владелец: «Причём тут мобильная версия? У тебя ошибок полно везде в компонентах в десктопе. Просто жесть.
Ты проверяешь и проверяешь очень плохо. Вообще никак». К тому моменту мобильный слой был вычищен до нуля —
и отчёт по одному мобильному слою прочитался как «не проверял вообще». Десктоп — не «панель рядом»:
у него свои детекторы (`audit-desktop.py`, `audit-live-desktop.py`), свой взгляд глазами по кропам **обеих**
половин и свои находки. Полный разбор с числами и кодом — `references/desktop-side-defects-and-detectors.md`.

Что нашлось на десктопе в тот день: Checkbox и Radio рисовались **системным контролом браузера**
(21 контрол 13 × 13 на трёх страницах), недоступная Button icon выглядела активной, три контейнера держали
пустое поле 83…266 px, подсказка textarea была срезана на 3 px — и, отдельно, **два текста на страницах
утверждали починенное в библиотеке, чего после отката уже не было**. Лживый текст на странице — такой же
дефект, как сломанный CSS: после любого отката библиотеки пройти по страницам и сверить формулировки
«починено / не правим» с реальностью.

**Теги текстом на странице — след `esc()` (12.09.2026).** На `index.html#scroll` владелец сказал «Смотри»: в блоке
«Почему так» было видно `<code>/components/scroll</code>` — теги как символы. Причина: в `page()` поле `why_ru`
шло через `esc()` (в отличие от `found_html`, `result_html`, `behaviour_html`), а в данных есть `<code>` (82 вхождения)
и `<b>` (2) — всего 13 страниц: backdrop, card, checkbox, chips, chips-input, divider, expansion-panel, icon-size,
input-number, radio, scroll, status, textarea. Лечение — одна строка: `"why": d["why_ru"]` без `esc()` (одиночных `<`
и `&` в этих полях нет — проверено сканом). Проверка: в сгенерированных страницах нет `&lt;code&gt;` / `&lt;b&gt;`
(0 из 39 файлов) плюс скрин спорной страницы. Общее правило: новый текстовый блок из `data/*.json` сначала проверять
на разметку — либо вставлять как HTML, либо вообще не писать теги в данных.

**«Опустить вниз и сделать последним блоком» (12.09.2026) — два разных места, и оба раза важна форма.**
Фраза «текст после заголовка страницы, который есть у всех компонентов» допускала два чтения: описание на
страницах компонентов (`<p class="desc">` в `page()`) или шесть абзацев-пояснений на оболочке (`index_page()`).
Он имел в виду **оболочку**, но первый шаг я сделал на страницах компонентов — это было ошибкой, и он потребовал
вернуть: «Описание компонента верни на место где был… Для всех компонентов». Поэтому в `page()` порядок
**исходный**: `crumbs` → `<h1>` → `<p class="desc">` → чип категории → панели. Не двигать его больше.

На оболочке правка заняла три шага, и два из них — мои ошибки чтения:
1. абзацы переехали под `.kit` (полосой через всю `.wrap`) — не то: «Я попросил последним блоком… Блоком. А не под меню»;
2. итоговый вид — обычная карточка `<div class="card">` с заголовком `<h2>Общее для всех компонентов</h2>` и шестью
   абзацами `.point` (13/19 — как в «Почему так»), **внутри правого столбца `.kit`**, сразу после `iframe`; после
   заголовка идёт сразу меню и страница, под меню внизу пусто. Свой класс `.note` со скопированными свойствами `.card`
   и абзацами `.desc` (14/20) он отклонил: «Ты можешь нормальный блок сделать как все остальные» — на страницах ВСЕ блоки
   это `.card` + `h2` + `.point`, поэтому любую новую коробку собирать **этим же набором**, а не своим классом и не
   своим кеглем.
3. **Выравнивание по сетке страницы.** Первая версия в колонке была шире карточек компонента: сам блок 305…1894 px,
   карточки внутри `iframe` — 329…1870 px (в теле страницы компонента `body{padding:24px}`). Владелец: «Коряво расположен».
   Лечение — правило каркаса `.kit .card{margin:16px 24px 0}`; замер после: блок 329…1870, совпадает с карточками над
   ним. Проверять края не глазами на уменьшенном скрине, а пиксельным замером строки (`min/max` белого по строке).
   И помнить: внутри `iframe` своя `body`-padding, поэтому «на всю колонку» ≠ «как на странице компонента».
4. **Отступ до блока был разный от страницы к странице (57 / 58 / 76 / 93 / 109 px).** Владелец: «Почему на каждых
   страницах разные отступы до этого блока?». Причина — в `fit()` высота фрейма бралась из
   `d.documentElement.scrollHeight`, а у корневого элемента `scrollHeight` **никогда не меньше высоты самого фрейма**:
   один раз посчитанная на `load` (до загрузки Roboto/Material Icons) и оказавшаяся больше контента высота «залипает»
   и уменьшиться уже не может — лишнее выходит как отступ под блоком. Лечение: высота из `d.body.scrollHeight`
   (у `body` высота по содержимому) + повторный `fit()` после `document.fonts.ready` и `ResizeObserver` на `body`.
   **Итог — то, что владелец принял, потребовало двух шагов.** (а) высота фрейма считается от низа **последнего
   блока страницы**, а не от `body.scrollHeight`: у страницы снизу свои 24 px `body`-padding и 16 px отступ её
   последней карточки, и они прибавлялись к отступу блока пояснений; (б) в тот же инжектируемый в `iframe` стиль
   (`#embedded-fix`) добавлено `html,body{overflow:hidden}` — без него обрезанный фрейм даёт внутреннюю полосу
   прокрутки, она сужает контент на 15 px и края перестают совпадать с блоком (карточка над блоком 329…1855
   против блока 329…1870). **Замер после: 17 px на всех 38 страницах** — ровно тот же промежуток, что между
   карточками внутри страницы (внутренние 17/18/21; 17 = 16 px margin + строка рамки). Промежуточное «57 px на всех
   страницах» я назвал нормой зря: между страницами совпадало, а с блоками — нет, отсюда «это не как у остальных».
   Мерить отступ только пиксельно по скрину (`min/max` не-фоновых пикселей в строке), DOM-замер через вложенный
   `iframe` врёт: там `scrollH` равен уже установленной высоте фрейма.
   Рецепты замеров, пробников и grep-проверок: `references/shell-geometry-and-probe-recipes.md`.

Разбор: «опустить вниз» — про **место**, «последним блоком» — про **форму** (карточка-блок, а не голые абзацы на
фоне). Когда его фраза допускает два предмета, спрашивать один короткий вопрос ДО правки, а не делать один вариант
и предлагать второй потом.

### Колонка «Правка» на странице: мобильный размер меняется из таблицы (12.09.2026)

Задача владельца: «Нужно попробовать добавить в блок „Что меняется на мобиле“ ещё одну колонку после Mobile.
И там сделать редактируемые поля тех значений которые стоят в колонке Mobile… возьмём Кнопку: Высота 36 px → 44 px,
будет 4 колонка после Mobile со значением 44 px, которое я могу поправить и сделать например 40, и это значение
применится к кнопке в отображении мобильной версии. И так по всем значениям в таблице». Уточнения, которые он дал,
и они обязательны: **правим только размеры** (строки про цвет/поведение/показ остаются текстом без поля); «те же»
в размерной строке — недопустимо, значение есть (оно равно десктопному): «Я не знаю зачем ты писал теже»; в строке
с несколькими числами — **отдельное поле на каждое число** («Вариант 1»: `12 / 16` → два поля).

Механика (реализована на `button.html` как образец, остальные страницы — по его «ок»):

- в данных строка получает `edit: [{id, v, sel, css, sync?}]` — по элементу на число, `@` в `css` заменяется введённым
  числом: `{"id":"height","v":44,"sel":".ds-btn","css":"height:@px","sync":{"field":"pad-v","a":0.5,"b":-10}}`;
- генератор (`changes_table()` в `_audit/rec/build.py`) рисует 4-ю колонку `<td class="edit">` с
  `<input class="edit__input" data-id data-sel data-css [data-sync-field|-a|-b]>`. **Колонку Mobile не трогает ни
  генератор, ни скрипт** — это рекомендованное значение, её текст берётся из данных как есть (первая версия помечала
  числа в тексте `<span data-vk>` и переписывала их при вводе; `_mark_values()` удалён: «Значения в колонке мобайл
  не правятся… Ты опять делаешь что-то своё»);
- на странице — `<style id="live">` (последним в `<head>`, после всех ссылок на CSS) и скрипт, который по `input`
  пишет `[data-mode="mobile"] <sel>{…}` **только для тронутых полей**: до первой правки страница выглядит как была.
  Правило живёт в таблице стилей, поэтому работает и для псевдоэлементов — тач-слой `.ds-btn::after{min-width/min-height}`
  правится так же, как высота;
- **связка `sync` считается линейно (`t = a·v + b`) и её результат виден в поле**: высота 40 → поле «Паддинги»
  показывает 10; паддинг 8 → поле «Высота» показывает 36. Цель помечается `__touched` и попадает в правила вместе
  с источником. Само правило строки «Высота» — только `height:@px`: считать паддинги формулой ВНУТРИ правила владелец
  запретил («Нахера это прятать куда-то под капот и вводить в заблуждение»);
- проверка — синхронный iframe-пробник: выставить `input.value`, `dispatchEvent(new Event('input'))` и замерить обе
  панели. Замер Button: mobile 44 → **40**, поле «Паддинги» само показало **10**, колонка Mobile осталась «44 px»,
  desktop **36 — не поехал**; обратный ход (паддинг 8 → высота 36) тоже виден. Целый скрипт страницы и схему
  связок держать в `references/editable-mobile-values.md`.

**Инвентарь таблицы (посчитан по 38 страницам, нужен для любой работы с этой колонкой):** всего 218 строк, размерных — 91
(52 уже с числом, 40 с «те же» — туда вписываются числа, 11 словами — приводятся к «число + пояснение»), не размерных — 127.
У 9 страниц (backdrop, badge, card, divider, hint-tooltip, logo, scroll, status, table-2-lvl) поля долго не появлялись, и я записал это
как «правильный результат». **13.09.2026 вечером владелец это отменил**: «если где-то написано тоже, также и похожие
слова то это тоже значания должны быть цифровые. Пусть они одинаковые с десктопом, но это цифры» — значит строки
с «то же / та же / те же» получают числа из Desktop и поле, и пустая колонка теперь читается как незакрытая строка
(ловит `check-patch.py`, категория `STILL-TAKZHE`; таких строк на 38 страницах 59).
В версии до 13.09.2026 эти страницы выглядели так (проверено `audit-edits.py`: «страниц без полей: 9»).
Stepper из этого списка выбыл после разлива: строка «Шаг… строка 24 → 48 px» поле получила. Строк в таблице 3…9, в среднем 5,7; радиус упомянут на 15
страницах из 38, рамка на 6 — «почему часть параметров выводится, а часть нет» объясняется только тем, что строки писал я
(единого правила вывода из CSS нет).

**Ловушка, стоившая прогона:** `page()` — это Python-`%`-шаблон, поэтому `'\n'` внутри JS попадает в файл реальным
переводом строки и скрипт падает (`SyntaxError: Invalid or unexpected token`, страница молча ничего не правит). Писать
`String.fromCharCode(10)`; быстрый диагноз — вытащить текст `<script>` из сгенерированной страницы и прогнать `node --check`,
либо вызвать его в пробнике через `new Function(txt)()` и прочитать ошибку.
Подробности механизма, код и план разлива на остальные страницы: `references/editable-mobile-values.md`.
Быстрая защита от главной ловушки (реальный перевод строки в JS → `SyntaxError`, страница молча ничего не правит):
`scripts/check-page-js.py` — вынимает `<script>` из всех сгенерированных страниц и прогоняет `node --check`.

**Разлив формата на все 38 страниц — партиями и через файлы-заготовки (13.09.2026).** Формулировка владельца:
«Давай доделаем страницы все. Итого везде на страницах нужно 4 колонка правки с изменением значений.
3 вариант превью с разными компонентами и главное чтобы компонент главный что исследуем тоже был.
И 3 колонки с рекомендациями по главному компоненту» — то есть тот же формат, что уже принят на
`button.html`, разлить на остальные. Схема: общее задание — `_audit/rec/out/SPEC.md`; исполнитель пишет
**только** свои файлы `out/<edits|previews|platforms>/<slug>.json` (одна заготовка = один компонент = один
блок) и не трогает `data/`, `build.py`, `mock.py`, `recommendations/`, сервер и браузер; слияние делает один
скрипт `_audit/rec/apply_out.py` (`--build` сразу пересобирает страницы, формат данных `indent=1` + CRLF
сохраняется). Комплектность проверяет `scripts/audit-edits.py`: `MISS` (селектор поля ничего не нашёл в
мобильной панели), `NOCHANGE` (подставленное число ни на что не влияет), `SCREENS` (экранов не три) и
расхождения «страница ↔ данные» по числу полей/экранов и наличию блока платформ. Псевдоэлементы (`::after`
тач-слоя) мерить `getComputedStyle(el, '::after')`, а `querySelector` брать по базе селектора — иначе
ложный `MISS`. Поле ставится на любую строку, где в Mobile есть число (в том числе равное десктопному),
строки без числа остаются пустыми. Полная схема, форматы заготовок, карта «slug → файл платформы»
(`radio` → `radio-button.json`, `hint-tooltip` → `tooltip.json`, `form-field` → `text-field.json`,
`table-2-lvl` → `table.json`, `snackbar` → `snackbar.json`) и состояние разлива:
`references/pages-bulk-fill-pipeline.md`.

**Что вылезло при проверке разлива (13.09.2026).** Итог: 3 экрана и 3 платформенные колонки — на всех 38 страницах,
рабочие поля «Правки» — на 29. `audit-edits.py` довёл `MISS / NOCHANGE / SCREENS / ERR` до нуля, но для этого пришлось
починить и заготовки, и сам харнесс:

- **Ложный `NOCHANGE` — три источника, все в проверке, а не в странице.** (а) фильтр «не мерить шорткаты `padding`/`margin`»
  выкидывал единственное свойство поля — мерить **все** свойства из `data-css`; (б) замер сразу после
  `dispatchEvent('input')` отдаёт значение **до** transition (ход ручки Slide toggle остался `matrix(…,20,0)` при правиле
  60 px) — мерить с паузой ~700 мс; (в) псевдоэлемент: `querySelector` по базе селектора, замер `getComputedStyle(el, '::after')`.
- **Настоящий мёртвый селектор — inline-стиль в разметке примера.** У `autocomplete` строка подсказки приходит из данных
  с `style="min-height:48px;width:auto"`; inline бьёт любой селектор, поэтому поле работает только с `!important` в своём
  `css`. Перед сдачей проходить строки, где свойство уже задано inline.
- **Настоящая проигранная специфичность.** Мобильный слой задаёт шаг степпера длинным селектором
  `.ds-stepper.ds-stepper--vertical .ds-step` (0,3,0) против `[data-mode="mobile"] .ds-step` (0,2,0) — поле обязано
  целиться тем же селектором, что и слой.
- **Классы сверять с CSS, а не по памяти.** В `mock.py` выбранный таб рисовался `ds-tab--selected`; в ДС такого класса нет —
  есть `ds-tab--active`, то есть табы в превью шли без стиля. Обратная ловушка валидатора: `ds-select-item__text` и
  `ds-input-number-but-icon--disabled` в CSS отсутствуют, но в разметке страниц есть — «класса нет в CSS» сам по себе не дефект.
- **Он проверяет глазами сразу** («Не вижу в колонке Правки чтобы можно было изменить какие-либо значения!»). После разлива
  снять скрин страницы и посмотреть vision-ом (поле + 3 экрана + 3 колонки), дать URL и напомнить один `Ctrl+F5`: «поля нет»
  одинаково означает и «эта страница из списка 9», и «вкладка открыта до слияния».
- Диагностика одного поля: `_audit/rec/checks/why-nochange.py` (элемент, его inline-стиль, текст `<style id="live">` до/после)
  и `why-rule.py` (какие вообще правила задают это свойство) — быстрее, чем гадать про каскад.

#### Приёмка блока «На экране» (13.09.2026)

Проверка — скриптом, а не взглядом: `audit-preview.py` печатает `COUNT` (экранов не столько), `NOCOMP` (нет класса
главного компонента), `DUP` (экраны совпали), `OVERFLOW` / `CLIPPED` / `EMPTY`. Из 36 новых превью править пришлось
четыре; определения детекторов, замеры и код — в `references/preview-screens-qa.md`. Кратко, что там важно:
классы главного компонента брать из его CSS (иначе `NOCOMP` ловит окружение); `OVERFLOW` пропускает элемент,
обрезанный контейнером ВНУТРИ экрана (прокрутка или `overflow:hidden`), и не пропускает вылезание за сам
`.phone__screen`; панель 360 px не уживается рядом с контентом в экране 375 px (нужен оверлей со своим `background`);
правила каркаса `.panel …` до экранов не доходят — дублировать для `.phone`; контент платформ проверять счётом
(`Counter` по `platform_notes_ru` + `logic_ru`, источник в скобках у каждого пункта).

Разбор четырёх страниц с замерами и кодом: `references/preview-screens-qa.md`.

#### Формат блока изменился: два экрана и панель «Что | Правка» (13.09.2026, вечер)

Владелец переиграл формат, который сам же заказал днём: «В превью нужно оставить 2 экрана мобилы вместо 3… показывать
одинаковый интерфейс с нашим основным компонентом… сам компонент разместить в разных местах… После 2 экрана, где стоял
3, поставить как раз нашу колонку из таблицы Правка. Вернее 2 колонки: Что и Правка», отдельно — «Колонка правка уезжает
наверх. В таблице ниже её не будет», и про строки — «если где-то написано тоже, также и похожие слова то это тоже
значания должны быть цифровые. Пусть они одинаковые с десктопом, но это цифры». Перед работой он потребовал подтвердить
понимание («Задача понятна? Сначала скажи что понятна»).

Каркас (`build.py`, образец `checkbox.html`, разлив — заготовками): `changes_table()` снова три колонки (Что / Desktop /
Mobile); `preview_card()` — `.editrow` = grid `minmax(0,1fr) 380px`: слева два экрана одного и того же интерфейса
(компонент в разных местах: тело ↔ шторка/шапка), справа `edits_panel()` — таблица «Что | Правка» с полями и подписью
«Правка применяется к правому экрану. Левый — значения как рекомендовано»; второй экран помечается
`data-preview="edit"`, правило пишется как `[data-mode="mobile"][data-preview="edit"].phone__screen <sel>{…}`;
`audit-edits.py` ждёт два экрана и печатает `LEAK` («правка задела первый, дефолтный экран»); «то же» в размерной
строке — только цифры (59 строк на 38 страницах, иначе `STILL-TAKZHE` в `check-patch.py`).
Капкан строковой сборки: `rstrip('</div></div>')` режет по символам, а не по суффиксу — после этого на странице было
четыре экрана и обрубок; править явным срезом суффикса и сверять `mock.check_balance()` + число `phones__item` ДО
записи в данные. Код, спека разлива и состояние — `references/preview-two-screens-and-edits-panel.md`.

#### Блок «На экране» — превью в корпусе телефона (12.09.2026)

После колонки «Правка» владелец сказал: «нам нужно какое-то внятное превью того как это выглядит на экране мобилы
в интерфейсе… есть предположения?» Из трёх вариантов (A — рамка вокруг той же панели, **B — экран-контекст из
компонентов ДС**, C — пересборка его реальных экранов `metro-general-settings`/`add-fasovka`) он выбрал **B**.
Реализовано на `button.html`: данные получают `preview_html`, `page()` рисует карточку `<h2>На экране</h2>` сразу под
панелями, внутри — flex-ряд `.phones` из трёх `.phone` (корпус 375 px, radius 40), экран `.phone__screen` помечен
`data-mode="mobile"`, поэтому в нём работают и мобильные значения ДС, и правила из `#live` (правка поля меняет кнопки
и в панели, и на всех трёх экранах). Три сценария — **разное расположение кнопок**: футер формы (две кнопки в ряд
пополам), действие в контенте (на всю ширину после чекбоксов), шторка снизу (кнопки в столбик на всю ширину).
Соседние компоненты берутся готовой разметкой из `data/*.json` (`.ds-input`, `.ds-checkbox`), подпись
`.phone__caption` — **вне** корпуса (иначе рисуется по чёрной рамке). Замер: кнопки на трёх экранах 44 → 40 вместе
с панелью, десктоп 36/28/24 и колонка Mobile — без изменений. Полный код, капканы и порядок расширения:
`references/screen-preview-phone-frame.md`.

**Меню рекомендаций — только названия компонентов.** «Убери в меню подписи размеры, структура и т.д. Это
лишнее» (12.09.2026): пункт меню — `<button class="nav__item" data-slug=…>Component</button>` без
`<span class="nav__note">`, правила `.nav__note` из каркаса удалены. Чип категории **на странице компонента**
остаётся — на вопрос «её тоже убрать?» ответ был «Там нужна. Только из меню».

**Скрины от владельца: вставку картинки в ACP-панель клиент не умеет — не предлагать.**
Расширение `formulahendry.acp-client 0.2.0` собирает промпт одним текстовым блоком (`sendPrompt` →
`[{type:"text",text:n}]`), обработчика вставки в его webview нет (`onDidPaste`/`dragover` отсутствуют),
а штатная `acp.attachFile` («Attach File to Prompt») шлёт webview сообщение `file-attached`, которого
в его `switch` нет — то есть не делает ничего. Адаптер Hermes блоки `ImageContentBlock` и `file://`
принимает (`acp_adapter/content.py`) — дело в клиенте, а не в агенте.
Захват буфера обмена и всплывающие плашки (скрипты `clip-save.ps1` / `screen-capture.ps1`,
`latest-shot.py`, папка `_shots`, справка в `references/`) **удалены 12.09.2026 по его слову**
(«Убери вообще нахрен» → «лишнее убирай») — не возвращать и не запускать заново.
Скрин от него — только файлом, путь он называет сам; признак «вставилось» бывает только там, где
вложения есть в композере: десктоп Hermes (`apps/desktop/src/app/chat/composer/attachments.tsx`,
`hooks/use-composer-drop.ts`, вставка из буфера даёт миниатюру) и `/paste` в терминальном Hermes.
Одну беседу в двух поверхностях не держать — turn встанет на lease.



Каталог найденных следов автогена (23 класса с `background` = `color`, nowrap, залитая обёртка кнопки
диалога, белая подпись светлого снекбара, тёмные подписи сайденава, контейнер без класса варианта) и код
нейтрализации в каркасе — `references/library-autogen-artifacts.md`.

### Иконки — отдельный класс «жести» (11.09.2026)

Владелец открыл готовые страницы и сказал: «Посмотри на иконки. Это же жесть, что ты понавставлял». Причём
размеры к тому моменту были верные — его взгляд ловит **нарисованное не по ДС**. На страницах стояли
самодельные SVG-треугольники вместо иконок (так вышло из-за проверки шрифта, которая отработала слишком рано).
Правило простое: рисуем только лигатуры Material Icons по имени, размер через `font-size`, свои SVG —
никогда. Приёмка страниц с иконками — скрин с `--virtual-time-budget=9000` (иначе лигатура попадёт в кадр словом)
и взгляд глазами: иконка должна читаться как значок, а не как прямоугольник или слово.
Разбор, карта «слот → имя» и код конвертации — `references/icons-material-ligatures.md`.

### Method — one component at a time

1. **Inventory the hardcoded values** in `components/<Name>_DS/*.css` and map each to an
   existing component token: `--ds-<comp>-<size>-size-{pad-top,pad-right,pad-bottom,pad-left,gap,icon-size,text-size,text-weight}`,
   `--ds-<comp>-border-radius`, `--ds-<comp>-border-size`.
2. **Tokenise first, and prove the desktop rendering did not move** (see verification).
   Express HUG heights as `calc(pad-top + pad-bottom + line-height)` instead of a height
   number — then a mode override changes only pads/type and the height follows.
   Button M: 8+8+20 = 36 px desktop, 12+12+20 = 44 px mobile. Sizes whose pixel value has
   no primitive (44) are reachable this way without inventing a Figma variable.
   Square components (Button icon) take the same treatment on **both** axes:
   `width: calc(pad-left + pad-right + icon-size)`, `height: calc(pad-top + pad-bottom +
   icon-size)` — M 8+8+20 = 36, S 4+4+20 = 28, XS 4+4+16 = 24; a mode override then moves the
   pads/icon and the square follows. Where a container has **no** height rule at all (Button
   toggle) do not add one: it is HUG by default and its content decides. У переключателя содержимое —
   **инстансы Button** (он надслойка над ними, см. Pitfalls), поэтому его высота = отступы трека +
   высота кнопки внутри, и на мобиле растёт вместе с Button; `height` фризил бы её против режима.
3. **Start from the component's row in the plan, not from the CSS.** `iiko-ds-mobile/desktop-to-mobile-plan.xlsx`
   (source: `.md`, generator `build-desktop-to-mobile-plan-xlsx.ps1`) is the per-component brief:
   group «Размеры / Размеры + поведение / Структура», what changes on mobile, how MD3 and Angular
   Material solve it, `_mob` status (Собран → Проверен → Готов), token binding. Read
   `mobile-workflow.md` / `mobile-steps.md` too — they demand the order **Desktop → Tablet (768) →
   Mobile** and the **журнал трансформаций** row (`Компонент | Desktop | Tablet | Mobile |
   Что изменилось | Категория`). Without that row the work reads as unfinished to the owner.
4. **Take mobile values from a source** (`Button_mob` in Figma / the comparison page — 12 `_mob`
   components already exist) and write only the differing tokens into `modes.css`. Colour, radius
   and shadow are not the mode's business — leave them alone.
4. **Verify in a real browser** — never report "44 px" from reading CSS.
5. **Document**: extend `iiko-ds-spec.md` with a section, its TOC entry, and the class-map
   row for any new modifier.

## Figma Dev Mode MCP — numbers that exist only on the canvas

The Figma desktop app serves the Dev Mode MCP on `127.0.0.1:3845`. Client: `scripts/figma-mcp.py`
(stdlib only). This is how a value that lives in the canvas but not in `tokens.css` gets read —
the `_mob` components above all. Node ids resolve **only inside the file currently open in the
desktop app**, so the ask to the user is short and concrete («переключи Figma на файл ДС и выдели
`Button toggle_mob`»), and `get_metadata` with no arguments is a cheap way to see which file is
live before asking. Full recipe, tool list, transport quirks and the exact error strings:
`references/figma-mcp.md`.

## Verification recipe (no browser approval needed)

Headless Chrome renders the page; the page records its own measurements into an attribute,
so the numbers are read back, not eyeballed:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu \
  --no-first-run --no-default-browser-check --user-data-dir="$TMP/udd" \
  --virtual-time-budget=5000 --dump-dom "file:///C:/path/to/demo.html"
```

`scripts/headless-measure.py` wraps that (render → extract `data-measure` JSON → optional
screenshot → optional regression diff). For screenshots use `--window-size=1440,2600
--screenshot=out.png` and then look at the PNG with vision.

**Chrome caches the CSS over `http://127.0.0.1:8899` — bust it or you measure yesterday's file.**
With a reused `--user-data-dir` the mode override looked like it was not applying at all (the Mobile panel kept
reporting 34 × 20 for Slide toggle while `modes.css` already held the new tokens). Use a fresh profile dir per
verification run or append `?v=<epoch>` to the URL (`python -m http.server` ignores the query, so the file is
refetched).

**С 11.09.2026 генератор штампует версию сам.** `build.py` считает `VER` = максимум `mtime` по всем CSS
`iiko-ds-web` + `iiko-ds-mobile` + `_audit/rec` и подставляет `?v=%(ver)s` в **каждую** ссылку на CSS
страницы компонента и в `src` iframe оболочки (`index.html`). Поэтому обычный F5 показывает текущий CSS,
а правка любого компонентного файла ломает кэш автоматически. Если увидишь ссылку без `?v=` — сборка
старая, перезапусти `python build.py`. Before reporting "the override does not work", read the variable itself:
`getComputedStyle(panel).getPropertyValue('--ds-…')` — if the token is right but the size is stale, it is cache
or specificity, not tokens. Details and the rest of the measured numbers: `references/mobile-mode-values-sizes.md`.

**Сервер тоже отдаёт no-store (12.09.2026).** В корне DS лежит `serve.py` — тот же
SimpleHTTPRequestHandler, но с `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`. Запускать его вместо
`python -m http.server`; старый сервер (без заголовка) кэшируется браузером по эвристике (≈10 % от возраста файла),
и тогда **владелец видит старый CSS в своей вкладке**: `tokens.css` от 8 сентября мог держаться часами, а мобильная
панель показывать десктопные числа. Если он говорит «у меня другое число / ничего не поменялось» — сначала
предложить один `Ctrl+Shift+R` (обычная F5 не перезапрашивает подресурсы), а не спорить с замерами: у агента
профиль свежий, у него — нет.

**The honest regression test** is against the previous version of the CSS, not against
Figma alone: dump the old file with `git show HEAD:<path> > old.css`, render the same
markup with old and new CSS in two temp pages, and diff the measured JSON. For the Button
refactor that showed all 45 size×style×type combos keeping identical heights, with exactly
two intended deltas (XS icon 20→16 px, line-height 14/12→20/16 px).

**Re-copy the current component CSS into the harness dir before every re-run.** The harness copies the
files once, so a later diff against a stale snapshot silently prints `changed fields: 0` — exactly what
happened after the Button icon disabled-state fix until the copy was refreshed (then it showed the intended
`bg #448AFF → #EBEBEB`, `color #FFFFFF → #9E9E9E`).

## Pitfalls

- `tokens.css`, `styles.css` and most of `iiko-ds-spec.md` are **generated** — put
  overrides in `modes.css`, append new spec sections instead of rewriting generated ones.
- **The repo is CRLF everywhere; `write_file` writes LF.** Normalise new files
  (`\n` → `\r\n`) or the diff looks like the whole file changed.
- **`patch` fails to match an `old_string` that ends with a trailing newline** in these
  files. Drop the trailing newline (keep the context otherwise unique) and it matches.
- **Build the regression matrix from the spec class map, and render the component twice: as `<div>`
  and as `<button>`.** The documented axes are Type × Content (`--filled/--outlined` ×
  `--text/--icon`) × Size, and a `<button>` carries a UA default `border: 2px outset` that the
  div (the spec's own markup) does not. Skipping the button hid three real defects in Button toggle:
  `--s` is a no-op (icon 20 = base), `--xs` shrinks only the icon so the segment keeps the base
  height (the label line-height holds it), and `--filled --icon` on a `<button>` keeps the 2px UA
  border → 32 px instead of 28. Report such findings; do not silently "fix" them.
- **After refactoring a component, the spec's CSS copy goes stale.** «Стили компонентов» in
  `iiko-ds-spec.md` is one giant generated fence (≈ lines 10790–17324) whose own rule is
  «сначала автоген всех компонентов, затем ВЫВЕРЕННЫЕ вручную файлы». It still showed the old
  `.ds-btn--m { height: 36px; padding: 8px 12px }` after the Button refactor. Do not hand-edit that
  block — say it is stale and ask for a regeneration (his generator), or offer a mechanical re-sync
  from the component files.
- **`browser_exec` driver code must be pure ASCII on this host**: кириллица в комментарии драйвера приезжает
  в ANSI-кодировке (0xC7 = «З» в cp1251), а клиент декодирует stdin как utf-8 →
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc7` и пустой вывод. Русский текст — в файл страницы,
  драйвер — ASCII. Плюс интерактивному браузеру нужен тик «Allow remote debugging» в Chrome: если владелец его
  не давал — не ждать и не просить, а взять те же числа headless-пробниками (раздел «Verification recipe»).
- The interactive browser tool may ask for Chrome remote-debugging approval; headless
  Chrome (above) needs none, so verification is never blocked on a click.
- **Don't resolve design questions yourself.** Touch target for S/XS, hover policy on
  touch, radius (8 px vs MD3 pill), 44 vs 48 dp are the owner's calls — report them as
  open questions with a recommendation.
- **Repo boundaries:** `iiko-ds-web` and `iiko-ds-prototypes` are each their own git repo
  (origin `Anders7Rusk/*`, branch `main`); `iiko-ds-mobile` and the `DS/` root are not repos.
  Check `git -C <repo> status` and **ask before committing or pushing** — publishing updates
  the live Pages spec.
- **Never delete a prototype/demo page — or the README/spec pointers to it — on your own
  initiative.** The user reversed exactly that call within the hour and asked for the page
  back: he reads the desktop/mobile difference off it (Figma's mode is file-global). Mobile
  demos live in `iiko-ds-mobile/prototypes/`, the rest in `iiko-ds-prototypes/`; when one is
  added, its path belongs in `iiko-ds-mobile/readme.md` and in the spec's «Живая проверка».
- **Recover, don't reinvent:** a file you deleted or overwrote is still in the session store —
  `state.db` keeps every `write_file` payload plus the follow-up edits that moved it. See the
  `session-store-forensics` skill, `scripts/recover-file-from-state-db.py`.
- **По мобиле источник — только уже собранные рекомендации платформ.** `DS/_audit/platform/<slug>.json`
  (+ `_raw`, `_src`) и пайплайн `_audit/rec` (`data/<slug>.json` + `data-tech/<slug>.json` → `build.py` →
  `iiko-ds-mobile/prototypes/recommendations/`). В Figma по мобильным **не ходить** и `_mob` оттуда не
  читать — прямая формулировка владельца: «Не надо лезть вообще в фигму и что-то там смотреть. По мобильным
  компонентам мы пользуемся только теми рекомендациями что есть тут». Figma-MCP применим только когда он сам
  об этом просит и нужный файл открыт в приложении (MCP читает активный документ, а не любой nodeId).
- **Мобильное число выводится из рекомендаций + примитивов ДС, а не из Figma.** Button icon: 40 dp —
  единственный размер контейнера, который называют M3 (state-layer 40, иконка 24) и Angular Material
  (`icon-button-state-layer-size` 40 на плотностях 0…−2); собирается из примитивов: pad 10 (`--ds-space-2-5x`)
  `+ иконка 20 = 40 (у Button было 12+12+20 = 44). Тач-таргет 48 dp и хит-регион 44 pt — **отдельным слоем**, высотой элемента их не набирать.
  **Но мобильные значения нужны ВСЕМ размерам, а не только базовому.** Первая версия подняла только M, оставив S/XS десктопными —
  владелец открыл мобильную панель и сказал: «Нигде ничего не поменялось. Я вижу одинаковые размеры по многим компонентам как и у десктопа».
  Он прав: плотные варианты ниже любого платформенного минимума, поэтому на мобиле они поднимаются до тач-минимума.
  Числа, которыми это делается (все — из `_audit/platform/*.json`): кнопка с текстом — 44 у всех размеров (iOS HIG «a button needs a hit region
  of at least 44x44 pt» + план «минимум для веба — 44 px»; плотности Angular 40/36/32/28 — не мобильные размеры), иконка-кнопка — 40 у всех
  (дефолт MD3, Angular density 0), тач-зона 48 — невидимым слоем `::after` (`position:absolute; left/top:50%;
  width/height:100%; min-width/min-height:48px; transform:translate(-50%,-50%); background:none`) в
  `iiko-ds-mobile/components/Button_DS/button-touch.css`. Строка (а не сам элемент) дорастает до 48 у чекбокса/радио
  (`Checkbox_DS/checkbox-touch.css`), тумблера (`Slide-Toggle_DS/slide-toggle-touch.css`) и шага вертикального степпера
  (`Stepper_DS/stepper-vertical.css`, `min-height:48px` — у Angular хедер шага 72 px, минимум 42).
  Формулы HUG делают это бесплатно: Button S 12+12+20 = 44, XS 14+14+16 = 44; Button icon S 10+10+20 = 40, XS 12+12+16 = 40.
  Замеренная регрессия: desktop 36/28/24 → mobile 44/44/44 (Button), 40/40/40 (иконка), тач-слой 48 у каждой.
  У Button toggle своих мобильных чисел нет вовсе: сегменты — инстансы Button, они растут по его режиму,
  трек — за ними.
- **В сгенерированном компонентном CSS состояния могут стоять ВЫШЕ блоков Style×Type** — тогда
  `.ds-btn-icon:disabled` (0,2,0) проигрывает `.ds-btn-icon--accent.ds-btn-icon--filled` (0,2,0) по порядку,
  и disabled выглядит как активная кнопка. У Button те же правила стоят в конце файла — выравнивать по нему:
  состояния после стилей. Проверка — `getComputedStyle(el).backgroundColor` у disabled и у обычной кнопки.
- **У Button toggle состояния были не только перепутаны, но и не применялись.** Фон Filled брался из
  компонентного токена `Button toggle/Filled/Background` = `Shapes/Default` = `#FFFFFF`; цвета контейнера
  были swapped (filled ≈ outlined-текст, outlined ≈ filled-текст = Text/Inversive = белый); а
  `.ds-button-toggle__label` жёстко красился в accent — поэтому состояние не влияло на текст вообще.
  Правильно: вешать цвет на сам модификатор (`.ds-button-toggle--filled` / `--outlined`) без требования
  пары с `--text`/`--icon` (иначе разметка из спеки рендерится белой). Но само оформление сегмента
  переключателю не принадлежит — см. следующий пункт.
- **Button toggle — надслойка над Button, а не кнопка.** Внутри него лежат ИНСТАНСЫ `.ds-btn` (в Figma слот
  назван «Button container» [59885:13]), поэтому `.ds-button-toggle` — трек-контейнер: `inline-flex`, отступы 4,
  промежуток 4, радиус 12, фон/рамка из `--ds-color-button-toggle-*` — и всё. Рамка живёт в **базовом** правиле
  контейнера (1 px `--ds-button-toggle-outlined-border-size` / `--ds-color-button-toggle-outlined-border-color`):
  она у трека всегда, у Filled и Outlined одна и та же, поэтому и высоты типов совпадают. Если повесить `border: none`
  на `--filled` (так написано в автогене спеки) — трек на белом фоне просто исчезает; владелец поймал ровно это:
  «Где рамки у баттон тогглов? Баттон тогл это контейнер с рамкой, в который вставлены инстансы кнопок». Вид сегмента (фон, рамка, текст,
  hover/press/disabled) задаёт Button со своими токенами и своим мобильным режимом. Собственных мобильных
  значений у переключателя нет, и `height` ему не задавать: высоту дают кнопки внутри. Замерено 12.09.2026
  на **откаченной** библиотеке (важно: у трека `box-sizing: border-box`, поэтому рамка входит в высоту —
  более ранние 46/54 были посчитаны с рамкой снаружи и оказались неверными): трек с сегментом M — 44 px,
  с S — 36, с XS — 32; на мобиле все три сегмента 44 → трек 52 у любого размера. Трек шириной/высотой не
  задавать и на мобиле: он HUG и следует за кнопками. Элементные правила `__label`/`__icon` в его CSS —
  артефакт автогена, в контейнерной модели не используются.
  Цена ошибки: я принял его за сегмент, и когда «выбранный» вышел белым (токен трека = `Shapes/Default` =
  `#FFFFFF`), подставил в фон токены Button Filled (`--ds-color-button-accent-filled-*`). Владелец это отклонил:
  «Он у нас совсем не так оформлен!». Токены чужого компонента в оформление не подставлять; если свои дают
  странный результат — сказать об этом и спросить, а не «чинить» на свой вкус.
- **Геометрию, которой нет токена, выводить формулой из тех, что есть.** Slide toggle: в CSS были числа
  (трек 34 × 20, ручка 16, отступ 2, `translateX(14px)`), токенов на ширину/высоту трека нет. Выражения
  через существующие токены воспроизводят десктоп **и** дают платформенное мобильное число:
  `--_st-track-w: calc(ручка * 2 + отступ)` = 34 → 52, `--_st-track-h: calc(pad-top + ручка + pad-bottom)`
  = 20 → 32, позиция ручки `left: calc(100% − ручка − selected-pad-right)` = 16 → 24 (вместо магического
  сдвига), отступ подписи = ширина трека + промежуток (42 → 60). Общие выведенные значения держать
  в локальных переменных компонента (`--_st-*`) на корне, а не дублировать в правилах. Регрессия по замерам
  обязана показать 0 отличий на десктопе — если не показала, формула не эквивалентна старому числу.
- **Семейство токенов у Form field — `--ds-form-field-*`**, не `--ds-input-*` (`--ds-input-number-*`,
  `--ds-input-datepicker-*` — это другие компоненты). Высоты 48 / 36 / 28 = `calc(паддинги + строка ввода)`,
  мобильные M-паддинги 16 дают 56 (MDC Web `$height: 56px`, Angular `form-field-container-height` 56 при
  density 0). У XS кегль ввода 14 px — на телефоне iOS зумит поле при фокусе (правило «≥ 16 px»), это
  открытый вопрос, а не то, что правит агент.
- **Card — компонент, у которого мобильных чисел НЕТ вообще, и это правильный результат, а не недоделка.**
  MD3 у карточки задаёт только радиус corner-medium 12 dp, обводку 1 dp и иконку 24 dp — **токена
  внутренних отступов у неё нет**; 16 px существует как `$mat-card-default-padding` в Angular Material
  («the standard padding specified in the Material Design spec»), а `density` у карточки там `()` — пусто;
  страницы Cards в iOS HIG нет вовсе (404). Значит `modes.css` для Card остаётся пустым, а единственное
  мобильное изменение — раскладка (одна колонка, вся ширина), то есть правило страницы (категория 3),
  а не компонента. Токенизировать можно только то, что совпадает по значению (радиус 8, рамка 1, gap
  шапки 8, типографика заголовка/подписей) — регрессия обязана дать 0 отличий (Card: 0 из 4 типов).
  Токены, которые расходятся с выверенным CSS, **не подставлять**: `Card/Pad left/right` = 24 против 16,
  `Card/Content/Pad top/bottom` = 8 против 16, `Card/Header/Pad top` = 24 против 16 (в самом файле помечен
  как устаревший `Space/6x`), `Card/Footer/Pad top/bottom` = 16 против 4/16. Это находки для дизайнера.
- **Checkbox и Radio после отката библиотеки снова системные.** Агрегатор `iiko-ds-web/components/index.css`
  подключает у них только `*-label.css`; `checkbox.css`, `checkbox-icons.css`, `radio.css`, `radio-icons.css`
  не подключает никто. Признак в замере: `.ds-checkbox` = `display:inline`, высота 0, а `input[type=checkbox]`
  нарисован браузером 13 × 13 (12.09.2026: 21 такой контрол на страницах Checkbox, Radio, List). Лечение в
  МОЕЙ зоне — 4 `<link>` на страницу в `_audit/rec/build.py`; после них маркер 20 × 20, `gap 8px`, нативный
  input 0 × 0. Библиотеку не править (4 импорта в агрегатор — предложить владельцу одной строкой).
- **Button icon: disabled выглядит активной.** В `Button-Icon_DS/button-icon.css` блок состояний (строки
  62–79) стоит ВЫШЕ блока «Стиль × Тип» (с 93-й), специфичность равна (0,2,0) — побеждает стиль. Замер:
  disabled `#448AFF`/`#FFFFFF`, после нейтрализации в каркасе `#EBEBEB`/`#9E9E9E`. У Button те же правила
  стоят в конце файла, поэтому Button корректен — сравнивать компоненты между собой, а не только с макетом.
- **`min-height` «по фрейму Figma» — семейство из 24 правил.** `menu-container 418`, `select-container 406`,
  `list-container 257`, `dialog-view 364`, `dialog-content 204`, `picture__crop 189`, `hint-footer 56`.
  На страницах видно у трёх контейнеров (контент 144/155/158 против 418/406/257). В каркасе у контейнеров
  `min-height:0`; библиотека не правится. Проверять детектором `VOID`, а не глазами: у остальных правил
  контент фрейм заполняет.
- **Подпись-подсказка textarea: `height: var(--ds-size-4x)` = 16 px при строке 19 px** — три пикселя срезаны
  (`CLIPPED`-детектор). В каркасе `height:auto`.
- `scripts/audit-mobile-values.py` был сломан и печатал «40 проверок сломано» при здоровом мобильном слое:
  (а) копия страницы с драйвером писалась в профиль Chrome, а URL считается от `base_url` → 404 → все значения
  пустые; (б) в spec драйвера уходили `c[2],c[3],c[4]` — свойство вместо селектора, `querySelector('height')`
  ничего не находил. Исправлено 12.09.2026: копия кладётся рядом с оригиналом, spec = `[c[1],c[2],c[4]]`.
  Если скрипт разом показывает «сломано всё» — сначала смотреть эти две вещи, а не мобильный слой.
  Проверку ширины sidenav заменил на `max-width: 100%`: в панели 375 px с паддингом 12 число 360 недостижимо
  (замер 349), это ограничение харнесса, а не дефект слоя.
- **Одинаковые размеры в панелях Desktop и Mobile — не автоматический дефект.** Прежде чем «доделывать»,
  проверить, есть ли у платформы мобильное число вообще; если нет — написать это прямым текстом с
  источниками (Card выше). Тянуть число из соседнего компонента или «по плотности» — то, за что владелец
  откатывает правку.
- **Мобильное правило может «не применяться», потому что CSS компонента вообще не подключён.** 12.09.2026:
  `min-height: 48px` из `Checkbox_DS/checkbox-touch.css` давал 48 px в одной разметке и 19 px в другой.
  Причина — агрегатор `iiko-ds-web/components/index.css` подключал у Checkbox и Radio **только `*-label.css`**
  (описание строки), а сами контролы `checkbox.css`, `checkbox-icons.css`, `radio.css`, `radio-icons.css`
  не подключал никто: ни агрегатор, ни одна страница в DS. Без них `.ds-checkbox` остаётся `display: inline`,
  а **у non-replaced инлайн-элемента `min-height` не действует**; в `display:flex`-строке тот же элемент
  становится flex-элементом — и высота применяется. Отсюда «в одном примере работает, в другом нет»
  при формально верных токенах. Порядок разбора: (1) есть ли файл в агрегаторе
  (`grep -n "<Имя>_DS/" iiko-ds-web/components/index.css`), (2) какой `display` у элемента в реальной
  разметке (inline → `min-height`/`height` молча игнорируются), (3) только потом кэш и специфичность.
  Готовый прогон — `scripts/verify-mobile-values.py`. Исправлено добавлением 4 импортов в агрегатор;
  замер до/после: `display:inline` без маркера → `display:flex`, маркер 20 × 20, цвета состояний.
- **Документированная высота ≠ измеренная: проверять `box-sizing`.** 12.09.2026 у числового поля стояло
  `.ds-input-number__frame { height: 48px }` **без `box-sizing: border-box`** — на экране кадр был **74 px**
  (48 + паддинги 12/12 + рамка 1/1), то есть числовое поле выходило выше обычного поля и не совпадало
  со своей же спекой. Тот же content-box у `.ds-textarea__input-frame { height: 76px }` — рендерится 94.
  В ДС border-box и content-box идут вперемешку (кадр поля формы — border-box, эти два — нет). Признак:
  разница ровно на сумму паддингов и рамки. Лечение — `border-box` плюс формула
  `calc(pad-top + pad-bottom + line-height)`, как у кадра поля формы: тогда десктоп 48 и мобила 56 приходят
  из токенов, и отдельный мобильный файл не нужен. Десктопное число при этом меняется (74 → 48) — сказать
  об этом прямым текстом и предложить откат одной строкой.
  **Дефект семейный, а не единичный** — искать его надо grep-ом, а не глазами: пройти по всем компонентным CSS
  и найти правила с `height: <N>px` без `box-sizing` **в том же правиле**, затем сравнить `getComputedStyle().height`
  с `getBoundingClientRect().height` (разница ровно на сумму паддингов и рамки = content-box). Полный прогон
  12.09.2026 дал 46 таких правил, из них реально ломались 10: пять кадров полей (`input-number`, `select-form`,
  `autocomplete-form`, `input-datepicker`, `input-timepicker` — все 48 → 74) и четыре блока с объявленной высотой
  и паддингами (блок действий диалога `dialog-footer`/`dialog-view` 68 → 100, ряд кнопок меню 52 → 68, ряд кнопок
  селекта 44 → 60), плюс `textarea__input-frame` 76 → 94. Остальные 36 — иконки, разделители и точки без паддингов:
  им content-box безвреден, не трогать. Кадры полей лечить формулой (как выше), блоки действий — одним
  `box-sizing: border-box`.
- **Тестовая страница обязана подключать оба мобильных файла, и разметка между прогонами не меняется.**
  Харнесс, который линкует только `modes.css` (токены) и забыл `iiko-ds-mobile/components/index.css`
  (агрегатор), молча теряет все `*-mobile.css` / `*-touch.css` и печатает десктопные числа — читается
  как «правило не применяется» (список 68 вместо 72, шапка 44 вместо 48, тач-слой 0 вместо 48). Порядок:
  font → tokens → modes.css → mobile components/index.css → styles → web components/index.css. И не менять
  HTML между «до» и «после»: подмена внутреннего элемента числового поля дала фальшивую регрессию 74 → 50.
- **Каркас страницы рекомендаций перебивает собственные ширины компонентов — и это выглядит как «правило не работает».**
  12.09.2026: панель меню 240 px и поле поиска 243 px на странице рисовались по 876 px, а мобильное «на всю ширину»
  выглядело одинаково в обеих панелях. Причина — правило каркаса `.ex__row--col > * { width: 100% }` в `rec.css`
  (генерируется из `CSS` в `_audit/rec/build.py`): при равной специфичности оно грузится последним и давит
  `width` самого компонента. Лечение уже в генераторе: каждый пример оборачивается в нейтральный
  `<div class="ex__inner">` (`.ex__inner{display:flex;flex-wrap:wrap…}`), каркас растягивает обёртку, а компонент
  внутри сохраняет свою ширину. Если правишь `panel()` или `rec.css` — проверь, что обёртка на месте.
  Два родственных капкана того же дня: (а) **инлайновые размеры в разметке примеров** (`style="width:240px"`,
  `min-height:36px`) побеждают любые мобильные правила — из примеров их вычищать, ширину должен давать CSS
  компонента; (б) для полноширинных мобильных контейнеров писать `width: 100%`, а не `auto`: в flex-контексте
  `auto` сжимается по содержимому (меню 240 → 179 вместо полной ширины).
- **Специфичность мобильного слоя, когда базовое правило состоит из двух классов.** Мало повторить класс один раз
  (`.ds-stepper.ds-stepper--vertical`): у Sidenav база — `.ds-sidenav-item--l1.ds-sidenav-item--expanded` (0,2,0),
  и мобильное `[data-mode="mobile"] .ds-sidenav-item` (0,2,0) проигрывает по порядку. Приём — повторить класс:
  `[data-mode="mobile"] .ds-sidenav-item--l1.ds-sidenav-item--expanded.ds-sidenav-item--expanded` (0,3,0).
  Признак такой же, как у Stepper: часть свойств применилась, часть нет.
- **Глобальный селектор в мобильном файле одного компонента перебивает другие компоненты.** Мобильный слой
  грузится как **один плоский CSS** (`iiko-ds-mobile/components/index.css`), поэтому правило без привязки
  к своим классам живёт для всей страницы: строка `[data-mode="mobile"] .ds-list-item { min-height: 48px }`,
  написанная в `Autocomplete_DS/autocomplete-mobile.css` «для строк подсказок», молча перебивала List
  (нужно 72) и Menu (72) — просто потому, что autocomplete-файл подключён позже. Признак: на странице
  компонента значение равно мобильному числу **другого** компонента. Правило: каждый мобильный файл
  трогает только классы своего компонента (`.ds-autocomplete-*`), а не универсальные `.ds-list-item` /
  `.ds-menu-item`; проверить grep-ом по мобильному слою перед добавлением нового правила.
  Проверено на живой странице: List показывал 48 вместо 72, Menu — 48 вместо 72, при формально верных файлах.
- **Замер «на всю ширину» сравнивать с content-box панели, а не с `.panel__body` целиком.** `getBoundingClientRect()`
  тела включает паддинги 16×2, поэтому полноширинный контейнер (725) выглядел как «МИМО» против тела (757) и
  наоборот — ложная тревога ровно на 2 × 16 px. Верный ориентир — `clientWidth` минус паддинги, либо ширина
  соседнего полноширинного элемента.
- **Сетка каркаса `1fr 1fr` против `minmax(0,1fr)`.** С `minmax` панели строго равны, но широкий пример
  (горизонтальный степпер на шесть шагов) начинает вылезать за панель; с `1fr` контент растягивает панель
  (разная ширина панелей на разных страницах, зато без выхода за границы). Оставлено `1fr 1fr`:
  выход за границы читается как сломанная вёрстка, разная ширина — нет.
- **Контейнеры ДС строятся на классе варианта.** `.ds-hint-container` без варианта остаётся
  `display:flex` строкой (колонкой его делают `--default`/`--up`/`--down`), и подвал уезжает за панель —
  замер 83 px. Образцы разметки сверять с вариантами в CSS компонента, а не только с классами элементов:
  признак — блоки лежат в ряд, хотя в макете столбиком.
- **«Почему не применились токены» — три разных случая, и ответ обязан идти от того, что ВИДНО на экране.**
  12.09.2026 владелец открыл `index.html#hint-tooltip` с этим вопросом, а на ответ таблицей `getComputedStyle`
  сказал: «Нихрена не понял что ты написал… Я блядь не вижу радиусы 8 px». Порядок разбора: (1) какой элемент
  **рисует** то, что он видит; (2) объявлено ли свойство у него; (3) читает ли CSS токен вообще. Случаи:
  (a) **токен объявлен, правил с ним нет** — у Hint 8 из 25 `--ds-hint-*` не встречаются ни в одном CSS-правиле
  (`--ds-hint-arrow-height/-width`, `--ds-hint-content-text-size/-weight`, `--ds-hint-header-text-size/-weight`,
  `--ds-hint-footer-title-size/-weight`): подписи берут `--ds-font-caption-l-12-normal-regular-*` и
  `--ds-font-body-s-14-normal-medium-*`. Значения совпадают, поэтому визуально «всё верно», а токены мёртвые.
  Проверка — grep: объявленные (`tokens.css`) минус читаемые (`var(--…)` по всем CSS); если имя встречается ещё
  только в `iiko-ds-spec.md` — правил с ним нет нигде;
  (b) **свойство объявлено не на том элементе, который рисует** — радиус 8 px живёт на `.ds-hint-container` с
  **прозрачным** фоном, а видимые тёмные плашки (`.ds-hint-header/__content/__footer`, фон #424242) имеют
  `radius: 0`. Вывод «замер показал 8 px» ничего не доказывает: скруглять нечего, углы всегда прямые;
  (c) **элемента нет в разметке** — `.ds-hint-container__arrow` не встречается ни в одном примере страницы, так что
  токены стрелки вообще ни при чём. Что при этом реально применилось (числа для отчёта): контейнер 250 → 349 px,
  кнопки подвала 77 × 28 → 149 × 44, подпись 12/16 в обоих режимах; `modes.css` для hint пуст — категория
  «Структура», мобильных размеров у компонента нет по плану.
- **`__label`-классы не взаимозаменяемы между состояниями.** `.ds-elements-2__label` в ДС белый
  (`--ds-color-text-inversive`) — это цвет **выбранной** строки времени; в невыбранных строках текст —
  обычный `<span>` (иначе белое по белому), а выбранная строка получает `.ds-elements-2--selected`.
  То же у Snackbar (подпись жёстко белая) и у сайденава (подписи тёмные на тёмной панели) —
  проверять контраст, а не только наличие класса.
- **Touch targets come from Material's mechanics, not from growing the button.** MD3 requires a
  48 × 48 dp target; Angular Material puts it in a separate `.mat-mdc-button-touch-target` element
  that density does not shrink. So for S/XS on mobile: keep the DS height and add a touch layer,
  do not stretch the component. Numbers and sources: `iiko-design-system`,
  `references/material-mobile-button.md`.
- **Platform recommendations come from primary sources, and `web_extract` is not required to get
  them**: when it answers `403 Keyless Exa …`, fetch the same URLs with `curl -sL`. Material's real
  numbers live in `material-components/material-web` (`tokens/_md-comp-*.scss`,
  `button/internal/_touch-target.scss` → `height: max(48px, 100%)`), Angular's in
  `angular/components` (`src/material/**/*.md|*.scss`). `m3.material.io` and `developer.apple.com`
  are client-rendered — curl returns no numbers from them.
- **Never assume "the behaviour does not change on mobile".** The user caught exactly that:
  a line saying «те же состояния (hover, press, disabled, loading)» was wrong because hover is
  not shown on touch. Check `:hover` / `@media (hover: none)` in the component CSS before
  claiming it, and reuse the platform wording already collected instead of improvising it.
  Numbers, quotes and source paths: `iiko-design-system`, `references/hover-and-states-on-touch.md`.
- **When platform recommendations were harvested before, read them, don't reason afresh.**
  They sit in `DS/_audit/platform/<slug>.json` (`_raw`, `_src` hold the raw exports) — grep
  there first; the user reads a memory-based answer as "inventing your own thing again".
- **He may explicitly ask for work «по рекомендациям», not «сравнение с Figma».** Then the source
  of truth is MD3 / Angular Material / iOS HIG and the DS's own CSS+tokens; do not pull the
  `_mob` components or the comparison pages in, and do not answer with clarifying questions only —
  act on the obvious reading, state the assumptions, say what to change if the format is off.
  Recipe: `iiko-design-system`, `references/platform-recommendations-pages.md`.

- **Владелец правит `iiko-ds-web` параллельно, прямо во время сессии.** 11.09.2026 в 20:34–20:37 у него сами
  поменялись `font.css` (вшитый base64 Roboto → онлайн-`@import` Google Fonts) и `iiko-ds-spec.md` (пункт
  «Иконки» переписан на Material Icons по имени). Перед фразой «в библиотеке чисто / это не моё» перечитать
  `git status` и `git diff --stat` в репозитории и посмотреть первые строки каждого дифа. Файл изменён не
  тобой — сказать это прямо и сверить свои страницы с новой версией (шрифт, иконки), а не молчать и не
  приписывать правку себе.
- **Временные страницы-проверки не оставлять в папке рекомендаций.** Детекторы и пробники (`_plates.html`,
  `_overflow.html`, `_contrast.html`, `_fonttest.html`, `_probe*.html`, листы скринов) живут в
  `_audit/rec/checks/`; в `iiko-ds-mobile/prototypes/recommendations/` — только страницы компонентов,
  `index.html` и `rec.css`. Лишние артефакты в папках ДС его раздражают.
- **Уборка — только по слову, и всегда с отчётом списком.** Развязка 12.09.2026 (скрины/уведомление) прошла
  цепочку: «Мне не нужно показывать что что-то сохранилось» → «Убери уведомление» → «Убери вообще нахран» →
  «То что ты тут лишнее сделал убирай по этому вопросу». До слова «убирай/удали» свои временные файлы,
  папки и скрипты не трогать вообще (это тот же капкан самодеятельности); после слова — удалять можно
  смело и не спрашивая по каждому файлу, но в ответе дать два списка: что удалено и что **оставлено**
  (рабочие детекторы, чужие файлы). Если сам сомневаешься, удалять ли что-то — спросить одной строкой.
- **Куратор копирует рабочие скрипты из репозитория в скилл — убирать надо в обоих местах.** После удаления
  `_audit/rec/checks/clip-save.ps1` и `latest-shot.py` их копии нашлись в
  `skills/software-development/iiko-ds-components/scripts/` (в `skills/.curator_ledger.jsonl` — actor `curator`).
  Порядок уборки любого механизма: (1) файлы в репозитории, (2) копии в `scripts/` скилла, (3) упоминания в
  `SKILL.md` и `references/*.md` (включая секцию Support files), (4) мёртвые ссылки на удалённое в чужих
  справках — переписать описание приёма без пути к файлу (так сделано с пробником `_raw.html` в
  `desktop-side-defects-and-detectors.md`: «собери одноразовую страницу, потом удали», а не «смотри `_raw.html`»).

## Reporting to this user

- **Формат для всех страниц: 3 тезиса-колонки + 3 макета (12.09.2026).** «Такие небольшие тезисы нужны будут везде,
на всех страницах. Как и 3 превью мобилы с разными компонентами и тем что исследуем».
Что значит формат на каждой странице: (а) блок «Что говорят платформы» — три колонки: **Material · iOS HIG ·
Логика (от себя, без источника)**; пункты короткие (1–2 строки), с числами и ссылкой на файл выгрузки в скобках
(«(button-icon.json)»); берутся **дословно** из `platform_notes_ru` / `logic_ru` в `data/<slug>.json`, ничего не
дописывая от себя; (б) `preview_html` — три макета телефона, в каждом исследуемый компонент в другой роли + соседние
компоненты ДС (взятые готовой разметкой из `data/*.json` других страниц). Сборка макетов — `_audit/rec/mock.py`
(хелперы `screen/phones/head/body/foot/line/actions/icons/lst/btn/iconbtn/chips/tabs/sheet/...`,
`check_balance()` для баланса тегов). Готово: Button, Button icon; остальные 36 — по батчам, потому что тезисы
пишутся руками по выгрузкам, а не генерируются.

**Платформы на странице — только написанный текст, не выгрузка (12.09.2026).** Первая версия блока выводила
`_audit/platform/<slug>.json` напрямую: числа из `sizes` строкой «xsmall — 32», заметки в свёрнутом `<details>` —
на это прилетело «какую хуйню ты мне там написал… У тебя выше написано всё уже. Текстом ты всё написал. Вытащи это
на страницу». Правильно: блок «Что говорят платформы» берёт поле `platform_notes_ru` из `data/<slug>.json` —
список разделов `[{title: "Material", items: [...]}, {title: "iOS HIG", items: [...]}]`, пункты вставляются дословно,
плюс отдельный блок «Логика (от себя, без источника)» из `logic_ru`. Выгрузки — источник правды для текста, но
на страницу идёт отредактированная формулировка; переносить выгрузку как есть нельзя.

**Блок «На экране» — превью в корпусе телефона (12.09.2026).** Правки размеров в таблице надо видеть ещё и «в интерфейсе»,
а не только в панели. Реализовано в каркасе страниц рекомендаций: поле `preview_html` в `data/<slug>.json` + в `build.py`
блок `<div class="card"><h2>На экране</h2>…` сразу под панелями Desktop/Mobile. Внутри — `.phones` (флекс-ряд, 3 экрана
375 px помещаются), каждый экран: `.phones__item` → `.phone` (корпус) → `.phone__screen[data-mode="mobile"]`
(экраны: статус-бар, шапка, строки, футер/шторка). Ключевое: экран помечен `data-mode="mobile"`, поэтому
и мобильные значения, и правила из `<style id="live">` (колонка «Правка») действуют и внутри корпуса.
Соседние компоненты берём только готовой разметкой из `data/*.json` других страниц (`ds-input`, `ds-checkbox`,
`ds-btn-icon`, `ds-search`, `ds-list-container`, `ds-tabs`, `ds-chips`, `ds-slide-toggle`, `ds-radio`, `ds-divider`) —
своих вариаций не выдумывать. Капканы: (а) `preview_html` — готовая HTML-строка, поэтому
баланс `<div>` проверять парсером (`HTMLParser`), а не глазами; подпись экрана должна быть **сестрой** корпуса
внутри `.phones__item`, иначе она рисуется внутри чёрной рамки; (б) кнопки другого компонента (иконка-кнопка
`ds-btn-icon`) полями страницы Button НЕ правятся — говорить это прямо, а не молчать; (в) правила каркаса,
записанные как `.panel <класс>`, до экранов **не доходят** — нейтрализацию плашек (`.phone .ds-list-item__text, …`)
и любые другие поправки дублировать для `.phone` (готовый приём — в `references/screen-preview-phone-frame.md`).
Строка из нескольких кнопок и правила «сколько кнопок влезает / что делать, когда не влезает» (цитаты MD3 и HIG +
наш замер 359 px) — `references/button-rows-and-overflow.md`.

**Пересчёт связанных значений должен быть виден (12.09.2026).** Сначала я считал паддинг от высоты скрыто,
формулой внутри правила — владелец: «Нахера это прятать куда-то под капот и вводить в заблуждение».
Правильно и в итоге сделано: связь задана в данных (`"sync": {"field": "pad-v", "a": 0.5, "b": -10}`,
линейно t = a*v + b), поле-цель само показывает новое число (высота 40 → паддинг 10; паддинг 8 → высота 36)
и применяется вместе с ним. То есть автоматика — да, скрытая автоматика — нет: любое следствие правки
обязано быть видно в том же блоке.

**Колонка Mobile в таблице — рекомендация, не правится (12.09.2026).** В правке «4-я колонка с полями» я заодно
переписывал число в колонке Mobile при вводе — получил: «Значения в колонке мобайл не правятся. Это
рекомендованные значения по материал. Я нигде не писал чтобы они правились. Ты опять делаешь что-то своё».
Правило: `Mobile` — источник (числа из платформ), её содержимое не меняется ни при каких правках; колонка
«Правка» — отдельная копия тех же чисел, и меняется только она. Это тот же класс ошибки, что «заодно поправить»:
данные, которые он считает опорными, не переписывать даже «для консистентности».

**Режим строгого следования задаче (12.09.2026).** После серии моих «докруток» он сказал: «Я боюсь уже
  с тобой работать… Я хочу только чтобы ты чётко следовал задаче поставленной». Протокол, которому следую без
  напоминаний: делать ровно то, что сказано; перед правкой одна строка «файл + элемент + что станет» и ждать «да»;
  никаких добавленных классов, заголовков, текстов и «заодно»; найденное рядом — списком в ответе, без правки;
  после правки — замер только того, о чём просили; непонятно — один короткий вопрос. Новые предложения и
  инициативы не выкатывать: ждать слова.
- **Правило «эталон первым» (12.09.2026, после вопроса «Почему ты это не исправляешь сразу?»).** Когда он говорит
  «сделать как остальные», «такой же, как все» — это НЕ «похоже и объяснимо», это конкретные числа у соседних
  элементов (у блока-карточки: отступ до соседа 16/17 px, края 329…1870, паддинг 16, h2 16/24, текст `.point` 13/19).
  Порядок: (1) ПОМЕРИТЬ эталон в той же вёрстке до правки, (2) править, (3) сравнить все признаки сразу
  (края + отступ + ширины + кегли + нет ли полос/обрезки) на всех страницах, а не на одной, (4) только потом писать
  «готово». Ошибка этого дня: края я померил, а отступ — нет; «57 px» объяснил сам себе и назвал нормой, после чего
  получил «пишешь что всё ок, хотя по факту много ошибок». Мера «объяснимо» ≠ мера «как у остальных».
- **Отвечать от того, что он видит, а не от DOM.** 12.09.2026 на вопрос «почему не все токены применились» я отдал
  таблицу `getComputedStyle` и фразу «применилось — радиус 8 px в обоих режимах»; ответ: «Нихрена не понял что ты написал…
  Я блядь не вижу радиусы 8 px» и одним абзацем позже «Мне похрену в чём конкретно дефект». Формат, который доходит:
  сначала — что видно на экране («углы плашки прямые»), потом — почему (свойство объявлено у прозрачной обёртки,
  у тёмных плашек `radius: 0`), и только затем числа. Замеры — в отчёт, а не в объяснение причин; таблицы
  `getComputedStyle` он не читает, ему нужен вывод и следствие.
- **«Задача понятна? Сначала скажи что понятна» (13.09.2026).** Многострочную спеку он хочет услышать обратно своими
  словами **до** работы: перечислить пункты как понял, задать максимум 1–2 уточнения (в той развязке — «колонку из
  таблицы убрать совсем?» и «что делать на 9 страницах, где править нечего?») и дождаться ответа. Так он поймал
  ошибку чтения на одном вопросе вместо переделки 38 страниц.
- **Пилот на одной странице перед разливом формата.** Меняя ФОРМАТ блока (не значения), сделать одну страницу,
  дать URL и спросить «так?». Владелец принял именно так («Сделал образец на Checkbox — посмотри»), после «делай
  дальше» разлив идёт заготовками через `apply_out.py`. Разлив без образца — риск переделать все 38.
- **«Делай дальше» = продолжай задачу, а не расширяй её.** Отложенное («с полями разберёмся») остаётся отложенным:
  не доделывать молча и не подсовывать под видом продолжения. В отчёте держать одну строку «ждёт твоего слова».
- Answer in **Russian**, plainly and factually; explain mechanism, not vibes.
- Lead with what changed (files) → the numbers that prove it (measured, not designed) →
  what is still open. No narration of the process.
- Never present an invented value as a DS value; if it is a placeholder, say so and say
  where the real value must come from.
- **Жалоба «в десктопе ошибок полно» не отвечается рассказом про мобильный слой.** Сначала прогнать
  десктопные детекторы (`_audit/rec/checks/audit-desktop.py desktop`, `audit-live-desktop.py`), затем дать
  таблицу «замер до → после» и отдельно «найдено в библиотеке, не правим», и только потом спрашивать,
  какую страницу он смотрел. «Я проверил» без чисел по десктопу читается как «не проверял».
- **Один компонент за раз.** Формулировка владельца: «По очереди, не спеша» — когда он перечисляет
  несколько компонентов (Stepper, Slide toggle, Form field, Card), он ждёт их **по одному**: сделать,
  показать замеры, дождаться «дальше». Не сваливать четыре компонента в один ответ и не бежать вперёд.
- **Но когда он говорит «делай все остальные как считаешь нужным» — работать партиями по группам плана**
  (A «размеры» → CSS + страницы; B и C — структурные). Одна партия = один ответ: список компонентов,
  CSS-файлы, замеры «desktop → mobile» таблицей и находки. Для компонентов группы D («без изменений»)
  результат — **сама страница**: CSS не трогать, но «не меняется» доказать источником (числа ДС → что даёт
  каждая платформа → почему мобильного значения нет и где 404), иначе владелец читает это как недоделку.
  Бриф брать из строки плана (`iiko-ds-mobile/desktop-to-mobile-plan.md`), он совпадает с источниками
  почти всегда — проверять расхождения и писать о них.
- **Страницы в браузере не открывать самому.** Пользователь прямо попросил: «Не нужно мне постоянно
  открывать автоматом страницы с компонентами». Рабочий приём — дать полный `http://127.0.0.1:8899/…`
  адрес отдельной строкой текстом (клик в ACP-панели всё равно ничего не откроет):
  `cmd.exe /c start "" "<url>"` и .url-ярлыки применять только когда он прямо попросит «открой».
- **Когда владелец приносит число («инпут в мобильной версии 48, а должен быть 56») — сначала локализовать, а не спорить.**
  Порядок: (1) инвентарь всех страниц, где элемент вообще рендерится (grep по классу + `<input`),
  (2) замер каждой по `http://127.0.0.1:8899` **со свежим профилем и без cache-buster** — обе панели,
  (3) назвать места, где значение правда десктопное: у `iiko-ds-prototypes/*.html` режима **нет вообще**
  (`metro-general-settings.html`, `add-fasovka.html`, десктопный блок `figma-1276-metro-desktop.html`) — 48 там
  ожидаемы, (4) если собранная страница верна — сказать это и спросить, какую страницу он смотрел.
  Ловушка: `[data-mode="mobile"]` встречается в inline-`<style>` этих страниц как селектор, поэтому grep по
  `data-mode` ничего не доказывает — смотреть предка элемента в DOM. Готовый инвентарь:
  `scripts/find-element-inventory.py` (файлы + режим + замер высоты).
- **A link to a local page must actually open.** In the VS Code ACP panel `file:///…` — and a
  markdown link to it — only looks like a link; the click does nothing. Serve the DS root over
  HTTP (`python -m http.server 8899 --bind 127.0.0.1 --directory C:/Users/asukharev/GitHub/DS`)
  and give the full `http://127.0.0.1:8899/…` URL as plain text (opening it for him — only when he asks,
  see the bullet above). Always write full paths from
  the DS root, never relative ones — he asked for that explicitly.
  Если `8899` отвечает `HTTP 000`, хотя `netstat` показывает LISTENING, — висит мёртвый сервер прошлой
  сессии: убить по PID (`cmd.exe /c "taskkill /F /PID <pid>"`, MSYS калечит `//F`) и поднять заново.

## Support files

- `references/mobile-mode-button.md` — the Button case study: token table, sources, the
  measurement diff, the latent bugs found in the shipped CSS, the open questions.
- `scripts/headless-measure.py` — render a local page in headless Chrome, pull its
  `data-measure` JSON, optionally screenshot, optionally diff two runs.
- `scripts/figma-mcp.py` — talk to the Figma Dev Mode MCP (127.0.0.1:3845): `tools`, `call`, `--node`.
- `references/figma-mcp.md` — the MCP recipe: tool list, active-document/selection rule, transport
  quirks, and the order of steps for pulling `_mob` values out of the canvas. Только для случаев, когда
  владелец сам просит посмотреть Figma: по мобильным компонентам её использование запрещено.
- Case studies компонентов, переведённых после Button (Button icon, Button toggle — структура, числа,
  дефекты, открытые вопросы): `iiko-design-system`, `references/mobile-mode-icon-and-toggle.md`.
- `references/mobile-mode-values-sizes.md` — сводка переведённых компонентов (Button, Button icon,
  Button toggle, Stepper, Slide toggle, Form field, **Card**): desktop/mobile числа, откуда они взяты,
  формулы геометрии, случаи «мобильных чисел нет по источникам», приёмы проверки (кэш Chrome и `?v=` от
  `build.py`, псевдоэлементы, клик по меню оболочки, диагностика «он видит другое число») и оболочка страниц
  рекомендаций. **Checkbox и Radio** (строка 20 → 48, маркер 20) и правило «мобильные значения — всем размерам»
  тоже там, плюс **партия 2**: Textarea (минимум 3 строки = 104), Input number (48 → 56, дефект content-box),
  List (68 → 72), Expansion panel (44 → 48/64), Icon size (тач-слой 48), Badge/Divider/Logo/Backdrop/Status/Scroll
  («без изменений» с обоснованием) и три капкана харнесса. Начинать следующий компонент отсюда.
- `references/mobile-layer-batches-b-c.md` — **партии 3–4 и завершение плана**: группа B (Chips, Chips input,
  Banners, Snackbar, Tabs), группа C (Select, Autocomplete, Datepicker, Timepicker, Menu, Hint/Tooltip, Dialog,
  Search, Sidenav, Table, Tree, table-2-lvl) и `UI: text-ui`. Таблица «desktop → mobile» с источником каждого
  числа, приёмы мобильных оверлеев (геометрия шторки без `position: fixed`, полноэкранные режимы, кнопки в столбик),
  случаи «источник только MD2» и «компонента нет ни у кого», открытые вопросы. План закрыт целиком: 38 компонентов = 38 страниц.
- `scripts/verify-mobile-values.py` — один прогон вместо трёх: проверяет, импортирован ли CSS компонента
  в агрегатор (и какие файлы его папки пропущены), затем рендерит страницу или файл в свежем профиле
  headless Chrome и печатает по каждой панели `data-mode` реальный размер элемента, `display`, размер
  маркера и разрешённый токен. Нужен, когда мобильное правило «не применяется»: отличает «CSS не подключён»
  от кэша и специфичности. Плюс режим `--harness <файл-разметки>`: рендерит одну и ту же разметку дважды
  (блок desktop + блок mobile) на странице, которая подключает **оба** мобильных слоя —
  `modes.css` И `mobile components/index.css`. Этим делать и «до/после», и разовый замер, не собирая
  тестовую страницу руками (собранная руками забывает второй слой и печатает десктопные числа).
- `scripts/find-element-inventory.py` — по CSS-классу (или `--selector`) обходит все HTML в `DS`, показывает
  страницы с элементом, есть ли у них `data-mode`, и по `--measure` замеряет высоты в каждой панели
  headless Chrome со свежим профилем. Нужен, когда владелец приносит «а у меня другое число».
- `references/mobile-structural-components.md` — компоненты группы «Структура»: где живёт файл варианта,
  капкан специфичности мобильного слоя, обязательная ссылка на мобильный агрегатор в `_audit/rec/build.py`,
  `html_mobile` в данных примера, кейс Stepper (числа, замеры, открытые вопросы) и очередь после него.
- `scripts/audit-mobile-values.py` — **матричный аудит мобильного слоя**: берёт список проверок
  (`page, selector, property, expect[, pseudo]`) и на каждой странице рекомендаций читает в обеих панелях
  `getComputedStyle` реальное значение, печатает таблицу `desktop → mobile` и список СЛОМАНО. Одним прогоном
  отличает «правило не применилось» от «значение верное» — этим найдено 17 сломанных проверок после отката
  библиотеки. Встроенный набор из 41 проверки запускается без аргументов, свой набор — `--checks file.json`.
  Код возврата 1, если что-то сломано.
- `references/mobile-layer-frozen-library.md` — эпизод отката `iiko-ds-web`: как откат проверяется,
  что именно ломается (17 из 41), какие значения переехали в мобильные файлы, пересечения правил между
  компонентами, исправленные числа Button toggle (рамка внутри трека) и как об этом докладывать владельцу.
- `references/library-autogen-artifacts.md` — каталог следов автогена в CSS `iiko-ds-web`: 23 класса, где
  `background` равен `color` (текст рисуется плашкой), nowrap у подписей, залитая акцентным цветом обёртка
  кнопки диалога, фиксированная высота блока действий, белая подпись светлого снекбара, тёмные подписи
  сайденава, контейнер без класса варианта, два вопроса палитры (бейдж warning ≈ 1.9, плейсхолдер поиска
  #d6d6d6). Там же — политика «нейтрализовать только в каркасе страниц» (константа `CSS` и `found_card()`
  в `_audit/rec/build.py`, поле `found_html`, 13 страниц с карточкой «Найдено в ДС») и ловушка парного
  регекспа сканера.
- `scripts/audit-page-render.py` — три детектора одним прогоном по всем страницам рекомендаций: **плашки**
  (`background` = `color` у элемента с собственным текстом), **невидимый текст** (контраст ниже порога к
  эффективному фону) и **выход за границы панели** (с пропуском обрезающих предков). Этим найдены и
  доведены до нуля плашки, светлый снекбар, подписи сайденава и строки времени. Требует запущенного
  `serve.py 8899`; код возврата 1, если что-то найдено.
- `references/icons-material-ligatures.md` — иконки: конвенция Material Icons лигатурой по имени,
  карта «слот ДС → имя иконки» для всех страниц, размеры и `line-height` в каркасе, код конвертации
  старых SVG в лигатуры, откуда брать пути символов (`symbols/web/<имя>/materialsymbolsoutlined/<имя>_24px.svg`
  через curl) и ловушка `document.fonts.check` в момент разбора страницы (даёт `false` → «шрифта нет» →
  заглушки; правильно — `await document.fonts.load(...)` и замер ширины глифа).
- `references/shell-geometry-and-probe-recipes.md` — **геометрия оболочки и приёмы замера**: пиксельный замер
  краёв и отступов по скрину (сканы строк на не-фон), числа блока пояснений (`.kit .card`, 329…1870, отступ 17 px),
  эволюция `fit()` (залипание `documentElement.scrollHeight` → `body.scrollHeight` → обрезка по низу последнего
  блока + инжект `html,body{overflow:hidden}`), синхронный iframe-пробник для `--dump-dom`, почему вложенный
  `iframe` врёт про `scrollHeight`, и grep-рецепты «токен объявлен vs читается».
- `references/editable-mobile-values.md` — **колонка «Правка»**: схема `edit` (`id`/`v`/`sel`/`css`/`sync`) в `data/*.json`,
  генератор и скрипт страницы (правила в `#live`, только тронутые поля, связка высота ↔ паддинг видна в поле),
  что колонка Mobile не правится, связки «строка → свойство» для Button, синхронный пробник
  с `dispatchEvent('input')`, инвентарь строк таблицы (218 / 91 размерная / 52 числовые) и что осталось разлить.
- `references/screen-preview-phone-frame.md` — **блок «На экране»**: варианты A/B/C и выбранный B, разметка корпуса
  телефона и экрана с `data-mode="mobile"`, три сценария с разным расположением кнопок, капканы (подпись только
  вне корпуса, никаких инлайн-стилей, соседи из готовых примеров, пустой экран выглядит недоделкой, плашки автогена
  вне `.panel`, вставка Python-кода внутрь CSS-литерала, ширина контейнера списка 258 px), бюджет строки кнопок
  (359 px против 362) и замеры 44 → 40 на трёх экранах.
- `references/button-rows-and-overflow.md` — **сколько кнопок влезает в строку**: цитаты MD3/HIG из `_audit/platform/*.json`
  (короткие подписи ради одной строки, лимиты 2/3/4 кнопок, 60 pt между центрами, запрет смешивать размеры,
  overflow однотипных «полок» — прокрутка), лестница «что делать, когда не влезает» и наши замеры ширины кнопок
  (121/54/106/40 при внутренних 359 px).
- `scripts/check-page-js.py` — вынимает `<script>` из всех сгенерированных страниц рекомендаций и прогоняет
  `node --check`: ловушка «`'\n'` в Python-шаблоне → реальный перевод строки в JS → `SyntaxError`, страница молча
  ничего не правит». Код возврата 1, если хоть один скрипт сломан; запускать после каждого `python build.py`.
- `references/desktop-side-defects-and-detectors.md` — **десктопная половина**: два детектора и что каждый
  ловит, шаблон iframe-обёртки и как отличить «JS упал» от «нечего выводить», приём «чистая библиотека»
  (одноразовый пробник без каркаса: только font.css → tokens.css → styles.css → components/index.css и
  разметка нужных классов), таблица измеренных дефектов ДС (content-box 48 → 74 у пяти кадров полей,
  min-height фреймов, Button icon disabled = активной, системные Checkbox/Radio) и список правок каркаса,
  которыми это закрыто.
- `references/pages-bulk-fill-pipeline.md` — **разлив формата страниц на все 38 компонентов**: схема
  «заготовки `out/<блок>/<slug>.json` → `apply_out.py` → `build.py`», почему параллельные исполнители не
  должны писать в `data/*.json`, формы заготовок трёх блоков, правило полей колонки «Правка», карта
  «slug → файл `_audit/platform/*.json`» (там числа на все компоненты плана, `data-tech` — только на 9),
  порядок проверки, ловушка драйвера (пустой `<pre id="out">` читается как «сервер виноват») и состояние
  разлива на 13.09.2026 (платформенные колонки — на всех 38, «Правка» и «На экране» — в работе).
- `scripts/audit-edits.py` — проверка колонки «Правка» на живых страницах: `MISS` / `NOCHANGE` / `SCREENS` / `ERR`
  плюс расхождения «страница ↔ `data/*.json`» (сверка числа полей, числа экранов и наличия блока платформ).
  Копия рабочего `_audit/rec/checks/audit-edits.py`; требует `serve.py 8899`. Запускать после каждого `apply_out.py --build`.
  **После пересборки 13.09.2026** проверяет два экрана, меряет только помеченный `data-preview="edit"` экран и печатает
  `LEAK`, если правка задела первый (дефолтный) — сверяться с версией в репозитории, копия может отставать.
- `scripts/why-nochange.py` — разбор одного «мёртвого» поля колонки «Правка»: печатает найденные элементы, их
  **inline-стиль**, вычисленные значения свойств до/после и текст `<style id="live">`. Этим отличена настоящая причина
  (inline `min-height:48px` у `autocomplete`, слишком короткий селектор у `stepper`) от ложной (transition, шорткаты
  `padding`/`margin`, псевдоэлемент) — ложные живут в проверке, а не в странице. Копия
  `_audit/rec/checks/why-nochange.py`.
- `scripts/why-rule.py` — какие вообще правила задают это свойство у элемента мобильной панели, в порядке
  специфичности и с пометкой `!important`. Нужен, когда поле «Правки» не срабатывает, а inline-стиля у элемента
  нет: у `stepper` мобильный слой писал `min-height` длинным селектором `.ds-stepper.ds-stepper--vertical .ds-step`
  (0,3,0) против `[data-mode="mobile"] .ds-step` (0,2,0). Копия `_audit/rec/checks/why-rule.py`.
- `scripts/audit-preview.py` — приёмка блока «На экране» по всем страницам: `COUNT` / `NOCOMP` / `DUP` /
  `OVERFLOW` / `CLIPPED` / `EMPTY`. Классы главного компонента берутся из его CSS, переполнение не считается
  дефектом у элемента, обрезанного контейнером внутри экрана (подробно в докстроке). Копия
  `_audit/rec/checks/audit-preview.py`; запускать после каждого разлива превью (с 13.09.2026 норма — два экрана).
- `_audit/rec/checks/check-patch.py` — валидатор заготовок (`python checks\check-patch.py <slug>` из `_audit/rec`):
  два экрана, баланс, классы, компонент на каждом экране, селекторы полей в разметке, `@` в css, `STILL-TAKZHE`.
  Его гоняют **сами исполнители** до сдачи; рядом `page-block.py` (где стоят блоки на странице) и
  `preview-sheet.py` (контактный лист в `_audit/rec/out`).
- `references/preview-screens-qa.md` — приёмка превью из трёх экранов: шесть детекторов и их определения,
  четыре починенные страницы (sidenav-оверлей с двумя ошибками по дороге, чипы, подсказка textarea, ложная
  тревога на табах), пары `.phone`-правил в `build.py`, правило «подпись экрана — часть разметки» и проверка
  контента платформ на повторы. Формат «три экрана» с 13.09.2026 вечера заменён на «два экрана + панель
  „Что | Правка“» — см. следующий файл.
- `references/preview-two-screens-and-edits-panel.md` — **текущий формат блока «На экране» (13.09.2026, вечер)**:
  два экрана одного интерфейса с компонентом в разных местах, панель «Что | Правка» третьей колонкой ряда,
  маркер `data-preview="edit"` и правило `[data-mode="mobile"][data-preview="edit"].phone__screen <sel>`, категория
  `LEAK` в `audit-edits.py`, правило «„то же“ в размерной строке → цифры с десктопа» (59 строк), капканы строковой
  сборки экранов (`rstrip` по символам, счёт закрывашек `mock.screen()`), инструменты `check-patch.py` /
  `page-block.py` / `preview-sheet.py` и состояние разлива (задание `out/SPEC2.md`).
