# Recommendation pages (`_audit/rec`) — pipeline, verification, pitfalls

Repo: `C:\Users\asukharev\GitHub\DS`. Server: `python serve.py 8899` at repo root;
pages at `http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/<slug>.html`.

## Files

| Path | What it is |
|---|---|
| `_audit/rec/data/<slug>.json` | page-facing source for one component page (38 components) |
| `_audit/rec/data-tech/<slug>.json` | technical notes (sources, measurements) |
| `_audit/platform/<slug>.json` | platform research per component: `platforms.md3/angular/apple` (sizes + quotes + links), `not_recommended_ru`, `verdict_ru` — the only allowed source of numbers for the «Что говорят платформы» columns |
| `_audit/rec/build.py` | generator: data → `recommendations/<slug>.html`, `index.html`, `rec.css` |
| `_audit/rec/mock.py` | phone-screen builders: `status/head/body/foot/line/actions/lst/search/input_field/btn/iconbtn/checkbox/radio/toggle/tabs/sheet/card/card_head/chips/row/divider/icons/plain_icon/screen/phones/check_balance` |
| `_audit/rec/apply_out.py` | merges `out/{edits,previews,platforms}/<slug>.json` into `data/`, `--build` runs build.py |
| `_audit/rec/checks/*` | the audits (below) |
| `_audit/rec/out/SPEC*.md` | specs handed to subagents |

## Page anatomy (as agreed 2026-09)

1. `.compare` — Desktop / Mobile panels (Mobile panel is 375 px wide on purpose).
2. «На экране» — `.editrow` grid: **two** phone screens of *one and the same* app screen
   (component in the body on screen 1, in a sheet/header/card on screen 2; where it is
   not, the same rows stand without its controls) + the `Что | Правка` table as the third
   column. `build.py` injects `data-preview="edit"` into the second screen; live rules are
   written as `[data-mode="mobile"][data-preview="edit"].phone__screen <sel>{…}`, so
   edits never touch the panels or the first screen.
3. «Что меняется на мобиле» — three columns: Что / Desktop / Mobile (no «Правка» column).
4. «Что говорят платформы» — three columns: Material Design 3 / iOS HIG / Логика (от себя).
5. «Почему так», «Итог», «Найдено в ДС (в библиотеке не правим)».

Buttons: two buttons that fit go in a ROW (`.phone__foot`, or `.phone__actions` inside
`.phone__sheet` — the framework gives them `width:auto; flex:1 1 auto` and wraps only when
labels really do not fit). Column only when they cannot fit.

## Content rules the owner enforces

- Mobile column: digits, never «то же / та же / тот же / те же». Unchanged value =
  repeat the desktop numbers (`8 × 8 px — та же`, `12 / 16 px — тот же`).
- Each row whose Mobile cell has a number gets an edit field in the `Правка` table; rows
  with no numbers in either column stay empty (backdrop, divider, hint-tooltip, logo,
  scroll, status, table-2-lvl have no fields for that reason).
- Platform-column items cite the source in parentheses; no invented numbers.
- Menu/plugin names, captions and all page text are Russian, short, his wording.

## The audits (run them yourself, they are the proof)

```
cd C:\Users\asukharev\GitHub\DS\_audit\rec
python checks\check-patch.py <slug>       # validates subagent patch files: 2 screens,
                                          # balance, classes, component per screen,
                                          # selectors exist, «то же» replaced, interface equal
python checks\audit-edits.py             # live: every field really changes the 2nd screen
                                          # (MISS / NOCHANGE / LEAK / SCREENS)
python checks\audit-preview.py           # live: 2 screens, component on each, no overflow,
                                          # no clipped text, not empty, not duplicates
python checks\page-block.py <slug> ".editrow;.edits"   # where a block actually landed
python checks\why-nochange.py            # why a field does nothing (prints inline styles,
                                          # live <style> content, computed before/after)
python checks\why-rule.py                # which CSS rules win on an element
python checks\preview-sheet.py <slugs>   # contact sheet of previews into out/ (visual pass)
```

## Headless-Chrome harness pattern (and its two traps)

All live checks share one pattern: write a wrapper HTML into the served directory, embed one
iframe per page, collect results into `<pre id="out">`, then
`chrome --headless=new --disable-gpu --no-sandbox --virtual-time-budget=180000
--user-data-dir=<tmp> --dump-dom <wrapper-url>` and parse the `<pre>` in Python.

- **Trap 1 — empty `<pre>` looks like "0 defects".** The harness must actually write
  `OUT` into `#out` (`flush()` after every page). A harness that only pushes to an array
  reports a clean run while measuring nothing.
- **Trap 2 — measure after a delay.** Components with `transition` report the pre-change
  computed value synchronously → false `NOCHANGE`. Apply the value, wait ~700 ms, then
  measure (and measure *all* declared properties, including `padding`/`margin` shorthands —
  filtering shorthands out produced three bogus NOCHANGE reports).
- `getBoundingClientRect()` ignores clipping, so "element sticks out" must be filtered:
  skip elements inside an ancestor with `overflow: auto|scroll` (intended scrolling) or
  `overflow: hidden` whose box contains them. The phone screen itself is excluded.

## Screenshot verification

`chrome --headless=new --screenshot=<path> --window-size=W,H --hide-scrollbars <url>`, then
crop with PIL at coordinates measured by `page-block.py` (the block does not sit where you
guess — crop the measured y, not a guessed one). Cloning a card into another document
loses the DS stylesheets, so screenshot the page itself; and visual downscaling kills text,
so crop tight for detail and review whole pages only for gross layout.

## CSS cascade pitfalls behind "the edit does nothing"

- Inline `style=` in the page markup beats page-level rules → that field's `css` needs
  `!important` (case: autocomplete `.ds-menu-item { min-height:48px }` in the example markup).
- The mobile layer often sets a value with a longer selector
  (`.ds-stepper.ds-stepper--vertical .ds-step`) → the live rule must be at least as
  specific; the `[data-mode="mobile"][data-preview="edit"].phone__screen` prefix buys three
  compound selectors, which covers most cases.
- `<style id="live">` is the last stylesheet in `<head>`, so equal specificity goes to the
  page's rule.
- Framework-level fixes belong in `build.py` CSS, including mirrors for the «На экране»
  block (`.phone …`), because `.panel` rules do not reach the phone screens.

## HTML string surgery — cheap mistakes that cost hours

- `s.rstrip('</div></div>')` removes a character SET, not a suffix. Assert
  `s.endswith(x)` and slice `s[:-len(x)]`.
- After every edit assert `mock.check_balance(html) == (0, [])` and count
  `phones__item` and `class="phone__sheet"` (plain `phone__sheet` also matches
  `phone__sheet-title` / `-text`).
- Writing data back: `json.dumps(obj, ensure_ascii=False, indent=1)` + `"\n"`, then
  `.replace("\n", "\r\n")` — repo files are CRLF; `newline=""` when opening.

## Outsourcing the bulk to subagents (worked well)

- Spec per round in `_audit/rec/out/SPEC<N>.md`; keep the delta spec (SPEC3 extends SPEC2)
  instead of rewriting the whole thing.
- Children write ONLY their patch files; give them the exact self-check command and require
  0 problems; they must not run `build.py` or touch `data/`.
- Children finished in minutes and their reports claimed success — the real gate was the
  live audits run by the parent afterwards, which found the leftover
  `MISS`/`NOCHANGE` fields.
- Keep the same subdirs across rounds (`out/previews`, `out/edits`) and archive the previous
  round into `out/_old-*/` before a re-run so `check-patch.py` validates the new files only.
