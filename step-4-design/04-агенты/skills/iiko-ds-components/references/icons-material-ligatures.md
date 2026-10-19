# Иконки в iiko DS — только Material Icons лигатурой (11.09.2026)

## Конвенция (переписана владельцем в спеке)

Владелец заменил пункт «Иконки» в `iiko-ds-web/iiko-ds-spec.md` на:

> **Иконки** — Google Material Icons, вставляются по имени (`<span class="material-icons">имя</span>`),
> цвет наследуется `currentColor`. Обязательного списка нет — берём из каталога Google; исключение —
> бренд-иконка iiko (SVG).

В том же заходе он убрал из `font.css` вшитый base64 Roboto и поставил онлайн-`@import` Google Fonts
(302 байта вместо 92 КБ). То есть **сеть в проекте теперь допускается** — прежние «прототипы работают
без интернета» и «SVG 20×20» в старых заметках устарели.

Разметка в примерах: лигатура живёт внутри слота ДС, размер — через `font-size`, а не через `width/height`
самого svg:

```html
<span class="ds-search__icon"><span class="material-icons" style="font-size:20px">search</span></span>
```

Слоты ДС уже `display:inline-flex; align-items:center; justify-content:center` с размером из токена
(`--ds-size-4x` = 16, `--ds-size-5x` = 20, `--ds-size-6x` = 24) — поэтому `font-size` лигатуры ставится
равным размеру слота. В каркас страниц (`_audit/rec/build.py`, константа `CSS`) добавлено:

```css
.panel .material-icons{line-height:1;display:inline-block}
```

иначе строка лигатуры выше слота и глиф съезжает.

## Какая иконка куда (страницы рекомендаций)

| Компонент / слот | Имя Material |
|---|---|
| `ds-search__icon` / `__right-icon` | `search` / `close` (очистка) |
| `ds-arrow-select`, `ds-autocomplete-form__icon` | `arrow_drop_down` |
| `ds-input-datepicker__icon` | `calendar_today` |
| `ds-control-panel__button-icon` | `chevron_left` / `chevron_right` |
| `ds-input-timepicker__icon` | `schedule` |
| `ds-input-number-but-icon__icon` (2 шт.) | `expand_less` / `expand_more` |
| `ds-expansion__arrow` | `expand_more` (свёрнута) / `expand_less` (раскрыта) |
| `ds-expansion__icon` | `receipt_long`, `block` (disabled), `info` (info-вариант) |
| `ds-tree__icon` | `expand_more` у родителей, `subdirectory_arrow_right` у листьев |
| `ds-list-item__icon`, `ds-select-item__icon`, `ds-menu-item__icon` (блюда) | `restaurant` |
| `ds-menu-item__icon` (заказы: открыть / повторить / удалить) | `receipt_long`, `refresh`, `delete` |
| `ds-select-item__icon` (заказы) | `receipt_long` |
| `ds-status__icon` (Черновик, Готово, Ждёт проверки, Ошибка) | `edit`, `check_circle`, `schedule`, `error` |
| `ds-snackbar__icon` | `error` |
| `ds-banner__icon` | `info` |
| `ds-chips__icon` (чип «Фильтр») | `tune` |
| `ds-icon-group__icon`, `ds-btn-icon__icon` | `settings`, `edit`, `delete`, `more_vert`, `add`, `chevron_right` |

## Как это было переведено (повторяемо)

Старые примеры держали самодельные SVG; менять их руками по одному не надо:

1. Сверить пути: у SVG-иконок путь → имя даёт обратная карта (`d` → имя). Символы Material беру с
   `raw.githubusercontent.com/google/material-design-icons/master/symbols/web/<имя>/materialsymbolsoutlined/<имя>_24px.svg`
   (curl работает; `web_extract` на этом хосте отвечает 403). Старая схема `<категория>/<имя>/materialicons/24px.svg`
   больше не существует — 404.
2. Пройти JSON-данные примеров (`_audit/rec/data/*.json`, включая вложенные примеры панелей!) и заменить
   `<svg …><path d="…"/></svg>` на лигатуру с `font-size` из прежнего `width`.
3. `python build.py`, затем скрин и взгляд глазами.

Готовые помощники лежат в `_audit/rec/` (`icons.py` — карта имён и функция `icon()`, `icon-map.json` —
соответствие слотов).

## Ловушка, из-за которой появились треугольники

`document.fonts.check('24px "Material Icons"')`, вызванный **сразу при разборе страницы**, возвращает
`false` — шрифт к этому моменту ещё не загружен. Я поверил этому и нарисовал заглушки (треугольники),
получив от владельца «Посмотри на иконки. Это же жесть, что ты понавставлял».

Верная проверка:

```js
await document.fonts.load('24px "Material Icons"', 'close');
await new Promise(r => setTimeout(r, 1500));
fonts.check('24px "Material Icons"')      // true
span.getBoundingClientRect().width         // 24 у глифа, ~49 у слова «close»
```

Правило: **отсутствие ассета сначала проверять нормально, и только потом что-то подставлять.** Если
иконка действительно не встаёт — сказать об этом и спросить, а не затыкать «похожим».

## Скрин с иконками нужно снимать с ожиданием

Headless Chrome по умолчанию фотографирует страницу до загрузки веб-шрифта, и лигатура попадёт в кадр
словом. Скрины страниц с иконками делать с `--virtual-time-budget=9000` (и/или проверять замер ширины
глифа перед выводом).
