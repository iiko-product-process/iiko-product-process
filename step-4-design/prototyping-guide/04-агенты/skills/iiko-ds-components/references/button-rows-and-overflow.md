# Сколько кнопок влезает в одну строку и что делать, когда не влезает

Вопрос владельца 12.09.2026: «Если 4 кнопки в строчку не умещаются в одну строчку, что должно происходить
по версии материал и просто логике?» Прямого правила ни у одной платформы нет — есть четыре соседних, и они
берутся из источников (MD3 / Angular Material / iOS HIG), а не из рассуждений.

## Что говорят источники

| Файл | Что следует | Цитата |
|---|---|---|
| `tooltip.json` (MD3 rich tooltip) | Держать подписи короткими именно ради одной строки; перенос — крайняя мера; кнопок не больше двух | «Rich tooltips can have up to two text buttons» · «Keep buttons short so they can be side by side. Avoid stacking them when possible.» |
| `dialog.json` | Ограничения на число действий заданы только у MD3 (диалог — максимум два действия) и у MD2-баннера (не более двух текстовых кнопок); в iOS HIG лимит другой, в Angular Material лимита нет | «Правило „не более двух действий“ есть только у MD3 (диалог: максимум два действия) и у MD2-баннера (не более двух текстовых кнопок)» |
| `dialog.json` / `snackbar.json` (iOS HIG) | Alert — до трёх кнопок, action sheet — до четырёх; это предел | «In all platforms, alerts display a title, optional informative text, and up to three buttons.» · action sheets — ≤4 |
| `button.json` (iOS HIG) | Кнопки не смешивать по размеру в одном ряду, различать стилем; центры — минимум 60 pt друг от друга (на 375 px это 2–3 подписанные кнопки) | «Use style — not size — to visually distinguish the preferred choice» · «placing two buttons of different sizes near each other can make the interface look confusing and inconsistent» · «Aim to place buttons so their centers are always at least 60 pts apart.» |
| `button-toggle.json` (iOS HIG) | Для однотипных сегментов — свой лимит: около пяти–семи в широком интерфейсе, около пяти на iPhone | «Aim for no more than about five to seven segments in a wide interface and no more than about five segments on iPhone» |
| `tabs.json` (MD3 / iOS) | Переполнение однотипных «полок» решается **прокруткой**, а не переносом; в iOS overflow уезжает в More | «Scrolls the toolbar, if overflowing, to the active tab, or the provided tab» · `overflow: auto` |
| `bottom-sheet.json` (iOS HIG) | Приоритет важнее полноты: не показывать вместе Cancel + Done + Back | «Avoid showing all three buttons — Cancel, Done, and Back — together.» |
| `button-group.json` | У Button group в MD3 есть только числа (container 32/40/56/96/136, between-space standard 18/12/8/8/8, connected 2 dp) — правил переполнения нет | — |

## Логика (моя, без источника — подаётся как таковая)

1. Сначала сокращать подписи: если четыре кнопки не влезли — виноват текст, а не раскладка.
2. Одно главное действие (на всю ширину), остальные — в overflow «⋯». Четыре равнозначные кнопки в строке —
   признак, что иерархия не выстроена.
3. Если действий 2–3 и они равнозначны — **перенос в столбик**, каждая на всю ширину (так уже сделано в шторке
   и в мобильном диалоге; в iOS так же ведёт себя action sheet).
4. Прокрутка строки — только для однотипных элементов (табы, чипсы, фильтры), не для набора действий:
   обрезанную кнопку никто не ищет.
5. Чего не делать: сжимать текст, резать подписи «…», менять кегль или размер одной кнопки, чтобы влезли
   (HIG прямо против смешанных размеров), уменьшать тач-зону ниже 48 dp.

## Наши числа (замерено на `button.html`)

- Мобильные кнопки M при паддингах 12/16: «➕ Создать» **121 px**, «ОК» **54 px**, «Далее ›** (иконка справа)
  **106 px**; иконка-кнопка (Button icon) **40 × 40**.
- Внутренняя ширина экрана в корпусе 375 px — **359 px**. Четыре кнопки в одну линию требуют
  `padding:8px 10px` + `gap:4px`; со стандартными `12px 16px` + `8px` контент 362 px и последняя кнопка обрезается
  (проверять `line.clientWidth` против `line.scrollWidth`).
- Контейнер списка в библиотеке — 258 px, мобильного значения нет (см. `screen-preview-phone-frame.md`).

## Как об этом докладывать ему

Сначала — что видно и что не влезает, потом — цитата платформы (одна-две, с именем файла), потом лестница
вариантов и вопрос, какой выбираем. Таблицу `getComputedStyle` в качестве ответа на дизайн-вопрос он не читает:
«Нихрена не понял что ты написал».
