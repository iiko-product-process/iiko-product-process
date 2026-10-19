# Шторки страниц рекомендаций: заглушки → разметка компонента

Класс работы (15.09.2026): в блоке «На экране» страниц `iiko-ds-mobile/prototypes/recommendations/`
шторка (`.phone__sheet`) была нарисована строками-заглушками — `phone__row`/`phone__list` или строками
списка с посторонней иконкой (`restaurant`) вместо самого компонента. Задача владельца: «в каждой —
заменить строки-заглушки на разметку компонента, как в Checkbox и Radio». Это инвариант блока
«На экране»: компонент настоящей разметкой ДС должен быть виден и в теле экрана, и в шторке.

## 0. Прежде чем править — проверить, что работа не сделана

Сессия часто начинается с «делай» после согласия в предыдущей. Предложение найти через `session_search`,
но состояние работы определять **файлами**, а не историей: данные и страницы живут в git, а сборка
оставляет mtime.

```bash
cd /c/Users/asukharev/GitHub/DS
git status --short | head -80          # что уже тронуто
ls -lt --time-style=+%m-%d_%H:%M _audit/rec/data/*.json | head -50
```

Дифф целиком не работает: дамп JSON отличается стилем (отступы/переводы строк), поэтому «изменён весь
файл». Сравнивать **по полям**:

```python
def head(p):
    s = subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8').stdout
    return json.loads(s)
diff = [k for k in set(a)|set(b) if a.get(k) != b.get(k)]   # у Checkbox/Radio это был ['preview_html']
```

Так видно точный след правки: у восьмёрки (List, Status, Select, Menu, Card, Badge, Search, Form field)
`preview_html` не был тронут — шторки оставались заглушками.

## 1. Запись JSON в его собственном стиле

Файлы `_audit/rec/data/*.json` писались разными прогонами: часть — `indent=1` + CRLF, часть — `indent=2` + LF.
Стиль определять и воспроизводить **байт-в-байт**, иначе в диффе появляется весь файл:

```python
def style_of(raw):
    d = json.loads(raw.decode('utf-8'))
    for ind in (1, 2, 4):
        for nl in ('\r\n', '\n'):
            cand = (json.dumps(d, indent=ind, ensure_ascii=False) + '\n').replace('\n', nl).encode('utf-8')
            if cand == raw:
                return d, ind, nl
    raise SystemExit('стиль не распознан')
```

Проверка после правки: `git status` показывает на каждый тронутый файл ровно `1 insertion / 1 deletion`
(одна огромная строка `preview_html`), а число изменённых файлов растёт только на те, что реально правились
(было 55 → стало 61 = шесть новых файлов данных, страницы в счёт не идут — их длинные строки уже были
изменены сборкой).

## 2. Замена блока шторки

`preview_html` несёт два экрана, поэтому блок шторки встречается дважды. Порядок:

1. балансным парсером (`<div` / `</div>`) вырезать все блоки `phone__sheet`;
2. утверждать, что они идентичны (`assert len(set(blocks)) == 1`) — иначе правка одной шторки молча
   разъедет экраны (это же ловит `checks/check-patch.py`, правило `PREV-INTERFACE`);
3. из старого блока взять `phone__sheet-title`, `phone__sheet-text` и блок `phone__actions` (тоже балансно);
4. собрать `<div class="phone__sheet">` + заголовок + текст + новая разметка + actions + `</div>`;
5. `h.replace(old, new)` — заменит сразу оба экрана.

Для Search «новая разметка» = поле `ds-search` **плюс** прежний список результатов (`mid` между текстом
и actions): результат остаётся, к нему добавляется поле компонента.

## 3. Разметка по компонентам (что взято)

| Компонент | Разметка в шторке |
|---|---|
| List | `ds-list-container` → `__item`: `__element-left` с `ds-list-item__icon` (`person`), `__content` (`label-up` + `text`), `__element-right` (`label-down` «18 заказов») |
| Status | столбик из `ds-status ds-status--{neutral,positive,warning,negative} ds-status--filled` с `__icon` (`edit`/`check_circle`/`schedule`/`error`) и `__label` |
| Select | `ds-select-container` → `__search` (`ds-input ds-input--s` с полем) + `ds-select-item--true` (выбранное) и `--false` |
| Menu | `ds-menu-container` (style `min-height:0`) → `ds-menu-item` `style="width:auto"`, `__icon`, столбик `__label-up` + `__text`; опасный — `style="color:#FF5252"` |
| Card | `ds-card ds-card--outlined` `style="width:100%"` → `__header` (`label-up` + `h3.ds-card__title` + `label-down`) + `__content` |
| Badge | строки `ds-list-container__item` без левой иконки: `__content` + `__element-right` со `ds-badge--counter--negative` / `ds-badge--point--accent`, третья строка — без знака |
| Search | `ds-search` со значением (`span` с `style="color:var(--ds-color-text-primary,#333333)"`) и `__right-icon` (close) + прежний список результатов |
| Form field | `ds-input ds-input--m` → `__frame` → `__content` (`ds-input__label` + `input.ds-input__field` с `placeholder`) |

Готовые примеры разметки брать со **своей же страницы**: `examples[].html` и `patterns_ru[].example_html`
в `data/<slug>.json` (у Menu и Select там есть даже примеры со шторкой).

Подписи под экранами (`phone__caption`) обязаны совпадать с нарисованным: у Card и Badge они обещали
обратное («в шторке те же строки без карточки», «шторка уведомлений пока без знаков») — после правки
переписаны.

## 4. Проверки (все выполнялись)

1. `json.load` каждого файла + дифф по полям против `HEAD` → изменён только `preview_html`
   (у Select/Form field до нас был тронут `changes` из `apply-values.py` — это чужое).
2. Блоки `.phone__body` / `.phone__head` / `.phone__status` / `.phone__foot` из текущего файла и из
   `git show HEAD:` — сравнить, тело обязано совпасть (см. капкан про строковую замену).
3. `python _audit/rec/build.py`, затем grep собранных страниц на новые классы (`ds-menu-item__label-up`,
   `ds-card--outlined`, `ds-badge--counter`, …) — по всем восьми.
4. Скриншот сетки: временная страница в `_audit/rec/checks/_sheets.html` с превью всех правленых
   компонентов (те же CSS-ссылки, что у страницы `build.py`, `zoom:0.52–0.62`) → headless Chrome
   `--window-size=1000,1900 --screenshot=…`, затем зрение. После прогона временные страницы удалить.
5. Цвета варианта ДС — против его же примеров на той же странице: временная страница со шторкой и
   `examples[0].html`, замер `getComputedStyle(...).backgroundColor` обоих наборов через `--dump-dom`.
   У Status вышло одинаково: neutral `rgb(250,250,250)`, positive `rgb(243,252,247)`,
   warning `rgb(255,252,248)`, negative `rgb(255,248,248)`, высота плашки 24 px — то есть в шторке
   настоящий вариант `--filled`, а не подбор цвета.
6. Отчёт владельцу — картинкой на Рабочий стол («Шторки — 8 компонентов после правки.png»),
   путь полным текстом, плюс команда отката `git checkout -- <восемь файлов> && python _audit/rec/build.py`.

## 5. Факты библиотеки, которые всплыли

- `.ds-list-container` и `.ds-list-item` держат **ширину числом 258 px** (`iiko-ds-web/components/List_DS/`),
  мобильного правила ширины у списка нет; ширина листа шторки — 327 px (телефон 375 − 2×8 корпус − 2×16 паддинг),
  внутренняя — 327. Поэтому значения/знаки в строках List, Badge, Search заканчиваются за 69 px до правого края
  листа, а длинная подпись переносится на вторую строку. **В теле экрана ровно так же** — это значение библиотеки,
  а не следствие правки. Растянуть строки = правка каркаса (`rec.css` из `build.py`), затронет все страницы;
  сам не делать — докладывать числами и ждать решения.
- У Select и Menu мобильный слой сам даёт `width:100%` (`iiko-ds-mobile/components/Select_DS`, `Menu_DS`),
  поэтому их блоки в шторке на всю ширину — расхождение с List не наше.
- `rec.css` содержит `.phone .ds-list-container, .phone .ds-menu-container, .phone .ds-select-container { min-height: 0 }` —
  замороженные `min-height` библиотеки внутри макета гасить не нужно.

## 6. Капканы

- **Строковая замена фрагмента бьёт и по телу экрана.** Замена фрагмента `__element-left` + иконка сняла
  иконки и в теле обоих экранов Badge (12 вместо 6). Восстанавливать по признаку строки (у тела есть
  `ds-list-item__label-up`, у шторки нет), затем сверять тело блоками с `HEAD`.
- **Длинный heredoc с кавычками не доезжает до python.** Скрипт на ~130 строк с одинарными кавычками в
  разметке уронил bash (`unexpected EOF while looking for matching \'\'`). Писать такие скрипты файлом
  (`write_file` в `%LOCALAPPDATA%\Temp\fix_sheets.py`) и запускать нативным путём
  (`python "C:/Users/asukharev/AppData/Local/Temp/fix_sheets.py"`).
- **Русский текст в коде `browser_exec` ломает stdin** (CLI читает ввод в кодовой странице — `UnicodeDecodeError`).
  Для замеров в этом репо рабочий путь — headless Chrome и `--dump-dom` с пробой-страницей в
  `_audit/rec/checks/` (числа в `<pre id="out">`), а `--screenshot` отдельным запуском.
- Секундомер по кадру: у макета высота 720 px, лист шторки — absolute bottom, поэтому длинная разметка
  (три строки списка по 72 px + заголовок + текст + кнопки ≈ 350 px) влезает спокойно; проверять глазами
  на сетке скриншотов, а не верить расчёту.
