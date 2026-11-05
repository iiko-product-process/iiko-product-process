/* ============================================================
   touch-mode.js — «тач-режим» прототипов (подключается на всех страницах кадров).
   Включается: ширина кадра ≤ 768 (телефон/планшет) · реальное тач-устройство
   ((hover:none)/(pointer:coarse)) · ?touch=1. Выключить: ?touch=0.
   Что делает:
     • тап по строке таблицы раскрывает её действия (ховера на тач нет);
       тап мимо — закрывает; действие работает обычным нажатием;
     • долгое нажатие (450 мс) на кнопке с тултипом показывает подсказку;
       клик после долгого нажатия не выполняется (иначе «прочитать» = «нажать»);
     • в шапке ширины режим помечается «· тач»;
     • в кадре вместо курсора — круг-«палец» ~44 px (размер среднего пальца);
     • ховеры компонентов в кадре отключены: селекторы с :hover перестают совпадать, при выходе —
       возвращаются; хром ревью (шапка ширины, плашки подсказок) не трогаем;
     • свайп-прокрутка: протяжка «пальцем» по полосе табов или таблице прокручивает её по
       горизонтали (в мобильном слое ДС скроллбары скрыты — свайп и есть управление);
       активный таб подскролливается в видимую зону при загрузке и смене ширины кадра.
   Стилевая часть — touch-mode.css.
   ============================================================ */
(function () {
  var q = new URLSearchParams(location.search);
  var force = q.get('touch'); // '1' | '0' | null
  var panel = document.getElementById('panel');
  if (!panel) return;
  var mq = window.matchMedia ? window.matchMedia('(hover: none), (pointer: coarse)') : null;
  var LONG_PRESS = 450, TIP_LINGER = 1200;

  function closest(el, sel) {
    while (el && el.nodeType === 1) { if (el.matches(sel)) return el; el = el.parentElement; }
    return null;
  }
  function isTouch() { return document.body.getAttribute('data-touch') === '1'; }

  // ── «Палец» вместо курсора: круг ~44 px (размер среднего пальца), ходит за указателем.
  // Настоящий курсор в кадре скрыт (см. touch-mode.css); мышь двигает круг, тап — подсвечивает.
  var finger = document.createElement('span');
  finger.className = 'touch-finger';
  finger.setAttribute('aria-hidden', 'true');
  document.body.appendChild(finger);
  function inPanel(x, y) {
    var r = panel.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  }
  function moveFinger(x, y) { finger.style.left = x + 'px'; finger.style.top = y + 'px'; }

  // ── Глушилка ховеров (тач-режим): на тач-устройствах ховера нет. Пока режим включён, все
  // CSS-правила со словом :hover временно становятся несовпадающими (селектор в таблицах стилей
  // меняем :hover → :not(*)); при выходе — возвращаем исходные. Хром ревью не трогаем: там мышь
  // уместна. Это эмуляция того же поведения, что даёт правило ДС «ховеры — только под
  // @media (hover: hover)» (components-web/generator-rules.md, п. 5; журнал DS/fixes.md, п. 26).
  var CHROME_HOVER_KEEP = ['modes-bar', 'hint', 'panel__handle'];
  var hoverRules = null, hoversDead = false;
  function collectHoverRules() {
    var found = [];
    function walk(rules) {
      for (var i = 0; i < rules.length; i++) {
        var r = rules[i];
        if (r.styleSheet) {   // @import — слой компонентов собран импортами
          try { if (r.styleSheet.cssRules) walk(r.styleSheet.cssRules); } catch (e) {}
          continue;
        }
        if (r.cssRules && !r.selectorText) { walk(r.cssRules); continue; }   // @media и пр.
        if (!r.selectorText || r.selectorText.indexOf(':hover') === -1) continue;
        var keep = false;
        for (var k = 0; k < CHROME_HOVER_KEEP.length; k++) {
          if (r.selectorText.indexOf(CHROME_HOVER_KEEP[k]) !== -1) { keep = true; break; }
        }
        if (!keep) found.push({ rule: r, orig: r.selectorText, dead: r.selectorText.split(':hover').join(':not(*)') });
      }
    }
    Array.prototype.forEach.call(document.styleSheets, function (sheet) {
      var rules;
      try { rules = sheet.cssRules; } catch (e) { return; }   // кросс-доменные (Google Fonts) — пропускаем
      if (rules) walk(rules);
    });
    return found;
  }
  function setHovers(alive) {
    if (alive === !hoversDead) return;
    try {
      if (!alive) {
        if (!hoverRules) hoverRules = collectHoverRules();
        hoverRules.forEach(function (h) { try { h.rule.selectorText = h.dead; } catch (e) {} });
        hoversDead = true;
      } else {
        if (hoverRules) hoverRules.forEach(function (h) { try { h.rule.selectorText = h.orig; } catch (e) {} });
        hoversDead = false;
      }
    } catch (e) {}
  }

  // ── Режим: ширина кадра / реальное тач-устройство / ?touch= ──
  var lastTouch = null, lastW = 0;
  function compute() {
    var touch = force === '1' ? true : force === '0' ? false : (panel.clientWidth <= 768 || !!(mq && mq.matches));
    if (touch) document.body.setAttribute('data-touch', '1');
    else { document.body.removeAttribute('data-touch'); finger.classList.remove('is-in', 'is-press'); }
    setHovers(!touch);   // тач: ховеры компонентов глушим; десктоп: возвращаем
    var wMode = document.getElementById('w-mode');
    if (wMode) {
      var base = panel.dataset.mode === 'mobile' ? 'mobile' : 'desktop';
      wMode.textContent = touch ? base + ' · тач' : base;
    }
    // Полоса табов шире кадра — активный таб должен быть виден (M3: scrollable tabs)
    if (touch && (touch !== lastTouch || panel.clientWidth !== lastW)) showActiveTab();
    lastTouch = touch; lastW = panel.clientWidth;
  }
  // ВАЖНО: держим ссылку на observer — без неё сборщик мусора может его забрать.
  // Плюс страховки: в фоновых вкладках/iframe цикл отрисовки на паузе и ResizeObserver молчит,
  // поэтому пересчитываем режим ещё и на тап/клик (после обработчиков ширины) и на resize.
  var ro = null;
  if (window.ResizeObserver) { ro = new ResizeObserver(compute); ro.observe(panel); }
  window.addEventListener('resize', compute);
  document.addEventListener('visibilitychange', compute);   // вернулись из фона — досчитываем режим
  document.addEventListener('pointerup', compute, true);    // конец драга ширины
  document.addEventListener('click', compute);              // после клика по пресету ширины
  compute();

  // ── «Палец»: мышь двигает круг за собой; тап/нажатие — подсветка; за пределами кадра круг прячется ──
  document.addEventListener('pointermove', function (e) {
    if (!isTouch() || e.pointerType !== 'mouse') return;
    if (inPanel(e.clientX, e.clientY)) { moveFinger(e.clientX, e.clientY); finger.classList.add('is-in'); }
    else finger.classList.remove('is-in', 'is-press');
  }, true);
  document.addEventListener('pointerdown', function (e) {
    if (!isTouch() || !inPanel(e.clientX, e.clientY)) return;
    moveFinger(e.clientX, e.clientY);
    finger.classList.add('is-in', 'is-press');
  }, true);
  document.addEventListener('pointerup', function (e) {
    finger.classList.remove('is-press');
    if (isTouch() && e.pointerType !== 'mouse') finger.classList.remove('is-in'); // палец «подняли»
  }, true);

  // ── Тултипы: долгое нажатие (вместо ховера) ──
  var lpTimer = null, lpFired = false;
  function closeTips() {
    Array.prototype.forEach.call(document.querySelectorAll('.tip.is-open'), function (t) { t.classList.remove('is-open'); });
  }
  function endPress() { if (lpTimer) { clearTimeout(lpTimer); lpTimer = null; } }
  document.addEventListener('pointerdown', function (e) {
    if (!isTouch()) return;
    lpFired = false;                 // новый тап сбрасывает подавление клика
    closeTips();
    var wrap = closest(e.target, '.tip-wrap');
    if (!wrap || !wrap.querySelector('.tip')) return;
    lpTimer = setTimeout(function () {
      wrap.querySelector('.tip').classList.add('is-open');
      lpFired = true;
    }, LONG_PRESS);
  }, true);
  document.addEventListener('pointerup', function () {
    if (!isTouch()) return;
    endPress();
    if (lpFired) setTimeout(closeTips, TIP_LINGER);   // даём дочитать после отпускания
  }, true);
  document.addEventListener('pointercancel', function () {
    if (!isTouch()) return;
    endPress();
    if (lpFired) closeTips();
  }, true);
  // клик сразу после долгого нажатия не выполняем
  document.addEventListener('click', function (e) {
    if (!isTouch() || !lpFired) return;
    lpFired = false;
    e.preventDefault();
    e.stopPropagation();
  }, true);
  // на реальных тач-устройствах долгое нажатие не должно вызывать контекстное меню
  document.addEventListener('contextmenu', function (e) {
    if (isTouch() && closest(e.target, '.tip-wrap')) e.preventDefault();
  });

  // ── Действия строк: раскрытие тапом ──
  function closeRows() {
    Array.prototype.forEach.call(document.querySelectorAll('.ds-table-content-row.is-hover'), function (r) { r.classList.remove('is-hover'); });
  }
  document.addEventListener('click', function (e) {
    if (!isTouch()) return;
    if (closest(e.target, '.js-acts, .row-actions')) { closeRows(); return; }   // нажато действие — закрываем раскрытие
    var row = closest(e.target, '.ds-table-content-row');
    if (row && row.querySelector('.js-acts, .row-actions')) { closeRows(); row.classList.add('is-hover'); return; }
    if (!row) closeRows();           // тап мимо строки — закрываем
  });

  // ── Свайп-прокрутка и видимость активного таба (мобильные паттерны ДС) ──
  // Полоса табов на мобиле прокручивается, скроллбар скрыт (components-mobile/Tabs_DS/tabs-mobile.css),
  // а активный таб должен быть в видимой зоне (M3 scrollable tabs) — подскролливаем его.
  function showActiveTab() {
    Array.prototype.forEach.call(document.querySelectorAll('.ds-tabs'), function (tabs) {
      var act = tabs.querySelector('.ds-tab--active');
      if (!act || tabs.scrollWidth <= tabs.clientWidth + 2) return;
      var tr = tabs.getBoundingClientRect(), ar = act.getBoundingClientRect();
      if (ar.left >= tr.left - 1 && ar.right <= tr.right + 1) return;   // уже виден — не дёргаем
      tabs.scrollLeft += (ar.left - tr.left) - (tabs.clientWidth - ar.width) / 2;
    });
  }
  // Мышь в тач-режиме = «палец»: протяжка по горизонтально прокручиваемому контейнеру (полоса
  // табов, обёртка таблицы) прокручивает его — эмуляция свайпа: мышь иначе не сдвинет (скроллбар скрыт).
  function hScrollable(el) {
    for (; el && el.nodeType === 1 && el !== document.body; el = el.parentElement) {
      if (el.scrollWidth > el.clientWidth + 2) {
        var ox = getComputedStyle(el).overflowX;
        if (ox === 'auto' || ox === 'scroll') return el;
      }
    }
    return null;
  }
  var swipe = null, swipeGuard = false;
  document.addEventListener('pointerdown', function (e) {
    swipeGuard = false;
    if (!isTouch() || e.pointerType !== 'mouse' || e.button !== 0 || !inPanel(e.clientX, e.clientY)) return;
    var el = hScrollable(e.target);
    swipe = el ? { el: el, x: e.clientX, y: e.clientY, left: el.scrollLeft, moved: false } : null;
  }, true);
  document.addEventListener('pointermove', function (e) {
    if (!swipe || e.pointerType !== 'mouse') return;
    var dx = e.clientX - swipe.x, dy = e.clientY - swipe.y;
    if (!swipe.moved) {
      if (Math.abs(dx) < 6) return;
      if (Math.abs(dy) > Math.abs(dx)) { swipe = null; return; }   // жест вертикальный — не наш
      swipe.moved = true;
      finger.classList.add('is-in', 'is-press');
    }
    swipe.el.scrollLeft = swipe.left - dx;
  }, true);
  document.addEventListener('pointerup', function () {
    if (swipe) { swipeGuard = swipe.moved; swipe = null; }
  }, true);
  // клик сразу после свайпа не выполняем (иначе протяжка «раскрыла бы строку» или нажала кнопку)
  document.addEventListener('click', function (e) {
    if (!swipeGuard) return;
    swipeGuard = false;
    e.preventDefault();
    e.stopPropagation();
  }, true);

  // ── Тап по строке списка: нажатие делаем ЗАМЕТНЫМ ──
  // В ДС нажатие строки — :active #E0E0E0, но при быстром тапе/клике оно мелькает
  // 30–50 мс — глазом не видно (замечание заказчика 2026-09-13). Держим подсветку
  // ~180 мс от нажатия: отклик виден, а пока палец прижат — работает родной :active.
  var PRESS_LINGER = 180;
  document.addEventListener('pointerdown', function (e) {
    if (!isTouch() || e.pointerType !== 'mouse' || e.button !== 0) return;
    var row = closest(e.target, '.ds-select-item');
    if (!row) return;
    row.classList.add('is-tap-press');
    setTimeout(function () { row.classList.remove('is-tap-press'); }, PRESS_LINGER);
  }, true);
})();
