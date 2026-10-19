# Material: что сказано про кнопку и где это лежит

Нужно, когда пользователь спрашивает «а что по этому компоненту говорит Material Design /
Angular Material?». Отвечать по первоисточникам, а не по пересказу.

## Как достать рекомендации

- `m3.material.io/components/buttons/specs` — **клиентский рендер**: curl отдаёт ~60 КБ HTML
  с нулём цифр, а интерактивный браузер требует разрешения Chrome на remote debugging
  (одобрение пользователя). Пока его нет — брать числа из источников ниже, они совпадают.
- **Angular Material: доки лежат markdown-ом в репозитории** и читаются curl-ом:
  `https://raw.githubusercontent.com/angular/components/main/src/material/button/button.md`.
  Механика размеров — `…/src/material/button/button.scss` и `…/button/_button-base.scss`
  (там видно, что тач-зона — отдельный элемент `.mat-mdc-button-touch-target`).
- **Material Web** (веб-реализация M3):
  `https://raw.githubusercontent.com/material-components/material-web/main/docs/components/button.md`
  и `…/button/internal/_shared.scss`; рендер — `https://material-web.dev/components/button/`.
- **Тач-таргет 48 dp** как норма доступности: `https://support.google.com/accessibility/android/answer/7101858`
  — «elements have a width and height of at least 48dp, as described in the Material Design
  Accessibility guidelines».
- **Внутри проекта**: `iiko-ds-prototypes/compare-button-mob.html` — таблица
  `Button_mob / MD3 / iOS` с числами и ссылкой на раздел спеки M3. Читать распаковкой
  JSON-объекта `const data = {…}` (html парсится через `json.JSONDecoder().raw_decode`).

## Material Design 3 — кнопка

| Параметр | Значение |
|---|---|
| Типы | elevated, filled, filled tonal, outlined, text |
| Высота контейнера | 40 dp |
| Горизонтальный паддинг | 24 dp |
| Форма | `container-shape: --md-sys-shape-corner-full` (pill ≈ 20 dp) |
| Текст | `label-large` 14 sp / 500 |
| Иконка | 18 dp |
| Тач-таргет | **минимум 48 × 48 dp** |
| Состояния | hover на тач-устройствах не работает → pressed / focus |

Отдельной «мобильной кнопки» в M3 **нет**: спека одна на все устройства, а мобильное
отличие — тач-таргет и состояния. Ровно это записано в нашей таблице плана:
«M3: шкала размеров кнопок, минимальная тач-зона 48 dp».

## Angular Material — кнопка

- Нативные `<button>`/`<a>`; `matButton` с appearance text / filled / tonal / outlined /
  elevated; отдельно `matIconButton`, `matFab`, `matMiniFab`.
- Высота — токен контейнера (`--mat-button-<type>-container-height`), а тач-зона —
  **отдельный элемент** `.mat-mdc-button-touch-target` (токены `button-*-touch-target-size`
  и `*-touch-target-display`). Density сжимает контейнер, но не тач-зону — именно так в
  Material «делают крупнее под палец», не меняя вид кнопки.
- В доках прямо: иконочным кнопкам нужен `aria-label`, а иконка — «minimum touch-target of
  48x48 … particularly on mobile devices and small screens».
- Ещё: текст не капсить (скринридер читает по буквам), `disabledInteractive` для
  фокусируемой недоступной кнопки, `progressIndicator` — спиннер поверх лейбла.

## Что это значит для нашего Button_mob

| | Button_mob (наш) | M3 | Angular Material |
|---|---|---|---|
| высота | 44 | 40 dp | токен контейнера |
| паддинги | 16 / 12 | 24 гориз. | — |
| текст | 16 px · 500 | label-large 14 sp · 500 | — |
| иконка | 20 | 18 dp | — |
| радиус | 8 | pill (20 dp) | — |
| тач-зона | M 44; S 28 и XS 24 — ниже нормы | 48 dp минимум | 48 × 48, не зависит от density |

Выводы, уже проговоренные пользователю:

1. Тач-зону решать **отдельным слоем** (псевдоэлемент/обёртка 48 × 48), а не высотой
   кнопки: в Material S/XS-кнопки не растягивают. Это закрывает открытый вопрос по S/XS
   без новых мобильных компонентов.
2. Кегль — единственное настоящее расхождение: M3 держит 14, `Button_mob` — 16, план
   говорит «текст и состояния без изменений». Решение владельца, не агента.
3. Радиус/pill и цвет не догонять — по плану они общие для платформ.
4. Наш `data-mode="mobile"` фактически равен density-шагу Angular + явный тач-таргет;
   это стоит дописать правилом в `modes.css` и в спеку.

## Шкала размеров кнопки в токенах M3 (не повторять ошибку)

Фраза «в Material размеров S/XS у кнопки нет» **неверна**. Размерная шкала в M3 есть, просто она
живёт в токенах, а не в веб-компоненте:
`material-web/tokens/versions/latest/sass/_md-comp-button-{xsmall,small,medium,large,xlarge}.scss` →

| Размер | Высота | leading-space | icon |
|---|---|---|---|
| xsmall (XS) | 32 dp | 12 | 20 |
| small (S) | 40 dp | 16 | 20 |
| medium (M) | 56 dp | 24 | 24 |
| large (L) | 96 dp | 48 | 32 |
| xlarge (XL) | 136 dp | 64 | 40 |

При этом `md-filled-button` атрибута `size` не имеет и рендерит дефолтные 40 dp — отсюда
ощущение, что шкалы нет. Верная формулировка для пользователя: «шкала есть в токенах M3, но нет
ни в реализации Material Web, ни в Angular Material, ни в HIG; у нас M 36 / S 28 / XS 24 — то есть
даже наш M ниже дефолта M3 на 40, а S мельче самого мелкого размера M3 (32)».

Числа взяты из выгрузки `DS/_audit/platform/button.json` (собрана субагентом 11.09.2026, с
цитатами и ссылками на файлы токенов) — перед использованием перепроверить `curl -sL` по тем же
путям.

Ещё по «состояниям»: страница `m3.material.io/foundations/interactive-states/states` не читается
ни curl-ом (Angular-шелл), ни headless Chrome (`--dump-dom` даёт ~978 символов текста). Про hover
на тач писать по Angular Material и по `references/hover-and-states-on-touch.md`, а не по памяти.
