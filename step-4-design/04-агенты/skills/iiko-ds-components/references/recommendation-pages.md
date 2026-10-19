# Recommendation pages (iiko DS) — pipeline, layout rules, checks

Generated «desktop → mobile» pages, one per component, plus the shell with the
component menu. Everything lives in the repo; the DS itself (`iiko-ds-web`) is
never edited for these pages.

## Pipeline

```
_audit/rec/data/<slug>.json      page-facing data (one file per component, 38 of them)
_audit/rec/data-tech/<slug>.json technical notes (sources, platform specs, measurements)
_audit/rec/platform/<slug>.json  platform research: platforms.md3 / .angular / .apple
                                 (sizes + quotes + sources), not_recommended_ru, verdict_ru
_audit/rec/mock.py               phone-screen helpers (status/head/body/foot/lst/btn/
                                 checkbox/radio/toggle/tabs/sheet/card/screen/phones,
                                 check_balance)
_audit/rec/build.py              generator: writes <slug>.html + index.html + rec.css
_audit/rec/apply_out.py          merges patches from out/ into data/, --build rebuilds
out/
└── {edits,previews,platforms,changes}/<slug>.json   patches (see below)

iiko-ds-mobile/prototypes/recommendations/<slug>.html + index.html + rec.css   output
served by `python serve.py 8899` from the repo root
```

`data/<slug>.json` keys used by build.py: `slug, component, ds_page, desc_ru,
category_ru, category_note_ru, panels{desktop,mobile}.sub_ru, changes[{what,
desktop,mobile,edit[]}], behaviour_html, why_ru, why_sources, result_html,
examples[{title_ru,html,html_mobile,stack}], preview_html, platform_notes_ru,
logic_ru, found_html`.

## Page layout — rules the owner fixed (2026-09)

1. Top: two panels **Desktop | Mobile** (recommended values, mobile panel 375 px wide).
2. «На экране»: **exactly two phone screens with the same interface** — identical
   markup, same head/body/footer/sheet; they differ only in *values*: the left one is
   «как рекомендовано», the right one is driven by the edit fields. Do not make the
   screens differ in layout, do not move the component to another slot per screen,
   and do not show three screens (the owner asked for two and for sheet-present-on-both
   when a sheet belongs to the screen). **Re-confirmed 2026-09-13 after a regression**
   («Ты сделал одно и сломал другое… на 2 экранах мобилы в превью должны быть одинаковые
   интерфейсы»): screen 2 is a **copy of screen 1** — its own caption is the only allowed
   difference on top of the `data-preview="edit"` marker. A summed-up body, the component
   moved into the sheet, an extra/missing header icon, a different width wrapper — all of
   that is the bug, not a second variant. If a component has a second variant (in the sheet),
   it shows up **inside one and the same interface**, i.e. on both screens alike.
3. Third slot of that row: the two-column table **«Что | Правка»** (built by
   `edits_panel()` from `changes[].edit`) with the note «правка применяется к правому
   экрану». The 4th column is **not** in the «Что меняется на мобиле» table (that table
   is Что | Desktop | Mobile).
4. Fields write rules into `<style id="live">` scoped to the *second* screen:
   `[data-mode="mobile"][data-preview="edit"].phone__screen <sel> { … }`.
   build.py injects `data-preview="edit"` into the 2nd `.phone__screen`; the first
   screen stays default (a leak check exists — see below).
5. Buttons: two buttons that fit go **in a row**, not stacked — build.py CSS turns
   `.phone__sheet .phone__actions` into a row and gives buttons `width:auto`.
6. «то же / та же / тот же / те же» in the Mobile column must be **numbers** (same as
   Desktop) whenever Desktop has sizes, and those rows get edit fields.
   Hex colours are not sizes — a row like «Цвета: #616161 … → те же» stays as is.
7. Block **«Примерные паттерны поведения»** — the renamed «Что говорят платформы»
   (2026-09: he asked for the heading only — a rename must not touch the content).
   Content is now authored as short **patterns** in the data key `patterns_ru` — the
   shape, the 3–6 count and the citation rules are in the section below.
   `platforms_card()` renders `patterns_ru` when present and otherwise falls back to
   `platform_notes_ru` + `logic_ru`, so un-migrated pages keep working.
   Yardstick he used: two buttons fit → one row; 3–4 don't fit → one primary full width +
   the rest in «⋯»; equal-weight 2–3 → column; scrolling a row of actions is forbidden
   («обрезанную кнопку никто не ищет»).
8. «На экране» shows the **problem case, not the ideal placement**: the studied
   component is visible both on the screen and in the sheet (different variants), and the
   screens show what happens when it does not fit. Never show behaviour our own patterns
   forbid — a scrolling row of four buttons was exactly that and he caught it immediately.
   A bottom sheet covers the footer, so an action bar that must stay visible belongs
   **inside `body()`**: on Button the `.phone__foot` row «Сохранить» + «⋯» is the first body
   block, above the list, and the sheet repeats the same actions stacked — the component is
   then visible on the screen *and* in the sheet in one and the same interface.

## Patterns — cited sources, not opinions (2026-09-13)

He rejected the from-memory version: «паттерны… не только по тому что я описал… Нужно как
раз найти в целом что с ними может произойти в мобверсии. Там наверняка есть и другие
нюансы.» So `patterns_ru` is a **researched** block, one JSON file per component
(`out/patterns/<slug>.json`), enforced by `check-patch.py`:

```json
{"slug": "…", "patterns_ru": [
  {"title": "короткая ситуация",
   "items": ["Что происходит: …", "Что делают системы: …", "Что делать нам: …"],
   "src": "Источники: Apple HIG · Buttons (URL) · IBM Carbon · Button usage (URL)"}]}
```

- **3–6 patterns per component**, each a different mobile nuance (overflow, touch target,
  keyboard covering, 375 px legibility, long labels, many items, disabled/loading,
  destructive, accessibility). Item prefixes «Что происходит:» / «Что делают системы:» /
  «Что делать нам:» — the third one is the decision for our DS on mobile.
- Checker rules: 3–6 patterns, `title` present, ≥2 items, each item ≥25 chars, `src` with
  names + URLs. Button (the reference page) holds six: two actions in a row · third and
  fourth don't fit (primary full width + «⋯») · long label wraps instead of truncating ·
  full-width button in the form footer · icon-only button and its 44×44 pt / 48 dp hit
  region · double tap → spinner inside the button and the button disabled.
- Fetch routes, verbatim quote bank and the **grep-the-quote-before-you-write-it**
  protocol: `references/ds-source-quotes.md`. A quote with a plausible URL that the source
  does not contain is the failure mode to watch for (it happened on Button).
- **Render shape: tabs, one per pattern** (2026-09-13, at his request: «сделай этот блок
  с табами… у каждого таба приведи пример»). `platforms_card()` now emits
  `<div class="ds-tabs ds-tabs--lvl2 pat__tabs" role="tablist">` with one `.ds-tab` per
  pattern and one `<div class="pat__panel" data-pat-panel="pat-<slug>-<i>">` per pattern
  (only the first without `hidden`); an IIFE appended to the page script toggles `hidden`
  and `.ds-tab--active` on click. Level-2 tabs are what fits: on Button **six level-1 tabs
  measure ≈1520 px in a 1518 px card** (last label clipped mid-word) while level-2 is
  1382 px — measured with the iframe probe, not eyeballed.
- **No scrollbar on the tab row — arrows instead** (2026-09-13: «Скролл у табов не нужен.
  Сделай стрелки туда сюда»). `platforms_card()` now wraps the row:
  `<div class="pat__bar"> [‹] <div class="ds-tabs ds-tabs--lvl2 pat__tabs">…</div> [›] </div>`,
  each arrow a DS icon button (`ds-btn-icon ds-btn-icon--m ds-btn-icon--neutral
  ds-btn-icon--text`, with `aria-label` and a Material Icons ligature `chevron_left` /
  `chevron_right` — never a hand-drawn SVG). CSS: `.pat__bar{display:flex;align-items:center;
  gap:8px}`, `.pat__tabs{flex:1 1 auto;min-width:0;overflow-x:auto;scrollbar-width:none}`,
  `.pat__arrow[hidden]{display:none}` — that last rule is required, because `.ds-btn-icon`
  sets `display:flex` and otherwise beats the `hidden` attribute. The IIFE hides both arrows
  when the row fits (`scrollWidth - clientWidth <= 1`), otherwise steps by
  `max(160, 0.6 * clientWidth)`, disables the arrow with nothing left to scroll, and re-syncs
  on `scroll`/`resize`. **Do not add `scroll-behavior:smooth`**: under headless Chrome the
  animation never completed, so the probe read `scrollLeft 0` after a click and a working
  arrow looked dead. Verified numbers (Button): row 815 vs tabs 1382 → click right 0→489,
  →567 = end with the right arrow disabled, click left 567→78; at full width row 1503 =
  tabs 1503 → both arrows hidden.
- **Every tab carries an example of its own case** — `example_html` + `example_ru` on the
  pattern object, rendered as an «Пример» plate under the sources (`example_ru` is the
  one-line caption). The example shows the *solution*, never the breakage, and uses **only
  DS classes** copied from `data/<slug>.json → examples[].html`; a narrow-screen case is
  wrapped in `<div class="pat__phone">` (343 px = 375 − 2×16), a row in `pat__phone-row`.
  Button's six: two buttons in a row · full-width primary + «⋯» · long label that wraps to a
  second line · full-width primary with a text action under it · icon-only button inside a
  dashed 48×48 `.pat__hit` box · enabled next to disabled for the double-tap case.
  Checker rules: `EX-MISSING` (no example), `EX-NOTE` (no caption), `EX-BALANCE` (markup
  not balanced), `EX-CLASS` (class not from the DS). Spec: `out/SPEC5.md`.
- **A new container for DS markup silently loses every framework fix — and a screenshot
  makes it read as «fine, just boxes».** The DS autogen writes `background` with the same
  token as `color` on ~23 text classes (`.ds-list-item__text`, `.ds-menu-item__label-up`,
  `.ds-dialog-header__description`, `.ds-text-ui__label-up`, `.ds-sidenav-item__l3`, …).
  `.panel` and `.phone` neutralise it (`background:none`), but the example plates are a
  **third** container: once the tabs landed, 134 text leaves across 16 pages drew as solid
  black/grey rectangles — the text was there, sitting under its own background. Fix in
  `build.py` beside the `.phone` mirroring, after the CSS constant is assembled:
  `_panel_rules = re.findall(r"(?m)^\.panel [^{]*\{[^}]*\}", CSS)` then
  `CSS += _rule.replace(".panel ", ".pat__panel ")`. That single copy also carries the
  frozen-height fixes (menu 418 / select 406 / list 257), the light-snackbar colour, the
  white sidenav labels and the dialog-action `height:auto` into the examples. Scope it at
  `.pat__panel`, **not** at the phone wrapper: one subagent wrapped its example in its own
  inline-styled `div`, so a `.pat__phone`-scoped copy never reached it. Copy whole rule
  **blocks**, never lines — a line-based pass replaces only the first selector of a
  multi-line selector list (that is exactly how `.phone .ds-list-item__text` stayed
  unprefixed on the first attempt and the plates kept rendering black).
- **Metrics the DS fixes in px beat the 343 px example body.** `.ds-dialog-view`,
  `.ds-dialog-header`, `.ds-dialog-content` are 500 px and `.ds-snackbar--single/--complex`
  370 px, so those two examples stuck out of their plate by 157 px and 27 px. In examples
  only: `.pat__phone .ds-dialog-view, .pat__phone .ds-dialog-header,
  .pat__phone .ds-dialog-content, .pat__phone .ds-dialog-view__action,
  .pat__phone .ds-snackbar { width: 100% }`.
- **Both defects are measurable without eyesight** — do that instead of squinting at a
  screenshot. In every `.pat__panel .pat__ex`, walk the leaves: flag text whose computed
  `backgroundColor` is opaque **and equal to** `color` (the autogen artifact above);
  separately compare `inner.scrollWidth - inner.clientWidth` per plate. Session numbers:
  invisible leaves 134 → 3 → 0 over three rounds (the last three were
  `.ds-sidenav-item__l3` inside a subagent's own wrapper, before the fix was scoped at
  `.pat__panel`), plate overflow 2 → 0. Shipped as `scripts/example-plates-audit.py`.
- Not every finding gets fixed: the Dialog example still shows the DS's own `min-height`
  (364 view / 204 content), so its plate is tall and half-empty. Reported to him as an
  observation rather than overriding a metric the DS declares — «найденное рядом — списком,
  не чинить».
- **Look of the example plate — he pushed back twice the same day** («пример сливается с
  текстом», «подпись к примеру не бледную»). The default `.ex__title` with a grey `#757575`
  caption is not enough: give the example its own surface —
  `.pat__ex{margin:16px 0 0;padding:12px 14px;background:#fafafa;
  border:1px solid var(--ds-color-stroke-default);border-radius:8px}` — and keep both the
  «Пример» heading and `example_ru` at 13 px/18 px in `#333`, never pale grey. The rule
  behind it generalises: if two pieces of content can be read as one, separate them
  visually; a caption that carries meaning is not secondary text.
- **Asked about scope, he answered «Общий механизм для всего».** A change requested on one
  page is a change to the generator (`build.py`), applied to all 38 pages — not a hand
  patch of a single page, and not a second mechanism living beside the first.

## Patch workflow (parallel-safe)

Subagents never touch `data/*.json`. Each writes its own patch files:

```json
// out/previews/<slug>.json
{"slug": "...", "preview_html": "<div class=\"phones\">…</div>"}
// out/edits/<slug>.json
{"slug": "...", "edits": [{"row": 1, "mobile": "48 px — …",
  "edits": [{"id": "row", "v": 48, "sel": ".ds-checkbox", "css": "min-height:@px"}]}]}
// out/platforms/<slug>.json
{"slug": "...", "platform_notes_ru": [{"title": "Material Design 3", "items": []},
 {"title": "iOS HIG", "items": []}], "logic_ru": []}
```

`row` is the index into `changes`; `mobile` rewrites the Mobile cell; `edits` replaces
that row's field list; `sync: {field, a, b}` makes a field follow `t = a*v + b`
(like button height ↔ vertical padding). Merge with
`python apply_out.py --build` (indent=1, CRLF preserved).

Give subagents a spec file (`_audit/rec/out/SPEC*.md`) and make them validate each
component before finishing:
`python checks/check-patch.py <slug>` → must print 0 problems.

Batch size that worked: ~9–10 components per subagent, four in parallel, each owning its
slugs end-to-end (pattern file, preview fix, self-check). Steer them mid-run with the
source recipe — they hit the same 403 walls otherwise. **Before delegating, check that
`apply_out.py` actually merges every `out/<kind>/` the spec asks for.**

## Verification scripts (`_audit/rec/checks/`)

Run from `_audit/rec`; they drive **headless Chrome** (`C:\Program Files\Google\Chrome\
Application\chrome.exe`) against `http://127.0.0.1:8899/...` — no playwright needed.

| script | catches |
|---|---|
| `audit-edits.py [slug]` | field whose selector matches nothing (`MISS`), field that changes nothing (`NOCHANGE`), edit leaking into the default screen (`LEAK`), wrong screen count, page-vs-data mismatches |
| `audit-preview.py` | screens ≠ 2 (`COUNT`), studied component missing on a screen (`NOCOMP`), screens differ (`DIFF`), element outside the phone (`OVERFLOW`), clipped text (`CLIPPED`), near-empty screen (`EMPTY`) |
| `check-patch.py [slug]` | patch files before merge: 2 screens, div balance, unknown classes, component on both screens, same interface — **full markup of both screens minus captions (`PREV-SAME`)**, not just title/sheet — selector present in markup, `@` in css, duplicate ids, «то же» rows still not numeric |
| `page-block.py <slug> "<sel>;…"` | where a block actually sits (x/y/size/display) — use instead of guessing crop coordinates |
| `audit-live-desktop.py` | long-standing panel defects: clipped, overlap, frozen-height voids, state-specificity |
| `preview-sheet.py <slug>…` | contact sheet of several pages' previews for a single eyeball pass (writes to `_audit/rec/out/`) |
| `why-nochange.py`, `why-rule.py` | debugging a dead field: matched elements, inline styles, live rule text, which CSS rule wins |

Headless harness pattern when writing a new check: build a small wrapper HTML in the
site root that creates one `<iframe>` per page, collects results into `<pre id="out">`,
run `chrome --headless=new --dump-dom --virtual-time-budget=…`, then regex the `<pre>`
and `html.unescape` it. Write results into the `<pre>` after every page (forgetting
that = empty output), and delete the wrapper in a `finally`.

The pattern block has its own probe, shipped with this skill:
`scripts/patterns-tabs-audit.py`. Without flags it counts, per component, patterns vs
examples vs `src` straight from `data/`; with `--chrome` it loads a page through the
harness above and reports tabs / panels / example plates, the active tab, whether the tab
row fits the card (`bar.scrollWidth <= width`), and — with `--click <i>` — that clicking a
tab leaves exactly one panel visible. `--arrow-click` instead presses the right arrow and
asserts the row really moved — the only honest check of a scrolling row. Clicking through the
harness is the only honest check of the switch: the inactive panels are `hidden`, so a
screenshot of the first tab says nothing about the other five. Overflow is no longer a
pass/fail by itself: an overflowing row is what the arrows are for, so the script flags
«arrows hidden while the row overflows» and «arrows shown while it fits» instead.

The **example plates** have their own probe, `scripts/example-plates-audit.py`. With
`--chrome` it walks every page and every pattern tab and reports invisible text
(`backgroundColor` == `color` — the DS autogen artifact), examples wider than their plate,
and each plate's rendered height; without flags it counts `patterns_ru` against
`example_html` / `example_ru` straight from `data/`. It exits non-zero when it finds
anything, so it can gate a rollout; run it after any change to the plates or to the CSS
that scopes them.

The **two-screen identity** has a re-runnable repair/check script shipped with this skill:
`scripts/align-preview-screens.py`. `--check` only reports which previews differ (exit 1);
without flags it rewrites `out/previews/*.json` so screen 2 is a copy of screen 1 with the
standard second caption; `--data` does the same to `data/*.json` and `--data --build` then
runs `apply_out.py --build`. Run it before merging a new round of preview patches.

## Pitfalls that cost real time here

- **A literal `%` anywhere in the page template breaks the whole build.** `page()` passes its
  HTML through `%`-formatting with a dict, so a `%` inside injected CSS/JS (a comment reading
  «листается на 60 %») raised `TypeError: not enough arguments for format string` and killed
  all 38 pages; the previously built page stayed on disk, so the look was silently stale. In
  text that build.py injects write «шесть десятых», not `%`, and run `python build.py` after
  every generator edit — the traceback names the line, a stale page does not.

- **Transitions**: measure 700 ms after applying a value; an instant read reports the
  old computed value and a working field looks dead (`slide-toggle` transform).
- **Measure all declared properties**, including bare `padding`/`margin` shorthands —
  filtering them out produced false `NOCHANGE` on form-field/select/timepicker.
- **Inline styles in page markup beat the live rule** → the field's css needs
  `!important` (`autocomplete`: `style="min-height:48px"` in the example markup).
- **The mobile layer may use a longer selector** than the field does
  (`.ds-stepper.ds-stepper--vertical .ds-step`) → mirror the mobile selector, otherwise
  the field loses on specificity.
- **Overlapping fields** (`.ds-tab` and `.ds-tabs--lvl2 .ds-tab` with the same value)
  make the second measure as a no-op; keep one field per value.
- **A field whose class the screen doesn't contain** reports `MISS` — `.ds-btn__icon` was
  missing because no preview button carried an icon. Put the component's sub-elements
  (icon, label, box, support) into the preview markup, not just the root class.
- `.phone__sheet .phone__actions` is forced to a row by build.py CSS; to show equal-weight
  actions stacked (the Button pattern) override it inline: `style="flex-direction:column"`.
- **Overflow inside a scrollable or `overflow:hidden` ancestor is not a defect**
  (tabs, chips rows, drawers) — the clipping ancestors' layout boxes still stick out.
- Phone screen is 375 px, `.phone__body` padding 16 → content must fit 343 px;
  DS frozen container heights (menu 418, select 406, list 257) need `min-height:0`
  inside phone screens too (build.py mirrors the panel fixes for `.phone`).
- **Cache**: `build_version()` busts CSS by mtime only, and data edits don't change it —
  tell the user to reload with Ctrl+F5 when a page looks stale.
- `browser_exec` with Cyrillic in the code fails on this Windows host
  (`UnicodeDecodeError`), and the CDP-backed browser may ask for a manual
  remote-debugging approval — use the headless-Chrome scripts above instead.
- `--screenshot` grabs the viewport: set a tall `--window-size` and crop with PIL.
- Keep the DS folder clean: wrapper HTML, contact sheets and screenshots go to
  `_audit/rec/out/`, never into `iiko-ds-mobile/prototypes/recommendations/`.
- **A patch kind nobody merges is invisible work.** `apply_out.py` merged edits,
  previews and platforms only — a whole round of `out/patterns/*.json` sat on disk while
  the pages kept rendering the `platform_notes_ru` fallback. Add the branch for a new kind
  *first*, then let subagents loose on it.
- **A check that only runs when the key exists is a vacuous check.** `check-patch.py`
  validated patterns inside `if pats is not None`, so 36 pages with no patterns passed
  green. Assert the artefact's presence itself (`PAT-MISSING`), otherwise «0 problems» only
  means «nothing was looked at».
- `python build.py` regenerates all 38 pages in under a second, so a single-slug sanity
  render is cheap: write that one `data/<slug>.json` by hand (`indent=1`, `newline=""` +
  CRLF) instead of running `apply_out.py`, which would also merge half-finished sibling
  patches while the subagents are still working.
- To crop a screenshot of a block you have not measured before, let a wrapper HTML return
  `getBoundingClientRect()` for it (same iframe trick as the checks), then crop the
  `--window-size` screenshot with PIL using those numbers — 1600 px wide pages put the
  patterns card at e.g. y≈1894, h≈867.
- **`rec.css` is generated as well — this one is a silent trap.** `build.py` writes
  `iiko-ds-mobile/prototypes/recommendations/rec.css` from its own `CSS = """…"""` constant
  near the top of the file. A `patch` on that CSS file **reports success and then vanishes
  on the next `python build.py`** (it cost a whole styling round: the tab panel rules looked
  applied, the long-label example kept rendering on one line). Put block styles
  (`.pat__tabs`, `.pat__panel`, `.pat__phone`, `.pat__narrow`, `.pat__hit`, …) into the
  constant in `build.py` next to the `.plats`/`.plat__` rules, then confirm with
  `grep -c 'pat__' …/recommendations/rec.css` after building. Same story for `rec.js` —
  `main()` deletes it, so page behaviour belongs in the page template's `<script>`.
- **A finished subagent cannot be steered.** `delegate_task(action='steer')` on a child that
  already returned answers `No live subagent … in this conversation's spawn tree` — its files
  are already on disk and that round is closed. Extend written work with a **new round aimed
  at the files** (`goal`: «добавь пример в каждый уже существующий паттерн; текст, пункты и
  `src` не переписывай»), and call `action='list'` first when some children may still be
  live. Spec files accumulate (`out/SPEC4.md` patterns → `out/SPEC5.md` examples) and are the
  only channel a child has, so write the spec before spawning.
- **Merging a subagent's preview patch can quietly break the «one interface» rule, and the
  checker did not catch it.** The 37 preview patches written for SPEC4 modelled the second
  variant *across* the screens: screen 1 carried the real component in the body, screen 2
  replaced the body with plain `phone__row` text and moved the component into the sheet. The
  old interface check compared only `phone__title` and the sheet titles, so 34 of 38 pages
  shipped visibly different screens and the owner caught it (2026-09-13). Fix: screen 2 :=
  screen 1 (caption replaced with «Тот же экран, с правками из таблицы справа») in
  `out/previews/*.json`, then `apply_out.py --build` — `scripts/align-preview-screens.py`
  does exactly that and is re-runnable. The checker gained `PREV-SAME`, and one split detail
  cost several rounds: the last part of `re.split(r'(?=<div class="phones__item">)')` also
  carries the closing `</div>` of `.phones`, so that trailing `</div>` must be stripped from
  the last part *before* comparing, otherwise the rule can never turn green. Verified after
  the fix: 38/38 identical, 0 problems, edit fields still move only the right screen (radius
  field 20 → right 20 px, left stays 8 px). General rule: after merging third-party patches,
  re-verify the invariants they were supposed to preserve — a green checker only means the
  rules it has, and this one had a vacuous version of the very rule that broke.
- **What that fix costs, and what to do about it.** With screen 2 copied from screen 1,
  components whose sheet variant existed only on the right screen no longer show it anywhere
  (Card, List, Menu, Input number…). Do not silently re-add it: the honest move — asked, still
  open — is to offer showing the component in the sheet on **both** screens, which keeps the
  identity rule intact.

## Identity is not enough — the component must be VISIBLE on the screen (2026-09-13)

Right after the identity fix the owner opened Button and exploded: «Что мне смотреть на экранах
мобилы на этой странице? Там ни одной кнопки нет.» He was right, and every checker was green.
The page carried eleven `ds-btn` per screen, but neither screen *showed* one: the sheet held
three plain `phone__row` lines («Создать заказ», «Сохранить черновик», «Отмена») while the real
buttons sat inside the card, below the sheet's top edge — and `.phone__screen` is 720 px with
`overflow:hidden`, so the sheet plus its scrim simply covered them.

As rules:

- **«Component present» must mean «component visible».** Walking the class list is not enough:
  assert a leaf of the component inside `.phone__screen` whose bounding rect lies inside the
  screen box **and above the sheet's top edge**. That is the check that was missing; the class
  check passed on a page that showed nothing.
- **Put the studied block at the top of `body()`** — the sheet overlays roughly the lower half,
  so anything that must be seen goes first (this is why the Button footer row sits above the list).
- **The sheet repeats the component in real DS markup**, never as text lines. Subagent-written
  previews had the habit of summarising the sheet: a `phone__row` «Создать заказ» instead of a
  `.ds-btn`, a text row instead of a list row. Measured across the 38 pages after the merge: the
  component is in the body on 37, in the sheet on only 5 — 33 pages carry text rows where the
  second variant belongs.
- **Never report a page (or a batch) as done off the checker.** After merging a round of
  third-party patches, look at the rendered screens — harness numbers or a screenshot — before
  saying «готово». «0 problems» cost the owner's trust twice on these pages (the interface
  regression and this one).

Button reworked by hand as the reference for the remaining pages — reproduce this shape:
body = the DS card (`ds-card--outlined`) with `__header` / `__content` and a
`ds-card__footer__action` holding **both real buttons** (outlined «Отмена» + filled «Создать»
with an `add` ligature); sheet = `phone__sheet-title` + `phone__sheet-text` («Две кнопки
умещаются в строку — стоят в строку») + `.phone__actions` with the same two buttons as real
`.ds-btn` in a row + a third action as a `.ds-btn--text` in the DS button group; screen 2 is a
copy with the standard caption «Тот же экран, с правками из таблицы справа»; captions describe
what is shown, not a variant that no longer exists. `python checks/check-patch.py button` → 0.
Rollout state: Button done, **32 pages still to rebuild**, in passes of 5–6 with a screenshot
each. The scope question («все 32 разом или по 5–6 с показом») was put to him and is still open —
do not decide it silently.

## Аудит паттернов: по компоненту, с кейсами компаний и специалистов (2026-09-13)

Его формулировка задачи: «Проверь ещё раз все паттерны поведения для каждого компонента. Всё
ли учли. Есть ли что важное добавить что будет полезно для мобильной версии» → «Нужны
реальные кейсы и применение от больших компаний или известных специалистов UX/UI гуру» →
«У каждого компонента свои кейсы и паттерны поведения.»

- **Структура — по компоненту, а не по сквозным темам.** 38 отдельных ответов в форме
  компонент → поведение → реальный кейс (названная компания/продукт) ИЛИ правило
  (названный специалист / дизайн-система) → дословная цитата → адрес → `verified` → чего в
  `patterns_ru` не хватает. Первую сводку я сделал темами (контраст, локализация, поворот) и
  получил «Паттерны поведения!!! Причем тут контрастность темы и прочее гавно. Ты ищешь уже
  не то что нужно.» Темы в разрезе паттернов не открывай вообще.
- **Назвал компонент — отвечай про этот компонент свежим материалом.** После общего статуса
  он спросил: «Ты по кнопке что-то ещё интересное нашёл или даже не искал?» Отчёт без
  новых фактов именно по названному компоненту читается как «не искал». Из того прохода
  вышли шесть подтверждённых добавок по кнопке (банк — `references/ds-source-quotes.md`,
  раздел round 2).
- **Аудит — только чтение.** Пока идёт разбор: никаких записей в `data/*.json`, `out/*`,
  страницы и git; сначала список предложений, потом его «да» (это его постоянное правило).
- **Форма делегирования, которая подходит:** четыре группы по ~9–10 компонентов
  (элементы управления · навигация и выбор · слои и сообщения · контент и формы), каждый
  ребёнок только читает и возвращает JSON
  `{components:[{slug, items:[{behavior, case, quote, url, verified}]}], summary}`, с
  требованием ставить `verified: false`, если цитату подтвердить не удалось, и с рецептом
  выборки из `references/ds-source-quotes.md`.
- **Дешёвая самопроверка «чего не хватает»** — грепнуть тексты всех 209 паттернов по
  ключевым словам поведения (`data/*.json` → `patterns_ru` title+items). Но бакеты делай
  **поведенческими** (свайп, переполнение строки, клавиатура, состояния, пикер), а не
  тематическими. Числа сессии: 375/переполнение 32 из 38, тач-зона 31, прокрутка 25,
  доступность 22, состояния 21; «зона большого пальца» 2, «жесты» 3, «пикеры» 4 — низкие
  значения и есть кандидаты на добавление.
- **Кейс — это документированное поведение продукта с адресом** (справка продукта, блог
  дизайн-команды, страница дизайн-системы или статья названного специалиста): B&H Photo /
  Overcast / YouTube внутри статьи NN/g про свайпы, Walmart внутри статьи NN/g про закрытие
  оверлеев. «Все знают, что Gmail так делает» без проверяемого адреса — не кейс.

## Working with this owner on the pages

- He asks for it explicitly: **confirm understanding before doing anything**
  («Задача понятна? Сначала скажи что понятна»). Answer with a short numbered restatement
  of the request plus at most 1–2 crisp questions; then wait for the go-ahead.
- A **question is not permission to act** («Это был вопрос, а не разрешение к действию»).
  A remark/screenshot/«а что тут написано?» gets an answer in words first — read the page or
  data, quote what is actually there, name the contradiction you found — and only then
  propose the change. Acting first reads as sabotage.
- Execute literal instructions literally. «Поменяй название» = the heading only — the
  content stays; «добавь шторку на первый экран» = add it, not a redesign of both screens.
  Reading more into a one-line fix is what makes him furious.
- Once he says «делай дальше», continue the current task and finish the open items — but
  do not invent new scope.
- After an interruption (his «Продолжаем?») re-derive the state **from files**, not from
  the transcript: `python scripts/rework-status.py` (shipped with this skill) plus
  `python checks/check-patch.py` with no arguments. Twice the real state was «patches
  written, never merged, checker silently green» — a summary of what was *said* in the
  previous session would have been wrong. Then say in two lines where it stopped and
  continue; he is asking about the work, not for a status report format.

- Pilot **one** page (checkbox is the reference), show the URL, then roll out to the
  other 37 with subagents. A 38-page rework on a wrong reading is expensive.
- Report as a short list: what is done, what was verified by which script, what is
  still open — in Russian, in his words, no invented terminology.
- Never add work beyond the ask (no «докрутка»): extra sections, extra findings, extra
  fixes read as sabotage. Findings found nearby are listed, not fixed.
- **Presentation is part of the job — do not make him ask twice.** Right after the tabbed
  block landed came «Сам догадаться не можешь?» about an example plate that merged with the
  body text and a caption that was almost invisible. «Ничего сверх задачи» does not mean
  «leave the look half-done»: when a block is functionally finished, finish its appearance on
  your own — surface for the example, readable caption colour, overflow handled by arrows
  then report. Checking that the pieces are distinguishable at a
  glance belongs to «сделал», not to a follow-up request.

  - **He did not ask for the screens to be rewritten, and said so** («Я не просил ничего менять
    в экран»). Two liberties added up to that incident: (1) `apply_out.py` merged 37 prepared
    preview patches into the pages without rendering a single one first — before the merge the
    pages still carried the approved screens; (2) when he then said the two screens must match,
    the screens were *rewritten* (screen 2 := screen 1 markup) instead of the preview *content*
    being rebuilt. Rules that follow: render **one** merged page (screenshot or a harness number)
    before a batch merge; when a rule like «two identical screens» is broken, fix the source
    patches so the component is visible in real DS markup on both screens — never satisfy a rule
    by copying markup over content the owner already approved, and never report a copy as a fix.
    Saying «экраны я поменял, вернуть прежние нечем» is honest but late: check first.

  ## Git — nothing can be lost (2026-09-13, at his request)

  «Делай гит чтобы ничего не удалялось.» The repo now exists at the workspace root
  (`C:\Users\asukharev\GitHub\DS`, branch `main`, `core.autocrlf=false` so the CRLF
  `data/*.json` stay byte-identical on checkout). Covers `_audit/` (data, out, checks,
  platform), `iiko-ds-mobile/` (pages + components), `serve.py`, `.github`, `.gitignore` —
  1086 files in the first snapshot. `iiko-ds-web` and `iiko-ds-prototypes` are **their own**
  repos with GitHub remotes and sit in the root `.gitignore`; never `git add` inside them.

  - Commit every accepted change, then anything can be put back:
    `git checkout -- <path>` (one file), `git checkout -- .` (everything), `git diff` (what
    moved), `git log --oneline` (the trail).
  - This is the safety net that was missing when a merged preview round destroyed the approved
    screens — before the repo existed there was no way back, and that is exactly what he was
    angry about.
  - Windows/MSYS detail: native git rejects MSYS paths — `git -C /c/Users/...` answers
    `fatal: cannot change to …`. Pass `C:/Users/...` (forward slashes) or `cd` first.

  ## Page block order (2026-09-13)

  He moved the pattern block up: the order is now `На экране` → **`Примерные паттерны
  поведения`** → `Что меняется на мобиле` → `Почему так` → `Итог`. `Что меняется на мобиле`
  was **not** deleted — it moved down. One edit in `build.py`'s `page()` template + `python
  build.py`; a reorder must not touch content. The «Что|Правка» fields live inside the «На
  экране» block (`edits_panel()`), not in «Что меняется на мобиле», so moving that card does not
  break the field mechanism — confirm with `grep -c 'edit__input' <page>` after building, and
  check the order with `re.findall(r'<h2>(.*?)</h2>', html)` on all 38 pages.

## Паттерн — это СИТУАЦИЯ, а не рекомендация (2026-09-13)

Отбраковано владельцем дословно: «Это рекомендации, а не паттерны поведения. Ты нашёл вообще не
то что нужно.» Так нельзя: «подписывать кнопку действием, а не ОК», «недоступную кнопку не
прятать молча», «кнопка — не для перехода на другой экран». Это правила и гайдлайны — в
`patterns_ru` они не идут.

Паттерн = **конкретная ситуация на телефоне**: не влезло / уехало / перекрыто клавиатурой или
шторкой / элементов много / состояние (недоступно, загрузка, ошибка, пусто) / жест / потеря
введённого. Плюс «Что делают системы» с дословной цитатой НАЗВАННОЙ системы и «Что делать нам».

Образцы, которые он принял (по кнопке, по 3 части каждый):

- «Иконка-кнопка без подписи — смысл узнать неоткуда» — Android: «long press or hover over a
  view, useful for icon-based layouts» (developer.android.com/develop/ui/views/components/tooltips)
  + Apple HIG · Context menus с кейсом Files.
- «Кнопка впритык к нижнему краю — часть нажатий уходит в системный жест» — Apple HIG · Layout:
  «A safe area is essential to make sure system UI and hardware features like the Dynamic Island
  don't obstruct content and controls».
- «Действие в шапке — одной рукой не достать» — NN/g touch-target-size (MIT Touch Lab: подушечка
  1,6–2 см, большой палец ~2,5 см) + NN/g bottom-sheet: «the middle of the screen represents the
  most easily tappable area for the wide variety of ways users hold mobile devices».

## Дописывание: старое не удалялось и не удаляется (2026-09-13)

«Ещё раз. Старое не удаляем дописываем новое что нашли.» — существующие объекты `patterns_ru`
не менять (тексты, порядок, источники), только `append` в конец массива.

- Следствие: лимит `PAT-COUNT` в `check-patch.py` поднят с 6 до **24** (базовые 3–6 + дописанные).
- Доказательство неизменности: перед раундом `git add -A && git commit`; после — сверка
  `git show HEAD:_audit/rec/out/patterns/<slug>.json` и `git diff` (только добавленные строки).
- Форма раунда, которая пошла: семь писателей, каждый владеет своими слагами (6/6/5/5/5/5/6 =
  38 компонентов), вход `out/new-patterns/<slug>.json`, выход — тот же `out/patterns/<slug>.json`,
  самопроверка `python checks/check-patch.py <slug>` + сверка со снимком git.

## Разбор отчётов субагентов без чата (2026-09-13)

Готовые отчёты лежат по одному на ребёнка:
`%LOCALAPPDATA%\hermes\cache\delegation\subagent-summary-<i>-<дата>_<время>_<pid>.txt`,
JSON обычно внутри ```` ```json ````-блока. Если consolidated-сообщение в чат не пришло — брать оттуда,
а не ждать.

Скрипты в `_audit/rec/checks/`: `harvest-gaps.py` (разбор ревизий в `out/gaps-review.json`),
`make-gaps-digest.py` (сводка по компонентам в `out/gaps-digest.md` с фильтром «не по теме»),
`new-patterns-to-json.py <маска времени>` (раскладка найденного в `out/new-patterns/<slug>.json` +
сводка `out/new-patterns.md`).

Осторожно с фильтром по подстроке: шаблон `темн` ловит слово «сис**темн**ые жесты» — так
выжимка молча потеряла целый раздел. Фильтровать по фразе («тёмная тема»), а не по корню.

## Источники, которые реально открываются под цитату (2026-09-13)

- **Apple HIG — через JSON**: `curl -sL https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`
  (buttons, alerts, context-menus, pickers, layout, lists-and-tables — отвечают 200), затем
  `grep -o "фрагмент[^\"]\{0,200\}"`.
- **NN/g статьи, из которых уже взяты цитаты**: `touch-target-size` (MIT Touch Lab 1.6–2 cm /
  2.5 cm), `bottom-sheet` (нижняя зона не самая доступная), `accidental-overlay-dismissal`
  (кейс Walmart), `contextual-swipe` (B&H Photo / Overcast / YouTube), `cards-component`,
  `mobile-input-checklist`, `input-steppers`, `date-input`, `tooltip-guidelines`,
  `accordions-complex-content`.
- **Material/Carbon/Ant — raw.githubusercontent.com**: `docs/components/<comp>.md`,
  `src/pages/components/<comp>/usage.mdx`, `components/<comp>/index.en-US.md`; плюс m1/m2.material.io
  (bottom-sheets, dialogs, tooltips, steppers), GOV.UK (components + patterns), SAP Fiori,
  developer.android.com (tooltips, accessibility, window-size-classes, edge-to-edge).
- `carbondesignsystem.com` и HTML `developer.apple.com` отдают 403 — через `raw`/JSON, не воевать.
- HTML GOV.UK грепается не всегда (часть текста собирается скриптом) — искать поиском, а не `grep`
  по скачанной странице.

