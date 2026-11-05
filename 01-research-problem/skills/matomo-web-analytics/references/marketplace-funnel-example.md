# Worked example: marketplace purchase funnel in Matomo

Scenario (iiko web app, 2026-09): a marketplace where restaurant employees browse partner
apps, open app cards, connect an app, pick restaurants + tariff, pay, then set the app up.
Goals: (a) which app cards get viewed most, (b) funnel per individual app.

## Event schema

| Field | Value | Example |
|---|---|---|
| Category | `Marketplace` (fixed, never changes) | `Marketplace` |
| Action | step from fixed enum | `connect_click` |
| Name | stable app key (slug/catalog code) | `delivery-pro` |
| Value | optional, numeric (tariff price, restaurant count) | `2990` |

Step enum (fix in code, never rename — event names live forever):

1. `catalog_view` — entered the marketplace catalog (can be derived from pageview of `/marketplace` instead of an event)
2. `card_view` — app card opened
3. `connect_click` — "Подключить" clicked
4. `plan_selected` — restaurants + tariff chosen
5. `payment_submit` — "Оплатить" clicked
6. `setup_start` — app setup screen reached
7. `app_connected` — app connected

## JS helper

```js
function trackMarketplace(step, appId, value) {
  _paq.push(['setCustomDimension', CD_APP_ID, appId]); // Action-scope CD "AppId"
  if (value !== undefined) {
    _paq.push(['trackEvent', 'Marketplace', step, appId, value]);
  } else {
    _paq.push(['trackEvent', 'Marketplace', step, appId]);
  }
}
```

`CD_APP_ID` is the numeric Custom Dimension id (Administration → Websites → Custom Dimensions).
For card pageviews also set it before `trackPageView` so the Pages report is segmentable by app.

## What the product manager sees

- **Overall funnel**: Reports → Events → Category `Marketplace`; rows = steps; always read the
  unique-visitors column (nb_uniq_visitors), not visits (visits are counted per event action).
- **Card popularity**: Actions → Pages on card URLs (`/marketplace/app/{id}`) with readable
  unique `document.title` like `Маркетплейс — {App name}`; optional Content Tracking for
  shown-vs-clicked (impressions / interactions / interaction rate); CD AppId segment on any report.
- **Per-app**: drill into an Action row → Name subtable lists apps with counts; or segment by
  Event Name / CD AppId; combine with the restaurantId CD (visit scope) and date range.

## Export — build per-app funnels yourself

```
index.php?module=API&method=Events.getAction&idSite=N&period=month&date=2026-08
  &secondaryDimension=eventName&flat=1&format=JSON
```

Returns rows "action × name" with nb_events, nb_uniq_visitors, sum_event_value
(verified against `plugins/Events/API.php` — `secondaryDimension` ∈
{eventAction, eventName, eventCategory}; also `Events.getCategory/getName`).
Pivot in pandas/Excel → step×app table; step N→N+1 conversion ≈ uniq visitors(N+1)/uniq(N).
Segments: restaurant CD (`segment=customDimension<id>==<restaurantId>`), userId, date range.

## Premium upgrade path

Funnels plugin (paid): one funnel "Marketplace connect" with steps on `Event Action equals
<step>`; per-app either via segment "Event Name = app" or per-app funnels created through the
Funnels HTTP API (unlimited funnels/steps). Step conditions also accept URL/path/title with
equals/contains/starts/ends. No re-tagging needed — the free event schema feeds the plugin as-is.

## Acceptance-mapping checklist (stage-style gates)

- All marketplace routes (catalog, card, checkout, setup) fire tracking; no dead zones.
- No duplicate tracking requests (dev StrictMode, button disabled during request, single handler).
- `document.title` unique and readable per card page.
- Sum of per-app event counts ≈ overall event counts for the same period.
- Events visible in Visitors → Visits Log with correct category/action/name.
- Authorized sessions carry restaurantId CD on every pageview and event.
