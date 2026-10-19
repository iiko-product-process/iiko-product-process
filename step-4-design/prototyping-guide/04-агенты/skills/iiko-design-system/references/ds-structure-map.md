# Карта структуры iiko DS — что за что отвечает (замерено 15.09.2026)

Ответ на запрос владельца «подробнее расписать, как и из чего устроена наша структура: по каждой папке
и условно по файлу — что за что отвечает, для понимания». И тогда, и в следующий раз это надо давать
**по замерам файлов**, а не по памяти: он сверяет числа. Ниже — готовая карта + команды, которыми она снята.

## Три части (и у кого свой git)

| Часть | Git | Что это | Объём |
|---|---|---|---|
| `components-web/` | **свой** репозиторий (публикуется как сайт ДС) | библиотека: токены + компоненты | 104 файла, 4,5 МБ (100 CSS, 3 MD, `.nojekyll`) |
| `components-mobile/` | под версиями **корневого** `DS` | мобильный слой: режим, мобильные компоненты | 74 файла, 2,9 МБ |
| `Prototypes/` | **свой** репозиторий | ручные прототипы экранов на компонентах ДС | 93 файла, 5,2 МБ |

Зависимость в одну сторону: `components-web` (база) → `components-mobile` (мобильные отличия) →
`Prototypes`.

## `components-web` — корень (все восемь файлов)

| Файл | Строк | За что отвечает | Руками |
|---|---|---|---|
| `font.css` | 3 | Roboto 400/500 онлайн `@import`; подключать первым | — |
| `tokens.css` | 2447 | **генерируется из Figma**: 1743 переменные в 10 коллекциях (Base Size 18, Base Color 127, Space 13, Radius 9, Base Stroke 5, Shadows 45, Base Typography 26, Typography 21, Color 133, **Component 1346**); в файле 2133 уникальных имени `--ds-*` | ⛔ |
| `styles.css` | 530 | выгрузка плагина v2 (текстовые стили, тени, эффекты) | ⛔ |
| `fixes.css` | 19 | ручной слой поверх генерации: подпись Status, `box-sizing` кадров полей; подключается последним | да |
| `generator-rules.md` | 95 | правила для того, кто ведёт конвертер «Figma → файлы ДС» | да |
| `iiko-ds-spec.md` | 778 КБ | единый источник для людей и ИИ; читать точечно | да |
| `readme.md` | 128 Б | одна строка | да |
| `.nojekyll` | 0 | GitHub Pages | — |

`components/`: **37 папок, 96 CSS**; `components/index.css` — агрегатор, **91 `@import`**. Файлов в папке
столько, сколько у компонента CSS-кусков: `Button_DS` — 1, `Stepper_DS` — 2, `Dialog_DS` — 5,
`Table_DS` — **13** (`table-header-row.css`, `table-content-row.css`, `table-footer.css`, `*-cell.css`).
Шапка каждого компонентного CSS фиксирует страницу Figma, варианты, состояния.

**Находка (не чинить):** четыре файла **не подключены агрегатором** — `Checkbox_DS/checkbox.css`,
`checkbox-icons.css`, `Radio-Button_DS/radio.css`, `radio-icons.css` (в агрегаторе только `*-label.css`).
Без них `.ds-checkbox` = `display:inline` и на экран выходит системный контрол 13 × 13 вместо маркера 20 × 20;
в примерах их подключают явно.

Порядок подключения: `font.css → tokens.css → components-mobile/modes.css →
components-mobile/components/index.css → styles.css → components-web/components/index.css → fixes.css`.

## `components-mobile` — мобильный слой

- `modes.css` (17,7 КБ, 6 блоков `[data-mode]`) — ось размера; отдельным файлом, потому что `tokens.css`
  генерируется. Размеры, которые десктопный CSS держит числом (`height:36px`), режимные токены не меняют —
  они лежат в `components/<Имя>_DS/*.css`.
- `components/index.css` — 30 `@import`; `components/` — **31 файл** (`button-touch.css` — размеры,
  `button-group-mob.css` — поведение строки, `stepper-vertical.css` — структура, `box-sizing.css`).
- `prototypes/button-modes.html` — демо Desktop/Mobile рядом + таблица замеров.
- Документы: `desktop-to-mobile-plan.md` (25 КБ, 38 строк) + `.xlsx` + генератор `*-xlsx.ps1` (20 КБ),
  `mobile-mode-notes.md` 13 КБ, `mobile-workflow.md` 12,7 КБ, `mobile-steps.md` 4,3 КБ,
  `mobile-block-schemes.md` 3,7 КБ, `readme.md` 4,5 КБ.

## `Prototypes` — ручные прототипы

- `index.html` (214 строк) — хаб: массив `PAGES` (файл + подпись, `sub:true` для подстраницы), iframe, выбор в адресе.
- Обвязка ревью: `ds-frame-nav.js` (перенос ширины кадра), `ds-sizes-toggle.js` (гасит `<link>` мобильного слоя),
  `touch-mode.js` 15 КБ + `touch-mode.css` + `touch-hover-off.css` (тач-режим ≤ 768), `device-chrome/`.
- Сквозные организмы приложения (шапка, боковое меню) — в ДС: `DS/organisms/`; страницы подключают их одной строкой `../DS/connect.js`.
- Прежние страницы-образцы (серия `figma-*` и другие) со временем удалены из репозитория.
- `readme.md` (правила + каталог); рабочие папки со снимками со временем удалены; журнал дефектов ДС — в ДС: `DS/fixes.md`
  (в прототипах остался файл-указатель).

## Цепочка

```
Figma → плагин → tokens.css, styles.css            [генерируется]
      → конвертер → components/*_DS/*.css          [генерируется]
           → fixes.css, generator-rules.md         [ручное]
           → modes.css + mobile components          [ручное]
```

## Как снимать эту карту (и что докладывать)

```bash
find components-web -type f -not -path '*/.git/*' | sed 's/.*\.//' | sort | uniq -c   # состав по расширениям
ls -d components-web/components/*/ | wc -l && grep -c '@import' components-web/components/index.css
grep -o '── [A-Za-z].* ──' components-web/tokens.css                                     # коллекции токенов
for f in $(find components-mobile/components -name '*.css' -not -name index.css | sed 's|.*components/||'); do
  grep -q "$f" components-mobile/components/index.css || echo "НЕ подключён: $f"; done   # ловит и веб-агрегатор, и мобильный
```

- Цифры докладывать в таблицах («папка → файлов → что это»), а не словами: он сверяет.
- Найденное рядом (не подключённые файлы, пустые папки, `__pycache__`) — **отдельным списком с пометкой
  «не чинилось»**, не правкой по своей инициативе.
- Тот же материал просят оформить PDF-ом — рецепт и капканы:
  `references/reports-as-files-and-external-repo-reviews.md`.
