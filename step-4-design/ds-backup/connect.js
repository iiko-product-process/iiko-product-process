/* connect.js — одна строка подключения дизайн-системы для страниц-прототипов.

   КАК ПОЛЬЗОВАТЬСЯ — вставить в <head> страницы одну строку:

       <script src="путь/до/DS/connect.js" defer></script>

   Скрипт работает от своего расположения, поэтому:
     • страница может лежать где угодно (главное — чтобы из неё был виден путь к DS);
     • путь можно указывать и абсолютным: <script src="file:///C:/.../DS/connect.js" defer></script>

   ЧТО ПОДТЯГИВАЕТСЯ САМО:
     1) стили ДС: components-web/font.css, tokens.css, styles.css, components/index.css, fixes.css;
     2) иконки Material Icons (обычные + Outlined);
     3) организмы: шапка app-header (с правой панелью app-right-panel — её шторка) и боковое меню app-sidenav (css + js);
     4) структура .panel > .frame — если её нет, создаётся, и содержимое страницы переносится внутрь
        (шапка и меню встают в неё автоматически).

   ФЛАГИ (атрибуты на том же теге script):
     data-no-header         — не подключать шапку;
     data-no-sidenav        — не подключать боковое меню;
     data-mobile            — добавить мобильный слой ДС (components-mobile);
     data-molecules="a,b"   — подключить молекулы из DS/molecules/<имя>/ (css + js).

   ЧТО ЗДЕСЬ МЕНЯТЬ: версии организмов (?v=) и список подключаемого — живут ТОЛЬКО здесь,
   страницам ничего дублировать не нужно. Обновили организм — подняли версию здесь — у всех
   страниц, подключённых через connect.js, сразу новая версия.

   Если страница уже подключает что-то вручную — повторно это не добавится (проверка дублей). */
(function () {
  'use strict';

  /* ── 1. База и флаги — по адресу самого скрипта ─────────────────────────── */
  var cs = document.currentScript;
  if (!cs) {
    var all = document.getElementsByTagName('script');
    for (var i = all.length - 1; i >= 0; i--) {
      if (/connect\.js/.test(all[i].src || '')) { cs = all[i]; break; }
    }
  }
  var BASE = (cs && cs.src) ? cs.src.replace(/connect\.js.*$/, '') : '';
  var FLAGS = {
    header:    !(cs && cs.hasAttribute('data-no-header')),
    sidenav:   !(cs && cs.hasAttribute('data-no-sidenav')),
    mobile:    !!(cs && cs.hasAttribute('data-mobile')),
    molecules: (cs && cs.getAttribute('data-molecules')) || ''
  };

  /* ── 2. Что подключаем ─────────────────────────────────────────────────── */
  var CSS = [
    'components-web/font.css',
    'components-web/tokens.css',
    'components-web/styles.css',
    'components-web/components/index.css',
    'components-web/components/Checkbox_DS/checkbox.css',
    'components-web/components/Checkbox_DS/checkbox-icons.css',
    /* Radio: в index.css файлы Radio-Button_DS не подключены (пробел выгрузки ДС №108) — тянем явно, как checkbox */
    'components-web/components/Radio-Button_DS/radio.css',
    'components-web/components/Radio-Button_DS/radio-icons.css',
    'components-web/fixes.css'
  ];
  if (FLAGS.mobile) CSS.push('components-mobile/modes.css', 'components-mobile/components/index.css');
  if (FLAGS.header) CSS.push('organisms/app-right-panel/app-right-panel.css?v=2', 'organisms/app-header/app-header.css?v=21');
  if (FLAGS.sidenav) CSS.push('organisms/app-sidenav/app-sidenav.css?v=15');

  var JS = [];
  if (FLAGS.header) JS.push('organisms/app-right-panel/app-right-panel.js?v=1', 'organisms/app-header/app-header.js?v=20');
  if (FLAGS.sidenav) JS.push('organisms/app-sidenav/app-sidenav.js?v=13');

  var MOL = [];
  if (FLAGS.molecules) {
    var names = FLAGS.molecules.split(',');
    for (var m = 0; m < names.length; m++) {
      var n = names[m].replace(/^\s+|\s+$/g, '');
      if (!n) continue;
      CSS.push('molecules/' + n + '/' + n + '.css');
      JS.push('molecules/' + n + '/' + n + '.js');
      MOL.push(n);
    }
  }

  /* ── 3. Утилиты (с проверкой дублей) ───────────────────────────────────── */
  function hasLink(marker) {
    return !!document.querySelector('link[href*="' + marker + '"]');
  }
  function hasScript(marker) {
    var ss = document.getElementsByTagName('script');
    for (var i = 0; i < ss.length; i++) {
      if ((ss[i].getAttribute('src') || '').indexOf(marker) >= 0) return true;
    }
    return false;
  }
  function addCss(href) {
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = /^(https?:)?\/\//.test(href) ? href : BASE + href;
    return l;
  }
  function addJs(src) {
    var s = document.createElement('script');
    s.src = BASE + src;
    s.async = false;   /* порядок гарантирован: панель → шапка → меню → молекулы */
    document.body.appendChild(s);
  }
  function hasIcons(outlined) {
    var ls = document.querySelectorAll('link[href]');
    for (var i = 0; i < ls.length; i++) {
      var h = ls[i].getAttribute('href') || '';
      var classic = h.indexOf('family=Material+Icons') >= 0 && h.indexOf('+Outlined') < 0;
      if (outlined ? h.indexOf('Material+Icons+Outlined') >= 0 : classic) return true;
    }
    return false;
  }

  /* ── 4. Стили — фрагментом в head ПЕРЕД первым style/link/script страницы ─ */
  var frag = document.createDocumentFragment();
  for (var c = 0; c < CSS.length; c++) {
    var marker = CSS[c].split('?')[0];
    if (!hasLink(marker)) frag.appendChild(addCss(CSS[c]));
  }
  if (!hasIcons(false)) frag.appendChild(addCss('https://fonts.googleapis.com/icon?family=Material+Icons'));
  if (!hasIcons(true)) frag.appendChild(addCss('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined'));

  var head = document.head || document.documentElement;
  var ref = null;
  for (var k = 0; k < head.children.length; k++) {
    var tag = head.children[k].tagName;
    if (tag === 'LINK' || tag === 'STYLE' || tag === 'SCRIPT') { ref = head.children[k]; break; }
  }
  head.insertBefore(frag, ref);   /* ref === null → в конец head */

  /* ── 5. Структура .panel > .frame (создаём, если её нет) ────────────────── */
  function ensureStructure() {
    var panel = document.getElementById('panel') || document.querySelector('.panel');
    var frame;
    if (panel && panel.querySelector('.frame')) return;
    if (panel) {
      frame = document.createElement('div');
      frame.className = 'frame';
      frame.id = 'frame';
      var ch = Array.prototype.slice.call(panel.children);
      for (var i = 0; i < ch.length; i++) {
        if (ch[i].tagName !== 'SCRIPT') frame.appendChild(ch[i]);
      }
      panel.appendChild(frame);
    } else {
      panel = document.createElement('div');
      panel.className = 'panel';
      panel.id = 'panel';
      panel.setAttribute('data-mode', 'desktop');
      frame = document.createElement('div');
      frame.className = 'frame';
      frame.id = 'frame';
      var kids = Array.prototype.slice.call(document.body.children);
      for (var j = 0; j < kids.length; j++) {
        if (kids[j].tagName !== 'SCRIPT') frame.appendChild(kids[j]);
      }
      panel.appendChild(frame);
      document.body.appendChild(panel);
    }
  }

  /* ── 6. Запуск ─────────────────────────────────────────────────────────── */
  function run() {
    ensureStructure();
    for (var i = 0; i < JS.length; i++) {
      var marker = JS[i].split('?')[0];
      if (!hasScript(marker)) addJs(JS[i]);
    }
    window.DSConnect = { base: BASE, flags: FLAGS, css: CSS, js: JS, molecules: MOL };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
