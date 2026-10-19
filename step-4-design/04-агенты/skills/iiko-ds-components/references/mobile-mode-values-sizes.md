# Размерные компоненты (категория «только значения»): числа, формулы, открытые вопросы

Банк для продолжения перевода: что уже снято, откуда взято и чем проверено.
Обновлено 12.09.2026: Button (все размеры), Button icon (все размеры), Button toggle, Stepper, Slide toggle,
Form field, Card, **Checkbox, Radio**, затем **партия 2 (20 страниц в оболочке)**: Textarea, Input number, List,
Expansion panel, Icon size, Badge и пять «без изменений» — Divider, Logo, Backdrop, Status, Scroll.

Источник чисел по мобиле — **только** `DS/_audit/platform/<slug>.json` (рекомендации платформ,
собранные субагентами; поля `sizes[]` с `height_dp`/`width_dp`, `quote`, `source`). Figma по мобильным
не смотрим. Десктопные числа — из `iiko-ds-web/components/<Имя>_DS/*.css`, токенов и спеки.

## Правило: мобильные значения — ВСЕМ размерам, не только базовому

Первая версия перевода подняла до мобильного минимума только M, а S и XS оставила десктопными. Владелец
открыл страницу метро в режиме «Рядом» и сказал: «Нигде ничего не поменялось. Я вижу одинаковые размеры по
многим компонентам как и у десктопа» — и был прав: в мобильной панели иконка-кнопка XS рисовалась 24 × 24,
строка шага 24, то есть десктопными числами.

Что делать с плотными размерами (числа — из собранных рекомендаций, не на глаз):

| Что | Desktop | Mobile | Откуда |
|---|---|---|---|
| Button с текстом, все размеры | M 36 (pad 8/12), S 28 (4/8), XS 24 (4/6) | **44 / 44 / 44** (M 12/16, S 12/16 при строке 20, XS 14/16 при строке 16) | iOS HIG «a button needs a hit region of at least 44x44 pt» + план «минимум для веба — 44 px»; плотности Angular 40/36/32/28 — это не мобильные размеры |
| Button icon, все размеры | M 36 (pad 8, иконка 20), S 28 (4/4/20), XS 24 (4/4/16) | **40 / 40 / 40** (M pad 10, S pad 10, XS pad 12) | дефолт MD3 `--md-filled-icon-button-container-width/height: 40px`, Angular 40 при density 0 |
| Тач-зона кнопок и иконка-кнопок | по контуру элемента | **48** невидимым слоем | MD3 `height: max(48px, 100%)`, Angular `touch-target-size: 48px` / `icon-button-touch-target-size` |
| Строка чекбокса, радио, тумблера | 20 | **48** | MD3 тач-цель 48 (у чекбокса это сам `<input>`), Angular `checkbox-touch-target-size: 48px` |
| Строка шага вертикального степпера | 24 | **48** | план + Angular: у хедера шага `$header-height: 72px`, `$header-minimum-height: 42px`, плотности 72→42 |

Тач-зона 48 у кнопок — невидимый слой (`::after` с `position:absolute; left/top:50%; width/height:100%;
min-width/min-height:48px; transform:translate(-50%,-50%); background:none`), файл
`iiko-ds-mobile/components/Button_DS/button-touch.css`; строки — `Checkbox_DS/checkbox-touch.css`,
`Slide-Toggle_DS/slide-toggle-touch.css`, `Stepper_DS/stepper-vertical.css` (min-height 48). Все они
подключены в `iiko-ds-mobile/components/index.css`. Формулы HUG дают нужную высоту без новых токенов:
Button S 12+12+20 = 44, XS 14+14+16 = 44; Button icon S 10+10+20 = 40, XS 12+12+16 = 40.

Замерено на одной разметке: desktop 36 / 28 / 24 → mobile 44 / 44 / 44 (Button), 40 / 40 / 40 (иконка),
тач-слой `::after` 48 × 48 у каждой; строка чекбокса/радио 20 → 48; строка тумблера 20 → 48;
шаг вертикального степпера 24 → 48. Цена правила: слои соседних кнопок перекрываются, если кнопки стоят
ближе 48 px (как и у Angular, где на плотностях −2/−3 тач-таргет выключается) — открытый вопрос.

## Сводка

| Компонент | Категория | Desktop | Mobile | Откуда мобильное | Файл значений |
|---|---|---|---|---|---|
| Button (M / S / XS) | только размеры | 36 / 28 / 24 | **44 / 44 / 44** + тач 48 | iOS HIG 44, план; исторический M 44 — из `Button_mob` до запрета Figma | `modes.css`, `components/Button_DS/button-touch.css` |
| Button icon (M / S / XS) | только размеры | 36 / 28 / 24 (иконка 20/20/16) | **40 / 40 / 40** + тач 48 | MD3 контейнер 40, Angular density 0 | `modes.css`, `components/Button_DS/button-touch.css` |
| Button toggle | НЕ размеры: надслойка | трек 46 / 38 / 34 | трек 54 у всех (сегменты 44) | собственных чисел нет — сегменты это Button | — |
| Stepper | структура | шаги в строку, строка 24 | шаги в столбик, строка **48** | план (группа C) + Angular «prefer vertical steppers on small screens» | `components/Stepper_DS/stepper-vertical.css` |
| Slide toggle | только размеры | трек 34 × 20, ручка 16, отступ 2 | **52 × 32**, ручка 24, отступ 4, строка **48** | MD3 switch и Angular сходятся на 52×32 и ручке 16/24/28 | `modes.css`, `components/Slide-Toggle_DS/slide-toggle-touch.css` |
| Form field (M / S / XS) | только размеры | 48 / 36 / 28 | **56** / 36 / 28 | MDC Web `$height: 56px` + Angular `form-field-container-height` 56 при density 0 | `modes.css` |
| Checkbox | только размеры | строка 20, маркер 20 | строка **48**, маркер 20 | MD3/Angular тач-цель 48; маркер у платформ 18 (MD3) и без шкалы | `components/Checkbox_DS/checkbox-touch.css` |
| Radio | только размеры | строка 20, маркер 20 | строка **48**, маркер 20 | то же; маркер 20 = ровно MD3 `icon-size: 20px` | `components/Checkbox_DS/checkbox-touch.css` (правило общее) |
| Card | структура | карточка по сетке | одна колонка на всю ширину, размеры те же | мобильных чисел нет ни у одной платформы | — |

## Slide toggle — как получены числа

Платформы (MD3 switch, Angular `mat-slide-toggle`) дают один набор: трек 52 × 32, ручка 16 (unselected) /
24 (selected) / 28 (pressed), state layer 40, тач-таргет 48. В собранных рекомендациях «трек меньше 32 и
ручка вне шкалы 16/24/28» помечены как **не рекомендуемые** — а наш десктоп 34 × 20 как раз такой.
HIG чисел не даёт, но требует switch только в строке списка.

Десктопная геометрия в CSS была числами (34/20/16/2 + `translateX(14px)`). Переведена в формулы,
которые воспроизводят десктоп **и** дают платформенные мобильные числа:

```css
.ds-slide-toggle {                     /* локальные переменные компонента, значения — из токенов */
  --_st-knob: var(--ds-slide-toggle-knob-width);
  --_st-inset: var(--ds-slide-toggle-deselected-pad-left);
  --_st-track-w: calc(var(--_st-knob) * 2 + var(--_st-inset));            /* 34 · мобила 52 */
  --_st-track-h: calc(var(--ds-slide-toggle-pad-top) + var(--_st-knob) + var(--ds-slide-toggle-pad-bottom));  /* 20 · 32 */
}
.ds-slide-toggle__track::after  { left: var(--_st-inset); }              /* выкл: 2 · 4 */
.ds-slide-toggle__input:checked + .ds-slide-toggle__track::after {
  left: calc(100% - var(--_st-knob) - var(--ds-slide-toggle-selected-pad-right));   /* 16 · 24, ход 14 · 20 */
}
.ds-slide-toggle__support { padding-left: calc(var(--_st-track-w) + var(--ds-slide-toggle-gap)); }  /* 42 · 60 */
```

Мобильные токены в `modes.css`: ручка `--ds-size-6x` (24), `pad-top/bottom` `--ds-space-1x` (4),
`deselected-pad-left`/`selected-pad-right` `--ds-space-1x` (4). Трек пересчитывается сам.

Замерено: desktop 34×20, ручка 16 (left 2 → 16), support 42; mobile 52×32, ручка 24 (left 4 → 24), support 60;
цвета в состояниях те же (`#9E9E9E` / `#448AFF` / `#E0E0E0`, ручка `#FFFFFF`). Регрессия git HEAD → текущий:
0 отличий на десктопе (4 состояния).

Открыто: у MD3 ручка растёт при включении и нажатии (16 → 24 → 28), у нас одного размера; hover на тач не гасится.

## Form field — как получены числа

Семейство токенов — **`--ds-form-field-*`** (`--ds-input-number-*`, `--ds-input-datepicker-*` — другие
компоненты). Высоты 48 / 36 / 28 больше не числа: `calc(паддинги + строка ввода)`
(12+12+24 = 48, 6+6+24 = 36, 4+4+20 = 28), поэтому режим трогает только паддинги.

Платформы: MDC Web `$height: 56px`, горизонтальные паддинги 16; Angular `form-field-container-height`
56 при density 0, вертикальный паддинг 16, шкала плотностей 56/52/48/44/40/36 с паддингами 16…6;
ввод везде 1 rem = 16 px; Apple высоту не фиксирует (44 × 44 pt, кегль 17 pt).

Мобильные токены в `modes.css`: M-паддинги `--ds-space-4x` (16) → высота 56. S остаётся 36 (= минимум
Angular при density −5), XS — 28 (такого поля нет ни у одной платформы).

Замерено: desktop M 48 (pad 12), S 36 (6/12), XS 28 (4/8, радиус 0), ввод 16/24 и 14/20 у XS;
mobile M 56 (pad 16), S/XS без изменений. Регрессия: десктоп 0 отличий (10 полей: M с лейблом и без,
S, XS, с иконкой, с поддержкой/подсказкой, error, disabled).

Открыто: XS — кегль ввода 14 px (iOS зумит поле при фокусе, правило «≥ 16 px»); иконка в поле
рендерится 20 px при токене `Form field/[M|S] size/Icon` = 24 px; токены `Form field/Pad support left/right`
(12) в CSS не применяются; hover на тач.

## Checkbox и Radio — единственное мобильное число и главный дефект ДС

Меняется **только нажимаемая строка**: 20 px → 48 px (правило `min-height: 48px` для `.ds-checkbox` и
`.ds-radio` в `components/Checkbox_DS/checkbox-touch.css`). Маркер 20 × 20, подписи 14/20, support 12/16
с отступом 28, отступы групп 8/32, цвета состояний — без изменений.

- MD3: тач-цель 48 dp — это **сам `<input>`** (`input { appearance: none; height: 48px; }`), отступ
  `margin: max(0px, ((48px - container-size) / 2))`; у радио отдельный `.touch-target { width: 48px; height: 48px }`.
  Маркер: чекбокс container 18 dp / обводка 2 / радиус 2, радио `icon-size: 20px`; шкалы large/small нет.
  State layer 40 dp. Состояния: чекбокс снят/выбран/смешанный + error + disabled; радио снят/выбран + disabled.
- Angular Material: `checkbox-touch-target-size: 48px`, `radio-touch-target-size: 48px` (видны на плотностях
  0 и −1, на −2/−3 скрываются), state layer 40 → 36 → 32 → 28.
- iOS HIG: ни страницы Checkboxes, ни Radio buttons нет (404); и то и другое описано только для macOS
  внутри Toggles, без чисел. HIG же советует >5 радио-опций выносить в pop-up button, а «вкл/выкл» — на switch.

**Дефект, найденный 12.09.2026 (исправлен):** агрегатор `iiko-ds-web/components/index.css` импортировал у
Checkbox и Radio **только `*-label.css`**, а `checkbox.css`, `checkbox-icons.css`, `radio.css`,
`radio-icons.css` не подключал никто и ни одна страница в DS. Поэтому `.ds-checkbox` / `.ds-radio`
рендерились без стилей: `display: inline`, без маркера 20 × 20 и без цветов состояний — а `min-height`
у non-replaced инлайн-элемента не действует, отсюда «мобильное правило не применяется». Добавлены 4 импорта;
замер до/после: `display:inline`, маркер 0 → `display:flex`, маркер 20 × 20, цвета `#616161` / `#448AFF` /
`#FF5252` / `#9E9E9E`.

Открыто: у радио подложка состояния `.ds-radio__state` 28 × 28 против state layer 40 у MD3/Angular (вопрос
десктопа, на тач hover не показывается); у выбранного состояния радио комбинатор `+`, у чекбокса `~`
(разъедутся при промежуточном узле); чекбокс без подписи — горизонтальная цель остаётся 20 px.

## Card — мобильных чисел нет вообще

MD3 у карточки даёт только радиус corner-medium 12 dp, обводку 1 dp и иконку 24 dp; токена внутренних
отступов у неё нет. 16 px — это `$mat-card-default-padding` в Angular Material («the standard padding
specified in the Material Design spec»), а `density` у карточки там `()`. Страницы Cards в iOS HIG нет (404).
Поэтому `modes.css` для Card пуст, а единственное мобильное изменение — раскладка (одна колонка, вся
ширина), то есть правило страницы. Токенизировано только совпадающее по значению (радиус 8, рамка 1,
gap шапки 8, типографика заголовка/подписей) — регрессия 0 отличий на 4 типах. Расходящиеся токены
(`Card/Pad left/right` 24 против 16, `Card/Content/Pad top/bottom` 8 против 16, `Card/Header/Pad top` 24
против 16, `Card/Footer/Pad top/bottom` 16 против 4/16) не подставлять — это находки для дизайнера.

## Приёмы проверки, стоившие времени

- **Кэш Chrome на `http://127.0.0.1:8899`.** С общим `--user-data-dir` Chrome отдаёт **старый** CSS:
  прогон показал в мобильной панели 34 × 20 (режим как будто не применился), хотя в `modes.css` токены
  уже были. Лечится свежим профилем (`--user-data-dir=<новый каталог>`) или `?v=<epoch>` в адресе.
  Перед выводом «не применилось» — проверить `getComputedStyle(panel).getPropertyValue('--ds-…-токен')`:
  если токен на панели верный, а размер нет — дело в кэше или в специфичности, а не в токенах.
- **С 12.09.2026 кэш закрыт с двух сторон.** `serve.py` в корне DS отдаёт всё с
  `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` (запускать вместо `python -m http.server`),
  а `build.py` штампует `?v=<max mtime CSS>` в каждую ссылку на CSS и в `src` iframe оболочки. Если владелец
  видит «старые» числа, а замер свежим профилем верный — предложить ему один `Ctrl+Shift+R` (обычная F5
  не перезапрашивает подресурсы) и не спорить.
- **`display` важнее правила.** Прежде чем искать специфичность или кэш, посмотреть `getComputedStyle(el).display`:
  у `inline`-элемента `min-height`/`height` **молча не применяются**, а внутри flex-строки тот же элемент
  становится flex-элементом и высота работает («в одном примере работает, в другом нет»). И до этого —
  проверить, что файл компонента вообще есть в `iiko-ds-web/components/index.css`. Один прогон:
  `scripts/verify-mobile-values.py --component Checkbox_DS --url <страница> --selector .ds-checkbox`.
- **Пробник писать рядом со страницей, а не в `%TEMP%`.** Копия страницы в темп-каталоге ломает
  относительные ссылки на CSS, и замер показывает нестилизованный документ (высоты 21/49, padding 0 при
  реальных 48/56).
- **Геометрия псевдоэлементов** читается `getComputedStyle(el, '::after')` — так измеряются тач-слой
  (`min-height: 48px`) и ручка слайд-тумблера, и результат попадает в тот же JSON замеров.
- **Клик по меню оболочки** проверяется без интерактива: временный файл в самой папке страниц (same-origin),
  внутри — `iframe` на `index.html`, ждём `load`, кликаем `items[2].click()`, читаем `data-slug` активного
  пункта, `iframe.src` и `style.height`, пишем результат в `document.title`, снимаем `--dump-dom`, файл удаляем.
- Регрессия полезна только если в харнессе **перекопирован текущий CSS** (см. SKILL.md) — иначе диф печатает `changed fields: 0`.
- **Скрипты `input.indeterminate` в примерах работают**: HTML примеров вставляется генератором в текст страницы
  (не через `innerHTML`), поэтому `<script>` внутри примера выполняется. Так на странице чекбокса показано
  смешанное состояние.

## Оболочка страниц рекомендаций (index.html)

`_audit/rec/build.py` → `index_page()` собирает оболочку: меню компонентов слева (`nav__item` с `data-slug`,
активный пункт подсвечен), справа `iframe`. Клик меняет `location.hash` (`index.html#<slug>` — прямая ссылка),
на `load` фрейм подгоняет высоту по содержимому и прячет внутри себя ссылку «← Все компоненты».
Меню строится из `data/*.json`, поэтому новый компонент появляется в нём сам после `python build.py`
(сейчас 9: Button, Button icon, Button toggle, Card, Checkbox, Form field, Radio, Slide toggle, Stepper).

Ширина: пользователь попросил «сделай страницу шире» — `.wrap` без ограничения по ширине
(`width:100%; max-width:100%`), сплошной текст («Почему так», «Итог») ограничен ~1100 px
(`.point`, `ul.list`), таблицы и панели — на всю ширину.

Один компонент — одна панель: `panel()` берёт `html` для десктопа и `html_mobile` (если есть) для мобильной
панели; структурные варианты показываются именно так, а не правилом `data-mode`.

Данные страницы: `data/<slug>.json` (`summary_ru`, `changes[]`, `examples[]`, `result_html`) и
`data-tech/<slug>.json` (цитаты платформ с источниками, `verdict.keep/drop/open`, `measured_ru`).
Примеры для Button и Button icon должны показывать **M, S и XS** — иначе изменения плотных размеров
на странице не видно и владелец читает это как «ничего не поменялось». Сейчас в оболочке **20 страниц**.

## Партия 2 — группа «только размеры» (Textarea, Input number, List, Expansion panel, Icon size, Badge)

| Компонент | Desktop | Mobile | Откуда мобильное | Файл значений |
|---|---|---|---|---|
| Textarea | кадр 76 px (фиксированный) | высота не фиксирована, минимум **104** = 3 строки × 24 + паддинги 16/16, растёт при наборе | ни MD3 (`type=textarea` + `rows`, пример `rows="3"`), ни Angular (`cdkTextareaAutosize`), ни Apple (Text view «высота не ограничена») высоту не фиксируют | `components/Textarea_DS/textarea-mobile.css` |
| Input number | поле 48, кнопки «+/−» 36 | поле **56**, кнопки **40** + тач 48 | числа наследуются от поля (MD3 56 dp, Angular 56 при density 0); «+/−» — инстансы Button icon M | высота из формулы в самом компоненте, мобильный файл не нужен |
| List | строка 68 | строка **72** | MD3 lists: one-line 56 / two-line 72 / three-line 88; ведущий/завершающий отступ 16, контейнер 8 — уже совпадали | `components/List_DS/list-mobile.css` |
| Expansion panel | шапка 44 | шапка **48** свёрнутая, **64** раскрытая | только Angular (`$header-height: 48`, раскрытая 64, минимумы 36/48, радиус 12); в MD3 компонента нет, в HIG — disclosure без чисел | `components/Expansion-Panel_DS/expansion-mobile.css` |
| Icon size | глифы 16/20/24, нажатие по контуру | глифы те же, тач-слой **48** у стрелок и state | MD3: иконка 24 в зоне иконочного контрола 48; Angular — единственный размер 24; iOS абсолютных размеров не даёт (44/28 pt) | `components/Icon-Size_DS/icon-size-touch.css` |
| Badge | точка 8, счётчик 18 | **то же** (не меняется) | MD3/Angular дают 6 и 16 и бейдж не является тач-целью; позиции (before/after, above/below) есть только у Angular | — |

- Замеры партии: textarea кадр 94 → 126; числовое поле **48 → 56**, кнопки 36 → 40; строка списка 68 → 72;
  шапка панели 44 → 48/64; стрелка и state 24 × 24 с тач-слоем 48 × 48.
- **Дефект числового поля (исправлен 12.09.2026).** `.ds-input-number__frame { height: 48px }` стоял **без
  `box-sizing: border-box`**, поэтому на экране кадр был **74 px** (48 + паддинги 12/12 + рамка 1/1) — выше
  обычного поля и не по спеке. Лечение: `box-sizing: border-box` + та же формула, что у кадра поля формы
  (`calc(pad-top + pad-bottom + line-height-m)`), тогда десктоп 48, мобила 56 приходят из токенов и отдельный
  мобильный файл не нужен. Тот же content-box у `.ds-textarea__input-frame { height: 76px }` → рендерится 94,
  это учтено в мобильном правиле (height: auto + min-height).
- Находки партии (в «Не решено» на страницах): у `.ds-textarea__field` нет базовых правил в CSS (только
  `--disabled`, стилизуют страницы прототипов); анимация раскрытия панели 150 ms против 225 ms у Angular;
  паддинг шапки 16 против 24; бейдж 8/18 против MD3 6/16; одно- и трёхстрочные строки списка (56/88) не описаны.

## Партия 2 — группа «без изменений» (Divider, Logo, Backdrop, Status, Scroll)

Здесь **страница и есть результат**: CSS не меняется, но «не меняется» обязано быть доказано источником, а не
заявлено. Рабочая формула ответа: числа ДС → что даёт каждая платформа → почему мобильного значения нет.

| Компонент | Числа ДС | Что говорят платформы |
|---|---|---|
| Divider | 1 px (m) / 2 px (l), состояния solid/lite/selected/disable/dashed | MD3 1 px + inset 16 с двух сторон; Angular 1 px + inset 80 слева + атрибут `vertical`; iOS толщин не публикует. Тоньше 1 px — нет ни у кого. Inset и вертикального варианта в ДС нет (находка) |
| Logo | высота 72 px (syrve 70,9) | компонента нет ни в MD3, ни в Angular, ни в HIG — все три 404: это брендбук. 24 px от иконок не переносить; Apple запрещает свои скругления/тени логотипу |
| Backdrop | цвет `--ds-color-backdrop-background`, **прозрачности в CSS нет** | платформы дают scrim **32 %** (MD3 `md.sys.color.scrim`, Angular CDK `cdk-overlay-dark-backdrop`), плюс `prefers-reduced-motion` 1 ms и `forced-colors` 0,6. Расхождение по прозрачности — находка для дизайна, на мобиле не править |
| Status | паддинг 4/6, иконка 16, кегль 12/500, типы neutral…contrast-4 × filled/text | отдельного компонента нет ни у одной платформы → в ДС он составной; якоря — прогресс MD3 48/4 px, `mat-badge` (small 6 px), progress-spinner. Правила: статус не кодировать только цветом, спиннер не подписывать |
| Scroll | ширина 184 (s 8), knob, фон #FAFAFA | скролла как компонента нет ни в MD3 (404 на /components/scroll, /components/scrollbars), ни в HIG; есть только поведение (полоса временная и полупрозрачная) и API у Angular CDK (`cdkScrollable`, virtual scroll) |

Мобильные правила для Scroll (файл `components/Scroll_DS/scroll-mobile.css`): сам `.ds-scroll` **не гасим**
(по брифу плана он не «скрыт», а не используется на мобиле), но прячем системную полосу
(`scrollbar-width: none` + `::-webkit-scrollbar { width:0; height:0 }`) и включаем инерцию
(`-webkit-overflow-scrolling: touch`). Safe-area и вложение прокрутки в прокрутку — правила раскладки, не компонента.

## Харнесс проверки мобильных значений — три капкана

1. **Подключать ОБА мобильных файла.** Тестовая страница, которая линкует только `modes.css` (токены), но
   забыла `iiko-ds-mobile/components/index.css` (агрегатор), молча теряет все `*-mobile.css` и `*-touch.css`:
   замер печатает десктопные числа, и это читается как «правило не применяется» (стоило прогона: список 68
   вместо 72, шапка 44 вместо 48, тач-слой 0 вместо 48). Порядок ссылок: font → tokens → **modes.css** →
   **mobile components/index.css** → styles → web components/index.css.
2. **Не менять разметку между «до» и «после».** Я подменил внутренний элемент числового поля между двумя
   прогонами и получил фальшивую регрессию 74 → 50. Сравниваются только CSS-файлы при неизменном HTML.
3. **Когда измеренная высота не бьётся с документацией — смотреть `box-sizing`, `padding`, `display`.**
   В ДС content-box и border-box идут вперемешку: кадр поля формы `border-box`, кадры числового поля и
   textarea — нет (48 → 74, 76 → 94 на экране). Признак: разница ровно на сумму паддингов и рамки.
