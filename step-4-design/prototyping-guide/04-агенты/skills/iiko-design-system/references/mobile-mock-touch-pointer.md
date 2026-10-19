# Тач вместо курсора в макетах ДС (блок «На экране»)

Два разных элемента, владелец просил оба — не путать:

| Что | Где | Зачем |
|---|---|---|
| **Живой кружок** `.phone__touch` | внутри каждого `.phone__screen`, следует за мышью | курсор мыши на мобильном макете заменён «пальцем» — «Я не вижу что у меня поменялся курсор от мышки на тач» |
| **Статичная метка** `.pat__hit::before` | примеры паттернов, где показан тап | показывает, куда попадает палец («на мобиле нужно показать не курсор, а кружок который имитирует тач») |

Размер — 44 px: усреднённая подушечка пальца, она же минимум хит-региона у Apple HIG
(«a button needs a hit region of at least 44x44 pt»). Невидимая зона нажатия 48 px
(MD3, `Button_DS/button-touch.css`) остаётся слоем CSS — кружок это только показ.

## Живой кружок (курсор)

CSS — в собственные стили примера (не в общий агрегатор: его перезаписывает генератор):

```css
@media (hover:hover) and (pointer:fine){
  .phone__screen,.phone__screen *{cursor:none}
}
.phone__touch{position:absolute;left:0;top:0;width:44px;height:44px;border-radius:50%;
              transform:translate(-50%,-50%);pointer-events:none;z-index:9;display:none;
              background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 22%,transparent)}
.phone__touch--press{background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 38%,transparent)}
```

JS — в шаблон страницы (`page()`), рядом с блоком, который сообщает высоту оболочке:

```js
(function () {
  if (!window.matchMedia || !window.matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  [].slice.call(document.querySelectorAll('.phone__screen')).forEach(function (screen) {
    var dot = document.createElement('div');
    dot.className = 'phone__touch';
    screen.appendChild(dot);
    function place(e) {
      var r = screen.getBoundingClientRect();
      dot.style.left = (e.clientX - r.left) + 'px';
      dot.style.top = (e.clientY - r.top) + 'px';
      dot.style.display = 'block';
    }
    screen.addEventListener('pointermove', place);
    screen.addEventListener('pointerover', place);
    screen.addEventListener('pointerleave', function () { dot.style.display = 'none'; });
    screen.addEventListener('pointerdown', function () { dot.classList.add('phone__touch--press'); });
    screen.addEventListener('pointerup', function () { dot.classList.remove('phone__touch--press'); });
  });
})();
```

Капканы:

- **Шаблон `page()` — %-форматирование.** Литерального `%` в JS/CSS быть не должно
  (`64 %%` иначе `TypeError`), поэтому плотность кружка задаётся не `opacity`, а
  `color-mix(… 22%, …)` — знак процента внутри `color-mix` остаётся литеральным.
- Кружок создаётся **по одному на экран** — на двух экранах блока их два; курсор скрыт и у
  самого экрана, и у кнопок/полей внутри (`cursor:pointer`/`text` из ДС иначе покажет стрелку).
- На тач-устройстве скрипт молчит (`matchMedia('(hover:hover) and (pointer:fine)')`), там палец настоящий.
- Скрипт встроен в страницу, поэтому владельцу говорить про **Ctrl+Shift+R** — иначе он «не видит,
  что поменялось» (CSS подтянется по `?v=<mtime>`, а инлайновый JS нет).

## Статичная метка тапа

```css
.pat__hit{position:relative;display:inline-flex;margin:0 10px}
.pat__hit::before{content:"";position:absolute;left:50%;top:50%;width:44px;height:44px;
                  transform:translate(-50%,-50%);border-radius:50%;pointer-events:none;z-index:2;
                  background:color-mix(in srgb,var(--ds-palette-accent-500,#448AFF) 22%,transparent)}
```

- **Поверх кнопки, не под ней.** На мобиле все размеры кнопки — 44 px высоты
  (`components-mobile/components/Button_DS/button-touch.css`: M/S/XS = 44), поэтому маркер,
  нарисованный под кнопкой, не виден вовсе (замер: кнопки 53×44 и 56×44 — кружок совпадал с кнопкой).
- Пунктирный квадрат 48 px `border-radius:8px` — **устаревший вид**, владелец от него отказался.
- Метка стоит только там, где показан тап: `.pat__hit` в `example_html` — сейчас это 9 компонентов
  (button, button-icon, banners, badge, icon-size, hint-tooltip, chips, stepper, tree). Правило живёт
  в общем CSS, поэтому разметку менять не нужно — подхватывается всеми страницами.

## Замер пробой (проверено 14.09.2026)

Синтетические PointerEvent из страницы-пробы (iframe, same-origin через `http://127.0.0.1:8899`):

```js
var ev = new w.PointerEvent('pointermove', { clientX: r.left + 120, clientY: r.top + 300, bubbles: true });
scr.dispatchEvent(ev);
```

Полученные числа (Button):

- `matchMedia('(hover:hover) and (pointer:fine)')` = `true` (headless Chrome ведёт себя как десктоп);
- экранов 2, `.phone__touch` в них 2 — по одному на экран;
- кружок `44px × 44px`, `border-radius 50%`, `left/top` = позиция указателя, фон
  `color(srgb 0.267 0.541 1 / 0.22)`;
- `cursor` = `none` и у экрана, и у кнопки внутри;
- `pointerdown` → `color(… / 0.38)` и класс `phone__touch--press`, `pointerup` → снова 0.22,
  `pointerleave` → `display:none`;
- статичные метки: по 2 кружка на экран в паттерне «Кнопка-иконка без подписи» и по 4 в
  «Зона нажатия минимум 44 pt» (тело + шторка, оба экрана зеркально).

Готовый раннер — `scripts/probe-page.py` (без него проба собирается руками: iframe + `<pre id="out">`,
`--dump-dom` в файл, разбор Python-регуляркой).

## Капканы прогона, на которых я потерял время

- **`--screenshot` в одном запуске с `--dump-dom`** снимает кадр до того, как проба досчитает: кружок
  на скриншоте не появился, хотя замер его видел. Скриншот — отдельным запуском (в `probe-page.py`
  это режим `--shot`).
- `sed -n '/<pre id="out">/,/<\/pre>/p'` по потоку `--dump-dom` матчит ещё и исходник инлайнового
  скрипта (в тексте пробы есть та же строка) и печатает мусор — сохранять дамп в файл и разбирать
  регуляркой в Python.
- Джейл терминала на очень длинные однострочные команды: пробу писать файлом (`write_file`) и
  запускать `bash <файл>`, а не собирать всё в одну строку.

## Цитаты владельца

- «На мобиле нужно показать не курсор, а кружок который имитирует тач. Размер наверное 44 px,
  кажется усредненное значение для усреднённого пальца.»
- «Я не вижу что у меня поменялся курсор от мышки на тач» (после того, как я сделал только статичную
  метку: нужен был именно живой курсор).
- «Ты сделал на 2 экранах мобилы же?» — проверять и докладывать числами, что оба экрана (левый
  рекомендованный и правый с правками) показывают одно и то же.
