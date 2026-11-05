#!/usr/bin/env bash
# update-design-step.sh — обновление шага 4 у сотрудника (раз в неделю, воскресенье).
#
# Что делает: обновляет клон репозитория процесса до свежего main и переустанавливает скиллы,
# чтобы в понедельник были актуальные дизайн-система и компоненты. Форков и пуша нет.
# Если обновлений не было — молчит (пустой вывод удобен для cron).
#
# usage: update-design-step.sh [--repo PATH] [--dry-run]
set -uo pipefail

REPO="${IIKO_REPO:-$HOME/iiko-product-process}"
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

TOKEN=""
ENV_FILE="${HERMES_HOME:-$HOME/.hermes}/.env"
[ -f "$ENV_FILE" ] && TOKEN="$(grep -m1 -E '^GITHUB(_TOKEN)?=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' \r')"

if [ ! -d "$REPO/.git" ]; then
  echo "update-design: клона нет, клонирую в $REPO"
  mkdir -p "$(dirname "$REPO")"
  url="https://github.com/iiko-product-process/iiko-product-process.git"
  [ -n "$TOKEN" ] && url="https://x-access-token:$TOKEN@github.com/iiko-product-process/iiko-product-process.git"
  git clone -q "$url" "$REPO" || { echo "update-design: клон не удался"; exit 1; }
fi

before="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo none)"

if [ -n "$(git -C "$REPO" status --porcelain 04-design)" ]; then
  echo "update-design: в 04-design есть локальные правки — пропускаю, чтобы не потерять"
  exit 1
fi

if [ "$DRY" = 1 ]; then
  git -C "$REPO" fetch -q origin || { echo "update-design: fetch не удался"; exit 1; }
  behind=$(git -C "$REPO" rev-list --count "HEAD..origin/main" 2>/dev/null || echo 0)
  echo "update-design (dry-run): отстаём на $behind коммит(ов)"
  exit 0
fi

git -C "$REPO" fetch -q origin || { echo "update-design: fetch не удался (сеть/токен)"; exit 1; }
git -C "$REPO" merge --ff-only origin/main >/dev/null 2>&1 || {
  echo "update-design: обновление невозможно (локальные коммиты или расхождение)"; exit 1; }

after="$(git -C "$REPO" rev-parse --short HEAD)"
if [ "$before" = "$after" ]; then exit 0; fi   # изменений нет — молчим

echo "update-design: клон обновлён $before -> $after"
bash "$REPO/skills/git-skills-install/scripts/install-skills-from-repo.sh" >/dev/null 2>&1 || \
  echo "update-design: скиллы не переустановились, повторите вручную"
echo "update-design: дизайн-система и компоненты актуальны"
