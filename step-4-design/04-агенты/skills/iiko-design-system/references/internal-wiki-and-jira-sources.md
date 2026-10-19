# Внутренние источники iiko: вики (Confluence) и Jira

Когда задача приходит ссылкой вида `https://wiki.iiko.ru/spaces/PDM/pages/<id>/<Title>` либо на
`jira.iiko.ru`. Проверено 15.09.2026 (страница PDM «Web KDS», pageId 112952652).

## Порядок: сначала проверить доступ, потом просить

1. **Что уже настроено у агента** — `config.yaml` (секция `mcp`), любые файлы с `mcpServers`,
   **имена** ключей в `%LOCALAPPDATA%\hermes\.env` (значения не печатать), `desktop-plugins/`.
   На 15.09.2026: MCP-серверов нет, в `.env` только `DEEPSEEK_API_KEY` и служебные переменные,
   из плагинов — только Figma-плагины ДС (`iiko-ds-plugin-v2`, `Tasks`). Докладывать это фактами,
   а не «доступа нет». Владелец спрашивает «Разве у гермеса нет доступа к Jira и Wiki iiko?»,
   если просьбу о токене выдать раньше проверки.
2. **Страница вообще есть, или это не та ошибка?** Логин и 404 выглядят по-разному:

   ```bash
   curl -s -m 20 -I "https://wiki.iiko.ru/spaces/PDM/pages/<id>/<Title>" | head -20
   # 302 + location: /login.action?…permissionViolation=true  → страница есть, нужна сессия
   curl -s -m 20 -o /dev/null -w "%{http_code}\n" \
     "https://wiki.iiko.ru/rest/api/content/<id>?expand=body.storage,title"   # → 401 без токена
   ```

3. **Версия Confluence без логина** — от неё зависит, возможен ли личный токен:

   ```bash
   curl -s -m 25 -L "https://wiki.iiko.ru/login.action" \
     | grep -o -E 'ajs-version-number" content="[0-9.]+"'
   # 15.09.2026 → 9.2.2 (Personal Access Tokens поддерживаются с 7.9)
   curl -s -m 25 "https://jira.iiko.ru/rest/api/2/serverInfo"   # анонимно: 401 + пустой JSON
   ```

## Способы доступа — предлагать по одному, коротко

- **Personal Access Token** (рекомендуемый): Confluence → аватар → Settings → Personal Access Tokens;
  Jira → Profile → Personal Access Tokens; для чтения хватает scope `read`. Просить положить токен
  **файлом вне репозитория** (`C:\Users\asukharev\.iiko_pat`), в чат токен не просить.
  Чтение после этого:
  `curl -s -H "Authorization: Bearer $(cat ~/.iiko_pat)" "https://wiki.iiko.ru/rest/api/content/<id>?expand=body.storage,title"`
  → тело страницы в `body.storage` (XHTML; для разбора снимать текст, теги Confluence выкидывать).
- **Сессия браузера**: браузер, которым управляет агент, должен быть залогинен в вики. Требует
  действий владельца — в Chrome `chrome://inspect/#remote-debugging` галочка «Allow remote debugging
  for this browser instance», и при подключении будет **ещё один** Allow (это норма, предупредить заранее).
- **Экспорт страницы** (Ctrl+S / PDF-Word) на Рабочий стол — когда токен выдать нельзя.

## Капканы

- `web_extract` на внутренние адреса отвечает `Blocked: URL targets a private or internal network
  address` — это не «страницы нет» и не причина останавливаться: внутренние хосты брать `curl`
  в терминале либо браузером.
- Код для `browser_exec` писать **только латиницей**: комментарий на кириллице роняет запуск
  (`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xce`) и выглядит как поломка инструмента.
- Ссылку на вики в ACP **не кликать** (клики по ссылкам не работают) и не открывать вкладки
  владельца самому: адрес — текстом, доступ — токеном файлом или разрешением на браузер.
- Токен/пароль в чат не просить: только файл вне репозитория (в `DS` и рядом с ним ничего не класть
  — это git-дерево с публичным `iiko-ds-web`).
