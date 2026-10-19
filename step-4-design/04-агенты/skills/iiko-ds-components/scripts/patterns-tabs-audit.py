#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit of the «Примерные паттерны поведения» block on the iiko DS recommendation pages.

(Текст и вывод — по-русски: так же, как остальные скрипты в `_audit/rec/checks/`.)

Что делает:
  1) без ключей — читает `_audit/rec/data/*.json` и печатает таблицу: паттернов /
     с примером / с подписью к примеру / пропущено `src`; в конце — итог по счётчикам;
  2) `--chrome` — тем же приёмом, что скрипты в `_audit/rec/checks/` (обёртка с
     `<iframe>` + `chrome --headless=new --dump-dom`), открывает страницы и печатает:
     табов / панелей / примеров, активный таб, влезает ли ряд табов в карточку
     (`bar.scrollWidth <= width`) и как ведут себя стрелки листания (`.pat__arrow--left`
     / `--right`: при переполнении видны, когда табы влезают — скрыты; у края
     соответствующая недоступна). Переполнение ряда само по себе НЕ дефект: ряд листают
     стрелками (владелец запретил полосу прокрутки, 2026-09-13);
  4) `--arrow-click` вместе с `--chrome` — жмёт стрелку вправо и проверяет, что ряд
     действительно сдвинулся (`scrollLeft` до/после), а у конца правая стрелка гаснет;
  3) `--click <i>` вместе с `--chrome` — кликает таб i и проверяет, что видна ровно
     одна панель, и что именно его (иначе переключатель табов сломан — а в разметке
     неактивные панели `hidden`, поэтому скриншот первого таба ничего не доказывает).

Запуск (сервер `python serve.py 8899` из корня DS должен быть поднят; Chrome — обычный):
    python patterns-tabs-audit.py                       # только данные
    python patterns-tabs-audit.py button --chrome
    python patterns-tabs-audit.py button button-icon --chrome --click 5

Страницы: `http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/<slug>.html`.
"""
import argparse
import glob
import html as htmlmod
import json
import os
import re
import subprocess
import sys

DS = os.environ.get("DS_ROOT", r"C:\Users\asukharev\GitHub\DS")
REC = os.path.join(DS, "_audit", "rec")
DATA = os.path.join(REC, "data")
CHECKS = os.path.join(REC, "checks")
URL = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/%s.html"
CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

# Название карточки — по слову «паттерны», чтобы не зависеть от точной формулировки заголовка.
PROBE = """<!doctype html><meta charset="utf-8"><body><pre id="out"></pre>
<iframe id="f" src="/iiko-ds-mobile/prototypes/recommendations/%(slug)s.html" width="1600" height="6000" style="border:0"></iframe>
<script>
const f=document.getElementById('f'), out=document.getElementById('out');
f.onload=()=>setTimeout(()=>{
  const d=f.contentDocument, N="\\u043f\\u0430\\u0442\\u0442\\u0435\\u0440\\u043d\\u044b";
  const c=[...d.querySelectorAll('.card')].find(x=>x.querySelector('h2')&&x.querySelector('h2').textContent.includes(N));
  if(!c){out.textContent=JSON.stringify({error:'нет карточки паттернов'});return;}
  const bar=c.querySelector('.pat__tabs');
  const pbar=c.querySelector('.pat__bar');
  const aL=pbar?pbar.querySelector('.pat__arrow--left'):null;
  const aR=pbar?pbar.querySelector('.pat__arrow--right'):null;
  const tabs=[...c.querySelectorAll('.pat__tabs .ds-tab')];
  const panels=[...c.querySelectorAll('.pat__panel')];
  const k=%(click)d;
  if(k===-2&&aR&&bar){
    const before=Math.round(bar.scrollLeft);
    aR.click();
    setTimeout(()=>{out.textContent=JSON.stringify({arrowClick:true,before:before,
      after:Math.round(bar.scrollLeft),leftDisabled:aL?aR.disabled&&!aL.disabled:null,
      rightDisabled:aR.disabled});},400);
    return;
  }
  if(k>=0&&tabs[k]) tabs[k].click();
  const vis=panels.filter(p=>!p.hidden);
  out.textContent=JSON.stringify({
    tabs:tabs.length, panels:panels.length,
    examples:c.querySelectorAll('.pat__panel .pat__ex').length,
    captions:c.querySelectorAll('.pat__panel .pat__ex-note').length,
    rowW:Math.round((bar||{scrollWidth:0}).scrollWidth),
    cardW:Math.round((bar||{getBoundingClientRect:()=>({width:0})}).getBoundingClientRect().width),
    fits:bar ? bar.scrollWidth<=Math.ceil(bar.getBoundingClientRect().width) : null,
    arrows:!!(aL&&aR),
    arrowsHidden:(aL&&aR)?[aL.hidden,aR.hidden]:null,
    arrowsDisabled:(aL&&aR)?[aL.disabled,aR.disabled]:null,
    scrollLeft:Math.round((bar||{scrollLeft:0}).scrollLeft),
    active:tabs.filter(t=>t.classList.contains('ds-tab--active')).map(t=>t.textContent.trim()),
    visible:vis.map(p=>p.getAttribute('data-pat-panel')),
    visibleWithExample:vis.filter(p=>p.querySelector('.pat__ex')).length});
},500);
</script></body>"""


def slugs_from_args(values):
    if values:
        return values
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(DATA, "*.json")))


def data_report(slugs):
    """Таблица по данным: паттерны, примеры, подписи, пропущенный `src`."""
    rows, totals = [], [0, 0, 0, 0]
    for slug in slugs:
        path = os.path.join(DATA, slug + ".json")
        if not os.path.exists(path):
            print("  ! нет файла данных: %s" % path)
            continue
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        pats = d.get("patterns_ru") or []
        ex = sum(1 for p in pats if p.get("example_html"))
        note = sum(1 for p in pats if p.get("example_html") and p.get("example_ru"))
        nosrc = sum(1 for p in pats if not p.get("src"))
        rows.append((slug, len(pats), ex, note, nosrc))
        totals[0] += len(pats)
        totals[1] += ex
        totals[2] += note
        totals[3] += nosrc
    width = max([len(r[0]) for r in rows] or [6])
    print("%-*s  паттернов  с примером  с подписью  без src" % (width, "компонент"))
    for slug, n, ex, note, nosrc in rows:
        flag = "" if (n and ex == n and note == n and not nosrc) else "   ← не готово"
        print("%-*s  %8d  %10d  %10d  %7d%s" % (width, slug, n, ex, note, nosrc, flag))
    print("итого: компонентов %d · паттернов %d · с примером %d · с подписью %d · без src %d"
          % (len(rows), totals[0], totals[1], totals[2], totals[3]))
    return rows


def chrome_path():
    for p in CHROME:
        if os.path.exists(p):
            return p
    print("Chrome не найден — укажи путь в CHROME")
    sys.exit(2)


def chrome_probe(slug, click=-1):
    """Открывает страницу в headless Chrome и возвращает разбор блока табов."""
    os.makedirs(CHECKS, exist_ok=True)
    wrapper = os.path.join(CHECKS, "_pat-audit.html")
    profile = os.path.join(os.environ.get("LOCALAPPDATA", "."), "Temp", "udd_pat_audit")
    try:
        with open(wrapper, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(PROBE % {"slug": slug, "click": click})
        cmd = [chrome_path(), "--headless=new", "--disable-gpu", "--no-sandbox",
               "--user-data-dir=" + profile, "--virtual-time-budget=9000", "--dump-dom",
               "http://127.0.0.1:8899/_audit/rec/checks/_pat-audit.html"]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=180).stdout
        m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
        if not m:
            return {"error": "обёртка не отдала результат (сервер 8899 поднят?) :: " + out[-200:]}
        return json.loads(htmlmod.unescape(m.group(1)))
    except Exception as exc:  # noqa: BLE001 — печатаем как есть, это диагностика
        return {"error": "%s: %s" % (type(exc).__name__, exc)}
    finally:
        if os.path.exists(wrapper):
            os.remove(wrapper)


def main():
    ap = argparse.ArgumentParser(description="Аудит блока «Примерные паттерны поведения»")
    ap.add_argument("slugs", nargs="*", help="слаги; по умолчанию — все из data/")
    ap.add_argument("--chrome", action="store_true", help="открыть страницы в headless Chrome")
    ap.add_argument("--click", type=int, default=-1, help="индекс таба для клика (вместе с --chrome)")
    ap.add_argument("--arrow-click", action="store_true",
                    help="нажать стрелку вправо и проверить, что ряд табов сдвинулся")
    args = ap.parse_args()
    click = -2 if args.arrow_click else args.click
    slugs = slugs_from_args(args.slugs)
    rows = data_report(slugs)
    if not args.chrome:
        return 0 if all(n and ex == n and note == n and not nosrc for _, n, ex, note, nosrc in rows) else 1
    print("\n--- браузер ---")
    bad = 0
    for slug in slugs:
        r = chrome_probe(slug, click)
        if r.get("arrowClick"):
            moved = r["after"] != r["before"]
            print("%-16s стрелка вправо: %d → %d%s" % (slug, r["before"], r["after"],
                  "" if moved else "  ← ряд не сдвинулся, стрелка мертва"))
            if not moved:
                bad += 1
            continue
        if r.get("error"):
            print("%-16s ошибка: %s" % (slug, r["error"]))
            bad += 1
            continue
        problems = []
        if r["tabs"] != r["panels"]:
            problems.append("табов %d, панелей %d" % (r["tabs"], r["panels"]))
        if r["examples"] != r["panels"]:
            problems.append("примеров %d из %d" % (r["examples"], r["panels"]))
        # Переполнение ряда — не дефект: ряд листают стрелками. Дефект — стрелок нет
        # или они показаны/скрыты не по делу (владелец: «Скролл у табов не нужен.
        # Сделай стрелки туда сюда», 2026-09-13).
        if r.get("arrows") and r["fits"] is True and r["arrowsHidden"] != [True, True]:
            problems.append("табы влезают, а стрелки видны")
        if r.get("arrows") and r["fits"] is False and r["arrowsHidden"] != [False, False]:
            problems.append("табы не влезают, а стрелок не видно: %d > %d" % (r["rowW"], r["cardW"]))
        if r.get("arrows") and r["arrowsDisabled"] and r["scrollLeft"] == 0 and not r["arrowsDisabled"][0]:
            problems.append("ряд в начале, а левая стрелка активна")
        if len(r["active"]) != 1:
            problems.append("активных табов %d" % len(r["active"]))
        if len(r["visible"]) != 1:
            problems.append("видимых панелей %d" % len(r["visible"]))
        if args.click >= 0 and r["visible"] and r["visible"][0] != "pat-%s-%d" % (slug, args.click):
            problems.append("после клика видна панель %s" % r["visible"][0])
        arrows = ((" · стрелки скрыты" if r.get("arrowsHidden") == [True, True] else " · стрелки видны")
                  if r.get("arrows") else " · стрелок нет")
        print("%-16s табов %d · панелей %d · примеров %d · ряд %d/%d%s%s%s"
              % (slug, r["tabs"], r["panels"], r["examples"], r["rowW"], r["cardW"],
                 " · активен «%s»" % (r["active"][0] if r["active"] else "—"), arrows,
                 "  ← " + "; ".join(problems) if problems else ""))
        bad += 1 if problems else 0
    print("\nпроблемных страниц: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
