#!/usr/bin/env bash
# make-skills-manifest.sh — собрать манифест скиллов репозитория для сбора наработок.
#
# Формат: name<TAB>sha1<TAB>version — тот же, что у canon-sync и collect-my-skills.
# Сравнивая с ним, сборщик видит только собственные новые/изменённые скиллы сотрудника.
#
# usage: make-skills-manifest.sh [--repo PATH] > manifest.tsv
set -uo pipefail

REPO="${IIKO_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[ "${1:-}" = "--repo" ] && REPO="${2:?}"

[ -d "$REPO" ] || { echo "make-skills-manifest: нет репозитория $REPO" >&2; exit 1; }

LIST="$(mktemp)"; trap 'rm -f "$LIST"' EXIT
{
  find "$REPO" -name SKILL.md -not -path "*/.git/*" -not -path "*/_inbox/*" 2>/dev/null
  find "$REPO" -maxdepth 3 -path "*/skills/*.md" -not -name "README.md" -not -path "*/.git/*" 2>/dev/null
} | sort -u | while IFS= read -r f; do
  base=$(basename "$f"); parent=$(basename "$(dirname "$f")")
  # отсекаем файлы из references/templates/scripts внутри скиллов
  if [ "$base" != "SKILL.md" ] && [ "$parent" != "skills" ]; then continue; fi
  name=$(sed -n 's/^name:[[:space:]]*//p' "$f" | head -1 | tr -d '"'"'"' ')
  [ -n "$name" ] || name="$base"
  [ "$name" = "SKILL.md" ] && name="$parent"
  version=$(sed -n 's/^version:[[:space:]]*//p' "$f" | head -1 | tr -d '"'"'"' ')
  sha=$(sha1sum "$f" | cut -d' ' -f1)
  printf '%s\t%s\t%s\n' "$name" "$sha" "${version:-0.0.0}"
done | sort -u
