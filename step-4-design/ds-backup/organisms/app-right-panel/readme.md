# app-right-panel — правая панель (организм)

Панель, появляющаяся справа: **обычная карточка (Card, Type=Shadow), только без скруглений углов**.
Содержимое — любое, его кладёт страница: формы, таблицы, настройки, табы, фильтры (слот контента).
Первый потребитель — шапка приложения (`organisms/app-header`): панель «Выберите ресторан» / «Уведомления»;
css/js организма она подтягивает автоматически.

## Подключение

```html
<link rel="stylesheet" href="../DS/organisms/app-right-panel/app-right-panel.css?v=2">
<script src="../DS/organisms/app-right-panel/app-right-panel.js?v=1" defer></script>
```

## Разметка (декларативно)

```html
<div class="app-rp-scrim ds-backdrop" data-rp-scrim="ID" hidden></div>
<aside class="app-rp" data-rp="ID" hidden aria-label="…">
  <div class="ds-card ds-card--shadow app-rp__frame">
    <div class="ds-card__header">
      <p class="ds-card__title app-rp__title">Заголовок</p>
      <span class="app-rp__close" role="button" tabindex="0" aria-label="Закрыть">
        <span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><span class="material-icons">close</span></span>
      </span>
    </div>
    <div class="ds-card__content">…контент…</div>
    <!-- подвал — когда нужны действия (как в сборке карточки — без разделителя;
         если разделитель нужен: <div class="ds-card__divider"></div> первым в подвале):
    <div class="ds-card__footer ds-card__footer--right">
      <div class="ds-card__footer__action">…кнопки…</div>
    </div>
    -->
  </div>
</aside>

<!-- триггер открытия — любой элемент: <button data-rp-open="ID">Открыть</button> -->
```

## Поведение и правила

- **Всё визуальное — от карточки**: фон, тень, паддинги, слоты (шапка / контент / подвал); **углы
  без скругления** («радиусы не нужны» — решение заказчика). Иконки — стандарт 20px
  (крестик — `ds-icon-size--5x`). Организм добавляет только: прижатие к правому краю контейнера,
  во всю высоту, скролл контента, строку шапки (заголовок + крестик-действие — по описанию Card:
  «действия справа кнопкой-иконкой») и затемнение (компонент Backdrop). Своих цветов/размеров у панели нет.
- **Ширина — по контенту** (узкая под форму, широкая под таблицу); фиксируется через
  `--app-rp-width` на `.app-rp` (например `style="--app-rp-width:500px"`).
- **Шапка остаётся на месте, контент скроллится**, подвал (если есть) — снизу
  (по макетам «Отчеты» 3576:29492 и 3907:14112).
- Закрытие: крестик, клик по фону (Backdrop), Esc. Открыта одна панель за раз.
- API: `AppRightPanel.open(id) / close(id) / closeAll()`; события на панели
  `app-rp-open` / `app-rp-close` (detail.id).
- Демо стенд — `demo.html`: каркас (кнопка «Открыть панель»); контент и подвал показаны как в карточке
  («Content title» / текст, кнопка «Подробнее» справа) — для понимания.
- Что добавлено «от себя» и открытые вопросы — журнал `DS/fixes.md` №105.
