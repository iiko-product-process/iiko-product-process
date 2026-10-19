/* app-header/app-header.js — сквозная шапка приложения («App bars: top», node 364:17664).
   Один источник разметки на все страницы-кадры: шапка вставляется первым ребёнком .panel
   (перед .frame), поэтому не уезжает при прокрутке содержимого.
   Пока реализовано только свёрнутое десктопное состояние из макета: кликабельные зоны помечены,
   но меню/дропдауны не подключены — ждём спецификаций. Мобильная версия — ждём макет.
   Ширина кадра: >1160 — десктопный макет (364:17664); 481–1160 — планшетный (429:19815): табы скрыты,
   пилюля с диапазоном дат, колокол right 80, пользователь — только аватар (481–760 — без пилюли);
   ≤480 — мобильный (1818:73188, полоса 56): бургер, пилюля-диапазон, tune, шестерёнка с бейджем. */
(function () {
  var MARKUP =
    '<div class="apph__left">' +
      '<div class="apph__logo-block">' +
        '<span class="apph__item" role="button" tabindex="0" aria-label="Меню"><img src="app-header/icon-menu.svg" width="24" height="24" alt=""></span>' +
        '<span class="apph__logo-wrap"><img src="app-header/logo-iiko.svg" width="60" height="24" alt="iiko"></span>' +
      '</div>' +
      '<div class="apph__store apph__item" role="button" tabindex="0" aria-label="Ресторан: Romashka OOO">' +
        '<span class="material-icons apph__store-icon" aria-hidden="true">storefront</span>' +
        '<span class="apph__store-name">Romashka OOO</span>' +
        '<img src="app-header/icon-chevron-down.svg" width="24" height="24" alt="">' +
      '</div>' +
    '</div>' +
    '<div class="apph__center">' +
      '<div class="apph__tabs" role="tablist" aria-label="Период">' +
        '<span class="apph__tab" role="tab" aria-selected="false">д</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">н</span>' +
        '<span class="apph__tab apph__tab--active" role="tab" aria-selected="true">м</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">г</span>' +
        '<span class="apph__tab" role="tab" aria-selected="false">п</span>' +
      '</div>' +
      '<div class="apph__pill">' +
        '<div class="apph__select">' +
          '<span class="apph__nav apph__item" role="button" tabindex="0" aria-label="Предыдущий месяц"><img src="app-header/icon-chevron-left.svg" width="20" height="20" alt=""></span>' +
          '<span class="apph__date apph__item" role="button" tabindex="0" aria-label="Период"><span class="apph__date-text apph__date-text--desktop">Apr. 2024</span><span class="apph__date-text apph__date-text--tablet">15/04/21 - 20/04/21</span><img src="app-header/icon-arrow-drop-down.svg" width="16" height="16" alt=""></span>' +
          '<span class="apph__nav apph__item" role="button" tabindex="0" aria-label="Следующий месяц"><img src="app-header/icon-chevron-right.svg" width="20" height="20" alt=""></span>' +
        '</div>' +
        '<span class="apph__item" role="button" tabindex="0" aria-label="Календарь"><img src="app-header/icon-date-range.svg" width="24" height="24" alt=""></span>' +
      '</div>' +
    '</div>' +
    '<span class="apph__bell apph__item" role="button" tabindex="0" aria-label="Уведомления"><img src="app-header/icon-bell.svg" width="24" height="24" alt=""></span>' +
    '<div class="apph__user apph__item" role="button" tabindex="0" aria-label="Администратор">' +
      '<img class="apph__avatar-img" src="app-header/icon-avatar.svg" width="24" height="24" alt="">' +
      '<span class="apph__avatar-plain" aria-hidden="true"></span>' +
      '<span class="apph__user-name">Администратор</span>' +
      '<img class="apph__user-chevron" src="app-header/icon-chevron-down.svg" width="24" height="24" alt="">' +
    '</div>' +
    '<div class="apph__mright">' +
      '<span class="apph__mpill"><span class="apph__mdate">15.04.21 - 20.04.21</span><img src="app-header/icon-date-range.svg" width="24" height="24" alt=""></span>' +
      '<span class="apph__item" role="button" tabindex="0" aria-label="Фильтры"><img src="app-header/icon-tune.svg" width="24" height="24" alt=""></span>' +
      '<span class="apph__item apph__badge-wrap" role="button" tabindex="0" aria-label="Настройки"><img src="app-header/icon-settings.svg" width="24" height="24" alt=""><span class="apph__badge">2</span></span>' +
    '</div>';

  function init() {
    var panel = document.getElementById('panel') || document.querySelector('.panel');
    if (!panel || panel.querySelector('.apph')) return;
    var hdr = document.createElement('header');
    hdr.className = 'apph';
    hdr.setAttribute('role', 'banner');
    hdr.innerHTML = MARKUP;
    panel.insertBefore(hdr, panel.firstChild);

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
