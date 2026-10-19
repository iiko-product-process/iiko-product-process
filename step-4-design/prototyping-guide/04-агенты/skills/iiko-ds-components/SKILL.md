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

Дневная работа владельца — **iiko Web DS**: CSS-компоненты из переменных Figma + растущий мобильный слой. Карта и token-first порядок правки компонента — ниже. Workspace: `C:\Users\asukharev\GitHub\iiko-DS\DS`.

`references/iiko-real-ui-screens.md` — правило владельца: дефолтные экраны (состав, подписи, числа) брать с реальных экранов iiko, ничего «правдоподобного» не выдумывать.

## When to Use

- Build/refactor a component in `components-web` (Button, Input, Banner, …).
- Produce the mobile (or tablet) version of a desktop component, or touch the
  desktop/mobile split at all.
- Answer "what does the DS say about X" / assemble a prototype on DS components.
- Anything that touches `iiko-ds-spec.md`, `tokens.css`, `modes.css`, prototypes.

## Repos — what lives where

| Path | What it is |
|---|---|
| `DS/components-web/` | The library — a folder inside the `DS` repo (`github.com/iiko-DS/DS`), branch `main`; no separate origin of its own. |
| `components-web/tokens.css` | **Generated** from Figma variables (~1743 vars; collections Base Size, Base Color, Space, Radius, Base Stroke, Shadows, Base Typography, Typography, Color, **Component**). Never hand-edit. |
| `components-web/styles.css` | Generated Figma text/shadow/colour styles. `font.css` = Roboto 400/500 inlined base64 → works offline, load it first. |
| `components-web/components/<Name>_DS/*.css` | One folder per component; `components/index.css` aggregates them with `@import`. |
| `components-web/iiko-ds-spec.md` | ~700 KB single source of truth written to be pasted into any AI: general rules, class map, token tables, full component CSS. Mostly generated. |
| `components-mobile/` | The **mobile layer** (not a git repo), structure mirrors `components-web`: `modes.css` (the mode axis), `components/index.css` (aggregator; a `components/<Name>_DS/` file appears only when a real `*_mob` component exists), `prototypes/` (demo pages, e.g. `prototypes/button-modes.html` — desktop and mobile side by side + measurements). Plus the plan docs: `desktop-to-mobile-plan.md` (classification A–D + how Material/Angular solve each), `mobile-mode-notes.md`, `mobile-workflow.md`, `mobile-steps.md`, `mobile-block-schemes.md`. |
| `Prototypes/` | HTML prototypes and the knowledge base — a **separate git repo** (`github.com/iiko-DS/Prototypes`) next to the `DS` folder. Some reference pages (hand-transcribed Figma values) are no longer in the repo. |

## Non-negotiables (spec, «Общие правила»)

- **⛔ Скриншот или замечание владельца — это НЕ задание.** 12.09.2026 он пометил красным пять абзацев
  пояснений на странице-оглавлении; я прочитал пометки как «убрать», убрал и получил: «Ничего убирать не
  надо. Я не просил. Никогда ничего не делай сам без моего ведома. Кажется, уже был такой разговор».
  Правило: правку текстов, каркаса и данных начинать ТОЛЬКО после явного «сделай / убери / поменяй».
  Скрин, пометка, жалоба, вопрос — материал для разговора, а не разрешение; если пометка читается как
  указание, задать один короткий вопрос и дождаться ответа. Если самодеятельность всё же случилась —
  первым действием откатить (вернуть как было и показать проверку «вернулось»), а не объяснять, почему так вышло.
  **Это не только про содержимое страниц.** После отката он добавил: «Ты уже заебал так делать… Уже не в
  первый раз и постоянно так делаешь что не просят» — то есть самодеятельность накапливается и перечитывается
  как система, а не как случайность. Ждать «да» до: правок текстов, каркаса и данных, массовых правок после жалобы на «ошибок полно», запуска фоновых
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
- **⛔⛔ НИКОГДА не править файлы в `components-web` без прямого разрешения владельца.** Ни токенизацию,
  ни формулы высот, ни «очевидные фиксы» (box-sizing, порядок состояний, импорты в агрегаторе) — даже
  когда они явно сломаны. Задача «сделай мобильные компоненты» НЕ даёт права на десктоп: у него любая
  правка библиотеки = сломанный источник истины (Figma-автоген + выверенные вручную файлы), а откат —
  один `git checkout`. Реакция на самовольные правки — ярость и требование откатить всё.
  Как делать мобильное без библиотеки: явные значения в `components-mobile` (`modes.css` + файлы
  `components-mobile/components/<Имя>_DS/*.css`, в том числе `height`/`padding` руками, если десктопный CSS
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

- `components-mobile/modes.css` holds `[data-mode="mobile"] { … }` overrides of only the tokens
  that differ. No attribute = Desktop default, so old prototypes stay as they were.
  (The file lives in the mobile folder, NOT in `components-web` — a demo page inside
  `components-mobile/prototypes/` links it as `../modes.css`, the library as `../../components-web/…`.)
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
belong in `modes.css`: it is a file in the mobile layer, `components-mobile/components/<Name>_DS/<variant>.css`,
registered in the mobile aggregator `components-mobile/components/index.css` (Stepper 11.09.2026 was the first
real one). Two traps, both hit for real:

- **Specificity, not order.** The documented order links the mobile layer *before*
  `components-web/components/index.css`, so a variant class with equal specificity loses on every property the
  base also sets (`flex-direction` applied from `.ds-stepper--vertical`, but `align-items` stayed from
  `.ds-stepper` and the vertical line drifted to the centre). Write `.ds-stepper.ds-stepper--vertical` (0,2,0)
  instead of reordering; and measure `align-items`/`gap`/divider orientation, not just the direction.
- **Страница с примером обязана подключать мобильный агрегатор `components-mobile/components/index.css`.**
  Без него структурный файл не загружается, и панель молча рендерит десктопный лейаут: замер показывал
  `row` / `8×1`, хотя класс был в разметке.

Разницу показывать примером с `html_mobile` (+ `stack: true`), а не правилом `data-mode` —
ориентация это композиция, как `orientation` у Angular. Полный рецепт, числа и кейс
Stepper: `references/mobile-structural-components.md`.

### Мобильный слой, когда библиотека «заморожена» (12.09.2026)

Владелец однажды потребовал откатить **все** правки в `components-web` («Какого хера ты полез в components-web???»)
— и был прав: откат делается одной командой `git checkout -- .` в репозитории и проверяется `git status`
(пусто) + `git diff --quiet HEAD` (код 0). После отката десктопный CSS снова держит размеры **числами**
(`.ds-btn--m { height: 36px }`, `.ds-input--m .ds-input__frame { height: 48px }`, трек тумблера 34 × 20),
поэтому режимные токены его не двигают, и мобильные значения надо задавать **явными правилами**
в `components-mobile/components/<Имя>_DS/*.css`.

Разделение труда внутри мобильного слоя:

| Что | Где живёт |
|---|---|
| Токены, которые компонентный CSS **читает** (паддинги полей, gap, типографика) | `modes.css`, блок `[data-mode="mobile"]` |
| Всё, что десктопный CSS задаёт числом (высоты, ширины, трек тумблера, ход ручки) | файл компонента в `components-mobile/components/<Имя>_DS/…` |

Порядок работы после любого отката библиотеки: (1) **сначала аудит** — матрица ожидаемых мобильных значений
против собранного CSS; (2) починить только в мобильном слое; (3) повторить аудит до нуля;
(4) проверить отрисовку в обоих режимах (считать элементы в панелях — пустая панель читается
как «компонент сломан»); (5) сверить числа с текстами, если текст утверждал то, чего больше нет
(например «высота приходит сама из паддингов»).
Десктопное число при этом никто не двигает: мобильные файлы не влияют на `data-mode` без атрибута.
Разбор случая и таблица «что было сломано → где починено»: `references/mobile-layer-frozen-library.md`.

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
3. **Start from the component's row in the plan, not from the CSS.** `components-mobile/desktop-to-mobile-plan.xlsx`
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

Before reporting "the override does not work", read the variable itself:
`getComputedStyle(panel).getPropertyValue('--ds-…')` — if the token is right but the size is stale, it is cache
or specificity, not tokens. Details and the rest of the measured numbers: `references/mobile-mode-values-sizes.md`.

**Если владелец говорит «у меня другое число / ничего не поменялось»** — сначала предложить один
`Ctrl+Shift+R` (обычная F5 не перезапрашивает подресурсы), а не спорить с замерами: у агента
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
- **Repo boundaries:** two repos, both private: `DS` (with `components-web/` and
  `components-mobile/` inside; origin `github.com/iiko-DS/DS`) and `Prototypes` (next to the
  `DS` folder; origin `github.com/iiko-DS/Prototypes`), branch `main`. Check `git -C <repo> status`
  and **ask before committing or pushing**.
- **Never delete a prototype/demo page — or the README/spec pointers to it — on your own
  initiative.** The user reversed exactly that call within the hour and asked for the page
  back: he reads the desktop/mobile difference off it (Figma's mode is file-global). Mobile
  demos live in `components-mobile/prototypes/`, the rest in `Prototypes/`; when one is
  added, its path belongs in `components-mobile/readme.md` and in the spec's «Живая проверка».
- **Recover, don't reinvent:** a file you deleted or overwrote is still in the session store —
  `state.db` keeps every `write_file` payload plus the follow-up edits that moved it. See the
  `session-store-forensics` skill, `scripts/recover-file-from-state-db.py`.
- **По мобиле источник — рекомендации платформ, а не Figma.**
  В Figma по мобильным **не ходить** и `_mob` оттуда не
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
  Числа, которыми это делается: кнопка с текстом — 44 у всех размеров (iOS HIG «a button needs a hit region
  of at least 44x44 pt» + план «минимум для веба — 44 px»; плотности Angular 40/36/32/28 — не мобильные размеры), иконка-кнопка — 40 у всех
  (дефолт MD3, Angular density 0), тач-зона 48 — невидимым слоем `::after` (`position:absolute; left/top:50%;
  width/height:100%; min-width/min-height:48px; transform:translate(-50%,-50%); background:none`) в
  `components-mobile/components/Button_DS/button-touch.css`. Строка (а не сам элемент) дорастает до 48 у чекбокса/радио
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
- **Checkbox и Radio после отката библиотеки снова системные.** Агрегатор `components-web/components/index.css`
  подключает у них только `*-label.css`; `checkbox.css`, `checkbox-icons.css`, `radio.css`, `radio-icons.css`
  не подключает никто. Признак в замере: `.ds-checkbox` = `display:inline`, высота 0, а `input[type=checkbox]`
  нарисован браузером 13 × 13 (12.09.2026: 21 такой контрол на страницах Checkbox, Radio, List). Лечение —
  подключить недостающие файлы; после них маркер 20 × 20, `gap 8px`, нативный
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
  В каркасе `height:auto`.
- **Одинаковые размеры в панелях Desktop и Mobile — не автоматический дефект.** Прежде чем «доделывать»,
  проверить, есть ли у платформы мобильное число вообще; если нет — написать это прямым текстом с
  источниками (Card выше). Тянуть число из соседнего компонента или «по плотности» — то, за что владелец
  откатывает правку.
- **Мобильное правило может «не применяться», потому что CSS компонента вообще не подключён.** 12.09.2026:
  `min-height: 48px` из `Checkbox_DS/checkbox-touch.css` давал 48 px в одной разметке и 19 px в другой.
  Причина — агрегатор `components-web/components/index.css` подключал у Checkbox и Radio **только `*-label.css`**
  (описание строки), а сами контролы `checkbox.css`, `checkbox-icons.css`, `radio.css`, `radio-icons.css`
  не подключал никто: ни агрегатор, ни одна страница в DS. Без них `.ds-checkbox` остаётся `display: inline`,
  а **у non-replaced инлайн-элемента `min-height` не действует**; в `display:flex`-строке тот же элемент
  становится flex-элементом — и высота применяется. Отсюда «в одном примере работает, в другом нет»
  при формально верных токенах. Порядок разбора: (1) есть ли файл в агрегаторе
  (`grep -n "<Имя>_DS/" components-web/components/index.css`), (2) какой `display` у элемента в реальной
  разметке (inline → `min-height`/`height` молча игнорируются), (3) только потом кэш и специфичность.
  Исправлено добавлением 4 импортов в агрегатор;
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
  Харнесс, который линкует только `modes.css` (токены) и забыл `components-mobile/components/index.css`
  (агрегатор), молча теряет все `*-mobile.css` / `*-touch.css` и печатает десктопные числа — читается
  как «правило не применяется» (список 68 вместо 72, шапка 44 вместо 48, тач-слой 0 вместо 48). Порядок:
  font → tokens → modes.css → mobile components/index.css → styles → web components/index.css. И не менять
  HTML между «до» и «после»: подмена внутреннего элемента числового поля дала фальшивую регрессию 74 → 50.
- **Инлайновые размеры и ширина контейнеров в примерах.** (а) `style="width:240px"`, `min-height:36px`
  в разметке примера побеждают любые мобильные правила — из примеров их вычищать, ширину должен давать CSS
  компонента; (б) для полноширинных мобильных контейнеров писать `width: 100%`, а не `auto`: в flex-контексте
  `auto` сжимается по содержимому (меню 240 → 179 вместо полной ширины).
- **Специфичность мобильного слоя, когда базовое правило состоит из двух классов.** Мало повторить класс один раз
  (`.ds-stepper.ds-stepper--vertical`): у Sidenav база — `.ds-sidenav-item--l1.ds-sidenav-item--expanded` (0,2,0),
  и мобильное `[data-mode="mobile"] .ds-sidenav-item` (0,2,0) проигрывает по порядку. Приём — повторить класс:
  `[data-mode="mobile"] .ds-sidenav-item--l1.ds-sidenav-item--expanded.ds-sidenav-item--expanded` (0,3,0).
  Признак такой же, как у Stepper: часть свойств применилась, часть нет.
- **Глобальный селектор в мобильном файле одного компонента перебивает другие компоненты.** Мобильный слой
  грузится как **один плоский CSS** (`components-mobile/components/index.css`), поэтому правило без привязки
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
  Сначала искать уже собранное, а не рассуждать заново;
  ответ «по памяти» владелец читает как «опять выдумываешь».
- **He may explicitly ask for work «по рекомендациям», not «сравнение с Figma».** Then the source
  of truth is MD3 / Angular Material / iOS HIG and the DS's own CSS+tokens; do not pull the
  `_mob` components or the comparison pages in, and do not answer with clarifying questions only —
  act on the obvious reading, state the assumptions, say what to change if the format is off.

- **Владелец правит `components-web` параллельно, прямо во время сессии.** 11.09.2026 в 20:34–20:37 у него сами
  поменялись `font.css` (вшитый base64 Roboto → онлайн-`@import` Google Fonts) и `iiko-ds-spec.md` (пункт
  «Иконки» переписан на Material Icons по имени). Перед фразой «в библиотеке чисто / это не моё» перечитать
  `git status` и `git diff --stat` в репозитории и посмотреть первые строки каждого дифа. Файл изменён не
  тобой — сказать это прямо и сверить свои страницы с новой версией (шрифт, иконки), а не молчать и не
  приписывать правку себе.
- **Временные проверочные страницы не оставлять в папках ДС.** Пробники, листы скринов и прочие артефакты
  после прогона убирать за собой; лишние файлы в папках ДС его раздражают.
- **Уборка — только по слову, и всегда с отчётом списком.** Развязка 12.09.2026 (скрины/уведомление) прошла
  цепочку: «Мне не нужно показывать что что-то сохранилось» → «Убери уведомление» → «Убери вообще нахран» →
  «То что ты тут лишнее сделал убирай по этому вопросу». До слова «убирай/удали» свои временные файлы,
  папки и скрипты не трогать вообще (это тот же капкан самодеятельности); после слова — удалять можно
  смело и не спрашивая по каждому файлу, но в ответе дать два списка: что удалено и что **оставлено**
  (рабочие детекторы, чужие файлы). Если сам сомневаешься, удалять ли что-то — спросить одной строкой.
- **Куратор копирует рабочие скрипты из репозитория в скилл — убирать надо в обоих местах.** Порядок уборки
  любого механизма: (1) файлы в репозитории, (2) копии в `scripts/` скилла, (3) упоминания в `SKILL.md` и
  `references/*.md` (включая секцию Support files), (4) мёртвые ссылки на удалённое в чужих справках —
  переписать описание приёма без пути к файлу.

## Reporting to this user

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
  ошибку чтения на одном вопросе вместо переделки всей пачки.
- **«Делай дальше» = продолжай задачу, а не расширяй её.** Отложенное («с полями разберёмся») остаётся отложенным:
  не доделывать молча и не подсовывать под видом продолжения. В отчёте держать одну строку «ждёт твоего слова».
- Answer in **Russian**, plainly and factually; explain mechanism, not vibes.
- Lead with what changed (files) → the numbers that prove it (measured, not designed) →
  what is still open. No narration of the process.
- Never present an invented value as a DS value; if it is a placeholder, say so and say
  where the real value must come from.
- **Жалоба «в десктопе ошибок полно» не отвечается рассказом про мобильный слой.** Сначала перепроверить
  десктопную половину (рендер, состояния, срезанные тексты), затем дать
  таблицу «замер до → после» и отдельно «найдено в библиотеке, не правим», и только потом спрашивать,
  какую страницу он смотрел. «Я проверил» без чисел по десктопу читается как «не проверял».
- **Один компонент за раз.** Формулировка владельца: «По очереди, не спеша» — когда он перечисляет
  несколько компонентов (Stepper, Slide toggle, Form field, Card), он ждёт их **по одному**: сделать,
  показать замеры, дождаться «дальше». Не сваливать четыре компонента в один ответ и не бежать вперёд.
- **Но когда он говорит «делай все остальные как считаешь нужным» — работать партиями по группам плана**
  (A «размеры» → CSS + страницы; B и C — структурные). Одна партия = один ответ: список компонентов,
  CSS-файлы, замеры «desktop → mobile» таблицей и находки. Для компонентов группы D («без изменений»)
  результат — CSS не трогать, а «не меняется» доказать источником (числа ДС → что даёт
  каждая платформа → почему мобильного значения нет и где 404), иначе владелец читает это как недоделку.
  Бриф брать из строки плана (`components-mobile/desktop-to-mobile-plan.md`), он совпадает с источниками
  почти всегда — проверять расхождения и писать о них.
- **Страницы в браузере не открывать самому.** Пользователь прямо попросил: «Не нужно мне постоянно
  открывать автоматом страницы с компонентами». Рабочий приём — дать полный `http://127.0.0.1:8899/…`
  адрес отдельной строкой текстом (клик в ACP-панели всё равно ничего не откроет):
  `cmd.exe /c start "" "<url>"` и .url-ярлыки применять только когда он прямо попросит «открой».
- **Когда владелец приносит число («инпут в мобильной версии 48, а должен быть 56») — сначала локализовать, а не спорить.**
  Порядок: (1) инвентарь всех страниц, где элемент вообще рендерится (grep по классу + `<input`),
  (2) замер каждой по `http://127.0.0.1:8899` **со свежим профилем и без cache-buster** — обе панели,
  (3) назвать места, где значение правда десктопное: у `Prototypes/*.html` режима **нет вообще**
  (прежние страницы-образцы) — 48 там
  ожидаемы, (4) если собранная страница верна — сказать это и спросить, какую страницу он смотрел.
  Ловушка: `[data-mode="mobile"]` встречается в inline-`<style>` этих страниц как селектор, поэтому grep по
  `data-mode` ничего не доказывает — смотреть предка элемента в DOM.
- **A link to a local page must actually open.** In the VS Code ACP panel `file:///…` — and a
  markdown link to it — only looks like a link; the click does nothing. Serve the DS root over
  HTTP (`python -m http.server 8899 --bind 127.0.0.1 --directory C:/Users/asukharev/GitHub/iiko-DS/DS`)
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
  формулы геометрии, случаи «мобильных чисел нет по источникам» и приёмы проверки (кэш Chrome,
  псевдоэлементы, диагностика «он видит другое число»). **Checkbox и Radio** (строка 20 → 48, маркер 20)
  и правило «мобильные значения — всем размерам»
  тоже там, плюс **партия 2**: Textarea (минимум 3 строки = 104), Input number (48 → 56, дефект content-box),
  List (68 → 72), Expansion panel (44 → 48/64), Icon size (тач-слой 48), Badge/Divider/Logo/Backdrop/Status/Scroll
  («без изменений» с обоснованием) и три капкана харнесса. Начинать следующий компонент отсюда.
- `references/mobile-layer-batches-b-c.md` — **партии 3–4 и завершение плана**: группа B (Chips, Chips input,
  Banners, Snackbar, Tabs), группа C (Select, Autocomplete, Datepicker, Timepicker, Menu, Hint/Tooltip, Dialog,
  Search, Sidenav, Table, Tree, table-2-lvl) и `UI: text-ui`. Таблица «desktop → mobile» с источником каждого
  числа, приёмы мобильных оверлеев (геометрия шторки без `position: fixed`, полноэкранные режимы, кнопки в столбик),
  случаи «источник только MD2» и «компонента нет ни у кого», открытые вопросы. План закрыт целиком.
- `references/mobile-structural-components.md` — компоненты группы «Структура»: где живёт файл варианта,
  капкан специфичности мобильного слоя, обязательное подключение мобильного агрегатора,
  `html_mobile` в данных примера, кейс Stepper (числа, замеры, открытые вопросы) и очередь после него.
- `references/mobile-layer-frozen-library.md` — эпизод отката `components-web`: как откат проверяется,
  что именно ломается (17 из 41), какие значения переехали в мобильные файлы, пересечения правил между
  компонентами, исправленные числа Button toggle (рамка внутри трека) и как об этом докладывать владельцу.
- `references/icons-material-ligatures.md` — иконки: конвенция Material Icons лигатурой по имени,
  карта «слот ДС → имя иконки», размеры и `line-height`, код конвертации
  старых SVG в лигатуры, откуда брать пути символов (`symbols/web/<имя>/materialsymbolsoutlined/<имя>_24px.svg`
  через curl) и ловушка `document.fonts.check` в момент разбора страницы (даёт `false` → «шрифта нет» →
  заглушки; правильно — `await document.fonts.load(...)` и замер ширины глифа).
- `references/button-rows-and-overflow.md` — **сколько кнопок влезает в строку**: цитаты MD3/HIG
  (короткие подписи ради одной строки, лимиты 2/3/4 кнопок, 60 pt между центрами, запрет смешивать размеры,
  overflow однотипных «полок» — прокрутка), лестница «что делать, когда не влезает» и наши замеры ширины кнопок
  (121/54/106/40 при внутренних 359 px).
