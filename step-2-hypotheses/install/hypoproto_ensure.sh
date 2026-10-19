#!/bin/bash
# Держит сервис прототипа гипотез (Шаг 2) запущенным и коммитит правки списков, сделанные не через сервис.
#
# Тихий, когда всё в порядке: пустой вывод = ок (удобно для cron: пустой stdout = ничего не отправили).
# Пишет только если поднял сервис заново или не смог.
#
# Пути выводятся из расположения скрипта (install/ внутри step-2-hypotheses), можно переопределить:
#   HYPOPROTO_PORT      порт сервиса (по умолчанию 8330)
#   HYPOPROTO_HOST      адрес прослушивания (по умолчанию 0.0.0.0)
#   HYPOPROTO_LOG       лог сервиса (по умолчанию <репозиторий>/.hypoproto/serve.log)
#   HYPOPROTO_AUTH_FILE файл с «логин:пароль» для HTTP Basic (по умолчанию <репозиторий>/.hypoproto-auth.txt)
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STEP="${HYPOPROTO_STEP:-$(dirname "$HERE")}"
REPO="$(dirname "$STEP")"

# Настройки, записанные install.sh (порт/хост конкретной установки). Переменные окружения важнее файла.
ENVFILE="${HYPOPROTO_ENV_FILE:-$STEP/.hypoproto/env}"
if [ -f "$ENVFILE" ]; then . "$ENVFILE"; fi
PORT="${HYPOPROTO_PORT:-${PORT:-8330}}"
HOST="${HYPOPROTO_HOST:-${HOST:-0.0.0.0}}"
LOG="${HYPOPROTO_LOG:-${LOG:-$STEP/.hypoproto/serve.log}}"
AUTHFILE="${HYPOPROTO_AUTH_FILE:-${AUTHFILE:-$STEP/.hypoproto-auth.txt}}"

# сервис может требовать HTTP Basic — тогда проверяем с теми же учётными данными
CURL_AUTH=()
if [ -f "$AUTHFILE" ]; then
    CURL_AUTH=(-u "$(tr -d '\r\n' < "$AUTHFILE")")
fi

# 1) сервис: если не отвечает — поднимаем
if ! curl -s -m 3 "${CURL_AUTH[@]}" "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
    mkdir -p "$(dirname "$LOG")"
    cd "$STEP" || { echo "ОШИБКА: нет каталога $STEP"; exit 1; }
    ARGS=(--port "$PORT" --host "$HOST")
    if [ -f "$AUTHFILE" ]; then
        ARGS+=(--auth "$(tr -d '\r\n' < "$AUTHFILE")")
    fi
    setsid python3 server/serve.py "${ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
    sleep 2
    if curl -s -m 3 "${CURL_AUTH[@]}" "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
        echo "Сервис прототипа гипотез был не запущен — поднял заново (порт ${PORT}). Лог: ${LOG}"
    else
        echo "ОШИБКА: сервис прототипа гипотез не поднимается, смотри ${LOG}"
        exit 1
    fi
fi

# 2) страховка: коммитим правки списков, сделанные не через сервис
#    (например, если папку данных правили вручную или из другой копии прототипа)
if [ -d "$REPO/.git" ]; then
    cd "$REPO" 2>/dev/null || exit 0
    if [ -n "$(git status --porcelain -- step-2-hypotheses/data 2>/dev/null)" ]; then
        python3 step-2-hypotheses/scripts/aggregate.py >/dev/null 2>&1 || true
        git add step-2-hypotheses/data >/dev/null 2>&1 || true
        git commit -q -m "Правки списков гипотез из прототипа ($(date '+%d.%m.%Y %H:%M'))" >/dev/null 2>&1 || true
        if ! git push -q origin main >/dev/null 2>&1; then
            echo "Правки списков закоммичены локально, но пуш в remote не прошёл — проверь доступ к репозиторию (токен/права)."
        fi
    fi
fi
