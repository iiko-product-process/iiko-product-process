# Button — desktop → mobile case study (first component on the mode axis)

Worked example for the `iiko-ds-components` skill. Everything here was measured in a
browser or read from a file; nothing was invented.

## Sources actually used

| Source | What it gave |
|---|---|
| A former comparison page (removed from the repo) | Figma `Button_mob` values, transcribed by hand earlier: 138×44 px, HUG/HUG, radius 8, padding 16 h / 12 v, text 16 px / 500, icon 20 px (vector 12×12), accent `#448AFF` |
| `components-mobile/desktop-to-mobile-plan.md` | Button = category A («только размерные значения»), «Частично общая» token binding |
| `components-mobile/mobile-mode-notes.md` §12 | `modes.css` + load order; `tokens.css` is generated |
| `components-web/tokens.css` (collection `Component`) | Existing size tokens — pad/gap/icon-size/text-size/text-weight per `xs|s|m`, `--ds-button-border-radius`, `--ds-button-border-size` |
| `components-web/iiko-ds-spec.md` (`#### Button`) | Desktop sizes M 36 / S 28 / XS 24, states default/hover/pressed/disabled/loading |

Reference numbers from the comparison page (for the design discussion, not for implementation):
MD3 filled = 40 dp tall, pill radius 20 dp, pad 24 dp, label 14 sp/500, icon 18 dp, primary
fill. iOS = 44 pt tall, capsule ~14 pt, pad ~16 pt, body 17 pt/600, icon 24 pt. Ours: 44 px,
8 px radius, 16/12 pad, 16 px/500 — i.e. iOS height, DS radius (the pill question is open).

## Token table (implemented)

| Token | Desktop | Mobile | Note |
|---|---|---|---|
| `--ds-button-m-size-pad-top` / `-bottom` | `--ds-space-2x` (8) | `--ds-space-3x` (12) | in `modes.css` |
| `--ds-button-m-size-pad-left` / `-right` | `--ds-space-3x` (12) | `--ds-space-4x` (16) | in `modes.css` |
| `--ds-button-m-size-text-size` | `--ds-typography-body-font-size-s` (14) | `--ds-typography-body-font-size-m` (16) | in `modes.css` |
| height (derived) | 36 | **44** | `calc(pad-top + pad-bottom + line-height 20)` |
| `-size-gap`, `-size-icon-size`, `border-radius`, colours | 8 · 20 · 8 · shared | unchanged | not touched |

S/XS are **not** changed by the mode — that is deliberate (Figma's `Button_mob` is the M
size) and is also the biggest open question: on mobile their 28/24 px targets sit below the
44 px minimum.

## Files touched

- `components-web/modes.css` (new) — mode axis + Button block.
- `components-web/components/Button_DS/button.css` — sizes moved to component tokens; heights
  derived with `calc()`; new `.ds-btn--full-width`; two latent bugs fixed (below).
- `Prototypes/button-modes.html` (new) — desktop/mobile side by side (three views:
  both / desktop only / mobile only) plus a table of measurements produced by the page's own
  JS (`document.body.dataset.measure`).
- `components-web/iiko-ds-spec.md` — TOC entry 8, new section «Режимы платформы (Desktop /
  Mobile)», `--full-width` added to the `.ds-btn` class-map row.

## Latent bugs found in the shipped `button.css`

1. A comment had swallowed a selector: `.ds-btn--xs /* … */ .ds-btn__label {` — parsed as
   the descendant selector `.ds-btn--xs .ds-btn__label`.
2. A second `.ds-btn__icon { font-size: 20px }` block, later in the file than the XS rule,
   won the cascade → the XS icon rendered 20 px instead of the DS's 16 px.

Both were invisible in review and only surfaced through measurement.

## Measured regression (old `button.css` from git HEAD vs new)

45 combos (3 sizes × 5 styles × 3 types), same markup, same tokens.css:

- **all heights identical** — 24 / 28 / 36 px, and no padding, font-size, weight,
  letter-spacing, radius or border-width change;
- `xs` icon: 20 px → **16 px** (fix #2), which also shrank the XS button width 101.98 → 95.31 px;
- line-height: XS 12 → 16 px, S/M 14 → 20 px — this is what makes the `calc()` height true
  and matches Figma's HUG text container; the text stays centred, so nothing moves visually.

Mobile mode, same page: M 44 px (touch ok), S 28, XS 24 (below the 44 px minimum).

## Open questions handed back to the owner

1. S / XS on mobile: leave 28/24, or add a 48 dp touch wrapper (Angular Material does this
   with a `::before` overlay on `.mat-mdc-icon-button`)?
2. Hover on touch: wrap hover rules in `@media (hover: hover)` (also changes desktop-wide
   behaviour) or accept the sticky hover after a tap?
3. Mobile M stays 44 px (Figma, iOS) or moves to Material's 48 dp?
4. Radius: Figma `Button_mob` keeps 8 px while MD3/iOS use a pill — confirm before the
   mobile layer looks like "a desktop button, only taller".
5. `Button group_mob` and `Bottom action bar_mob` (both already exist in Figma) are the
   structural step: stack the group, sticky footer, full-width primaries.
6. The spec's «Полные CSS-стили» and `components/index.css` do not include `modes.css` yet —
   the generator needs a line for it when it is next regenerated.
