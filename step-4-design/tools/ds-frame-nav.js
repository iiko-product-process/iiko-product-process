/* ds-frame-nav.js — обвязка ревью: при переходах между страницами-кадрами СОХРАНЯЕМ ширину кадра.
   Зачем: работая в мобильной версии (375/768) в «Поставщиках» и внутренних страницах, переходы
   «туда-сюда» не должны выбрасывать на десктоп по умолчанию (замечание заказчика 2026-09-13).

   Три канала переноса ширины:
     1) window.dsFrameNav(url) — для JS-переходов страниц: location.href = dsFrameNav('figma-….html');
     2) перехват кликов по <a href> на страницу-кадр — дописываем ?w=<текущая ширина>;
     3) запоминание ширины (localStorage 'ds-w') при уходе со страницы + восстановление её в адресе
        при открытии без ?w= (history.replaceState) — покрывает хаб, прямые открытия и перезагрузку.

   Всё некритичное — в try/catch (на file:// доступ к storage/истории может быть закрыт; тогда
   работает перенос по клику и через dsFrameNav). Подключать в <head> БЕЗ defer — восстановление
   адреса должно случиться до скриптов страницы, читающих ?w=. */
(function () {
  var LS_KEY = 'ds-w';
  var MIN = 375, MAX = 1440;

  function frameWidth() {
    var p = document.getElementById('panel');
    return p ? Math.round(p.offsetWidth) : 0;
  }
  function remember(w) {
    try { if (w) localStorage.setItem(LS_KEY, String(w)); } catch (e) {}
  }
  function withW(url, w) {
    var i = url.indexOf('#');
    var path = i === -1 ? url : url.slice(0, i);
    var hash = i === -1 ? '' : url.slice(i);
    if (!w || /[?&]w=/.test(path)) return url;   /* ширина уже задана — не трогаем */
    return path + (path.indexOf('?') === -1 ? '?' : '&') + 'w=' + w + hash;
  }

  /* JS-переходы страниц: location.href = dsFrameNav('figma-….html') */
  window.dsFrameNav = function (url) {
    var w = frameWidth();
    remember(w);
    return withW(url, w);
  };

  /* Открытие без ?w= — вспоминаем последнюю ширину кадра (до скриптов страницы) */
  try {
    if (!new URLSearchParams(location.search).get('w')) {
      var saved = parseInt(localStorage.getItem(LS_KEY), 10) || 0;
      if (saved >= MIN && saved <= MAX) {
        try {
          history.replaceState(null, '', location.pathname +
            (location.search ? location.search + '&' : '?') + 'w=' + saved + location.hash);
        } catch (e2) {}
      }
    }
  } catch (e3) {}

  /* Переходы по ссылкам-страницам кадров: дописываем текущую ширину кадра */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || e.defaultPrevented) return;
    var href = a.getAttribute('href') || '';
    if (!/figma-[\w-]+\.html/i.test(href)) return;   /* только страницы-кадры */
    var w = frameWidth();
    remember(w);
    a.setAttribute('href', withW(href, w));
  }, true);

  /* Уход со страницы (в т.ч. после перетаскивания ручки) — запоминаем ширину */
  window.addEventListener('pagehide', function () { remember(frameWidth()); });
})();
