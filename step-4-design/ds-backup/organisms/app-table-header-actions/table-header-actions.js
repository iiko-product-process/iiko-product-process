/* table-header-actions - «полоса над таблицей» (шапка таблицы) - организм дизайн-системы.
   Страницы подключают его как ../Design-System/organisms/app-table-header-actions/table-header-actions.css + .js.
   Скрипт делает ровно две вещи:
     1) подставляет иконки <img data-tha-icon="..."> из папки организма: база считается
        по адресу самого скрипта, поэтому разметка работает с любой страницы и при переносе
        папки (тот же приём, что у app-header и header-content). Иконки - точные SVG из Figma
        (20px; цвет #616161 = Icon/Primary);
     2) переключает части блока, как свойства компонента в Figma:
        TableHeaderActions.set(root, { title:false, toggle:false, actions:false })
        ставит на корень .tha атрибуты data-tha-*="off" (true - атрибут снимается).
        Нет атрибута = часть показана (дефолт - всё включено). Разделитель в слоте
        «После заголовка» в PARTS не входит - он автоматический (правило в css):
        без заголовка или без тумблера исчезает сам.
   Больше скрипт ничего не делает: клики (тумблер, кнопки действий) - дело страницы,
   обработчики вешает она сама. */
(function () {
  'use strict';

  if (window.TableHeaderActions) return;   /* повторное подключение - не дублируем */

  var PARTS = ['title', 'toggle', 'actions'];

  /* База ассетов - по адресу самого скрипта: работает с любой страницы */
  var cs = document.currentScript;
  if (!cs) {
    var ss = document.getElementsByTagName('script');
    for (var i = ss.length - 1; i >= 0; i--) {
      if (/table-header-actions\.js/.test(ss[i].src || '')) { cs = ss[i]; break; }
    }
  }
  var TB = (cs && cs.src) ? cs.src.replace(/table-header-actions\.js.*$/, '') : '';

  /* Подстановка иконок: <img data-tha-icon="add"> -> TB + icon-add.svg */
  function apply(root) {
    var list = (root || document).querySelectorAll('img[data-tha-icon]');
    for (var i = 0; i < list.length; i++) {
      var img = list[i];
      if (img.getAttribute('src')) continue;
      img.src = TB + 'icon-' + img.getAttribute('data-tha-icon') + '.svg';
    }
  }

  /* Переключатели частей: set(root, {title:false, ...}) -> data-tha-*="off" */
  function set(root, parts) {
    if (!root || !parts) return;
    for (var k in parts) {
      if (PARTS.indexOf(k) === -1) continue;
      if (parts[k]) root.removeAttribute('data-tha-' + k);
      else root.setAttribute('data-tha-' + k, 'off');
    }
  }

  window.TableHeaderActions = { apply: apply, set: set, parts: PARTS };

  function init() { apply(document); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
