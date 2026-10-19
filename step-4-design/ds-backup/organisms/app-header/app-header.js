/* app-header — сквозная шапка приложения («App bars: top») — организм дизайн-системы.
   Живёт в DS/organisms/app-header; страницы подключают его как
   ../DS/organisms/app-header/app-header.css + ../DS/organisms/app-header/app-header.js.
   Один источник разметки на все страницы-кадры: шапка вставляется первым ребёнком .panel
   (перед .frame), поэтому не уезжает при прокрутке содержимого.
   Макет-источник: Figma «Отчеты», node 4318:51379 — меню ресторанов «Все рестораны (5)»,
   табы периода, пилюля диапазона, справа — «Поиск», помощь, уведомления (с красной точкой).
   Бургер и лого iiko — наши (в макете их нет). Адаптив — по макетам E-invioice, пока без нового.
   Ширина кадра: >1160 — десктопный макет (4318:51379); 481–1160 — планшетный (429:19815):
   табы скрыты, кнопка «Поиск» скрыта; 481–760 — без пилюли;
   ≤480 — мобильный (1818:73188, полоса 56): бургер, пилюля-диапазон, tune, шестерёнка с бейджем;
   пороги 1160/760/480 — из макетов E-invioice, не токены (пробел ДС №71).
   Интерактив: панель «Выберите ресторан» (макет 3368:33082) — на организме app-right-panel
   (карточка Card/Type=Shadow без скруглений; css/js организма подтягиваются автоматически),
   календарь (компонент Datepicker_DS), уведомления, меню помощи. «Поиск» — пока заглушка
   без действия: панель убрана, поведение будет после макета (шапка остаётся сквозной — она на всех разделах).
   Конструктор блоков: у скрипта подключения можно перечислить показываемые блоки —
   data-hdr="store,tabs,range,cal,search,help,bell"; чего нет в списке, то скрыто.
   Нет атрибута — показано всё. Компоненты внутри — классы ДС. */
(function () {
  /* База ассетов — по адресу самого скрипта: шапка работает с любой страницы
     и при переносе папки организма (../DS/organisms/app-header/). */
  var AB = '';
  var hdr = null, sheet = null, scrim = null, popMenu = null, popCal = null, storeNameEl = null;
  var cs = document.currentScript;
  if (!cs) {
    var ss = document.getElementsByTagName('script');
    for (var i = ss.length - 1; i >= 0; i--) {
      if (/app-header\.js/.test(ss[i].src)) { cs = ss[i]; break; }
    }
  }
  if (cs && cs.src) AB = cs.src.replace(/app-header\.js.*$/, '');

  var MARKUP =
    '<div class="apph__left">' +
      '<div class="apph__logo-block">' +
        '<span class="apph__item ds-icon-size ds-icon-size--6x ds-icon-size--state" role="button" tabindex="0" aria-label="Меню"><img src="' + AB + 'icon-menu.svg" width="24" height="24" alt=""></span>' +
        '<span class="apph__logo-wrap"><img src="' + AB + 'logo-iiko.svg" width="60" height="24" alt="iiko"></span>' +
      '</div>' +
      '<div class="apph__store apph__item ds-text-ui" role="button" tabindex="0" aria-label="Рестораны: Все рестораны (5)">' +
        '<span class="ds-text-ui__element-left"><span class="ds-icon-size ds-icon-size--5x"><span class="material-icons apph__store-icon" aria-hidden="true">storefront</span></span></span>' +
        '<span class="ds-text-ui__content"><span class="ds-text-ui__label apph__store-name">Все рестораны (5)</span></span>' +
        '<span class="ds-text-ui__element-right"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-arrow-drop-down-24.svg" width="20" height="20" alt=""></span></span>' +
      '</div>' +
    '</div>' +
    '<div class="apph__center">' +
      '<div class="apph__tabs" role="tablist" aria-label="Период">' +
        '<span class="apph__tab" role="tab" aria-selected="false">д</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">н</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">м</span>' +
        '<span class="apph__tab apph__tab--active" role="tab" aria-selected="true">г</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">п</span>' +
      '</div>' +
      '<div class="apph__pill">' +
        '<div class="apph__select">' +
          '<span class="apph__nav apph__item" role="button" tabindex="0" data-step="-1" aria-label="Предыдущий период"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-chevron-left.svg" width="20" height="20" alt=""></span></span>' +
          /* стрелка ⌄ в пилюле убрана — решение заказчика 02.10 (журнал №98); в v2 меню пресетов переезжает на клик по датам+стрелке */
          '<span class="apph__date apph__item" role="button" tabindex="0" aria-label="Период"><span class="apph__date-text">01.01.26 - 31.12.26</span></span>' +
          '<span class="apph__nav apph__item" role="button" tabindex="0" data-step="1" aria-label="Следующий период"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-chevron-right.svg" width="20" height="20" alt=""></span></span>' +
        '</div>' +
        '<span class="apph__cal apph__item" role="button" tabindex="0" aria-label="Календарь"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-date-range.svg" width="20" height="20" alt=""></span></span>' +
      '</div>' +
    '</div>' +
    '<div class="apph__right">' +
      '<button class="ds-btn ds-btn--s ds-btn--neutral ds-btn--outlined apph__search" type="button" aria-label="Поиск">' +
        '<span class="ds-btn__icon"><img src="' + AB + 'icon-search.svg" width="20" height="20" alt=""></span>' +
        '<span class="ds-btn__label">Поиск</span>' +
      '</button>' +
      '<span class="apph__help apph__item" role="button" tabindex="0" aria-label="Помощь"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-help.svg" width="20" height="20" alt=""></span></span>' +
      '<span class="apph__bell apph__item" role="button" tabindex="0" aria-label="Уведомления"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><img src="' + AB + 'icon-bell-dot.svg" width="20" height="20" alt=""></span></span>' +
    '</div>' +
    '<div class="apph__mright">' +
      '<span class="apph__mpill"><span class="apph__mdate">01.01.26 - 31.12.26</span><img src="' + AB + 'icon-date-range.svg" width="24" height="24" alt=""></span>' +
      '<span class="apph__item" role="button" tabindex="0" aria-label="Фильтры"><img src="' + AB + 'icon-tune.svg" width="24" height="24" alt=""></span>' +
      '<span class="apph__item apph__badge-wrap" role="button" tabindex="0" aria-label="Настройки"><img src="' + AB + 'icon-settings.svg" width="24" height="24" alt=""><span class="apph__badge">2</span></span>' +
    '</div>';

  /* ══ Интерактив шапки ════════════════════════════════════════════════
     Панель «Выберите ресторан» — макет 3368:33082 (Iiko-Web-DS «Отчеты»).
     «Поиск» — заглушка без действия: панель убрана, поведение — после макета.
     Шапка СКВОЗНАЯ — живёт на всех разделах. Уведомления и меню помощи — условные.
     Панели — правая шторка 500px + затемнение внутри .panel; календарь и меню помощи —
     поповеры внутри шапки. Внутри — компоненты ДС (ds-checkbox, ds-slide-toggle, ds-search,
     ds-menu-*, ds-list-item, ds-elements/datepicker, ds-btn). */

  var STORE = [
    { name: 'Delco Ltd', items: ['Название ресторана'] },
    { name: 'SIT Inc', items: ['SIT Cafe', 'SIT Restaurant'] },
    { name: 'Romashka OOO', items: ['Название ресторана'] },
    { name: 'Название ресторана', items: ['Название ресторана'] }
  ];

  var NOTIF = [
    { text: 'Отчёт «KPI report» готов', time: 'только что' },
    { text: 'Новая версия дизайн-системы', time: 'вчера' },
    { text: 'Заканчивается пробный период', time: 'через 3 дня' }
  ];
  var MENU_ITEMS = ['Центр помощи', 'Написать в поддержку', 'Что нового'];

  var H = {
    sel: { '1.0': 1 },              /* выбранные рестораны (SIT Cafe — как в макете) */
    snap: null,                      /* снимок выбора для «Отменить» */
    openGroups: { 1: true },         /* раскрытые группы (SIT Inc раскрыт — как в макете) */
    onlySel: false, filter: '',      /* «Показать выбранные» и строка поиска в панели */
    sheet: null, menu: false, cal: false
  };

  var RANGE = { start: new Date(2026, 0, 1), end: new Date(2026, 11, 31), mode: 'г' };   /* стартовый диапазон — как в макете шапки */

  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function fmtD(d) { return pad2(d.getDate()) + '.' + pad2(d.getMonth() + 1) + '.' + String(d.getFullYear()).slice(2); }
  function cut(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  function addDays(d, n) { var x = new Date(d); x.setDate(x.getDate() + n); return x; }
  function addMonths(d, n) { var x = new Date(d); var day = x.getDate(); x.setDate(1); x.setMonth(x.getMonth() + n); x.setDate(Math.min(day, new Date(x.getFullYear(), x.getMonth() + 1, 0).getDate())); return x; }
  function mondayOf(d) { var x = cut(d); return addDays(x, -((x.getDay() + 6) % 7)); }
  function sameDay(a, b) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
  /* клик внутри элемента: путь события фиксируется на момент dispatch, поэтому не ломается,
     если обработчик во время клика пересобрал DOM (календарь, списки панели) */
  function pathHas(e, sel) {
    if (e.composedPath) {
      var p = e.composedPath();
      for (var i = 0; i < p.length; i++) if (p[i] && p[i].matches && p[i].matches(sel)) return true;
      return false;
    }
    return !!(e.target && e.target.closest && e.target.closest(sel));
  }
  function copySel() { var c = {}; for (var k in H.sel) c[k] = H.sel[k]; return c; }
  function selCount() { var n = 0; for (var k in H.sel) if (H.sel[k]) n++; return n; }
  function leafTotal() { var n = 0; for (var g = 0; g < STORE.length; g++) n += STORE[g].items.length; return n; }
  function selInGroup(g) { var n = 0, it = STORE[g].items; for (var i = 0; i < it.length; i++) if (H.sel[g + '.' + i]) n++; return n; }

  /* ── Панель ресторанов ─────────────────────────────────────────────── */
  function cbHTML(attr) {
    return '<span class="ds-checkbox apph-row__cb"><input class="ds-checkbox__input" type="checkbox" data-cb="' + attr + '"><span class="ds-checkbox__box"></span></span>';
  }
  function renderStoreList() {
    var box = sheet.querySelector('[data-list="store"]');
    if (!box) return;
    var f = H.filter.trim().toLowerCase();
    var html = '<div class="ds-list-item apph-row" data-role="master">' + cbHTML('master') +
               '<span class="apph-row__name apph-row__name--md">Все рестораны (57)</span></div><span class="ds-divider"></span>';
    for (var g = 0; g < STORE.length; g++) {
      var grp = STORE[g];
      var gVis = !f || grp.name.toLowerCase().indexOf(f) >= 0;
      var hasSel = selInGroup(g) > 0;
      var any = false;
      for (var i = 0; i < grp.items.length; i++) {
        var nm = grp.items[i];
        if (H.onlySel && !H.sel[g + '.' + i]) continue;
        if (f && !gVis && nm.toLowerCase().indexOf(f) < 0) continue;
        any = true;
      }
      if (H.onlySel && !hasSel) continue;
      if (!any && !gVis) continue;
      var open = !!H.openGroups[g] || !!f;
      html += '<div class="ds-list-item apph-row" data-role="group" data-g="' + g + '">' +
                '<span class="apph-row__chev material-icons" data-chev="' + g + '" aria-hidden="true">' + (open ? 'expand_more' : 'chevron_right') + '</span>' +
                cbHTML('g' + g) + '<span class="apph-row__name">' + grp.name + '</span></div>';
      if (open) {
        for (var j = 0; j < grp.items.length; j++) {
          if (H.onlySel && !H.sel[g + '.' + j]) continue;
          if (f && !gVis && grp.items[j].toLowerCase().indexOf(f) < 0) continue;
          html += '<div class="ds-list-item apph-row apph-row--child" data-role="leaf" data-key="' + g + '.' + j + '">' +
                    cbHTML(g + '.' + j) + '<span class="apph-row__name">' + grp.items[j] + '</span></div>';
        }
      }
    }
    box.innerHTML = html;
    syncStoreBoxes();
    var cnt = sheet.querySelector('[data-count]');
    if (cnt) cnt.textContent = 'Выбрано ресторанов: ' + selCount();
  }
  function syncStoreBoxes() {
    var boxes = sheet.querySelectorAll('input[data-cb]');
    var total = leafTotal(), sel = selCount();
    for (var j = 0; j < boxes.length; j++) {
      var el = boxes[j], a = el.getAttribute('data-cb');
      if (a === 'master') { el.checked = sel > 0 && sel === total; el.indeterminate = sel > 0 && sel < total; }
      else if (a.charAt(0) === 'g') {
        var g = parseInt(a.slice(1), 10), t = STORE[g].items.length, s = selInGroup(g);
        el.checked = s > 0 && s === t; el.indeterminate = s > 0 && s < t;
      } else { el.checked = !!H.sel[a]; }
    }
  }
  function applyStore() {
    var total = leafTotal(), n = selCount(), single = '';
    for (var g = 0; g < STORE.length; g++) for (var i = 0; i < STORE[g].items.length; i++) if (H.sel[g + '.' + i]) single = STORE[g].items[i];
    var label;
    if (n === 0) label = 'Выберите ресторан';
    else if (n === total) label = 'Все рестораны (' + total + ')';
    else if (n === 1) label = single;
    else label = 'Выбрано: ' + n;
    storeNameEl.textContent = label;
  }

  /* ── Календарь: компонент Datepicker (Datepicker_DS/datepicker.js) ─────
     Сетка, состояния и клики — в компоненте; шапка только монтирует его в свой
     поповер (при первом открытии), позиционирует и синхронизирует диапазон. */
  var calInst = null, dpLoading = false, dpQueue = [];
  function ensureDatepicker(cb) {
    if (window.Datepicker) { cb(); return; }
    dpQueue.push(cb);
    if (dpLoading) return;
    dpLoading = true;
    var s = document.createElement('script');
    s.src = AB + '../../components-web/components/Datepicker_DS/datepicker.js';
    s.onload = function () {
      dpLoading = false;
      var q = dpQueue; dpQueue = [];
      for (var i = 0; i < q.length; i++) q[i]();
    };
    (document.head || document.documentElement).appendChild(s);
  }
  function positionCal() {
    var pr = hdr.getBoundingClientRect();
    /* якорь — пилюля диапазона; если она скрыта конструктором, встаём под иконку календаря */
    var anchor = hdr.querySelector('.apph__date');
    if (!anchor || anchor.offsetParent === null) anchor = hdr.querySelector('.apph__cal');
    var r = anchor ? anchor.getBoundingClientRect() : pr;
    popCal.style.left = Math.max(8, Math.round(r.left - pr.left)) + 'px';
  }
  function onCalPicked(s, e) {
    RANGE.start = s;
    RANGE.end = e;
    RANGE.mode = 'п';
    setActiveTab('п');
    updateDates();
  }

  /* ── Период: табы, стрелки, даты ───────────────────────────────────── */
  function updateDates() {
    /* один день (совпали начало и конец) показываем без диапазона */
    var s = sameDay(RANGE.start, RANGE.end) ? fmtD(RANGE.start) : fmtD(RANGE.start) + ' - ' + fmtD(RANGE.end);
    var t1 = hdr.querySelector('.apph__date-text'); if (t1) t1.textContent = s;
    var t2 = hdr.querySelector('.apph__mdate'); if (t2) t2.textContent = s;
  }
  function setActiveTab(label) {
    var tabs = hdr.querySelectorAll('.apph__tab');
    for (var i = 0; i < tabs.length; i++) {
      var on = tabs[i].textContent === label;
      tabs[i].classList.toggle('apph__tab--active', on);
      tabs[i].setAttribute('aria-selected', on ? 'true' : 'false');
    }
  }
  function setMode(label) {
    var t = cut(new Date());
    if (label === 'д') { RANGE.start = t; RANGE.end = t; }
    else if (label === 'н') { RANGE.start = mondayOf(t); RANGE.end = addDays(RANGE.start, 6); }
    else if (label === 'м') { RANGE.start = new Date(t.getFullYear(), t.getMonth(), 1); RANGE.end = new Date(t.getFullYear(), t.getMonth() + 1, 0); }
    else if (label === 'г') { RANGE.start = new Date(t.getFullYear(), 0, 1); RANGE.end = new Date(t.getFullYear(), 11, 31); }
    RANGE.mode = label;   /* «п» — диапазон задаётся в календаре, не трогаем */
    setActiveTab(label);
    updateDates();
    if (H.cal && calInst) calInst.view(RANGE.start);
  }
  function shiftBounds(dir) {
    if (RANGE.mode === 'п') return;
    if (RANGE.mode === 'д') { RANGE.start = addDays(RANGE.start, dir); RANGE.end = addDays(RANGE.end, dir); }
    else if (RANGE.mode === 'н') { RANGE.start = addDays(RANGE.start, 7 * dir); RANGE.end = addDays(RANGE.end, 7 * dir); }
    else if (RANGE.mode === 'м') { RANGE.start = addMonths(RANGE.start, dir); RANGE.end = addMonths(RANGE.end, dir); }
    else if (RANGE.mode === 'г') { RANGE.start = addMonths(RANGE.start, 12 * dir); RANGE.end = addMonths(RANGE.end, 12 * dir); }
    updateDates();
  }

  /* ── Панели и поповеры: открытие/закрытие ──────────────────────────── */
  /* каркас панели — организм app-right-panel: фрейм-карточка (Card, Type=Shadow, без скруглений),
     шапка (Card title 20px + крестик 20), контент (скролл), подвал (действия справа) */
  function sheetShell(title, body, actions) {
    return '<div class="ds-card ds-card--shadow app-rp__frame">' +
             '<div class="ds-card__header">' +
               '<p class="ds-card__title app-rp__title">' + title + '</p>' +
               '<span class="app-rp__close" role="button" tabindex="0" aria-label="Закрыть"><span class="ds-icon-size ds-icon-size--5x ds-icon-size--state"><span class="material-icons">close</span></span></span>' +
             '</div>' +
             '<div class="ds-card__content">' + body + '</div>' +
             (actions ? '<div class="ds-card__footer ds-card__footer--right"><div class="ds-card__footer__action">' + actions + '</div></div>' : '') +
           '</div>';
  }
  function openSheet(name) {
    closePopovers();
    H.sheet = name;
    if (name === 'store') {
      H.snap = copySel();
      H.onlySel = false;
      H.filter = '';
      sheet.innerHTML = sheetShell('Выберите ресторан',
        '<div class="ds-search apph-field"><span class="material-icons apph-field__icon">search</span><input class="apph-field__input" type="text" placeholder="Поиск" data-input="store"></div>' +
        '<div class="apph-store__meta"><span class="apph-store__count" data-count>Выбрано ресторанов: ' + selCount() + '</span><span class="apph-vdiv"></span>' +
          '<label class="ds-slide-toggle"><span class="ds-slide-toggle__row"><input type="checkbox" class="ds-slide-toggle__input" data-toggle="onlySel"><span class="ds-slide-toggle__track"></span><span class="ds-slide-toggle__title">Показать выбранные</span></span></label></div>' +
        '<div class="apph-store__list" data-list="store"></div>',
        '<button class="ds-btn ds-btn--m ds-btn--neutral ds-btn--outlined" type="button" data-act="cancel"><span class="ds-btn__label">Отменить</span></button>' +
        '<button class="ds-btn ds-btn--m ds-btn--accent ds-btn--filled" type="button" data-act="apply"><span class="ds-btn__label">Применить</span></button>');
      renderStoreList();
    } else {
      var nb = '';
      for (var i = 0; i < NOTIF.length; i++) {
        nb += '<div class="ds-list-item apph-row apph-row--notif">' +
                '<span class="apph-row__check material-icons">notifications</span>' +
                '<span class="apph-row__name">' + NOTIF[i].text + '<span class="apph-row__time">' + NOTIF[i].time + '</span></span></div>';
      }
      sheet.innerHTML = sheetShell('Уведомления', nb);
    }
    sheet.setAttribute('aria-label', name === 'store' ? 'Выберите ресторан' : 'Уведомления');
    if (window.AppRightPanel) window.AppRightPanel.open('sheet');
    else { scrim.hidden = false; sheet.hidden = false; }   /* фолбэк, пока организм не загрузился */
  }
  function closeSheet() {
    H.sheet = null; H.snap = null; H.filter = '';
    if (window.AppRightPanel) window.AppRightPanel.close('sheet');
    sheet.hidden = true; scrim.hidden = true;
  }
  function toggleMenu() { if (H.menu) { closeMenu(); return; } closeSheet(); closeCal(); H.menu = true; popMenu.hidden = false; }
  function closeMenu() { H.menu = false; popMenu.hidden = true; }
  function toggleCal() {
    if (H.cal) { closeCal(); return; }
    closeSheet(); closeMenu();
    ensureDatepicker(function () {
      if (!calInst) calInst = window.Datepicker.mount(popCal, { onPick: onCalPicked });
      calInst.reset();
      calInst.view(RANGE.start);
      H.cal = true;
      popCal.hidden = false;
      positionCal();
    });
  }
  function closeCal() { H.cal = false; popCal.hidden = true; }
  function closePopovers() { closeMenu(); closeCal(); }

  /* ── Клики ─────────────────────────────────────────────────────────── */
  function onSheetClick(e) {
    var t = e.target;
    if (t.closest('.app-rp__close')) { closeSheet(); return; }   /* крестик организма (дублирует делегат app-right-panel — безвредно) */
    if (t.closest('[data-act="cancel"]')) { if (H.snap) H.sel = H.snap; closeSheet(); return; }
    if (t.closest('[data-act="apply"]')) { applyStore(); closeSheet(); return; }
    var chev = t.closest('[data-chev]');
    if (chev) { var g = chev.getAttribute('data-chev'); H.openGroups[g] = !H.openGroups[g]; renderStoreList(); return; }
    var row = t.closest('.apph-row');
    if (row && sheet.querySelector('[data-list="store"]') && sheet.querySelector('[data-list="store"]').contains(row)) {
      var role = row.getAttribute('data-role');
      if (role === 'master') {
        if (selCount() === leafTotal()) H.sel = {};
        else { H.sel = {}; for (var g2 = 0; g2 < STORE.length; g2++) for (var i2 = 0; i2 < STORE[g2].items.length; i2++) H.sel[g2 + '.' + i2] = 1; }
      } else if (role === 'group') {
        var g3 = parseInt(row.getAttribute('data-g'), 10), t3 = STORE[g3].items.length;
        if (selInGroup(g3) === t3) { for (var i3 = 0; i3 < t3; i3++) delete H.sel[g3 + '.' + i3]; }
        else { for (var i4 = 0; i4 < t3; i4++) H.sel[g3 + '.' + i4] = 1; }
      } else if (role === 'leaf') {
        var k = row.getAttribute('data-key');
        if (H.sel[k]) delete H.sel[k]; else H.sel[k] = 1;
      }
      renderStoreList();
      return;
    }
  }
  function onSheetChange(e) {
    var t = e.target;
    if (t && t.getAttribute && t.getAttribute('data-toggle') === 'onlySel') { H.onlySel = !!t.checked; renderStoreList(); }
  }
  function onSheetInput(e) {
    var t = e.target;
    if (!t || !t.getAttribute) return;
    if (t.getAttribute('data-input') === 'store') { H.filter = t.value || ''; renderStoreList(); }
  }
  function onHeaderClick(e) {
    var t = e.target;
    if (!t.closest) return;
    if (pathHas(e, '.apph-cal') || pathHas(e, '.apph-menu')) return;   /* поповеры обрабатывают свои клики сами */
    if (t.closest('.apph__item[aria-label="Меню"]')) { document.dispatchEvent(new CustomEvent('app-snav-toggle')); return; }
    if (t.closest('.apph__store')) { openSheet('store'); return; }
    /* «Поиск» пока заглушка: клик ничего не делает (панель и поведение — после макета) */
    if (t.closest('.apph__bell')) { openSheet('notif'); return; }
    if (t.closest('.apph__help')) { toggleMenu(); return; }
    if (t.closest('.apph__date') || t.closest('.apph__cal')) { toggleCal(); return; }
    var tab = t.closest('.apph__tab');
    if (tab) { setMode((tab.textContent || '').trim()); return; }
    var nav = t.closest('.apph__nav');
    if (nav) { shiftBounds(parseInt(nav.getAttribute('data-step'), 10)); return; }
  }
  function ensureHeaderDeps() {
    var files = ['components/Checkbox_DS/checkbox.css', 'components/Checkbox_DS/checkbox-icons.css', 'fixes.css'];
    for (var i = 0; i < files.length; i++) {
      if (!document.querySelector('link[href*="' + files[i] + '"]')) {
        var l = document.createElement('link');
        l.rel = 'stylesheet';
        l.href = AB + '../../components-web/' + files[i];
        (document.head || document.documentElement).appendChild(l);
      }
    }
    /* правая панель — организм app-right-panel: стили + поведение (каркас шторки шапки).
       Проверка по маркеру: повторно не добавится, если страница уже подключила их сама
       (в т.ч. через connect.js). */
    if (!document.querySelector('link[href*="app-right-panel.css"]')) {
      var lp = document.createElement('link');
      lp.rel = 'stylesheet';
      lp.href = AB + '../app-right-panel/app-right-panel.css';
      (document.head || document.documentElement).appendChild(lp);
    }
    if (!window.AppRightPanel && !document.querySelector('script[src*="app-right-panel.js"]')) {
      var sp = document.createElement('script');
      sp.src = AB + '../app-right-panel/app-right-panel.js';
      (document.head || document.documentElement).appendChild(sp);
    }
  }

  function init() {
    var panel = document.getElementById('panel') || document.querySelector('.panel');
    if (!panel || panel.querySelector('.apph')) return;
    hdr = document.createElement('header');
    hdr.className = 'apph';
    hdr.setAttribute('role', 'banner');
    hdr.innerHTML = MARKUP;
    panel.insertBefore(hdr, panel.firstChild);
    storeNameEl = hdr.querySelector('.apph__store-name');

    /* Конструктор блоков: data-hdr="store,tabs,range,cal,search,help,bell" у скрипта
       подключения — показываем только перечисленное; нет атрибута — показано всё. */
    if (cs && cs.getAttribute) {
      var spec = cs.getAttribute('data-hdr');
      if (spec !== null) {
        var on = {}, parts = spec.split(','), blocks = ['store', 'tabs', 'range', 'cal', 'search', 'help', 'bell'];
        for (var pi = 0; pi < parts.length; pi++) { var pad = parts[pi].replace(/^\s+|\s+$/g, ''); if (pad) on[pad] = 1; }
        for (var bi = 0; bi < blocks.length; bi++) hdr.classList.toggle('apph--no-' + blocks[bi], !on[blocks[bi]]);
      }
    }

    ensureHeaderDeps();

    /* слои панели (внутри .panel): затемнение (Backdrop) + правая панель — организм app-right-panel
       (фрейм-карточка Card/Type=Shadow без скруглений; ширина 500 — из макета 3368:33082) */
    scrim = document.createElement('div');
    scrim.className = 'app-rp-scrim ds-backdrop';
    scrim.setAttribute('data-rp-scrim', 'sheet');
    scrim.hidden = true;
    scrim.addEventListener('click', closeSheet);
    sheet = document.createElement('aside');
    sheet.className = 'app-rp apph-panel';
    sheet.setAttribute('data-rp', 'sheet');
    sheet.style.setProperty('--app-rp-width', '500px');
    sheet.hidden = true;
    sheet.addEventListener('app-rp-close', function () { H.sheet = null; H.snap = null; H.filter = ''; });
    panel.appendChild(scrim);
    panel.appendChild(sheet);

    /* поповеры внутри шапки: меню помощи и календарь */
    popMenu = document.createElement('div');
    popMenu.className = 'apph-menu';
    popMenu.hidden = true;
    var mh = '<div class="ds-menu-container apph-menu__box">';
    for (var mi = 0; mi < MENU_ITEMS.length; mi++) mh += '<div class="ds-menu-item apph-menu__item" role="button" tabindex="0">' + MENU_ITEMS[mi] + '</div>';
    popMenu.innerHTML = mh + '</div>';
    popCal = document.createElement('div');
    popCal.className = 'apph-cal';
    popCal.hidden = true;
    hdr.appendChild(popMenu);
    hdr.appendChild(popCal);

    hdr.addEventListener('click', onHeaderClick);
    sheet.addEventListener('click', onSheetClick);
    sheet.addEventListener('change', onSheetChange);
    sheet.addEventListener('input', onSheetInput);
    popMenu.addEventListener('click', function () { closeMenu(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeSheet(); closePopovers(); }
    });
    document.addEventListener('click', function (e) {
      if (H.menu && !pathHas(e, '.apph-menu') && !pathHas(e, '.apph__help')) closeMenu();
      if (H.cal && !pathHas(e, '.apph-cal') && !pathHas(e, '.apph__date') && !pathHas(e, '.apph__cal')) closeCal();
    });

    updateDates();

    function applyWidth() {
      var w = panel.clientWidth;
      hdr.classList.toggle('apph--tablet', w > 480 && w <= 1160);   // планшетный макет 429:19815
      hdr.classList.toggle('apph--mini', w > 480 && w < 760);      // планшетный бэнд: пилюля не помещается
      hdr.classList.toggle('apph--mobile', w <= 480);              // мобильный макет 1818:73188
    }
    applyWidth();
    // пересчёт и без ResizeObserver (фоновые вкладки молчат) — паттерн touch-mode.js
    if (window.ResizeObserver) { var ro = new ResizeObserver(applyWidth); ro.observe(panel); }
    window.addEventListener('resize', applyWidth);
    window.addEventListener('pointerup', applyWidth);
    window.addEventListener('click', applyWidth);
    window.addEventListener('visibilitychange', applyWidth);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
