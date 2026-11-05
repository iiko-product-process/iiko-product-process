/* ds-sizes-toggle.js — обвязка ревью: переключатель «Компоненты: Mobile / Desktop».
   Зачем: сравнить одну и ту же страницу-кадр с мобильными размерами ДС (рекомендации Material,
   кажутся крупными) и с десктопными — при том же узком кадре, лейауте и поведениях.

   Как работает: мобильные размеры живут ТОЛЬКО в мобильном слое ДС —
   components-mobile/modes.css (токены) + components-mobile/components/index.css (значения числом).
   Выключаем эти два <link> (link.disabled) — компоненты возвращаются к десктопным значениям
   из tokens.css и components-web/components/*; лейаут страницы (data-mode="mobile") и поведения
   (фильтр-шторка и т.п.) не трогаются.

   Где видно: НАД ЭКРАНОМ по центру кадра — две строки (абсолютом внутри .panel, left:50%):
   1) «Посмотреть с десктопными размерами» — рабочий переключатель (в десктопном состоянии
      текст «Вернуть мобильные размеры», подчёркнут);
   2) «Дизайнерские размеры iiko» — ЗАГЛУШКА на будущее (серая, неактивная): третий набор
      размеров (в разработке).
   В тач-режиме кадр получает запас сверху (+60px, обвязка ревью); строки — только в мобильном/
   планшетном режиме (body[data-touch], как в touch-mode.js).
   ?sizes=desktop — стартовое состояние (невидимый параметр для скриншотов).
   По умолчанию — mobile (как сейчас). */
(function () {
  var wantDesktop = /[?&]sizes=desktop\b/.test(location.search);
  var btn = null, panel = null, lines = null;
  var TOP_SPACE = 60;   /* запас над кадром под две строки; место съедается только в тач-режиме */

  function mobileLinks() {
    var out = [], links = document.querySelectorAll('link[rel="stylesheet"]');
    for (var i = 0; i < links.length; i++) {
      if ((links[i].getAttribute('href') || '').indexOf('components-mobile/') !== -1) out.push(links[i]);
    }
    return out;
  }

  function apply() {
    var links = mobileLinks();
    for (var i = 0; i < links.length; i++) links[i].disabled = wantDesktop;
    if (!btn) return;
    btn.textContent = wantDesktop ? 'Вернуть мобильные размеры' : 'Посмотреть с десктопными размерами';
    btn.className = wantDesktop ? 'is-active' : '';
    btn.setAttribute('aria-pressed', wantDesktop ? 'true' : 'false');
    btn.title = wantDesktop
      ? 'Сейчас показаны ДЕСКТОПНЫЕ размеры компонентов. Клик — вернуть мобильные.'
      : 'Показать все компоненты в десктопных размерах (мобильный слой ДС выключен); кадр и лейаут остаются мобильными.';
  }

  function sync() {
    if (!btn || !panel) return;
    var bar = document.getElementById('modes-bar');
    var on = document.body.getAttribute('data-touch') === '1' && !!bar && !bar.hidden;
    if (lines) lines.hidden = !on;                      /* строки — только для планшета/телефона */
    panel.style.marginTop = on ? TOP_SPACE + 'px' : ''; /* место под строки над кадром */
    apply();
  }

  function init() {
    panel = document.getElementById('panel');
    if (!panel) return;
    var st = document.createElement('style');
    st.textContent =
      '#ds-sizes-lines{position:absolute;left:50%;top:-78px;transform:translateX(-50%);z-index:2;' +
      'display:flex;flex-direction:column;align-items:center;gap:8px}' +
      '#ds-sizes-lines button{border:0;background:none;padding:0;white-space:nowrap;' +
      'font-family:inherit;font-size:14px;line-height:20px;font-weight:500}' +
      '#ds-sizes-btn{cursor:pointer;color:var(--ds-color-text-accent,#448aff)}' +
      '#ds-sizes-btn:hover,#ds-sizes-btn.is-active{text-decoration:underline}' +
      '#ds-sizes-btn:focus-visible{outline:2px solid var(--ds-color-brand-accent-default,#448aff);outline-offset:2px;border-radius:4px}' +
      /* ЗАГЛУШКА на будущее: третий набор (iiko-дизайнерские размеры) — включим, когда он появится */
      '#ds-sizes-iiko-btn{color:#9e9e9e;cursor:default}';
    document.head.appendChild(st);
    lines = document.createElement('div');
    lines.id = 'ds-sizes-lines';
    btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'ds-sizes-btn';
    btn.addEventListener('click', function () { wantDesktop = !wantDesktop; apply(); });
    var iiko = document.createElement('button');
    iiko.type = 'button';
    iiko.id = 'ds-sizes-iiko-btn';
    iiko.disabled = true;
    iiko.textContent = 'Дизайнерские размеры iiko';
    iiko.title = 'Появится позже: третий набор размеров — значения из таблицы «Компоненты: Desktop → Mobile»';
    lines.appendChild(btn);
    lines.appendChild(iiko);
    panel.appendChild(lines);   /* внутри кадра, абсолютом — две строки по центру над «экраном» */
    if (window.MutationObserver) {
      new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ['data-touch'] });
    }
    window.addEventListener('resize', sync);
    if (window.ResizeObserver) {   /* пресеты/ручка меняют ширину кадра — держим положение и запас */
      var ro = new ResizeObserver(sync);
      ro.observe(panel);
      window.__dsSizesToggleRO = ro;   /* держим ссылку — ловушка GC */
    }
    sync();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
