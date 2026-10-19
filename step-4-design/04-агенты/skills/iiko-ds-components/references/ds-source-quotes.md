# Cited sources for the recommendation pages («Примерные паттерны поведения»)

How to get **verbatim, citable** design-system text on this host, and the quote bank
collected so far. The owner accepts no from-memory claims here: every pattern item
carries a quote or a named real case, and every column ends with a `src` line of
system names + URLs.

## Fetch recipe (works from this corporate Windows host)

| source | how | URL shape |
|---|---|---|
| Material (M3 / Material Web) | `web_extract` on the raw GitHub markdown | `https://raw.githubusercontent.com/material-components/material-web/main/docs/components/<comp>.md` |
| IBM Carbon | raw GitHub markdown of the docs site | `https://raw.githubusercontent.com/carbon-design-system/carbon-website/main/src/pages/components/<comp>/usage.mdx` (also `…/<comp>/style.mdx`) |
| Ant Design | raw GitHub markdown | `https://raw.githubusercontent.com/ant-design/ant-design/master/components/<comp>/index.en-US.md` |
| Shopify Polaris | markdown in `Shopify/polaris` | `shopify.dev/docs/api/polaris` for the human link |
| Apple HIG | `curl` the JSON the page itself loads | `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` |
| GOV.UK Design System, NN/g | `web_extract` straight away | `design-system.service.gov.uk/components/<comp>/`, `nngroup.com/articles/<slug>` |
| fast local bank | `_audit/rec/platform/<slug>.json` → `platforms.{md3,angular_material,ios_hig}` (`quote` + `source`, plus `touch_target_dp`, `verdict_ru`) | file name ≠ slug sometimes: `form-field→text-field`, `hint-tooltip→tooltip`, `radio→radio-button`, `table-2-lvl→table`, `text-ui→nearest` |

The docs sites themselves (`carbondesignsystem.com`, `developer.apple.com`) answer
`web_extract` with HTTP 403 — that is a WAF, not a broken tool: go to their markdown
mirrors / JSON endpoints, or `curl` in the terminal (curl gets the HIG JSON fine).
Apple's HTML pages render client-side, so the JSON is the only text you can quote.

**Three host details that silently break a fetch (2026-09-13).**

1. `curl` is a native Windows binary and does **not** understand MSYS paths: `-o
   /c/Users/.../file` exits 0 and writes a 0-byte file — the run looks fine and the grep
   finds nothing. Pass a native forward-slash path (`-o "C:/Users/…/harvest/x.md"`) and
   check the reported size (`-w "%{http_code} %{size_download}"`).
2. **One URL per terminal call.** A long compound loop/one-liner with several curls and
   `;`/`:` splits gets blocked by the command parser — fetch separately, then grep saved
   files.
3. Apple's HIG JSON is a **single line**, so `grep -F`/ripgrep returns the whole file.
   Pull the sentence window instead: `grep -o "Cancel[^\"]\{0,120\}" hig_alerts.json`
   (same for `destructive`, `two-word`, `primary role`).

Some product help pages are not fetchable as text (`support.google.com` answer ids we
had 404; `faq.whatsapp.com` timed out; `support.apple.com` guides render client-side) —
find the case through `web_search` and cite the article that documents it rather than the
help page itself.

## Quote bank — Button, round 2 (verified 2026-09-13)

Apple HIG · Alerts (`…/human-interface-guidelines/alerts.json`):

- «Cancel buttons are typically on the leading side of a row or at the bottom of a stack.»
- «…a two-word title that describes the result of selecting the button. Prefer verbs and
  verb phrases that relate directly to the alert text…»
- «…destructive style to identify a button that performs a destructive action people
  didn't deliberately choose.» · «…it's important to display an alert in case they
  initiated the action accidentally.»

Nielsen Norman Group · «OK-Cancel or Cancel-OK? The Trouble With Buttons» (Jakob Nielsen,
`nngroup.com/articles/ok-cancel-or-cancel-ok/`):

- «Should the OK button come before or after the Cancel button? Following platform
  conventions is more important than optimizing an individual dialog box.»
- «It's often better to name a button to explain what it does than to use a generic label
  (like "OK"). An explicit label serves as just-in-time help, giving users more confidence
  in selecting the correct action.»
- the same article: Windows puts OK first, Apple puts OK last.

Material Web · button (`…/docs/components/button.md`):

- «By default, disabled buttons are not focusable with the keyboard, while "soft-disabled"
  buttons are. Some use cases encourage focusability of disabled toolbar items to increase
  their discoverability.» (points at the W3C ARIA guidance on focusable disabled controls)

IBM Carbon · Button usage:

- «Do not use buttons as navigational elements. Instead, use links when the desired action
  is to take the user to a new page.»

These six are the Button additions worked out on 2026-09-13 — label instead of «OK», place
of «Отмена», two-word confirm label, confirm an irreversible destructive action,
soft-disabled instead of hiding a disabled button, button ≠ link. **Status: shown to him,
awaiting «да»; not yet in `patterns_ru`.**

## Quote bank — other components' behaviours (verified 2026-09-13)

- NN/g · «Using Swipe to Trigger Contextual Actions» (Angie Li,
  `nngroup.com/articles/contextual-swipe`): «Poorly implemented swipe-to-delete can lead to
  loss of data… it's important to always ask for confirmation or provide an easy way to
  undo the swipe.» Named cases in the same article: **B&H Photo** (one swipe revealed
  Remove from cart / Save for Later / Savings / Accessories — users never found them),
  **Overcast** (swipe alone does not delete; the Delete button must be pressed), **YouTube**
  (offers undo right after unsubscribing).
- NN/g · «Bottom Sheets: Definition and UX Guidelines» (Page Laubheimer,
  `nngroup.com/articles/bottom-sheet/`): «A common (but largely incorrect) rationale for
  using bottom sheets is that they improve reachability… the bottom of the screen is often
  not the most easily reachable screen region (the middle of the screen represents the most
  easily tappable area…)»
- NN/g · «Accidental Dismissal of Overlays» (Budiu / Behnam / Moran,
  `nngroup.com/articles/accidental-overlay-dismissal/`): dismissal methods differ (handle
  swipe, Back button, horizontal back-swipe on iOS and Android) and users pick the wrong
  one; the worked case is **Walmart**.
- NN/g · «Touch targets» (`nngroup.com/articles/touch-target-size/`): «A past study from the
  MIT Touch Lab found that the average person's fingertips are 1.6–2cm … The impact area of
  the typical thumb is even larger — an average of 2.5cm (1 inch) wide!»
- Apple HIG · Pickers (`…/pickers.json`): «Compact — A button that displays editable date and
  time content in a modal view.»
- Apple HIG · Layout (`…/layout.json`): «A safe area is essential to make sure system UI and
  hardware features like the Dynamic Island don't obstruct content and controls.»
- Android · `developer.android.com/design/ui/mobile/guides/layout-and-content/edge-to-edge`:
  «The edge-to-edge feature lets you draw the UI under the system bars for an immersive
  experience»; `…/compose/layouts/adaptive/window-size-classes`: Compact width «width <
  600dp, 99.96% of phones in portrait», Medium 600–840 dp, Expanded 840–1200 dp.

**Not pattern material — his call (2026-09-13).** Тёмная тема, контраст (WCAG 4.5:1),
локализация «+30 %» и безопасные зоны/поворот как самостоятельные темы были отвергнуты:
«Паттерны поведения!!! Причем тут контрастность темы и прочее гавно.» Держи такое вне
`patterns_ru`; если это важно для поведения компонента (например длинный перевод рвёт ряд
кнопок) — пиши это как поведение того компонента, а не как тему.

## What «mobile nuance» means per component

**Attribute the section, not the system.** The HIG full-width advice sits under the
`watchOS` heading — write «Apple HIG · Buttons · раздел watchOS», never «Apple требует
full-width в iOS». Getting this wrong is the same sin as inventing a quote.

## Verification protocol (do this before writing a quote)

1. Fetch the source into a file (`curl -sL … -o carb_<comp>.md` or save the
   `web_extract` content).
2. `grep -F "<the exact phrase you plan to quote>" <file>` — **0 hits means the quote
   does not exist**: drop it or find the real wording. Do not reword it into a quote.
3. Keep the URL you actually fetched next to the quote; the `src` line must show the
   system *and* that address.
4. If a platform has no number for something, say so in words — never fill the gap.

Real incident (2026-09): the first Button pattern set claimed Material says «Keep buttons
short so they can be side by side. Avoid stacking them when possible» and cited
`m3.material.io/components/tooltips` — the phrase has **0 hits** in the Material Web
buttons doc and the URL was a different component. It was replaced with the verified
HIG and Carbon lines below. A quote with a plausible-sounding URL is the failure mode
this protocol exists for.

## Quote bank — Button (verified 2026-09-13)

Apple HIG · Buttons (`developer.apple.com/design/human-interface-guidelines/buttons`):

- «As a general rule, a button needs a hit region of at least 44x44 pt — in visionOS,
  60x60 pt — to ensure that people can select it easily, whether they use a fingertip, a
  pointer, their eyes, or a remote.»
- «In general, use a button that has a prominent visual style for the most likely action
  in a view. … Keep the number of prominent buttons to one or two per view. Presenting too
  many prominent buttons increases cognitive load, requiring people to spend more time
  considering options before making a choice.»
- «Use style — not size — to visually distinguish the preferred choice among multiple
  options.»
- «A button's role can have additional effects on its appearance. For example, a primary
  button uses an app's accent color, whereas a destructive button uses the system red
  color.» · «Don't assign the primary role to a button that performs a destructive
  action, even if that action is the most likely choice.»
- «Always include a press state for a custom button. Without a press state, a button can
  feel unresponsive, making people wonder if it's accepting their input.»
- watchOS section: «Prefer buttons that span the width of the screen for primary actions
  in your app. Full-width buttons look better and are easier for people to tap. If two
  buttons must share the same horizontal space, use the same height for both, and use
  images or short text titles for each button's content.»
- hit region / touch target numbers: 44x44 pt (iOS), 60x60 pt (visionOS); visionOS-only
  size scale 28/32/44/52/64 pt — see `_audit/rec/platform/button.json`.

IBM Carbon · Button usage (`carbondesignsystem.com/components/button/usage`):

- «Each page should have only one primary button. Any remaining calls to action should be
  represented as lower emphasis buttons.»
- «When the button's label is too long to fit within the available space of the button,
  the label should overflow and wrap to the second line. We do not recommend truncating a
  button label.» (same page advises the «{verb} + {noun}» content formula)
- «Fluid width buttons are always preferable to fixed width default buttons in a layout.
  When possible, set the button container's relative position to the responsive layout
  grid and match the button width to the width of other elements on the page. Ideally,
  when using groups of related buttons … they should all be the same width.» — the
  alignment table gives «Full-span» to dialogs, side panels and small tiles and notes the
  current code caps full-span at 320 px.
- «Buttons can have inline loading that provides visual feedback that the action is in
  process. The button would be disabled when inline loading is in progress.»
- «In some cases a button group—or even a single button in the case of a side panel or
  small tile—may span the entire width of a window or container.» (nested button locations:
  banner CTAs, dialogs, wizards, forms, cards, toolbars)

IBM Carbon · Menu buttons / overflow
(`carbondesignsystem.com/components/menu-buttons/usage`):

- «Menu buttons, including menu buttons, combo buttons, and overflow menus, open a menu
  with a list of interactive options.»
- «The icon button of overflow menu is treated as the ghost button, displaying only an
  icon and following its designated color and style.»

Ant Design · Button (`ant.design/components/button`):

- «Primary button: used for the main action, there can be at most one primary button in a
  section.»
- «loading: adds a loading spinner in button, avoids multiple submits too.»
- «danger: used for actions of risk, like deletion or authorization.»

Material Web · button (`…/material-web/main/docs/components/button.md`): five types
(elevated, filled, filled tonal, outlined, text), 40 dp default container height; the
48 dp touch target lives in `button/internal/_touch-target.scss` (`max(48px, 100%)`), and
Angular Material keeps `$touch-target-size: 48px` — i.e. the drawn button may be 40 dp
while the tappable box must stay 48 dp.

## What «mobile nuance» means per component

The 3–6 patterns must cover the component's real mobile failure modes, not only
overflow: what runs off the 375 px screen and how systems solve it · what the finger
misses (< 48 dp / 44 pt) · what the on-screen keyboard covers · what stops being legible
on a narrow screen · long labels and long values · many items (scrolling, depth) ·
disabled / loading / error / empty · destructive actions · accessibility (labels, roles,
not colour alone). Name the real product when it illustrates the case (Gmail, Slack,
Notion, Figma, Stripe) — but only as a case, never instead of a source.
