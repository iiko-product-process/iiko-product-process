#!/usr/bin/env bash
# collect-my-skills.sh — собрать наработки сотрудника по процессу + инвентарь всех скиллов.
#
# Два сигнала:
#   1) НАРАБОТКИ — новые и изменённые *процессные* скиллы (из канона или по шаблонам имени);
#      уходят содержимым в архив.
#   2) ИНВЕНТАРЬ — ВСЕ локальные скиллы, только метаданные (имя, версия, sha1, категория,
#      в каноне/нет). Содержимое чужих скиллов не отправляется никогда.
#
# Отправка: Telegram (sendDocument) или папка. Если наработок нет и инвентарь не изменился
# с прошлого запуска — скрипт молчит.
#
# usage:
#   collect-my-skills.sh [--home PATH] [--manifest FILE] [--author NAME]
#                        [--out DIR | --telegram] [--patterns FILE]
#                        [--dry-run] [--force]
#   env: TG_TOKEN, TG_CHAT, TG_THREAD, TG_PROXY, TG_API
#
# По умолчанию: --home $HERMES_HOME (или ~/.hermes), --out ~/skill-reports
# Манифест канона: TSV "name<TAB>sha1<TAB>version".
# Шаблоны процессных скиллов: файл со строками-подстроками (регистр не важен).
set -uo pipefail

HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
MANIFEST=""
AUTHOR="$(whoami 2>/dev/null || echo employee)"
OUT_DIR="$HOME/skill-reports"
MODE="dir"
DRY=0
FORCE=0
PATTERNS=""

while [ $# -gt 0 ]; do
  case "$1" in
    --home) HOME_DIR="${2:?}"; shift ;;
    --manifest) MANIFEST="${2:?}"; shift ;;
    --author) AUTHOR="${2:?}"; shift ;;
    --out) OUT_DIR="${2:?}"; MODE="dir"; shift ;;
    --telegram) MODE="telegram" ;;
    --patterns) PATTERNS="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    --force) FORCE=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

SKILLS="$HOME_DIR/skills"
[ -d "$SKILLS" ] || { echo "collect-my-skills: не найден каталог скиллов (искал $SKILLS)"; exit 1; }

STATE="$HOME_DIR/.skills-inbox-state"
DATE="$(date +%Y-%m-%d)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
PKG="$WORK/skills-$AUTHOR-$DATE"; mkdir -p "$PKG/skills"

# ---------- шаблоны процессных имён ----------
# по умолчанию — префиксы процесса; файл --patterns дополняет/заменяет список
DEFAULT_PATTERNS='^(iiko|pb|prd|spec|problem|hypothes|research|interview|job|market|competitor|benchmark|task|hermes|share|mirror|process|design|ds-|ux-|jira|pyrus|matomo|meeting|notes|skills-inbox|feature|jtbd|dogfood|live-prototype|prototype-)'
PAT_FILE="${PATTERNS:-$(dirname "$0")/../process-skill-patterns.txt}"
if [ -f "$PAT_FILE" ]; then
  PAT_RE="$(grep -v '^\s*#' "$PAT_FILE" | grep -v '^\s*$' | paste -sd'|' -)"
  [ -n "$PAT_RE" ] && PAT_RE="^($PAT_RE)"
else
  PAT_RE="$DEFAULT_PATTERNS"
fi

is_process() {
  local n="$1"
  [ -n "${CANON_SHA[$n]:-}" ] && return 0
  printf '%s' "$n" | grep -qiE "$PAT_RE"
}

# ---------- манифест канона ----------
declare -A CANON_SHA CANON_VER
if [ -n "$MANIFEST" ] && [ -f "$MANIFEST" ]; then
  while IFS=$'\t' read -r n s v; do
    [ -n "${n:-}" ] || continue
    CANON_SHA["$n"]="${s:-}"; CANON_VER["$n"]="${v:-}"
  done < "$MANIFEST"
fi

# ---------- скан ----------
items="$WORK/items.jsonl"; : > "$items"
total=0; p_new=0; p_changed=0; p_identical=0; p_attention=0; other=0

find "$SKILLS" -maxdepth 3 -name SKILL.md -type f 2>/dev/null | sort > "$WORK/list.txt"

while IFS= read -r f; do
  [ -n "$f" ] || continue
  dir="$(dirname "$f")"; name="$(basename "$dir")"
  docname="$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')"
  [ -n "$docname" ] && name="$docname"
  ver="$(sed -n 's/^version:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')"
  sha="$(sha1sum "$f" | cut -d' ' -f1)"
  rel="${dir#$SKILLS/}"; category="${rel%%/*}"; [ "$category" = "$rel" ] && category="—"
  total=$((total+1))

  in_canon=0; [ -n "${CANON_SHA[$name]:-}" ] && in_canon=1
  # в каноне сравнение по sha1 (dir-hash не нужен: манифест собран по SKILL.md)
  status="other"
  if [ "$in_canon" = 1 ]; then
    if [ "${CANON_SHA[$name]}" = "$sha" ]; then status="identical"; else status="changed"; fi
  elif is_process "$name"; then
    status="new"
  fi

  # секреты проверяем только у процессных: чужие не отправляем вообще
  secrets=""
  if [ "$status" != "other" ] && [ "$status" != "identical" ]; then
    while IFS= read -r hit; do
      [ -n "$hit" ] && secrets="$secrets$(basename "$hit");"
    done < <(grep -rIlE 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' "$dir" 2>/dev/null | head -5)
    [ -n "$secrets" ] && status="attention"
  fi

  case "$status" in
    new) p_new=$((p_new+1)) ;;
    changed) p_changed=$((p_changed+1)) ;;
    identical) p_identical=$((p_identical+1)) ;;
    attention) p_attention=$((p_attention+1)) ;;
    other) other=$((other+1)) ;;
  esac

  size=$(du -sk "$dir" 2>/dev/null | cut -f1)
  printf '{"name":"%s","version":"%s","sha1":"%s","status":"%s","in_canon":%s,"canon_version":"%s","category":"%s","size_kb":%s,"secrets":"%s","path":"%s","mtime":"%s"}\n' \
    "$name" "${ver:-}" "$sha" "$status" "$in_canon" "${CANON_VER[$name]:-}" "$category" "${size:-0}" "$secrets" \
    "$rel" "$(date -r "$f" +%Y-%m-%d 2>/dev/null || echo "")" >> "$items"

  # содержимое — только процессные и только отличные от канона
  if [ "$status" = "new" ] || [ "$status" = "changed" ] || [ "$status" = "attention" ]; then
    mkdir -p "$PKG/skills/$name"
    ( cd "$dir" && find . -type f -size -5120k -print0 2>/dev/null | while IFS= read -r -d '' x; do
        mkdir -p "$PKG/skills/$name/$(dirname "$x")"; cp "$x" "$PKG/skills/$name/$x"; done )
  fi
done < "$WORK/list.txt"

count_to_send=$((p_new + p_changed + p_attention))

# ---------- манифест запуска ----------
cat > "$PKG/manifest.json" <<EOF
{
  "author": "$AUTHOR",
  "date": "$DATE",
  "host": "$(hostname 2>/dev/null || echo unknown)",
  "canon_manifest": "${MANIFEST:-none}",
  "counts": {"total": $total, "new": $p_new, "changed": $p_changed, "identical": $p_identical, "attention": $p_attention, "third_party": $other}
}
EOF

# ---------- инвентарь (метаданные, без содержимого) ----------
python3 - "$items" "$PKG/inventory.json" "$AUTHOR" "$DATE" "$(hostname 2>/dev/null || echo unknown)" <<'PY'
import json, sys
src, dst, author, date, host = sys.argv[1:6]
items = [json.loads(l) for l in open(src, encoding='utf-8') if l.strip()]
seen = {}
for d in items:
    seen[d['name']] = d                      # одинаковые имена из разных категорий — последний
uniq = sorted(seen.values(), key=lambda d: d['name'])
out = {
    "author": author, "date": date, "host": host, "kind": "inventory",
    "summary": {
        "total": len(items),
        "unique": len(uniq),
        "in_canon": sum(1 for d in uniq if d['in_canon']),
        "changed": sum(1 for d in uniq if d['status'] == 'changed'),
        "new_process": sum(1 for d in uniq if d['status'] in ('new', 'attention')),
        "third_party": sum(1 for d in uniq if d['status'] == 'other'),
    },
    "skills": [{
        "name": d['name'], "version": d['version'], "sha1": d['sha1'],
        "status": d['status'], "in_canon": bool(d['in_canon']),
        "canon_version": d['canon_version'], "category": d['category'],
        "size_kb": d['size_kb'], "mtime": d['mtime'],
    } for d in uniq],
}
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"inventory: {len(uniq)} уникальных, в каноне {out['summary']['in_canon']}, "
      f"изменено {out['summary']['changed']}, новых процессных {out['summary']['new_process']}, "
      f"чужих {out['summary']['third_party']}")
PY

INV_SHA="$(sha1sum "$PKG/inventory.json" | cut -d' ' -f1)"
INV_SUMMARY="$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));s=d['summary'];print(f\"всего {s['unique']}, в каноне {s['in_canon']}, изменено {s['changed']}, новых {s['new_process']}, чужих {s['third_party']}\")" "$PKG/inventory.json")"

# ---------- состояние: молчим, если ничего не поменялось ----------
PREV_SHA=""; PREV_DATE=""
[ -f "$STATE" ] && { PREV_SHA="$(cut -d' ' -f1 "$STATE")"; PREV_DATE="$(cut -d' ' -f2 "$STATE")"; }

# молчим, если с прошлой отправки ничего не изменилось (инвентарь = статусы + sha всех скиллов).
# Неотправленные наработки при этом не теряются: они попадут в следующий архив, когда состав изменится,
# либо по запуску с --force.
if [ "$INV_SHA" = "$PREV_SHA" ] && [ "$FORCE" = 0 ]; then
  echo "collect-my-skills: нет изменений с прошлой отправки — ждут отправки $count_to_send, инвентарь не менялся ($INV_SUMMARY)"
  exit 0
fi

# ---------- отчёт ----------
{
  echo "# Наработки $AUTHOR, $DATE"
  echo
  echo "Локально скиллов: $total · в каноне: $p_identical идентичны, $p_changed изменены ·"
  echo "новых процессных: $p_new · требуют внимания: $p_attention · чужих (в инвентаре): $other"
  echo
  if [ "$count_to_send" -gt 0 ]; then
    echo "## Наработки в архиве"
    echo
    echo "| Скилл | Версия | Статус | Размер |"
    echo "|---|---|---|---|"
    python3 - "$items" <<'PY'
import json, sys
for line in open(sys.argv[1], encoding='utf-8'):
    d = json.loads(line)
    if d['status'] in ('identical', 'other'):
        continue
    print(f"| {d['name']} | {d['version'] or '—'} | {d['status']} | {d['size_kb']} КБ |")
PY
    echo
  else
    echo "## Наработок нет"
    echo
    echo "В архив попал только инвентарь: изменился состав или версии локальных скиллов."
    echo
  fi
  echo "## Инвентарь"
  echo
  echo "$INV_SUMMARY"
  echo
  echo "Файл: \`inventory.json\` (только метаданные, содержимое чужих скиллов не отправляется)."
  echo
  echo "## Зачем (заполни, если не сложно)"
  echo
  echo "- "
} > "$PKG/report.md"

# ---------- архив ----------
ARCHIVE="$WORK/skills-$AUTHOR-$DATE.tar.gz"
tar -czf "$ARCHIVE" -C "$WORK" "skills-$AUTHOR-$DATE"

if [ "$DRY" = 1 ]; then
  echo "collect-my-skills (dry-run): наработок $count_to_send (новых $p_new, изменённых $p_changed, внимание $p_attention), идентичных $p_identical, чужих $other"
  echo "  инвентарь: $INV_SUMMARY"
  echo "  архив: $ARCHIVE"
  echo "  состав:"; tar -tzf "$ARCHIVE" | head -25
  exit 0
fi

# ---------- отправка ----------
case "$MODE" in
  dir)
    mkdir -p "$OUT_DIR"; cp "$ARCHIVE" "$OUT_DIR/"; cp "$PKG/report.md" "$OUT_DIR/skills-$AUTHOR-$DATE-report.md"
    cp "$PKG/inventory.json" "$OUT_DIR/inventory-$AUTHOR-$DATE.json"
    echo "collect-my-skills: наработок $count_to_send (новых $p_new, изменённых $p_changed, внимание $p_attention), инвентарь $INV_SUMMARY -> $OUT_DIR/$(basename "$ARCHIVE")"
    ;;
  telegram)
    : "${TG_TOKEN:?нужен TG_TOKEN}"; : "${TG_CHAT:?нужен TG_CHAT}"
    proxy_args=(); [ -n "${TG_PROXY:-}" ] && proxy_args=(--proxy "$TG_PROXY")
    thread_args=(); [ -n "${TG_THREAD:-}" ] && thread_args=(-F "message_thread_id=$TG_THREAD")
    caption="Наработки $AUTHOR, $DATE: новых $p_new, изменённых $p_changed, внимание $p_attention · инвентарь: $INV_SUMMARY"
    if curl -sS ${proxy_args[@]+"${proxy_args[@]}"} --max-time 120 \
        -F "chat_id=$TG_CHAT" -F "caption=$caption" ${thread_args[@]+"${thread_args[@]}"} \
        -F "document=@$ARCHIVE" \
        "${TG_API:-https://api.telegram.org}/bot$TG_TOKEN/sendDocument" -o "$WORK/tg.json"; then
      if grep -qE '"ok"[[:space:]]*:[[:space:]]*true' "$WORK/tg.json"; then
        echo "collect-my-skills: отправлено в Telegram ($caption)"
      else
        echo "collect-my-skills: Telegram ответил ошибкой: $(head -c 200 "$WORK/tg.json")"; exit 1
      fi
    else
      echo "collect-my-skills: не удалось отправить в Telegram (сеть/прокси)"; exit 1
    fi
    ;;
esac

# состояние обновляем только после успешной отправки
printf '%s %s\n' "$INV_SHA" "$DATE" > "$STATE"
