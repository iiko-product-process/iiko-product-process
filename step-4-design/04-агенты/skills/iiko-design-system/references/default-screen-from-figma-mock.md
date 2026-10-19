# Дефолтный экран блока «На экране»: макет Figma → разметка ДС

Когда владелец пишет «Собери примерно вот такой экран» и даёт ссылку на Figma-узел — речь о
**дефолтном** экране блока «На экране» (меню паттернов + два одинаковых телефона). Задача: снять
макет и собрать его разметкой ДС, а не нарисовать похожее своими руками.

## 1. Снять макет (Figma Dev Mode MCP)

Клиент — `scripts/figma-mcp.py` скилла `iiko-ds-components` (только stdlib). Файл должен быть
**активной вкладкой в Figma desktop**, иначе «No node could be found for the provided nodeId».

```bash
python scripts/figma-mcp.py call get_metadata   --node 5581:31479 > meta.xml
python scripts/figma-mcp.py call get_screenshot --node 5581:31479 --json-out shot.json
```

- `get_metadata` даёт структуру слоёв: id, имя, x/y/width/height, `hidden`. **Имена текстовых слоёв — это
  подписи в макете** (часть слов печатается кракозябрами в терминале — читать файл как UTF-8).
- `get_screenshot` кладёт в файл `{"result":{"content":[{"type":"image","data":"<base64>"}]}}` —
  декодировать base64 в PNG и смотреть глазами: это и есть эталон для сборки.
- `get_design_context` (reference-код) на большом фрейме **отваливается по таймауту** (незакрывающийся
  SSE) — не долбить его: метадаты + скриншота достаточно, чтобы собрать экран из компонентов ДС.
- Метадата на инстанс (например `Button`) детей **не разворачивает** — подписи кнопок и текст шторки
  брать со скриншота.

## 2. Слой макета → класс ДС

Пример разбора макета «Заказ товаров на склад» (file «Склад_Заказ-товаров», node 5581:31479, 375×800):

| Слой макета Figma | Чем собирать |
|---|---|
| `Header full` (браузерная рамка, вкладка, «iiko») | **не переносить** — это хром браузера в макете, не экран приложения |
| Header page: иконки + заголовок | `.phone__head` + `ds-btn-icon` (назад/⋮) + `.phone__title` |
| `Status` («Черновик») | `.ds-status.ds-status--warning` + `__label` |
| поставщик / даты | каркас: `.phone__kv` (иконка + подпись + значение), `ds-divider`, `.phone__sep` |
| `Tabs` (Детали/Заказ/История) | `.ds-tabs` + `.ds-tab`/`.ds-tab--active` |
| `filters and search` | `.ds-checkbox` («Только выбранные») + `.ds-search.ds-search--xs` (круглая) |
| `Button` на всю ширину («＋ Добавить продукт») | `.ds-btn.ds-btn--m.ds-btn--accent.ds-btn--text` + иконка `add` |
| `Card view` / `Card header` + `✕` | `.ds-card.ds-card--outlined` либо каркас `.phone__card--item` + `ds-btn-icon--xs` для закрытия |
| карточки с раскрытием (`Inner card`, `Expansion panel`) | `ds-card` + `ds-list-item`/`ds-input-number`, если нужен состав |
| `Bottom action bar` (сумма + группа) | `.phone__foot` + `.ds-btn-group.ds-btn-group--horizontal` |
| `Bottom sheet` (`curtain` + `Textarea` + группа) | `.phone__sheet` + `.phone__grabber` + `.ds-textarea` + `ds-btn-group` |
| `Backdrop` | `phone__scrim` есть в каркасе, но в макете затемнение **визуально не читается** — в дефолте не выводить, экран должен остаться светлым |

## 3. Разметка и данные

`preview_html` в `_audit/rec/data/<slug>.json` = **корпус + экран**:

```html
<div class="phone"><div class="phone__screen" data-mode="mobile">…</div></div>
```

Ровно одно вхождение `data-mode="mobile">` — `screens_card()` делает из него второй экран заменой на
`data-mode="mobile" data-preview="edit">`. Забыл корпус — экраны без рамки, мобильный режим не
подключается (компоненты рисуются десктопными), правки из 4-й колонки некуда писать.

Слоты кнопок: `data-buttons="screen"` (кнопки в теле экрана) и `data-buttons="sheet"` (в шторке);
внутри — обычная разметка `.ds-btn`, часто в `.ds-btn-group`. При выборе паттерна JS подставляет в них
кнопки примера **одинаково на двух экранах**; поля «Правка» пишутся только в правый экран.

Детали макета собирать через `_audit/rec/mock.py`: `status/head/body/foot/line/actions/icons/chips/row/
divider/search/input_field/lst/btn/iconbtn/checkbox/radio/toggle/tabs/sheet/card/card_head/screen/phones`
и `check_balance(html)` (проверка баланса `<div>` — глазами ошибку не видно).

Новые классы каркаса (`.phone__kv/.phone__kv-label/.phone__kv-value/.phone__sep/.phone__filter/
.phone__grabber/.phone__card--item/.phone__card-body`) добавлять в CSS-константу `build.py` — `rec.css`
генерируется и правки в нём исчезают. Цвета/размеры — токенами `--ds-*`, не хардкодом.

Если мобильный слой мешает: в `data-mode="mobile"` `ds-search` растягивается на 100 %
(`iiko-ds-mobile/components/Search_DS`), поэтому круглый XS-поиск закрепляется правилом каркаса
`.phone__filter .ds-search--xs{width:var(--ds-size-9x);min-width:var(--ds-size-9x);flex:0 0 auto}`.
Сам `iiko-ds-web` не править.

## 4. Проверка (проба-iframe + headless)

Собрать: `python _audit/rec/build.py <slug>` (или через importlib — `page(data)` + `CSS`), затем проба в
`_audit/rec/checks/_pN.html`: iframe на `../../../iiko-ds-mobile/prototypes/recommendations/<slug>.html`
(тот же origin через `http://127.0.0.1:8899`), в скрипте — печатать в `<pre id="out">`: число экранов и штор,
состав каждого `[data-buttons]`, число пунктов текста паттерна, число элементов, вылезших за границы
экрана, и высоты первых кнопок левого/правого экрана после правки `height`.

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --no-sandbox \
  --user-data-dir="$(cygpath -w "$LOCALAPPDATA/Temp/cp9")" --virtual-time-budget=20000 \
  --window-size=1600,2400 --dump-dom "http://127.0.0.1:8899/_audit/rec/checks/_pN.html" \
  | sed -n '/<pre id="out">/,/<\/pre>/p' | sed 's/<[^>]*>//g'
```

Скриншот блока: `--screenshot` + кроп по координатам блока (смотреть глазами, обрезка кнопок и полей
видна только на картинке). Пробу после проверки удалить, временные скрины держать в
`%LOCALAPPDATA%/Temp/ds-shots/`.

## 5. Отчёт владельцу

Перечислить: что взято из макета, **что осознанно не перенесено** (например нижняя панель со суммой —
в макете она перекрыта открытой шторкой) и что будет, если он захочет иначе. Плюс числа проверки:
слоты, подстановка паттерна, правка только правого экрана, ноль вылезших за экран элементов.

## Принятый пример (14.09.2026)

Экран «Заказ 2026-1205235-1280» (складской заказ, node 5581:31479): шапка «← Заказ … ⋮» из `ds-btn-icon`,
статус «Черновик», «Поставщик: Муравьиная ферма», строки отправки/доставки, табы «Детали | Заказ |
История», чекбокс «Только выбранные» + круглый поиск, кнопка «＋ Добавить продукт», карточки «Сливки /
Арт. 00025 · Остаток: 10 порц» и «Салат цезарь», шторка «Комментарий» с `ds-textarea` и группой
[Отменить]/[Сохранить] — два одинаковых экрана, слоты `screen` и `sheet`.
