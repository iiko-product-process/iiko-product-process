#!/usr/bin/env bash
# setup-all.sh — подключить папку процесса и настроить все джобы одной командой.
#
# Делает по порядку и безопасно повторно:
#   1) получает папку процесса (если её нет) или обновляет её;
#   2) ставит все скиллы процесса в Hermes;
#   3) создаёт хранилище артефактов (Hermes wiki → ARTIFACTS/);
#   4) ставит обёртки для двух еженедельных задач;
#   5) печатает параметры cron-задач и итоговый чек-лист.
#
# usage: setup-all.sh [--repo PATH] [--home PATH] [--artifacts PATH] [--dry-run]
set -uo pipefail

REPO="${IIKO_REPO:-$HOME/iiko_process}"
[ -d "$REPO/.git" ] || { [ -d "$HOME/iiko_process/.git" ] && [ -z "${IIKO_REPO:-}" ] && REPO="$HOME/iiko_process"; }
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
ARTIFACTS="${IIKO_ARTIFACTS:-}"
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --home) HOME_DIR="${2:?}"; shift ;;
    --artifacts|--wiki) ARTIFACTS="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

# --home меняет и путь вики по умолчанию, поэтому вычисляем после разбора флагов
[ -n "$ARTIFACTS" ] || ARTIFACTS="$REPO/ARTIFACTS"   # всё в одной папке: <папка процесса>/ARTIFACTS

DRYARG=""; [ "$DRY" = 1 ] && DRYARG="--dry-run"
ENV_FILE="$HOME_DIR/.env"
TOKEN=""
[ -f "$ENV_FILE" ] && TOKEN="$(grep -m1 -E '^GITHUB(_TOKEN)?=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' \r')"

echo "== 1. репозиторий"
if [ -d "$REPO/.git" ]; then
  if [ -z "$(git -C "$REPO" status --porcelain 2>/dev/null)" ]; then
    if [ "$DRY" = 0 ]; then
      git -C "$REPO" fetch -q origin 2>/dev/null && git -C "$REPO" merge --ff-only origin/main >/dev/null 2>&1 \
        && echo "обновлён: $(git -C "$REPO" log -1 --format='%h %ad' --date=short)" \
        || echo "клон есть, обновить не удалось — проверьте доступ"
    else
      echo "папка процесса есть: $REPO (dry-run, не обновляю)"
    fi
  else
    echo "в рабочей копии есть локальные изменения — обновление пропущено"
  fi
else
  mkdir -p "$(dirname "$REPO")"
  url="https://github.com/iiko-product-process/iiko-product-process.git"
  [ -n "$TOKEN" ] && url="https://x-access-token:$TOKEN@github.com/iiko-product-process/iiko-product-process.git"
  if [ "$DRY" = 0 ]; then
    git clone -q "$url" "$REPO" && echo "папка процесса получена: $REPO" || { echo "папку получить не удалось — проверьте доступ/токен"; exit 1; }
  else
    echo "будет получена папка процесса: $REPO"
  fi
fi

if [ ! -d "$REPO/.git" ]; then
  echo "== 2-5. пропущено: репозитория ещё нет (dry-run)"
  exit 0
fi

echo "== 2. скиллы"
bash "$REPO/skills/git-skills-install/scripts/install-skills-from-repo.sh" --home "$HOME_DIR" $DRYARG | tail -1
# манифест канона: по нему сборщик отличает свои наработки от поставленных скиллов
if [ "$DRY" = 0 ]; then
  bash "$REPO/scripts/make-skills-manifest.sh" --repo "$REPO" > "$HOME_DIR/canon-skills-manifest.tsv"
  echo "манифест: $(wc -l < "$HOME_DIR/canon-skills-manifest.tsv") скиллов"
fi

echo "== 3. хранилище артефактов"
if [ -d "$ARTIFACTS/_шаблон" ]; then
  echo "ARTIFACTS уже есть: $ARTIFACTS"
elif [ "$DRY" = 1 ]; then
  echo "будет создана: $ARTIFACTS (_шаблон)"
else
  bash "$REPO/skills/hermes-wiki/scripts/wiki-init.sh" "$ARTIFACTS" >/dev/null && echo "создана: $ARTIFACTS"
fi

echo "== 4. джобы"
if [ "$DRY" = 1 ]; then
  echo "будут созданы обёртки: design-update-weekly.sh, skills-collect-weekly.sh"
else
  bash "$REPO/scripts/setup-design-cron.sh" --repo "$REPO" --home "$HOME_DIR" >/dev/null
  mkdir -p "$HOME_DIR/scripts"
  cat > "$HOME_DIR/scripts/skills-collect-weekly.sh" <<EOF
#!/usr/bin/env bash
# skills-collect-weekly.sh — еженедельный сбор наработок сотрудника (создано setup-all.sh).
out=\$(bash "$REPO/skills/skills-inbox/scripts/collect-my-skills.sh" --home "$HOME_DIR" --author "\$(whoami)" --manifest "$HOME_DIR/canon-skills-manifest.tsv" --out "$HOME_DIR/skill-reports" 2>&1) || rc=\$?
case "\$out" in
  *"нечего"*|*"0 файл"*|*"0 скилл"*|*"скиллов нет"*|*"нет изменений"*) exit 0 ;;   # нечего отправлять — молчим
esac
[ -n "\${rc:-}" ] && { echo "\$out"; exit "\$rc"; }
echo "\$out"
EOF
  chmod +x "$HOME_DIR/scripts/skills-collect-weekly.sh"
  echo "обёртки: design-update-weekly.sh, skills-collect-weekly.sh"
fi

if [ "$DRY" = 0 ]; then
  echo "== 5. проверка"
  bash "$REPO/scripts/check-setup.sh" --repo "$REPO" --home "$HOME_DIR" --artifacts "$ARTIFACTS" | tail -8
fi

cat <<'EOF'

Cron-задачи (создаёт Гермес, режим — без агента):
  1) обновление дизайн-системы : 0 6 * * 0  (вс 09:00 МСК)  скрипт design-update-weekly.sh
  2) сбор наработок сотрудника : 0 7 * * 5  (пт 10:00 МСК)  скрипт skills-collect-weekly.sh
Пустой вывод = изменений не было и уведомление не нужно.
EOF
