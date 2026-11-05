#!/usr/bin/env bash
# install-skills-from-repo.sh — установить ВСЕ скиллы из репозитория процесса в Hermes.
#
# Запуск после клонирования репозитория или после git pull: копирует скиллы из папок шагов
# и из skills/ в $HERMES_HOME/skills/productivity/<имя>/, чтобы Гермес их видел.
#
# usage: install-skills-from-repo.sh [--repo PATH] [--home PATH] [--category NAME] [--dry-run] [--force]
#
# Политика конфликтов: если установленная копия отличается от той, что записана в манифесте
# (то есть её правили руками), такая копия НЕ перезаписывается — она попадает в отчёт.
# --force перезаписывает всё.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CATEGORY="productivity"
DRY=0
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:?}"; shift ;;
    --home) HOME_DIR="${2:?}"; shift ;;
    --category) CATEGORY="${2:?}"; shift ;;
    --dry-run) DRY=1 ;;
    --force) FORCE=1 ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$HOME_DIR/skills" ] || HOME_DIR="$HOME"
SKILLS_ROOT="$HOME_DIR/skills"
[ -d "$SKILLS_ROOT" ] || { echo "install-skills: не найден каталог скиллов ($SKILLS_ROOT)"; exit 1; }

STATE="$HOME_DIR/.repo-skills-manifest.tsv"
STATE_HEADER="#dirhash-v2"

# отпечаток каталога целиком: важен не только SKILL.md, но и references/templates/scripts
dir_sha() {
  find "$1" -type f -print0 2>/dev/null | sort -z | xargs -0 -r sha1sum 2>/dev/null \
    | awk '{print $1}' | sha1sum | cut -d' ' -f1
}
TARGET="$SKILLS_ROOT/$CATEGORY"
[ "$DRY" = 0 ] && mkdir -p "$TARGET"
echo "install-skills: репозиторий $REPO -> $TARGET"

LIST="$(mktemp)"; RAW="$(mktemp)"; WIN="$(mktemp)"; NEW="$(mktemp)"
find "$REPO" \( -path "$REPO/skills/*/SKILL.md" -o -path "$REPO/*/skill/SKILL.md" \
  -o -path "$REPO/*/skills/*/SKILL.md" -o -path "$REPO/*/skills/*.md" \) -type f 2>/dev/null \
  | grep -v '/.git/' | grep -v '/_inbox/' | sort > "$RAW"

# отсекаем вложенные файлы скиллов (references/, templates/, scripts/):
# принимаем только SKILL.md или плоский скилл, лежащий прямо в <шаг>/skills/
while IFS= read -r f; do
  base=$(basename "$f"); parent=$(basename "$(dirname "$f")")
  if [ "$base" != "SKILL.md" ] && [ "$parent" != "skills" ]; then continue; fi
  printf '%s\n' "$f" >> "$LIST"
done < "$RAW"

while IFS= read -r f; do
  name=$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')
  [ -n "$name" ] || name=$(basename "$(dirname "$f")")
  prev=$(awk -F'\t' -v n="$name" '$1==n{print $2}' "$WIN")
  if [ -n "$prev" ]; then
    case "$prev" in
      *prototyping-guide*) printf '%s\t%s\n' "$name" "$f" >> "$WIN.tmp"; awk -F'\t' -v n="$name" '{if($1==n) next; print}' "$WIN" >> "$WIN.tmp"; mv "$WIN.tmp" "$WIN" ;;
      *) : ;;
    esac
  else
    printf '%s\t%s\n' "$name" "$f" >> "$WIN"
  fi
done < "$LIST"

printf '%s\n' "$STATE_HEADER" > "$NEW"
installed=0; updated=0; same=0; skipped=0; flat=0
while IFS=$'\t' read -r name f; do
  [ -n "$name" ] || continue
  ver=$(sed -n 's/^version:[[:space:]]*//p' "$f" | head -1 | tr -d '\r')
  src_dir=$(dirname "$f")
  dst_dir="$TARGET/$name"
  dst="$dst_dir/SKILL.md"
  flat_src=0; [ "$(basename "$f")" = "SKILL.md" ] || flat_src=1
  if [ "$flat_src" = 1 ]; then sha=$(sha1sum "$f" | cut -d' ' -f1); else sha=$(dir_sha "$src_dir"); fi

  if [ -f "$dst" ]; then
    if [ "$flat_src" = 1 ]; then cur=$(sha1sum "$dst" | cut -d' ' -f1); else cur=$(dir_sha "$dst_dir"); fi
    [ "$cur" = "$sha" ] && { same=$((same+1)); printf '%s\t%s\t%s\t%s\n' "$name" "$sha" "${ver:-}" "${f#$REPO/}" >> "$NEW"; continue; }
    prev=$(awk -F'\t' -v n="$name" '$1==n{print $2}' "$STATE" 2>/dev/null | head -1)
    grep -qx "$STATE_HEADER" "$STATE" 2>/dev/null || prev=""   # старый формат манифеста — без защиты от перезаписи
    if [ "$FORCE" = 0 ] && [ -n "$prev" ] && [ "$prev" != "$cur" ]; then
      echo "  пропуск: $name — локальная копия правилась руками"; skipped=$((skipped+1)); continue
    fi
    action="обновлён"; updated=$((updated+1))
  else
    action="установлен"; installed=$((installed+1))
  fi

  if [ "$DRY" = 0 ]; then
    rm -rf "$dst_dir"; mkdir -p "$dst_dir"
    if [ "$(basename "$f")" = "SKILL.md" ]; then cp -r "$src_dir/." "$dst_dir/"; else cp "$f" "$dst"; flat=$((flat+1)); fi
  fi
  echo "  $action: $name (${ver:-без версии})"
  printf '%s\t%s\t%s\t%s\n' "$name" "$sha" "${ver:-}" "${f#$REPO/}" >> "$NEW"
done < "$WIN"

if [ "$DRY" = 0 ]; then mv "$NEW" "$STATE"; else rm -f "$NEW"; fi
rm -f "$LIST" "$RAW" "$WIN"

total=$((installed + updated + same + skipped))
echo "install-skills: всего $total | установлено $installed | обновлено $updated | без изменений $same | пропущено $skipped"
[ "$DRY" = 1 ] && echo "режим dry-run: ничего не изменено (уберите --dry-run)"
exit 0
