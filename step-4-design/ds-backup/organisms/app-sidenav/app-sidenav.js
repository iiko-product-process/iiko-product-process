/* app-sidenav.js — боковое меню приложения (организм): рейл L1 + панель L2.
   Один источник разметки и данных на все страницы-прототипы — «вставил и у всех одно и то же».
   Вставляется в .panel перед .frame (как app-header). ≥760 — рейл в кадре во всю высоту:
   шапка и кадр начинаются правее меню (макет 59160:21175); <760 — шторка поверх страницы
   (макет «Адаптив»): открывается бургером шапки (событие app-snav-toggle), закрывается ✕
   в шапке меню, кликом по затемнению или Esc.

   Поведение — по макету DS «Взаимодействие с меню» (Iiko-Web-DS, узел 59160:36140):
     • клик по разделу L1 — открывается его L2 (раздел выделяется фоном + белый индикатор слева);
     • повторный клик по открытому разделу или крестик в шапке L2 — закрывает L2 (индикатор гаснет);
     • «Свернуть меню» — переключает L1 200 ↔ 52; открытая панель L2 при этом не закрывается;
     • у разделов с L2 стрелка наведения: в раскрытом меню — справа, у открытого — в обратную
       сторону; в свёрнутом — вместо иконки; там же тултип с названием раздели.

   Данные меню (состав, тексты, Info-блоки) — объект MENU ниже: ЕДИНСТВЕННОЕ место правок.
   Состав — как в макете ДС; у разделов без нарисованного L2 (пока у большинства) панель не
   открывается, стрелка не показывается — ждём макет.

   Разметка собрана из классов ДС (ds-sidenav-view/header/control/item/footer, ds-badge,
   ds-divider, ds-element-sidenav). Недостающее в ДС закрыто локально в app-sidenav.css
   (помечено «пробел ДС №N») и в журнале DS/fixes.md (пп. 56–67). Иконки — Material Icons Outlined по имени;
   трёх глифов (Кухня, API, Администрирование) в шрифте нет — они лежат файлами в app-sidenav/.

   Страховка подключений: если страница забыла подключить ДС (font/tokens/styles/components/fixes)
   или иконки — скрипт достроит их сам (см. ensureDsLinks), чтобы меню нигде не «рассыпалось».

   API для страниц и демо стенда (app-sidenav/demo.html): window.AppSidenav. */
(function () {
  'use strict';

  /* ── Данные меню (единственное место правок состава и текстов) ────────────────
     item: { id, label, icon — имя Material Icons | iconSvg — файл в app-sidenav/,
             badge? — пилюля («Pro») или счётчик («17»), badgeStyle? — Style бейджа из ДС
             (accent — синий «Pro» по макету | positive — зелёный счётчик «Склад» по макету),
             avatar? — инициалы, l2? — панель второго уровня }
     l2.items: { label, arrow?, divider? } | { group:true, label, expanded?, children:[{label, selected?}] }
     l2.info:  [{ title, text }] — блоки подсказок в сером контейнере (Text UI из макета) */
  var MENU = {
    version: 'ver: 7.8.6.29440',
    items: [
      { id: 'pos', label: 'Касса и зал', icon: 'point_of_sale' },
      { id: 'kitchen', label: 'Кухня', iconSvg: 'icon-kuhnya.svg' },
      { id: 'menu', label: 'Меню и цены', icon: 'menu_book', l2: {
        title: 'Меню и цены',
        items: [
          { label: 'Меню ресторана', divider: true },
          { label: 'Меню для внешних заказов', arrow: true, divider: true },
          { group: true, label: 'Номенклатура', expanded: true, children: [
            { label: 'Комбо-наборы' },
            { label: 'Изменение цен по приказу', selected: true },
            { label: 'Актуальные цены' }
          ] }
        ],
        info: [
          { title: 'Создавайте меню', text: 'Чтобы лучше понимать их предпочтения и предлагать персонализированный сервис' },
          { title: 'Управляйте номенклатурой', text: 'Чтобы привлечь больше гостей и увеличить прибыль ресторана.' },
          { title: 'Следите за актуальностью цен', text: 'Чтобы поощрять постоянных гостей и увеличивать их возвращаемость в ваш ресторан.' }
        ]
      } },
      { id: 'delivery', label: 'Доставка', icon: 'delivery_dining', l2: {
        title: 'Доставка',
        items: [
          { label: 'Внешние курьеры', divider: true },
          { label: 'Зоны доставки', arrow: true, divider: true }
        ],
        info: [
          { title: 'Настраивайте зоны доставки', text: 'Чтобы лучше понимать их предпочтения и предлагать персонализированный сервис' },
          { title: 'Подключайте службы внешних курьеров', text: 'Чтобы привлечь больше гостей и увеличить прибыль ресторана.' },
          { title: 'Следите за актуальностью цен', text: 'Чтобы поощрять постоянных гостей и увеличивать их возвращаемость в ваш ресторан.' }
        ]
      } },
      { id: 'staff', label: 'Сотрудники', icon: 'group' },
      { id: 'stock', label: 'Склад', icon: 'warehouse', badge: '17', badgeStyle: 'positive' },
      { id: 'api', label: 'API и интеграции', iconSvg: 'icon-api.svg' },
      { id: 'admin', label: 'Администрирование', iconSvg: 'icon-admin.svg' },
      { id: 'loyalty', label: 'Лояльность', icon: 'favorite', l2: {
        title: 'Лояльность',
        items: [
          { label: 'Показатели', divider: true },
          { group: true, label: 'Гости', expanded: true, children: [
            { label: 'Вход и регистрация' },
            { label: 'База гостей' },
            { label: 'Сегменты' }
          ] },
          { group: true, label: 'Программа лояльности', expanded: true, children: [
            { label: 'Управление акциями' },
            { label: 'Бонусно-ранговая система' },
            { label: 'Электронная карта', selected: true }
          ] }
        ],
        info: [
          { title: 'Создайте базу гостей', text: 'Чтобы лучше понимать их предпочтения и предлагать персонализированный сервис' },
          { title: 'Настраивайте акции', text: 'Чтобы привлечь больше гостей и увеличить прибыль ресторана.' },
          { title: 'Создавайте карты лояльности', text: 'Чтобы поощрять постоянных гостей и увеличивать их возвращаемость в ваш ресторан.' },
          { title: 'Управляйте бонусами и рангами', text: 'Чтобы поощрять постоянных гостей и повышать их лояльность к вашему ресторану.' }
        ]
      } },
      { id: 'biz', label: 'Бизнес', icon: 'analytics', badge: 'Pro' },
      { id: 'fin', label: 'Финансы', icon: 'payments', badge: 'Pro' }
    ],
    footer: [
      { id: 'market', label: 'Маркетплейс', icon: 'storefront' },
      { id: 'help', label: 'Центр помощи', icon: 'support_agent' },
      { id: 'user', label: 'Константин Константин', avatar: 'КК' }
    ]
  };

  var AB = 'app-sidenav/';   /* путь до ассетов меню — уточняется по адресу самого скрипта */
  var state = { collapsed: true, openId: null, drawerOpen: false };
  var panel = null, root = null, l2view = null, hintEl = null, scrim = null, tipEl = null;
  var renderedId = null;     /* какой раздел сейчас собран в L2 — чтобы не пересобирать DOM на каждый update() */

  /* ── Разметка ──────────────────────────────────────────────────────────────── */

  function iconHTML(it) {
    if (it.avatar) {
      return '<span class="app-snav__avatar"><img src="' + AB + 'avatar-kk.svg" width="20" height="20" alt="">' +
             '<span class="ds-element-sidenav__label app-snav__avatar-text">' + it.avatar + '</span></span>';
    }
    if (it.iconSvg) {
      return '<img class="app-snav__icon-img" src="' + AB + it.iconSvg + '" width="20" height="20" alt="">';
    }
    return '<span class="material-icons" aria-hidden="true">' + it.icon + '</span>';
  }

  function itemHTML(it) {
    var h = '<div class="ds-sidenav-item ds-sidenav-item--l1 ds-sidenav-item--expanded app-snav__item"' +
            ' role="button" tabindex="0" data-section="' + it.id + '"' + (it.l2 ? ' data-l2="1"' : '') +
            ' aria-label="' + it.label + '">';
    h += '<span class="app-snav__content">';
    h += '<span class="app-snav__icon">' + iconHTML(it) + '</span>';
    h += '<span class="ds-sidenav-item__label app-snav__label">' + it.label + '</span>';
    if (it.badge) h += '<span class="ds-badge ds-badge--counter ds-badge--' + (it.badgeStyle || 'accent') + ' app-snav__badge">' + it.badge + '</span>';
    h += '</span>';
    if (it.l2) h += '<span class="material-icons app-snav__arrow" aria-hidden="true">chevron_right</span>';
    if (it.badge) h += '<span class="ds-badge ds-badge--point ds-badge--' + (it.badgeStyle || 'accent') + ' app-snav__dot" aria-hidden="true"></span>';
    h += '<span class="app-snav__indicator" aria-hidden="true"></span>';
    h += '</div>';
    return h;
  }

  function l1HTML() {
    var h = '<div class="ds-sidenav-view app-snav__l1">';
    h += '<div class="ds-sidenav-header ds-sidenav-header--l1 ds-sidenav-header--expanded app-snav__head">' +
           '<img class="app-snav__logo" src="' + AB + 'logo-iiko-white.svg" width="56" height="24" alt="iiko">' +
           '<img class="app-snav__mark" src="' + AB + 'logo-iiko-mark.svg" width="24" height="24" alt="iiko">' +
           '<span class="app-snav__close" role="button" tabindex="0" aria-label="Закрыть меню"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><span class="material-icons">close</span></span></span>' +
         '</div>';
    h += '<div class="ds-sidenav-control ds-sidenav-control--expanded app-snav__control" role="button" tabindex="0"' +
           ' aria-label="Свернуть или развернуть меню">' +
           '<span class="ds-sidenav-control__content">' +
             /* шеврон сворачивания — без ховер-подложки: иконка внутри строки-кнопки, подложка — только самостоятельным иконкам-триггерам (№99) */
             '<span class="app-snav__collapse"><span class="ds-icon-size ds-icon-size--4x"><span class="material-icons" aria-hidden="true">chevron_left</span></span></span>' +
             '<span class="ds-sidenav-control__label">Свернуть меню</span>' +
           '</span>' +
           '<span class="app-snav__divider"></span>' +
         '</div>';
    h += '<div class="app-snav__body">' + MENU.items.map(itemHTML).join('') + '</div>';
    h += '<div class="app-snav__foot"><span class="app-snav__divider"></span>' + MENU.footer.map(itemHTML).join('') + '</div>';
    h += '</div>';
    return h;
  }

  function l2HTML(sec) {
    var h = '<div class="ds-sidenav-header ds-sidenav-header--l2 ds-sidenav-header--expanded app-snav__l2head">' +
              '<span class="ds-sidenav-header__label app-snav__l2title">' + sec.l2.title + '</span>' +
              '<span class="app-snav__l2info" role="button" tabindex="0" aria-label="Подсказка по разделу"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><span class="material-icons">info</span></span></span>' +
              '<span class="app-snav__l2close" role="button" tabindex="0" aria-label="Закрыть меню раздела"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><span class="material-icons">close</span></span></span>' +
            '</div>';
    h += '<div class="app-snav__l2body"><div class="app-snav__l2items">';
    sec.l2.items.forEach(function (it) {
      if (it.group) {
        h += '<div class="ds-sidenav-item ds-sidenav-item--l2 app-snav__l2group" role="button" tabindex="0">' +
               '<span class="ds-sidenav-item__label app-snav__l2label">' + it.label + '</span>' +
               '<span class="material-icons app-snav__grarrow" aria-hidden="true">keyboard_arrow_down</span>' +
             '</div>';
        h += '<div class="app-snav__l3' + (it.expanded === false ? ' app-snav__l3--collapsed' : '') + '">';
        (it.children || []).forEach(function (ch) {
          h += '<div class="ds-sidenav-item ds-sidenav-item--l3 app-snav__l3item' + (ch.selected ? ' app-snav__l3item--selected' : '') + '"' +
                 ' role="button" tabindex="0">' +
                 '<span class="ds-sidenav-item__label app-snav__l3label">' + ch.label + '</span>' +
                 '<span class="app-snav__l3indicator" aria-hidden="true"></span>' +
               '</div>';
        });
        h += '</div>';
      } else {
        h += '<div class="ds-sidenav-item ds-sidenav-item--l2 app-snav__l2item" role="button" tabindex="0">' +
               '<span class="ds-sidenav-item__label app-snav__l2label">' + it.label + '</span>' +
               (it.arrow ? '<span class="material-icons app-snav__l2arrow" aria-hidden="true">keyboard_arrow_right</span>' : '') +
             '</div>';
        if (it.divider) h += '<span class="ds-divider"></span>';
      }
    });
    h += '</div>';
    if (sec.l2.info && sec.l2.info.length) {
      h += '<div class="app-snav__info"><div class="app-snav__info-box">';
      sec.l2.info.forEach(function (bl) {
        h += '<div class="app-snav__info-item">' +
               '<span class="app-snav__info-title">' + bl.title + '</span>' +
               '<span class="app-snav__info-text">' + bl.text + '</span>' +
             '</div>';
      });
      h += '</div></div>';
    }
    h += '</div>';
    h += '<div class="ds-sidenav-footer ds-sidenav-footer--l2 ds-sidenav-footer--expanded app-snav__l2foot">' +
           '<img src="' + AB + 'logo-iiko.svg" width="38" height="16" alt="iiko">' +
           '<span class="app-snav__vdiv" aria-hidden="true"></span>' +
           '<span class="ds-sidenav-footer__label">' + MENU.version + '</span>' +
         '</div>';
    return h;
  }

  /* ── Состояние ─────────────────────────────────────────────────────────────── */

  function findItem(id) {
    for (var i = 0; i < MENU.items.length; i++) if (MENU.items[i].id === id) return MENU.items[i];
    return null;
  }

  function swap(el, prefix, variant) {
    if (!el) return;
    el.classList.remove(prefix + 'collapsed', prefix + 'expanded');
    el.classList.add(prefix + variant);
  }

  function update() {
    if (!root) return;
    var open = state.openId;
    var adaptive = panel.clientWidth < 760;               /* <760 — режим шторки; на 760 и шире меню стоит в кадре */
    var collapsed = state.collapsed && !adaptive;         /* в шторке L1 всегда раскрыт */
    var variant = collapsed ? 'collapsed' : 'expanded';

    root.classList.toggle('app-snav--drawer', adaptive);
    root.classList.toggle('app-snav--l1collapsed', collapsed);
    root.classList.toggle('app-snav--l1expanded', !collapsed);
    root.classList.toggle('app-snav--l2open', !!open);
    panel.classList.toggle('app-snav-on', !adaptive || state.drawerOpen);
    panel.classList.toggle('app-snav-drawer-on', adaptive && state.drawerOpen);

    swap(root.querySelector('.app-snav__head'), 'ds-sidenav-header--', variant);
    swap(root.querySelector('.app-snav__control'), 'ds-sidenav-control--', variant);

    var ctlIcon = root.querySelector('.app-snav__collapse .material-icons');
    if (ctlIcon) ctlIcon.textContent = collapsed ? 'chevron_right' : 'chevron_left';

    var items = root.querySelectorAll('.app-snav__item');
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      swap(it, 'ds-sidenav-item--', variant);
      var isOpen = it.getAttribute('data-section') === open;
      it.classList.toggle('app-snav__item--open', isOpen);
      var ar = it.querySelector('.app-snav__arrow');
      if (ar) ar.textContent = isOpen ? 'chevron_left' : 'chevron_right';
    }

    var w = (state.collapsed ? 52 : 200) + (open ? 260 : 0);
    panel.style.setProperty('--app-snav-w', w + 'px');
    panel.style.setProperty('--app-snav-dw', (panel.clientWidth <= 480 ? 280 : 300) + 'px');

    var sec = open ? findItem(open) : null;
    if (sec && sec.l2) {
      /* Пересобираем содержимое ТОЛЬКО при смене раздела. update() зовётся на каждый
         pointerup/click (адаптив), и пересборка innerHTML прямо во время клика рвёт жест:
         mousedown и mouseup попадают в разные узлы → click не рождается, кнопки L2 «мертвы». */
      if (renderedId !== open) {
        l2view.innerHTML = l2HTML(sec);
        renderedId = open;
        tipHide();                                  /* панель пересобрана — тултип закрываем */
      }
      l2view.hidden = false;
    } else {
      state.openId = null;
      renderedId = null;
      l2view.hidden = true;
      tipHide();
    }
    hintHide();
  }

  /* ── Действия ──────────────────────────────────────────────────────────────── */

  function toggleSection(id) {
    if (!id) return;
    var it = findItem(id);
    if (!it || !it.l2) return;                          /* у раздела нет L2 — ждём макет */
    state.openId = (state.openId === id) ? null : id;
    update();
  }

  function closeL2() { state.openId = null; update(); }
  function toggleCollapsed() { state.collapsed = !state.collapsed; update(); }

  /* Шторка (адаптив <760): меню поверх страницы, открывается бургером шапки */
  function isAdaptive() { return !!panel && panel.clientWidth < 760; }
  function openDrawer() { if (!isAdaptive()) return; state.drawerOpen = true; update(); }
  function closeDrawer() { state.drawerOpen = false; update(); }
  function toggleDrawer() {
    if (!isAdaptive()) return;
    state.drawerOpen = !state.drawerOpen;
    update();
  }

  function toggleGroup(g) {
    var l3 = g.nextElementSibling;
    if (!l3 || !l3.classList.contains('app-snav__l3')) return;
    var collapsed = l3.classList.toggle('app-snav__l3--collapsed');
    g.classList.toggle('app-snav__l2group--collapsed', collapsed);
  }

  function onClick(e) {
    var inf = e.target.closest ? e.target.closest('.app-snav__l2info') : null;
    if (inf) { tipShow(inf); return; }                 /* ⓘ — тултип (клик — для тач-устройств) */
    if (tipEl && tipEl.classList.contains('is-on')) tipHide();   /* клик мимо иконки — тултип закрыт */
    var x = e.target.closest ? e.target.closest('.app-snav__close') : null;
    if (x) { closeDrawer(); return; }                  /* ✕ в шапке меню-шторки */
    var g = e.target.closest ? e.target.closest('.app-snav__l2group') : null;
    if (g) { toggleGroup(g); return; }
    var cl = e.target.closest ? e.target.closest('.app-snav__l2close') : null;
    if (cl) { closeL2(); return; }
    var ctl = e.target.closest ? e.target.closest('.app-snav__control') : null;
    if (ctl) {                                         /* в шторке «Свернуть меню» закрывает шторку */
      if (isAdaptive()) closeDrawer(); else toggleCollapsed();
      return;
    }
    var it = e.target.closest ? e.target.closest('.app-snav__item') : null;
    if (it) toggleSection(it.getAttribute('data-section'));
  }

  function onKeydown(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var t = e.target;
    if (t && t.getAttribute && t.getAttribute('role') === 'button' && /app-snav/.test(t.className)) {
      e.preventDefault();
      t.click();
    }
  }

  /* Тултип свёрнутого меню: один слой на всё меню (внутри прокручиваемого списка его режет overflow) */
  function hintShow(it) {
    if (!state.collapsed || isAdaptive() || !hintEl) return;
    var lbl = it.querySelector('.app-snav__label');
    hintEl.querySelector('.ds-hint-content__label').textContent = lbl ? lbl.textContent : (it.getAttribute('aria-label') || '');
    var r = it.getBoundingClientRect();
    hintEl.style.left = (r.right + 8) + 'px';
    hintEl.style.top = (r.top + r.height / 2) + 'px';
    hintEl.classList.add('is-on');
  }

  function hintHide() { if (hintEl) hintEl.classList.remove('is-on'); }

  /* Тултип у иконки ⓘ (шапка L2): компонент Hint-Tooltip из ДС — ds-hint-container + ds-hint-content.
     Текст — заглушка: финальные формулировки подсказок подставляются в TIP_TEXT (или из данных MENU). */
  var TIP_TEXT = 'Текст подсказки';
  function tipShow(el) {
    if (!tipEl) return;
    var lbl = tipEl.querySelector('.ds-hint-content__label');
    if (lbl) lbl.textContent = TIP_TEXT;
    var r = el.getBoundingClientRect();
    var left = Math.round(r.left + r.width / 2 - 125);      /* 125 — половина ширины 250px из ДС */
    left = Math.max(8, Math.min(left, (window.innerWidth || 0) - 258));
    tipEl.style.left = left + 'px';
    tipEl.style.top = Math.round(r.bottom + 8) + 'px';
    tipEl.classList.add('is-on');
  }
  function tipHide() { if (tipEl) tipEl.classList.remove('is-on'); }

  function onOver(e) {
    var inf = e.target.closest ? e.target.closest('.app-snav__l2info') : null;
    if (inf) { tipShow(inf); return; }
    var it = e.target.closest ? e.target.closest('.app-snav__item') : null;
    if (it) hintShow(it); else hintHide();
  }

  function onOut(e) {
    if (!e.target.closest) return;
    if (e.target.closest('.app-snav__l2info')) tipHide();
    if (e.target.closest('.app-snav__item')) hintHide();
  }

  /* ── Страховка подключений ДС ────────────────────────────────────────────────
     Страница должна подключать ДС (font/tokens/styles/components/fixes) и иконки Material.
     Если что-то забыли — достроим, чтобы меню в любом случае выглядело одинаково.
     (Мобильный слой components-mobile сюда не входит — его подключают страницы сами; меню — десктопное.) */
  function addLink(href) {
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = href;
    (document.head || document.documentElement).appendChild(l);
  }

  function hasClassicIcons() {
    var ls = document.querySelectorAll('link[href]');
    for (var i = 0; i < ls.length; i++) {
      var h = ls[i].getAttribute('href') || '';
      if (h.indexOf('family=Material+Icons') >= 0 && h.indexOf('+Outlined') < 0) return true;
    }
    return false;
  }

  function ensureDsLinks() {
    var dsBase = AB + '../../components-web/';   /* соседний репозиторий ДС (из папки app-sidenav на два уровня вверх) */
    var files = ['font.css', 'tokens.css', 'styles.css', 'components/index.css', 'fixes.css'];
    for (var i = 0; i < files.length; i++) {
      if (!document.querySelector('link[href*="components-web/' + files[i] + '"]')) addLink(dsBase + files[i]);
    }
    if (!document.querySelector('link[href*="Material+Icons+Outlined"]')) {
      addLink('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');
    }
    if (!hasClassicIcons()) addLink('https://fonts.googleapis.com/icon?family=Material+Icons');
  }

  /* ── Запуск ────────────────────────────────────────────────────────────────── */

  function init() {
    var cs = document.currentScript;
    if (!cs) {
      var ss = document.getElementsByTagName('script');
      for (var i = ss.length - 1; i >= 0; i--) {
        if (/app-sidenav\.js/.test(ss[i].src)) { cs = ss[i]; break; }
      }
    }
    if (cs && cs.src) AB = cs.src.replace(/app-sidenav\.js.*$/, '');

    ensureDsLinks();

    panel = document.getElementById('panel') || document.querySelector('.panel');
    if (!panel || panel.querySelector('.app-snav')) return;
    var frame = panel.querySelector('.frame');
    if (!frame) return;

    root = document.createElement('nav');
    root.className = 'app-snav';
    root.setAttribute('aria-label', 'Боковое меню');
    root.innerHTML = l1HTML() + '<div class="ds-sidenav-view app-snav__l2" hidden></div>' +
      '<span class="app-snav__hint" aria-hidden="true"><span class="ds-hint-content__label"></span></span>';
    panel.insertBefore(root, frame);
    l2view = root.querySelector('.app-snav__l2');
    hintEl = root.querySelector('.app-snav__hint');

    /* тултип иконки ⓘ: компонент Hint-Tooltip из ДС — контейнер + контент, один на всё меню */
    tipEl = document.createElement('span');
    tipEl.className = 'app-snav__tip';
    tipEl.innerHTML = '<span class="ds-hint-container ds-hint-container--down">' +
                        '<span class="ds-hint-content ds-hint-content--single-content">' +
                          '<span class="ds-hint-content__label"></span>' +
                        '</span>' +
                      '</span>';
    root.appendChild(tipEl);

    scrim = document.createElement('span');
    scrim.className = 'app-snav__scrim';
    scrim.setAttribute('aria-hidden', 'true');
    scrim.addEventListener('click', closeDrawer);
    panel.insertBefore(scrim, root);

    root.addEventListener('click', onClick);
    root.addEventListener('keydown', onKeydown);
    root.addEventListener('mouseover', onOver);
    root.addEventListener('mouseout', onOut);
    document.addEventListener('app-snav-toggle', toggleDrawer);            /* сигнал бургера шапки */
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      tipHide();
      if (state.drawerOpen) closeDrawer();
    });
    root.addEventListener('focusin', function (e) {
      var inf = e.target.closest ? e.target.closest('.app-snav__l2info') : null;
      if (inf) tipShow(inf);                                              /* фокус с клавиатуры */
    });
    root.addEventListener('focusout', function (e) {
      var inf = e.target.closest ? e.target.closest('.app-snav__l2info') : null;
      if (inf) tipHide();
    });

    update();

    function applyWidth() { update(); }
    applyWidth();
    /* пересчёт и без ResizeObserver (фоновые вкладки молчат) — паттерн touch-mode.js */
    if (window.ResizeObserver) { var ro = new ResizeObserver(applyWidth); ro.observe(panel); }
    window.addEventListener('resize', applyWidth);
    window.addEventListener('pointerup', applyWidth);
    window.addEventListener('click', applyWidth);
    window.addEventListener('visibilitychange', applyWidth);
  }

  /* API для страниц и демо стенда */
  window.AppSidenav = {
    open: function (id) { toggleSection(id); },
    close: closeL2,
    toggle: toggleSection,
    setCollapsed: function (v) { state.collapsed = !!v; update(); },
    isCollapsed: function () { return state.collapsed; },
    openId: function () { return state.openId; },
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    toggleDrawer: toggleDrawer,
    isDrawerOpen: function () { return state.drawerOpen; },
    sections: function () {
      return MENU.items.filter(function (i) { return !!i.l2; }).map(function (i) { return i.id; });
    }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
