# Hover и состояния на тач-устройствах

Нужно, когда на странице/в ответе появляется фраза «поведение на мобиле не меняется»
или когда пользователь спрашивает «а разве на мобиле есть hover?». Один раз он поймал
меня ровно на этом: строка «те же состояния (hover, press, disabled, loading)» была
неверной — hover на тач не показывается.

## Первое: не рассуждать, искать в уже собранных данных

Если рекомендации платформ уже собирались (параллельные субагенты), данные лежат в
`DS/_audit/platform/<slug>.json` и в `DS/_audit/platform/_raw`, `_src` (сырые выгрузки
исходников, имена местами обрезаны — `am_exp...ader.scss`). Правильный порядок действий:
**grep по этим файлам** → только если там нет — идти в первоисточник. Реакция пользователя
на обратное: «У нас же есть уже все данные. Уже все собрано. Ты зачем опять придумываешь
что-то своё?».

```bash
cd DS/_audit/platform && grep -rn -i "hover" --include=*.md --include=*.scss --include=*.ts . | head -40
```

## Второе: что где сказано (проверено)

### Наша библиотека

`grep -rn "hover: hover\|hover: none\|@media" iiko-ds-web/components/ iiko-ds-mobile/modes.css`
→ **ни одного `@media (hover: …)`**. При этом `:hover` и `:active` описаны (например
`.ds-btn--accent.ds-btn--filled:hover` #3969D5 / `:active` #2651B5). Значит в режиме
`data-mode="mobile"` меняются только размеры, а hover остаётся и на тач «залипает»
после тапа до следующего касания. Это НЕ вывод «у нас так задумано» — это открытый
вопрос для дизайна.

### Angular Material — эталон, и у него всё сказано прямым текстом

- `src/material/expansion/expansion-panel-header.scss` (≈46–50):
  «Disable the hover on touch devices since it can appear like it is stuck. We can't use
  `@media (hover)` above, because the desktop support browser support isn't great.»
  → `@media (hover: none) { background: <фон контейнера>; }`
- `src/material/stepper/step-header.scss` (≈48–55):
  «On touch devices the :hover state will linger on the element after a tap. Reset it via
  `@media` after the declaration, because the media query isn't supported by all browsers yet.»
  → `@media (hover: none) { &:hover { background: none; } }`

Обя ссылки — `https://raw.githubusercontent.com/angular/components/main/<путь>`; их берут
`curl -sL`, содержимое совпадает с тем, что лежит в `_audit/platform/_src`.

### Material Design 3

Текстового правила «на тач hover не показываем» получить не удалось, и утверждать его
нельзя. Что реально есть в собранном:

- hover — одно из состояний со своим **state layer**: токены `hover-state-layer-opacity`
  рядом с focus/pressed/dragged (в наборах material-web встречались .08 / .10 / .15 / .16);
  отдельного «мобильного hover» в MD3 нет — состояние описано для ввода указателем.
- Клиентский рендер: `m3.material.io/foundations/interactive-states/states` — curl отдаёт
  Angular-шелл (0 текста), headless Chrome с `--virtual-time-budget=20000` отдаёт ~978
  символов текста и ни слова про hover; `m2.material.io/design/interaction/states.html`
  сейчас тоже клиентский рендер. Живой браузер (`browser_exec`) откроет страницу, но
  спросит галочку «Allow remote debugging» — это единственный путь к точной формулировке
  MD3, и это решение пользователя.

### iOS HIG

hover описан только для Apple Pencil/указателя
(`developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble`):
«Use hover to help people predict what will happen when Apple Pencil touches the screen»,
«Avoid using hover to initiate an action». Для пальца hover не предусмотрен.

## Как это писать на странице/в ответе

- Строка в «Что меняется»: `Наведение (hover) | есть — подсветка при наведении курсора |
  нет — на телефоне только нажатие (press)`.
- В «Почему так» — «палец вместо курсора»: зона нажатия (48 px Material / 44 px iOS)
  и отсутствие состояния наведения.
- В «Итоге» — отдельным пунктом «Не решено»: в нашей библиотеке hover на тач не гасится
  нигде; Angular Material гасит через `@media (hover: none)`. Гасить так же или оставить —
  решение дизайна. Своей правкой CSS это не решать: медиазапрос затронет и десктоп с
  тачскрином, а это как раз тот класс решений, который пользователь оставляет себе.
- Если формулировка MD3 нужна точной — сказать прямо, что она не подтверждена собранными
  источниками, и предложить живой браузер, а не пересказывать по памяти.
