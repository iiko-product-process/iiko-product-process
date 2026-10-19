# Шторки на страницах рекомендаций: заглушки → разметка компонента (15.09.2026)

На страницах `iiko-ds-mobile/prototypes/recommendations/<slug>.html` шторка (`.phone__sheet`
внутри `preview_html`) у части компонентов была нарисована не собой: либо строками списка с
Material-иконкой в слоте слева, либо простыми строками `.phone__row`. Задача владельца —
перерисовать шторки разметкой самого компонента. Сперва Checkbox и Radio (14.09), затем
восьмёрка: List, Status, Select, Menu, Card, Badge, Search, Form field (15.09).

## Откуда брать правильную разметку (не выдумывать)

- `data/<slug>.json` → `examples[].html` — примеры самого компонента на этой же странице;
- `patterns_ru[].example_html` — у menu / select / scroll в примерах паттернов уже есть шторка
  (`phone__sheet`) с корректной разметкой: `ds-menu-container`, `ds-select-container` с
  `ds-select-item--true/--false`, `ds-list-container` внутри шторки;
- библиотека: `iiko-ds-web/components/<Имя>_DS/*.css` (классы, токены), мобильный слой —
  `iiko-ds-mobile/components/*` (`select-mobile.css` и `menu-mobile.css` сами растягивают свой
  контейнер на 100 % в `data-mode="mobile"`, у списка такого правила нет).

Что получилось: **List** — `ds-list-container` + `__item` (иконка, `label-up`, `text`,
`ds-list-item__label-down` справа); **Status** — четыре `ds-status--<mod> --filled` в колонке
`gap:16px` (neutral/edit, positive/check_circle, warning/schedule, negative/error); **Select** —
`ds-select-container` с `__search` (`ds-input--s`) и пунктами `ds-select-item`; **Menu** —
`ds-menu-container` + `ds-menu-item` («Опасно» — `label-up`, красный `#FF5252`); **Card** —
`ds-card--outlined` (header `label-up`/`title`/`label-down` + content); footer не дублировать —
в шторке уже есть `.phone__actions`; **Badge** — строки списка со знаком справа (`--counter`,
`--point`); **Search** — поле `ds-search` с введённым значением + прежний список результатов;
**Form field** — `ds-input--m` с `ds-input__label` (значение показывать `placeholder`-ом, как в
теле экрана этого же компонента).

## Правила правки данных

- Менять **только** `preview_html` (и подпись под экраном, если она описывает старую заглушку).
  Проверка: сравнить поля с `git show HEAD:<файл>` — отличаться должен ровно `preview_html`;
  блоки `.phone__body/__head/__status/__foot` — байт-в-байт как в HEAD (сравнивать блоками,
  сбалансированным разбором `<div\b|</div>`).
- Писать JSON **в том же стиле, что файл**: у страниц разный отступ (1 или 2) и перевод строки
  (CRLF/LF) — перебрать `indent ∈ {1,2,4}` × `\r\n|\n` и сверить байты, иначе в diff попадёт весь
  файл. Пример определения стиля: `(json.dumps(d, indent=ind, ensure_ascii=False) + '\n').replace('\n', nl).encode('utf-8') == raw`.
- Шторка в старых данных лежит **двумя копиями** (`data-mode="mobile"` дважды). Вырезать блок
  сбалансированным разбором и заменять `h.replace(old, new)` — обе копии одним действием; перед
  заменой `assert len(set(blocks)) == 1` (копии идентичны).
- Подпись под экраном — тоже проверяемое утверждение: у Card было «в шторке те же строки без
  карточки», у Badge «шторка уведомлений пока без знаков» — после правки врали, переписаны.
- После правки: `python _audit/rec/build.py` (пересобирает все 38 страниц), затем `git status`
  и удаление временных страниц из `_audit/rec/checks/` — владелец не терпит артефактов в репо.

## Проверка картинкой и замерами

- Проверочная страница `_audit/rec/checks/_sheets.html` (удалять после): те же CSS, что в шаблоне
  страницы — `../../../iiko-ds-web/{font,tokens,styles}.css`,
  `../../../iiko-ds-web/components/index.css`, четыре файла checkbox/radio,
  `../../../iiko-ds-mobile/modes.css`, `../../../iiko-ds-mobile/components/index.css`,
  `../../iiko-ds-mobile/prototypes/recommendations/rec.css`, Material Icons с Google — плюс
  `preview_html` компонентов в гриде с `zoom:.52…0.62`. Снять `chrome --headless=new --screenshot`
  и смотреть своим зрением; так же готовится файл-отчёт владельцу (Рабочий стол).
- Замеры без CDP: страница пишет цифры в `<pre id="out">`, запуск `chrome --headless=new
  --dump-dom` и вычитка JSON из вывода. Так измерено: экран 359 px, шторка 359 (внутри 327), а
  `.ds-list-container` — **258 px жёстко в библиотеке** (`.ds-list-item` тоже). Следствие: значения
  и знаки в строках List / Badge / Search не доходят до края шторки на ~69 px, длинные подписи
  переносятся на две строки. Владельцу отдано как «найдено рядом», **не чинил**: в теле экрана
  ровно так же, это ширина библиотеки; растягивать — правка оболочки `rec.css` и вопрос к нему.
- Плашки `ds-status --filled` сверены с примером ДС на той же странице: neutral `#FAFAFA`,
  positive `#F3FCF7`, warning `#FFFCF8`, negative `#FFF8F8`, высота 24 px — совпадает. «Бледно» —
  так задумано ДС, не «чинить».
- `ds-select-item--true` от `--false` отличается только паддингом: явного вида «выбрано» в CSS нет.

## Грабли

- Глобальная замена без проверки контекста: убрал слот `element-left` с иконкой `receipt_long` по
  всему файлу — снялось 12 вхождений вместо 6 (6 строк шторки + 6 строк тела). После такой правки
  сверять тело с HEAD и дописывать назад по признаку (в теле у строки есть `ds-list-item__label-up`).
- Длинную подпись в строке списка не сокращать: она переносится из-за 258 px — либо так, либо
  вопрос владельцу про ширину (см. выше).
- Формулировки владельца понимать буквально, «как у остальных» = те же числа, что у соседних
  элементов: в шторке сверять с телом того же экрана на той же странице.
