#!/usr/bin/env bash
# probe-page.sh — замер HTML-прототипа (и любой локальной страницы) headless Chrome'ом.
#
# Зачем. В страницах-прототипах разметку рисует JS, поэтому «посмотреть глазами»
# не отвечает на вопросы «влезло ли число в кнопку 56 px», «какой цвет у полосы», «сработало ли
# нажатие». Владелец ждёт в отчёте числа, а не «стало лучше». Скрипт вклеивает JS-пробу в копию
# страницы, гонит её в headless Chrome и печатает то, что проба положила в <pre id="probe">.
#
# Использование:
#   scripts/probe-page.sh <page.html> <probe.js> [--state state.js] [--shot out.png]
#                         [--budget 9000] [--width 1700] [--height 1100]
#
#   <probe.js> — ТЕЛО пробы (без обёртки): выполняется по load + 500 мс; строки отчёта класть
#                в массив o (o.push('ключ: значение')). Обёртка, ошибки JS и переполнение
#                страницы печатаются скриптом автоматически — их в probe.js писать не нужно.
#   --state    — файл с JS, который подставляется ПЕРЕД первым paint():
#                timeOn=true; elapsedMin=6; pressed={warm:['cold']};
#                Так и замер, и кадр показывают нужное состояние без кликов — клик из скрипта
#                иногда не успевает к кадру, а состояние перед paint() не «отстаёт».
#                Видимость вкладки ставить там же, из JS, а не кликом:
#                document.querySelector('[data-vpanel="1"]').classList.remove('is-on');
#                document.querySelector('[data-vpanel="3"]').classList.add('is-on');
#   --shot     — дополнительно сохранить PNG подготовленной страницы. Путь — НАТИВНЫЙ
#                (C:/Users/…/имя.png) и только в папку макетов задачи: на Рабочий стол
#                скриншоты не выгружать (владелец считает это мусором).
#
# Грабли, из-за которых это скрипт, а не строчка в терминале:
#   * JS держать в ОТДЕЛЬНОМ файле — в bash-heredoc экранирование ломает код;
#   * у каждого прогона свой --user-data-dir, иначе Chrome цепляется за прошлый профиль;
#   * --virtual-time-budget 9–14 с: ждём таймеры и шрифты (Roboto, Material Icons тянутся из сети);
#   * Chrome нативный, MSYS-путь /c/... ему не годится — URL считаем через pathlib.as_uri()
#     (получается file:///C:/…);
#   * getComputedStyle спрашивать через дефис ('animation-name'), иначе вернётся пустая строка.
set -euo pipefail

CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
if [ ! -x "$CHROME" ]; then
  CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || true)"
fi
[ -n "$CHROME" ] && [ -x "$CHROME" ] || { echo "не найден Chrome: задай CHROME=/путь/к/chrome" >&2; exit 2; }

PY="$(command -v python || command -v python3 || true)"
[ -n "$PY" ] || { echo "нужен python (вклейка пробы и разбор вывода)" >&2; exit 2; }

PAGE="${1:?использование: probe-page.sh <page.html> <probe.js> [--state state.js] [--shot out.png]}"
PROBE="${2:?нужен файл пробы (probe.js)}"
shift 2

STATE=""; SHOT=""; BUDGET=9000; W=1700; H=1100
while [ $# -gt 0 ]; do
  case "$1" in
    --state)  STATE="${2:?--state ждёт файл}"; shift 2 ;;
    --shot)   SHOT="${2:?--shot ждёт путь к png}"; shift 2 ;;
    --budget) BUDGET="${2:?}"; shift 2 ;;
    --width)  W="${2:?}"; shift 2 ;;
    --height) H="${2:?}"; shift 2 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
done
[ -f "$PAGE" ]  || { echo "нет файла страницы: $PAGE" >&2; exit 2; }
[ -f "$PROBE" ] || { echo "нет файла пробы: $PROBE" >&2; exit 2; }
if [ -n "$STATE" ] && [ ! -f "$STATE" ]; then echo "нет файла состояния: $STATE" >&2; exit 2; fi

TMP="${TMPDIR:-${LOCALAPPDATA:-/tmp}}"; TMP="${TMP%/}/Temp"; mkdir -p "$TMP"
WORK="$(mktemp -d "$TMP/probe-XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# 1. копия страницы: состояние перед первым paint() + проба перед </body>; печатает file:// URL
URI="$("$PY" - "$PAGE" "$PROBE" "$STATE" "$WORK/page.html" <<'PYEOF'
import pathlib, sys
page, probe_f, state_f, out = sys.argv[1:5]
s = pathlib.Path(page).read_text(encoding='utf-8')
if state_f:
    st = pathlib.Path(state_f).read_text(encoding='utf-8').strip()
    if '\npaint();' not in s:
        sys.stderr.write('предупреждение: не нашёл "\\npaint();" — состояние не подставлено\n')
    s = s.replace('\npaint();', '\n' + st + '\npaint();', 1)
body = pathlib.Path(probe_f).read_text(encoding='utf-8')
inject = (
  '<pre id="probe"></pre>\n<script>\n'
  'var probErr=[];window.addEventListener("error",function(e){probErr.push(e.message);});\n'
  'window.addEventListener("load",function(){setTimeout(function(){\n'
  'var o=[];try{\n' + body + '\n}catch(e){o.push("ОШИБКА ПРОБЫ: "+e.message);}\n'
  'o.push("ошибки JS: "+(probErr.length?probErr.join(" | "):"нет"));\n'
  'o.push("переполнение: "+Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)+" px");\n'
  'document.getElementById("probe").textContent="START\\n"+o.join("\\n")+"\\nEND";\n'
  '},500);});\n</script>\n')
s = s.replace('</body>', inject + '</body>', 1)
pathlib.Path(out).write_text(s, encoding='utf-8')
print(pathlib.Path(out).absolute().as_uri())
PYEOF
)"

# 2. прогон
mkdir -p "$WORK/profile"
"$CHROME" --headless=new --disable-gpu --no-first-run --allow-file-access-from-files \
  --user-data-dir="$WORK/profile" --virtual-time-budget="$BUDGET" \
  --window-size="$W,$H" --dump-dom "$URI" > "$WORK/dom.html" 2>/dev/null || true

# 3. вывод пробы
"$PY" - "$WORK/dom.html" <<'PYEOF'
import pathlib, re, sys
s = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
m = re.search(r'<pre id="probe">(.*?)</pre>', s, re.S)
print(m.group(1).strip() if m else 'ПРОБА НЕ СРАБОТАЛА: <pre id="probe"> пуст — проверь синтаксис probe.js (node --check)')
PYEOF

# 4. кадр состояния (по желанию)
if [ -n "$SHOT" ]; then
  mkdir -p "$WORK/profile2"
  "$CHROME" --headless=new --disable-gpu --no-first-run --allow-file-access-from-files \
    --user-data-dir="$WORK/profile2" --virtual-time-budget="$BUDGET" \
    --window-size="$W,$H" --screenshot="$SHOT" "$URI" >/dev/null 2>&1 || true
  echo "скриншот: $SHOT"
fi
