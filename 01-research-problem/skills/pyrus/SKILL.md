---
name: pyrus
description: "Collect Pyrus form/registry tasks via direct REST."
---

# Pyrus: сбор задач и реестров форм

## Когда использовать
- Собрать задачи формы/реестра за период (запросы на доработку, инциденты, обращения и т.п.)
- Получить поля формы, задачи по ID, автора/статус/клиента

## Доступ — два канала

### 1. MCP-прокси (hermes.iiko.ru:8000/mcp) — удобен, но с багами
- Авторизация: заголовок `Authorization: Bearer ${PYRUS_TOKEN}` (из `$HERMES_HOME/.env`).
- Работают: `get_forms`, `get_form`, `get_task` (только для задач **без** файлов), `get_inbox`, `get_profile`, `list_accounts`.
- **БАГ**: `get_registry` падает с `Unable to serialize unknown type: File`, если хоть у одной задачи в выборке прикреплены файлы (поля «Файлы 1/2»). Весь вызов рушится, частичных данных нет.
- Прокси молча игнорирует любые доп. параметры: `fields`, `field_ids`, `format=csv`, `created_after/before`, `task_ids`, `sort`, `offset` — не пробрасывает их в SDK. Не тратить время на перебор имён параметров.
- Ответ `get_registry` нестандартный: **каждая задача — отдельный content-элемент** (не JSON-массив) — парсить нужно все content, не только `content[0]`.
- Обход для реестров: прямой REST (ниже).

### 2. Прямой REST API (api.pyrus.com/v4) — рабочий путь для реестров
- `PYRUS_TOKEN` из `.env` — это связка `login:security_key` (формат `email:JY75dKPY...`), **НЕ** Bearer-токен для api.pyrus.com (с ним будет `invalid_token`).
- Разделить по первому `:` → login, security_key.
- `POST /v4/auth` с `{"login": ..., "security_key": ...}` → `access_token` (JWT).
- Дальше — обычные Bearer-запросы.

## Реестр формы за период (главный рецепт)
```
POST https://api.pyrus.com/v4/forms/{form_id}/register
Authorization: Bearer <access_token>
{
  "created_after":  "2026-07-01T00:00:00Z",
  "created_before": "2026-08-01T00:00:00Z",
  "item_count": 2000,
  "include_archived": true
}
```
- Даты строго в формате `%Y-%m-%dT%H:%M:%SZ` (иначе SDK/API их не примет).
- `item_count` — до 20000.
- Ответ: `{"tasks": [{"id", "create_date", "last_modified_date", "current_step", "fields": [{"id","name","type","value"}]}]}`.
- Готовый скрипт: `scripts/pyrus_registry.py` (авторизация + выгрузка реестра в JSON).

## Форма «iiko — Запрос на доработку» (id 824016) — ключевые поля
Задача(1), Задача бизнеса(2), Как сейчас(4), Как должно быть(13), Повторяемость(3), Масштабность(12), Ценность(11), А то что(23), Модуль iiko(9), Продуктовые компоненты iiko(30), Приоритет для клиента(22), Партнер(35), Клиент(36), Статус(28), Автор(26), Дата создания(24), Номер задачи в Jira(17), Запланировано на версию(21), Срок(25), Файлы 1/2(10/20).

## Pitfalls
- `PYRUS_TOKEN` напрямую как Bearer на api.pyrus.com → `invalid_token`; как `security_key` без разбиения → `invalid_credentials`. Только split по `:` + `/v4/auth`.
- MCP `get_task` тоже падает на задачах с файлами (та же сериализация File) — файловые задачи читать только через прямой REST.
- Ошибка MCP-прокси `Unable to serialize unknown type: File` — серверная, с нашей стороны не чинится; это не повод отказываться от задачи, переключаться на REST.
