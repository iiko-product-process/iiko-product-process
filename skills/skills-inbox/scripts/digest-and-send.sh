#!/usr/bin/env bash
# digest-and-send.sh — админская обёртка: собрать дайджест и отправить файлом в Telegram.
#
# Запускается по cron раз в неделю. Если архивов нет — молчит (ничего не отправляет).
#
# usage: digest-and-send.sh [--inbox DIR] [--canon-repo PATH] [--token-file FILE] [--chat-file FILE]
# env: TG_PROXY, TG_API (подмена адреса API — для тестов)
set -uo pipefail

INBOX="${INBOX:-/opt/data/skills-inbox}"
CANON="${CANON:-/opt/data/iiko-product-office-skills}"
TOKEN_FILE="${TOKEN_FILE:-/opt/data/tg-skills-token}"
CHAT_FILE="${CHAT_FILE:-/opt/data/tg-skills-token.chat}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [ $# -gt 0 ]; do
  case "$1" in
    --inbox) INBOX="${2:?}"; shift ;;
    --canon-repo) CANON="${2:?}"; shift ;;
    --token-file) TOKEN_FILE="${2:?}"; shift ;;
    --chat-file) CHAT_FILE="${2:?}"; shift ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$INBOX" ] || { echo "digest-and-send: нет инбокса $INBOX"; exit 1; }
[ -f "$TOKEN_FILE" ] || { echo "digest-and-send: нет токена $TOKEN_FILE"; exit 1; }
[ -f "$CHAT_FILE" ] || { echo "digest-and-send: нет файла чата $CHAT_FILE"; exit 1; }

shopt -s nullglob
files=( "$INBOX"/*.tar.gz )
count=${#files[@]}
[ "$count" -eq 0 ] && exit 0     # тишина: присылать нечего

OUT_DIR="${OUT_DIR:-/opt/data/reports}"; mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/digest-$(date +%F).md"

bash "$HERE/skills-digest.sh" --inbox "$INBOX" --canon-repo "$CANON" --out "$OUT" || exit 1
[ -s "$OUT" ] || exit 0

TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"
CHAT="$(head -1 "$CHAT_FILE" | tr -d '[:space:]')"
THREAD="$(sed -n '2p' "$CHAT_FILE" | tr -d '[:space:]')"

proxy_args=(); [ -n "${TG_PROXY:-}" ] && proxy_args=(--proxy "$TG_PROXY")
thread_args=(); [ -n "$THREAD" ] && thread_args=(-F "message_thread_id=$THREAD")

curl -sS "${proxy_args[@]}" --max-time 120 \
  -F "chat_id=$CHAT" "${thread_args[@]}" \
  -F "caption=Дайджест скиллов сотрудников, $(date +%F)" \
  -F "document=@$OUT" \
  "${TG_API:-https://api.telegram.org}/bot$TOKEN/sendDocument" -o "${TMP_JSON:-/tmp/digest-send.json}" || {
    echo "digest-and-send: не удалось отправить (сеть/прокси)"; exit 1; }

if grep -qE '"ok"[[:space:]]*:[[:space:]]*true' "${TMP_JSON:-/tmp/digest-send.json}"; then
  echo "digest-and-send: дайджест отправлен ($count архивов) -> $OUT"
else
  echo "digest-and-send: Telegram ответил ошибкой: $(head -c 200 "${TMP_JSON:-/tmp/digest-send.json}")"; exit 1
fi
