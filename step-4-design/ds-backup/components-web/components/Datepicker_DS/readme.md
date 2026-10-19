# Datepicker / Input Datepicker — компоненты ДС

Календарь дизайн-системы в трёх видах, как в Figma (узел 58509-5439, Type=Day / Year / Month):
сетка дней (выбор **одного дня** кликом, **диапазона** — вторым), вид по годам (4×3) и по месяцам
(3×4) — переключаются пилюлей «месяц год ⌄»; листание месяцев «‹ ›» (только в виде дней).
Плюс сборка «Input Datepicker» (узел 58548-4764; float-модель лейбла — по примерам
«Datepicker (Examples)» 58987-16573): поле даты + выпадающий календарь.

## Файлы в папке и кто их пишет

| Файл | Кто пишет | Что это |
|---|---|---|
| `datepicker.css`, `control-panel.css`, `elements.css`, `input-datepicker.css` | генератор Фигма→CSS | вид компонента (не правим, обновления перезаписывают) |
| `datepicker.js` | **ручной** (генератор не трогает) | поведение + разметка: `Datepicker.mount` (календарь), `Datepicker.mountInput` (сборка с полем) |
| `demo.html` | **ручной** | демо-стенд с табами (компонент Tabs ДС): 1) Basic example, 2) Input Datepicker (Empty/Populated), 3) Elements Datepicker, 4) Control Panel Datepicker, 5) Datepicker (Day/Year/Month) — порядок как в Фигме |
| `readme.md` | **ручной** | этот файл |

Ручные правки поверх генерации — в `../../fixes.css`: раздел «Datepicker» (п. 9–11: фон/hover
выбранных ячеек и пилюли, композиция сетки и строки недели, разделитель, opacity выключенных
ячеек, space-between панели Control) и раздел «Input Datepicker» (п. 12: выпадашка,
float-модель лейбла «Выберите дату», размер иконки). Журнал находок — `DS/fixes.md` (№75, 77–81).

## Подключение

```html
<link rel="stylesheet" href="../DS/components-web/components/index.css">   <!-- включает css дейтпикера и поля -->
<script src="../DS/components-web/components/Datepicker_DS/datepicker.js" defer></script>
<!-- плюс ручной слой последним: -->
<link rel="stylesheet" href="../DS/components-web/fixes.css">
```

Иконка `date_range` — глиф Material Icons Outlined (токен ДС `--ds-input-datepicker-icon`).
Табы демо-стенда — компонент ДС Tabs (`ds-tabs`, `ds-tab`, `ds-tab--active`); переключение панелей — скрипт стенда.

## Использование

### Календарь (`Datepicker.mount`)

```js
var cal = Datepicker.mount(document.getElementById('cal'), {
  start: new Date(2026, 0, 10),   // необязательно: начальное начало
  end:   new Date(2026, 0, 20),   // необязательно: начальный конец (если равен start — один день)
  mode:  'day',                   // необязательно: стартовый вид — 'day' | 'year' | 'month'
  onPick: function (s, e) {       // вызывается на каждый клик: s,e — Date
    console.log(Datepicker.fmtD(s), Datepicker.fmtD(e));
  }
});

cal.view(new Date(2026, 1, 1));   // показать другой месяц (вид снова — сетка дней)
cal.set(new Date(2026, 2, 1), new Date(2026, 2, 5));   // задать выделение программно
cal.reset();                      // начать выбор заново (следующий клик — новый один день)
```

### Поле даты (`Datepicker.mountInput`)

```js
var dp = Datepicker.mountInput(document.getElementById('dp'), {
  value: new Date(),   // необязательно: начальная дата (вариант Populated)
  open:  false,        // необязательно: открыть календарь сразу
  onPick: function (s) { console.log(Datepicker.fmtFull(s)); }
});
```

Лейбл поля — «Выберите дату» (`label`): в покое стоит в строке ввода (серый), при фокусе
или значении всплывает наверх (в фокусе — акцентный #448AFF); формат-плейсхолдер «ДД.ММ.ГГГГ»
(`placeholder`) виден только при вводе — как в примерах Figma «Datepicker (Examples)».

Поведение: календарь открывается по иконке справа; выбор дня подставляет дату в поле
(формат `ДД.ММ.ГГГГ`, `Datepicker.fmtFull`) и закрывает выпадашку; Esc и клик снаружи закрывают;
дату можно набрать руками (значение не парсится). Форматы: `fmtFull` — `ДД.ММ.ГГГГ` (поле),
`fmtD` — `ДД.ММ.ГГ` (подписи шапки приложения).

Поведение кликов в календаре: 1-й клик — один день (в подписи без тире), 2-й — диапазон;
одиночный день рисуется **без** подсветки диапазона. Виды дня/года/месяца сверены с узлом
58509-5439 (пилюля «месяц год ⌄»: день → год → месяц → день) и уходят в сборку «Input Datepicker».

Ещё не реализовано (делаем при необходимости): недоступные даты (стиль `--disabled` есть,
логики блокировки нет), показ двух месяцев, парсинг ручного ввода даты.
