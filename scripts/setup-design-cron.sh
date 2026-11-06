#!/usr/bin/env bash
# setup-design-cron.sh — подготовить у сотрудника еженедельное обновление шага 4.
#
# Hermes-cron запускает только скрипты из $HERMES_HOME/scripts, поэтому здесь:
#   1) ставится обёртка design-update-weekly.sh, которая дергает scripts/update-design-step.sh;
#   2) печатается точная инструкция для cron-задачи (её создаёт Hermes по просьбе сотрудника).
#
# usage: setup-design-cron.sh [--repo PATH] [--home PATH] [--check]
set -uo pipefail

REPO="${IIKO_REPO:-$HOME/iiko_process}"
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CHECK=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --home) HOME_DIR="${2:?}"; shift ;;
    --check) CHECK=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

WRAPPER="$HOME_DIR/scripts/design-update-weekly.sh"

if [ "$CHECK" = 1 ]; then
  [ -x "$WRAPPER" ] && echo "setup-design-cron: обёртка на месте ($WRAPPER)" || echo "setup-design-cron: обёртки нет — запустите без --check"
  exit 0
fi

mkdir -p "$HOME_DIR/scripts"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
# design-update-weekly.sh — обновление шага 4 у сотрудника (создано setup-design-cron.sh).
exec "$REPO/scripts/update-design-step.sh" --repo "$REPO" "\$@"
EOF
chmod +x "$WRAPPER"
echo "setup-design-cron: обёртка установлена -> $WRAPPER"

cat <<EOF

Осталось создать cron-задачу (Гермес делает это сам по просьбе сотрудника):
  расписание : 0 6 * * 0   (воскресенье, 09:00 МСК)
  режим      : без агента
  скрипт     : design-update-weekly.sh
  результат  : пустой вывод = обновлений не было

Проверить вручную:
  bash "$REPO/scripts/update-design-step.sh" --dry-run
EOF
