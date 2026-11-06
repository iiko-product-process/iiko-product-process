#!/usr/bin/env bash
# check-setup.sh — проверить, что настройка процесса на машине сотрудника сделана целиком.
#
# Ничего не меняет: только смотрит и печатает чек-лист. Код 1 — если что-то критичное не настроено.
#
# usage: check-setup.sh [--repo PATH] [--home PATH] [--artifacts PATH]
set -uo pipefail

REPO="${IIKO_REPO:-$HOME/iiko_process}"
[ -d "$REPO/.git" ] || { [ -d "$HOME/iiko_process/.git" ] && [ -z "${IIKO_REPO:-}" ] && REPO="$HOME/iiko_process"; }
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
ARTIFACTS="${IIKO_ARTIFACTS:-}"

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --home) HOME_DIR="${2:?}"; shift ;;
    --artifacts|--artifacts) ARTIFACTS="${2:?}"; shift ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ -z "$ARTIFACTS" ]; then
  if [ -f "$HOME_DIR/iiko-artifacts-root" ]; then ARTIFACTS="$(cat "$HOME_DIR/iiko-artifacts-root")"
  elif [ -d "$REPO/ARTIFACTS" ]; then ARTIFACTS="$REPO/ARTIFACTS"
  elif [ -d "$HOME_DIR/ARTIFACTS" ]; then ARTIFACTS="$HOME_DIR/ARTIFACTS"
  elif [ -d "$HOME/ARTIFACTS" ]; then ARTIFACTS="$HOME/ARTIFACTS"; fi
fi

ok=0; bad=0
say_ok(){ printf 'OK   %s\n' "$*"; ok=$((ok+1)); }
say_bad(){ printf 'НЕТ  %s\n' "$*"; bad=$((bad+1)); }

# 1. клон
if [ -d "$REPO/.git" ]; then
  say_ok "клон репозитория: $REPO ($(git -C "$REPO" log -1 --format='%h %ad' --date=short 2>/dev/null))"
else
  say_bad "клон репозитория: $REPO — не найден (клонируйте или укажите --repo)"
fi

# 2. токен
ENV_FILE="$HOME_DIR/.env"
if [ -f "$ENV_FILE" ] && grep -qE '^GITHUB(_TOKEN)?=' "$ENV_FILE"; then
  say_ok "токен GitHub в $ENV_FILE"
else
  say_bad "токен GitHub: нет в $ENV_FILE (ключ GITHUB_TOKEN или GITHUB)"
fi

# 3. скиллы: сколько из INDEX.md установлено
if [ -d "$REPO" ] && [ -f "$REPO/INDEX.md" ] && [ -d "$HOME_DIR/skills" ]; then
  total=0; have=0
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    total=$((total+1))
    find "$HOME_DIR/skills" -maxdepth 2 -type d -name "$n" 2>/dev/null | grep -q . && have=$((have+1))
  done < <(grep -E '^\| [a-z0-9][a-z0-9-]+ \|' "$REPO/INDEX.md" | cut -d'|' -f2 | tr -d ' ')
  if [ "$have" -eq "$total" ]; then say_ok "скиллы установлены: $have из $total"
  else say_bad "скиллы установлены: $have из $total — запустите install-skills-from-repo.sh"; fi
else
  say_bad "скиллы: нет INDEX.md или каталога скиллов"
fi

# 4. ARTIFACTS — отдельная папка в дереве
if [ -n "$ARTIFACTS" ] && [ -d "$ARTIFACTS/_шаблон" ]; then
  say_ok "ARTIFACTS: $ARTIFACTS (_шаблон на месте)"
else
  say_bad "ARTIFACTS: папка не найдена — запустите wiki-init.sh"
fi

# 4b. ARTIFACTS не должна быть в git
if [ -n "$ARTIFACTS" ] && [ -d "$ARTIFACTS" ] && [ -d "$REPO/.git" ]; then
  if [ -n "$(git -C "$REPO" ls-files -- ARTIFACTS 2>/dev/null | head -1)" ]; then
    say_bad "ARTIFACTS попала в git — уберите из индекса (git rm -r --cached ARTIFACTS)"
  else
    say_ok "ARTIFACTS не в git (.gitignore)"
  fi
fi

# 5. автообновление шага 4
if [ -x "$HOME_DIR/scripts/design-update-weekly.sh" ]; then
  say_ok "обновление шага 4: обёртка design-update-weekly.sh на месте"
else
  say_bad "обновление шага 4: обёртки нет — запустите setup-design-cron.sh"
fi

# 6. MCP в конфиге
CFG="$HOME_DIR/config.yaml"
if [ -f "$CFG" ] && grep -q '^mcp_servers:' "$CFG"; then
  mcp=$(awk '/^mcp_servers:/{f=1;next} f&&/^[a-z_]+:/{f=0} f&&/^  [a-z_]+:/{print $1}' "$CFG" | tr -d ':' | tr '\n' ' ')
  say_ok "MCP подключены: ${mcp:-нет ни одного}"
else
  say_bad "MCP: в $CFG нет секции mcp_servers"
fi

echo
if [ "$bad" -eq 0 ]; then echo "ИТОГ: всё настроено ($ok проверок)"; exit 0
else echo "ИТОГ: не настроено $bad из $((ok+bad)) — см. строки «НЕТ»"; exit 1; fi
