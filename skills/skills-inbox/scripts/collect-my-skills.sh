#!/usr/bin/env bash
# collect-my-skills.sh — собрать НОВЫЕ и ИЗМЕНЁННЫЕ скиллы сотрудника в архив и отправить админу.
#
# Сотруднику git не нужен: скрипт сравнивает локальные скиллы с манифестом канона,
# упаковывает отличия в tar.gz и отправляет в Telegram или складывает в папку.
#
# usage:
#   collect-my-skills.sh [--home PATH] [--manifest FILE] [--author NAME]
#                        [--out DIR | --telegram]
#                        [--dry-run]
#   env: TG_TOKEN, TG_CHAT, TG_THREAD (id темы в группе, необязательно),
#        TG_PROXY (например socks5h://proxy:1080), TG_API (подмена адреса API — для тестов)
#
# По умолчанию: --home $HERMES_HOME (или ~/.hermes), --out ~/skill-reports
# Формат манифеста канона: TSV "name<TAB>sha1<TAB>version" (как .canon-sync-state.tsv).
set -uo pipefail

HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
MANIFEST=""
AUTHOR="$(whoami 2>/dev/null || echo employee)"
OUT_DIR="$HOME/skill-reports"
MODE="dir"
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --home) HOME_DIR="${2:?}"; shift ;;
    --manifest) MANIFEST="${2:?}"; shift ;;
    --author) AUTHOR="${2:?}"; shift ;;
    --out) OUT_DIR="${2:?}"; MODE="dir"; shift ;;
    --telegram) MODE="telegram" ;;
    --dry-run) DRY=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$HOME_DIR/skills" ] || HOME_DIR="$HOME"
SKILLS="$HOME_DIR/skills"
[ -d "$SKILLS" ] || { echo "collect-my-skills: не найден каталог скиллов (искал $SKILLS)"; exit 1; }

DATE="$(date +%Y-%m-%d)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
PKG="$WORK/skills-$AUTHOR-$DATE"; mkdir -p "$PKG/skills"

# ---------- манифест канона (name -> sha1, version) ----------
declare -A CANON_SHA CANON_VER
if [ -n "$MANIFEST" ] && [ -f "$MANIFEST" ]; then
  while IFS=$'\t' read -r n s v; do
    [ -n "${n:-}" ] || continue
    CANON_SHA["$n"]="${s:-}"; CANON_VER["$n"]="${v:-}"
  done < "$MANIFEST"
fi

# ---------- скан скиллов ----------
items_json="$WORK/items.jsonl"
: > "$items_json"
total=0; new=0; changed=0; identical=0; attention=0

find "$SKILLS" -maxdepth 3 -name SKILL.md -type f 2>/dev/null | sort | while IFS= read -r f; do echo "$f"; done > "$WORK/list.txt"

while IFS= read -r f; do
  [ -n "$f" ] || continue
  dir="$(dirname "$f")"; name="$(basename "$dir")"
  docname="$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')"
  [ -n "$docname" ] && name="$docname"
  ver="$(sed -n 's/^version:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')"
  sha="$(sha1sum "$f" | cut -d' ' -f1)"
  total=$((total+1))

  status="new"
  if [ -n "${CANON_SHA[$name]:-}" ]; then
    if [ "${CANON_SHA[$name]}" = "$sha" ]; then status="identical"; else status="changed"; fi
  fi

  # секреты: не отправляем молча, но помечаем
  secrets=""
  while IFS= read -r hit; do
    [ -n "$hit" ] && secrets="$secrets$(basename "$hit");"
  done < <(grep -rIlE 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' "$dir" 2>/dev/null | head -5)
  [ -n "$secrets" ] && status="attention"

  case "$status" in
    new) new=$((new+1)) ;;
    changed) changed=$((changed+1)) ;;
    identical) identical=$((identical+1)) ;;
    attention) attention=$((attention+1)) ;;
  esac

  size=$(du -sk "$dir" 2>/dev/null | cut -f1)
  printf '{"name":"%s","version":"%s","sha1":"%s","status":"%s","size_kb":%s,"secrets":"%s","path":"%s","mtime":"%s"}\n' \
    "$name" "${ver:-}" "$sha" "$status" "${size:-0}" "$secrets" "${dir#$SKILLS/}" \
    "$(date -r "$f" +%Y-%m-%d 2>/dev/null || echo "")" >> "$items_json"

  if [ "$status" != "identical" ]; then
    mkdir -p "$PKG/skills/$name"
    # только текст и мелочь; крупные бинарники не тащим
    ( cd "$dir" && find . -type f -size -5120k -print0 2>/dev/null | while IFS= read -r -d '' x; do
        mkdir -p "$PKG/skills/$name/$(dirname "$x")"; cp "$x" "$PKG/skills/$name/$x"; done )
  fi
done < "$WORK/list.txt"

count_to_send=$((new+changed+attention))
if [ "$count_to_send" -eq 0 ]; then
  echo "collect-my-skills: новых и изменённых скиллов нет (всего $total, идентичны канону $identical)"
  exit 0
fi

# ---------- manifest.json + отчёт ----------
{
  printf '{\n  "author": "%s",\n  "date": "%s",\n  "host": "%s",\n  "manifest": "%s",\n  "items": [\n' \
    "$AUTHOR" "$DATE" "$(hostname 2>/dev/null || echo unknown)" "${MANIFEST:-none}"
  awk 'BEGIN{first=1} {if(!first) printf ",\n"; first=0; printf "    %s", $0} END{printf "\n"}' "$items_json"
  printf '  ]\n}\n'
} > "$PKG/manifest.json"

{
  echo "# Скиллы $AUTHOR, $DATE"
  echo
  echo "Всего локально: $total · новых: $new · изменённых: $changed · идентичны канону: $identical · требуют внимания: $attention"
  echo
  echo "## Что отправлено"
  echo
  echo "| Скилл | Версия | Статус | Размер |"
  echo "|---|---|---|---|"
  python3 - "$items_json" <<'PY'
import json, sys
for line in open(sys.argv[1], encoding='utf-8'):
    d = json.loads(line)
    if d['status'] == 'identical':
        continue
    print(f"| {d['name']} | {d['version'] or '—'} | {d['status']} | {d['size_kb']} КБ |")
PY
  echo
  echo "## Зачем (заполни, если не сложно)"
  echo
  echo "- "
} > "$PKG/report.md"

ARCHIVE="$WORK/skills-$AUTHOR-$DATE.tar.gz"
tar -czf "$ARCHIVE" -C "$WORK" "skills-$AUTHOR-$DATE"

if [ "$DRY" = 1 ]; then
  echo "collect-my-skills (dry-run): новых $new, изменённых $changed, внимание $attention, идентичных $identical — отправил бы $count_to_send из $total"
  echo "  архив: $ARCHIVE"
  echo "  состав:"; tar -tzf "$ARCHIVE" | head -20
  exit 0
fi

case "$MODE" in
  dir)
    mkdir -p "$OUT_DIR"; cp "$ARCHIVE" "$OUT_DIR/"
    cp "$PKG/report.md" "$OUT_DIR/skills-$AUTHOR-$DATE-report.md"
    echo "collect-my-skills: отправлено $count_to_send скиллов (новых $new, изменённых $changed, внимание $attention) -> $OUT_DIR/$(basename "$ARCHIVE")"
    ;;
  telegram)
    : "${TG_TOKEN:?нужен TG_TOKEN}"; : "${TG_CHAT:?нужен TG_CHAT}"
    proxy_args=(); [ -n "${TG_PROXY:-}" ] && proxy_args=(--proxy "$TG_PROXY")
    thread_args=(); [ -n "${TG_THREAD:-}" ] && thread_args=(-F "message_thread_id=$TG_THREAD")
    caption="Скиллы $AUTHOR, $DATE: новых $new, изменённых $changed, внимание $attention"
    if curl -sS "${proxy_args[@]}" --max-time 120 \
        -F "chat_id=$TG_CHAT" -F "caption=$caption" "${thread_args[@]}" \
        -F "document=@$ARCHIVE" \
        "${TG_API:-https://api.telegram.org}/bot$TG_TOKEN/sendDocument" -o "$WORK/tg.json"; then
      if grep -qE '"ok"[[:space:]]*:[[:space:]]*true' "$WORK/tg.json"; then
        echo "collect-my-skills: отправлено $count_to_send скиллов в Telegram ($caption)"
      else
        echo "collect-my-skills: Telegram ответил ошибкой: $(head -c 200 "$WORK/tg.json")"; exit 1
      fi
    else
      echo "collect-my-skills: не удалось отправить в Telegram (сеть/прокси)"; exit 1
    fi
    ;;
esac
