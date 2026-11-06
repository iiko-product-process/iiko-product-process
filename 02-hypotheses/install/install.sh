#!/bin/bash
# Установка сервиса прототипа гипотез (Шаг 2) на сервер сотрудника.
#
#   bash install/install.sh [--port 8330] [--host 0.0.0.0] [--auth логин:пароль] [--no-cron]
#
# Что делает:
#   1. проверяет зависимости (python3 ≥ 3.8, curl; git — если нужна история изменений);
#   2. создаёт каталоги для логов и файл авторизации (если задан --auth);
#   3. ставит в cron автоподъём сервиса (каждые 15 минут + при загрузке), если не указан --no-cron;
#   4. поднимает сервис и проверяет, что он отвечает;
#   5. печатает ссылку для сотрудника и что осталось сделать (открыть порт, раздать доступ).
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STEP="${HYPOPROTO_STEP:-$(dirname "$HERE")}"
REPO="$(dirname "$STEP")"

PORT="${HYPOPROTO_PORT:-8330}"
HOST="0.0.0.0"
AUTH=""
NO_CRON=0
while [ $# -gt 0 ]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        --host) HOST="$2"; shift 2 ;;
        --auth) AUTH="$2"; shift 2 ;;
        --no-cron) NO_CRON=1; shift ;;
        *) echo "неизвестный аргумент: $1"; exit 2 ;;
    esac
done

echo "== установка сервиса прототипа гипотез (шаг 2) =="
echo "каталог шага:   $STEP"
echo "репозиторий:    $REPO"
echo "порт:           $PORT"
echo

# 1) зависимости
if ! command -v python3 >/dev/null 2>&1; then
    echo "ОШИБКА: нет python3. Поставь python 3.8+ и повтори."; exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "ОШИБКА: нужен python 3.8+, сейчас $(python3 -V 2>&1)."; exit 1
fi
command -v curl >/dev/null 2>&1 || echo "ВНИМАНИЕ: нет curl — проверка здоровья сервиса не сработает."
if [ -d "$REPO/.git" ]; then
    command -v git >/dev/null 2>&1 || echo "ВНИМАНИЕ: нет git — история изменений вестись не будет."
else
    echo "ПРИМЕЧАНИЕ: это не git-репозиторий — списки будут храниться локально без истории."
fi

# 2) данные и каталоги
mkdir -p "$STEP/data/lists" "$STEP/data/problems" "$STEP/.hypoproto"
if [ ! -f "$STEP/data/lists/obshiy-spisok.json" ]; then
    cat > "$STEP/data/lists/obshiy-spisok.json" <<'JSON'
{
 "list": {"id": "obshiy-spisok", "title": "Общий список гипотез", "type": "general", "problem": null,
          "created": "", "updated": ""},
 "goals": [
  {"id": "ns",  "name": "North Star 2027", "g": 2.0,  "kind": "reference"},
  {"id": "g32", "name": "Годовая: цифровизация процессов, +20% критичных", "g": 1.7, "kind": "reference"},
  {"id": "q",   "name": "Квартальная: OKR продукта", "g": 1.4, "kind": "reference"},
  {"id": "sup", "name": "Поддерживающие задачи", "g": 1.0, "kind": "reference"},
  {"id": "bg",  "name": "Эксперименты и фон", "g": 0.8, "kind": "reference"},
  {"id": "must","name": "Обязательное (вне рейтинга)", "g": 0.0, "kind": "reference"}
 ],
 "items": []
}
JSON
    echo "создан пустой общий список: data/lists/obshiy-spisok.json"
fi

# 3) авторизация
if [ -n "$AUTH" ]; then
    printf '%s\n' "$AUTH" > "$STEP/.hypoproto-auth.txt"
    chmod 600 "$STEP/.hypoproto-auth.txt"
    echo "включена HTTP Basic авторизация (файл $STEP/.hypoproto-auth.txt, в git не попадает)"
fi

# 3a) настройки установки: чтобы watchdog и restart знали порт и хост
printf 'PORT=%s\nHOST=%s\n' "$PORT" "$HOST" > "$STEP/.hypoproto/env"
echo "настройки установки записаны: $STEP/.hypoproto/env (PORT=$PORT, HOST=$HOST)"

# 4) автоподъём
if [ "$NO_CRON" = "0" ]; then
    if command -v crontab >/dev/null 2>&1; then
        ENSURE_LINE_15="*/15 * * * * HYPOPROTO_PORT=$PORT bash $HERE/hypoproto_ensure.sh"
        ENSURE_LINE_BOOT="@reboot HYPOPROTO_PORT=$PORT bash $HERE/hypoproto_ensure.sh"
        ( crontab -l 2>/dev/null | grep -v 'hypoproto_ensure.sh'
          echo "$ENSURE_LINE_15"
          echo "$ENSURE_LINE_BOOT" ) | crontab -
        echo "в cron добавлен автоподъём сервиса: каждые 15 минут и при загрузке"
    else
        echo "ВНИМАНИЕ: нет crontab — настрой автозапуск вручную (пример unit для systemd — в install/README.md)"
    fi
else
    echo "автоподъём в cron не ставился (--no-cron)"
fi

# 5) запуск и проверка
echo
HYPOPROTO_PORT="$PORT" HYPOPROTO_HOST="$HOST" bash "$HERE/hypoproto_restart.sh" || true
CURL_AUTH=()
[ -f "$STEP/.hypoproto-auth.txt" ] && CURL_AUTH=(-u "$(tr -d '\r\n' < "$STEP/.hypoproto-auth.txt")")
if curl -s -m 4 "${CURL_AUTH[@]}" "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
    IP=$(hostname -I 2>/dev/null | awk '{print $1}')
    [ -z "$IP" ] && IP=$(hostname 2>/dev/null || echo "<адрес-сервера>")
    echo
    echo "готово. Ссылка для сотрудника:"
    echo "    http://${IP}:${PORT}/?list=obshiy-spisok"
    echo
    echo "дальше:"
    echo "  1) открой порт ${PORT} в firewall / пробрось его (если сервис нужен не только с этого хоста);"
    if [ -z "$AUTH" ]; then
        echo "  2) доступ сейчас без пароля: включить — удалить сервис и запустить install.sh с --auth логин:пароль"
        echo "     (или создать файл $STEP/.hypoproto-auth.txt и выполнить install/hypoproto_restart.sh)";
    else
        echo "  2) авторизация включена — логин и пароль передай сотруднику отдельно;"
    fi
    echo "  3) проверь по чек-листу в install/README.md (сохранение, меню списков, коммит в git)."
else
    echo "ОШИБКА: сервис не отвечает. Смотри лог $STEP/.hypoproto/serve.log и раздел «Диагностика» в install/README.md."
    exit 1
fi
