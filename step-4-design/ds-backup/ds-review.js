/* ds-review.js — верхняя панель ревью («надстройка») для страниц-стендов прототипов.
   Служебный слой показа: для владельцев и участников. На юзерских прототипах не подключается.

   ПОДКЛЮЧЕНИЕ (одна строка, после connect.js):
     <script src="../DS/ds-review.js" defer></script>
   Скрипт сам подтягивает ds-review.css (лежит рядом) и — если он есть — реестр
   `layouts.js` РЯДОМ СО СТРАНИЦЕЙ (другой путь можно задать атрибутом data-registry).

   РЕЕСТР (layouts.js рядом со страницами проекта; без реестра панель покажет только заголовок):
     window.dsLayouts = {
       проект:   'Внешнее меню',                 // общий заголовок слева
       адаптив:  true,                           // показывать секцию «Размеры»; нет — секцию не выводим
       шаги: [                                   // селект «Экраны» (ДС Select) + стрелки ‹ ›; меньше двух — секции нет
         { file: 'page.html', title: 'Название шага', hint: 'Строка-пояснение' },
         { file: 'page2.html', state: 'edit', title: '…' }   // state — переключение состояния на той же странице
       ],
       пути: [ { label: 'Схемы', url: '…' } ],   // кнопки-ссылки (по умолчанию скрыты, тумбл в ⚙); без url — кнопка никуда не ведёт
       подсказки: [                              // «Подсказки ДС»: номерные маркеры (по умолчанию ВЫКЛ)
         { num: 119, target: '.hint', text: 'Суть пробела ДС…' }   // num — номер пункта журнала DS/fixes.md
       ]
     };

   ПАРАМЕТРЫ СТРАНИЦЫ: ?w=<px> — ширина кадра; ?hints=1 — подсказки включены; ?ui=0 — панель
   полностью скрыта (чистая ссылка юзеру); ?ui=1 — показать принудительно.
   Настройки (скрыта ли панель, какие секции видны, ширина) запоминаются в localStorage.
   Клавиатура: ← → — по экранам. Состояния экрана: событие `dsreview:state` (detail.id) или
   необязательная функция window.DSReviewState(id). */
(function () {
  'use strict';
  if (window.__dsrLoaded) return;
  window.__dsrLoaded = true;

  var cs = document.currentScript;
  var BASE = (cs && cs.src) ? cs.src.replace(/ds-review\.js.*$/, '') : '';

  /* ── Параметры и настройки ─────────────────────────────────────────────── */
  function parseQuery() {
    var out = {}, s = location.search.replace(/^\?/, '');
    if (!s) return out;
    s.split('&').forEach(function (p) {
      var i = p.indexOf('=');
      var k = i === -1 ? p : p.slice(0, i);
      var v = i === -1 ? '' : p.slice(i + 1);
      try { out[decodeURIComponent(k)] = decodeURIComponent(v); } catch (e) {}
    });
    return out;
  }
  var Q = parseQuery();

  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function load(k, d) { try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }

  var saved = load('dsr', {}) || {};
  var S = {
    sections: saved.sections || {},
    hidden: Q.ui === '0' ? true : (Q.ui === '1' ? false : !!saved.hidden),
    w: (/^\d{2,4}$/.test(Q.w || '') ? Q.w : (/^\d{2,4}$/.test(saved.w || '') ? saved.w : null)),
    hintsOn: Q.hints === '1',
    registry: window.dsLayouts || null,
    bar: null, restore: null, layer: null, bubble: null, pop: null,
    badges: [], stepsEls: null, selEls: null, sizeSel: null, titleEl: null, presetH: null, hintsEls: null, pathsEls: null
  };
  /* «Подсказки ДС» и «Пути» — всегда выключены по умолчанию: сохранённое в браузере состояние
     игнорируем, включение в ⚙ действует только на текущую сессию */
  S.sections.hints = false;
  S.sections.paths = false;
  function persist() {
    var s = {};                                   /* «Подсказки ДС» и «Пути» не запоминаем */
    if (S.sections) for (var k in S.sections) { if (k !== 'hints' && k !== 'paths') s[k] = S.sections[k]; }
    store('dsr', { sections: s, hidden: S.hidden, w: S.w });
  }

  /* ── Утилиты ───────────────────────────────────────────────────────────── */
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function basename(p) { return String(p).split('/').pop().split('\\').pop(); }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function addParam(url, k, v) {
    var i = url.indexOf('#');
    var path = i === -1 ? url : url.slice(0, i);
    var hash = i === -1 ? '' : url.slice(i);
    if (new RegExp('[?&]' + k + '=').test(path)) return url;
    return path + (path.indexOf('?') === -1 ? '?' : '&') + k + '=' + v + hash;
  }
  function closePop(keep) {
    if (S.pop && S.pop !== keep) { S.pop.remove(); S.pop = null; }
    if (S.bubble && S.bubble !== keep) { S.bubble.remove(); S.bubble = null; }
  }
  function placePop(pop, anchor) {
    var r = anchor.getBoundingClientRect();
    var pw = pop.offsetWidth || 300;
    /* правый край поповера — под якорем, но не вылезаем за края окна */
    var left = Math.min(Math.max(8, r.right - pw), window.innerWidth - pw - 8);
    pop.style.top = Math.round(r.bottom + 6) + 'px';
    pop.style.left = Math.round(left) + 'px';
    pop.style.right = 'auto';
  }

  /* ── Шаги ──────────────────────────────────────────────────────────────── */
  function currentStep(steps) {
    var base = basename(location.pathname), st = Q.state || '', i, f, fMatch;
    for (i = 0; i < steps.length; i++) {
      f = steps[i].file;
      fMatch = !f || basename(f) === base;
      if (fMatch && (steps[i].state || '') === st) return i;
    }
    for (i = 0; i < steps.length; i++) {
      f = steps[i].file;
      if (f && basename(f) === base) return i;
    }
    return -1;
  }
  function setState(id) {
    try {
      var url = new URL(location.href);
      url.searchParams.set('state', id);
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    } catch (e) {}
    Q.state = String(id);                  /* стрелки и селект читают позицию из Q — держим актуальной */
    try { document.dispatchEvent(new CustomEvent('dsreview:state', { detail: { id: id } })); } catch (e2) {}
    if (typeof window.DSReviewState === 'function') { try { window.DSReviewState(id); } catch (e3) {} }
  }
  function goStep(i) {
    var steps = S.stepsEls.steps, st = steps[i];
    if (!st) return;
    var same = !st.file || basename(st.file) === basename(location.pathname);
    if (same) {
      if (st.state) setState(st.state);
      setCurrent(i);
      return;
    }
    var url = st.file;
    if (st.state) url = addParam(url, 'state', st.state);
    if (S.w) url = addParam(url, 'w', S.w);
    location.href = url;
  }
  /* ── Селекты панели (ДС Select): шаги + размер ─────────────────────────── */
  function selObjs() { return [S.selEls, S.sizeSel].filter(Boolean); }
  function openSel(o, open) {
    if (!o) return;
    if (o === S.sizeSel) fitSizesField();   /* перед открытием ширину поля пересчитываем (к этому моменту замер точно корректен) */
    if (open) {
      selObjs().forEach(function (x) {                 /* открыт всегда один список */
        if (x !== o) { x.list.hidden = true; x.field.setAttribute('aria-expanded', 'false'); }
      });
    }
    o.list.hidden = !open;
    o.field.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function closeSels(keep) {
    selObjs().forEach(function (x) {
      if (x !== keep) { x.list.hidden = true; x.field.setAttribute('aria-expanded', 'false'); }
    });
  }
  /* «Размер»: ширина поля — по самому длинному значению (замер по живому полю; все подстановки —
     в одном кадре, до отрисовки); при смене значения форма не меняется */
  function fitSizesField() {
    if (!S.sizeSel || !S.sizeSel.values) return;
    var ft = S.sizeSel.fieldText, keep = ft.textContent, mx = 0;
    S.sizeSel.values.forEach(function (v) {
      ft.textContent = v;
      mx = Math.max(mx, ft.getBoundingClientRect().width);
    });
    ft.textContent = keep;
    ft.style.minWidth = mx + 'px';
  }
  function markSel(o, idx) {
    if (!o) return;
    o.items.forEach(function (it, k) {
      var on = k === idx;
      it.classList.toggle('ds-select-item--selected', on);
      it.setAttribute('aria-selected', on ? 'true' : 'false');
      var chk = it.querySelector('.ds-select-item__element-right');
      if (chk) chk.style.visibility = on ? '' : 'hidden';
    });
  }
  /* Собрать селект ДС: поле + выпадающий список; cfg = {cls, aria, items:[{label,hint}], onPick(i)} */
  function mkSelect(cfg) {
    var sel = el('span', 'dsr-sel' + (cfg.cls ? ' ' + cfg.cls : ''));
    var field = el('div', 'ds-select-form ds-select-form--xs');
    field.setAttribute('role', 'button');
    field.setAttribute('tabindex', '0');
    field.setAttribute('aria-haspopup', 'listbox');
    field.setAttribute('aria-expanded', 'false');
    field.setAttribute('aria-label', cfg.aria || '');
    field.innerHTML = '<div class="ds-input ds-input--xs"><div class="ds-input__frame"><div class="ds-input__content">' +
      '<span class="ds-input__field"></span></div><span class="ds-input__icon">' +
      '<span class="material-icons" aria-hidden="true">arrow_drop_down</span></span></div></div>';
    var list = el('div', 'ds-select-container ds-select-container--container dsr-sel__list');
    list.setAttribute('role', 'listbox');
    list.hidden = true;
    var items = [];
    (cfg.items || []).forEach(function (it, i) {
      var node = el('div', 'ds-select-item ds-select-item--false');
      node.setAttribute('role', 'option');
      var cont = el('div', 'ds-select-item__content');
      cont.appendChild(el('span', 'ds-select-item__label', it.label));
      if (it.hint) cont.appendChild(el('span', 'ds-select-item__label-down', it.hint));
      node.appendChild(cont);
      var chk = el('span', 'ds-select-item__element-right');
      chk.appendChild(el('span', 'material-icons', 'check'));
      chk.style.visibility = 'hidden';   /* слот галочки зарезервирован у всех пунктов — колонка не скачет */
      node.appendChild(chk);
      node.addEventListener('click', function (e) { e.stopPropagation(); closeSels(); cfg.onPick(i); });
      items.push(node);
      list.appendChild(node);
    });
    var o = { sel: sel, field: field, fieldText: field.querySelector('.ds-input__field'), list: list, items: items };
    field.addEventListener('click', function (e) { e.stopPropagation(); openSel(o, o.list.hidden); });
    field.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openSel(o, o.list.hidden); }
    });
    sel.appendChild(field);
    sel.appendChild(list);
    return o;
  }
  function setCurrent(i) {
    var e = S.stepsEls, s = S.selEls;
    if (e) {
      e.prev.disabled = i <= 0;
      e.next.disabled = i < 0 || i >= e.steps.length - 1;
      if (S.countEl) S.countEl.textContent = (i >= 0 ? i + 1 : '—') + '/' + e.steps.length;
    }
    if (s && e) {
      var st = i >= 0 ? e.steps[i] : null;
      s.fieldText.textContent = st ? (st.title || ('Экран ' + (i + 1))) : '';
      markSel(s, i);
      closeSels();
    }
  }

  /* ── Ширина кадра ──────────────────────────────────────────────────────── */
  function applyW(w, save) {
    var panel = document.getElementById('panel') || document.querySelector('.panel');
    if (w === 'auto') w = null;
    S.w = w;
    if (save !== false) persist();
    if (panel) {
      /* косяк ДС: у .panel нет position — абсолютный рейл меню якорится к странице
         и «уезжает» от суженного кадра; обвязка ревью выравнивает якорь по кадру */
      if (getComputedStyle(panel).position === 'static') panel.style.position = 'relative';
      if (w) panel.style.width = w + 'px'; else panel.style.width = '';
      applyFrame();                                   /* хром/статус-полосы + высота «экрана» */
      layoutPage();                                   /* отступы вокруг кадра + центрирование */
    }
    if (S.sizeSel) {
      S.sizeSel.fieldText.textContent = S.w ? String(S.w) : '—';
      markSel(S.sizeSel, S.sizeSel.values.indexOf(String(S.w || '')));
    }
    try { window.dispatchEvent(new Event('resize')); } catch (e) {}   /* организмы пересчитывают ширину панели */
    requestAnimationFrame(placeRestore);                              /* кнопка возврата — к правому краю кадра */
  }

  /* ── Подсказки ДС ──────────────────────────────────────────────────────── */
  function layoutHints() {
    if (!S.layer || !S.hintsOn) return;
    S.badges.forEach(function (p) {
      var r = p.el.getBoundingClientRect();
      var off = (r.width === 0 && r.height === 0);     /* элемент скрыт — маркер тоже */
      p.badge.hidden = off;
      if (!off) {
        p.badge.style.left = Math.round(r.right - 10) + 'px';
        p.badge.style.top = Math.round(r.top - 10) + 'px';
      }
    });
  }
  function showBubble(h, badge) {
    closePop();
    var bub = el('div', 'dsr-bubble');
    bub.innerHTML = '<span class="ds-hint-container ds-hint-container--default">' +
                      '<span class="ds-hint-content ds-hint-content--single-content">' +
                        '<span class="ds-hint-content__label"></span>' +
                      '</span>' +
                    '</span>';
    bub.querySelector('.ds-hint-content__label').textContent = (h.num != null ? '№' + h.num + '. ' : '') + h.text;
    document.body.appendChild(bub);
    var r = badge.getBoundingClientRect();
    var br = bub.getBoundingClientRect();
    var left = Math.max(8, Math.min(r.left, window.innerWidth - br.width - 8));
    var top = r.bottom + 8;
    if (top + br.height > window.innerHeight - 8) top = Math.max(8, r.top - br.height - 8);
    bub.style.left = Math.round(left) + 'px';
    bub.style.top = Math.round(top) + 'px';
    S.bubble = bub;
  }
  function setHints(on) {
    if (!S.hintsEls) return;
    S.hintsOn = on;
    if (S.hintsEls.btn) {
      S.hintsEls.btn.classList.toggle('is-on', on);
      S.hintsEls.btn.classList.toggle('ds-btn--accent', on);
      S.hintsEls.btn.classList.toggle('ds-btn--neutral', !on);
    }
    document.body.classList.toggle('dsr-hints-on', on);
    if (on) {
      if (!S.layer) {
        S.layer = el('div', 'dsr-layer');
        document.body.appendChild(S.layer);
        S.badges = [];
        S.hintsEls.hints.forEach(function (h) {
          var target = null;
          try { target = document.querySelector(h.target); } catch (e) {}
          if (!target) return;
          target.classList.add('dsr-target');
          var badge = el('button', 'dsr-badge', String(h.num != null ? h.num : '!'));
          badge.type = 'button';
          badge.title = 'Подсказка ДС';
          badge.addEventListener('click', function (e) { e.stopPropagation(); showBubble(h, badge); });
          S.layer.appendChild(badge);
          S.badges.push({ el: target, badge: badge });
        });
        var raf = null;
        var relayout = function () {
          if (raf) return;
          raf = requestAnimationFrame(function () { raf = null; layoutHints(); });
        };
        window.addEventListener('scroll', relayout, true);
        window.addEventListener('resize', relayout);
      }
      if (S.badges) S.badges.forEach(function (p) { p.el.classList.add('dsr-target'); });
      layoutHints();
    } else {
      closePop();
      if (S.layer) S.layer.hidden = true;
      if (S.badges) S.badges.forEach(function (p) { p.badge.hidden = true; p.el.classList.remove('dsr-target'); });
    }
    if (on && S.layer) { S.layer.hidden = false; layoutHints(); }
  }

  /* ── Скрытие панели ────────────────────────────────────────────────────── */
  function setHidden(v, save) {
    S.hidden = v;
    if (save) persist();
    if (S.bar) S.bar.hidden = v;
    /* кнопку возврата не показываем в юзерской ссылке (?ui=0) */
    if (S.restore) S.restore.hidden = !(v && Q.ui !== '0');
    if (v) { closePop(); closeSels(); placeRestore(); }
  }
  /* Возврат приклеен к правому краю кадра (у .panel нет position — якорь считаем сами) */
  function panelEl() { return document.getElementById('panel') || document.querySelector('.panel'); }
  /* Раскладка страницы: отступы вокруг кадра ± центрирование по горизонтали */
  function layoutPage() {
    if (Q.ui === '0') return;                       /* чистая юзерская ссылка — страницу не трогаем */
    var panel = panelEl();
    if (!panel) return;
    var w = panel.getBoundingClientRect().width;
    var g = 24;                                     /* боковые отступы кадра */
    var gt = 16;                                    /* от плашки бара до экрана — 16 (с подложкой и без) */
    var gc = 16;                                    /* с хромом — тот же зазор 16 */
    var vw = document.documentElement.clientWidth;
    panel.style.marginTop = chromeOn() ? '0px' : gt + 'px';
    panel.style.marginBottom = (S.navEl && !S.navEl.hidden) ? '0px' : g + 'px';
    if (chromeOn()) {                               /* хром и навбар ходят с кадром */
      S.chromeEl.style.marginTop = gc + 'px';
      S.chromeEl.style.marginBottom = '0px';
      S.chromeEl.style.marginLeft = panel.style.marginLeft;
      S.chromeEl.style.marginRight = panel.style.marginRight;
    }
    if (S.navEl && !S.navEl.hidden) {
      S.navEl.style.marginTop = '0px';
      S.navEl.style.marginBottom = g + 'px';
      S.navEl.style.marginLeft = panel.style.marginLeft;
      S.navEl.style.marginRight = panel.style.marginRight;
    }
    if (w + g * 2 <= vw) {                          /* кадр влезает в окно — по центру */
      panel.style.marginLeft = 'auto';
      panel.style.marginRight = 'auto';
    } else {                                        /* кадр шире окна — отступ слева, справа прокрутка */
      panel.style.marginLeft = g + 'px';
      panel.style.marginRight = g + 'px';
    }
  }
  function placeRestore() {
    if (!S.restore || S.restore.hidden) return;
    var panel = panelEl();
    if (!panel) return;
    var r = panel.getBoundingClientRect();
    var x = r.right + 8, y = r.top + 8;                       /* жёлоб справа от кадра */
    if (x + 44 > window.innerWidth - 4) { x = window.innerWidth - 44; y = r.top + 72; }  /* жёлоба нет — под шапкой */
    S.restore.style.left = Math.round(x + window.scrollX) + 'px';
    S.restore.style.top = Math.round(y + window.scrollY) + 'px';
  }

  /* ── Подложка Chrome — точно по макету «Гайды»:
     1440×900 — десктопный хром 86 (вкладки 43 + тулбар 43);
     телефон 375×812 и планшет — мобильный набор: статусбар 44 + мобильный хром 66 + навбар 20 ── */
  var CHROME_H = 86;
  var STATUS_H = 44, MBAR_H = 66, NAV_H = 20;
  function isMobileW(w) { return w === '375' || w === '1024'; }
  function chromeHFor(w) { return isMobileW(w) ? (STATUS_H + MBAR_H) : CHROME_H; }
  function navHFor(w) { return isMobileW(w) ? NAV_H : 0; }
  function chromeOn() { return !!(S.chromeEl && S.sections.chrome !== false); }
  function buildChrome() {
    var A = function (n) { return BASE + 'dsr-assets/' + n + '.svg'; };
    var ch = el('div', 'dsr-chrome');
    ch.innerHTML =
      '<div class="dsr-chrome__desktop">' +
        '<div class="dsr-chrome__top">' +
          '<div class="dsr-chrome__tabs">' +
            '<div class="dsr-chrome__bookend"><span class="dsr-chrome__roundbtn"><img src="' + A('chevron') + '" alt=""></span></div>' +
            '<div class="dsr-chrome__tab"><img class="dsr-chrome__favicon" src="' + A('logo-iiko') + '" alt="">' +
              '<span class="dsr-chrome__tabname">iiko</span><img class="dsr-chrome__tabclose" src="' + A('x-close') + '" alt=""></div>' +
            '<div class="dsr-chrome__newtab"><img src="' + A('new-tab') + '" alt=""></div>' +
          '</div>' +
          '<div class="dsr-chrome__win">' +
            '<span class="dsr-chrome__winbtn"><i class="dsr-chrome__min"></i></span>' +
            '<span class="dsr-chrome__winbtn"><i class="dsr-chrome__max"></i></span>' +
            '<span class="dsr-chrome__winbtn dsr-chrome__winbtn--close"><img src="' + A('close-window') + '" alt=""></span>' +
          '</div>' +
        '</div>' +
        '<div class="dsr-chrome__bar">' +
          '<span class="dsr-chrome__nav"><img src="' + A('back') + '" alt=""><img src="' + A('forward') + '" alt=""><img src="' + A('refresh') + '" alt=""></span>' +
          '<span class="dsr-chrome__url"><img class="dsr-chrome__lock" src="' + A('lock') + '" alt="">' +
            '<span class="dsr-chrome__urltext">iiko</span><img class="dsr-chrome__star" src="' + A('star') + '" alt=""></span>' +
          '<span class="dsr-chrome__right"><img src="' + A('puzzle') + '" alt=""><span class="dsr-chrome__div"></span>' +
            '<img src="' + A('profile') + '" alt=""><img src="' + A('kebab') + '" alt=""></span>' +
        '</div>' +
      '</div>' +
      '<div class="dsr-chrome__mobile">' +
        '<div class="dsr-status"><span class="dsr-status__time">8:00</span><img class="dsr-status__stats" src="' + A('stats') + '" alt=""></div>' +
        '<div class="dsr-mbar">' +
          '<img class="dsr-mbar__home" src="' + A('home') + '" alt="">' +
          '<span class="dsr-mbar__url"><img class="dsr-mbar__lock" src="' + A('lock-mobile') + '" alt=""><span class="dsr-mbar__text">iiko</span></span>' +
          '<span class="dsr-mbar__tabs">1</span>' +
          '<img class="dsr-mbar__more" src="' + A('more') + '" alt="">' +
        '</div>' +
      '</div>';
    return ch;
  }
  /* Размеры «экрана»: подложка по пресету, приложению — остаток высоты */
  function applyFrame() {
    var panel = panelEl();
    if (!panel) return;
    var w = S.w ? String(S.w) : '';
    var ph = (w && S.presetH) ? S.presetH[w] : null;
    var on = chromeOn();
    if (S.chromeEl) {
      S.chromeEl.hidden = !on;
      S.chromeEl.dataset.w = w;
      S.chromeEl.style.width = w ? w + 'px' : '';
    }
    if (S.navEl) {
      S.navEl.hidden = !(on && navHFor(w) > 0);
      S.navEl.dataset.w = w;
      S.navEl.style.width = w ? w + 'px' : '';
    }
    if (ph) {
      panel.style.height = (ph - (on ? chromeHFor(w) : 0) - (on ? navHFor(w) : 0)) + 'px';
      panel.style.overflow = 'auto';
    } else {
      panel.style.height = ''; panel.style.overflow = '';
    }
  }

  /* ── Отрисовка ─────────────────────────────────────────────────────────── */
  function build() {
    var reg = S.registry || {};
    var steps = reg['шаги'] || reg.steps || [];
    var hints = reg['подсказки'] || reg.hints || [];
    var paths = reg['пути'] || reg.paths || [];
    var adaptive = reg['адаптив'] === true || reg.adaptive === true;

    var bar = el('div', 'dsr-bar');
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Панель ревью');
    S.bar = bar;
    /* Страница-канва: фон под кадром (в чистой юзерской ссылке ?ui=0 не ставим) */
    if (Q.ui !== '0') document.body.classList.add('dsr-page');

    /* Заголовок — название раздела (проекта); название экрана не дублируем — оно в селекте.
       Может быть длинным — режем многоточием, полный текст в подсказке */
    var title = reg['проект'] || reg.project || document.title;
    var titleEl = el('span', 'dsr-bar__title', title);
    titleEl.title = title;
    if (S.sections.title === false) titleEl.hidden = true;   /* «Название» — выключается в ⚙ */
    S.titleEl = titleEl;
    bar.appendChild(titleEl);

    /* Экраны — селект ДС (название текущего экрана + список), стрелки листают;
       блок центрируется в баре: растушки слева и справа */
    var cur = currentStep(steps);
    if (steps.length >= 2) {
      bar.appendChild(el('span', 'dsr-grow'));
      /* блок «Экраны» — дивами, отступы явные: [лейбл] →8→ [группа: ‹ →4→ 1/3 →4→ ›] →8→ [селект] */
      var sec = el('div', 'dsr-sec');
      sec.appendChild(el('span', 'dsr-lbl', 'Экраны:'));
      var stepsNav = el('div', 'dsr-steps');             /* группа «шагов»: стрелки, счётчик, форм-селект — внутри 4 */
      var countEl = el('span', 'dsr-count');             /* счётчик «1/3» — между стрелками */
      countEl.setAttribute('aria-label', 'Счётчик экранов');
      var prev = el('button', 'ds-btn-icon ds-btn-icon--s ds-btn-icon--neutral ds-btn-icon--text');
      prev.type = 'button'; prev.title = 'Предыдущий экран (←)'; prev.setAttribute('aria-label', 'Предыдущий экран');
      prev.innerHTML = '<span class="ds-btn-icon__icon"><span class="material-icons" aria-hidden="true">chevron_left</span></span>';
      var next = el('button', 'ds-btn-icon ds-btn-icon--s ds-btn-icon--neutral ds-btn-icon--text');
      next.type = 'button'; next.title = 'Следующий экран (→)'; next.setAttribute('aria-label', 'Следующий экран');
      next.innerHTML = '<span class="ds-btn-icon__icon"><span class="material-icons" aria-hidden="true">chevron_right</span></span>';
      prev.addEventListener('click', function () { var i = currentStep(steps); if (i > 0) goStep(i - 1); });
      next.addEventListener('click', function () { var i = currentStep(steps); if (i >= 0 && i < steps.length - 1) goStep(i + 1); });
      stepsNav.appendChild(prev);
      stepsNav.appendChild(countEl);
      stepsNav.appendChild(next);
      sec.appendChild(stepsNav);
      S.countEl = countEl;
      var stepsSel = mkSelect({
        cls: 'dsr-sel--steps',
        aria: 'Экраны прототипа',
        items: steps.map(function (st, i) { return { label: st.title || ('Экран ' + (i + 1)), hint: st.hint || '' }; }),
        onPick: function (i) { goStep(i); }
      });
      sec.appendChild(stepsSel.sel);   /* селект — сестрица группы: от › до него 8 (gap секции) */
      S.selEls = stepsSel;
      bar.appendChild(sec);
      S.stepsEls = { steps: steps, prev: prev, next: next };
      if (S.sections.steps === false) sec.hidden = true;
      S.secSteps = sec;
      setCurrent(cur);
    }

    if (steps.length < 2) bar.appendChild(el('span', 'dsr-grow'));   /* без «Экранов» правый блок уводим вправо */

    /* Размер (только если у макета есть адаптив): селект ДС с тремя гайдовыми размерами 1440/1024/375 */
    if (adaptive) {
      var presets = (reg['размеры'] || ['1440', '1024', '375']).map(String);
      S.presetH = { '1440': 900, '1024': 768, '375': 812 };   /* экраны: ширина × высота — как настоящие */
      if (!S.w || presets.indexOf(String(S.w)) === -1) S.w = presets[0];
      var sec2 = el('span', 'dsr-sec');
      sec2.appendChild(el('span', 'dsr-lbl', 'Размер:'));
      var sizeSel = mkSelect({
        cls: 'dsr-sel--sizes',
        aria: 'Ширина кадра',
        items: presets.map(function (p) { return { label: p }; }),
        onPick: function (i) { applyW(presets[i]); }
      });
      sizeSel.values = presets;
      sec2.appendChild(sizeSel.sel);
      bar.appendChild(sec2);
      S.sizeSel = sizeSel;
      S.secSizes = sec2;
      if (S.sections.sizes === false) sec2.hidden = true;
    }

    /* Подсказки ДС — внутреннее; по умолчанию выключено (кнопка — компонент ДС) */
    if (hints.length) {
      var hb = el('button', 'ds-btn ds-btn--s ds-btn--neutral ds-btn--outlined dsr-hints-btn', 'Подсказки ДС · ' + hints.length);
      hb.type = 'button';
      hb.title = 'Номерные маркеры пробелов ДС (в модели и журнале); по умолчанию выключено';
      hb.addEventListener('click', function () { setHints(!S.hintsOn); });
      bar.appendChild(hb);
      S.hintsEls = { btn: hb, hints: hints };
      S.secHints = hb;
      if (S.sections.hints !== true) hb.hidden = true;   /* по умолчанию кнопка подсказок скрыта (включается в ⚙) */
    }

    /* Пути — ссылки на описание/блоки макета (кнопка ДС) */
    if (paths.length) {
      var sec3 = el('span', 'dsr-sec');
      paths.forEach(function (p) {
        var a = el('a', 'ds-btn ds-btn--s ds-btn--neutral ds-btn--outlined', p.label || 'Схемы');   /* вид — как у «Подсказок ДС» */
        if (p.url) { a.href = p.url; a.target = '_blank'; a.rel = 'noopener'; }
        else { a.setAttribute('aria-disabled', 'true'); a.title = 'Страница в разработке'; }   /* «Схемы» — пока никуда не ведёт */
        sec3.appendChild(a);
      });
      bar.appendChild(sec3);
      S.secPaths = sec3;
      if (S.sections.paths !== true) sec3.hidden = true;   /* «Пути» — по умолчанию скрыты (включаются в ⚙) */
    }

    /* Настройки (иконка ДС settings) и скрытие (кнопка ДС) */
    var gear = el('button', 'ds-btn-icon ds-btn-icon--s ds-btn-icon--neutral ds-btn-icon--text dsr-gear');
    gear.type = 'button';
    gear.title = 'Настройки панели';
    gear.setAttribute('aria-label', 'Настройки панели');
    gear.innerHTML = '<span class="ds-btn-icon__icon"><span class="material-icons" aria-hidden="true">settings</span></span>';
    gear.addEventListener('click', function (e) { e.stopPropagation(); openSettings(gear); });

    var hide = el('button', 'ds-btn-icon ds-btn-icon--s ds-btn-icon--neutral ds-btn-icon--text dsr-hide');
    hide.type = 'button';
    hide.title = 'Скрыть панель';
    hide.setAttribute('aria-label', 'Скрыть панель');
    hide.innerHTML = '<span class="ds-btn-icon__icon"><span class="material-icons" aria-hidden="true">visibility_off</span></span>';
    hide.addEventListener('click', function () { setHidden(true, true); });
    var iconGroup = el('span', 'ds-btn-icon-group');   /* группа кнопок-иконок ДС: настройки + скрытие */
    iconGroup.appendChild(gear);
    iconGroup.appendChild(hide);
    bar.appendChild(iconGroup);

    document.body.insertBefore(bar, document.body.firstChild);

    fitSizesField();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitSizesField);
    /* финальные пересчёты после полной загрузки: css применён, раскладка бара устоялась
       (ранние замеры могут пройти до применения стилей или в момент переноса бара) */
    function lateFit() { requestAnimationFrame(function () { requestAnimationFrame(fitSizesField); }); }
    if (document.readyState === 'complete') lateFit();
    else window.addEventListener('load', lateFit);

    /* Кнопка возврата (когда панель скрыта; в ?ui=0 не показывается):
       прилипает к правому краю кадра — позицию считает placeRestore */
    S.restore = el('button', 'dsr-restore');
    S.restore.type = 'button';
    S.restore.title = 'Показать панель ревью';
    S.restore.setAttribute('aria-label', 'Показать панель ревью');
    S.restore.innerHTML = '<span class="material-icons" aria-hidden="true">settings</span>';
    S.restore.addEventListener('click', function () { setHidden(false, true); });
    S.restore.hidden = true;
    document.body.appendChild(S.restore);
    window.addEventListener('resize', function () { layoutPage(); placeRestore(); });

    /* Подложка Chrome: окно браузера вокруг «экрана» + статус-полосы адаптивов */
    S.chromeEl = buildChrome();
    S.navEl = el('div', 'dsr-nav');
    S.navEl.innerHTML = '<span class="dsr-nav__home"></span>';
    var pnl = panelEl();
    if (pnl && pnl.parentNode) {
      pnl.parentNode.insertBefore(S.chromeEl, pnl);
      pnl.parentNode.insertBefore(S.navEl, pnl.nextSibling);   /* null → в конец */
    }

    /* Стартовые состояния */
    if (adaptive && S.w) applyW(S.w, false);
    else layoutPage();
    if (S.hintsEls && S.hintsOn) setHints(true);
    setHidden(S.hidden, false);
  }

  /* ── Настройки (⚙): какие секции показывать — меню ДС + туглы ДС ────────── */
  function applySectionVisibility() {
    if (S.titleEl) S.titleEl.hidden = S.sections.title === false;
    if (S.secSteps) S.secSteps.hidden = S.sections.steps === false;
    if (S.secSizes) S.secSizes.hidden = S.sections.sizes === false;
    if (S.secHints) S.secHints.hidden = S.sections.hints !== true;   /* подсказки — по умолчанию скрыты */
    if (S.secPaths) S.secPaths.hidden = S.sections.paths !== true;   /* «Пути» — по умолчанию скрыты */
    applyFrame();                                   /* подложка: высота «экрана» зависит от неё */
    layoutPage();
  }
  function openSettings(anchor) {
    if (S.pop) { S.pop.remove(); S.pop = null; return; }
    closePop();
    closeSels();
    var pop = el('div', 'ds-menu-container dsr-pop');
    var trow = el('div', 'ds-menu-container__title');
    trow.appendChild(el('span', 'ds-text-body-s-14-normal-medium', 'Настройки панели'));
    pop.appendChild(trow);
    var avail = [];
    if (S.titleEl) avail.push(['title', 'Название']);
    if (S.secSteps) avail.push(['steps', 'Экраны']);
    if (S.secSizes) avail.push(['sizes', 'Размеры']);
    if (S.hintsEls) avail.push(['hints', 'Подсказки ДС']);   /* возвращает кнопку подсказок в бар */
    if (S.secPaths) avail.push(['paths', 'Схемы']);   /* возвращает кнопку «Схемы» в бар (по умолчанию скрыта) */
    if (S.chromeEl) avail.push(['chrome', 'Подложка Chrome']);   /* подложка — последней в списке (по запросу) */
    avail.forEach(function (kv) {
      var row = el('div', 'dsr-pop__row');
      var lbl = el('label', 'ds-slide-toggle');
      var srow = el('span', 'ds-slide-toggle__row');
      var input = document.createElement('input');
      input.type = 'checkbox';
      input.className = 'ds-slide-toggle__input';
      input.checked = (kv[0] === 'hints' || kv[0] === 'paths')
        ? S.sections[kv[0]] === true
        : S.sections[kv[0]] !== false;
      srow.appendChild(input);
      srow.appendChild(el('span', 'ds-slide-toggle__track'));
      srow.appendChild(el('span', 'ds-slide-toggle__title', kv[1]));
      lbl.appendChild(srow);
      row.appendChild(lbl);
      input.addEventListener('change', function () {
        S.sections[kv[0]] = input.checked;
        persist();
        applySectionVisibility();
      });
      pop.appendChild(row);
    });
    pop.appendChild(el('div', 'dsr-pop__note',
      'Настройки хранятся в браузере. Панель прячется кнопкой с перечёркнутым глазом; вернуть — кнопка у правого края кадра. ' +
      '?ui=0 — чистая ссылка без панели (для юзера).'));
    document.body.appendChild(pop);
    placePop(pop, anchor);
    S.pop = pop;
  }

  /* ── Общие обработчики ─────────────────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    if (S.pop && !S.pop.contains(e.target) && !e.target.closest('.dsr-gear')) { S.pop.remove(); S.pop = null; }
    if (S.bubble && !S.bubble.contains(e.target) && !e.target.closest('.dsr-badge')) { S.bubble.remove(); S.bubble = null; }
    if (!e.target.closest('.dsr-sel')) closeSels();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closePop(); closeSels(); return; }
    if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var t = e.target;
    if (t && t.closest && t.closest('input, textarea, select, [contenteditable="true"]')) return;
    if (S.hidden || !S.stepsEls || S.sections.steps === false) return;
    var i = currentStep(S.stepsEls.steps), ni = e.key === 'ArrowLeft' ? i - 1 : i + 1;
    if (i >= 0 && ni >= 0 && ni < S.stepsEls.steps.length) { e.preventDefault(); goStep(ni); }
  });

  /* ── Запуск ────────────────────────────────────────────────────────────── */
  function addCss() {
    if (document.querySelector('link[href*="ds-review.css"]')) return;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = BASE + 'ds-review.css';
    (document.head || document.documentElement).appendChild(l);
  }
  function loadRegistry(cb) {
    if (S.registry) { cb(); return; }
    var s = document.createElement('script');
    s.src = (cs && cs.getAttribute('data-registry')) || 'layouts.js';   /* рядом со страницей */
    s.onload = function () { S.registry = window.dsLayouts || null; cb(); };
    s.onerror = function () { S.registry = null; cb(); };                /* нет реестра — работаем без него */
    document.head.appendChild(s);
  }
  function init() {
    if (!document.body) { document.addEventListener('DOMContentLoaded', init); return; }
    addCss();
    loadRegistry(function () { build(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
