/* header-content - «хедер контента» (шапка раздела) - организм дизайн-системы.
   Страницы подключают его как ../Design-System/organisms/app-header-content/header-content.css + header-content.js.
   Скрипт делает ровно две вещи:
     1) подставляет иконки <img data-hc-icon="..."> из папки организма: база считается
        по адресу самого скрипта, поэтому разметка работает с любой страницы и при переносе
        папки (тот же приём, что у app-header). Иконки - точные SVG из Figma
        (arrow-back 24; search / edit / add 20; цвет #616161 = Icon/Primary);
     2) переключает части блока, как булевы свойства компонента «Header content» в Figma:
        HeaderContent.set(root, { arrow:false, subtitle:false, status:false,
                                  after:false, search:false, actions:false })
        ставит на корень .hc атрибуты data-hc-*="off" (true - атрибут снимается).
        Нет атрибута = часть показана (дефолты компонента - всё включено).
   Больше скрипт ничего не делает: клики (стрелка назад, поиск, кнопки) - дело страницы,
   обработчики вешает она сама. */
(function () {
  'use strict';

  if (window.HeaderContent) return;   /* повторное подключение - не дублируем */

  var PARTS = ['arrow', 'subtitle', 'status', 'after', 'search', 'actions'];

  /* База ассетов - по адресу самого скрипта: работает с любой страницы */
  var cs = document.currentScript;
  if (!cs) {
    var ss = document.getElementsByTagName('script');
    for (var i = ss.length - 1; i >= 0; i--) {
      if (/header-content\.js/.test(ss[i].src || '')) { cs = ss[i]; break; }
    }
  }
  var HB = (cs && cs.src) ? cs.src.replace(/header-content\.js.*$/, '') : '';

  /* Подстановка иконок: <img data-hc-icon="arrow-back"> -> HB + icon-arrow-back.svg */
  function apply(root) {
    var list = (root || document).querySelectorAll('img[data-hc-icon]');
    for (var i = 0; i < list.length; i++) {
      var img = list[i];
      if (img.getAttribute('src')) continue;
      img.src = HB + 'icon-' + img.getAttribute('data-hc-icon') + '.svg';
    }
  }

  /* Переключатели частей: set(root, {arrow:false, ...}) -> data-hc-*="off" */
  function set(root, parts) {
    if (!root || !parts) return;
    for (var k in parts) {
      if (PARTS.indexOf(k) === -1) continue;
      if (parts[k]) root.removeAttribute('data-hc-' + k);
      else root.setAttribute('data-hc-' + k, 'off');
    }
  }

  window.HeaderContent = { apply: apply, set: set, parts: PARTS };

  function init() { apply(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
