#!/usr/bin/env bash
# wiki-init.sh — создать/дополнить Hermes wiki: корень, artifacts/, шаблон задачи.
#
# usage:
#   wiki-init.sh <путь-вики>                  # index.md, artifacts/, artifacts/_шаблон
#   wiki-init.sh <путь-вики> --task <слаг>    # ещё и новая задача из шаблона
#   wiki-init.sh <путь-вики> --dry-run        # только показать план
set -uo pipefail

WIKI="${1:?укажите путь к вики}"; shift || true
TASK=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --task) TASK="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

SECTIONS=("01-проблема" "02-гипотезы" "03-требования" "04-дизайн" "05-спека" "06-реализация" "07-пилот" "материалы" "встречи")

make_task() {  # $1 = путь папки задачи, $2 = слаг
  local dir="$1" slug="$2"
  mkdir -p "$dir"
  for s in "${SECTIONS[@]}"; do mkdir -p "$dir/$s"; done
  if [ ! -f "$dir/README.md" ]; then
    cat > "$dir/README.md" <<EOF
---
задача: $slug
статус: в работе
шаг: 01-проблема
ведёт: 
создано: $(date +%F)
---

# Задача: $slug

**Статус:** в работе · **Текущий шаг:** 01-проблема · **Ведёт:** —

## Ссылки

- Jira: 
- Прототип: 
- PRD: 

## Что дальше

- [ ] 
EOF
  fi
  if [ ! -f "$dir/журнал.md" ]; then
    cat > "$dir/журнал.md" <<'EOF'
# Журнал задачи

| Дата | Что сделали | Артефакты | Кто |
|---|---|---|---|
EOF
  fi
}

if [ "$DRY" = 1 ]; then
  echo "wiki-init (dry-run): $WIKI"
  echo "  создать: artifacts/, artifacts/_шаблон, index.md (если нет)"
  [ -n "$TASK" ] && echo "  создать задачу: artifacts/$TASK"
  exit 0
fi

mkdir -p "$WIKI/artifacts"
[ -f "$WIKI/index.md" ] || cat > "$WIKI/index.md" <<'EOF'
# Hermes wiki

Артефакты задач процесса iiko. Репозиторий хранит скиллы, здесь — работа по задачам.

| Задача | Статус | Шаг | Ссылки |
|---|---|---|---|
EOF

make_task "$WIKI/artifacts/_шаблон" "_шаблон"
echo "wiki-init: готово — $WIKI (artifacts/, _шаблон)"

if [ -n "$TASK" ]; then
  make_task "$WIKI/artifacts/$TASK" "$TASK"
  grep -q "artifacts/$TASK" "$WIKI/index.md" || \
    printf '| [%s](artifacts/%s/README.md) | в работе | 01-проблема |  |\n' "$TASK" "$TASK" >> "$WIKI/index.md"
  echo "wiki-init: создана задача artifacts/$TASK"
fi
