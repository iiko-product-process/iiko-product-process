/* device-chrome.js — системные полосы устройств (статусбар + навбар) для страниц-кадров.
   Статусбар: «9:41» + иконки (сеть/wi-fi/батарея); навбар: home-индикатор.
   Только при подложках планшета/телефона (классы device-* ставит пресет-JS страницы);
   на мониторе (device-desktop) полос нет. В чистом кадре (?ui=0) классов device-* нет —
   полосы не добавляются.
   Подключать ПОСЛЕ app-header.js: статусбар встаёт перед шапкой (первым ребёнком #panel). */
(function () {
  function makeStatus() {
    var st = document.createElement('div');
    st.id = 'dev-status';
    st.className = 'dev-status';
    st.setAttribute('aria-hidden', 'true');
    st.innerHTML = '<span class="dev-status__time">9:41</span>' +
      '<span class="dev-status__icons">' +
      '<span class="material-icons">signal_cellular_4_bar</span>' +
      '<span class="material-icons">wifi</span>' +
      '<span class="material-icons">battery_full</span>' +
      '</span>';
    return st;
  }
  function makeNav() {
    var nv = document.createElement('div');
    nv.id = 'dev-nav';
    nv.className = 'dev-nav';
    nv.setAttribute('aria-hidden', 'true');
    nv.innerHTML = '<span class="dev-nav__home"></span>';
    return nv;
  }
  function ensure() {
    var panel = document.getElementById('panel');
    if (!panel) return;
    var cls = document.body.classList;
    var need = cls.contains('device-phone') || cls.contains('device-tablet');
    var st = document.getElementById('dev-status');
    var nv = document.getElementById('dev-nav');
    if (!need) {
      if (st && st.parentNode) st.parentNode.removeChild(st);
      if (nv && nv.parentNode) nv.parentNode.removeChild(nv);
      return;
    }
    if (!st || st.parentNode !== panel) panel.insertBefore(makeStatus(), panel.firstChild);
    if (!nv || nv.parentNode !== panel) panel.appendChild(makeNav());
  }
  if (window.MutationObserver) {
    new MutationObserver(ensure).observe(document.body, { attributes: true, attributeFilter: ['class'] });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ensure); else ensure();
  window.addEventListener('resize', ensure);
})();
