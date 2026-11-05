/* page-footer - подвал страницы (и таблицы) - организм дизайн-системы.
   Страницы подключают его как ../Design-System/organisms/app-page-footer/page-footer.css + .js.
   Скрипт делает ровно две вещи:
     1) подставляет иконки <img data-pf-icon="..."> из папки организма: база считается
        по адресу самого скрипта, поэтому разметка работает с любой страницы и при
        переносе папки (тот же приём, что у app-header, header-content и
        table-header-actions). Иконки - точные SVG из Figma (info, 24-сетка; цвет
        зашит: серая #616161 для подписи, красная #FF5252 для подсказки);
     2) переключает части блока, как свойства компонента:
        PageFooter.set(root, { content:false, actions:false }) ставит на корень .pf
        атрибуты data-pf-*="off" (true - атрибут снимается). Нет атрибута = часть
        показана (дефолт). Разделитель - всегда (как в компоненте), переключателя нет.
   Больше скрипт ничего не делает: клики (кнопки действий) - дело страницы,
   обработчики вешает она сама. */
(function () {
  'use strict';

  if (window.PageFooter) return;   /* повторное подключение - не дублируем */

  var PARTS = ['content', 'actions'];

  /* База ассетов - по адресу самого скрипта: работает с любой страницы */
  var cs = document.currentScript;
  if (!cs) {
    var ss = document.getElementsByTagName('script');
    for (var i = ss.length - 1; i >= 0; i--) {
      if (/page-footer\.js/.test(ss[i].src || '')) { cs = ss[i]; break; }
    }
  }
  var PB = (cs && cs.src) ? cs.src.replace(/page-footer\.js.*$/, '') : '';

  /* Подстановка иконок: <img data-pf-icon="info"> -> PB + icon-info.svg */
  function apply(root) {
    var list = (root || document).querySelectorAll('img[data-pf-icon]');
    for (var i = 0; i < list.length; i++) {
      var img = list[i];
      if (img.getAttribute('src')) continue;
      img.src = PB + 'icon-' + img.getAttribute('data-pf-icon') + '.svg';
    }
  }

  /* Переключатель разделителя: set(root, {divider:false}) -> data-pf-divider="off" */
  function set(root, parts) {
    if (!root || !parts) return;
    for (var k in parts) {
      if (PARTS.indexOf(k) === -1) continue;
      if (parts[k]) root.removeAttribute('data-pf-' + k);
      else root.setAttribute('data-pf-' + k, 'off');
    }
  }

  window.PageFooter = { apply: apply, set: set, parts: PARTS };

  function init() { apply(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
