# Оболочка страниц рекомендаций: геометрия, замер, пробники

Всё ниже — с прогонов 12.09.2026 (`_audit/rec/build.py` → `iiko-ds-mobile/prototypes/recommendations/`).
Цель файла: следующий сеанс меряет «как у остальных» и не повторяет путь из пяти итераций.

## 1. Как устроена оболочка (index.html)

```
.wrap (body padding 24)
├── h1 «Компоненты: Desktop → Mobile»
└── .kit (grid 260px minmax(0,1fr), gap 20)
    ├── nav.nav           260 px, sticky, 38 пунктов (высота ~1480)
    └── div                 ← колонка страницы
        ├── iframe.frame   страница компонента (width 100 %)
        └── div.card       блок «Общее для всех компонентов» (6 абзацев .point)
```

Правила каркаса, которые держат геометрию (константа `CSS` в `build.py`):

- `.frame{width:100%;border:0;display:block;min-height:600px;background:transparent}`
- `.kit .card{margin:16px 24px 0}` — блок встаёт по сетке страницы компонента (в её теле `body{padding:24px}`)
- `.card` — общий блок: белый фон, рамка 1 px `--ds-color-stroke-default`, `--ds-radius-3x`, паддинг 16

Замеренные края при окне 1920: колонка страницы 304…1896, контент внутри фрейма и блок пояснений — **329…1870**
(24 px с каждой стороны). Если у окна появляется вертикальная полоса прокрутки (страница выше окна), у обоих
краёв становится **1855** — одинаково у блока и у карточки над ним, это не расхождение.

## 2. Пиксельный замер краёв и отступов (единственный честный для «как выглядит»)

Фон оболочки и страницы компонента одинаковый — `#f4f5f7`. Поэтому скан строки даёт края, а скан столбца — стыки:

```python
from PIL import Image
BG = (244, 245, 247)

def runs_nonbg(px, w, h, x0=340, x1=1850, step=3):
    """Полосы контента в колонке страницы: строки, где есть хоть один не-фоновый пиксель."""
    rows = []
    for y in range(h):
        non = False
        for x in range(x0, x1, step):
            r, g, b = px[x, y]
            if abs(r-BG[0]) > 4 or abs(g-BG[1]) > 4 or abs(b-BG[2]) > 4:
                non = True; break
        rows.append(non)
    runs, start = [], None
    for y, nn in enumerate(rows):
        if nn and start is None: start = y
        elif not nn and start is not None:
            runs.append((start, y-1)); start = None
    if start is not None: runs.append((start, h-1))
    return runs

def white_span(px, w, y):           # края белой карточки в строке
    xs = [x for x in range(300, w) if px[x, y] == (255, 255, 255)]
    return (min(xs), max(xs)) if xs else None
```

Как читать результат: `runs[-1]` — блок пояснений, `runs[-2]` — последняя карточка страницы компонента.
Отступ = `runs[-1][0] - runs[-2][1]`; края — `white_span` на середине каждой полосы. **Сравнивать края блока
с краями карточки над ним, а не с чем-то «по смыслу».** Скрин — свежим профилем:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --no-first-run \
  --no-default-browser-check --user-data-dir="$LOCALAPPDATA/Temp/udd_x" --virtual-time-budget=12000 \
  --window-size=1920,3700 --screenshot="$LOCALAPPDATA/Temp/p.png" \
  "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/index.html#<slug>"
```

38 страниц — примерно две минуты (3–5 с на страницу), разбивать на партии по 19 в одном вызове.

Числа, которые должны получиться: отступ **17 px** на всех 38 (16 px margin + строка рамки; внутренние
промежутки страницы 17/18/21), края блока = края карточки над ним. Было до правок: 57 / 58 / 76 / 93 / 109 px.

## 3. `fit()` — история одной высоты

```js
// Вариант 1 (сломанный): у корневого элемента scrollHeight НИКОГДА не меньше высоты фрейма.
// Как только фрейм оказался выше контента (например высота посчитана на load до загрузки
// Roboto/Material Icons), значение «залипает» и уменьшиться уже не может → лишнее вылезает
// отступом под блоком пояснений (57/58/76/93/109 px по страницам).
frame.style.height = Math.max(d.documentElement.scrollHeight, 600) + 'px';

// Вариант 2: у body высота по содержимому — но у страницы снизу ещё свои 24 px padding
// и 16 px отступ последней карточки, и они тоже попадают в отступ блока (57 px вместо 17).
var h = Math.max(d.body.scrollHeight, 600);

// Финальный: высота = низ последнего блока страницы.
var wrap = d.querySelector('.wrap');
var last = wrap ? wrap.lastElementChild : null;
var bottom = last ? last.getBoundingClientRect().bottom + (d.documentElement.scrollTop || 0)
                  : d.body.scrollHeight;
frame.style.height = Math.max(Math.ceil(bottom), 600) + 'px';
```

Плюс пересчёт, а не один замер на `load`:

```js
function watch() {
  var d = frame.contentDocument;
  if (!d || !d.body) return;
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(fit);
  setTimeout(fit, 300);
  if (window.ResizeObserver) {
    if (frame.__ro) { try { frame.__ro.disconnect(); } catch (e) {} }
    frame.__ro = new ResizeObserver(fit);
    frame.__ro.observe(d.body);
  }
}
frame.addEventListener('load', function () { fit(); watch(); });
```

**Обязательная пара к обрезке** — инжектируемый в фрейм стиль (`#embedded-fix`) с `html,body{overflow:hidden}`.
Без него обрезанный фрейм получает внутреннюю полосу прокрутки: она отнимает 15 px ширины, контент страницы
перестаёт совпадать по краям с блоком (329…1855 против 329…1870) и в кадре видна полоса.

## 4. Пробники: как прочитать числа из headless-прогона

- **`--dump-dom` отдаёт DOM по событию `load`.** Таймеры (`setTimeout`) к этому моменту не выполнялись,
  поэтому асинхронный пробник печатает `<pre id="out">` пустым. Рабочий приём — **мерить синхронно в `onload`
  самого `iframe`**: его `load` наступает раньше `load` родителя, результат успевает попасть в дамп.
  Пробник живёт рядом со страницами (`_audit/rec/checks/_probe*.html`), `src` iframe — относительный путь
  `../../../iiko-ds-mobile/prototypes/recommendations/<slug>.html`, всё через `serve.py 8899` (same-origin).
- **Нужны значения «после загрузки шрифтов» — рисуй их текстом на странице и снимай скрин.** Асинхронный
  сценарий (`await fonts.ready` → `await wait(600)` → запись в `<pre>`) в `--dump-dom` не виден, а в скриншоте
  виден: `--screenshot` + `--virtual-time-budget=60000`, `<pre>` покрупнее — числа читаются (проверено: frameH /
  scrollH / lastBottom / inside / noteGap / total по 6 страницам за один прогон).
- **Вложенный `iframe` врёт про `scrollHeight`.** Если мерить оболочку внутри ещё одного iframe, `documentElement.scrollHeight`
  вернёт уже установленную высоту фрейма (1380 = низ + 40), и вывод «отступ одинаковый» будет ложным.
  Для «что видно» — только пиксельный замер.
- Меню оболочки переключается без интерактива: `iframe.src = 'index.html#' + slug` (хэш вызывает `activate()`).

## 5. grep-рецепты «токен объявлен vs читается»

```bash
# что CSS вообще читает
rg -o --no-filename 'var\(\s*(--ds-hint[a-z0-9-]*)' iiko-ds-web/components/Hint-Tooltip_DS \
  iiko-ds-mobile/components/Hint-Tooltip_DS | sed 's/var(\s*//' | sort -u
# где ещё встречается имя токена (кроме tokens.css)
rg -l -- '--ds-hint-arrow-width' --glob '!tokens.css'
```

Если имя живёт только в `tokens.css` и в `iiko-ds-spec.md` — правил с ним нет нигде, токен мёртвый.
Разбор Hint/Tooltip (8 из 25 мёртвых + радиус на прозрачной обёртке) — секция Pitfalls в SKILL.md.

## 6. Отчёт владельцу по геометрии

Формат, который он принимает: «было X → стало Y» одной строкой на признак, по **всем** страницам, и отдельно —
из чего складывается число (16 px margin + строка рамки). Не подставлять «объяснимо» вместо «как у остальных» и не
давать таблицы `getComputedStyle` без перевода на то, что видно на экране.
