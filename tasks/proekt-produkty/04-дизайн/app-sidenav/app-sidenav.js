/* app-sidenav.js — свёрнутое боковое меню (один источник разметки на все страницы-кадры).
   Вставляется в #panel между шапкой и .frame; видно только на десктопе (>1160) —
   на планшете и мобильном меню уезжает в гамбургер шапки (поведение ждём макетом).
   Состав пунктов — плейсхолдеры DS-макета (иконка «i»), как в узле 55074:555:
   два обычных, выбранный, «подменю» с шевроном и зелёной точкой (состояние hover из макета),
   три обычных, три с синей точкой; подвал — разделитель, два пункта и аватар «КК».
   Белый индикатор выбранного пункта убран по указанию заказчика (13.09.2026).
   Реальные разделы меню — по отдельной спецификации. */
(function () {
  function item(opts) {
    var cls = 'ds-sidenav-item ds-sidenav-item--l1 ds-sidenav-item--collapsed app-snav__item';
    if (opts.selected) cls += ' app-snav__item--selected';
    if (opts.hover) cls += ' app-snav__item--hover';
    var inner = '<span class="app-snav__icon"><img src="app-sidenav/icon-' + (opts.chevron ? 'chevron' : 'info') + '.svg" width="20" height="20" alt=""></span>';
    if (opts.dot) inner += '<span class="app-snav__dot app-snav__dot--' + opts.dot + '"></span>';
    return '<div class="' + cls + '" role="button" aria-label="Пункт меню">' + inner + '</div>';
  }

  var BODY =
    item({}) + item({}) +
    item({ selected: true }) +
    item({}) +
    item({ chevron: true, hover: true, dot: 'positive' }) +
    item({}) + item({}) + item({}) +
    item({ dot: 'accent' }) + item({ dot: 'accent' }) + item({ dot: 'accent' });

  var FOOTER =
    item({}) + item({}) +
    '<div class="ds-sidenav-item ds-sidenav-item--l1 ds-sidenav-item--collapsed app-snav__item" role="button" aria-label="Пользователь КК">' +
      '<span class="app-snav__avatar"><img src="app-sidenav/avatar-kk.svg" width="20" height="20" alt=""><span class="app-snav__avatar-text">КК</span></span>' +
    '</div>';

  var MARKUP =
    '<div class="app-snav__header"><img src="app-sidenav/logo-iiko-mark.svg" width="24" height="24" alt="iiko"></div>' +
    '<div class="app-snav__control"><span class="app-snav__collapse" role="button" aria-label="Развернуть меню"><span class="material-icons" aria-hidden="true">chevron_right</span><span class="app-snav__dot app-snav__dot--positive"></span></span></div>' +
    '<div class="app-snav__divider"></div>' +
    '<div class="app-snav__body">' + BODY + '</div>' +
    '<div class="app-snav__footer"><div class="app-snav__divider"></div>' + FOOTER + '</div>';

  function init() {
    var panel = document.getElementById('panel') || document.querySelector('.panel');
    if (!panel || panel.querySelector('.app-snav')) return;
    var frame = panel.querySelector('.frame');
    if (!frame) return;
    var nav = document.createElement('nav');
    nav.className = 'app-snav ds-sidenav-view';
    nav.setAttribute('aria-label', 'Боковое меню');
    nav.innerHTML = MARKUP;
    panel.insertBefore(nav, frame);

    function applyWidth() {
      panel.classList.toggle('app-snav-on', panel.clientWidth > 1160);
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
