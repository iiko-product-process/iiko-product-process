# components-mobile

Папка внутри репозитория `DS`. Мобильный слой дизайн-системы iiko: всё, что относится к планшету и телефону.

## Структура

```
components-mobile/
├── modes.css                  ось режима (размер): [data-mode="mobile"]
├── components/                только CSS компонентов (как в components-web)
│   └── index.css              агрегатор мобильного слоя
├── prototypes/                страницы-прототипы (как в Prototypes)
│   └── button-modes.html      демо: Desktop и Mobile рядом + замеры из браузера
├── desktop-to-mobile-plan.md  план перевода компонентов ДС на мобилу
├── desktop-to-mobile-plan.xlsx
├── mobile-mode-notes.md       архитектура переменных: режимы и темы
├── mobile-workflow.md         регламент для дизайнеров
├── mobile-steps.md            тот же процесс по шагам
└── mobile-block-schemes.md    схемы процесса
```

Правило структуры то же, что в `components-web`: один компонент — одна папка
`components/<Имя>_DS/`. Здесь лежат только те файлы, которые существуют
**на мобиле иначе**: структурные `*_mob`-компоненты (другая раскладка или
состав — шторка снизу, липкий футер, вертикальная группа кнопок).

## Что здесь НЕ дублируется

- **База токенов.** Она одна — `components-web/tokens.css` (1743 переменные из
  Figma). Копия в этом репозитории разошлась бы с оригиналом при первом же
  обновлении ДС.
- **Компоненты, которые на мобиле отличаются только размерами** (Button,
  Input, Toggle, List и т. д.). Это те же файлы в `components-web/components/`;
  мобильные размеры для них задаёт `modes.css`. Так же устроена и Figma:
  режим `Mobile` создаётся **у коллекции переменных**, а не у компонента.

## Как эта папка лежит внутри DS

`components-web` и `components-mobile` — папки одного репозитория `DS`: страницы-прототипы
ходят к ним по относительным путям, имена папок менять нельзя. Клонируется и обновляется
всё сразу вместе с `DS`. Прототипы экранов — отдельный репозиторий `Prototypes` рядом
с папкой `DS`. Порядок клонирования и первые команды — в readme репозитория `DS`.

## Как подключить

```html
<link rel="stylesheet" href="../components-web/font.css">
<link rel="stylesheet" href="../components-web/tokens.css">
<link rel="stylesheet" href="../components-mobile/modes.css">             <!-- ось размера -->
<link rel="stylesheet" href="../components-mobile/components/index.css">  <!-- мобильные *_mob -->
<link rel="stylesheet" href="../components-web/components/index.css">
```
и на корне экрана — атрибут режима:

```html
<html data-mode="mobile">
```

Порядок важен: `modes.css` обязан идти после `tokens.css` (специфичность у
`[data-mode="mobile"]` и `:root` одинаковая, решает очерёдность).

## Проверка

Открыть `prototypes/button-modes.html` — там десктоп и мобила стоят
рядом на одной странице (в Figma так нельзя: режим глобальный на файл) и есть
таблица замеров, снятых из браузера: высота, паддинги, кегль, иконка, тач-зона.

Ожидаемые высоты: Desktop M 36 / S 28 / XS 24, Mobile M 44.
