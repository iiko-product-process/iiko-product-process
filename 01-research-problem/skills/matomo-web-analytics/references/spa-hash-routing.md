# SPA «только /index»: диагностика и фиксы (проверено 2026-09 на analytics.iiko.services)

## Симптом
Веб-SPA (iiko web): каждый раздел — свой каталог `<restaurant>.iikoweb.ru/<module>/index.html`,
экраны внутри раздела — хэш-роуты `…/index.html#/<route>` (customer-screen/list, settings/display,
controls/list). В Matomo «Страницы» показывает на раздел ОДИН лист `/<module>/index.html`,
экраны не разделяются — пользователь видит «только /index».

## Root cause
Matomo срезает URL-фрагмент `#…` при записи. На инстансе у сайта «iiko prod» в
`SitesManager.getSiteFromId` стоит `keep_url_fragment: 0`. Приложение при этом УЖЕ шлёт
`trackPageView` на каждый переход роута (2,5–3 pageview/визит — видно по nb_hits/nb_visits),
но URL не меняется (фрагмент теряется) → все экраны раздела сливаются в одну строку.

## Диагностика (порядок проверок, прежде чем обещать «постраничный» отчёт)
1. **Есть ли под-пути вообще**: `Actions.getPageUrls` `flat=1` + `filter_pattern` на `#`, на
   фрагменты роутов (`list`, `settings`, `controls`…) за весь период трекинга. Пусто → под-роуты
   не записываются никогда.
2. **Где экран мог уцелеть** (проверить все три):
   - titles: `Actions.getPageTitles` с ТОЧНЫМ сегментом `pageUrl==<полный url>` (не `=@`) —
     на iiko по customer-screen только название модуля («Advertise screens»), «Page Name not
     defined» (~40%) и хвост чужих заголовков → title экраны НЕ различает.
   - события: `Events.getAction` (`pageUrl=@…`) — на iiko только служебные
     `bounce_pagehide`/`bounce_visibilitychange`, продуктовых нет.
   - контент-группы: `Contents.getContentNames` — пусто.
3. **Вывод**: если пусто во всех трёх — информация об экране потеряна при ingest. Никакой
   «умный» рендер отчёта (учёт/чистка index) это не восстановит: report-side может лишь
   косметически чистить `index.html` в подписях, разделять нечего. Отвечать честно:
   «постранично нельзя, пока не починен трекинг». Историю не пересчитать; сравнение до/после
   некорректно ещё ~неделю после фикса.

## Фикс A — без кода, ТОЛЬКО статичные хэш-роуты
Admin → Websites → сайт → Edit → «Keep Page URL fragments when tracking Page URLs»
(per-site; есть и глобальная «Global websites settings»). API: `SitesManager.updateSite`
`keep_url_fragment=1`. URL начнут писаться `…/index.html#/<route>` → постраничность появится,
но строки с `#` и `index.html` посередине (иерархия некрасивая). НЕ годится при динамических
сегментах (`#/edit/12345`): кардинальность взорвётся — каждый объект станет отдельной строкой.

## Фикс B — рекомендуемый, любой роутинг
Переопределять URL перед каждым `trackPageView` через `setCustomUrl`, строя путь из
КОНФИГУРАЦИИ роутера (шаблон маршрута), а не из сырого `location.hash`. Динамические сегменты
схлопывать в константу (`:id` → `_id` или удалять) → страница = строка, объекты не плодят строки.
Плюс уникальный читаемый `document.title` на экран (иначе растёт «Page Name not defined»).
После фикса иерархия: `customer-screen → list`, `customer-screen → edit/_id`, `settings → display`.

Angular-сниппет (подписка на переходы + сборка статичного пути):
```ts
router.events.pipe(filter(e => e instanceof NavigationEnd)).subscribe(() => {
  _paq.push(['setCustomUrl', buildRoutePath(router.routerState.root)]);
  _paq.push(['setDocumentTitle', document.title]);
  _paq.push(['trackPageView']);
});

function buildRoutePath(snapshot: ActivatedRouteSnapshot): string {
  const parts: string[] = [];
  let s: ActivatedRouteSnapshot | null = snapshot;
  while (s) {
    if (s.routeConfig?.path) parts.unshift(s.routeConfig.path); // 'customer-screen/list', 'edit/:id'
    s = s.parent;
  }
  const path = '/' + parts.filter(Boolean).join('/');
  return path.replace(/:[^/]+/g, '_id'); // '/customer-screen/edit/123' -> '/customer-screen/edit/_id'
}
```
Первый экран при загрузке тоже гнать через тот же хук. Если нужна аналитика ПО ОБЪЕКТАМ
(какой именно редактировали) — это события / action-scope CD, не URL (см. marketplace-funnel-example).

## Инстанс-квирки (проверено)
- `Live.getLastVisits` через MCP-мост → HTTP 400 (и с сегментом, и без; Live на инстансе не
  отдаёт визит-лог) — фактическую разметку проверять через Actions/Events-отчёты.
- Единственная настроенная Custom Dimension: id=1 «Store ID» (action scope, extraction пустой).
- Сайт «iiko prod»: `keep_url_fragment: 0`, трекинг полный с 20.08.2026.
