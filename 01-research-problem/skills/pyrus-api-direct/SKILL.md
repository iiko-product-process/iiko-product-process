---
name: pyrus-api-direct
description: Use when collecting Pyrus tasks/registries via REST.
---

# Pyrus: прямой REST-доступ (обход бага MCP get_registry)

## Когда использовать
Любой сбор задач/реестров из Pyrus (iiko): «запросы на доработку», инциденты, задачи формы и т.п.
MCP-инструменты `mcp__pyrus__*` (hermes.iiko.ru:8000/mcp) работают для get_forms/get_form/get_task/get_inbox, **но `get_registry` падает** на задачах с прикреплёнными файлами:

```
Error executing tool get_registry: Unable to serialize unknown type: <class 'pyrus.models.entities.File'>
```

Прокси игнорирует `fields`/`field_ids`/`format=csv`/`created_after` (проверено через прямой JSON-RPC) — обойти через MCP нельзя. Прямой REST API решает всё.

## Ключевой факт
`PYRUS_TOKEN` в `$HERMES_HOME/.env` — это **связка `login:security_key`** (разделитель `:`), а не Bearer-токен:
```
pmalofeev@iikosoftware.com:JY75dKPY... (123 символа, login 39 + ':' + secret 83)
```
Для api.pyrus.com НЕ работает ни `Authorization: Bearer <PYRUS_TOKEN>` целиком, ни `POST /auth` с login=email + security_key=<PYRUS_TOKEN целиком>. Только после разделения по `:`.

## Шаги

### 1. Авторизация → access_token
```bash
TOKEN=$(grep -oP 'PYRUS_TOKEN=\K.*' $HERMES_HOME/.env | tr -d '\r\n')
LOGIN="${TOKEN%%:*}"      # часть до первого ':'
SECRET="${TOKEN#*:}"      # часть после первого ':'
curl -s -X POST "https://api.pyrus.com/v4/auth" -H "Content-Type: application/json" \
  -d "{\"login\":\"${LOGIN}\",\"security_key\":\"${SECRET}\"}"
# → {"access_token": "eyJhb..."} — его передавать как Authorization: Bearer
```

### 2. Реестр формы за период
```bash
curl -s -X POST "https://api.pyrus.com/v4/forms/824016/register" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"created_after":"2026-07-01T00:00:00Z","created_before":"2026-08-01T00:00:00Z",
       "item_count":1000,"include_archived":true}'
# → {"tasks":[{id, create_date, fields:[{id,name,type,value},...]}, ...]}
```
Параметры тела (FormRegisterRequest):
- `created_after` / `created_before` — ISO `%Y-%m-%dT%H:%M:%SZ`
- `item_count` — максимум задач (<=20000)
- `include_archived` — bool
- `field_ids` — список id полей, вернутся только они (защита от тяжёлых полей)
- `format: "csv"` — вернуть CSV-строку (ответ `{"csv": "..."}`)

Задачи реестра приходят **от свежих к старым**; `create_date` в формате `2026-07-30T15:34:08Z`.

### 3. Готовая Python-заготовка (проверена)
```python
import json, urllib.request, urllib.error
CRED = [l for l in open('$HERMES_HOME/.env') if l.startswith('PYRUS_TOKEN=')][0].split('=',1)[1].strip()
LOGIN, SECRET = CRED.split(':', 1)
API = 'https://api.pyrus.com/v4'
def req(url, method='GET', body=None, token=None, timeout=90):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'pyrus-api-client'}
    if token: headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
st, resp = req(f'{API}/auth', 'POST', {'login': LOGIN, 'security_key': SECRET})
TOKEN = resp['access_token']
st, resp = req(f'{API}/forms/824016/register', 'POST',
               {'created_after': '2026-07-01T00:00:00Z', 'created_before': '2026-08-01T00:00:00Z',
                'item_count': 1000, 'include_archived': True}, TOKEN)
tasks = resp.get('tasks', [])
```

## Полезные эндпоинты
- `POST /v4/auth` — получить access_token
- `GET /v4/forms` — список форм; `GET /v4/forms/{id}` — поля формы
- `POST /v4/forms/{id}/register` — реестр (см. выше)
- `GET /v4/tasks/{id}` — задача с полями и комментариями
- `GET /v4/inbox?item_count=N` — инбокс пользователя
- `GET /v4/calendar?...` — календарь (часто пуст, если у задач нет due_date)
- `GET /v4/lists` / `GET /v4/lists/{id}/tasks` — списки задач

## Грабли
1. **Не передавай PYRUS_TOKEN целиком** как Bearer или security_key — только после разделения по `:`.
2. **MCP get_registry бесполезен для полных реестров** — падает на File; не трать время на перебор параметров (fields/field_ids/format/steps/offset/sort — все игнорируются).
3. MCP-прокси сериализует каждую задачу отдельным content-элементом; при ошибке теряется весь ответ.
4. Токен доступа живёт недолго — для длинных выгрузок авторизуйся один раз и переиспользуй.
5. `get_task`/`get_registry` через MCP тоже падают на задачах с файлами — REST-ответ файлы отдаёт нормально (url/name/size).
6. Скрипты в `$HERMES_HOME/scripts/pyrus_*.py` — рабочие примеры (pyrus_direct.py, pyrus_save.py).

## Верификация
- AUTH: HTTP 200 + `access_token` непустой
- REGISTRY: HTTP 200 + `tasks` список; сверь `create_date` попадают в запрошенный диапазон
- Количество задач из REST = полное (в отличие от MCP, где limit=3 уже падает)
