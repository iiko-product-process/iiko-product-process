# Подключение DS — как собрать прототип

Это единственная точка входа: подключение, карта и правила — здесь. Прочитай сам — или просто
отправь ссылку на эту страницу своему ИИ со словами «собери прототип, используя нашу ДС»:
дальше он сделает всё по этой инструкции. Подробная справочная база по компонентам —
спецификация в репозитории `DS` (ссылка в карте ниже).
«ДС» — дизайн-система iiko: компоненты (классы `ds-*`), токены и организмы.

## Ничего скачивать не нужно

Твой прототип — обычная HTML-страница, которая лежит у тебя где угодно. Она **ссылается на наши
файлы на GitHub** (прямыми ссылками): ни папок рядом, ни скачиваний, ни копий не нужно.

## Подключение — одна строка

В страницу добавляется одна строка — ссылка на наш подключатель в GitHub:

```html
<script src="https://iiko-ds.github.io/DS/connect.js" defer></script>
```

Она сама подтянет всё, что нужно:

- стили дизайн-системы и все компоненты;
- иконки Material Icons;
- **демо-страница прототипа — контейнер, плашка (общий заголовок раздела, «Экраны», «Размер»),
  хедер (с правой панелью) и сайднав: подключается сразу, автоматически** — на странице их
  не собирать, не копировать и не подключать отдельно; эталон и живой пример — `demo-connect.html`
  (ссылки ниже).
- **демо-контент в прототипе не остаётся — только свой** (заказчик, 16.10.2026: «остаётся только
  чисто свой контент… демо-контент должен исчезнуть, удалиться»): демо-страница идёт как
  шаблон-подложка; взяв её, всё содержимое шаблона — контент, экраны, пункты селекта «Экраны»,
  демо-примеры — заменяем своим, а демо-контент удаляем. В готовой странице — только контент юзера.

## Компоненты, токены, css — бери из репозитория

Ничего не выдумывать: всё лежит в репозитории `DS`, у каждого компонента — своя папка
со своим исходником. Карта (ссылки машиночитаемые — ИИ открывает их напрямую):

- **Каталог всех компонентов** — `components-web/components`, по папке на компонент:
  https://github.com/iiko-DS/DS/tree/main/components-web/components · машинный список:
  https://api.github.com/repos/iiko-DS/DS/contents/components-web/components
- **В папке каждого компонента**: `*.css` — все его классы и состояния; у многих — `demo.html`,
  живой пример правильной разметки. Пример (Button):
  https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Button_DS/button.css ·
  https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Button_DS/demo.html
- **Токены** (цвета, отступы, размеры):
  https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/tokens.css
- **Стили и шрифты**: `styles.css`, `font.css` — в той же папке `components-web/`.
- **Спецификация** — справочная база по всем компонентам (описания, варианты, разметка, css —
  одним большим файлом); открывай, когда нужна глубина — для обычной сборки хватает папок выше:
  https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/iiko-ds-spec.md

## Карта демо-стендов

У компонентов из списка ниже в папке есть `demo.html` — **живой стенд**: правильная разметка,
все состояния и примеры сборок (повторяет набор Figma). Собираешь такой компонент — сверяйся
по этому стенду (ссылки машиночитаемые, ИИ открывает их напрямую):

- Autocomplete: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Autocomplete_DS/demo.html
- Backdrop: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Backdrop_DS/demo.html
- Badge: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Badge_DS/demo.html
- Banners: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Banners_DS/demo.html
- Button: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Button_DS/demo.html
- Button icon: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Button-Icon_DS/demo.html
- Button toggle: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Button-Toggle_DS/demo.html
- Card: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Card_DS/demo.html
- Checkbox: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Checkbox_DS/demo.html
- Chips: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Chips_DS/demo.html
- Chips input: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Chips-Input_DS/demo.html
- Datepicker: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Datepicker_DS/demo.html
- Dialog: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Dialog_DS/demo.html
- Divider: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Divider_DS/demo.html
- Expansion panel: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Expansion-Panel_DS/demo.html
- Form field input: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Form-Field-Input_DS/demo.html
- Hint tooltip: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Hint-Tooltip_DS/demo.html
- Icon size: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Icon-Size_DS/demo.html
- Input number: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Input-Number_DS/demo.html
- List: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/List_DS/demo.html
- Logo: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Logo_DS/demo.html
- Menu: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Menu_DS/demo.html
- Radio button: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Radio-Button_DS/demo.html
- Scroll: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Scroll_DS/demo.html
- Search: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Search_DS/demo.html
- Select: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Select_DS/demo.html
- Sidenav: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Sidenav_DS/demo.html
- Slide toggle: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Slide-Toggle_DS/demo.html
- Snackbar: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Snackbar_DS/demo.html
- Status: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Status_DS/demo.html
- Stepper: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Stepper_DS/demo.html
- Table: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Table_DS/demo.html
- Tabs: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Tabs_DS/demo.html
- Textarea: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Textarea_DS/demo.html
- Timepicker: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Timepicker_DS/demo.html
- Tree: https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/Tree_DS/demo.html
- UI components (Text UI): https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/components/UI-Components_DS/demo.html

Организмы (сборки уровня приложения) — у каждого свой стенд (`demo.html`) и readme; папка
`organisms/<имя>`: https://github.com/iiko-DS/DS/tree/main/organisms

- **приходят сами** с демо-страницей (на странице их не собирать): `app-header` (шапка),
  `app-sidenav` (боковое меню), `app-right-panel` (правая панель — шторка шапки);
- **подключаются вручную по своему readme** (через `connect.js` не приходят — нужны не каждой
  странице): `app-header-content` — шапка раздела, `app-table-header-actions` — полоса над
  таблицей, `app-page-footer` — подвал страницы и таблицы, `app-table-card-adaptive` — карточка
  строки таблицы в адаптиве. Readme — с точными путями подключения и разметкой:
  - https://raw.githubusercontent.com/iiko-DS/DS/main/organisms/app-header-content/readme.md
  - https://raw.githubusercontent.com/iiko-DS/DS/main/organisms/app-table-header-actions/readme.md
  - https://raw.githubusercontent.com/iiko-DS/DS/main/organisms/app-page-footer/readme.md
  - https://raw.githubusercontent.com/iiko-DS/DS/main/organisms/app-table-card-adaptive/readme.md

Теперь demo.html есть у **всех компонентов** (батчи A–E, 10.2026) — если компонента нет в списке выше,
смотри спецификацию; состав и состояния также фиксировались в журнале ДС `fixes.md` (батчи A–E —
№115–135; дальше сверки стендов по Figma — до №190).

## Что писать на странице

Интерфейс собирается из компонентов ДС — классами `ds-*`. Например, кнопка:

```html
<button class="ds-btn ds-btn--m ds-btn--accent ds-btn--filled" type="button">
  <span class="ds-btn__label">Сохранить</span>
</button>
```

Правила коротко:

- классы и варианты компонентов — только из их исходников в репозитории ДС (карта выше:
  css и demo.html каждого компонента, токены; там же спецификация); ничего не выдумывать —
  чего нет в ДС, того нет;
- **референс может быть любым** — текст задачи, скриншоты, ссылка на Balsamiq, Figma-макет:
  состав, порядок и тексты берём из него; каждый элемент собираем из компонентов ДС,
  спорное сверяем по `demo.html` и спецификации; стили референса не копируем;
- свои стили — только для раскладки (колонки, отступы контекста); внешний вид компонентов
  не переписываем: **как выглядит — только из ДС**;
- **ширина — по блоку**: каждый компонент растягивается по ширине блока, в котором стоит
  (поле, чипы, карточка, панель — на всю ширину колонки/контейнера, а не по содержимому);
  ширину задаёт блок раскладки;
- **ширина Select-контейнера не равна ширине поля** (заказчик, 19.10.2026): выпадающий список
  может быть любой ширины и не обязан совпадать с Select-формой — даже у компактного поля (XS/S)
  список можно делать шире, по содержимому пунктов; ширины поля и списка задаются независимо;
- **больше одного атома — ищи групповой компонент** (заказчик, 15.10.2026): 2+ однотипных
  элемента (кнопки, чипы, иконки-кнопки…) собираем через групповой компонент ДС (кнопки —
  `ds-btn-group`, чипы — `ds-chips-group`), зазор — токеном группы, свой `gap`/`margin` не
  задавать; если группового компонента в ДС нет — между атомами всё равно обязателен отступ
  (gap из токенов ДС);
- **select container — «Title select» и «Поиск» по умолчанию не выводим** (заказчик, 16.10.2026):
  инпут размера M — «Title select» не выводим, размера S — показываем; поиск в контейнере — только
  если значений больше 12; по умолчанию поиска нет;
- **реальные компоненты и паттерны поведения — как в Material Design / Angular Material** (заказчик,
  19.10.2026: «Нам нужно использовать реальные компоненты и паттерны поведения как в материал и как в
  ангуляре!»): контрол собираем по реальному паттерну (M3 Select/Chips/Combobox/Menu/Dialog; Angular
  Material — `mat-select`, `mat-autocomplete`, `mat-chip-grid`, `MatDialog`): состав, состояния, клавиатура,
  закрытие; Визуал/токены — из ДС, Material/Angular — источник паттернов поведения; нет единого компонента
  в ДС — композиция из компонентов ДС по тому же паттерну (пример: мультиселект с чипами = Chips Input +
  Select container + Checkbox в `element-left` у каждого пункта; «Выбрать все» — отдельный пункт с Checkbox);
- **фильтр таблицы — в полосе таблицы** (заказчик, 16.10.2026): фильтр, относящийся только к таблице,
  размещается в полосе таблицы (header table actions), не в шапке страницы; **справа в полосе — только
  кнопки и иконки действий** (селект — не кнопка), слева — заголовок и настройки отображения
  (группировки, тумблеры); размер элемента в полосе — не больше её высоты (36): у селекта брать размер
  S (у Select form M 48 / S 36 / XS 28);
- **колонка действий строки фиксируется только при наведении** (заказчик, 19.10.2026: «фикс только
  при наведении, а не всегда»): действия строки скрыты до наведения; при наведении/фокусе строки её
  колонка прижимается к правому краю видимой области (sticky, `right: 0`) с фоном строки (#F5F5F5;
  выбранная — Accent/5 #F8F9FC), чтобы текст не просвечивал под иконками; в покое колонка обычная —
  без фона, тени и разделителя («белого столба» нет). Правило ДС `background:transparent` у ячейки
  при наведении не должно снимать фон у `t-c-actions` — нужен `:not(.t-c-actions)`;
- **всё, что есть в примере, работает** (заказчик, 19.10.2026): диалог/панель открывается и
  закрывается (крестик, Esc, кнопка действия, клик по затемнению Backdrop); если есть скролл —
  контент реально прокручивается, ползунок Scroll перетаскивается и синхронизирован;
  контролы живые, картинкой их не показываем;
- текст и заголовки вне компонентов — только шрифт ДС (Roboto 400/500); системные шрифты
  браузера не оставляем (у голого `<h1>` по умолчанию — Times). Пресеты типографики — токены ДС,
  например: `font: var(--ds-font-header-s-20-normal-medium); letter-spacing: var(--ds-font-header-s-20-normal-medium-spacing);`
- иконки — Material Icons по имени: `<span class="material-icons">search</span>`.
- **все демо-страницы компонентов собираем только по слоям и настройкам Figma** (заказчик, 19.10.2026):
  перед сборкой/правкой вкладки — дерево слоёв + Properties (вариант, размер, состояние, слоты,
  вложенные инстансы, скрытые слои); вложенные инстансы — компонентами ДС, не голыми svg.

## Пример страницы целиком

```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Мой прототип</title>
  <script src="https://iiko-ds.github.io/DS/connect.js" defer></script>
</head>
<body>
  <div style="padding: 24px;">
    <button class="ds-btn ds-btn--m ds-btn--accent ds-btn--filled" type="button">
      <span class="ds-btn__label">Кнопка ДС</span>
    </button>
  </div>
</body>
</html>
```

Открой файл в браузере — страница уже с хедером и меню: они пришли сами.

Живой пример такой страницы — `demo-connect.html` в репозитории `Prototypes`:
открыть: https://iiko-ds.github.io/Prototypes/demo-connect.html
машиночитаемый исходник для ИИ:
https://raw.githubusercontent.com/iiko-DS/Prototypes/main/demo-connect.html

## Если собираешь с ИИ

Дай агенту ссылку на эту страницу и опиши задачу. Обязательная часть задачи: **агент идёт
в репозиторий ДС и забирает компоненты оттуда** (карта выше) — открывает папки нужных
компонентов, классы берёт из их css, разметку сверяет по demo.html, значения — из tokens.css.
Классы не выдумывать: например, `ds-button` в ДС нет — кнопка это `ds-btn`; чего нет
в репозитории ДС, того нет и на странице. Хедер и меню агент не собирает — они приходят сами.
Важно: у ИИ должен быть доступ в интернет — без него он не сможет открыть ссылки.
Если чат не открывает GitHub-страницу — дай ему прямую (raw) ссылку на этот же документ:
https://raw.githubusercontent.com/iiko-DS/Prototypes/main/prototyping-guide/подключение-ds.md

## Дальше

- каталог компонентов (css и demo.html каждого — бери оттуда):
  https://github.com/iiko-DS/DS/tree/main/components-web/components
- спецификация всех компонентов (классы, варианты, состояния):
  https://raw.githubusercontent.com/iiko-DS/DS/main/components-web/iiko-ds-spec.md
- правила применения компонентов (что можно и нельзя при сборке):
  https://raw.githubusercontent.com/iiko-DS/Prototypes/main/prototyping-guide/дизайн-система/сборка-из-ДС.md
- отступы и компоновка экранов (контент-зона 20/30/24, заголовки H1–H3, карточки):
  https://raw.githubusercontent.com/iiko-DS/Prototypes/main/prototyping-guide/дизайн-система/принципы-группировки-контента.md
- остальная база знаний — в этом же репозитории.
