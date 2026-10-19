# Карта структуры iiko DS — что за что отвечает (замерено 15.09.2026)

Ответ на запрос владельца «подробнее расписать, как и из чего устроена наша структура: по каждой папке
и условно по файлу — что за что отвечает, для понимания». И тогда, и в следующий раз это надо давать
**по замерам файлов**, а не по памяти: он сверяет числа. Ниже — готовая карта + команды, которыми она снята.

## Четыре части (и у кого свой git)

| Часть | Git | Что это | Объём |
|---|---|---|---|
| `iiko-ds-web/` | **свой** репозиторий (публикуется как сайт ДС) | библиотека: токены + компоненты | 104 файла, 4,5 МБ (100 CSS, 3 MD, `.nojekyll`) |
| `iiko-ds-mobile/` | под версиями **корневого** `DS` | мобильный слой: режим, мобильные компоненты, страницы рекомендаций | 74 файла, 2,9 МБ |
| `iiko-ds-prototypes/` | **свой** репозиторий | ручные прототипы экранов на компонентах ДС | 93 файла, 5,2 МБ |
| `_audit/` | под версиями **корневого** `DS` | цех: данные, генератор, проверки, черновики (не публикуется) | 29 МБ |

Зависимость в одну сторону: `iiko-ds-web` (база) → `iiko-ds-mobile` (мобильные отличия) →
`iiko-ds-prototypes` и страницы рекомендаций. `_audit` читает всё, частью библиотеки не является.

## `iiko-ds-web` — корень (все восемь файлов)

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
страницы рекомендаций подключают их явно (`build.py`, строки 774–780).

Порядок подключения: `font.css → tokens.css → iiko-ds-mobile/modes.css →
iiko-ds-mobile/components/index.css → styles.css → iiko-ds-web/components/index.css → fixes.css`.

## `iiko-ds-mobile` — мобильный слой

- `modes.css` (17,7 КБ, 6 блоков `[data-mode]`) — ось размера; отдельным файлом, потому что `tokens.css`
  генерируется. Размеры, которые десктопный CSS держит числом (`height:36px`), режимные токены не меняют —
  они лежат в `components/<Имя>_DS/*.css`.
- `components/index.css` — 30 `@import`; `components/` — **31 файл** (`button-touch.css` — размеры,
  `button-group-mob.css` — поведение строки, `stepper-vertical.css` — структура, `box-sizing.css`).
- `prototypes/button-modes.html` — демо Desktop/Mobile рядом + таблица замеров.
- `prototypes/recommendations/` — **39 страниц** + `rec.css` (генерируется `build.py`) + `index.html` (оболочка).
- Документы: `desktop-to-mobile-plan.md` (25 КБ, 38 строк) + `.xlsx` + генератор `*-xlsx.ps1` (20 КБ),
  `mobile-mode-notes.md` 13 КБ, `mobile-workflow.md` 12,7 КБ, `mobile-steps.md` 4,3 КБ,
  `mobile-block-schemes.md` 3,7 КБ, `readme.md` 4,5 КБ.

## `iiko-ds-prototypes` — ручные прототипы

- `index.html` (214 строк) — хаб: массив `PAGES` (файл + подпись, `sub:true` для подстраницы), iframe, выбор в адресе.
- Обвязка ревью: `ds-frame-nav.js` (перенос ширины кадра), `ds-sizes-toggle.js` (гасит `<link>` мобильного слоя),
  `touch-mode.js` 15 КБ + `touch-mode.css` + `touch-hover-off.css` (тач-режим ≤ 768), `device-chrome/`.
- `app-header/`, `app-sidenav/` — **каркас приложения iiko** (CSS+JS+SVG), не компоненты ДС.
- Экраны: `figma-*` ×5 (Метро 1276/1277, Поставщики 7422, Прайс-лист 7431/7436, Создание товара 7450),
  `metro-general-settings.html`, `add-fasovka.html`, `compare-button-mob.html`, `KDS/` (экран, витрина UX, 6 версий карточки).
- `readme.md` (правила + каталог), `review-notes.md` 20 КБ (журнал дефектов ДС), `_crops/`, `_figma-1276-*.png`.

## `_audit` — цех

- `platform/` — 42 `<slug>.json` + `_raw/` (выгрузки xml/scss/html) + `_src/`; ключи: `component`,
  `platforms` (MD3 / iOS HIG), `not_recommended_ru`, `verdict_ru`, `verified_on`.
- `rec/`: `build.py` **913** · `mock.py` **182** (детали макета `status/head/body/foot/sheet/btn/iconbtn/lst/input_field/tabs/checkbox/divider/check_balance`) ·
  `icons.py` + `icon-map.json` 34 (инлайн-SVG Material Symbols — шрифт иконок не грузится, прототип должен работать без сети) ·
  `boxsize-list.json` 44 · `apply_out.py` 97 (`out/` → `data/`, `--build` сразу собирает, поле **перезаписывается** целиком) ·
  `data/` **38** (`slug, component, ds_page, desc_ru, category_ru, category_note_ru, summary_ru, panels, changes, behaviour_html, why_ru, why_sources, result_html, examples, preview_html, logic_ru, platform_notes_ru, patterns_ru`) ·
  `data-tech/` **9** (`ds_values, platforms, verdict, hover_on_touch, measured_ru`) ·
  `out/` (edits 37, previews 37, patterns 38, new-patterns 38, platforms 0) · `checks/` **67 файлов**
  (главная `check-patch.py`, 241 строка).
- Корень `_audit`: `spec-catalog.json` 272 КБ, `ds-css-values.json` 80 КБ, пробы `*.mjs`/`*.ps1`, скриншоты-замеры.

## `build.py` — что это за сборщик

Вход — только `data/*.json`; во Figma и в CSS ДС он не ходит. `main()`: (1) пишет `rec.css` из своей
константы `CSS`; (2) удаляет старый `rec.js`; (3) читает 38 `data/*.json`, сортирует по компоненту;
(4) `page(d)` → `recommendations/<slug>.html`; (5) `index_page(all_data)` → `index.html`.

| Функция | Что делает |
|---|---|
| `page(d)` | шаблон страницы целиком |
| `panel(side, d)` | панель Desktop / Mobile на одной разметке |
| `changes_table(d)` | таблица «Что меняется» + колонка «Правка» |
| `screens_card(d)` | блок «На экране»: `preview_html` как есть в `.phones__item`, второй экран → `data-preview="edit"` |
| `found_card(d)` | плашка «Найдено в ДС» |
| `review_row` / `review_comment` / `edits_of` | решения ревью и поля правок |
| `esc()`, `build_version()` | экранирование и метка `?v=` |
| `index_page(all_data)` | меню-оболочка, `#slug` — прямая ссылка |

Ловушки сборщика (обе проверены): `%`-форматирование (`page()` — литеральный процент в разметке роняет
все страницы) и `preview_html` обязан нести корпус телефона ровно с одним `data-mode="mobile">`.
Чего сборщик **не** делает: не генерирует CSS ДС, не читает Figma, не проверяет качество (это `checks/`).

## Цепочка

```
Figma → плагин → tokens.css, styles.css            [генерируется]
      → конвертер → components/*_DS/*.css          [генерируется]
           → fixes.css, generator-rules.md         [ручное]
           → modes.css + mobile components          [ручное]
                → data/*.json                       [ручное / заготовки]
                     → build.py → recommendations/* [генерируется]
                          → check-patch.py          [проверка]
```

## Как снимать эту карту (и что докладывать)

```bash
find iiko-ds-web -type f -not -path '*/.git/*' | sed 's/.*\.//' | sort | uniq -c   # состав по расширениям
ls -d iiko-ds-web/components/*/ | wc -l && grep -c '@import' iiko-ds-web/components/index.css
grep -o '── [A-Za-z].* ──' iiko-ds-web/tokens.css                                     # коллекции токенов
wc -l _audit/rec/build.py _audit/rec/mock.py iiko-ds-web/*.css
grep -n '^def ' _audit/rec/build.py                                                   # карта функций сборщика
python -c "import json;d=json.load(open('_audit/rec/data/button.json',encoding='utf-8'));print(list(d))"
for f in _audit/rec/checks/*.py; do python - "$f" <<'EOF'   # назначение пробы из её docstring
import ast,sys;print(sys.argv[1], (ast.get_docstring(ast.parse(open(sys.argv[1],encoding='utf-8').read())) or '').splitlines()[:1])
EOF
done
for f in $(find iiko-ds-mobile/components -name '*.css' -not -name index.css | sed 's|.*components/||'); do
  grep -q "$f" iiko-ds-mobile/components/index.css || echo "НЕ подключён: $f"; done   # ловит и веб-агрегатор, и мобильный
```

- Цифры докладывать в таблицах («папка → файлов → что это»), а не словами: он сверяет.
- Найденное рядом (не подключённые файлы, пустые папки, `__pycache__`) — **отдельным списком с пометкой
  «не чинилось»**, не правкой по своей инициативе.
- Тот же материал просят оформить PDF-ом — рецепт и капканы:
  `references/reports-as-files-and-external-repo-reviews.md`.
