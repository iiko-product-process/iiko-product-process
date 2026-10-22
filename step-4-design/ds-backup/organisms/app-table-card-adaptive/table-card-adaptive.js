/* table-card-adaptive — универсальная карточка таблицы (адаптив) — организм ДС.
   Страницы подключают его как ../Design-System/organisms/app-table-card-adaptive/table-card-adaptive.css + .js.
   Скрипт делает ровно две вещи:
     1) подставляет иконки <img data-tc-icon="..."> из папки организма: база считается
        по адресу самого скрипта, поэтому разметка работает с любой страницы и при
        переносе папки (тот же приём, что у app-header, header-content, page-footer и
        table-header-actions). Иконки — точные SVG из Figma (файл иконок ДС), цвет
        зашит в файле (#616161, Icon/Primary);
     2) переключает части карточки, как части компонента:
        TableCard.set(root, { check:false, kebab:false, status:false, icons:false, dates:false,
        actions:false }) ставит на корень .tc атрибуты data-tc-<часть>="off" (true — атрибут снимается).
        Нет атрибута — часть показана (дефолт).
   Больше скрипт ничего не делает: клики (чекбокс, кебаб, кнопки действий) — дело
   страницы, обработчики вешает она сама. */
(function () {
  'use strict';

  if (window.TableCard) return;   /* повторное подключение - не дублируем */

  var PARTS = ['check', 'kebab', 'status', 'icons', 'dates', 'actions'];

  /* База ассетов - по адресу самого скрипта: работает с любой страницы */
  var cs = document.currentScript;
  if (!cs) {
    var ss = document.getElementsByTagName('script');
    for (var i = ss.length - 1; i >= 0; i--) {
      if (/table-card-adaptive\.js/.test(ss[i].src || '')) { cs = ss[i]; break; }
    }
  }
  var TB = (cs && cs.src) ? cs.src.replace(/table-card-adaptive\.js.*$/, '') : '';

  /* Подстановка иконок: <img data-tc-icon="more-vert"> -> TB + icon-more-vert.svg */
  function apply(root) {
    var list = (root || document).querySelectorAll('img[data-tc-icon]');
    for (var i = 0; i < list.length; i++) {
      var img = list[i];
      if (img.getAttribute('src')) continue;
      img.src = TB + 'icon-' + img.getAttribute('data-tc-icon') + '.svg';
    }
  }

  /* Переключатель частей: set(root, {kebab:false}) -> data-tc-kebab="off" */
  function set(root, parts) {
    if (!root || !parts) return;
    for (var k in parts) {
      if (PARTS.indexOf(k) === -1) continue;
      if (parts[k]) root.removeAttribute('data-tc-' + k);
      else root.setAttribute('data-tc-' + k, 'off');
    }
  }

  window.TableCard = { apply: apply, set: set, parts: PARTS };

  function init() { apply(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
