# header-content — хедер контента (шапка раздела) — организм

Верхняя строка раздела: стрелка назад, подпись + заголовок, слот «После заголовка» (статус
и/или дополнительный текст), поиск и действия. Источник — компонент **«Header content»**
(63308:202539) Figma «Iiko Web DS (New)», страница «Header content_ORG»; части — компонентами ДС:

- **стрелка назад** — «Icon size» (Size=24, Content=Icon), иконка `arrow_back`;
- **подпись + заголовок** — «Text UI» одним блоком: «Label up» = подпись (Caption L 12, серая),
  «List item text» = заголовок (стиль «Header M (24) / Normal / Medium»);
- **слот «После заголовка»** — «Status» (Style=Accent, Type=Filled) и/или «Text UI»
  (Caption L 12 серым, справа иконка `edit`);
- **поиск** — «Search» (Size=XS, State=Default) — круглая кнопка 36;
- **действия** — «Button group» (Orientation=Horizontally, Margins=Off) из «Button»
  (Size=M, Style=Neutral, Type=Filled).

## Размеры (из компонента)

- высота строки — **48**; стрелка↔заголовок — **16**; заголовок↔слот «После заголовка» — **16**;
  внутри слота — **8**; поиск↔кнопки — **29** (как в компоненте); между кнопками — 8 (Button group/Gap);
- блок растягивается на всю ширину, действия прижаты вправо (space-between);
  подпись — 16, заголовок — 32 (16 + 32 = 48).
- слот «После заголовка» центрируется **по строке заголовка** (24/32) — `align-self: flex-end` + отступ 4
  от низа блока (работает и с подписью, и без неё); так же по строке заголовка центрируется стрелка назад
  (`.hc__back`) — стрелка, заголовок и слот всегда на одной центральной линии;
  при выключенной подписи (тумблер «Подпись») строка схлопывается — заголовок встаёт на место подписи,
  пустого разрыва над ним нет.

## Переключатели (как булевы свойства компонента; дефолт — всё включено)

| Часть | Атрибут на корне |
|---|---|
| Стрелка назад | `data-hc-arrow="off"` |
| Подпись | `data-hc-subtitle="off"` |
| Статус | `data-hc-status="off"` |
| Показ дополнения (текст в слоте) | `data-hc-after="off"` |
| Поиск | `data-hc-search="off"` |
| Кнопки действий | `data-hc-actions="off"` |

Нет атрибута — часть показана. То же самое из js:
`HeaderContent.set(блок, { arrow:false, subtitle:false, status:false, after:false, search:false, actions:false })`.
Если в слоте «После заголовка» / правой части ничего не осталось, они схлопываются целиком
(пустых гэпов не остаётся).

## Подключение

```html
<link rel="stylesheet" href="../Design-System/organisms/app-header-content/header-content.css?v=1">
<script src="../Design-System/organisms/app-header-content/header-content.js?v=1" defer></script>
```

Страницы-прототипы подключают организм по этим путям (через `../Design-System/connect.js` он не приходит —
блок нужен не каждой странице). Ассеты считаются от расположения скрипта, поэтому разметка
работает с любой страницы и при переносе папки.

## Разметка (декларативно)

```html
<header class="hc">
  <div class="hc__left">
    <div class="ds-text-ui hc__title">
      <span class="ds-text-ui__element-left hc__back" role="button" tabindex="0" aria-label="Назад">
        <span class="ds-icon-size ds-icon-size--6x ds-icon-size--state"><img data-hc-icon="arrow-back" width="24" height="24" alt=""></span>
      </span>
      <span class="ds-text-ui__content">
        <span class="ds-text-ui__label-up hc__subtitle">Подзаголовок раздела</span>
        <span class="ds-text-ui__list-item hc__heading">Заголовок раздела</span>
      </span>
    </div>
    <div class="hc__after">
      <span class="ds-status ds-status--accent ds-status--filled hc__status"><span class="ds-status__label">Активная</span></span>
      <span class="ds-text-ui hc__addition">
        <span class="ds-text-ui__content"><span class="ds-text-ui__list-item">с 01.10.2024</span></span>
        <span class="ds-text-ui__element-right"><span class="ds-icon-size ds-icon-size--5x"><img data-hc-icon="edit" width="20" height="20" alt=""></span></span>
      </span>
    </div>
  </div>
  <div class="hc__right">
    <span class="ds-search ds-search--xs hc__search" role="button" tabindex="0" aria-label="Поиск">
      <span class="ds-search__icon"><span class="ds-icon-size ds-icon-size--5x"><img data-hc-icon="search" width="20" height="20" alt=""></span></span>
    </span>
    <div class="ds-btn-group ds-btn-group--horizontal hc__actions">
      <button type="button" class="ds-btn ds-btn--m ds-btn--neutral ds-btn--filled"><span class="ds-btn__icon"><img data-hc-icon="add" width="20" height="20" alt=""></span><span class="ds-btn__label">Button</span></button>
      <!-- кнопок столько, сколько нужно странице -->
    </div>
  </div>
</header>
```

- Заголовок/подпись — любые тексты; статус — любой вариант «Status» ДС (в примерах «Активная»
  и «Черновик»); дополнение — любой текст (или вместо него другой контент слота);
  кнопки — «Button» ДС (основное действие — крайнее справа, как в ДС).
- Ненужные части можно просто не размечать (или выключить атрибутом `data-hc-*="off"`).

## Правила

- Клики не заданы: стрелка назад, поиск и кнопки — действия страницы, обработчики вешает она.
  Скрипт организма делает только две вещи: подставляет иконки (`img[data-hc-icon]` → SVG из этой
  папки) и переключает части (`HeaderContent.set`). На демо-стенде, чтобы блок был «рабочим»,
  поиск раскрывается в поле Search S полным составом варианта (лупа + текст + «Right icon»:
  разделитель и search_off; при вводе — крестик): живой ввод, «✕» очищает, Esc/клик мимо
  сворачивают — это стендовая механика, организм кликов не задаёт.
- Иконки — точные SVG из Figma (`icon-arrow-back.svg` 24; `icon-search.svg` / `icon-edit.svg` /
  `icon-add.svg` / `icon-close.svg` / `icon-search-off.svg` 20; цвет #616161 = Icon/Primary);
  глифы не заменять Material-шрифтом (крестик и search_off — для раскрытого поиска на стенде).
- Демо стенд — `demo.html`: живой блок с тумблерами (как свойства компонента) + конфигурации
  из фрейма «Header контента — примеры использования».
- Правки — только здесь; что добавлено «от себя» — помечено в коде меткой «пробел ДС».

## Пробелы ДС (локальные обводки)

- **Search XS** — в сгенерированном `search.css` у `--xs` наследуются фон/рамка размеров M/S
  (#F8F9FC, рамка #E0E0E0), а в наборе у XS фон Accent/50 (ховер — Accent/100) и рамки нет;
  обводка живёт здесь, в `.hc__search` (в клоне репозитория продублирована в `components-web/fixes.css`).
- **Text UI в контексте хедера** — артбордные `min-height: 52` и гэп 8 в хедере заменяются
  на 48 и 16 (значения из компонента) — обвязка организма (`.hc__title`, `.hc__addition`).
