# table-header-actions — полоса над таблицей (шапка таблицы) — организм

Строка над таблицей в контентной части: заголовок раздела (или счётчик выбранного),
слот «После заголовка» (разделитель + тумблер), действия справа. Источник — старая ДС
«Iiko Web DS (Old)»: мастер **«Title actions table»** (8455:19257; варианты `Type=Title` /
`Type=Title+actions`) и копии по разделам — Номенклатура (13014:11189, 13023:14504),
Заказ товаров (4661:9071), Персонал (8402:19671), Конструктор сайта (9441:22975),
Модификаторы (8384:19757), Отчёты (5814:13959). Собрано на компонентах новой ДС:

- **заголовок** — текст стилем «Body M (16) / Normal / Medium» (может быть счётчиком:
  «Выбрано: 2»);
- **слот «После заголовка»** — «Divider» (вертикальный штрих 1×16, #E0E0E0; автоматический —
  показывается, только когда есть и заголовок, и тумблер) + «Slide toggle»
  (трек 34×20 + подпись; стиль подписи — из компонента: Body S 14/20);
- **действия** — «Button» (Size=M, Style=Neutral, Type=Text) и «Button icon» (Size=M, Style=Neutral,
  Type=Text); между группами — тот же вертикальный Divider.

## Размеры (из копий)

- высота строки — **36**; заголовок↔слот «После заголовка» — **16**; внутри слота — **16**;
  подпись тумблера от трека — 8 (даёт компонент Slide toggle); между действиями — **8**;
  разделители — **1×16**; мин. зазор заголовок↔действия — **8**;
- блок растягивается на всю ширину, действия прижаты вправо (space-between).

**Расхождения файла старой ДС (как есть, не выравнивались):** слева паддинг **16** у части
копий (Персонал, Модификаторы), у остальных 0 — в организме не зашит (это паддинг контейнера);
подпись тумблера в Номенклатуре 16/400/24, в «Конструкторе сайта» и Отчётах — 14/400/20 —
в коде взят стиль компонента Slide toggle новой ДС (14/400/20); заголовок в «Конструкторе
сайта» 16/400 вместо 16/500 — в коде стиль «Body M (16) / Normal / Medium».

## Переключатели (как свойства компонента; дефолт — всё включено)

| Часть | Атрибут на корне |
|---|---|
| Заголовок | `data-tha-title="off"` |
| Тумблер (с подписью) | `data-tha-toggle="off"` |
| Действия | `data-tha-actions="off"` |

Нет атрибута — часть показана. То же самое из js:
`TableHeaderActions.set(блок, { title:false, toggle:false, actions:false })`.
Разделитель в слоте «После заголовка» — автоматический, отдельного переключателя у него нет:
показывается, только когда есть и заголовок, и тумблер; без одного из них исчезает сам.
Если в слоте ничего не осталось, он схлопывается целиком (пустых гэпов нет).

## Подключение

```html
<link rel="stylesheet" href="../Design-System/organisms/app-table-header-actions/table-header-actions.css?v=2">
<script src="../Design-System/organisms/app-table-header-actions/table-header-actions.js?v=2" defer></script>
```

Страницы-прототипы подключают организм по этим путям (через `../Design-System/connect.js` он не приходит —
блок нужен не каждой странице). Ассеты считаются от расположения скрипта, поэтому разметка
работает с любой страницы и при переносе папки.

## Разметка (декларативно)

```html
<div class="tha">
  <div class="tha__left">
    <span class="tha__title">Товары</span>
    <div class="tha__after">
      <span class="ds-divider tha__divider"></span>
      <label class="ds-slide-toggle tha__toggle"><span class="ds-slide-toggle__row"><input class="ds-slide-toggle__input" type="checkbox"><span class="ds-slide-toggle__track"></span><span class="ds-slide-toggle__title">Удалённые: 2</span></span></label>
    </div>
  </div>
  <div class="tha__right">
    <button type="button" class="ds-btn-icon ds-btn-icon--m ds-btn-icon--neutral ds-btn-icon--text" aria-label="Вид"><span class="ds-btn-icon__icon"><img data-tha-icon="grid_view" width="20" height="20" alt=""></span></button>
    <span class="ds-divider tha__divider"></span>
    <button type="button" class="ds-btn ds-btn--m ds-btn--neutral ds-btn--text"><span class="ds-btn__icon"><img data-tha-icon="add" width="20" height="20" alt=""></span><span class="ds-btn__label">Добавить товар</span></button>
  </div>
</div>
```

- Заголовок — любой текст (или счётчик); тумблер — «Slide toggle» ДС (подпись можно не размечать —
  тогда останется только трек, как в «Персонале»); подпись тумблера удалённых — со счётчиком:
  «Удалённые: N» (число подставляет страница по своим данным; на стенде — пример «Удалённые: 2»,
  решение владельца 16.10: «показывай цифрой сколько удалённых»); действия — «Button» / «Button icon» ДС
  (основное действие — крайнее справа, как в ДС).
- Ненужные части можно просто не размечать (или выключить атрибутом `data-tha-*="off"`).

## Вариант 2 — «выделение строк» (активные действия с таблицей)

Второй вариант отображения полосы: когда в таблице выбраны строки (чекбоксами или иначе),
страница показывает **вместо** обычной полосы полосу активных действий с выбранным — по Figma
«Централизованное управление киосками», «Title actions table» (2495:9199):

- слева — счётчик «Выбрано: 3» (16.10 — единый формат без сущности: «оставляем только слово Выбрано… это везде так будет»; тот же стиль заголовка) и **сразу за ним крестик очистки**:
  иконка `close` в контейнере `ds-icon-size ds-icon-size--5x ds-icon-size--state` (подложка при
  наведении) внутри `.tha__text-action` (слой «Text default» по Figma — **не кнопка**, без
  кнопочной плашки и паддингов); зазор **8** — только между цифрой и крестиком (группа `.tha__sel`),
  остальные зазоры полосы — родные 16. Текст «Очистить выбор» и Divider в паре — **убраны**
  (решение владельца 16.10: «сделать как во 2 варианте баннеров»);
- справа — «Удалить» (Button Neutral Text с иконкой `delete-negative` — красная **только иконка**,
  текст обычный; сверено пикселями макета), Divider 1×16 и «Добавить» (Button Neutral Text
  с иконкой `add`).

```html
<div class="tha tha--selection">
  <div class="tha__left">
    <span class="tha__sel">
      <span class="tha__title">Выбрано: 3</span>
      <div class="tha__after">
        <button type="button" class="tha__text-action" aria-label="Очистить выбор"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img data-tha-icon="close" width="20" height="20" alt=""></span></button>
      </div>
    </span>
  </div>
  <div class="tha__right">
    <button type="button" class="ds-btn ds-btn--m ds-btn--neutral ds-btn--text"><span class="ds-btn__icon"><img data-tha-icon="delete-negative" width="20" height="20" alt=""></span><span class="ds-btn__label">Удалить</span></button>
    <span class="ds-divider tha__divider"></span>
    <button type="button" class="ds-btn ds-btn--m ds-btn--neutral ds-btn--text"><span class="ds-btn__icon"><img data-tha-icon="add" width="20" height="20" alt=""></span><span class="ds-btn__label">Добавить</span></button>
  </div>
</div>
```

Класс `.tha--selection` — маркер варианта (высота 36; зазор пары «счётчик ↔ крестик» — 8 через
группу `.tha__sel`, остальные — как у варианта 1; сборка — те же классы и компоненты ДС).
Замена полос — дело страницы: она решает, какую полосу показать при каком выделении, и вешает
обработчики на крестик очистки / «Удалить» / «Добавить». Иконки `close` и `delete-negative` лежат
в папке организма; скрипт подставляет их так же, как остальные. На демо-стенде оба варианта
выведены в кадре стопкой (вариант 1 — живой, вариант 2 — пример).

## Правила

- Клики не заданы: тумблер и кнопки — действия страницы, обработчики вешает она.
  Скрипт организма делает только две вещи: подставляет иконки (`img[data-tha-icon]` → SVG из этой
  папки) и переключает части (`TableHeaderActions.set`).
- Иконки — точные SVG из Figma (`add`, `arrow_drop_down`, `grid_view`, `open_with`, `filter_list`,
  `compare_arrows`, `edit`, `content_copy`, `delete`; 20px, цвет #616161 = Icon/Primary);
  глифы не заменять Material-шрифтом.
- Демо стенд — `demo.html`: живой блок с тумблерами (как свойства компонента) + конфигурации
  из разделов старой ДС.
- Правки — только здесь.
