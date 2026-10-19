#!/bin/bash
# Перезапуск сервиса прототипа гипотез (Шаг 2).
# Нужен после правок server/serve.py — код читается один раз при старте.
#
#   bash install/hypoproto_restart.sh [--port 8330] [--host 0.0.0.0]
#
# Учитывает переменные HYPOPROTO_PORT / HYPOPROTO_HOST / HYPOPROTO_LOG / HYPOPROTO_AUTH_FILE.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STEP="${HYPOPROTO_STEP:-$(dirname "$HERE")}"
REPO="$(dirname "$STEP")"

# Настройки, записанные install.sh (порт/хост конкретной установки). Переменные окружения и --port важнее.
ENVFILE="${HYPOPROTO_ENV_FILE:-$STEP/.hypoproto/env}"
if [ -f "$ENVFILE" ]; then . "$ENVFILE"; fi
PORT="${HYPOPROTO_PORT:-${PORT:-8330}}"
HOST="${HYPOPROTO_HOST:-${HOST:-0.0.0.0}}"
LOG="${HYPOPROTO_LOG:-${LOG:-$STEP/.hypoproto/serve.log}}"
AUTHFILE="${HYPOPROTO_AUTH_FILE:-${AUTHFILE:-$STEP/.hypoproto-auth.txt}}"

while [ $# -gt 0 ]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        --host) HOST="$2"; shift 2 ;;
        *) echo "неизвестный аргумент: $1"; exit 2 ;;
    esac
done

# 1) остановить текущий процесс сервиса (ищем по аргументам командной строки)
for d in /proc/[0-9]*; do
    pid=${d#/proc/}
    [ "$pid" = "$$" ] && continue
    [ "$pid" = "$PPID" ] && continue
    cmd=$(tr '\0' ' ' < "$d/cmdline" 2>/dev/null) || continue
    case "$cmd" in
        *"serve.py --port $PORT"*) kill -TERM "$pid" 2>/dev/null && echo "остановлен процесс $pid" ;;
    esac
done
sleep 2

# 2) поднять заново
mkdir -p "$(dirname "$LOG")"
cd "$STEP" || { echo "ОШИБКА: нет каталога $STEP"; exit 1; }
ARGS=(--port "$PORT" --host "$HOST")
if [ -f "$AUTHFILE" ]; then
    ARGS+=(--auth "$(tr -d '\r\n' < "$AUTHFILE")")
fi
setsid python3 server/serve.py "${ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
sleep 2

CURL_AUTH=()
if [ -f "$AUTHFILE" ]; then
    CURL_AUTH=(-u "$(tr -d '\r\n' < "$AUTHFILE")")
fi
if curl -s -m 4 "${CURL_AUTH[@]}" "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
    echo "сервис прототипа гипотез перезапущен (порт ${PORT})"
else
    echo "ОШИБКА: сервис не поднялся, смотри ${LOG}"
    exit 1
fi
