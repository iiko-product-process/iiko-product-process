# Button icon и Button toggle — перевод на компонентные токены

Состояние 11.09.2026 (вечер): десктоп обоих компонентов токенизирован и проверен регрессией,
Button icon получил мобильные 40 px, Button toggle оказался **контейнером над Button**.
Делалось сразу после Button, по тому же методу (`iiko-ds-components`, «Method»).

Итог в двух строках: у Button icon мобильное значение выведено из рекомендаций платформ;
у Button toggle собственных размеров нет вообще — их несут кнопки внутри него.

## Button icon — `iiko-ds-web/components/Button-Icon_DS/button-icon.css`

Все размерные значения переведены на компонентные токены и на квадратный HUG:

```css
width:  calc(var(--ds-button-icon-m-size-pad-left) + var(--ds-button-icon-m-size-pad-right)
             + var(--ds-button-icon-m-size-icon-size));
height: calc(var(--ds-button-icon-m-size-pad-top) + var(--ds-button-icon-m-size-pad-bottom)
             + var(--ds-button-icon-m-size-icon-size));
```

| Размер | Сторона (desktop) | Паддинги | Иконка | Токены |
|---|---|---|---|---|
| M | 36×36 | 8 | 20 | `--ds-button-icon-m-size-*` |
| S | 28×28 | 4 | 20 | `--ds-button-icon-s-size-*` |
| XS | 24×24 | 4 | 16 | `--ds-button-icon-xs-size-*` |

Радиус 8 (`--ds-button-icon-border-radius`), рамка 1 px (`--ds-button-icon-border-size`),
группа — gap 8. Иконка по размеру задаётся **после** общего блока `.ds-btn-icon__icon`, иначе общий
блок перебивает размерные варианты.

### Мобильные значения (сделано — только из рекомендаций, без Figma)

В `iiko-ds-mobile/modes.css`, блок `[data-mode="mobile"]`:

```css
--ds-button-icon-m-size-pad-top/bottom/left/right: var(--ds-space-2-5x);   /* 10px → 10+10+20 = 40 */
```

Откуда 10: **40 dp — единственный размер контейнера, который называют обе платформы**
(`_audit/platform/button-icon.json`): M3/Material Web — `'state-layer-height': 40px`,
`'state-layer-width': 40px`, `'icon-size': 24px` (`tokens/versions/v0_192/_md-comp-icon-button.scss`),
в доке `--md-filled-icon-button-container-width/height | 40px`; Angular Material —
`icon-button-state-layer-size: list.nth((40px, 36px, 32px, 28px, 24px, 24px), $index)`, т.е. 40 на
плотностях 0…−2, а ниже 40 идёт `icon-button-touch-target-display: none`. iOS числовой высоты контейнера
не даёт вовсе — только хит-регион «at least 44x44 pt». Иконка 20 px — наша (у M3 внутри его 40 dp иконка 24).
S и XS на мобиле не берём: меньше 40 dp платформы описывают только с отключённым тач-таргетом.

Проверено замером на странице рекомендаций: desktop 36×36 (pad 8, иконка 20) → mobile 40×40 (pad 10,
иконка 20); у S и XS мобильных отличий нет. Остаётся решением владельца: тач-слой 48×48 отдельным
элементом и выравнивание 40 против 44 у Button (правка одного токена — `--ds-space-3x` вместо `--ds-space-2-5x`).

### Дефект, найденный при токенизации: disabled не применялся

Блок состояний (`.ds-btn-icon:disabled`, `.ds-btn-icon--outlined:disabled`, `…--text:disabled`) стоял в файле
**выше** блоков Style×Type. Специфичность одинаковая (0,2,0), поэтому побеждал порядок, и
`.ds-btn-icon--accent.ds-btn-icon--filled` перебивал disabled — отключённая кнопка выглядела активной
(замерено: `bg #448AFF`, иконка `#FFFFFF` у обеих). Исправлено переносом блока состояний в конец файла,
как это сделано у Button. После правки: disabled `bg #EBEBEB` (`--ds-color-button-neutral-disable` =
`--ds-palette-neutral-100`), иконка `#9E9E9E`, активная без изменений (`bg #448AFF`, текст `#FFFFFF`).

## Button toggle — `iiko-ds-web/components/Button-Toggle_DS/button-toggle.css`

### Структура (главное; я ошибался именно здесь)

Button toggle — **надслойка над Button**: сам компонент это контейнер-трек, а внутри лежат **инстансы**
Button (`.ds-btn`). В Figma слот так и назван — «Button container» [59885:13]. Формулировка владельца:
«Баттон тугл это надслойка по сути над компонентами баттон. Внутри компонента баттон тугл инстансы
компонента баттон».

Следствия для файла компонента:

- у переключателя только геометрия и фон трека: `inline-flex`, `gap` 4, `padding` 4, `border-radius` 12,
  `box-sizing: border-box`, фон/рамка из `--ds-color-button-toggle-*`;
- вид сегмента (фон, рамка, цвет, hover/press/disabled) — целиком Button, со своими токенами;
- `height` треку **не задавать**: высоту дают кнопки внутри, а они растут на мобиле по своему режиму;
- `.ds-button-toggle__label` и `.ds-button-toggle__icon` — артефакты автогена (в контейнерной модели
  содержимое — `.ds-btn__label` / `.ds-btn__icon`); не удалять самому, но и не использовать в разметке;
- разметка: `<div class="ds-button-toggle ds-button-toggle--outlined"><button class="ds-btn ds-btn--m
  ds-btn--accent ds-btn--filled">…</button><button class="ds-btn ds-btn--m ds-btn--neutral ds-btn--text">…</button></div>`.

### Замеры трека (desktop → mobile)

| Что | Desktop | Mobile |
|---|---|---|
| сегмент Button M | 36 px | 44 px — растёт сам, по режиму Button |
| трек, Filled | 44 px | 52 px |
| трек, Outlined (рамка 1 px) | 46 px | 54 px |
| Button S / XS | 28 / 24, трек 36/38 и 32/34 | без изменений |
| отступы трека / gap / радиус | 4 / 4 / 12 px | те же (в `modes.css` своих значений у переключателя нет) |

### Дефекты (не «чинить» молча — это решения владельца)

1. **Размерной шкалы в токенах нет**: в коллекции `Component` только `pad-*` 4 / `gap` 4 / `radius` 12 /
   `outlined-border-size`. Следствия: `--s` — no-op (иконка 20 = как у базового), `--xs` уменьшает только
   иконку, высоту не меняет. Ось Size из Figma (12 вариантов) в CSS не реализована.
2. **На `<button>`-контейнере** остаётся UA-рамка `2px outset`, если модификатор её не сбрасывает.
3. **Фон трека по токенам — `Shapes/Default` = `#FFFFFF`**: на белой поверхности Filled-трек не виден
   вовсе, виден только Outlined (за счёт рамки). Нужен ли треку тон — вопрос к токенам.
4. **Рамка Outlined делает трек на 2 px выше** (44/46, 52/54).
5. **Спека**: у Button toggle в каталоге пустые `sizes_line`/`states_line` (у Button — «Размеры: M (36px),
   S (28px), XS (24px)», «Состояния: default, hover, pressed, disabled, loading»), т.е. оформление этого
   компонента в спеке **не выверено**; автоген-блок CSS в спеке ещё и расходится с репозиторием.

### Отклонённая попытка (чтобы не повторить)

Когда выбранный сегмент вышел белым, я «починил» это подстановкой токенов Button Filled
(`--ds-color-button-accent-filled-*`) и `color: currentColor` лейблу. Владелец: «Что за жесть с баттон тогл.
Он у нас совсем не так оформлен! Ты точно все взял из токенов, стилей и прочее?» — и это была правда:
заливка принадлежит не треку, а кнопке внутри. Откат вернул рендер ровно на токены компонента.
Правило: чужой компонентный токен в оформление не подставлять. Если свои токены дают странный результат —
сказать об этом и спросить, а не выправлять по своему вкусу.

## Как это проверялось

- Регрессия: `git show HEAD:<path>` в temp-папку, две страницы с одним и тем же markup, замер
  (`iiko-ds-components/scripts/headless-measure.py --json …`), сравнение `--diff`. Button icon — 62 замера
  (3 размера × 5 стилей × 3 типа + базовая + disabled + группа); Button toggle — 24 варианта
  (`div` и `button` × Type × Content × 3 размера). **Перед повторным прогоном перекопировать текущий CSS в
  temp-папку** — иначе diff считается против старого снимка и молча даёт `changed fields: 0`.
- Скрытые дефекты видны только на матрице: рендерить компонент и `<div>`-ом (разметка из спеки), и `<button>`-ом
  (UA-рамка). Так нашлись и no-op `--s`, и `36/28/24` вместо `32`.
- Замеры на **сгенерированной** странице рекомендаций: у неё нет `data-measure`, поэтому копия страницы
  кладётся в ту же папку как `_probe_*.html` с внедрённым скриптом, который пишет JSON в `document.title`,
  читается `--dump-dom`, после чего probe-файл удаляется.

## Что с источниками мобильных значений

- **Button icon** — Figma-компонента `_mob` нет (в плане колонка «нет»); числа выведены из
  `_audit/platform/button-icon.json` (40 dp + тач-таргет 48 dp) и собраны из примитивов ДС.
- **Button toggle** — своих мобильных значений не нужно: сегменты — Button и растут по его режиму.
  Колонка `_mob` в плане (`Button toggle_mob` — «Собран») здесь **не используется**: владелец запретил ходить
  в Figma за мобильными числами. Колонка остаётся полезной только как признак «есть/нет отдельный мобильный
  компонент» — и то, если он сам попросит сравниться с Figma.
- Страницы: `iiko-ds-mobile/prototypes/recommendations/{button-icon,button-toggle}.html`, данные —
  `_audit/rec/data{,-tech}/<slug>.json`, генератор — `_audit/rec/build.py`.

## Открытые вопросы (у владельца)

- Button icon: тач-слой 48×48 и выравнивание 40 vs 44 в ряду с Button; иконка 20 против 24 у M3/Angular.
- Button toggle: какой Style и Type у вложенных Button (в примере — Accent Filled выбран / Neutral Text
  остальные); нужен ли треку тон при `#FFFFFF`; рамка +2 px; 40 dp у платформ против наших 52 на мобиле;
  hover на тач не гасится нигде в библиотеке.
- Общее: планшетный проход 768 не сделан ни по Button, ни по этим двум; автоген-блок CSS в спеке надо
  перегенерировать (для всех трёх компонентов).
