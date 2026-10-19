# iiko Design System — база компонентов и токенов

> **Точка входа для сборки прототипов — документ «Подключение DS»** (одна строка подключения,
> карта компонентов и правила): https://github.com/iiko-DS/Prototypes/blob/main/prototyping-guide/подключение-ds.md
>
> Этот файл — справочная база дизайн-системы: описания и классы компонентов, токены, правила сборки.
> Собирая прототип, берите значения отсюда: классы — из [карты классов](#карта-классов-css-библиотеки),
> значения — из таблиц токенов. CSS и токены живут файлами в репозитории — ссылки в разделе
> [CSS и токены в файлах библиотеки](#css-и-токены-в-файлах-библиотеки).

Главное правило для ИИ: референс задаёт структуру и тексты, **внешний вид — только из этой ДС** (см. [Общие правила](#общие-правила), пункт 0).

---

Единый источник компонентов и токенов для всех прототипов: **токены + компоненты + иконки + правила** — у всех одни и те же.

Главное для ИИ: работать как разработчик высокой квалификации — сначала разобрать макет/описание и составить план, потом верстать. Порядок разбора — в разделе [Как думать при сборке](#как-думать-при-сборке-порядок-работы-опытного-разработчика).

## Содержание

1. [Общие правила](#общие-правила)
2. [Как думать при сборке (порядок работы разработчика)](#как-думать-при-сборке-порядок-работы-опытного-разработчика)
3. [Токены](#токены)
   - Палитра · Семантические цвета · Компонентные цвета · Размеры · Отступы · Радиусы · Типографика · Тени
4. [Компоненты](#компоненты)
   - [Каталог компонентов Figma](#каталог-компонентов-figma-все-106)
   - [Карта классов CSS-библиотеки](#карта-классов-css-библиотеки)
5. [Иконки](#иконки-google-material-icons)
6. [CSS и токены в файлах библиотеки](#css-и-токены-в-файлах-библиотеки)
7. [Чек-лист соответствия ДС](#чек-лист-соответствия-дс)
## Общие правила

0. **⛔ НЕ ГАДАТЬ (закон над законом).** Права гадать нет. Каждое значение (ширина, цвет, размер, шрифт, иконка, состояние) берётся ТОЛЬКО из источника — код макета (`mockup.md`) + этот спек. Нет значения/компонента в источнике → СТОП, СПРОСИТЬ и предложить замену из ДС. «Свериться, а не гадать» = действие ДО правки, не фраза; сказать «сверюсь» и угадать = нарушение.
0. **Приоритет ДС над референсом (главное правило).** Референс (скриншот, макет, описание) задаёт **структуру, состав блоков и тексты**. Внешний вид берётся **только из этой дизайн-системы**. Если компонент на референсе отличается от ДС (другой цвет, радиус, высота, шрифт, самодельная панель) — использовать компонент ДС, а не копировать референс. Ничего не подгонять «на глаз» под картинку: размеры, отступы, типографика — только из токенов и параметров компонентов ниже. Если подходящего компонента в ДС нет — взять ближайший из каталога и явно пометить это в результате.

**ЗАКОН №1 (никогда не нарушать): компоненты — ТОЛЬКО из ДС.** Есть ДС-компонент (ds-card, ds-stepper, ds-expansion-panel/group/content, ds-table-header/content-row/cell, ds-list-item, ds-search, ds-btn, ds-input, ds-banner, ds-tabs, ds-slide-toggle, ds-input-number) → использовать ЕГО, **НЕ рисовать свой класс**. Свои классы допускаются **только** для каркаса/лейаута, у которого нет ДС-компонента (page/grid/modal/toolbar/footer). Нет ДС-компонента → **остановиться, СПРОСИТЬ и ПРЕДЛОЖИТЬ замену из ДС**; если замены нет — только тогда рисовать своё, строго в рамках ДС (токены), ничего не выдумывать и не подбирать «похожее». Иконки берём из Google Material Icons (раздел «Иконки»).
1. **Никаких хардкодов.** Цвета, радиусы, отступы, размеры и шрифты — только через токены `var(--ds-*)`.
2. **Классы компонентов** — префикс `ds-`: `ds-btn`, `ds-input`, `ds-checkbox`, `ds-radio`, `ds-badge`. Модификаторы через `--`: `ds-btn--m`, `ds-btn--accent`, `ds-btn--filled`.
3. **Шрифт** — Roboto 400/500 (размеры, веса, letter-spacing — из токенов типографики).
4. **Иконки** — Google Material Icons, вставляются по имени (`<span class="material-icons">имя</span>`), цвет наследуется `currentColor`. Обязательного списка нет — берём из каталога Google (раздел «Иконки»); исключение — бренд-иконка iiko (SVG).
5. **Состояния** — нативные: hover/press через CSS, disabled через атрибут, error через класс `--error`.
6. **Компонентные токены** — использовать специфичные для компонента (`--ds-color-button-*`, `--ds-color-checkbox-*`), а не общие (`--ds-color-text-*`, `--ds-color-icon-*`).

### Как думать при сборке: порядок работы опытного разработчика

Общие рекомендации для любого экрана и любой задачи. Смотреть на макет, скриншот или текстовое описание
нужно **как разработчик высокой квалификации, который получил задание сверстать интерфейс**: сначала разбор
и план, потом код. Не начинать с написания HTML.

**Шаг 1. Понять экран целиком.** Определить тип страницы (например: форма, пошаговый мастер, настройки,
список или таблица, карточка объекта, диалог) и главное действие пользователя. Тип экрана подсказывает
набор компонентов: где шаги — компоненты шагов, где набор настроек — контейнеры-карточки с переключателями
и полями, где перечень данных — таблица или список.

**Шаг 2. Разложить на зоны сверху вниз.** Типичные зоны: шапка, строка заголовка с действиями, навигация,
тело (секции/группы), панель действий. Для каждой зоны определить ширину и выравнивание, а также
вертикальные ритмы — отступы между зонами берутся из токенов отступов, а не подбираются на глаз.

**Шаг 3. Сопоставить каждый блок с компонентом ДС** по карте классов и каталогу компонентов:
«блок → компонент → вариант (Size/Type/State)». Ориентиры выбора носят условный характер, проверять по
каталогу: рамка вокруг группы контента — контейнер-карточка; раскрывающаяся панель-пояснение — панель
раскрытия; короткое сообщение в строку — баннер; подсказка по наведению — тултип; поле с выпадающим
значением — поле ввода с иконкой-стрелкой; включение/выключение настройки — переключатель;
выбор нескольких значений — чекбоксы; выбор одного значения — радиокнопки.
Если точного компонента в ДС нет — взять ближайший и **явно пометить** это, а не рисовать свой.

**Шаг 3а. Однотипных элементов больше одного → групповой компонент.** Если элементов одного вида
**два и более** (кнопки, чекбокса, радио) и у компонента в ДС есть **группа** — использовать именно
**групповой компонент**: 2+ кнопки → `Button group` (`.ds-btn-group`), 2+ чекбокса → `Checkbox group`,
2+ радио → `Radio group`. Одиночный элемент — обычный компонент. У `Button group` есть версия с маржинс
(`--margins`, паддинг 8px 16px) — она в основном для **футера/нижней панели** (отступ от краёв контейнера,
напр. «Отмена/Сохранить» в `__footer`); в тулбаре/списке (середина экрана) группа — **без маржинс**.

**Зазор между кнопками в группе — только из токена, НЕ ставить произвольный отступ.**
`Button group` задаёт `gap` токеном `--ds-button-group-gap` (= `--ds-space-2x`, 8px). Не выставлять
`margin`/`gap` у отдельных кнопок вручную — это ломает единый интервал и «разъезжается» вид.
Разметка горизонтальной группы: `<div class="ds-btn-group ds-btn-group--horizontal">КНОПКИ</div>`.
Одна кнопка — обычный `Button`, **без** обёртки `ds-btn-group`.

**Шаг 4. Определить данные и состояния.** Что заполнено, что плейсхолдер, что обязательно, что включено или
выключено, что недоступно, где ошибка. Тексты — дословно из задания, без переписывания и «улучшений».

**Шаг 5. Спланировать раскладку до кода.** Один общий слой CSS каркаса (сетка, отступы, ограничения ширины)
на flex/grid с отступами из токенов. Компоненты ДС в этом слое **не переопределять** — они приходят
готовыми; каркас только расставляет их. Никаких `style="..."` в разметке.

**Шаг 6. Собирать в правильном порядке.** Сначала скелет зон и порядок блоков (пустые контейнеры) →
затем компоненты сверху вниз → затем иконки (Material Icons по имени) и состояния → в конце отступы и выравнивание.
Так дефекты видны сразу, а не всплывают в конце.

**Шаг 7. Ничего не добавлять от себя.** В прототипе только то, что есть в задании: не тащить слоты
компонента (подвал, панель действий, разделители), которых нет в описании, не придумывать иконки, поля и
кнопки. Не хватает данных — спросить, а не додумать.

**Шаг 8. Проверить как на код-ревью.** Пройти чек-лист и сверить в инспекторе: высоты, радиусы и отступы
совпадают с параметрами компонентов, цвета равны значениям токенов, нет горизонтального скролла, консоль
без ошибок, все иконки видимы (не нулевого размера). Если строки или колонки «разъезжаются» — причина
почти всегда в **разной высоте строк**, а не в ширине колонок: выравнивать высоту/`vertical-align`.

**Типичные ошибки, за которые вёрстку возвращают:** свои классы вместо классов ДС; отдельные элементы
вместо группового компонента при двух и более однотипных; `style="..."` в разметке;
подгонка размеров «на глаз» под картинку; переопределение стилей компонента;
свой класс рядом с уже существующим в ДС; блоки, которых не было в задании.

## Токены

Все токены сгенерированы из Figma (DS.json → tokens.css). В прототипах использовать эти имена как CSS-переменные: `var(--ds-palette-accent-500)`.

### Палитра (Base Color)

Базовые цвета бренда. Семантические и компонентные токены ссылаются на них.

| Токен | Значение |
|---|---|

### Семантические цвета (Color)

Цвета смысловых состояний: brand (акцент), positive, negative, neutral, contrast-1…4.

| Токен | Значение |
|---|---|

### Компонентные цвета (Component)

Цвета конкретных компонентов. **В прототипах использовать именно эти токены**, а не общие (Text/Icon).

### Base Size

| Токен | Значение |
|---|---|

### Space

| Токен | Значение |
|---|---|

### Radius

| Токен | Значение |
|---|---|

### Base Stroke

| Токен | Значение |
|---|---|

### Типографика (Typography + Base Typography)

Шрифт: **Roboto** (400/500). Размеры, веса, межбуквенные расстояния и высоты строк — только из токенов.

| Токен | Значение |
|---|---|

### Тени (Shadows)

| Токен | Значение |
|---|---|

### Текстовые стили ДС (готовые классы)

Стили из Figma один в один. В разметке ставить **класс**, а не набор свойств: `<span class="ds-text-body-m-normal-regular">`.

| Стиль Figma | Класс | font (вес размер/интерлиньяж) | Трекинг | Регистр |
|---|---|---|---|---|
| Header L (34)/Normal/Regular | `.ds-text-header-l-34-normal-regular` | `400 34px/40px "Roboto"` | 0px | none |
| Header L (34) / Normal / Medium | `.ds-text-header-l-34-normal-medium` | `500 34px/40px "Roboto"` | 0px | none |
| Header L (34) / Caps / Regular | `.ds-text-header-l-34-caps-regular` | `400 34px/40px "Roboto"` | 0px | uppercase |
| Header L (34) / Caps / Medium | `.ds-text-header-l-34-caps-medium` | `500 34px/40px "Roboto"` | 0px | uppercase |
| Header M (24) / Normal / Regular | `.ds-text-header-m-24-normal-regular` | `400 24px/32px "Roboto"` | 0.5px | none |
| Header M (24) / Normal / Medium | `.ds-text-header-m-24-normal-medium` | `500 24px/32px "Roboto"` | 0.5px | none |
| Header M (24) / Caps / Regular | `.ds-text-header-m-24-caps-regular` | `400 24px/32px "Roboto"` | 0.5px | uppercase |
| Header M (24) / Caps / Medium | `.ds-text-header-m-24-caps-medium` | `500 24px/32px "Roboto"` | 0.5px | uppercase |
| Header S (20) / Normal / Regular | `.ds-text-header-s-20-normal-regular` | `400 20px/28px "Roboto"` | 0.5px | none |
| Header S (20) / Normal / Medium | `.ds-text-header-s-20-normal-medium` | `500 20px/28px "Roboto"` | 0.5px | none |
| Header S (20) / Caps / Regular | `.ds-text-header-s-20-caps-regular` | `400 20px/28px "Roboto"` | 0.5px | uppercase |
| Header S (20) / Caps / Medium | `.ds-text-header-s-20-caps-medium` | `500 20px/28px "Roboto"` | 0.5px | uppercase |
| Body L (18) / Normal / Regular | `.ds-text-body-l-18-normal-regular` | `400 18px/24px "Roboto"` | 0.5px | none |
| Body L (18) / Normal / Medium | `.ds-text-body-l-18-normal-medium` | `500 18px/24px "Roboto"` | 0.5px | none |
| Body L (18) / Caps / Regular | `.ds-text-body-l-18-caps-regular` | `400 18px/24px "Roboto"` | 0.5px | uppercase |
| Body L (18) / Caps / Medium | `.ds-text-body-l-18-caps-medium` | `500 18px/24px "Roboto"` | 0.5px | uppercase |
| Body M (16) / Normal / Regular | `.ds-text-body-m-16-normal-regular` | `400 16px/24px "Roboto"` | 0.5px | none |
| Body M (16) / Normal / Medium | `.ds-text-body-m-16-normal-medium` | `500 16px/24px "Roboto"` | 0.5px | none |
| Body M (16) / Caps / Regular | `.ds-text-body-m-16-caps-regular` | `400 16px/24px "Roboto"` | 0.5px | uppercase |
| Body M (16) / Caps / Medium | `.ds-text-body-m-16-caps-medium` | `500 16px/24px "Roboto"` | 0.5px | uppercase |
| Body S (14) / Normal / Regular | `.ds-text-body-s-14-normal-regular` | `400 14px/20px "Roboto"` | 0.5px | none |
| Body S (14) / Normal / Medium | `.ds-text-body-s-14-normal-medium` | `500 14px/20px "Roboto"` | 0.5px | none |
| Body S (14) / Caps / Regular | `.ds-text-body-s-14-caps-regular` | `400 14px/20px "Roboto"` | 0.5px | uppercase |
| Body S (14) / Caps / Medium | `.ds-text-body-s-14-caps-medium` | `500 14px/20px "Roboto"` | 0.5px | uppercase |
| Caption L (12) / Normal / Regular | `.ds-text-caption-l-12-normal-regular` | `400 12px/16px "Roboto"` | 0.5px | none |
| Caption L (12) / Normal / Medium | `.ds-text-caption-l-12-normal-medium` | `500 12px/16px "Roboto"` | 0.5px | none |
| Caption L (12) / Caps / Regular | `.ds-text-caption-l-12-caps-regular` | `400 12px/16px "Roboto"` | 0.5px | uppercase |
| Caption L (12) / Caps / Medium | `.ds-text-caption-l-12-caps-medium` | `500 12px/16px "Roboto"` | 0.5px | uppercase |
| Caption M (10) / Normal / Regular | `.ds-text-caption-m-10-normal-regular` | `400 10px/12px "Roboto"` | 0.5px | none |
| Caption M (10)/Normal/Medium | `.ds-text-caption-m-10-normal-medium` | `500 10px/12px "Roboto"` | 0.5px | capitalize |
| Caption M (10) / Caps / Regular | `.ds-text-caption-m-10-caps-regular` | `400 10px/12px "Roboto"` | 0.5px | uppercase |
| Caption M (10) / Caps / Medium | `.ds-text-caption-m-10-caps-medium` | `500 10px/12px "Roboto"` | 0.5px | uppercase |
| Caption S (8) / Normal / Regular | `.ds-text-caption-s-8-normal-regular` | `400 8px/10px "Roboto"` | 0.5px | none |
| Caption S (8) / Normal / Medium | `.ds-text-caption-s-8-normal-medium` | `500 8px/10px "Roboto"` | 0.5px | none |
| Caption S (8) / Caps / Regular | `.ds-text-caption-s-8-caps-regular` | `400 8px/10px "Roboto"` | 0.5px | uppercase |
| Caption S (8) / Caps / Medium | `.ds-text-caption-s-8-caps-medium` | `500 8px/10px "Roboto"` | 0.5px | uppercase |

### Эффект-стили ДС (тени как готовые значения)

Ставить `box-shadow: var(--ds-shadow-…)`, не переписывать пиксели.

| Стиль Figma | Токен | Значение box-shadow |
|---|---|---|
| Shadows/None | `--ds-shadow-shadows-none` | `0px 2px 0px 0px #ffffff` |
| Shadows/01 dp Sl | `--ds-shadow-shadows-01-dp-sl` | `0px 0px 4px 0px rgba(33, 33, 33, 0.12), 0px 2px 2px 0px rgba(33, 33, 33, 0.04)` |
| Shadows/08 dp S | `--ds-shadow-shadows-08-dp-s` | `0px 0px 16px 0px rgba(33, 33, 33, 0.12), 0px 4px 6px 0px rgba(33, 33, 33, 0.1)` |
| Shadows/12 dp M | `--ds-shadow-shadows-12-dp-m` | `0px 0px 28px 0px rgba(33, 33, 33, 0.12), 0px 10px 24px 0px rgba(33, 33, 33, 0.12)` |
| Shadows/24 dp XL | `--ds-shadow-shadows-24-dp-xl` | `0px 0px 32px 0px rgba(33, 33, 33, 0.16), 0px 12px 16px 0px rgba(33, 33, 33, 0.16)` |

### Цветовые стили ДС

Цветовые стили Figma. Для компонентов приоритет у компонентных токенов `--ds-color-*`.

| Стиль Figma | Токен | Значение |
|---|---|---|
| Surface / Default | `--ds-paint-surface-default` | #ffffff |
| Surface / Default V2 | `--ds-paint-surface-default-v2` | #f8f9fc |
| Surface / Hover | `--ds-paint-surface-hover` | #f5f5f5 |
| Surface / Selected | `--ds-paint-surface-selected` | #ebebeb |
| Surface / Press | `--ds-paint-surface-press` | #e0e0e0 |
| Surface / Disable | `--ds-paint-surface-disable` | #e0e0e0 |
| Surface/SnackTooltip | `--ds-paint-surface-snacktooltip` | #424242 |
| Surface/Sidebar | `--ds-paint-surface-sidebar` | #f8f9fc |
| Surface/Sidebar_Selected | `--ds-paint-surface-sidebar-selected` | #f0f5ff |
| Surface / Sidebar_Active | `--ds-paint-surface-sidebar-active` | #a8c9ff |
| Table surfase / Default | `--ds-paint-table-surfase-default` | #ffffff |
| Table surfase / Hover | `--ds-paint-table-surfase-hover` | #f5f5f5 |
| Table surfase / Selected | `--ds-paint-table-surfase-selected` | #ebebeb |
| Table surfase / Group | `--ds-paint-table-surfase-group` | #ebebeb |
| Table surfase / Head | `--ds-paint-table-surfase-head` | #f0f5ff |
| Table surfase / Head Group | `--ds-paint-table-surfase-head-group` | #a8c9ff |
| Text/Primary | `--ds-paint-text-primary` | #333333 |
| Text/Inversive | `--ds-paint-text-inversive` | #ffffff |
| Text / Caption | `--ds-paint-text-caption` | #616161 |
| Text / Placeholder | `--ds-paint-text-placeholder` | #d6d6d6 |
| Text / Disable | `--ds-paint-text-disable` | #9e9e9e |
| Text/Accent | `--ds-paint-text-accent` | #448aff |
| Text/Positive | `--ds-paint-text-positive` | #14b456 |
| Text / Warning | `--ds-paint-text-warning` | #ffab40 |
| Text/Negative | `--ds-paint-text-negative` | #ff5252 |
| Button / Neutral / Default | `--ds-paint-button-neutral-default` | #ffffff |
| Button / Neutral / Hover | `--ds-paint-button-neutral-hover` | #f5f5f5 |
| Button / Neutral / Press | `--ds-paint-button-neutral-press` | #ebebeb |
| Button / Neutral / Disable | `--ds-paint-button-neutral-disable` | #ebebeb |
| Button/Accent/Default | `--ds-paint-button-accent-default` | #448aff |
| Button/Accent/Hover | `--ds-paint-button-accent-hover` | #3969d5 |
| Button/Accent/Press | `--ds-paint-button-accent-press` | #2651b5 |
| Button/Positive/Default | `--ds-paint-button-positive-default` | #14b456 |
| Button/Positive/Hover | `--ds-paint-button-positive-hover` | #0f852c |
| Button/Positive/Press | `--ds-paint-button-positive-press` | #0a571a |
| Button/Warning/Default | `--ds-paint-button-warning-default` | #ffab40 |
| Button/Warning/Hover | `--ds-paint-button-warning-hover` | #ea7806 |
| Button/Warning/Press | `--ds-paint-button-warning-press` | #994000 |
| Button/Negative/Default | `--ds-paint-button-negative-default` | #ff5252 |
| Button/Negative/Hover | `--ds-paint-button-negative-hover` | #de1a12 |
| Button/Negative/Press | `--ds-paint-button-negative-press` | #7f0f0a |
| Icon/Primary | `--ds-paint-icon-primary` | #616161 |
| Icon/Inversive | `--ds-paint-icon-inversive` | #ffffff |
| Icon/Disable | `--ds-paint-icon-disable` | #9e9e9e |
| Icon/Accent | `--ds-paint-icon-accent` | #448aff |
| Icon/Positive | `--ds-paint-icon-positive` | #14b456 |
| Icon/Warning | `--ds-paint-icon-warning` | #ea7806 |
| Icon/Negative | `--ds-paint-icon-negative` | #ff5252 |
| Shapes / Default | `--ds-paint-shapes-default` | #ffffff |
| Shapes / SuperLight NT | `--ds-paint-shapes-superlight-nt` | #f5f5f5 |
| Shapes / Lightest NT | `--ds-paint-shapes-lightest-nt` | #ebebeb |
| Shapes / Lighter NT | `--ds-paint-shapes-lighter-nt` | #e0e0e0 |
| Shapes / Lighter PR | `--ds-paint-shapes-lighter-pr` | #f8f9fc |
| Shapes / Lighter SC | `--ds-paint-shapes-lighter-sc` | #ebfbf2 |
| Shapes/Lighter WR | `--ds-paint-shapes-lighter-wr` | #fff9f0 |
| Shapes / Lighter ER | `--ds-paint-shapes-lighter-er` | #fff2f2 |
| Shapes / Lightest MG | `--ds-paint-shapes-lightest-mg` | #fbf7fc |
| Shapes / Lightest BR | `--ds-paint-shapes-lightest-br` | #f7e9e3 |
| Shapes / Lightest DB | `--ds-paint-shapes-lightest-db` | #f9fafb |
| Stroke / Default | `--ds-paint-stroke-default` | #e0e0e0 |
| Stroke / Hover | `--ds-paint-stroke-hover` | #9e9e9e |
| Stroke / Disable | `--ds-paint-stroke-disable` | #ebebeb |
| Stroke / Primary | `--ds-paint-stroke-primary` | #448aff |
| Stroke / Secondary | `--ds-paint-stroke-secondary` | #14b456 |
| Stroke / Warning | `--ds-paint-stroke-warning` | #ffab40 |
| Stroke / Error | `--ds-paint-stroke-error` | #ff5252 |

### Сетка (Grid / Контейнер)

Контент собирается в Контейнер (max-width) с 4 брейкпоинтами. Ширина контейнера и поля (margin) — из Figma _Grids_DS_; отступы между блоками внутри контейнера — из шкалы Space (`--ds-space-*`). Проверять по `border-box`.

| Брейкпоинт | Экран | Контент (Container) | Поля (margin) | gap между блоками |
|---|---|---|---|---|
| Desktop | 1440 | 1176 | 32 + 32 | 24 / 16 / 8 |
| Tablet | 768 | 652 | 32 + 32 | 16 / 8 |
| Phone | 374 | 342 | 16 + 16 | 8 |

**Отступы между блоками/компонентами в контейнере** — только из шкалы Space:
| Токен | Значение | Для чего |
|---|---|---|
| `--ds-space-1x` | 4 | микро-отступ внутри инлайн (иконка·текст) |
| `--ds-space-2x` | 8 | мелкий блок (gap иконки/кнопок, Tab-строки) |
| `--ds-space-3x` | 12 | средний между компонентами в строке |
| `--ds-space-4x` | 16 | средний блок (паддинг контента, gap разделов) |
| `--ds-space-5x` | 20 | крупный внутри секции |
| `--ds-space-6x` | 24 | крупный блок (gap секций контейнера) |
| `--ds-space-7x` | 28 | между крупными секциями |
| `--ds-space-8x` | 32 | поля (margin) контейнера Desktop/Tablet |

`Container` Desktop 1176 ширина + поля 32. На Phone поля сжимаются до 16. Колонки в сетке колоночные не заданы (в Figma `layoutGrids` пуст) — раскладка строится на flex/grid и шкале Space.

## Компоненты

### Каталог компонентов Figma (все 106)

Полный набор компонентов дизайн-системы (сканирование всех страниц файла Figma CJBjyS1OnRXqiOqaXYVCVd, включая неопубликованные и вложенные): свойства, все значения вариантов и токены компонента.

**Всего компонентов: 106**

#### Arrow `[55939:14119]` — 13 вариантов
**Описание и рекомендации по применению:**
Набор стрелок — направление действия и раскрытие: возврат назад, шаг по периоду, сортировка, раскрытие списка.  
Берите стрелку из этого набора, а не рисуйте свою: размер и толщина линий согласованы с иконками ДС.  

Как выбрать вариант: по смыслу действия — назад/вперёд, вверх/вниз, раскрыть, свернуть.
- **Content** (VARIANT): arrow_back, arrow_downward_alt, arrow_drop_down, arrow_drop_up, arrow_forward, arrow_left, arrow_right, arrow_upward_alt, keyboard_arrow_down, keyboard_arrow_left, keyboard_arrow_right, keyboard_arrow_up, unfold_less
- Размеры и параметры:
    - высота: `var(--ds-size-6x)` (фикс.)
    - ширина: `var(--ds-size-6x)` (фикс.)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-arrow">
  <div class="ds-arrow__drop-down"></div>
  <span class="ds-arrow__icon"><!-- иконка: material-icons по имени --></span>
</div>
```

#### Arrow list `[55939:13307]` — 13 вариантов
**Описание и рекомендации по применению:**
Стрелка в пункте списка — показывает, что пункт раскрывается или ведёт внутрь раздела.  
Служебный элемент списка: ставится справа в пункте List item, отдельно на экран не выносится.  

Как выбрать вариант: по смыслу — переход внутрь, раскрытие или свёртывание пункта.
- **Content** (VARIANT): arrow_back, arrow_downward_alt, arrow_drop_down, arrow_drop_up, arrow_forward, arrow_left, arrow_right, arrow_upward_alt, keyboard_arrow_down, keyboard_arrow_left, keyboard_arrow_right, keyboard_arrow_up, unfold_less
- Размеры и параметры:
    - высота: `var(--ds-size-6x)` (фикс.)
    - ширина: `var(--ds-size-6x)` (фикс.)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-arrow-list">
  <div class="ds-arrow-list__drop-down"></div>
  <span class="ds-arrow-list__icon"><!-- иконка: material-icons по имени --></span>
</div>
```

#### Arrow menu `[56090:1628]` — 13 вариантов
**Описание и рекомендации по применению:**
Стрелка в пункте меню — показывает вложенное подменю или направление перехода.  
Служебный элемент меню: ставится справа в пункте Menu item, отдельно на экран не выносится.  

Как выбрать вариант: по смыслу — вложенное подменю, возврат или раскрытие.
- **Content** (VARIANT): arrow_back, arrow_downward_alt, arrow_drop_down, arrow_drop_up, arrow_forward, arrow_left, arrow_right, arrow_upward_alt, keyboard_arrow_down, keyboard_arrow_left, keyboard_arrow_right, keyboard_arrow_up, unfold_less
- Размеры и параметры:
    - высота: `var(--ds-size-6x)` (фикс.)
    - ширина: `var(--ds-size-6x)` (фикс.)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-arrow-menu">
  <div class="ds-arrow-menu__drop-down"></div>
  <span class="ds-arrow-menu__icon"><!-- иконка: material-icons по имени --></span>
</div>
```

#### Arrow select `[57735:17989]` — 13 вариантов
**Описание и рекомендации по применению:**
Стрелка в поле выбора — показывает, что список раскрывается, и его текущее состояние.  
Служебный элемент Select: ставится справа в поле, отдельно на экран не выносится.  

Как выбрать вариант: список закрыт или раскрыт, направление перехода.
- **Content** (VARIANT): arrow_back, arrow_downward_alt, arrow_drop_down, arrow_drop_up, arrow_forward, arrow_left, arrow_right, arrow_upward_alt, keyboard_arrow_down, keyboard_arrow_left, keyboard_arrow_right, keyboard_arrow_up, unfold_less
- Размеры и параметры:
    - высота: `var(--ds-size-6x)` (фикс.)
    - ширина: `var(--ds-size-6x)` (фикс.)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-arrow-select">
  <div class="ds-arrow-select__drop-down"></div>
  <span class="ds-arrow-select__icon"><!-- иконка: material-icons по имени --></span>
</div>
```

#### Autocomplete form `[58107:8230]` — 10 вариантов
**Описание и рекомендации по применению:**
Поле с подсказкой из справочника — ввод с поиском по большому списку: товар, контрагент, сотрудник.  
Берите его, когда вариантов слишком много для обычного списка; подсказки показывайте по мере ввода.  

Как выбрать вариант:  
Variant=Empty — значение не выбрано; Populated — значение выбрано.  
Состояния: Default, Hover, Focus, Focus+Value, Error, Disable.
- **Variant** (VARIANT): Empty, Populated
- **State** (VARIANT): Default, Disable, Error, Focus, Focus+Value, Hover
- Размеры и параметры:
    - высота: минимум `48px`, растёт по контенту
    - ширина: `250px` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--empty`: color `var(--ds-color-form-field-input-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-input-text-color, #9e9e9e)`
    - `--populated`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-label-text-color, #9e9e9e)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-autocomplete-form ds-autocomplete-form--disabled">
  <span class="ds-autocomplete-form__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-autocomplete-form__input"></div>
  <div class="ds-autocomplete-form__input-frame"></div>
  <span class="ds-autocomplete-form__label">Текст</span>
  <span class="ds-autocomplete-form__support">Текст</span>
</div>
```

#### Backdrop `[53623:806]` — 1 вариантов
**Описание и рекомендации по применению:**
Затемнение под диалогом — перекрывает экран, пока открыто модальное окно или панель.  
Берите его вместе с диалогом; клик по затемнению закрывает окно только там, где нет несохранённых данных.
- **Type** (VARIANT): Default
- CSS не требуется: собственного оформления нет — компонент задаёт только структуру/поведение, вид приходит от вложенных элементов.

#### Badge `[54428:187]` — 8 вариантов
**Описание и рекомендации по применению:**
Бейдж — отметка о новом или требующем внимания на элементе: пункте меню, кнопке, вкладке, пункте списка.  
Показывает количество или сам факт события; для метки состояния объекта используйте Status.  

Как выбрать вариант:  
Type=Counter — с числом, когда количество важно; Type=Point — точка, когда важен только факт.  
Style=Accent — обычное новое; Positive — успешно; Warning — требует внимания; Negative — ошибка или просрочено.  

Число не выдумывайте: бейдж показывает реальное количество, при большом значении — сокращение вида «99+».
- **Style** (VARIANT): Accent, Negative, Positive, Warning
- **Type** (VARIANT): Counter, Point
- CSS: выверено вручную, см. `components/Badge_DS/badge.css`

#### Banners `[54367:2566]` — 12 вариантов
**Описание и рекомендации по применению:**
Баннер — контекстное сообщение на странице: подсказка, предупреждение, ошибка, подтверждение.  
Показывайте поверх контента вверху страницы или блока, когда нужно привлечь внимание к событию.  

Как выбрать вариант:  
Neutral — нейтральное сообщение, без эмоциональной окраски.  
Accent — информационное или рекламное сообщение.  
Positive — успех, подтверждение.  
Warning — событие требует внимания, но не критично.  
Negative — ошибка или блокирующее событие: «Счёт не оплачен».  
Tip — подсказка с пунктирной обводкой, совет по продукту.  

Orientation=Horizontal — иконка, текст и кнопки в одну строку. Vertical — иконка и текст сверху, кнопки снизу.  
Состав настраивается внутри: Element left (иконка), Buttons, Close (крестик).  
Фронт: https://frontend-common.iiko.ru/components/banners
- **Style** (VARIANT): Accent, Negative, Neutral, Positive, Tip, Warning
- **Orientation** (VARIANT): Horizontal, Vertical
- Прочие свойства: Element left#18321:0 (BOOLEAN), Buttons#54443:2 (BOOLEAN), Close#54443:4 (BOOLEAN)
- CSS: выверено вручную, см. `components/index.css`

#### Button `[17022:63091]` — 153 вариантов
**Описание и рекомендации по применению:**
Кнопка действия. Используйте для основного действия на экране.  
Одна акцентная кнопка на область. Кнопки только с иконкой — это Button icon; группы — Button group.  

Состав: текст + иконка (слева или справа), можно без иконки.  
Варианты:  
Accent Filled — основная.  
Neutral Outlined — второстепенная.  
Neutral Text — третьестепенная.  
Positive / Negative — успех / ошибка.  

Размеры: M (36px), S (28px), XS (24px).  
Состояния: default, hover, pressed, disabled, loading.  
Фронт: \<button restoButton\> — https://frontend-common.iiko.ru/components/button
- **Size** (VARIANT): M, S, XS
- **Style** (VARIANT): Accent, Disable, Negative, Neutral, Positive, Warning
- **Type** (VARIANT): Filled, Outlined, Text
- **State** (VARIANT): Default, Disable, Hover, Loading, Press
- Прочие свойства: Element left#17025:2 (BOOLEAN), Element right#17025:123 (BOOLEAN), Button text#17039:607 (TEXT), Text#17053:733 (BOOLEAN)
- CSS: выверено вручную, см. `components/Button_DS/button.css`

#### Button group `[53619:15772]` — 4 вариантов
**Описание и рекомендации по применению:**
Группа кнопок — несколько действий рядом с единым выравниванием и отступами: подвал диалога, шапка блока, панель над таблицей.  
Порядок слева направо: сначала второстепенные действия, главное — последним справа. Больше трёх кнопок в группу не ставьте, лишнее уводите в меню.  

Как выбрать вариант:  
Orientation=Horizontally — в строку, основной случай; Vertically — в столбец, для узких блоков и мобильных экранов.  
Margins=On — с внешними отступами группы; Off — без них, когда отступы задаёт контейнер.
- **Orientation** (VARIANT): Horizontally, Vertically
- **Margins** (VARIANT): Off, On
- Прочие свойства: Slot#60175:12 (SLOT)
- CSS: выверено вручную, см. `components/Button_DS/button.css`

#### Button icon `[17123:81299]` — 153 вариантов
**Описание и рекомендации по применению:**
Кнопка-иконка — действие без подписи, когда смысл понятен по иконке и место ограничено: строки таблиц, шапки блоков, панели инструментов.  
Всегда добавляйте тултип с названием действия; если действие важное или неочевидное — берите обычную кнопку с текстом (Button).  

Как выбрать вариант:  
Style=Neutral — обычное действие; Accent — акцентное; Positive — подтверждение; Warning — действие с последствиями; Negative — удаление и необратимое.  
Type=Filled — заметная; Outlined — второй план; Text — в таблицах и шапках, не перетягивает внимание.  
Size=M — основной; S — панели и плотные блоки; XS — строки таблиц и ячейки.  

Состояния: Default, Hover, Press, Disable, Loading.
- **Size** (VARIANT): M, S, XS
- **Style** (VARIANT): Accent, Negative, Neutral, Positive, Warning
- **Type** (VARIANT): Filled, Outlined, Text
- **State** (VARIANT): Default, Disable, Hover, Loading, Press
- CSS: выверено вручную, см. `components/Button-Icon_DS/button-icon.css`

#### Button icon group `[53828:5738]` — 2 вариантов
**Описание и рекомендации по применению:**
Группа кнопок-иконок — набор действий одной иконкой рядом: панель инструментов, действия в строке таблицы, шапка карточки.  
Всем кнопкам в группе давайте тултипы; разнородные действия не смешивайте в одну группу.  

Как выбрать вариант: Horizontally — в строку (основной случай), Vertically — в столбец для узких панелей.
- **Orientation** (VARIANT): Horizontally, Vertically
- Прочие свойства: Slot#60176:0 (SLOT)
- CSS: выверено вручную, см. `components/Button-Icon_DS/button-icon.css`

#### Button toggle `[17039:71554]` — 12 вариантов
**Описание и рекомендации по применению:**
Кнопка-переключатель — кнопка с состоянием «нажата / не нажата»: режим отображения, фильтр, форматирование.  
Собирается в группы (Toggle buttons); для обычных действий берите Button, для действия одной иконкой — Button icon.  

Как выбрать вариант:  
Type=Filled — активный, выбранный переключатель; Type=Outlined — невыбранный.  
Content=Icon / Text — только иконка (режим понятен по иконке) / с текстом.  
Size=M, S, XS — по плотности интерфейса: M в формах, S и XS в таблицах и панелях.
- **Size** (VARIANT): M, S, XS
- **Type** (VARIANT): Filled, Outlined
- **Content** (VARIANT): Icon, Text
- Прочие свойства: Button container#59885:13 (SLOT)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-button-toggle-pad-top, 4px) var(--ds-button-toggle-pad-right, 4px) var(--ds-button-toggle-pad-bottom, 4px) var(--ds-button-toggle-pad-left, 4px)`
    - промежуток между элементами: `var(--ds-button-toggle-gap, 4px)`
    - скругление: `var(--ds-button-toggle-border-radius, 12px)`
- Модификаторы (что меняет каждый):
    - `--filled`: фон `var(--ds-color-button-toggle-filled-background, #ffffff)`, color `var(--ds-color-button-accent-outlined-default-text-color, #448aff)`, рамка `none`, тень `none`
    - `--outlined`: фон `var(--ds-color-button-toggle-outlined-background, #ffffff)`, рамка `1px solid var(--ds-color-button-toggle-outlined-border-color, #e0e0e0)`, color `var(--ds-color-button-accent-filled-default-text-color, #ffffff)`, тень `none`
    - `--s`: ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
    - `--xs`: ширина `var(--ds-size-4x)`, высота `var(--ds-size-4x)`
- Разметка:

```html
<div class="ds-button-toggle ds-button-toggle--filled">
  <span class="ds-button-toggle__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-button-toggle__label">Текст</span>
</div>
```

#### Card content `[53744:3079]` — 2 вариантов
**Описание и рекомендации по применению:**
Содержимое карточки — область с текстом, значениями или своим набором элементов.  
Как выбрать вариант: готовая раскладка или собственное содержимое.
- **Content** (VARIANT): Custom, Default
- Прочие свойства: Title#56245:7 (BOOLEAN), Content#58799:0 (SLOT)
- CSS: выверено вручную, см. `components/Card_DS/card-view.css`

#### Card footer `[53744:3139]` — 1 вариантов
**Описание и рекомендации по применению:**
Подвал карточки — кнопки или дополнительная информация под содержимым.  
Добавляйте его только если действия действительно есть — иначе карточка обходится без подвала.
- **Content** (VARIANT): Default
- Прочие свойства: Divider#53753:1 (BOOLEAN)
- CSS: выверено вручную, см. `components/Card_DS/card-view.css`

#### Card header `[52916:15126]` — 1 вариантов
**Описание и рекомендации по применению:**
Шапка карточки — заголовок, подзаголовок и действия карточки.  
Действия ставьте справа кнопкой-иконкой; заголовок не дублируйте в содержимом.
- **Content** (VARIANT): Default
- Прочие свойства: Divider#53766:0 (BOOLEAN), Title#56245:0 (BOOLEAN), Label up#56245:1 (BOOLEAN), Label down#56245:2 (BOOLEAN)
- CSS: выверено вручную, см. `components/Card_DS/card-view.css`

#### Card view `[53744:3181]` — 3 вариантов
**Описание и рекомендации по применению:**
Карточка целиком — блок с самостоятельным содержимым: карточка новости на главной iikoWeb, инвойс в E-invoice, карта гостя, адрес в колл-центре.  
Собирается из шапки (Card header), содержимого (Card content) и подвала (Card footer) — лишние части не добавляйте, если их нет на экране.  

Как выбрать вариант:  
Type=Filled — с заливкой, для плиток и списков карточек.  
Type=Outlined — с рамкой, когда карточек много и фон один.  
Type=Shadow — с тенью, когда карточка отделена от фона или кликабельна.
- **Type** (VARIANT): Filled, Outlined, Shadow
- Прочие свойства: Shadow#53237:9 (BOOLEAN)
- CSS: выверено вручную, см. `components/Card_DS/card-view.css`

#### Checkbox `[53806:5694]` — 21 вариантов
**Описание и рекомендации по применению:**
Чекбокс — выбор нескольких независимых пунктов или включение отдельной настройки.  
Используйте, когда пунктов несколько и можно выбрать любое их число; если выбор строго один — берите Radio button, если это переключатель режима «вкл/выкл» — Slide toggle.  

Состав: квадратный индикатор без подписи. С подписью и support-текстом — Checkbox label; для набора пунктов с общим заголовком — Checkbox group.  

Как выбрать вариант:  
Type=Deselected / Selected — пункт не выбран / выбран.  
Type=Indeterminate — часть вложенных пунктов выбрана (родительский пункт списка).  
Variant=Normal / Error / Disable — обычный, с ошибкой (в группе не выбран обязательный пункт), недоступный.  

Состояния: Default, Hover, Press.
- **Variant** (VARIANT): Disable, Error, Normal
- **Type** (VARIANT): Deselected, Indeterminate, Selected
- **State** (VARIANT): Default, Hover, Press
- CSS: выверено вручную, см. `components/index.css`

#### Checkbox group `[53810:889]` — 3 вариантов
**Описание и рекомендации по применению:**
Группа чекбоксов — набор пунктов выбора с общим заголовком и общим support-текстом или текстом ошибки.  
Используйте, когда пункты относятся к одному вопросу: «Товары и склад» с подсказкой «Выберите один вариант (обязательно)».  

Состав: заголовок группы (Support up), пункты Checkbox label, общий текст под группой (Support down) — в ошибке он становится текстом ошибки для всей группы.  

Как выбрать вариант:  
Orientation=Vertical — пункты в столбец, основной случай.  
Orientation=Horizontal — в строку, когда пунктов мало и они короткие.  
Orientation=Group — вложенная группа: родительский пункт и подчинённые под ним.
- **Orientation** (VARIANT): Group, Horizontal, Vertical
- Прочие свойства: Slot vertical#57252:0 (SLOT), Slot group#57252:4 (SLOT), Slot horizontal#57252:8 (SLOT), Support up#58195:66 (BOOLEAN), Support down#58195:70 (BOOLEAN)
- CSS: выверено вручную, см. `components/index.css`

#### Checkbox label `[53810:880]` — 9 вариантов
**Описание и рекомендации по применению:**
Чекбокс с подписью — основной способ показать пункт выбора: индикатор + текст, при необходимости support-текст под подписью.  
Используйте в настройках и формах: «Фасовки у товаров», «Добавлять товары, которых не было в заказе».  

Состав: чекбокс слева или справа от подписи (Checkbox left / Checkbox right), Label, Support text.  
Кликабельна вся строка вместе с подписью — не ставьте отдельный текст рядом с чекбоксом.  

Как выбрать вариант:  
Type=Deselected / Selected / Inderterminate — не выбран / выбран / частичный выбор.  
Variant=Normal / Error / Disable — обычный, с ошибкой (support-текст становится текстом ошибки), недоступный.
- **Variant** (VARIANT): Disable, Error, Normal
- **Type** (VARIANT): Deselected, Inderterminate, Selected
- Прочие свойства: Checkbox left#17172:1340 (BOOLEAN), Checkbox right#17172:1349 (BOOLEAN), Label#54065:0 (BOOLEAN), Support text#58192:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-5x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-checkbox-label-gap-support, 4px)`
- Модификаторы (что меняет каждый):
    - `--disable`: color `var(--ds-color-checkbox-label-text-disable-color, #9e9e9e)`
    - `--error`: color `var(--ds-color-checkbox-label-text-color, #333333)`
    - `--normal`: color `var(--ds-color-checkbox-label-text-color, #333333)`
- Разметка:

```html
<div class="ds-checkbox-label ds-checkbox-label--disable">
  <div class="ds-checkbox-label__form"></div>
  <span class="ds-checkbox-label__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-checkbox-label__label">Текст</span>
  <div class="ds-checkbox-label__left"></div>
  <div class="ds-checkbox-label__right"></div>
  <span class="ds-checkbox-label__support">Текст</span>
  <div class="ds-checkbox-label__support-text"></div>
</div>
```

#### Chips `[17168:83542]` — 18 вариантов
**Описание и рекомендации по применению:**
Чип — компактная метка-фильтр или выбранное значение, которое можно снять: применённые фильтры над таблицей, выбранные товары, теги.  
Чип всегда относится к чему-то выбранному пользователем; для статуса объекта берите Status, для количества — Badge.  

Состав: текст, элемент слева (иконка или аватар) и элемент справа (крестик для снятия).  

Как выбрать вариант:  
Type=Filled — выбранный, активный чип; Outlined — доступный к выбору.  
Size=M — основной; S — плотные панели и строки таблиц.  
Состояния: Default, Hover, Focus, Press, Disable.
- **Size** (VARIANT): M, S
- **Type** (VARIANT): Filled, Outlined
- **State** (VARIANT): Default, Disable, Focus, Hover, Press
- Прочие свойства: Element left#17172:1340 (BOOLEAN), Element right#17172:1349 (BOOLEAN)
- Размеры и параметры:
    - высота: `var(--ds-size-8x)` (фикс.)
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-chips-m-size-pad-top, 6px) var(--ds-chips-m-size-pad-right, 8px) var(--ds-chips-m-size-pad-bottom, 6px) var(--ds-chips-m-size-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-chips-m-size-gap, 8px)`
    - скругление: `var(--ds-chips-m-size-border-radius, 12px)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--filled`: фон `var(--ds-color-chips-filled-default-background, #f8f9fc)`, color `var(--ds-color-chips-text-color, #333333)`, фон `var(--ds-color-chips-disable-background-filled, #ebebeb)`, color `var(--ds-color-chips-disable-text-color, #9e9e9e)`
    - `--outlined`: фон `var(--ds-color-chips-outlined-default-background, #ffffff)`, рамка `1px solid var(--ds-color-chips-outlined-default-border-color, #e0e0e0)`, color `var(--ds-color-chips-text-color, #333333)`, фон `var(--ds-color-chips-disable-background-outlined, #ffffff)`
    - `--s`: промежуток между элементами `var(--ds-chips-s-size-gap, 4px)`, внутренние отступы `var(--ds-chips-s-size-pad-top, 4px) var(--ds-chips-s-size-pad-right, 6px) var(--ds-chips-s-size-pad-bottom, 4px) var(--ds-chips-s-size-pad-left, 6px)`, скругление `var(--ds-chips-s-size-border-radius, 8px)`, ширина `var(--ds-size-4x)`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-chips ds-chips--disabled">
  <div class="ds-chips__add"></div>
  <div class="ds-chips__chip-container"></div>
  <div class="ds-chips__chip-text"></div>
  <div class="ds-chips__close"></div>
  <span class="ds-chips__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-chips__icon-size"></div>
  <span class="ds-chips__label">Текст</span>
</div>
```

#### Chips group `[55750:5485]` — 2 вариантов
**Описание и рекомендации по применению:**
Группа чипов — набор фильтров или выбранных значений в один ряд с переносом на новую строку.  
Берите группу, чтобы зазоры и перенос были одинаковыми; при большом числе чипов сворачивайте лишние в «ещё N».  

Как выбрать вариант: по размеру чипов в группе.
- **Size** (VARIANT): M, S
- Прочие свойства: Slot#60220:1 (SLOT)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-chips-gap-group, 8px)`
- Модификаторы (что меняет каждый):
    - `--s`: ширина `var(--ds-size-4x)`, высота `var(--ds-size-4x)`
- Разметка:

```html
<div class="ds-chips-group ds-chips-group--s">
  <span class="ds-chips-group__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-chips-group__label">Текст</span>
</div>
```

#### Chips Input `[52916:14622]` — 16 вариантов
**Описание и рекомендации по применению:**
Поле ввода тегов — несколько значений в одном поле, каждое становится чипом: список товаров, получатели, метки.  
Берите его, когда значений несколько и их набирают вручную; для одного значения из справочника — Autocomplete, для выбора из списка — Select.  

Как выбрать вариант:  
Size=M — основной; S — плотные формы и панели.  
Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **Size** (VARIANT): M, S
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Прочие свойства: Support text#55693:0 (BOOLEAN), Element right#55751:38 (BOOLEAN), Support#59392:7 (BOOLEAN), Hint text#59430:0 (BOOLEAN), Label text value#59432:1 (TEXT), Support text value#59437:20 (TEXT), Hint text value#59437:40 (TEXT), Action text#59437:60 (BOOLEAN), Action text value#59437:80 (TEXT), Placeholder value#59507:0 (TEXT), Text value#59507:16 (TEXT), Slot#60231:21 (SLOT)
- Размеры и параметры:
    - ширина: `280px` (фикс.)
    - промежуток между элементами: `var(--ds-size-1x)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--s`: промежуток между элементами `var(--ds-form-field-gap-input-support, 4px)`, ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-chips-input ds-chips-input--disabled">
  <div class="ds-chips-input__content"></div>
  <div class="ds-chips-input__frame"></div>
  <span class="ds-chips-input__hint">Текст</span>
  <span class="ds-chips-input__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-chips-input__label">Текст</span>
  <span class="ds-chips-input__support">Текст</span>
  <span class="ds-chips-input__text">Текст</span>
</div>
```

#### Chips Input `[61382:55775]` — 16 вариантов
_Описание компонента в Figma отсутствует._
- **Size** (VARIANT): M, S
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Прочие свойства: Support text#55693:0 (BOOLEAN), Element right#55751:38 (BOOLEAN), Support#59392:7 (BOOLEAN), Hint text#59430:0 (BOOLEAN), Label text value#59432:1 (TEXT), Support text value#59437:20 (TEXT), Hint text value#59437:40 (TEXT), Action text#59437:60 (BOOLEAN), Action text value#59437:80 (TEXT), Placeholder value#59507:0 (TEXT), Text value#59507:16 (TEXT), Slot#60231:21 (SLOT)
- Размеры и параметры:
    - ширина: `280px` (фикс.)
    - промежуток между элементами: `var(--ds-form-field-gap-input-support, 4px)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--s`: ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-chips-input-2 ds-chips-input-2--disabled">
  <div class="ds-chips-input-2__content"></div>
  <div class="ds-chips-input-2__frame"></div>
  <span class="ds-chips-input-2__hint">Текст</span>
  <span class="ds-chips-input-2__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-chips-input-2__label">Текст</span>
  <span class="ds-chips-input-2__support">Текст</span>
  <span class="ds-chips-input-2__text">Текст</span>
</div>
```

#### Chips input cell `[60231:75648]` — 8 вариантов
**Описание и рекомендации по применению:**
Ввод тегов внутри ячейки таблицы — несколько значений прямо в строке: комплектующие, метки, склады.  
Используйте в редактируемых таблицах; вне таблицы берите Chips Input.  

Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Размеры и параметры:
    - высота: минимум `var(--ds-size-10x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-table-cell-pad-top, 8px) var(--ds-table-cell-pad-right, 8px) var(--ds-table-cell-pad-bottom, 8px) var(--ds-table-cell-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-size-2x)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-chips-input-cell ds-chips-input-cell--disabled">
  <div class="ds-chips-input-cell__frame"></div>
  <span class="ds-chips-input-cell__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-chips-input-cell__label">Текст</span>
  <span class="ds-chips-input-cell__support">Текст</span>
</div>
```

#### Control arrow button `[52868:3935]` — 3 вариантов
**Описание и рекомендации по применению:**
Кнопка-стрелка — шаг по списку или календарю: предыдущий и следующий месяц, прокрутка вкладок, перелистывание.  
Используйте парой (назад и вперёд); когда шаг недоступен — блокируйте кнопку, а не убирайте её.  

Как выбрать вариант: по размеру блока, в котором стоит кнопка.
- **Size** (VARIANT): M, S, XS
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-0-5x)`
- Модификаторы (что меняет каждый):
    - `--s`: ширина `var(--ds-size-3x)`, высота `var(--ds-size-3x)`
- Разметка:

```html
<div class="ds-control-arrow-button ds-control-arrow-button--s">
  <span class="ds-control-arrow-button__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-control-arrow-button__icon-size"></div>
</div>
```

#### Control Panel `[58501:4052]` — 3 вариантов
**Описание и рекомендации по применению:**
Панель управления календарём — переключение месяца и года, строка дней недели над сеткой.  
Служебный компонент календаря: используется внутри Datepicker.  

Как выбрать вариант: панель переключения периода, строка дней недели или заголовок сетки.
- **Type** (VARIANT): Calendar, Control, Week
- Прочие свойства: Slot Week#58546:5 (SLOT)
- Размеры и параметры:
    - ширина: `280px` (фикс.)
    - внутренние отступы: `var(--ds-size-1x) 0 var(--ds-size-1x) 0`
    - промежуток между элементами: `74px`
- Модификаторы (что меняет каждый):
    - `--calendar`: ширина `fit-content`, направление `column`, align-items `center`, фон `#ffffff`
    - `--control`: направление `row`, align-items `center`, color `var(--ds-color-text-primary, #333333)`
    - `--week`: ширина `fit-content`, направление `row`, внутренние отступы `var(--ds-size-0-5x) 0 var(--ds-size-0-5x) 0`, color `var(--ds-color-text-primary, #333333)`
- Разметка:

```html
<div class="ds-control-panel ds-control-panel--calendar">
  <div class="ds-control-panel__button-icon"></div>
  <div class="ds-control-panel__button-icon-group"></div>
  <div class="ds-control-panel__elements"></div>
  <span class="ds-control-panel__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-control-panel__label">Текст</span>
  <div class="ds-control-panel__month"></div>
</div>
```

#### Control Panel `[58982:11018]` — 2 вариантов
**Описание и рекомендации по применению:**
Панель управления выбором времени — заголовок и переключение между часами и минутами.  
Служебный компонент выбора времени: используется внутри Timepicker.  

Как выбрать вариант: панель переключения или строка со значением времени.
- **Type** (VARIANT): Control, Time
- Прочие свойства: Slot Time#58546:5 (SLOT)
- Размеры и параметры:
    - ширина: `280px` (фикс.)
    - внутренние отступы: `var(--ds-size-1x) 0 var(--ds-size-1x) 0`
    - промежуток между элементами: `74px`
- Модификаторы (что меняет каждый):
    - `--control`: align-items `center`, color `var(--ds-color-text-primary, #333333)`
    - `--time`: ширина `fit-content`, внутренние отступы `var(--ds-size-0-5x) 0 var(--ds-size-0-5x) 0`, color `var(--ds-color-text-primary, #333333)`
- Разметка:

```html
<div class="ds-control-panel-2 ds-control-panel-2--control">
  <div class="ds-control-panel-2__button-icon-group"></div>
  <div class="ds-control-panel-2__elements"></div>
  <span class="ds-control-panel-2__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-control-panel-2__label">Текст</span>
  <div class="ds-control-panel-2__month"></div>
</div>
```

#### Datepicker `[58509:5439]` — 3 вариантов
**Описание и рекомендации по применению:**
Календарь — выбор даты или периода: дата поставки, период отчёта, срок.  
Открывается из поля даты (Input Datepicker); отдельно на экране не живёт.  

Как выбрать вариант:  
Type=Day — сетка дней месяца, основной вид.  
Type=Month — выбор месяца.  
Type=Year — выбор года.
- **Type** (VARIANT): Day, Month, Year
- Прочие свойства: Headline#53001:0 (TEXT), Supporting text#53001:4 (TEXT), Supporting text (range)#53001:8 (TEXT), Headline (range)#53001:12 (TEXT), Show clear button#54584:0 (BOOLEAN), show controls#58548:10 (BOOLEAN)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-size-2x) var(--ds-size-4x) var(--ds-size-2x) var(--ds-size-4x)`
    - скругление: `var(--ds-size-3x)`
    - рамка: `1px solid var(--ds-color-stroke-default, #e0e0e0)`
- Модификаторы (что меняет каждый):
    - `--day`: color `var(--ds-color-text-primary, #333333)`
    - `--month`: color `var(--ds-color-text-primary, #333333)`
    - `--year`: color `var(--ds-color-text-primary, #333333)`
- Разметка:

```html
<div class="ds-datepicker ds-datepicker--day">
  <div class="ds-datepicker__button-icon-group"></div>
  <div class="ds-datepicker__control-panel"></div>
  <div class="ds-datepicker__divider"></div>
  <div class="ds-datepicker__elements"></div>
  <span class="ds-datepicker__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-datepicker__label">Текст</span>
  <div class="ds-datepicker__week-6"></div>
</div>
```

#### Dialog content `[53535:1369]` — 1 вариантов
**Описание и рекомендации по применению:**
Содержимое диалога — область под шапкой: текст, форма, таблица.  
При длинном содержимом прокручивается именно эта область, шапка и подвал остаются на месте.
- **State** (VARIANT): Default
- Прочие свойства: Slot#58937:21 (SLOT), Scroll#58937:24 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `204px`, растёт по контенту
    - ширина: `500px` (фикс.)
    - фон: `var(--ds-color-dialog-background, #ffffff)`
- Разметка:

```html
<div class="ds-dialog-content">
  <div class="ds-dialog-content__background"></div>
  <span class="ds-dialog-content__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-dialog-content__label">Текст</span>
  <div class="ds-dialog-content__scroll"></div>
</div>
```

#### Dialog footer `[53749:638]` — 1 вариантов
**Описание и рекомендации по применению:**
Подвал диалога — кнопки действий окна: главное действие справа, отмена слева от него.  
Главное действие называйте по смыслу («Создать», «Сохранить»), а не «ОК».
- **State** (VARIANT): Default
- Прочие свойства: Divider#53749:3 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `69px`, растёт по контенту
    - ширина: `501px` (фикс.)
    - фон: `var(--ds-color-dialog-background, #ffffff)`
- Разметка:

```html
<div class="ds-dialog-footer">
  <div class="ds-dialog-footer__action"></div>
  <div class="ds-dialog-footer__button"></div>
  <div class="ds-dialog-footer__divider"></div>
  <span class="ds-dialog-footer__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-dialog-footer__label">Текст</span>
</div>
```

#### Dialog header `[53535:1322]` — 2 вариантов
**Описание и рекомендации по применению:**
Шапка диалога — заголовок окна и кнопка закрытия, при необходимости картинка над заголовком.  
Заголовок формулируйте по задаче окна («Создание накладной»), а не «Внимание».  

Как выбрать вариант: только текст или с картинкой сверху.
- **Type** (VARIANT): Picture, Text
- Прочие свойства: Divider#53619:9 (BOOLEAN), Close#59197:0 (BOOLEAN), Picture#59215:10 (SLOT), Description#59215:16 (BOOLEAN)
- Размеры и параметры:
    - ширина: `500px` (фикс.)
    - фон: `var(--ds-color-dialog-background, #ffffff)`
- Модификаторы (что меняет каждый):
    - `--text`: color `var(--ds-color-dialog-header-title-color, #333333)`
- Разметка:

```html
<div class="ds-dialog-header ds-dialog-header--text">
  <div class="ds-dialog-header__description"></div>
  <div class="ds-dialog-header__divider"></div>
  <span class="ds-dialog-header__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-dialog-header__label">Текст</span>
  <div class="ds-dialog-header__title-container"></div>
</div>
```

#### Dialog view `[52952:1285]` — 1 вариантов
**Описание и рекомендации по применению:**
Диалог целиком — модальное окно поверх экрана: подтверждение, форма создания, просмотр записи.  
Берите его как основу окна: шапка (Dialog header), содержимое (Dialog content), подвал с кнопками (Dialog footer), затемнение под окном (Backdrop).  
Закрытие — крестик в шапке и кнопка в подвале; не оставляйте окно без явного способа закрыть.
- **State** (VARIANT): Default
- Прочие свойства: Content#58947:4 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `364px`, растёт по контенту
    - ширина: `500px` (фикс.)
    - скругление: `var(--ds-dialog-border-radius, 12px)`
    - фон: `var(--ds-color-dialog-background, #ffffff)`
    - тень: `var(--ds-shadow-shadows-12-dp-m)`
- Разметка:

```html
<div class="ds-dialog-view">
  <div class="ds-dialog-view__action"></div>
  <div class="ds-dialog-view__content"></div>
  <div class="ds-dialog-view__divider"></div>
  <div class="ds-dialog-view__footer"></div>
  <div class="ds-dialog-view__header"></div>
  <span class="ds-dialog-view__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-dialog-view__label">Текст</span>
  <div class="ds-dialog-view__scroll"></div>
</div>
```

#### Divider `[58320:441]` — 16 вариантов
**Описание и рекомендации по применению:**
Разделитель с состояниями — линия между блоками, которую можно перетаскивать: граница колонок таблицы, граница панелей.  
Лежит на странице UI components (раздел «не готовы или под вопросом») — перед использованием уточните актуальность у владельца ДС. Обычная линия-разделитель — компонент Divider со страницы Divider.  

Как выбрать вариант:  
Type=Solid — сплошная; Dashed — пунктирная (граница, которую можно двигать).  
Size=M, L — по длине и толщине линии.  
Состояния: Lite, Default, Hover, Selected, Disable.
- **Size** (VARIANT): L, M
- **Type** (VARIANT): Dashed, Solid
- **State** (VARIANT): Default, Disable, Hover, Lite, Selected
- CSS: выверено вручную, см. `components/index.css`

#### Divider `[53556:7964]` — 1 вариантов
**Описание и рекомендации по применению:**
Разделитель — тонкая линия между блоками или пунктами списка.  
Берите его вместо рамки, когда нужно только разделить содержимое; не ставьте разделители там, где хватает отступа.
- **Type** (VARIANT): Solid
- CSS: выверено вручную, см. `components/index.css`

#### Element `[54104:20956]` — 9 вариантов
**Описание и рекомендации по применению:**
Слот элемента в пункте списка — выбирает, что стоит слева или справа от текста пункта: иконка, картинка, чекбокс, переключатель, счётчик.  
Служебный компонент списка: подставляется в List item, отдельно на экран не ставится.  

Как выбрать вариант: по тому, что показывает пункт.
- **Content** (VARIANT): Checkbox, Counter, Icon group, Icon size, Image size, Indicator, Radio button, Slide toggle, Text default
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--checkbox`: направление `row`
    - `--counter`: направление `column`, color `var(--ds-color-badge-text-color, #ffffff)`
    - `--icon-group`: направление `row`, align-items `center`
    - `--icon-size`: направление `row`, align-items `center`
    - `--image-size`: направление `row`, align-items `center`
    - `--indicator`: ширина `var(--ds-size-6x)`, направление `row`
    - `--radio-button`: направление `row`
    - `--slide-toggle`: направление `row`, color `var(--ds-color-slide-toggle-text-color, #333333)`
    - `--text-default`: направление `row`, color `var(--ds-color-brand-neutral-super-dark, #333333)`
- Разметка:

```html
<div class="ds-element ds-element--checkbox">
  <span class="ds-element__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element__image-size"></div>
  <span class="ds-element__label">Текст</span>
</div>
```

#### Element cell `[58885:32432]` — 11 вариантов
**Описание и рекомендации по применению:**
Слот содержимого ячейки таблицы — выбирает, что стоит внутри ячейки: текст, иконка, кнопка, статус, поле ввода.  
Служебный компонент таблицы: подставляется в ячейку, отдельно на экран не ставится.  

Как выбрать вариант: по тому, что показывает ячейка.
- **Variant** (VARIANT): Button, Button icon, Cell Input, Checkbox, Chips, Icon group, Icon size, Input number, Slide toggle, Status, Text UI
- CSS не требуется: это **слот-контейнер** — пустая обёртка под вложенный компонент (иконку, ячейку). Оформление задаёт вложенный компонент, а размер — контент.

#### Element Form Field `[60231:76795]` — 3 вариантов
**Описание и рекомендации по применению:**
Слот поля внутри ячейки таблицы — выбирает, какое именно поле ввода стоит в редактируемой ячейке.  
Служебный компонент таблицы: подставляется внутрь ячейки, отдельно на экран не ставится.  

Как выбрать вариант: по типу значения в ячейке — обычный ввод, выбор из списка или ввод тегов.
- **Variant** (VARIANT): Chips input cell, Input cell, Select cell
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--chips-input-cell`: color `#616161`
    - `--input-cell`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`
    - `--select-cell`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`
- Разметка:

```html
<div class="ds-element-form-field ds-element-form-field--chips-input-cell">
  <div class="ds-element-form-field__input"></div>
  <div class="ds-element-form-field__input-cell"></div>
  <span class="ds-element-form-field__label">Текст</span>
</div>
```

#### Element left `[59851:11313]` — 5 вариантов
**Описание и рекомендации по применению:**
Иконка слева во всплывающем сообщении — показывает характер сообщения.  
Служебный элемент Snackbar: цвет выбирайте по смыслу сообщения, отдельно на экран не ставится.
- **Style** (VARIANT): Accent, Negative, Neutral, Positive, Warning
- Размеры и параметры:
    - высота: минимум `var(--ds-size-5x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
- Разметка:

```html
<div class="ds-element-left">
  <span class="ds-element-left__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element-left__info"></div>
</div>
```

#### Element menu `[56090:1611]` — 8 вариантов
**Описание и рекомендации по применению:**
Слот элемента в пункте меню — выбирает, что стоит рядом с названием пункта: иконка, картинка, чекбокс, переключатель, счётчик.  
Служебный компонент меню: подставляется в Menu item, отдельно на экран не ставится.  

Как выбрать вариант: по тому, что показывает пункт меню.
- **Content** (VARIANT): Checkbox, Counter, Icon size, Image size, Indicator, Radio button, Slide toggle, Text default
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--checkbox`: направление `row`
    - `--counter`: направление `column`, color `var(--ds-color-badge-text-color, #ffffff)`
    - `--icon-size`: направление `row`, align-items `center`
    - `--image-size`: направление `row`, align-items `center`
    - `--indicator`: ширина `var(--ds-size-6x)`, направление `row`
    - `--radio-button`: направление `row`
    - `--slide-toggle`: направление `row`, color `var(--ds-color-slide-toggle-text-color, #333333)`
    - `--text-default`: направление `row`, color `var(--ds-color-brand-neutral-super-dark, #333333)`
- Разметка:

```html
<div class="ds-element-menu ds-element-menu--checkbox">
  <span class="ds-element-menu__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element-menu__image-size"></div>
  <span class="ds-element-menu__label">Текст</span>
</div>
```

#### Element select `[57735:17972]` — 8 вариантов
**Описание и рекомендации по применению:**
Слот элемента в пункте списка выбора — выбирает, что стоит рядом со значением: иконка, картинка, чекбокс, переключатель, счётчик.  
Служебный компонент Select: подставляется в Select item, отдельно на экран не ставится.  

Как выбрать вариант: по тому, что показывает пункт списка выбора.
- **Content** (VARIANT): Checkbox, Counter, Icon size, Image size, Indicator, Radio button, Slide toggle, Text default
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--checkbox`: направление `row`
    - `--counter`: направление `column`, color `var(--ds-color-badge-text-color, #ffffff)`
    - `--icon-size`: направление `row`, align-items `center`
    - `--image-size`: направление `row`, align-items `center`
    - `--indicator`: ширина `var(--ds-size-6x)`, направление `row`
    - `--radio-button`: направление `row`
    - `--slide-toggle`: направление `row`, color `var(--ds-color-slide-toggle-text-color, #333333)`
    - `--text-default`: направление `row`, color `var(--ds-color-brand-neutral-super-dark, #333333)`
- Разметка:

```html
<div class="ds-element-select ds-element-select--checkbox">
  <span class="ds-element-select__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element-select__image-size"></div>
  <span class="ds-element-select__label">Текст</span>
</div>
```

#### Element sidenav `[56598:2991]` — 2 вариантов
**Описание и рекомендации по применению:**
Слот элемента бокового меню — выбирает, что стоит в строке меню: кнопка свёртывания или аватар пользователя.  
Служебный компонент бокового меню, отдельно на экран не ставится.
- **Content** (VARIANT): Avatar, Collaps icon
- Размеры и параметры:
    - высота: `var(--ds-size-5x)` (фикс.)
    - ширина: `var(--ds-size-5x)` (фикс.)
    - скругление: `var(--ds-size-1x)`
- Модификаторы (что меняет каждый):
    - `--avatar`: направление `column`, align-items `center`, промежуток между элементами `var(--ds-size-2-5x)`, внутренние отступы `3px var(--ds-size-0-5x) 3px var(--ds-size-0-5x)`
    - `--collaps-icon`: направление `row`, фон `var(--ds-color-sidenav-element-collaps-icon-background, #36474e)`
- Разметка:

```html
<div class="ds-element-sidenav ds-element-sidenav--avatar">
  <span class="ds-element-sidenav__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element-sidenav__keyboard-arrow-left"></div>
  <span class="ds-element-sidenav__label">Текст</span>
</div>
```

#### Element step `[55403:7248]` — 12 вариантов
**Описание и рекомендации по применению:**
Маркер шага степпера — иконка или счётчик (номер) на подложке.  
Часть степпера, отдельно не используется: вставляется в шаг (Step).  

Как выбрать вариант:  
Content=Icon size — маркер с иконкой, когда смысл шага понятен по иконке.  
Content=Counter — маркер с номером шага.  

Состояния: Default, Hover, Press, Selected (текущий шаг), Error (шаг заполнен неверно), Disable (шаг недоступен).  
Фронт: https://frontend-common.iiko.ru/components/stepper
- **Content** (VARIANT): Counter, Icon size
- **State** (VARIANT): Default, Disable, Error, Hover, Press, Selected
- Прочие свойства: Text#57060:7 (TEXT)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-6x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--counter`: направление `column`, color `var(--ds-color-brand-neutral-super-dark, #333333)`, color `var(--ds-color-brand-neutral-neutral, #9e9e9e)`
    - `--disabled`: pointer-events `none`
    - `--icon-size`: направление `row`, align-items `center`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-element-step ds-element-step--counter">
  <span class="ds-element-step__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-element-step__icon-size"></div>
  <div class="ds-element-step__info"></div>
  <span class="ds-element-step__label">Текст</span>
</div>
```

#### Elementare cell `[60220:72578]` — 10 вариантов
**Описание и рекомендации по применению:**
Слот содержимого ячейки таблицы — вложенный служебный набор того, что можно поставить в ячейку.  
Используется внутри строки таблицы; на экран отдельно не выносится.  

Как выбрать вариант: по тому, что показывает ячейка.
- **Variant** (VARIANT): Button, Button icon, Checkbox, Chips, Icon group, Icon size, Input number, Slide toggle, Status, Text UI
- CSS не требуется: это **слот-контейнер** — пустая обёртка под вложенный компонент (иконку, ячейку). Оформление задаёт вложенный компонент, а размер — контент.

#### Elements `[58501:4220]` — 30 вариантов
**Описание и рекомендации по применению:**
Ячейка календаря — день, месяц или год в сетке выбора.  
Служебный компонент календаря: используется внутри Datepicker. Недоступные даты блокируйте, а не убирайте из сетки.  

Как выбрать вариант:  
Type=Cell — день; Month — месяц; Year — год.  
Variant=Default — обычная дата; Today — сегодня; Selected — выбранная; Range — внутри выбранного периода.  
Состояния: Default, Hover, Press, Disable.
- **Type** (VARIANT): Cell, Month, Year
- **Variant** (VARIANT): Default, Range, Selected, Today
- **State** (VARIANT): Default, Disable, Hover, Press
- Прочие свойства: Back right#58506:0 (BOOLEAN), Back left#58506:1 (BOOLEAN), Start range#58506:2 (BOOLEAN), End range#58506:3 (BOOLEAN), Date#58506:4 (TEXT), Show focus indicator#58506:5 (BOOLEAN), Year#58506:84 (TEXT), Month#58506:165 (TEXT)
- Размеры и параметры:
    - высота: `var(--ds-size-10x)` (фикс.)
    - ширина: `var(--ds-size-10x)` (фикс.)
    - скругление: `var(--ds-radius-circular, 9999px)`
- Модификаторы (что меняет каждый):
    - `--cell`: фон `var(--ds-color-brand-neutral-lighter, #e0e0e0)`, color `var(--ds-color-text-disable, #9e9e9e)`, направление `row`, align-items `center`
    - `--disabled`: pointer-events `none`
    - `--month`: ширина `fit-content`, направление `row`, промежуток между элементами `var(--ds-size-2x)`, внутренние отступы `var(--ds-size-2-5x) var(--ds-size-1x) var(--ds-size-2-5x) var(--ds-size-2x)`
    - `--year`: ширина `fit-content`, направление `column`, align-items `center`, color `var(--ds-color-text-inversive, #ffffff)`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-elements ds-elements--cell">
  <div class="ds-elements__date"></div>
  <span class="ds-elements__label">Текст</span>
  <div class="ds-elements__range-highlight-end"></div>
  <div class="ds-elements__range-highlight-middle"></div>
  <div class="ds-elements__range-highlight-start"></div>
</div>
```

#### Elements `[58982:9594]` — 8 вариантов
**Описание и рекомендации по применению:**
Значение времени в списке — час или минута, доступные для выбора.  
Служебный компонент выбора времени: используется внутри Timepicker. Недоступное время блокируйте, а не убирайте из списка.  

Как выбрать вариант:  
Variant=Default — обычное значение; Selected — выбранное.  
Состояния: Default, Hover, Press, Range (внутри выбранного интервала), Disable.
- **Variant** (VARIANT): Default, Selected
- **State** (VARIANT): Default, Disable, Hover, Press, Range
- Прочие свойства: Start range#58506:2 (BOOLEAN), End range#58506:3 (BOOLEAN), Time#58506:84 (TEXT)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-10x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
- Модификаторы (что меняет каждый):
    - `--default`: color `var(--ds-color-text-disable, #9e9e9e)`, направление `row`, промежуток между элементами `var(--ds-size-2-5x)`, внутренние отступы `var(--ds-size-2x) var(--ds-size-4x) var(--ds-size-2x) var(--ds-size-4x)`
    - `--disabled`: pointer-events `none`
    - `--selected`: направление `column`, color `var(--ds-color-text-inversive, #ffffff)`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-elements-2 ds-elements-2--default">
  <div class="ds-elements-2__date"></div>
  <span class="ds-elements-2__label">Текст</span>
  <div class="ds-elements-2__range-highlight-end"></div>
  <div class="ds-elements-2__range-highlight-start"></div>
</div>
```

#### Expansion content `[61361:99603]` — 2 вариантов
**Описание и рекомендации по применению:**
Содержимое раскрывающейся панели — область под заголовком, куда складывается сам блок.  
Служебный компонент панели: используется внутри Expansion panel.  

Как выбрать вариант: с внутренними отступами или без них, когда отступы задаёт вложенный блок.
- **Padding off/on** (VARIANT): False, True
- Прочие свойства: Slot#61363:19 (SLOT)
- Размеры и параметры:
    - ширина: `597px` (фикс.)
    - внутренние отступы: `var(--ds-expansion-panel-content-pad-top, 16px) var(--ds-expansion-panel-content-pad-right, 16px) var(--ds-expansion-panel-content-pad-bottom, 16px) var(--ds-expansion-panel-content-pad-left, 16px)`
- Модификаторы (что меняет каждый):
    - `--false`: color `var(--ds-color-expansion-panel-content-text-color, #333333)`
    - `--true`: color `var(--ds-color-expansion-panel-content-text-color, #333333)`
- Разметка:

```html
<div class="ds-expansion-content ds-expansion-content--false">
  <span class="ds-expansion-content__label">Текст</span>
</div>
```

#### Expansion group panel `[56155:1676]` — 2 вариантов
**Описание и рекомендации по применению:**
Группа раскрывающихся панелей — несколько панелей подряд с общими разделителями.  
Берите группу, когда блоков настроек несколько; открытым держите только нужный.  

Как выбрать вариант: группа свёрнута или раскрыта.
- **Type ?** (VARIANT): Collaps, Expand
- Прочие свойства: Slot#61364:25 (SLOT)
- Размеры и параметры:
    - ширина: `597px` (фикс.)
    - промежуток между элементами: `var(--ds-expansion-panel-collaps-gap-group, 8px)`
- Модификаторы (что меняет каждый):
    - `--collaps`: color `var(--ds-color-expansion-panel-collaps-text-color, #333333)`
    - `--expand`: color `var(--ds-color-expansion-panel-collaps-text-color, #333333)`
- Разметка:

```html
<div class="ds-expansion-group-panel ds-expansion-group-panel--collaps">
  <span class="ds-expansion-group-panel__label">Текст</span>
</div>
```

#### Expansion panel `[52937:1329]` — 12 вариантов
**Описание и рекомендации по применению:**
Раскрывающаяся панель — блок, который сворачивается до заголовка: группы настроек, детали документа, дополнительные параметры.  
Прячьте в неё второстепенное, обязательные поля держите открытыми. По умолчанию оставляйте свёрнутой, если содержимое нужно не всем.  

Как выбрать вариант:  
Variant=Default — обычная панель; Info — панель с пояснением.  
Collaps/Expand=On — раскрыта; Off — свёрнута.  
Состояния: Default, Hover, Press, Disable.
- **Variant** (VARIANT): Default, Info
- **Collaps/Expand** (VARIANT): Off, On
- **State** (VARIANT): Default, Disable, Hover, Press
- Прочие свойства: Element left#17172:1340 (BOOLEAN), Element right#17172:1349 (BOOLEAN), Icon text#58024:0 (BOOLEAN), Expansion panel_Content#58991:0 (SLOT), Expansion panel_Content2#58991:9 (SLOT), Expansion panel_Content3#58991:18 (SLOT), Expansion panel_Content4#58991:27 (SLOT)
- CSS: выверено вручную, см. `components/Expansion-Panel_DS/expansion.css`

#### Expansion table panel `[56217:15104]` — 0 вариантов
_Описание компонента в Figma отсутствует._
- CSS не требуется: это **слот-контейнер** — пустая обёртка под вложенный компонент (иконку, ячейку). Оформление задаёт вложенный компонент, а размер — контент.

#### Form field cell `[60220:72732]` — 1 вариантов
**Описание и рекомендации по применению:**
Обёртка редактируемой ячейки таблицы — выравнивание и отступы поля внутри ячейки.  
Служебный компонент таблицы: используется внутри строки, отдельно на экран не ставится.
- **Variant** (VARIANT): Table content cell Chips input
- Размеры и параметры:
    - высота: минимум `var(--ds-size-10x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-form-field-cell">
  <div class="ds-form-field-cell__table-content"></div>
  <div class="ds-form-field-cell__table-content-chips-input"></div>
</div>
```

#### Hint container `[54593:479]` — 10 вариантов
**Описание и рекомендации по применению:**
Подсказка — короткое пояснение по элементу: назначение кнопки-иконки, правило заполнения поля, расшифровка статуса.  
Появляется по наведению и не должна содержать действий, без которых нельзя обойтись. Текст — одна-две строки.  

Как выбрать вариант:  
Size=Single — короткая подсказка одной строкой; Complex — с заголовком и несколькими строками.  
Orientation — сторона, с которой подсказка выходит к элементу: Up, Down, Right, Left; Default — без хвостика.
- **Size** (VARIANT): Complex, Single
- **Orientation** (VARIANT): Default, Down, Left, Right, Up
- Прочие свойства: Header#54713:4 (BOOLEAN), Content#54713:15 (BOOLEAN), Footer#54713:26 (BOOLEAN)
- Размеры и параметры:
    - ширина: `250px` (фикс.)
    - скругление: `var(--ds-hint-border-radius, 8px)`
    - тень: `var(--ds-shadow-shadows-08-dp-s)`
- Модификаторы (что меняет каждый):
    - `--default`: направление `column`, color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--down`: направление `column`, color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--left`: направление `row`, color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--right`: направление `row`, color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--up`: направление `column`, color `var(--ds-color-hint-header-text-color, #ffffff)`
- Разметка:

```html
<div class="ds-hint-container ds-hint-container--default">
  <span class="ds-hint-container__arrow"><!-- иконка: material-icons по имени --></span>
  <div class="ds-hint-container__content"></div>
  <div class="ds-hint-container__footer"></div>
  <div class="ds-hint-container__header"></div>
  <span class="ds-hint-container__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-hint-container__label">Текст</span>
</div>
```

#### Hint content `[54713:3325]` — 2 вариантов
**Описание и рекомендации по применению:**
Содержимое подсказки — текст внутри подсказки: одна строка или несколько блоков.  
Служебный компонент подсказки, отдельно на экран не ставится.
- **Content** (VARIANT): Group content, Single content
- Прочие свойства: Element right#56260:9 (BOOLEAN), Element left#56260:12 (BOOLEAN)
- Размеры и параметры:
    - ширина: `250px` (фикс.)
    - внутренние отступы: `var(--ds-hint-content-pad-top, 8px) var(--ds-hint-content-pad-right, 12px) var(--ds-hint-content-pad-bottom, 8px) var(--ds-hint-content-pad-left, 12px)`
    - промежуток между элементами: `var(--ds-hint-content-gap, 8px)`
    - фон: `var(--ds-color-hint-background-color, #424242)`
- Модификаторы (что меняет каждый):
    - `--group-content`: color `var(--ds-color-hint-content-text-color, #ffffff)`
    - `--single-content`: align-items `center`, color `var(--ds-color-hint-content-text-color, #ffffff)`
- Разметка:

```html
<div class="ds-hint-content ds-hint-content--group-content">
  <div class="ds-hint-content__block"></div>
  <div class="ds-hint-content__clear"></div>
  <div class="ds-hint-content__close"></div>
  <span class="ds-hint-content__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-hint-content__icon-size"></div>
  <div class="ds-hint-content__info"></div>
  <span class="ds-hint-content__label">Текст</span>
</div>
```

#### Hint footer `[54600:517]` — 1 вариантов
**Описание и рекомендации по применению:**
Подвал подсказки — ссылка или кнопка под текстом подсказки («Подробнее»).  
Добавляйте только когда есть куда вести; основное действие в подсказку не выносите.
- **Content** (VARIANT): Default
- Прочие свойства: Step text#54600:1 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `56px`, растёт по контенту
    - ширина: `250px` (фикс.)
    - внутренние отступы: `var(--ds-hint-footer-pad-top, 16px) var(--ds-hint-footer-pad-right, 12px) var(--ds-hint-footer-pad-bottom, 12px) var(--ds-hint-footer-pad-left, 12px)`
    - промежуток между элементами: `var(--ds-hint-footer-gap, 12px)`
    - фон: `var(--ds-color-hint-background-color, #424242)`
- Модификаторы (что меняет каждый):
    - `--default`: color `var(--ds-color-hint-footer-text-color, #ffffff)`
- Разметка:

```html
<div class="ds-hint-footer ds-hint-footer--default">
  <div class="ds-hint-footer__button-group"></div>
  <span class="ds-hint-footer__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-hint-footer__label">Текст</span>
</div>
```

#### Hint header `[54594:2219]` — 5 вариантов
**Описание и рекомендации по применению:**
Заголовок подсказки — тема пояснения и его окраска по смыслу.  
Цвет выбирайте по характеру сообщения, а не для украшения.  

Как выбрать вариант: обычное пояснение, акцентное, второстепенное, предупреждение или ошибка.
- **Style** (VARIANT): Error, Neutral, Primary, Secondary, Warning
- Прочие свойства: Element left#54594:55 (BOOLEAN), Element right#54594:56 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-8x)`, растёт по контенту
    - ширина: `250px` (фикс.)
    - внутренние отступы: `var(--ds-hint-header-pad-top, 8px) var(--ds-hint-header-pad-right, 12px) var(--ds-hint-header-pad-bottom, 4px) var(--ds-hint-header-pad-left, 12px)`
    - промежуток между элементами: `var(--ds-hint-header-gap, 8px)`
    - фон: `var(--ds-color-hint-background-color, #424242)`
- Модификаторы (что меняет каждый):
    - `--error`: color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--neutral`: color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--primary`: color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--secondary`: color `var(--ds-color-hint-header-text-color, #ffffff)`
    - `--warning`: color `var(--ds-color-hint-header-text-color, #ffffff)`
- Разметка:

```html
<div class="ds-hint-header ds-hint-header--error">
  <div class="ds-hint-header__clear"></div>
  <div class="ds-hint-header__close"></div>
  <span class="ds-hint-header__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-hint-header__icon-size"></div>
  <div class="ds-hint-header__info"></div>
  <span class="ds-hint-header__label">Текст</span>
  <span class="ds-hint-header__title">Текст</span>
</div>
```

#### Icon group `[53467:1060]` — 2 вариантов
**Описание и рекомендации по применению:**
Группа иконок — две и более иконки рядом с единым зазором: индикаторы в строке таблицы, набор статусных иконок в карточке.  
Зазор берите из варианта, вручную не раздвигайте.  

Как выбрать вариант: по нужному зазору между иконками — плотный или разряженный.
- **Size gap** (VARIANT): 2x, 4x
- Прочие свойства: Slot#60190:14 (SLOT)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-5x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-icon-size-gap-group-2x, 8px)`
- Модификаторы (что меняет каждый):
    - `--4x`: промежуток между элементами `var(--ds-icon-size-gap-group-4x, 16px)`
- Разметка:

```html
<div class="ds-icon-group ds-icon-group--4x">
  <span class="ds-icon-group__icon"><!-- иконка: material-icons по имени --></span>
</div>
```

#### Icon size `[52927:6286]` — 12 вариантов
**Описание и рекомендации по применению:**
Контейнер иконки или картинки — задаёт единый размер и выравнивание всего, что вставляется как иконка: в кнопки, поля, пункты списков, ячейки таблиц.  
Вставляйте иконку внутрь этого контейнера, а не напрямую — иначе иконки в одном ряду разъезжаются по высоте.  

Как выбрать вариант:  
Content=Icon — векторная иконка; Content=Img — картинка или аватар.  
Size — под размер родителя: мелкие в строках таблиц и подписях, средние в кнопках и полях, крупные в пустых состояниях и плитках.
- **Size** (VARIANT): 16, 20, 24, 32, 36, 40
- **Content** (VARIANT): Icon, Img
- Прочие свойства: State#54063:8 (BOOLEAN), Instance#60108:34 (INSTANCE_SWAP)
- CSS не требуется: это **слот-контейнер** — пустая обёртка под вложенный компонент (иконку, ячейку). Оформление задаёт вложенный компонент, а размер — контент.

#### Input `[52670:7573]` — 29 вариантов
**Описание и рекомендации по применению:**
Поле ввода — для однострочного текста: название, сумма, телефон, адрес.  
Свойства включаются внутри компонента: Label, Element left (иконка слева), Element right (иконка/кнопка справа),  
Support text (подсказка) и Hint text. Есть режимы с лимитом символов и счётчиком (например, 10/256),  
с префиксами (телефон, e-mail) и с сообщением об ошибке.  

Как выбрать вариант:  
Variant=Empty — поле без значения, плейсхолдер или Label внутри.  
Variant=Populated — поле со значением, Label над полем.  
Variant=No label up — компактные вытянутые поля (S / XS), без Label сверху.  
Size: M (основной), S (компактный), XS (минимальный — для строк таблиц и ячеек).  

State: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.  
Фронт: https://frontend-common.iiko.ru/components/input
- **Size** (VARIANT): M, S, XS
- **Variant** (VARIANT): Empty, No label up, Populated
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Прочие свойства: Input text#52678:0 (TEXT), Label text#52678:3 (TEXT), Support text#52678:6 (TEXT), Label#56934:32 (BOOLEAN), Element left#56934:282 (BOOLEAN), Element right#56934:407 (BOOLEAN), Support text#56934:532 (BOOLEAN), Input text#56968:66 (BOOLEAN), Hint text#57893:0 (BOOLEAN), Support#57893:30 (BOOLEAN), Hint text#57893:60 (TEXT)
- CSS: выверено вручную, см. `components/Form-Field-Input_DS/input.css`

#### Input cell `[60229:74436]` — 8 вариантов
**Описание и рекомендации по применению:**
Поле ввода внутри ячейки таблицы — правка значения прямо в строке, без отдельной формы.  
Используйте в редактируемых таблицах: количество, цена, комментарий в накладной. Вне таблицы берите обычное поле Input.  

Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Hover, Vocus+Value
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `200px` (фикс.)
    - внутренние отступы: `var(--ds-table-cell-pad-top, 8px) var(--ds-table-cell-pad-right, 8px) var(--ds-table-cell-pad-bottom, 8px) var(--ds-table-cell-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-size-2x)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-input-cell ds-input-cell--disabled">
  <div class="ds-input-cell__frame"></div>
  <span class="ds-input-cell__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-input-cell__label">Текст</span>
  <span class="ds-input-cell__support">Текст</span>
</div>
```

#### Input Datepicker `[58548:4764]` — 2 вариантов
**Описание и рекомендации по применению:**
Поле даты — ввод и выбор даты: дата поставки, период отчёта, срок годности.  
Дату можно ввести с клавиатуры или выбрать в календаре по иконке справа. Для времени берите Input Timepicker.  

Как выбрать вариант: Empty — дата не выбрана, Populated — дата выбрана.
- **Type** (VARIANT): Empty, Populated
- Размеры и параметры:
    - высота: минимум `48px`, растёт по контенту
    - ширина: `250px` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--empty`: color `var(--ds-color-form-field-input-label-text-color, #616161)`
    - `--populated`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`
- Разметка:

```html
<div class="ds-input-datepicker ds-input-datepicker--empty">
  <div class="ds-input-datepicker__frame"></div>
  <span class="ds-input-datepicker__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-input-datepicker__label">Текст</span>
  <span class="ds-input-datepicker__support">Текст</span>
</div>
```

#### Input number `[17193:84750]` — 29 вариантов
**Описание и рекомендации по применению:**
Поле числа — количество и числовые значения: количество товара, цена, процент, число дней.  
Рядом стоят кнопки шага «минус» и «плюс»; вводить можно и с клавиатуры.  
Не используйте его для текста и для дат — для дат берите Input Datepicker.  

Как выбрать вариант:  
Variant=Empty — без значения; Populated — со значением; No label up — без Label сверху (для таблиц и плотных форм).  
Size=M — основной; S и XS — плотные формы, панели, строки таблиц.  
Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **Size** (VARIANT): M, S, XS
- **Variant** (VARIANT): Empty, No label up, Populated
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Прочие свойства: Close icon#57962:0 (BOOLEAN)
- Размеры и параметры:
    - ширина: `138px` (фикс.)
    - промежуток между элементами: `18px`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--empty`: align-items `center`, color `var(--ds-color-form-field-input-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-input-text-color, #9e9e9e)`
    - `--populated`: align-items `center`, color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-label-text-color, #9e9e9e)`
    - `--s`: ширина `fit-content`
    - `--xs`: ширина `fit-content`, ширина `var(--ds-size-6x)`, высота `var(--ds-size-6x)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-input-number ds-input-number--disabled">
  <div class="ds-input-number__frame"></div>
  <span class="ds-input-number__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-input-number__label">Текст</span>
  <span class="ds-input-number__support">Текст</span>
</div>
```

#### Input number_but icon `[56967:10506]` — 1 вариантов
_Описание компонента в Figma отсутствует._
- Прочие свойства: Support#57977:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `56px`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-1x)`
- Разметка:

```html
<div class="ds-input-number-but-icon">
  <div class="ds-input-number-but-icon__button"></div>
  <div class="ds-input-number-but-icon__container"></div>
  <span class="ds-input-number-but-icon__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-input-number-but-icon__label">Текст</span>
  <div class="ds-input-number-but-icon__support-text"></div>
  <span class="ds-input-number-but-icon__text">Текст</span>
</div>
```

#### Input Timepicker `[58982:9561]` — 2 вариантов
**Описание и рекомендации по применению:**
Поле времени — ввод и выбор времени: время доставки, начало смены, время закрытия.  
Время можно ввести с клавиатуры или выбрать в списке по иконке справа. Для даты берите Input Datepicker.  

Как выбрать вариант: Empty — время не выбрано, Populated — время выбрано.
- **Type** (VARIANT): Empty, Populated
- Размеры и параметры:
    - высота: минимум `48px`, растёт по контенту
    - ширина: `250px` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--empty`: color `var(--ds-color-form-field-input-label-text-color, #616161)`
    - `--populated`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`
- Разметка:

```html
<div class="ds-input-timepicker ds-input-timepicker--empty">
  <div class="ds-input-timepicker__frame"></div>
  <span class="ds-input-timepicker__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-input-timepicker__label">Текст</span>
  <span class="ds-input-timepicker__support">Текст</span>
</div>
```

#### List (Сontainer) `[57604:4762]` — 1 вариантов
**Описание и рекомендации по применению:**
Контейнер списка — подложка с отступами, в которую складываются пункты List item.  
Берите его вместо своей подложки: отступы, разделители и прокрутка уже заданы.
- **Type** (VARIANT): Сontainer
- Прочие свойства: List container#57620:0 (SLOT), Scroll#57620:2 (BOOLEAN), Title#57623:6 (BOOLEAN), Divider header#57862:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `257px`, растёт по контенту
    - ширина: `258px` (фикс.)
    - внутренние отступы: `var(--ds-list-pad-top, 8px) 0 var(--ds-list-pad-bottom, 8px) 0`
    - скругление: `var(--ds-list-border-radius)`
    - фон: `var(--ds-color-list-background, #ffffff)`
- Модификаторы (что меняет каждый):
    - `--container`: color `var(--ds-color-list-item-text-label-color, #616161)`
- Разметка:

```html
<div class="ds-list-container ds-list-container--container">
  <div class="ds-list-container__content"></div>
  <div class="ds-list-container__divider"></div>
  <span class="ds-list-container__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-list-container__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-list-container__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-list-container__item"></div>
  <span class="ds-list-container__label">Текст</span>
  <div class="ds-list-container__scroll"></div>
</div>
```

#### List item `[54101:7922]` — 8 вариантов
**Описание и рекомендации по применению:**
Пункт списка — одна строка перечня: товар, документ, сотрудник, пункт меню действий.  
Вся строка кликабельна; действия над пунктом ставьте справа.  

Состояния: Default, Hover, Press, Selected, Back selected, Link, Negative (удаление), Disable.
- **State** (VARIANT): Back selected, Default, Disable, Hover, Link, Negative, Press, Selected
- Прочие свойства: Element left#54167:1 (BOOLEAN), Element right#54167:6 (BOOLEAN), Label up#54741:15 (BOOLEAN), Label down#54741:30 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `68px`, растёт по контенту
    - ширина: `258px` (фикс.)
    - внутренние отступы: `var(--ds-list-item-pad-top, 8px) var(--ds-list-item-pad-right, 16px) var(--ds-list-item-pad-bottom, 8px) var(--ds-list-item-pad-left, 16px)`
    - промежуток между элементами: `var(--ds-list-item-gap, 8px)`
    - фон: `var(--ds-color-list-item-default-background, #ffffff)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-list-item ds-list-item--disabled">
  <div class="ds-list-item__checkbox"></div>
  <div class="ds-list-item__content"></div>
  <span class="ds-list-item__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-list-item__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-list-item__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-list-item__icon-size"></div>
  <span class="ds-list-item__label">Текст</span>
  <div class="ds-list-item__label-down"></div>
  <div class="ds-list-item__label-up"></div>
  <span class="ds-list-item__text">Текст</span>
</div>
```

#### Logo iiko `[55332:19892]` — 4 вариантов
**Описание и рекомендации по применению:**
Логотип iiko — знак продукта в шапке приложения, боковом меню и на экранах входа.  
Пропорции и цвета не меняйте, поверх пёстрых фонов используйте инверсный вариант.  

Как выбрать вариант:  
Size=Full — знак с названием; Small — только знак (для свёрнутого меню).  
Style=Main — основной; Inverse — инверсный для тёмного фона.
- **Size** (VARIANT): Full, Small
- **Style** (VARIANT): Inverse, Main
- Размеры и параметры:
    - высота: `72px` (фикс.)
    - ширина: по контенту (hug)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-logo-iiko">
  <div class="ds-logo-iiko__vector"></div>
</div>
```

#### Logo Syrve `[56079:771]` — 4 вариантов
**Описание и рекомендации по применению:**
Логотип Syrve — знак продукта для международной версии: шапка приложения, боковое меню, экран входа.  
Пропорции и цвета не меняйте; в макетах Syrve не смешивайте с логотипом iiko.  

Как выбрать вариант:  
Size=Full — знак с названием; Small — только знак (для свёрнутого меню).  
Style=Main — основной; Inverse — инверсный для тёмного фона.
- **Size** (VARIANT): Full, Small
- **Style** (VARIANT): Inverse, Main
- Размеры и параметры:
    - высота: `72px` (фикс.)
    - ширина: по контенту (hug)
    - фон: `#ffffff`
- Разметка:

```html
<div class="ds-logo-syrve">
  <div class="ds-logo-syrve__vector"></div>
</div>
```

#### Menu (Container) `[54163:6705]` — 1 вариантов
**Описание и рекомендации по применению:**
Контейнер меню — подложка с тенью, в которую складываются пункты Menu item.  
Берите его вместо своей подложки: отступы, тень и разделители уже заданы.
- **Type** (VARIANT): Container
- Прочие свойства: Scroll#55632:0 (BOOLEAN), Menu container#56968:88 (SLOT), Title#57636:8 (BOOLEAN), Search#57750:7 (BOOLEAN), Button#57848:0 (BOOLEAN), Divider header#57848:2 (BOOLEAN), Divider footer#57848:4 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `418px`, растёт по контенту
    - ширина: `240px` (фикс.)
    - внутренние отступы: `var(--ds-menu-pad-top, 8px) 0 var(--ds-menu-pad-bottom, 8px) 0`
    - промежуток между элементами: `var(--ds-menu-gap)`
    - скругление: `var(--ds-menu-border-radius, 8px)`
    - фон: `var(--ds-color-menu-background, #ffffff)`
    - тень: `var(--ds-shadow-shadows-08-dp-s)`
- Модификаторы (что меняет каждый):
    - `--container`: color `var(--ds-color-search-default-text-color, #d6d6d6)`
- Разметка:

```html
<div class="ds-menu-container ds-menu-container--container">
  <div class="ds-menu-container__button-group"></div>
  <div class="ds-menu-container__content"></div>
  <div class="ds-menu-container__divider"></div>
  <span class="ds-menu-container__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-menu-container__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-menu-container__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-menu-container__label">Текст</span>
  <div class="ds-menu-container__scroll"></div>
  <div class="ds-menu-container__search"></div>
  <span class="ds-menu-container__title">Текст</span>
</div>
```

#### Menu item `[56090:1476]` — 7 вариантов
**Описание и рекомендации по применению:**
Пункт меню — одно действие или переход в выпадающем меню: «Изменить», «Дублировать», «Удалить».  
Опасные действия ставьте последними и оформляйте вариантом Negative; недоступные — блокируйте, а не убирайте.  

Состояния: Default, Hover, Press, Selected, Back selected, Negative, Disable.
- **State** (VARIANT): Back selected, Default, Disable, Hover, Negative, Press, Selected
- Прочие свойства: Element left#54167:1 (BOOLEAN), Element right#54167:6 (BOOLEAN), Label up#54741:15 (BOOLEAN), Label down#54741:30 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `68px`, растёт по контенту
    - ширина: `258px` (фикс.)
    - внутренние отступы: `var(--ds-menu-item-pad-top, 8px) var(--ds-menu-item-pad-right, 16px) var(--ds-menu-item-pad-bottom, 8px) var(--ds-menu-item-pad-left, 16px)`
    - промежуток между элементами: `var(--ds-menu-item-gap, 8px)`
    - фон: `var(--ds-color-menu-item-default-background, #ffffff)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-menu-item ds-menu-item--disabled">
  <div class="ds-menu-item__checkbox"></div>
  <div class="ds-menu-item__content"></div>
  <span class="ds-menu-item__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-menu-item__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-menu-item__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-menu-item__icon-size"></div>
  <span class="ds-menu-item__label">Текст</span>
  <div class="ds-menu-item__label-down"></div>
  <div class="ds-menu-item__label-up"></div>
  <span class="ds-menu-item__text">Текст</span>
</div>
```

#### Picture `[58937:3985]` — 1 вариантов
_Описание компонента в Figma отсутствует._
- Прочие свойства: Crop#58947:6 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `189px`, растёт по контенту
    - ширина: `446px` (фикс.)
    - внутренние отступы: `var(--ds-size-2x) var(--ds-size-2x) var(--ds-size-2x) var(--ds-size-2x)`
    - промежуток между элементами: `var(--ds-size-2-5x)`
    - скругление: `var(--ds-size-2x)`
    - фон: `var(--ds-color-brand-accent-super-lightest, #f8f9fc)`
- Разметка:

```html
<div class="ds-picture">
  <div class="ds-picture__crop"></div>
  <div class="ds-picture__frame-1000001806"></div>
</div>
```

#### Radio button `[54095:4263]` — 14 вариантов
**Описание и рекомендации по применению:**
Радиокнопка — выбор строго одного варианта из нескольких.  
Используйте, когда варианты взаимоисключающие: «Склад поставки». Если можно выбрать несколько — Checkbox.  

Состав: круглый индикатор без подписи. С подписью — Radio button label; набор вариантов с заголовком — Radio button group.  
Вариант по умолчанию должен быть выбран заранее — не оставляйте группу пустой.  

Как выбрать вариант:  
Type=Deselected / Selected — вариант не выбран / выбран.  
Variant=Normal / Error / Disable — обычный, с ошибкой (в группе не выбран обязательный вариант), недоступный.  

Состояния: Default, Hover, Press.
- **Variant** (VARIANT): Disable, Error, Normal
- **Type** (VARIANT): Deselected, Selected
- **State** (VARIANT): Default, Hover, Press
- CSS: выверено вручную, см. `components/index.css`

#### Radio button group `[54095:4392]` — 2 вариантов
**Описание и рекомендации по применению:**
Группа радиокнопок — набор взаимоисключающих вариантов с общим заголовком и общим support-текстом или текстом ошибки.  
Используйте, когда варианты относятся к одному вопросу и выбрать нужно один.  

Состав: заголовок группы (Support up), варианты Radio button label, общий текст под группой (Support down) — в ошибке он становится текстом ошибки для всей группы.  

Как выбрать вариант:  
Orientation=Vertical — варианты в столбец, основной случай.  
Orientation=Horizontal — в строку, когда вариантов мало и они короткие.
- **Orientation** (VARIANT): Horizontal, Vertical
- Прочие свойства: Slot vertical#57257:12 (SLOT), Slot horizontal#57257:15 (SLOT), Support up#58199:15 (BOOLEAN), Support down#58199:18 (BOOLEAN)
- CSS: выверено вручную, см. `components/index.css`

#### Radio button label `[54095:4306]` — 6 вариантов
**Описание и рекомендации по применению:**
Радиокнопка с подписью — основной способ показать вариант выбора: индикатор + текст, при необходимости support-текст.  
Используйте в формах и настройках, где нужен один вариант из списка.  

Состав: радиокнопка слева или справа от подписи (Icon left / Icon right), Label, Support.  
Кликабельна вся строка вместе с подписью.  

Как выбрать вариант:  
Type=Deselected / Selected — не выбран / выбран.  
Variant=Normal / Error / Disable — обычный, с ошибкой, недоступный.
- **Variant** (VARIANT): Disable, Error, Normal
- **Type** (VARIANT): Deselected, Selected
- Прочие свойства: Icon left#17172:1340 (BOOLEAN), Icon right#17172:1349 (BOOLEAN), Label#54065:0 (BOOLEAN), Support#58197:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-5x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-radio-button-label-gap-support, 4px)`
- Модификаторы (что меняет каждый):
    - `--disable`: color `var(--ds-color-radio-button-label-text-disable-color, #9e9e9e)`
    - `--error`: color `var(--ds-color-radio-button-label-text-color, #333333)`
    - `--normal`: color `var(--ds-color-radio-button-label-text-color, #333333)`
- Разметка:

```html
<div class="ds-radio-button-label ds-radio-button-label--disable">
  <div class="ds-radio-button-label__form"></div>
  <span class="ds-radio-button-label__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-radio-button-label__label">Текст</span>
  <div class="ds-radio-button-label__left"></div>
  <div class="ds-radio-button-label__right"></div>
  <span class="ds-radio-button-label__support">Текст</span>
  <div class="ds-radio-button-label__support-text"></div>
</div>
```

#### Scroll `[53615:15339]` — 12 вариантов
**Описание и рекомендации по применению:**
Полоса прокрутки — прокрутка длинного содержимого: таблицы, списка, панели.  
Берите её для оформления прокручиваемых блоков в макете; в готовом интерфейсе полосу рисует браузер.  

Как выбрать вариант:  
Position=First — ползунок у начала; Middle — в середине; Last — в конце.  
Size=M, S — по толщине полосы под размер блока.  
Состояния: Default, Hover.
- **Size** (VARIANT): M, S
- **Position** (VARIANT): First, Last, Middle
- **State** (VARIANT): Default, Hover
- Размеры и параметры:
    - ширина: `184px` (фикс.)
    - внутренние отступы: `var(--ds-scroll-pad-top, 2px) var(--ds-scroll-pad-right, 2px) var(--ds-scroll-pad-bottom, 2px) var(--ds-scroll-pad-left, 2px)`
- Модификаторы (что меняет каждый):
    - `--first`
    - `--last`
    - `--middle`: align-items `center`
    - `--s`: ширина `var(--ds-size-2x)`
- Состояния: `:hover` (наведение)
- Разметка:

```html
<div class="ds-scroll ds-scroll--first">
  <div class="ds-scroll__background"></div>
  <div class="ds-scroll__knob"></div>
</div>
```

#### Scroll tabs `[59032:1821]` — 4 вариантов
**Описание и рекомендации по применению:**
Стрелка прокрутки вкладок — появляется, когда вкладки не помещаются по ширине.  
Служебный элемент вкладок: ставится по краям строки вкладок, отдельно не используется. Вкладки не переносите на вторую строку — прокручивайте.  

Как выбрать вариант: сторона прокрутки — влево или вправо.
- **Orientation** (VARIANT): Left, Right
- **State** (VARIANT): Default, Hover
- Размеры и параметры:
    - высота: минимум `var(--ds-size-7x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `0 0 0 48px`
    - промежуток между элементами: `var(--ds-size-2-5x)`
- Модификаторы (что меняет каждый):
    - `--left`: внутренние отступы `0 48px 0 0`
- Разметка:

```html
<div class="ds-scroll-tabs ds-scroll-tabs--left">
  <div class="ds-scroll-tabs__button-icon"></div>
  <span class="ds-scroll-tabs__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-scroll-tabs__icon-size"></div>
</div>
```

#### Search `[54453:1620]` — 15 вариантов
**Описание и рекомендации по применению:**
Поле поиска — фильтрация списка или таблицы по строке: поиск товара, накладной, сотрудника.  
Показывайте результаты по мере ввода, а не по кнопке; крестик справа очищает запрос.  

Как выбрать вариант:  
Size=M — основной; S — панели и шапки блоков; XS — строки таблиц и плотные панели.  
Состояния: Default, Hover, Focus, Focus+Value, Completed, Disable.
- **Size** (VARIANT): M, S, XS
- **State** (VARIANT): Completed, Default, Disable, Focus, Focus+Value, Hover
- Прочие свойства: Left icon#54453:0 (BOOLEAN), Right icon#54459:3 (BOOLEAN)
- Размеры и параметры:
    - ширина: `243px` (фикс.)
    - внутренние отступы: `var(--ds-search-m-size-pad-top, 12px) var(--ds-search-m-size-pad-right, 12px) var(--ds-search-m-size-pad-bottom, 12px) var(--ds-search-m-size-pad-left, 12px)`
    - промежуток между элементами: `var(--ds-search-gap, 8px)`
    - скругление: `var(--ds-search-border-radius, 12px)`
    - рамка: `1px solid var(--ds-color-search-default-border-color, #e0e0e0)`
    - фон: `var(--ds-color-search-background, #f8f9fc)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--s`: внутренние отступы `var(--ds-search-s-size-pad-top, 8px) var(--ds-search-s-size-pad-right, 12px) var(--ds-search-s-size-pad-bottom, 8px) var(--ds-search-s-size-pad-left, 12px)`, ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
    - `--xs`: высота `var(--ds-size-9x)`, ширина `var(--ds-size-9x)`, внутренние отступы `var(--ds-size-1-5x) var(--ds-size-1-5x) var(--ds-size-1-5x) var(--ds-size-1-5x)`, скругление `var(--ds-size-circular)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-search ds-search--disabled">
  <div class="ds-search__divider"></div>
  <span class="ds-search__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-search__icon-size"></div>
  <span class="ds-search__label">Текст</span>
  <div class="ds-search__right-icon"></div>
  <span class="ds-search__text">Текст</span>
</div>
```

#### Select (Сontainer) `[57735:17612]` — 1 вариантов
**Описание и рекомендации по применению:**
Контейнер выпадающего списка — подложка с тенью, в которую складываются пункты Select item.  
Берите его для собственного списка вместо рисования своей подложки; отступы и тень уже заданы.
- **Type** (VARIANT): Сontainer
- Прочие свойства: Scroll#55632:0 (BOOLEAN), Item container#56968:88 (SLOT), Title#57636:8 (BOOLEAN), Search#57740:3 (BOOLEAN), Button#57740:5 (BOOLEAN), Divider header#57862:2 (BOOLEAN), Divider footer#57862:4 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `406px`, растёт по контенту
    - ширина: `240px` (фикс.)
    - внутренние отступы: `var(--ds-menu-pad-top, 8px) 0 var(--ds-menu-pad-bottom, 8px) 0`
    - промежуток между элементами: `var(--ds-space-0)`
    - скругление: `var(--ds-radius-3x, 12px)`
    - фон: `var(--ds-color-menu-background, #ffffff)`
    - тень: `var(--ds-shadow-shadows-08-dp-s)`
- Модификаторы (что меняет каждый):
    - `--container`: color `var(--ds-color-search-default-text-color, #d6d6d6)`
- Разметка:

```html
<div class="ds-select-container ds-select-container--container">
  <div class="ds-select-container__button"></div>
  <div class="ds-select-container__button-group"></div>
  <div class="ds-select-container__content"></div>
  <div class="ds-select-container__divider"></div>
  <span class="ds-select-container__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-select-container__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-select-container__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-select-container__label">Текст</span>
  <div class="ds-select-container__scroll"></div>
  <div class="ds-select-container__search"></div>
  <span class="ds-select-container__title">Текст</span>
</div>
```

#### Select cell `[60231:74976]` — 7 вариантов
**Описание и рекомендации по применению:**
Список выбора внутри ячейки таблицы — выбор значения прямо в строке: склад, статус, единица измерения.  
Используйте в редактируемых таблицах; вне таблицы берите Select form.  

Состояния: Default, Hover, Focus, Focus+Value, Error, Error+Hover, Disable.
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Value, Hover
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `200px` (фикс.)
    - внутренние отступы: `var(--ds-table-cell-pad-top, 8px) var(--ds-table-cell-pad-right, 8px) var(--ds-table-cell-pad-bottom, 8px) var(--ds-table-cell-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-size-2x)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-select-cell ds-select-cell--disabled">
  <span class="ds-select-cell__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-select-cell__input"></div>
  <div class="ds-select-cell__input-frame"></div>
  <span class="ds-select-cell__label">Текст</span>
  <span class="ds-select-cell__support">Текст</span>
</div>
```

#### Select form `[57862:17226]` — 22 вариантов
**Описание и рекомендации по применению:**
Список выбора — выбор значения из готового набора: склад, поставщик, тип оплаты.  
Берите его, когда вариантов много и они известны заранее; для 2–3 вариантов на виду используйте Radio button или Toggle buttons, для поиска по большому справочнику — Autocomplete.  

Состав: Label, поле со значением и стрелкой, выпадающий список (Select item внутри контейнера), support-текст под полем.  

Как выбрать вариант:  
Variant=Empty — значение не выбрано; Populated — значение выбрано.  
Size=M — основной; S и XS — плотные формы и таблицы.  
Состояния: Default, Hover, Focus, Focus+Value, Error, Disable.
- **Size** (VARIANT): M, S, XS
- **Variant** (VARIANT): Empty, Populated
- **State** (VARIANT): Default, Disable, Error, Focus, Focus+Value, Hover
- Размеры и параметры:
    - ширина: `250px` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--empty`: color `var(--ds-color-form-field-input-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-input-text-color, #9e9e9e)`
    - `--populated`: color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`, color `var(--ds-color-form-field-filled-disable-label-text-color, #9e9e9e)`
    - `--s`: ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
    - `--xs`: ширина `var(--ds-size-5x)`, высота `var(--ds-size-5x)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-select-form ds-select-form--disabled">
  <span class="ds-select-form__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-select-form__input"></div>
  <div class="ds-select-form__input-frame"></div>
  <span class="ds-select-form__label">Текст</span>
  <span class="ds-select-form__support">Текст</span>
</div>
```

#### Select item `[57735:17872]` — 8 вариантов
**Описание и рекомендации по применению:**
Пункт выпадающего списка — одна строка выбора внутри Select: значение, при необходимости с подзаголовком и иконкой.  
Подзаголовок используйте, когда одного названия недостаточно (артикул, склад, комментарий).  

Состояния: Default, Hover, Press, Selected, Back selected, Error, Disable.
- **State** (VARIANT): Back selected, Default, Disable, Error, Hover, Press, Selected
- **Subtitle** (VARIANT): False, True
- Прочие свойства: Element left#54167:1 (BOOLEAN), Element right#54167:6 (BOOLEAN), Label up#54741:15 (BOOLEAN), Label down#54741:30 (BOOLEAN), Left#60868:0 (BOOLEAN), Right#60868:1 (BOOLEAN)
- Размеры и параметры:
    - ширина: `258px` (фикс.)
    - внутренние отступы: `var(--ds-select-item-pad-top-sub, 12px) var(--ds-select-item-pad-right, 16px) var(--ds-select-item-pad-bottom-sub, 6px) var(--ds-select-item-pad-left, 16px)`
    - промежуток между элементами: `var(--ds-select-item-gap, 8px)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--false`: внутренние отступы `var(--ds-select-item-pad-top, 8px) var(--ds-select-item-pad-right, 16px) var(--ds-select-item-pad-bottom, 8px) var(--ds-select-item-pad-left, 16px)`, фон `var(--ds-color-select-item-default-background, #ffffff)`, color `var(--ds-color-select-item-text-label-color, #616161)`, фон `var(--ds-color-select-item-disable-background, #ffffff)`
    - `--true`: align-items `center`, фон `var(--ds-color-select-item-default-background, #ffffff)`, color `var(--ds-color-select-item-text-label-color, #616161)`
- Состояния: `:active` (нажатие), `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-select-item ds-select-item--disabled">
  <div class="ds-select-item__content"></div>
  <span class="ds-select-item__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-select-item__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-select-item__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-select-item__icon-size"></div>
  <span class="ds-select-item__label">Текст</span>
  <div class="ds-select-item__label-down"></div>
  <div class="ds-select-item__label-up"></div>
  <div class="ds-select-item__subtitle"></div>
</div>
```

#### Sidenav control `[55142:1734]` — 6 вариантов
**Описание и рекомендации по применению:**
Кнопка свёртывания бокового меню — переключает меню между раскрытым и свёрнутым видом.  
Стоит на границе меню; в макете показывайте её в том же состоянии, что и само меню.  

Состояния: Default, Hover, Press.
- **Mode** (VARIANT): Collapsed, Expanded
- **State** (VARIANT): Default, Hover, Press
- Прочие свойства: Divider#55147:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `41px`, растёт по контенту
    - ширина: `200px` (фикс.)
    - промежуток между элементами: `var(--ds-sidenav-control-expanded-gap)`
- Модификаторы (что меняет каждый):
    - `--collapsed`: ширина `fit-content`, промежуток между элементами `var(--ds-sidenav-control-collapsed-gap)`
    - `--expanded`: фон `var(--ds-color-sidenav-control-background, #263136)`, color `var(--ds-color-sidenav-control-text-color, #ffffff)`
- Состояния: `:active` (нажатие), `:hover` (наведение)
- Разметка:

```html
<div class="ds-sidenav-control ds-sidenav-control--collapsed">
  <div class="ds-sidenav-control__content"></div>
  <div class="ds-sidenav-control__divider"></div>
  <span class="ds-sidenav-control__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-sidenav-control__icon-size"></div>
  <span class="ds-sidenav-control__label">Текст</span>
</div>
```

#### Sidenav Footer `[55111:1056]` — 3 вариантов
**Описание и рекомендации по применению:**
Подвал бокового меню — пользователь, помощь и выход под списком разделов.  
В свёрнутом меню остаются только иконки.  

Как выбрать вариант: уровень меню (основное или вложенное) и раскрыто ли меню.
- **Type** (VARIANT): L1, L2
- **Mode** (VARIANT): Collapsed, Expanded
- Прочие свойства: Divider#55147:10 (BOOLEAN), Container#59128:17 (SLOT), Container#59128:25 (SLOT)
- Размеры и параметры:
    - ширина: `260px` (фикс.)
    - внутренние отступы: `var(--ds-sidenav-footer-l2-pad-top, 12px) var(--ds-sidenav-footer-l2-pad-right, 16px) var(--ds-sidenav-footer-l2-pad-bottom, 12px) var(--ds-sidenav-footer-l2-pad-left, 16px)`
    - промежуток между элементами: `var(--ds-sidenav-footer-l2-gap, 12px)`
- Модификаторы (что меняет каждый):
    - `--l1`: ширина `200px`, направление `column`, color `var(--ds-color-sidenav-item-l1-text-color, #ffffff)`, ширина `52px`
    - `--l2`: направление `row`, align-items `center`, фон `var(--ds-color-sidenav-footer-l2-background, #ffffff)`, color `var(--ds-color-sidenav-footer-l2-text-color, #616161)`
- Разметка:

```html
<div class="ds-sidenav-footer ds-sidenav-footer--l1">
  <div class="ds-sidenav-footer__divider"></div>
  <span class="ds-sidenav-footer__label">Текст</span>
  <div class="ds-sidenav-footer__logo-iiko"></div>
  <div class="ds-sidenav-footer__vector"></div>
  <div class="ds-sidenav-footer__ver-7-8-6-29440"></div>
</div>
```

#### Sidenav header `[55045:637]` — 3 вариантов
**Описание и рекомендации по применению:**
Шапка бокового меню — логотип и название заведения или раздела над списком пунктов.  
В свёрнутом меню остаётся только знак логотипа.  

Как выбрать вариант: уровень меню (основное или вложенное) и раскрыто ли меню.
- **Type** (VARIANT): L1, L2
- **Mode** (VARIANT): Collapsed, Expanded
- Прочие свойства: Element right#55074:0 (BOOLEAN), Element left#55661:0 (BOOLEAN), Divider#59107:0 (BOOLEAN), Informer#59128:5 (BOOLEAN)
- Размеры и параметры:
    - ширина: `200px` (фикс.)
    - внутренние отступы: `var(--ds-sidenav-header-pad-top, 12px) var(--ds-sidenav-header-l1-expanded-pad-right, 16px) var(--ds-sidenav-header-pad-bottom, 12px) var(--ds-sidenav-header-l1-expanded-pad-left, 16px)`
    - промежуток между элементами: `var(--ds-sidenav-header-l1-expanded-gap, 92px)`
- Модификаторы (что меняет каждый):
    - `--l1`: направление `row`, фон `var(--ds-color-sidenav-header-l1-background, #263136)`, ширина `52px`, направление `column`
    - `--l2`: высота `48px`, ширина `260px`, направление `row`, промежуток между элементами `var(--ds-sidenav-header-l2-gap, 8px)`
- Разметка:

```html
<div class="ds-sidenav-header ds-sidenav-header--l1">
  <div class="ds-sidenav-header__close"></div>
  <span class="ds-sidenav-header__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-sidenav-header__icon-size"></div>
  <span class="ds-sidenav-header__label">Текст</span>
  <div class="ds-sidenav-header__logo-iiko"></div>
  <div class="ds-sidenav-header__vector"></div>
</div>
```

#### Sidenav item `[55070:3734]` — 13 вариантов
**Описание и рекомендации по применению:**
Пункт бокового меню — раздел приложения в левой навигации: «Заказы», «Склады», «Отчёты».  
Три уровня вложенности: раздел, подраздел, пункт подраздела. В свёрнутом меню видна только иконка, название показывайте тултипом.  

Как выбрать вариант:  
Type=L1, L2, L3 — уровень вложенности пункта.  
Mode=Expanded — меню раскрыто (иконка + название); Collapsed — свёрнуто (только иконка).  
Состояния: Default, Hover, Active (текущий раздел), Selected (выбран).
- **Type** (VARIANT): L1, L2, L3
- **Mode** (VARIANT): Collapsed, Expanded
- **State** (VARIANT): Active, Default, Hover, Selected
- Прочие свойства: Element right#55070:0 (BOOLEAN), Badge#55083:0 (BOOLEAN), Divider#55219:13 (BOOLEAN), Indicator#59087:0 (BOOLEAN)
- Размеры и параметры:
    - ширина: `260px` (фикс.)
    - внутренние отступы: `var(--ds-sidenav-item-l3-pad-top, 8px) var(--ds-sidenav-item-l3-pad-right, 16px) var(--ds-sidenav-item-l3-pad-bottom, 8px) var(--ds-sidenav-item-l3-pad-left, 32px)`
    - промежуток между элементами: `var(--ds-sidenav-item-l3-gap, 8px)`
- Модификаторы (что меняет каждый):
    - `--l1`: ширина `200px`, направление `row`, align-items `center`, промежуток между элементами `var(--ds-sidenav-item-l1-gap-container, 8px)`
    - `--l2`: направление `column`, фон `var(--ds-color-sidenav-item-l2-background, #ffffff)`, color `var(--ds-color-sidenav-item-l2-text-color, #333333)`
    - `--l3`: направление `row`, align-items `center`, фон `var(--ds-color-sidenav-item-l3-background, #ffffff)`, color `var(--ds-color-sidenav-item-l3-text-color, #333333)`
- Состояния: `:hover` (наведение)
- Разметка:

```html
<div class="ds-sidenav-item ds-sidenav-item--l1">
  <div class="ds-sidenav-item__l3"></div>
  <span class="ds-sidenav-item__label">Текст</span>
</div>
```

#### Sidenav View `[55074:393]` — 3 вариантов
**Описание и рекомендации по применению:**
Боковое меню целиком — готовая левая навигация: шапка, пункты, подвал.  
Берите её как основу экрана и подставляйте свои пункты; ширину раскрытого и свёрнутого меню не меняйте.  

Как выбрать вариант: уровень меню и его состояние — раскрыто или свёрнуто.
- **Type** (VARIANT): L1, L2
- **State** (VARIANT): Collapsed, Expanded
- Прочие свойства: Scroll#55227:26 (BOOLEAN), Container#59137:0 (SLOT), Container#59137:4 (SLOT), Container#59137:8 (SLOT), Container#59137:12 (SLOT), Info#59160:3 (BOOLEAN), More Pannel#59214:0 (BOOLEAN)
- CSS не требуется: собственного оформления нет — компонент задаёт только структуру/поведение, вид приходит от вложенных элементов.

#### Slide toggle `[52887:2592]` — 6 вариантов
**Описание и рекомендации по применению:**
Переключатель — включение и выключение настройки, действие применяется сразу, без кнопки «Сохранить».  
Используйте для режимов и правил: «Требуется подтверждение», «Стоимость товаров в заказе видна сотруднику ресторана». Если выбор нужно подтвердить кнопкой или пунктов несколько — Checkbox.  

Состав: переключатель, Title, support-текст под заголовком (Support down), элемент справа (Element right) — например иконка-подсказка.  
Подпись формулируйте утверждением, а не вопросом; не дублируйте в ней слово «включить».  

Как выбрать вариант:  
Active=On / Off — настройка включена / выключена.  
State=Default, Hover, Disable — обычное состояние, курсор над переключателем, недоступен.
- **Active** (VARIANT): Off, On
- **State** (VARIANT): Default, Disable, Hover
- Прочие свойства: Title#53326:0 (BOOLEAN), Support down#58203:7 (BOOLEAN), Element right#58364:0 (BOOLEAN)
- CSS: выверено вручную, см. `components/Slide-Toggle_DS/slide-toggle.css`

#### Snackbar `[54373:10303]` — 4 вариантов
**Описание и рекомендации по применению:**
Всплывающее сообщение о результате действия: «Изменения сохранены», «Товары добавлены», «Не удалось сохранить изменения», «Сервер временно недоступен».  
Появляется на короткое время внизу экрана и не требует ответа; если решение обязательно — берите диалог.  
Действие внутри допускается одно («Обновить», «Открыть», «Отменить»).  

Как выбрать вариант:  
Type=Single — одна строка сообщения; Complex — с заголовком, описанием и действием.  
Mode=Dark — на светлых экранах; Light — на тёмных.
- **Type** (VARIANT): Complex, Single
- **Mode** (VARIANT): Dark, Light
- Прочие свойства: Element left#54373:16 (BOOLEAN), Element right#54426:0 (BOOLEAN), Progress#58768:0 (BOOLEAN), Content#58768:6 (BOOLEAN), Bottom actions#58768:12 (BOOLEAN)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - скругление: `var(--ds-snackbar-border-radius, 8px)`
    - тень: `var(--ds-shadow-shadows-08-dp-s)`
- Модификаторы (что меняет каждый):
    - `--complex`: ширина `232px`, фон `var(--ds-color-snackbar-complex-dark-background, #424242)`, color `var(--ds-color-snackbar-complex-dark-text-color, #ffffff)`, ширина `370px`
    - `--single`: фон `var(--ds-color-snackbar-complex-dark-background, #424242)`, color `var(--ds-color-snackbar-complex-dark-text-color, #ffffff)`, ширина `370px`, фон `var(--ds-color-snackbar-complex-light-background, #ffffff)`
- Разметка:

```html
<div class="ds-snackbar ds-snackbar--complex">
  <div class="ds-snackbar__body"></div>
  <div class="ds-snackbar__button"></div>
  <div class="ds-snackbar__content"></div>
  <span class="ds-snackbar__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-snackbar__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-snackbar__label">Текст</span>
  <div class="ds-snackbar__progress"></div>
</div>
```

#### State `[54063:12395]` — 2 вариантов
**Описание и рекомендации по применению:**
Подложка состояния под иконкой — круглая или квадратная подсветка при наведении и нажатии.  
Служебный элемент кнопок-иконок и пунктов: подставляется под иконку, отдельно на экран не ставится.
- **State** (VARIANT): Hover, Press
- Размеры и параметры:
    - высота: `var(--ds-size-6x)` (фикс.)
    - ширина: `var(--ds-size-6x)` (фикс.)
- Состояния: `:active` (нажатие), `:hover` (наведение)

#### Status `[52928:6588]` — 18 вариантов
**Описание и рекомендации по применению:**
Статус — короткая метка состояния объекта: «Новый», «В работе», «Оплачен», «Закрыт».  
Показывайте в таблицах, списках и карточках рядом с названием или в колонке «Статус».  

Как выбрать вариант:  
Accent — активное состояние, действие сейчас выполняется.  
Positive — успех, подтверждение.  
Warning — требуется внимание, просрочено.  
Negative — ошибка, блокирующее состояние.  
Neutral — нейтральное, без акцента.  
Contrast-1 … 4 — дополнительные цвета, когда основных недостаточно.  

Type=Filled — с подложкой, заметный. Type=Text — только текст, не перетягивает внимание.  
Фронт: https://frontend-common.iiko.ru/components/status
- **Style** (VARIANT): Accent, Contrast-1, Contrast-2, Contrast-3, Contrast-4, Negative, Neutral, Positive, Warning
- **Type** (VARIANT): Filled, Text
- Прочие свойства: Element left#17172:1340 (BOOLEAN), Element right#17172:1349 (BOOLEAN)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-status-pad-top, 4px) var(--ds-status-pad-right, 6px) var(--ds-status-pad-bottom, 4px) var(--ds-status-pad-left, 6px)`
    - промежуток между элементами: `var(--ds-status-gap, 4px)`
    - скругление: `var(--ds-status-border-radius, 8px)`
- Модификаторы (что меняет каждый):
    - `--accent`: фон `var(--ds-color-status-accent-filled-background, #f5f9ff)`, color `var(--ds-color-status-accent-filled-text-color, #448aff)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-accent-text-text-color, #448aff)`
    - `--contrast-1`: фон `var(--ds-color-status-contrast-1-filled-background, #fcf6fd)`, color `var(--ds-color-status-contrast-1-filled-text-color, #9c27b0)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-contrast-1-text-text-color, #9c27b0)`
    - `--contrast-2`: фон `var(--ds-color-status-contrast-2-filled-background, #fcf8f6)`, color `var(--ds-color-status-contrast-2-filled-text-color, #3e261e)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-contrast-2-text-text-color, #3e261e)`
    - `--contrast-3`: фон `var(--ds-color-status-contrast-3-filled-background, #f8fafc)`, color `var(--ds-color-status-contrast-3-filled-text-color, #263136)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-contrast-3-text-text-color, #263136)`
    - `--contrast-4`: фон `var(--ds-color-status-contrast-4-filled-background, #f9fbea)`, color `var(--ds-color-status-contrast-4-filled-text-color, #4f5412)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-contrast-4-text-text-color, #4f5412)`
    - `--negative`: фон `var(--ds-color-status-negative-filled-background, #fff8f8)`, color `var(--ds-color-status-negative-filled-text-color, #ff5252)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-negative-text-text-color, #ff5252)`
    - `--neutral`: фон `var(--ds-color-status-neutral-filled-background, #fafafa)`, color `var(--ds-color-status-neutral-filled-text-color, #616161)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-neutral-text-text-color, #616161)`
    - `--positive`: фон `var(--ds-color-status-positive-filled-background, #f3fcf7)`, color `var(--ds-color-status-positive-filled-text-color, #14b456)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-positive-text-text-color, #14b456)`
    - `--warning`: фон `var(--ds-color-status-warning-filled-background, #fffcf8)`, color `var(--ds-color-status-warning-filled-text-color, #ea7806)`, внутренние отступы `var(--ds-status-pad-top-text) var(--ds-status-pad-right-text) var(--ds-status-pad-bottom-text) var(--ds-status-pad-left-text)`, color `var(--ds-color-status-warning-text-text-color, #ea7806)`
- Разметка:

```html
<div class="ds-status ds-status--accent">
  <div class="ds-status__content"></div>
  <span class="ds-status__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-status__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-status__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-status__info"></div>
  <span class="ds-status__label">Текст</span>
</div>
```

#### Step `[54800:3659]` — 12 вариантов
**Описание и рекомендации по применению:**
Степпер — шаги многошагового процесса: мастер настройки, онбординг, оформление заказа.  
Показывает текущее положение и сколько шагов осталось. Внизу — панель с кнопками «Назад» и «Далее».  
Не сочетайте степпер с крестиком закрытия — если нужно закрыть, используйте кнопку внизу.  

Состав степпера:  
Step — кликабельный шаг (иконка + название).  
Element step — маркер шага: иконка или счётчик на подложке.  
Stepper line — контейнер, строка со всеми маркерами.  
Stepper button — кнопка «Назад» / «Далее» в панели внизу.  
Фронт: https://frontend-common.iiko.ru/components/stepper
- **Background** (VARIANT): Off, On
- **State** (VARIANT): Default, Disable, Error, Hover, Press, Selected
- Прочие свойства: Element left#55771:0 (BOOLEAN), Element right#55771:13 (BOOLEAN), Text#57060:20 (TEXT)
- CSS: выверено вручную, см. `components/Stepper_DS/stepper.css`

#### Stepper button `[55419:7330]` — 12 вариантов
**Описание и рекомендации по применению:**
Кнопка навигации степпера — «Назад» и «Далее» в панели внизу многошагового процесса.  
Используется только вместе со степпером; для обычных действий берите Button.  

Как выбрать вариант:  
Type=Filled — акцентная (обычно «Далее»); Type=Outlined — второстепенная (обычно «Назад»).  
Position=First / Middle / Last — место в группе: First — «Назад» слева, Last — «Далее» справа.  
Content=Icon — только иконка; Content=Text — с текстом.  
Фронт: https://frontend-common.iiko.ru/components/stepper
- **Type** (VARIANT): Filled, Outlined
- **Position** (VARIANT): First, Last, Middle
- **Content** (VARIANT): Icon, Text
- Прочие свойства: Text#55442:0 (BOOLEAN)
- CSS: выверено вручную, см. `components/Stepper_DS/stepper.css`

#### Stepper line `[54689:3072]` — 4 вариантов
**Описание и рекомендации по применению:**
Строка степпера — контейнер со всеми маркерами шагов в один ряд.  
Ставится вверху экрана или диалога многошагового процесса; внутрь вкладываются шаги Step.  

Как выбрать вариант:  
Step=On — с маркерами шагов; Step=Off — контейнер без маркеров, только подложка.  
Background=On — с подложкой под шагами; Background=Off — без подложки, по контенту.  
Фронт: https://frontend-common.iiko.ru/components/stepper
- **Step** (VARIANT): Off, On
- **Background** (VARIANT): Off, On
- Прочие свойства: Content step#59393:0 (SLOT), Content step background#59393:5 (SLOT), Content#59393:10 (SLOT), Content background#59393:15 (SLOT), Scroll left#59393:20 (BOOLEAN), Scroll right#59393:25 (BOOLEAN)
- CSS: выверено вручную, см. `components/Stepper_DS/stepper.css`

#### Tab element `[54404:200]` — 16 вариантов
**Описание и рекомендации по применению:**
Вкладка — один раздел в строке вкладок: название, при необходимости иконка и счётчик.  
Счётчик показывает количество записей в разделе; активная вкладка всегда одна.  

Как выбрать вариант:  
Active=On — текущий раздел; Off — остальные разделы.  
Lvl=1 — основной уровень; Lvl=2 — вложенный.  
Состояния: Default, Hover, Press, Disable.
- **Lvl** (VARIANT): 1, 2
- **State** (VARIANT): Default, Disable, Hover, Press
- **Active** (VARIANT): Off, On
- Прочие свойства: Element left#54447:8 (BOOLEAN), Counter#54447:13 (BOOLEAN), Text#54876:8 (BOOLEAN), Element right#59422:0 (BOOLEAN)
- CSS: выверено вручную, см. `components/index.css`

#### Table 2 lvl `[60074:44684]` — 2 вариантов
**Описание и рекомендации по применению:**
Вложенный уровень таблицы — подстрока и подъячейка внутри строки: состав блюда, позиции в документе, разбивка по складам.  
Берите его, когда запись раскрывается в детали; для отдельной таблицы уровень не нужен.  

Как выбрать вариант: подстрока целиком или отдельная ячейка второго уровня.
- **Type** (VARIANT): Table cell 2 lvl, Table row 2 lvl
- Прочие свойства: Header 2 lvl#60074:0 (SLOT)
- Размеры и параметры:
    - высота: минимум `72px`, растёт по контенту
    - ширина: `162px` (фикс.)
- Модификаторы (что меняет каждый):
    - `--table-cell-2-lvl`: направление `column`, рамка `1px solid var(--ds-color-stroke-default, #e0e0e0)`
    - `--table-row-2-lvl`: ширина `fit-content`, направление `row`, align-items `center`
- Разметка:

```html
<div class="ds-table-2-lvl ds-table-2-lvl--table-cell-2-lvl">
  <div class="ds-table-2-lvl__header-row"></div>
</div>
```

#### Table Chips Input `[60220:70978]` — 8 вариантов
**Описание и рекомендации по применению:**
Ячейка таблицы с вводом тегов — готовая ячейка вместе с полем тегов и отступами строки.  
Служебный компонент таблицы: ставится в строку, отдельно на экран не выносится.  

Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **Style** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Hover, Vocus+Value
- Размеры и параметры:
    - высота: минимум `var(--ds-size-6x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - фон: `#ffffff`
- Модификаторы (что меняет каждый):
    - `--default`: color `#616161`
    - `--disable`: color `#9e9e9e`
    - `--error`: color `#616161`
    - `--error-hover`: color `#616161`
    - `--focus`: color `#333333`
    - `--focus-placeholder`: color `#333333`
    - `--hover`: color `#616161`
    - `--vocus-value`: color `#333333`
- Разметка:

```html
<div class="ds-table-chips-input ds-table-chips-input--default">
  <div class="ds-table-chips-input__frame"></div>
  <span class="ds-table-chips-input__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-table-chips-input__label">Текст</span>
  <span class="ds-table-chips-input__support">Текст</span>
</div>
```

#### Table content cell `[52954:1253]` — 8 вариантов
**Описание и рекомендации по применению:**
Ячейка таблицы — одно значение в строке данных: название товара, количество, цена, ссылка на документ.  
Выравнивание берите по типу данных: текст влево, числа вправо. Пустое значение показывайте прочерком, а не пустотой.  

Состояния: Default, Null (нет значения), Link, Hover, Focus, Edit (правка значения), Error, Disable.
- **State** (VARIANT): Default, Disable, Edit, Error, Focus, Hover, Link, Null
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-table-cell-pad-top, 8px) var(--ds-table-cell-pad-right, 8px) var(--ds-table-cell-pad-bottom, 8px) var(--ds-table-cell-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-size-2x)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-table-content-cell ds-table-content-cell--disabled">
  <div class="ds-table-content-cell__element"></div>
  <span class="ds-table-content-cell__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-table-content-cell__label">Текст</span>
  <div class="ds-table-content-cell__text-ui"></div>
</div>
```

#### Table content row `[60105:56764]` — 5 вариантов
**Описание и рекомендации по применению:**
Строка таблицы — набор ячеек одной записи: позиция накладной, товар, документ.  
Выделение строки используйте для действий над записью; чередование фона включайте только в длинных таблицах.  

Состояния: Default, Zebra (чередование фона), Hover, Selected, Disable.
- **State** (VARIANT): Default, Disable, Hover, Selected, Zebra
- Прочие свойства: Content#60036:0 (SLOT)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - рамка: `1px solid var(--ds-color-stroke-default, #e0e0e0)`
    - фон: `var(--ds-color-table-row-content-default-background, #ffffff)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-table-content-row ds-table-content-row--disabled">
  <span class="ds-table-content-row__label">Текст</span>
</div>
```

#### Table footer `[59207:20759]` — 1 вариантов
**Описание и рекомендации по применению:**
Подвал таблицы — итоги по колонкам и постраничная навигация.  
Итоги показывайте по тем же колонкам, что и в строках; если итогов нет — подвал не добавляйте.
- **Type** (VARIANT): Default
- Прочие свойства: Slot Content#59249:0 (SLOT)
- Размеры и параметры:
    - высота: `65px` (фикс.)
    - ширина: `980px` (фикс.)
    - фон: `var(--ds-color-table-footer-background, #ffffff)`
    - тень: `var(--ds-shadow-shadows-01-dp-sl)`
- Модификаторы (что меняет каждый):
    - `--default`: color `var(--ds-color-expansion-panel-content-text-color, #333333)`
- Разметка:

```html
<div class="ds-table-footer ds-table-footer--default">
  <div class="ds-table-footer__content"></div>
  <div class="ds-table-footer__divider"></div>
  <span class="ds-table-footer__label">Текст</span>
</div>
```

#### Table header cell `[60098:45424]` — 3 вариантов
**Описание и рекомендации по применению:**
Ячейка шапки таблицы — название колонки и сортировка по ней.  
Название колонки пишите коротко, единицы измерения выносите в название, а не в каждую ячейку.  

Состояния: Default, Hover, Disable (сортировка недоступна).
- **State** (VARIANT): Default, Disable, Hover
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-table-cell-pad-top, 8px) var(--ds-table-cell-pad-right, 8px) var(--ds-table-cell-pad-bottom, 8px) var(--ds-table-cell-pad-left, 8px)`
    - промежуток между элементами: `var(--ds-size-2x)`
    - рамка: `1px solid var(--ds-color-stroke-default, #e0e0e0)`
    - фон: `var(--ds-color-table-cell-header-default-background, #f0f5ff)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно), `:hover` (наведение)
- Разметка:

```html
<div class="ds-table-header-cell ds-table-header-cell--disabled">
  <div class="ds-table-header-cell__element"></div>
  <span class="ds-table-header-cell__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-table-header-cell__label">Текст</span>
  <div class="ds-table-header-cell__text-ui"></div>
</div>
```

#### Table header row `[53556:3571]` — 1 вариантов
**Описание и рекомендации по применению:**
Шапка таблицы — строка с названиями колонок, закреплена при прокрутке.  
Собирается из ячеек Table header cell; порядок колонок должен совпадать с порядком в строках данных.
- **State** (VARIANT): Default
- Прочие свойства: Header#59320:28 (SLOT)
- Размеры и параметры:
    - высота: минимум `var(--ds-size-9x)`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - скругление: `var(--ds-table-row-header-border-radius-top-left)`
    - рамка: `1px solid var(--ds-color-stroke-default, #e0e0e0)`
    - фон: `var(--ds-color-table-row-header-background-header, #f0f5ff)`
- Разметка:

```html
<div class="ds-table-header-row">
  <span class="ds-table-header-row__label">Текст</span>
</div>
```

#### Как собрать таблицу целиком (Table)
Любая таблица собирается из полос и ячеек этого семейства, сверху вниз: шапка → строки → подстрока 2-го уровня → футер (если есть итоги). Правила:

- **Шапка**: полоса `ds-table-header-row`, внутри — только ячейки `ds-table-header-cell` (текст — `__label`). Рамку, фон и скругление несёт полоса; ячейка прозрачна и без рамки. В выгрузке рамка/фон есть у обеих (двойные швы — известный пробел №1, обход в `fixes.css` п. 22). Закрепление при прокрутке — `position: sticky` на полосе шапки (обвязка страницы).
- **Строки**: полоса `ds-table-content-row`, внутри — ячейки `ds-table-content-cell`. Текст ячейки — `__label`; контролы (чекбокс, статус, кнопка) — в слот `__element` (внутрь — Element cell или сам компонент). Состояния полосы: `:hover` — в css; `--zebra` (чередование фона) и `--selected` (выделение записи) — классы из `fixes.css` п. 22 (в выгрузке только токены `--ds-color-table-row-content-*`).
- **Ширина колонок** задаётся на ячейках (свои классы обвязки, напр. `w-280`); порядок ячеек в строке = порядок колонок в шапке.
- **Ячейка-ссылка** — `ds-table-content-cell--link` (Accent; классы `--link`/`--focus`/`--edit`/`--error` — `fixes.css` п. 22, в ДС пока нет — №3). Пустое значение — прочерк «—» текстом (State=Null).
- **2-й уровень** (состав блюда, позиции документа): подстрока `ds-table-2-lvl--table-row-2-lvl` из подъячеек `ds-table-2-lvl--table-cell-2-lvl`; подъячейка — две полосы `ds-table-2-lvl__header-row` подряд (верх — 1 ячейка, низ — 2). Css — `UI-Components_DS/table-2-lvl.css`.
- **Футер**: `ds-table-footer` одним блоком под строками (итоги по колонкам).
- ⚠️ В выгрузке полосы свёрстаны колонкой (`flex-direction: column`) — без обхода `fixes.css` п. 22 строку из ячеек не собрать (пробел №4, чинится в ДС).

Скелет разметки (шапка + строка + подстрока):

```html
<div class="w-table">
  <div class="ds-table-header-row">
    <div class="ds-table-header-cell w-c1"><span class="ds-table-header-cell__label">Колонка 1</span></div>
    <div class="ds-table-header-cell w-c2"><span class="ds-table-header-cell__label">Колонка 2</span></div>
  </div>
  <div class="ds-table-content-row">
    <div class="ds-table-content-cell w-c1"><span class="ds-table-content-cell__label">Значение</span></div>
    <div class="ds-table-content-cell w-c2"><span class="ds-table-content-cell__label">Значение</span></div>
  </div>
  <div class="ds-table-2-lvl ds-table-2-lvl--table-row-2-lvl">
    <div class="ds-table-2-lvl ds-table-2-lvl--table-cell-2-lvl w-c1">
      <div class="ds-table-2-lvl__header-row">
        <div class="ds-table-header-cell"><span class="ds-table-header-cell__label">Деталь</span></div>
      </div>
      <div class="ds-table-2-lvl__header-row">
        <div class="ds-table-header-cell"><span class="ds-table-header-cell__label">Значение</span></div>
      </div>
    </div>
  </div>
  <div class="ds-table-content-row ds-table-content-row--zebra">…</div>
</div>
```

Живой пример полной сборки — демо-стенд `components/Table_DS/demo.html` (вкладка «Пример сборки»).

#### Tabs `[54854:3052]` — 4 вариантов
**Описание и рекомендации по применению:**
Вкладки — переключение разделов одного экрана без перезагрузки: «Общие», «Товары», «История».  
Берите их, когда разделов 2–7 и они равнозначны; для вложенной навигации — второй уровень вкладок.  
Активная вкладка подчёркнута; названия пишите коротко, без многоточий.  

Состав: строка вкладок из Tab element, при нехватке места — стрелки прокрутки (Scroll tabs).  

Как выбрать вариант:  
Lvl=1 — основные разделы экрана; Lvl=2 — вложенные разделы внутри раздела.  
Content=Text — с текстом; Icon — только иконки, когда раздел понятен по иконке.
- **Lvl** (VARIANT): 1, 2
- **Content** (VARIANT): Icon, Text
- Прочие свойства: Content text m#58420:0 (SLOT), Content icon m#58420:5 (SLOT), Content text s#58420:10 (SLOT), Content icon s#58420:15 (SLOT), Scroll left#59422:17 (BOOLEAN), Scroll right#59422:22 (BOOLEAN)
- CSS: выверено вручную, см. `components/index.css`

#### Text UI `[57938:18290]` — 7 вариантов
**Описание и рекомендации по применению:**
Текст интерфейса — подпись, значение или ссылка в ячейках, списках и карточках.  
Берите его, чтобы текст в однотипных местах совпадал по размеру и цвету; заголовки страниц и блоков набирайте стилями типографики.  
Лежит на странице UI components (раздел «не готовы или под вопросом») — перед использованием уточните актуальность у владельца ДС.  

Состояния: Default, Link, Hover, Press, Selected, Negative, Disable.
- **State** (VARIANT): Default, Disable, Hover, Link, Negative, Press, Selected
- Прочие свойства: Element left#54167:1 (BOOLEAN), Element right#54167:6 (BOOLEAN), Label up#54741:15 (BOOLEAN), Label down#54741:30 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `52px`, растёт по контенту
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-list-item-gap, 8px)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
- Состояния: `:disabled` (неактивно)
- Разметка:

```html
<div class="ds-text-ui ds-text-ui--disabled">
  <div class="ds-text-ui__checkbox"></div>
  <div class="ds-text-ui__content"></div>
  <span class="ds-text-ui__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-text-ui__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-text-ui__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-text-ui__icon-size"></div>
  <span class="ds-text-ui__label">Текст</span>
  <div class="ds-text-ui__label-down"></div>
  <div class="ds-text-ui__label-up"></div>
  <div class="ds-text-ui__list-item"></div>
</div>
```

#### Textarea `[57916:9023]` — 13 вариантов
**Описание и рекомендации по применению:**
Многострочное поле — длинный текст: комментарий к заказу, примечание к накладной, описание позиции.  
Берите его, когда ответ не помещается в одну строку; для короткого значения используйте Input.  

Состав: Label над полем, само поле с прокруткой, support-текст под полем (подсказка или ошибка).  
Высоту задавайте под ожидаемый текст, растягивать вручную не нужно.  

Как выбрать вариант:  
Variant=Empty — поле без текста; Populated — с введённым текстом.  
Состояния: Default, Hover, Focus, Focus+Placeholder, Focus+Value, Error, Error+Hover, Disable.
- **Size** (VARIANT): M
- **Variant** (VARIANT): Empty, Populated
- **State** (VARIANT): Default, Disable, Error, Error+Hover, Focus, Focus+Placeholder, Focus+Value, Hover
- Прочие свойства: Input text#52678:0 (TEXT), Label text#52678:3 (TEXT), Support text#52678:6 (TEXT), Label#56934:32 (BOOLEAN), Element left#56934:282 (BOOLEAN), Element right#56934:407 (BOOLEAN), Support text#56934:532 (BOOLEAN), Input text#56968:66 (BOOLEAN), Hint text#57893:0 (BOOLEAN), Support#57893:30 (BOOLEAN), Hint text#57893:60 (TEXT), Scroll#57994:0 (BOOLEAN)
- Размеры и параметры:
    - высота: минимум `96px`, растёт по контенту
    - ширина: `250px` (фикс.)
    - промежуток между элементами: `var(--ds-form-field-gap-input-support, 4px)`
- Модификаторы (что меняет каждый):
    - `--disabled`: pointer-events `none`
    - `--empty`: color `var(--ds-color-form-field-filled-disable-input-text-color, #9e9e9e)`, color `var(--ds-color-form-field-input-label-text-color, #616161)`
    - `--populated`: color `var(--ds-color-form-field-filled-disable-label-text-color, #9e9e9e)`, color `var(--ds-color-form-field-filled-default-label-text-color, #616161)`
- Состояния: `:disabled` (неактивно), `:focus-visible`, `:hover` (наведение)
- Разметка:

```html
<div class="ds-textarea ds-textarea--disabled">
  <span class="ds-textarea__element-left"><!-- иконка: material-icons по имени --></span>
  <span class="ds-textarea__element-right"><!-- иконка: material-icons по имени --></span>
  <span class="ds-textarea__hint">Текст</span>
  <span class="ds-textarea__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-textarea__input-content"></div>
  <div class="ds-textarea__input-frame"></div>
  <span class="ds-textarea__label">Текст</span>
  <div class="ds-textarea__scroll"></div>
  <span class="ds-textarea__support">Текст</span>
  <span class="ds-textarea__text">Текст</span>
</div>
```

#### Timepicker `[58982:9858]` — 2 вариантов
**Описание и рекомендации по применению:**
Выбор времени — список или сетка часов и минут: время доставки, начало смены.  
Открывается из поля времени (Input Timepicker); отдельно на экране не живёт.  

Как выбрать вариант:  
Type=Time line — список времени одной колонкой, прокруткой.  
Type=Time grid — сетка значений, когда нужен быстрый выбор круглых значений.
- **Type** (VARIANT): Time grid, Time line
- Прочие свойства: Slot Time#58983:4 (SLOT), Control Panel#58983:7 (SLOT), Scroll#58983:10 (BOOLEAN)
- Размеры и параметры:
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `var(--ds-size-2x) 0 var(--ds-size-2x) 0`
    - скругление: `var(--ds-size-3x)`
    - рамка: `1px solid var(--ds-color-stroke-default, #e0e0e0)`
    - фон: `var(--ds-color-brand-neutral-default, #ffffff)`
    - тень: `var(--ds-shadow-shadows-08-dp-s)`
- Модификаторы (что меняет каждый):
    - `--time-grid`: направление `column`, align-items `center`, color `var(--ds-color-text-primary, #333333)`
    - `--time-line`: направление `row`, color `var(--ds-color-text-primary, #333333)`
- Разметка:

```html
<div class="ds-timepicker ds-timepicker--time-grid">
  <div class="ds-timepicker__control-panel"></div>
  <span class="ds-timepicker__icon"><!-- иконка: material-icons по имени --></span>
  <span class="ds-timepicker__label">Текст</span>
  <div class="ds-timepicker__scroll"></div>
</div>
```

#### Tree `[59564:1473]` — 8 вариантов
**Описание и рекомендации по применению:**
Дерево — иерархический список с раскрытием: группы товаров, склады, оргструктура.  
Берите его, когда у записей есть вложенность; для плоского перечня используйте List.  

Как выбрать вариант:  
Level — уровень вложенности ветки.  
Mode=Middle — ветка в середине уровня; End — последняя ветка уровня.  
For icon=On — с местом под иконку у ветки; Off — без него.
- **Level** (VARIANT): 2, 3
- **Mode** (VARIANT): End, Middle
- **For icon** (VARIANT): Off, On
- Размеры и параметры:
    - высота: `44px` (фикс.)
    - ширина: `fit-content` (фикс.)
    - промежуток между элементами: `var(--ds-size-2-5x)`
- Модификаторы (что меняет каждый):
    - `--2`: направление `row`, направление `column`, align-items `center`
    - `--3`: направление `row`, align-items `center`
- Разметка:

```html
<div class="ds-tree ds-tree--2">
  <span class="ds-tree__icon"><!-- иконка: material-icons по имени --></span>
  <div class="ds-tree__item"></div>
  <div class="ds-tree__separator-stroke"></div>
</div>
```

#### Tree item `[59564:1504]` — 5 вариантов
**Описание и рекомендации по применению:**
Линия связи в дереве — соединяет ветку с родителем и показывает, продолжается ли уровень.  
Служебный элемент дерева: ставится внутрь ветки, отдельно на экран не выносится.  

Как выбрать вариант: по месту ветки в уровне и длине связи.
- **Mode** (VARIANT): End, End-long, Middle, Middle-long, Start
- Размеры и параметры:
    - высота: `44px` (фикс.)
    - ширина: `fit-content` (фикс.)
    - внутренние отступы: `0 0 var(--ds-size-5x) 11px`
    - промежуток между элементами: `var(--ds-size-2-5x)`
- Модификаторы (что меняет каждый):
    - `--end`: направление `row`, align-items `center`, ширина `48px`, направление `column`
    - `--end-long`: ширина `48px`, направление `column`, внутренние отступы `0 0 21px 11px`
    - `--middle`: направление `row`, align-items `center`, внутренние отступы `0 0 0 11px`, ширина `48px`
    - `--middle-long`: ширина `48px`, направление `row`, align-items `center`, внутренние отступы `0 0 0 11px`
    - `--start`: ширина `var(--ds-size-6x)`, направление `row`, align-items `center`, внутренние отступы `0 var(--ds-size-3x) 0 11px`
- Разметка:

```html
<div class="ds-tree-item ds-tree-item--end">
  <div class="ds-tree-item__separator-stroke"></div>
</div>
```

### Карта классов CSS-библиотеки

Готовые стили для **всех компонентов** ДС лежат в `components/index.css` (сгенерировано из Figma, все значения — токены). Паттерн: контейнер `.ds-<компонент>` + модификаторы вариантов `--<значение>` + элементы `__label` / `__icon`.

**✓ выверено по узлам Figma вручную** (размеры, шрифты, состояния сняты поштучно): Button, Input, Checkbox, Radio button, Badge, Tabs (Lvl 1/2), Divider, Banners, Card view (+header/content/footer), Expansion panel (+content), Stepper (+Step), Slide toggle. Остальные — сгенерированы автоматически: цвета/размеры/радиусы на токенах верные, структура упрощённая (при первом использовании стоит сверить с макетом).

**Подключение стилей** — одной строкой `<script src="https://iiko-ds.github.io/DS/connect.js" defer></script>` (подробнее — документ «Подключение DS»); отдельные css-файлы лежат в репозитории — ссылки в разделе [CSS и токены в файлах библиотеки](#css-и-токены-в-файлах-библиотеки).

| Компонент | Класс | Модификаторы |
|---|---|---|
| Arrow | `.ds-arrow` |
| Arrow list | `.ds-arrow-list` |
| Arrow menu | `.ds-arrow-menu` |
| Arrow select | `.ds-arrow-select` |
| Autocomplete form | `.ds-autocomplete-form` · `--empty` `--populated` `--empty` `--populated` `--populated` `--empty` `--empty` `--populated` `--populated` `--disabled` · :disabled, :focus, :hover |
| Backdrop | `.ds-backdrop` |
| Button toggle | `.ds-button-toggle` · `--s` `--xs` `--filled` `--outlined` `--outlined` `--filled` |
| Checkbox label | `.ds-checkbox-label` · `--normal` `--normal` `--normal` `--error` `--error` `--error` `--disable` `--disable` `--disable` |
| Chips | `.ds-chips` · `--s` `--s` `--outlined` `--outlined` `--outlined` `--outlined` `--outlined` `--outlined` `--filled` `--filled` `--filled` `--filled` `--filled` `--disabled` · :active, :disabled, :focus, :hover |
| Chips group | `.ds-chips-group` · `--s` |
| Chips Input | `.ds-chips-input` · `--s` `--s` `--disabled` · :disabled, :focus, :hover |
| Chips Input | `.ds-chips-input-2` · `--s` `--disabled` · :disabled, :focus, :hover |
| Chips input cell | `.ds-chips-input-cell` · `--disabled` · :disabled, :focus, :hover |
| Control arrow button | `.ds-control-arrow-button` · `--s` |
| Control Panel | `.ds-control-panel` · `--control` `--week` `--calendar` |
| Control Panel | `.ds-control-panel-2` · `--control` `--time` |
| Datepicker | `.ds-datepicker` · `--day` `--year` `--month` |
| Dialog content | `.ds-dialog-content` |
| Dialog footer | `.ds-dialog-footer` |
| Dialog header | `.ds-dialog-header` · `--text` |
| Dialog view | `.ds-dialog-view` |
| Element | `.ds-element` · `--image-size` `--icon-size` `--icon-group` `--text-default` `--checkbox` `--radio-button` `--indicator` `--slide-toggle` `--counter` |
| Element cell | `.ds-element-cell` · `--icon-size` `--icon-group` `--button` `--button-icon` `--status` `--text-ui` `--input-number` `--checkbox` `--slide-toggle` `--chips` `--cell-input` |
| Element Form Field | `.ds-element-form-field` · `--input-cell` `--select-cell` `--chips-input-cell` |
| Element left | `.ds-element-left` |
| Element menu | `.ds-element-menu` · `--image-size` `--icon-size` `--text-default` `--checkbox` `--radio-button` `--indicator` `--slide-toggle` `--counter` |
| Element select | `.ds-element-select` · `--image-size` `--icon-size` `--text-default` `--checkbox` `--radio-button` `--indicator` `--slide-toggle` `--counter` |
| Element sidenav | `.ds-element-sidenav` · `--collaps-icon` `--avatar` |
| Element step | `.ds-element-step` · `--icon-size` `--counter` `--counter` `--counter` `--counter` `--counter` `--disabled` · :active, :disabled, :hover |
| Elementare cell | `.ds-elementare-cell` · `--icon-size` `--icon-group` `--button` `--button-icon` `--status` `--text-ui` `--input-number` `--checkbox` `--slide-toggle` `--chips` |
| Elements | `.ds-elements` · `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--cell` `--year` `--cell` `--cell` `--year` `--year` `--year` `--year` `--year` `--year` `--year` `--year` `--year` `--year` `--month` `--month` `--month` `--month` `--month` `--disabled` · :active, :disabled, :hover |
| Elements | `.ds-elements-2` · `--selected` `--default` `--default` `--default` `--default` `--default` `--disabled` · :active, :disabled, :hover |
| Expansion content | `.ds-expansion-content` · `--true` `--false` |
| Expansion group panel | `.ds-expansion-group-panel` · `--collaps` `--expand` |
| Form field cell | `.ds-form-field-cell` |
| Hint container | `.ds-hint-container` · `--up` `--down` `--right` `--left` `--default` |
| Hint content | `.ds-hint-content` · `--group-content` `--single-content` |
| Hint footer | `.ds-hint-footer` · `--default` |
| Hint header | `.ds-hint-header` · `--neutral` `--primary` `--secondary` `--warning` `--error` |
| Icon group | `.ds-icon-group` · `--4x` |
| Input cell | `.ds-input-cell` · `--disabled` · :disabled, :focus, :hover |
| Input Datepicker | `.ds-input-datepicker` · `--empty` `--populated` |
| Input number | `.ds-input-number` · `--s` `--xs` `--xs` `--populated` `--empty` `--populated` `--populated` `--empty` `--populated` `--populated` `--empty` `--empty` `--disabled` · :disabled, :focus, :hover |
| Input number_but icon | `.ds-input-number-but-icon` |
| Input Timepicker | `.ds-input-timepicker` · `--empty` `--populated` |
| List (Сontainer) | `.ds-list-container` · `--container` |
| List item | `.ds-list-item` · `--disabled` · :active, :disabled, :hover |
| Logo iiko | `.ds-logo-iiko` |
| Logo Syrve | `.ds-logo-syrve` |
| Menu (Container) | `.ds-menu-container` · `--container` |
| Menu item | `.ds-menu-item` · `--disabled` · :active, :disabled, :hover |
| Picture | `.ds-picture` |
| Radio button label | `.ds-radio-button-label` · `--normal` `--normal` `--error` `--error` `--disable` `--disable` |
| Scroll | `.ds-scroll` · `--s` `--first` `--middle` `--middle` `--last` · :hover |
| Scroll tabs | `.ds-scroll-tabs` · `--left` |
| Search | `.ds-search` · `--s` `--s` `--xs` `--xs` `--disabled` · :disabled, :focus, :hover |
| Select (Сontainer) | `.ds-select-container` · `--container` |
| Select cell | `.ds-select-cell` · `--disabled` · :disabled, :focus, :hover |
| Select form | `.ds-select-form` · `--s` `--xs` `--empty` `--populated` `--empty` `--populated` `--populated` `--empty` `--empty` `--populated` `--populated` `--disabled` · :disabled, :focus, :hover |
| Select item | `.ds-select-item` · `--true` `--false` `--false` `--false` `--false` `--false` `--disabled` · :active, :disabled, :hover |
| Sidenav control | `.ds-sidenav-control` · `--collapsed` `--collapsed` `--expanded` `--expanded` `--expanded` `--collapsed` · :active, :hover |
| Sidenav Footer | `.ds-sidenav-footer` · `--l2` `--l1` `--l1` |
| Sidenav header | `.ds-sidenav-header` · `--l1` `--l2` `--l1` |
| Sidenav item | `.ds-sidenav-item` · `--l3` `--l3` `--l2` `--l2` `--l1` `--l1` `--l1` `--l1` · :hover |
| Sidenav View | `.ds-sidenav-view` |
| Snackbar | `.ds-snackbar` · `--single` `--single` `--complex` `--complex` |
| State | `.ds-state` · :active, :hover |
| Status | `.ds-status` · `--neutral` `--accent` `--positive` `--warning` `--negative` `--contrast-1` `--contrast-2` `--contrast-3` `--contrast-4` `--neutral` `--accent` `--positive` `--warning` `--negative` `--contrast-1` `--contrast-2` `--contrast-3` `--contrast-4` |
| Table 2 lvl | `.ds-table-2-lvl` · `--table-cell-2-lvl` `--table-row-2-lvl` |
| Table Chips Input | `.ds-table-chips-input` · `--default` `--hover` `--focus` `--focus-placeholder` `--vocus-value` `--error` `--error-hover` `--disable` |
| Table content cell | `.ds-table-content-cell` · `--disabled` · :disabled, :hover |
| Table content row | `.ds-table-content-row` · `--disabled` · :disabled, :hover |
| Table footer | `.ds-table-footer` · `--default` |
| Table header cell | `.ds-table-header-cell` · `--disabled` · :disabled, :hover |
| Table header row | `.ds-table-header-row` |
| Text UI | `.ds-text-ui` · `--disabled` · :disabled |
| Textarea | `.ds-textarea` · `--populated` `--populated` `--empty` `--empty` `--populated` `--populated` `--empty` `--populated` `--empty` `--disabled` · :disabled, :focus, :hover |
| Timepicker | `.ds-timepicker` · `--time-grid` `--time-line` |
| Tree | `.ds-tree` · `--2` `--2` `--3` `--3` `--2` `--2` `--3` `--3` |
| Tree item | `.ds-tree-item` · `--end` `--end-long` `--middle` `--middle-long` `--start` |

#### Ручные (выверенные по Figma) файлы — их классы

Эти компоненты сняты с узлов Figma поштучно и живут в отдельных файлах (`button, input, selection, selection-icons, badge, navigation, card, expansion, stepper, toggle`). Имена классов КОРОЧЕ имени компонента в Figma — писать в разметке именно их.

| Класс | Модификаторы | Элементы |
|---|---|---|
| `.ds-btn` | `--accent` `--disabled` `--filled` `--m` `--negative` `--neutral` `--outlined` `--positive` `--s` `--text` `--warning` `--xs` | `__icon` `__label` |
| `.ds-btn-group` | `--horizontal` `--margins` `--vertical` | — |
| `.ds-btn-icon` | `--accent` `--disabled` `--m` `--negative` `--neutral` `--outlined` `--positive` `--s` `--text` `--warning` `--xs` | `__icon` |
| `.ds-btn-icon-group` | `--vertically` | — |
| `.ds-input` | `--disabled` `--error` `--m` `--s` `--xs` | `__content` `__field` `__frame` `__hint` `__icon` `__label` `__stepper` `__support` `__support-row` |
| `.ds-checkbox` | `--disabled` `--error` | `__box` `__input` `__label` `__support` |
| `.ds-radio` | `--disabled` `--error` | `__box` `__input` `__label` `__state` `__support` |
| `.ds-checkbox-wrap` | — | — |
| `.ds-checkbox-group` | `--horizontal` `--vertical` | — |
| `.ds-radio-group` | `--horizontal` `--vertical` | — |
| `.ds-badge` | `--accent` `--counter` `--negative` `--point` `--positive` `--warning` | — |
| `.ds-tabs` | `--lvl2` | — |
| `.ds-tab` | `--active` `--disabled` | `__counter` `__icon` |
| `.ds-divider` | `--dashed` `--disable` `--l` `--lite` `--m` `--selected` | — |
| `.ds-divider-line` | `--dashed` `--disable` `--lite` `--selected` | — |
| `.ds-banner` | `--accent` `--horizontal` `--negative` `--neutral` `--positive` `--vertical` `--warning` | `__buttons` `__icon` `__row` `__text` |
| `.ds-field-label` | — | — |
| `.ds-card` | `--custom` `--filled` `--outlined` `--shadow` | `__content` `__divider` `__footer` `__footer--right` `__footer__action` `__header` `__label-down` `__label-up` `__title` |
| `.ds-expansion` | `--disabled` `--info` `--open` | `__actions` `__arrow` `__content` `__content--no-padding` `__header` `__icon` `__title` |
| `.ds-stepper` | — | `__divider` |
| `.ds-step` | `--bg` `--disabled` `--error` `--selected` | `__icon` `__num` |
| `.ds-stepper-button` | — | `__counter` `__group` |
| `.ds-slide-toggle` | `--disabled` `--error` | `__icon` `__input` `__row` `__support` `__title` `__track` |

### Иконки (Google Material Icons)

Иконки — **Google Material Icons**, вставляются **по имени** (а не SVG-кодом), поэтому разметка компактная, а иконки одинаковые у всех прототипов. Пришли из файла иконок ДС (Figma `skjpVJUl8ir0JazrrPAMOW`), имена совпадают с набором Google Material.

**Подключение** (один раз в `<head>` прототипа):
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
```

**Вставка по имени**, цвет наследуется от текста (`currentColor`):
```html
<span class="material-icons">add</span>
```
Иконку вставляйте туда, где ей место: внутрь `.ds-btn__icon` / `.ds-btn-icon__icon` / `.ds-input__icon`.

Иконки берём **любые из Google Material Icons** — обязательного списка имён нет.
Каталог с именами (отсюда подставляем имя): https://fonts.google.com/icons
Как устроены иконки в Material: https://m3.material.io/styles/icons/overview

Имена в файле иконок ДС совпадают с Google Material (например `schedule_time` → `schedule`, `arrow_left/right` → `arrow_back/forward`) — подбираем подходящее имя из каталога. Размер иконки — как у иконочного слота компонента: обычно 20 px (`Icon size/Size 5x`); где слот задаёт 16 (например Button icon XS) — оставляем 16 по токену компонента.

### Бренд-иконка iiko (SVG, не Material)

Логотип iiko — **не Material**, вставляется SVG-кодом (цвет `currentColor`):

```html
<svg width="20" height="20" viewBox="0 0 169 72" fill="none" xmlns="http://www.w3.org/2000/svg"> <g clip-path="url(#clip0_55332_22289)"> <path d="M142.121 27.4503C125.935 27.4503 115.721 35.7723 115.721 49.5734C115.721 63.3744 125.935 71.6712 142.121 71.6712C158.308 71.6712 168.521 63.3491 168.521 49.5734C168.521 35.7976 158.282 27.4503 142.121 27.4503ZM142.121 59.5548C137.728 59.5548 137.626 53.9089 137.626 49.5734C137.626 45.2378 137.723 39.5666 142.121 39.5666C146.519 39.5666 146.58 45.2125 146.58 49.5734C146.58 53.9342 146.514 59.5548 142.121 59.5548Z" fill="currentColor"/> <path d="M20.0802 28.4165H1.73282C1.14173 28.4165 0.662552 28.8922 0.662552 29.4789V69.6324C0.662552 70.2191 1.14173 70.6948 1.73282 70.6948H20.0802C20.6713 70.6948 21.1505 70.2191 21.1505 69.6324V29.4789C21.1505 28.8922 20.6713 28.4165 20.0802 28.4165Z" fill="currentColor"/> <path d="M20.0802 9.87015H1.73282C1.14173 9.87015 0.662552 10.3458 0.662552 10.9325V22.9325C0.662552 23.5193 1.14173 23.9949 1.73282 23.9949H20.0802C20.6713 23.9949 21.1505 23.5193 21.1505 22.9325V10.9325C21.1505 10.3458 20.6713 9.87015 20.0802 9.87015Z" fill="currentColor"/> <path d="M48.6869 28.4165H30.3395C29.7484 28.4165 29.2692 28.8922 29.2692 29.4789V69.6324C29.2692 70.2191 29.7484 70.6948 30.3395 70.6948H48.6869C49.278 70.6948 49.7571 70.2191 49.7571 69.6324V29.4789C49.7571 28.8922 49.278 28.4165 48.6869 28.4165Z" fill="currentColor"/> <path d="M48.6869 9.87015H30.3395C29.7484 9.87015 29.2692 10.3458 29.2692 10.9325V22.9325C29.2692 23.5193 29.7484 23.9949 30.3395 23.9949H48.6869C49.278 23.9949 49.7571 23.5193 49.7571 22.9325V10.9325C49.7571 10.3458 49.278 9.87015 48.6869 9.87015Z" fill="currentColor"/> <path d="M99.6825 48.0506C99.3002 47.4536 99.341 46.6897 99.7691 46.1282L111.338 31.1332C112.199 30.0253 111.394 28.4216 109.988 28.4216H91.1815C90.626 28.4216 90.096 28.6948 89.7851 29.1551L78.69 45.2175H78.3434V11.5599C78.3434 10.629 77.584 9.87521 76.6463 9.87521H59.5832C58.6454 9.87521 57.8861 10.629 57.8861 11.5599V69.0051C57.8861 69.9359 58.6454 70.6897 59.5832 70.6897H76.6463C77.584 70.6897 78.3434 69.9359 78.3434 69.0051V50.2007H78.69L89.6475 69.8246C89.9431 70.3609 90.519 70.6897 91.1356 70.6897H110.925C112.256 70.6897 113.071 69.2277 112.363 68.1045L99.6723 48.0455H99.6774L99.6825 48.0506Z" fill="currentColor"/> <path d="M133.595 11.2766C134.456 12.4098 135.618 13.2293 136.668 14.1956C137.876 15.3288 139.134 16.8364 139.038 18.5565C138.971 19.3457 138.691 20.0337 138.243 20.6863C137.636 21.597 136.933 22.371 136.184 23.1096C135.46 23.8128 135.48 24.9815 136.224 25.6644H136.209L137.31 26.6813C138.003 27.3187 139.094 27.3035 139.766 26.6408C140.169 26.2412 140.567 25.8213 140.944 25.4014C141.015 25.4975 141.097 25.5936 141.193 25.6745H141.188L142.305 26.6863C143.008 27.3238 144.088 27.2985 144.761 26.6358C145.164 26.2361 145.561 25.8263 145.938 25.4064C146.005 25.5025 146.081 25.5936 146.173 25.6695H146.168L147.258 26.6712C147.962 27.3086 149.042 27.2884 149.725 26.6206C150.388 25.968 151.035 25.3002 151.611 24.5818C152.182 23.8584 152.589 22.973 152.849 22.1332C153.068 21.511 153.043 20.7572 152.977 20.0944C152.91 19.5329 152.661 18.8752 152.375 18.3693C151.774 17.2361 150.79 16.2041 149.847 15.3187C148.522 14.0894 147.156 13.1231 146.428 11.3676C146.208 10.8668 146.045 10.2041 146.045 9.67286C146.015 9.01518 146.142 8.44351 146.392 7.85161C146.896 6.59191 147.702 5.63576 148.655 4.79596C149.419 4.10793 149.429 2.90894 148.67 2.20574L147.615 1.21417C146.953 0.596972 145.923 0.576736 145.24 1.15852C144.807 1.52783 144.379 1.91232 143.997 2.35751C143.976 2.37775 143.956 2.41316 143.93 2.43846C143.864 2.35751 143.803 2.27151 143.721 2.19562L142.666 1.20405C142.009 0.586854 140.995 0.566618 140.296 1.13829C139.843 1.51771 139.41 1.90726 139.012 2.35245C138.992 2.37269 138.961 2.4081 138.941 2.43846C138.875 2.35245 138.803 2.27151 138.722 2.19056L137.667 1.199C137.004 0.581795 135.975 0.561559 135.292 1.14335C134.859 1.51265 134.43 1.89714 134.048 2.34233C132.754 3.7538 131.734 5.79259 132.091 7.77572C132.31 9.03542 132.82 10.2243 133.61 11.2563L133.595 11.2664V11.2766ZM141.397 7.86679C141.555 7.4823 141.759 7.12817 141.968 6.78921C141.953 7.12817 141.968 7.46206 142.019 7.80102C142.238 9.06072 142.748 10.2496 143.538 11.2816C144.399 12.4148 145.561 13.2344 146.601 14.2007C147.809 15.3339 149.068 16.8415 148.976 18.5616C148.91 19.3508 148.629 20.0388 148.181 20.6914C148.13 20.7724 148.074 20.8331 148.023 20.914C148.023 20.6358 148.023 20.3626 148.002 20.0944C147.936 19.5329 147.686 18.8752 147.401 18.3693C146.8 17.2361 145.78 16.2041 144.873 15.3187C143.512 14.0894 142.182 13.1231 141.433 11.3676C141.244 10.8668 141.086 10.2041 141.051 9.67286C141.02 9.01518 141.148 8.44351 141.397 7.85161V7.86173V7.86679ZM136.433 7.85667C136.591 7.46206 136.79 7.11299 136.999 6.76392C136.984 7.10793 136.984 7.45195 137.04 7.79596C137.259 9.05566 137.799 10.2445 138.559 11.2766C139.445 12.4098 140.582 13.2293 141.632 14.1956C142.84 15.3288 144.098 16.8364 144.002 18.5565C143.971 19.3457 143.655 20.0337 143.242 20.6863C143.176 20.7723 143.115 20.8533 143.054 20.9444C143.054 20.656 143.038 20.3575 143.013 20.0843C142.947 19.5228 142.697 18.8651 142.412 18.3592C141.81 17.226 140.827 16.1939 139.884 15.3086C138.559 14.0793 137.193 13.113 136.464 11.3575C136.245 10.8567 136.082 10.1939 136.082 9.66274C136.051 9.00507 136.179 8.4334 136.428 7.84149V7.85161L136.433 7.85667Z" fill="currentColor"/> </g> <defs> <clipPath id="clip0_55332_22289"> <rect width="169" height="72" fill="white"/> </clipPath> </defs> </svg>
```

## CSS и токены в файлах библиотеки

Весь css и токены дизайн-системы лежат готовыми файлами в репозитории `DS` — копировать их в прототип не нужно: стили приезжают одной строкой подключения, а файлы открываются для справки.

Подключение в прототипе (одна строка):
```html
<script src="https://iiko-ds.github.io/DS/connect.js" defer></script>
```

Файлы в репозитории `DS` (`components-web/…`):

- Токены — `tokens.css`: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/tokens.css
- Стили и шрифты — `styles.css`, `font.css`; ручные правки — `fixes.css`
- Компоненты — папки `components/<Имя>_DS/`: в каждой css компонента, у многих — `demo.html` с разметкой:
  https://github.com/iiko-DS/DS/tree/main/components-web/components
- Полный перечень css-файлов компонентов — `components/index.css`

Карта, подключение и правила — в документе «Подключение DS»:
https://github.com/iiko-DS/Prototypes/blob/main/prototyping-guide/подключение-ds.md

## Чек-лист соответствия ДС

- [ ] Все цвета, размеры, радиусы — только `var(--ds-*)`, без хардкода
- [ ] Кнопки: класс `ds-btn` + размер (`--xs/--s/--m`) + стиль (`--accent/--neutral/--positive/--negative/--warning`) + тип (`--filled/--outlined/--text`)
- [ ] Одна accent-кнопка на область, negative — экономно
- [ ] Иконки — Material Icons по имени внутри `.ds-btn__icon` / `.ds-btn-icon__icon` / `.ds-input__icon`, цвет через `currentColor`
- [ ] Input: размер из набора M/S/XS, лейбл только у M
- [ ] Checkbox/Radio: иконки-глифы 20×20, цвета из компонентных токенов
- [ ] Badge: Counter или Point, стиль из 4 вариантов
- [ ] Шрифт Roboto 400/500, размеры из токенов типографики