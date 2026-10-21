#!/usr/bin/env bash
# weekly-fork-sync.sh — еженедельный сбор НОВЫХ скиллов процесса и отправка их в СВОЙ форк.
#
# Логика:
#   1) берём скиллы, которые появились или менялись с прошлого запуска (mtime > отметка состояния);
#   2) отбираем только процессные (по имени/тегам), чтобы не тащить в форк pdf/arxiv/прочее;
#   3) те, которых ещё нет в клоне репозитория, копируем в <клон>/skills/_inbox/<имя>/;
#   4) коммитим и пушим ТОЛЬКО в свой форк (origin, ветка personal по умолчанию);
#   5) первый запуск ничего не отправляет — только ставит отметку времени (baseline).
#
# Не делает: PR, push в общий репозиторий, перезапись существующих скиллов.
# Молчит, если новых скиллов нет (пустой вывод = нет уведомления от cron).
#
# usage: weekly-fork-sync.sh [--repo PATH] [--branch personal] [--dry-run] [--reset-state]
set -uo pipefail

REPO="${HOME}/iiko-product-process"
BRANCH="personal"
DRY=0
RESET=0
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --branch) BRANCH="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    --reset-state) RESET=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

LOG_DIR="$HOME_DIR/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/weekly-fork-sync.log"
STATE="$HOME_DIR/.weekly-fork-sync-last"
log() { printf '%s\t%s\n' "$(date '+%F %T')" "$*" >> "$LOG"; }

# процессные скиллы: по имени или по тегам фронтматтера
PROCESS_NAME_RE='^(iiko-|pb-|spec-|prd-|problem-|data-|competitor-|benchmark-|interview-|job-|market-|research-|jira-|requirement-|task-workspace|share-to-common|mirror-skill|git-onboarding|jtbd-|ux-writing|iikoweb)'

if ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  echo "weekly-fork-sync: $REPO — не git-репозиторий, проверьте путь"; log "нет репозитория $REPO"; exit 1
fi
if [ -n "$(git -C "$REPO" status --porcelain)" ]; then
  echo "weekly-fork-sync: в $REPO есть незакоммиченные изменения — сначала разберитесь с ними"
  log "грязная рабочая копия"; exit 1
fi

if [ ! -f "$STATE" ] || [ "$RESET" = 1 ]; then
  touch "$STATE"
  echo "weekly-fork-sync: первый запуск — отметка времени поставлена, отправлять пока нечего"
  log "baseline установлен"
  exit 0
fi

INBOX="$REPO/skills/_inbox"
existing="$(mktemp)"
find "$REPO" \( -path "$REPO/skills/*/SKILL.md" -o -path "$REPO/step-*/skill/SKILL.md" \
  -o -path "$REPO/step-*/skills/*/SKILL.md" -o -path "$REPO/step-*/skills/*.md" \) -type f 2>/dev/null \
  | while IFS= read -r f; do sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '\r'; done | sort -u > "$existing"

added=""; count=0; skipped=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  name=$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')
  [ -n "$name" ] || continue
  # только процессные: имя по шаблону или тег iiko в frontmatter
  if ! printf '%s' "$name" | grep -qE "$PROCESS_NAME_RE" && ! sed -n '1,20p' "$f" | grep -qi 'iiko'; then
    skipped=$((skipped+1)); continue
  fi
  grep -qx "$name" "$existing" && continue
  count=$((count+1)); added="$added $name"
  if [ "$DRY" = 0 ]; then
    mkdir -p "$INBOX/$name"
    cp -r "$(dirname "$f")/." "$INBOX/$name/"
  fi
done < <(find "$HOME_DIR/skills" -maxdepth 3 -name SKILL.md -type f -newer "$STATE" 2>/dev/null | sort)

rm -f "$existing"

if [ "$count" -eq 0 ]; then
  [ "$DRY" = 1 ] && echo "weekly-fork-sync (dry-run): новых процессных скиллов нет (непроцессных пропущено: $skipped)"
  log "новых нет (пропущено непроцессных: $skipped)"; exit 0
fi

if [ "$DRY" = 1 ]; then
  echo "weekly-fork-sync (dry-run): новых процессных скиллов $count:$added (пропущено непроцессных: $skipped)"
  exit 0
fi

git -C "$REPO" add "$INBOX"
git -C "$REPO" -c user.name="hermes" -c user.email="hermes@iiko" \
  commit -q -m "weekly: новые скиллы процесса из контейнера ($count):$(printf '%s' "$added")" || {
    echo "weekly-fork-sync: коммит не создан (нечего коммитить?)"; log "commit failed"; exit 0; }

if git -C "$REPO" push origin "HEAD:$BRANCH" >/dev/null 2>&1; then
  touch "$STATE"
  echo "weekly-fork-sync: добавлено новых скиллов $count:$added (ветка $BRANCH, форк)"
  log "отправлено $count:$added -> origin/$BRANCH"
else
  echo "weekly-fork-sync: коммит создан, но push в origin/$BRANCH не прошёл — проверьте доступ к форку"
  log "push failed"; exit 1
fi
