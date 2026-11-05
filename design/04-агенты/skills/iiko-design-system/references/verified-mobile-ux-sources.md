# Проверенные мобильные источники: цитаты и адреса

Требование владельца: в контенте нужны «реальные кейсы и применение от больших компаний или
известных специалистов UX/UI гуру» — платформенных доков недостаточно. Ниже — то, что уже
вытащено со страниц и подтверждено текстом источника. Цитаты приводить дословно.

## Как вытаскивать (проверенные пути)

- **Apple HIG** — HTML отдаёт 403/шелл без текста, но есть официальный JSON:
  `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`
  (`layout`, `buttons`, `pickers`, `lists-and-tables`, `typography`, `inclusion`). Страницы
  `localization` и `text-size-and-weight` там нет (404).
- **Nielsen Norman Group** — `curl -sL https://www.nngroup.com/articles/<slug>/` отдаёт полный текст
  статьи, цитаты берутся регуляркой по тексту.
- **raw.githubusercontent.com** — дословные доки дизайн-систем: Material Web
  (`docs/components/<name>.md`, токены и `button/internal/_touch-target.scss`), Carbon
  (`src/pages/components/<component>/usage.mdx`), Ant Design (`components/<name>/index.en-US.md`).
- **developer.android.com**, **w3.org/WAI**, **design-system.service.gov.uk**, **m2.material.io** —
  открываются curl-ом (у Android-страниц текст в разметке, у m2 — нет).
- `carbondesignsystem.com` (HTML) и `developer.apple.com` (HTML) — 403; брать зеркалами выше.
  `polaris.shopify.com` и `lightningdesignsystem.com` отдают JS-шелл без текста.
- `web_extract` при 403 не блокер — те же адреса берутся `curl -sL` в терминале (пути `C:/…`).

## Зона нажатия и большой палец

- **NN/g · Touch targets** (nngroup.com/articles/touch-target-size): «A past study from the MIT Touch Lab
  found that the average person's fingertips are 1.6–2cm (0.6–0.8 in) wide. The impact area of the typical
  thumb is even larger — an average of 2.5cm (1 inch) wide!»
- **MD3 / Angular Material** — тач-таргет 48 dp: Material Web `button/internal/_touch-target.scss`
  (`height: max(48px, 100%)`), Angular `$touch-target-size: 48px`. Apple HIG: «a button needs a hit region
  of at least 44x44 pt».

## Нижние шторки, досягаемость, закрытие оверлеев

- **NN/g · Bottom Sheets** (Page Laubheimer, 2023, nngroup.com/articles/bottom-sheet): «A common (but largely
  incorrect) rationale for using bottom sheets is that they improve reachability for users on mobile devices…
  the bottom of the screen is often not the most easily reachable screen region (the middle of the screen
  represents the most easily tappable area for the wide variety of ways users hold mobile devices)». Там же:
  расширяемая шторка тянется за ручку, свайп вниз конфликтует с системными жестами.
- **NN/g · Accidental Dismissal of Overlays** (Budiu, Behnam, Moran, 2022): способов закрытия несколько
  (кнопка, свайп по ручке, Back, горизонтальный свайп-назад на iOS и Android) — пользователи выбирают
  не тот; разобран кейс **Walmart**. URL: nngroup.com/articles/accidental-overlay-dismissal/.

## Свайпы в списках

- **NN/g · Using Swipe to Trigger Contextual Actions** (Angie Li, 2017, nngroup.com/articles/contextual-swipe):
  «Poorly implemented swipe-to-delete can lead to loss of data… it's important to always ask for confirmation
  or provide an easy way to undo the swipe». Кейсы в статье: **B&H Photo** (свайп раскрывал сразу
  Remove from cart / Save for Later / Savings / Accessories — действия необнаружимы), **Overcast**
  (свайп сам не удаляет, нужно попасть в кнопку Delete), **YouTube** (после отписки сразу даёт «отменить»).
- **Apple HIG · Lists and tables**: «People appreciate being able to reorder a list, even if they can't add or
  remove items. In iOS and iPadOS, people must enter an edit mode before they can select table items.»

## Пикеры и выбор даты/времени

- **Apple HIG · Pickers**: «Compact — A button that displays editable date and time content in a modal view»;
  стили Inline и Wheel разведены по платформам — то есть системный пикер открывается модально, а не
  разворачивается на месте.
- Material: `date pickers` — modal и docked. Исследования по календарям в бронировании — Baymard
  (baymard.com; страницы отдают текст, проверять перед цитированием).

## Безопасные зоны, края экрана, планшет

- **Apple HIG · Layout**: «A safe area is essential to make sure system UI and hardware features like the
  Dynamic Island don't obstruct content and controls»; там же — про поворот, изменение окна, сплит.
- **Android · edge-to-edge** (developer.android.com/design/ui/mobile/guides/layout-and-content/edge-to-edge):
  «The edge-to-edge feature lets you draw the UI under the system bars for an immersive experience».
- **Android · window size classes**
  (developer.android.com/develop/ui/compose/layouts/adaptive/window-size-classes): Compact width —
  «width < 600dp, 99.96 % of phones in portrait»; Medium — 600–840 dp (планшеты в портрете);
  Expanded — 840–1200 dp.

## Контраст (тёмная тема)

- **WCAG 2.2, критерий 1.4.3 Contrast (Minimum)** (w3.org/WAI/WCAG22/Understanding/contrast-minimum.html):
  «The visual presentation of text and images of text has a contrast ratio of at least 4.5:1… Large-scale
  text and images of large-scale text have a contrast ratio of at least 3:1».

## Что осталось без приличного источника

- **Растяжение текста при локализации (тезис «на 30–50 % длиннее»)** — подтверждается только
  коммерческими сайтами локализации (gtelocalize, better-i18n), не авторитетами из списка владельца.
  Не выдавать за факт: либо искать дальше (док-стандарты, дизайн-блоги крупных компаний), либо говорить
  прямо, что надёжного источника нет.
- **Тёмная тема от Material Design 3** — страница клиентская, текст через curl не берётся; пока
  опора на WCAG и токены `themes.css` самого ДС.
