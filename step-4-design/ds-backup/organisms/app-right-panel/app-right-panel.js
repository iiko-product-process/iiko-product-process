/* ============================================================
   app-right-panel — поведение правой панели (организм ДС). Версия v1.
   Разметка страницы (декларативно, контент — свой):
     <aside class="app-rp" data-rp="ID" hidden aria-label="…">
       <div class="ds-card ds-card--shadow app-rp__frame">
         <div class="ds-card__header">
           <p class="ds-card__title app-rp__title">Заголовок</p>
           <span class="app-rp__close" role="button" tabindex="0" aria-label="Закрыть">…крестик…</span>
         </div>
         <div class="ds-card__content">…контент…</div>
         <div class="ds-card__footer ds-card__footer--right" hidden|…>…действия…</div>
       </div>
     </aside>
     <div class="app-rp-scrim ds-backdrop" data-rp-scrim="ID" hidden></div>
     триггер открытия: любой элемент [data-rp-open="ID"]
   Закрытие: крестик .app-rp__close, клик по скриму, Esc. Открыта одна панель за раз.
   API: window.AppRightPanel.open(id) / close(id) / closeAll();
   события на панели: app-rp-open / app-rp-close (bubbles, detail.id).
   ============================================================ */
(function (global) {
  'use strict';

  var VERSION = 'v1';
  var openId = null;

  function panelFor(id) { return document.querySelector('.app-rp[data-rp="' + id + '"]'); }
  function scrimFor(id) { return document.querySelector('.app-rp-scrim[data-rp-scrim="' + id + '"]'); }

  function open(id) {
    var panel = panelFor(id);
    if (!panel || !panel.hidden && openId === id) return;
    if (openId && openId !== id) close(openId);
    panel.hidden = false;
    var sc = scrimFor(id);
    if (sc) sc.hidden = false;
    openId = id;
    panel.dispatchEvent(new CustomEvent('app-rp-open', { bubbles: true, detail: { id: id } }));
  }

  function close(id) {
    var panel = panelFor(id);
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    var sc = scrimFor(id);
    if (sc) sc.hidden = true;
    if (openId === id) openId = null;
    panel.dispatchEvent(new CustomEvent('app-rp-close', { bubbles: true, detail: { id: id } }));
  }

  function closeAll() {
    Array.prototype.slice.call(document.querySelectorAll('.app-rp[data-rp]')).forEach(function (p) {
      close(p.getAttribute('data-rp'));
    });
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var opener = t.closest('[data-rp-open]');
    if (opener) { open(opener.getAttribute('data-rp-open')); return; }
    var closer = t.closest('.app-rp__close');
    if (closer) { var p = closer.closest('.app-rp'); if (p) close(p.getAttribute('data-rp')); return; }
    var sc = t.closest('.app-rp-scrim');
    if (sc) { close(sc.getAttribute('data-rp-scrim')); }
  });

  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (e.key === 'Escape') { closeAll(); return; }
    if ((e.key === 'Enter' || e.key === ' ') && t && t.closest && t.closest('.app-rp__close')) {
      e.preventDefault();
      var p = t.closest('.app-rp');
      if (p) close(p.getAttribute('data-rp'));
    }
  });

  global.AppRightPanel = { version: VERSION, open: open, close: close, closeAll: closeAll };
})(window);
