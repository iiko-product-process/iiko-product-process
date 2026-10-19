# Mobile mode conversion — рабочий пример: Button

Первый компонент, переведённый на режим `data-mode="mobile"`. Служит шаблоном
для остальных (Button icon, Input, List, Tabs, Chips, Banner, Snackbar…).

## Статус на конец сессии

Всё спроектировано, но **не записано**: `write_file` / `patch` отклонялись
approval-гейтом ACP-клиента (разбор и починка — в
`hermes-desktop-backend-diagnostics`, раздел про approval-гейт). Что значит для
следующего захода:

- `iiko-ds-web/modes.css` ещё не существует, `button.css` не токенизирован,
  демо-страница `button-modes.html` не собрана;
- в `iiko-ds-spec.md` соглашения о режимах нет вообще — по grep'у в нём ноль
  упоминаний `data-mode`, `modes.css`, `Button_mob` (раздел 13 из
  `mobile-mode-notes.md` остался планом);
- файловая часть работы начинается с вопроса о разрешении на запись — без него
  считать/замерять можно, а создавать файлы нет; сперва это, потом код.
- `iiko-ds-web`: рабочее дерево чистое, ветка `main`, все файлы — под git;
  правки стоит группировать в один осмысленный коммит, а не дробить по файлу.

## Источники значений (читать до проектирования)

| Источник | Что берём |
|---|---|
| `iiko-ds-mobile/desktop-to-mobile-plan.md` | Группа A: Button меняет **только размерные значения**; `_mob` уже собран в Figma |
| `iiko-ds-prototypes/compare-button-mob.html` | Числа `Button_mob`, снятые из Figma |
| `iiko-ds-web/iiko-ds-spec.md` (якорь `#### Button \``) | Десктоп: M 36, S 28, XS 24; свойства Size/Style/Type/State |
| `iiko-ds-web/components/Button_DS/button.css` | Текущая реализация (там были хардкоды) |

### `Button_mob` из Figma (страница Button_DS, COMPONENT_SET Button_mob)

Высота 44 · паддинги 12 (верт.) / 16 (гор.) · текст 16 px / 500 · иконка 20
(вектор 12×12) · радиус 8 (**без изменений**) · цвет accent `#448AFF` (**без
изменений**) · Sizing HUG. Совпадает с iOS 44 pt; MD3 даёт 40 dp + pill-радиус
20 dp — заимствуем эргономику, не внешний вид.

## Маппинг токенов (M): десктоп → мобила

| Токен | Десктоп | Мобила |
|---|---|---|
| `--ds-button-m-size-pad-top` / `-bottom` | `--ds-space-2x` (8) | `--ds-space-3x` (12) |
| `--ds-button-m-size-pad-left` / `-right` | `--ds-space-3x` (12) | `--ds-space-4x` (16) |
| `--ds-button-m-size-text-size` | `--ds-typography-body-font-size-s` (14) | `--ds-typography-body-font-size-m` (16) |
| `--ds-button-m-size-gap` | `--ds-space-2x` (8) | без изменений |
| `--ds-button-m-size-icon-size` | `--ds-icon-size-size-5x` (20) | без изменений |
| `--ds-button-border-radius` | `--ds-radius-2x` (8) | без изменений |

Всё это уже есть в `tokens.css` (коллекция `Component`) — новых переменных
заводить не нужно, нужен только блок `[data-mode="mobile"]` в `modes.css`.

## Геометрия: почему высота не токен

В `tokens.css` у Button есть pad/gap/icon/text — и **нет** height: в Figma высота
HUG. Примитива 44 px в Base Size тоже нет (максимум `--ds-size-10x` = 40).
Поэтому высота собирается из строки текста и паддингов:

| Размер | Паддинги | Строка | Высота |
|---|---|---|---|
| XS | 4 / 6 | `--ds-typography-caption-line-height-l` 16 | 4+4+16 = **24** |
| S | 4 / 8 | `--ds-typography-body-line-height-s` 20 | 4+4+20 = **28** |
| M | 8 / 12 | `--ds-typography-body-line-height-s` 20 | 8+8+20 = **36** |
| M · mobile | 12 / 16 | то же 20 (не body-m 24!) | 12+12+20 = **44** |

Важно: на мобиле кегль растёт до 16, но строка остаётся 20 px — так 44 px
сходится с Figma. Иконка (20) равна строке, поэтому содержимое не раздувает
высоту.

## Дефекты, которые ловятся при токенизации (встречались в button.css)

1. Комментарий, съевший селектор: `.ds-btn--xs /* … */ .ds-btn__label {` —
   валидный CSS, но правило превращается в потомка; искать в местах ручных
   правок.
2. Дубль общего блока ниже по файлу перебивает размерные варианты:
   `.ds-btn__icon { font-size: 20px }` (позже по файлу) отменял 16 px у XS.
3. Иконка-SVG реагирует только на `width/height`, не на `font-size` — нужен
   `.ds-btn__icon svg { width: 1em; height: 1em; display: block }`.

## Recipe: демо-страница режимов

`iiko-ds-prototypes/button-modes.html` — по образцу
`metro-general-settings.html`: локальные `../iiko-ds-web/font.css`, `tokens.css`,
**`modes.css`**, `styles.css`, `components/index.css`.

- Две колонки: `<div data-mode="desktop">` и `<div data-mode="mobile">` — один
  и тот же HTML кнопок, разный режим. Плюс переключатель `data-mode` на
  `<html>` для проверки каскада «как в бою».
- Таблица замеров из JS: `getBoundingClientRect().height`, `getComputedStyle`
  font-size/padding по каждому размеру — сверять с 24/28/36 и 44.
- Матрица: Style (accent/neutral/positive/negative/warning) × Type
  (filled/outlined/text), состояния default/hover/active/disabled, иконка
  слева/справа, `--full-width`, группа.

## Открытые вопросы (решает пользователь, не токены)

1. **S (28) и XS (24) на мобиле**: оставить как есть или расширять зону нажатия
   до 48 dp обёрткой (`::before`, как в Angular Material `mat-mdc-icon-button`)?
2. **Hover на тач-устройствах**: обернуть hover-правила в `@media (hover: hover)`
   (уходит «залипание» после тапа) — но правка меняет и десктопное поведение.
3. **44 px (Figma, = iOS) против 48 dp (Material)** — какое число считаем нормой.
4. **Full-width кнопки в футерах форм**: модификатор `.ds-btn--full-width`
   (добавлен как опция) против отдельного контейнера `Bottom action bar_mob`.
5. **Loading-состояние**: в спеке у Button заявлено `State Loading`, в CSS его
   нет — дорабатывать отдельно на обоих режимах.
