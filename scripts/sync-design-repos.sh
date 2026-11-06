#!/usr/bin/env bash
# sync-design-repos.sh — админская синхронизация шага 4 с репозиториями дизайнеров.
#
# Что делает: тянет iiko-DS/Design-System и iiko-DS/Prototype-Guide, заменяет копии в 04-design/
# целиком (точная копия, без переупаковки), сохраняет в общий слой, затем переустанавливает скиллы.
# Если изменений нет — молчит (пустой вывод удобен для cron).
#
# usage: sync-design-repos.sh [--repo PATH] [--cache DIR] [--dry-run]
set -uo pipefail

REPO="${REPO:-/opt/data/iiko-product-office-skills}"
CACHE="${CACHE:-/opt/data/cache/design-repos}"
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --cache) CACHE="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$REPO/.git" ] || { echo "sync-design: $REPO — не git-репозиторий"; exit 1; }
mkdir -p "$CACHE"

TOKEN=""
ENV_FILE="${HERMES_HOME:-$HOME/.hermes}/.env"
[ -f "$ENV_FILE" ] && TOKEN="$(grep -m1 -E '^GITHUB(_TOKEN)?=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' \r')"

clone_or_update() {  # $1 = имя репозитория
  local name="$1" dir="$CACHE/$1"
  if [ -d "$dir/.git" ]; then
    git -C "$dir" fetch -q origin || return 1
    git -C "$dir" reset -q --hard origin/main || return 1
  else
    # остался мусор от прошлого запуска (каталог без .git) — иначе clone не сможет создать папку
    [ -e "$dir" ] && [ ! -d "$dir/.git" ] && rm -rf "$dir"
    local url="https://github.com/iiko-DS/$name.git"
    [ -n "$TOKEN" ] && url="https://x-access-token:$TOKEN@github.com/iiko-DS/$name.git"
    git clone -q --depth 1 "$url" "$dir" || return 1
  fi
}

changed=0
for name in Design-System Prototype-Guide; do
  clone_or_update "$name" || { echo "sync-design: не удалось получить $name"; exit 1; }
  src="$CACHE/$name"; dst="$REPO/04-design/$name"
  if [ -d "$dst" ] && diff -rq --exclude=.git "$src" "$dst" >/dev/null 2>&1; then
    continue
  fi
  changed=$((changed+1))
  echo "обновление: $name -> 04-design/$name"
  if [ "$DRY" = 0 ]; then
    rm -rf "$dst"; mkdir -p "$dst"
    cp -r "$src/." "$dst/"; rm -rf "$dst/.git"
  fi
done

if [ "$changed" -eq 0 ]; then
  [ "$DRY" = 1 ] && echo "sync-design (dry-run): копии актуальны"
  exit 0
fi

if [ "$DRY" = 1 ]; then
  echo "sync-design (dry-run): изменилось $changed репозиториев, коммит не делаю"
  exit 0
fi

if [ -z "$(git -C "$REPO" status --porcelain 04-design)" ]; then
  echo "sync-design: после копирования изменений нет"; exit 0
fi

git -C "$REPO" add 04-design
git -C "$REPO" -c user.name=hermes -c user.email=hermes@iiko commit -q -m "Шаг 4: синхронизация с репозиториями дизайнеров ($(date +%F))"
if git -C "$REPO" push origin main >/dev/null 2>&1; then
  echo "sync-design: обновлено и отправлено в main ($changed репозиториев)"
else
  echo "sync-design: коммит создан, push не прошёл — проверьте доступ"; exit 1
fi

# скиллы ДС лежат внутри Prototype-Guide — переустановить, чтобы Hermes увидел изменения
bash "$REPO/skills/git-skills-install/scripts/install-skills-from-repo.sh" >/dev/null 2>&1 || true
