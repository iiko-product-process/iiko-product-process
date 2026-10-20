# Нет доступа к канону при живом токене

Порядок разбора — сверху вниз, каждая команда печатает только факт:

```bash
# 1. токен жив и какие у него скоупы (печатаются только заголовки)
curl -s -o /dev/null -D - -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user \
  | grep -iE '^HTTP/|x-oauth-scopes'

# 2. под кем работаем
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])"

# 3. членство в организациях
curl -s -H "Authorization: token $GITHUB_TOKEN" 'https://api.github.com/user/orgs?per_page=100' \
  | python3 -c "import sys,json; print([o['login'] for o in json.load(sys.stdin)])"

# 4. непринятые приглашения (организации и репозитории)
curl -s -H "Authorization: token $GITHUB_TOKEN" 'https://api.github.com/user/memberships/orgs?state=pending'
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/repository_invitations

# 5. виден ли канон
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/iiko-product-process/iiko-product-process
```

| Что показали | Вывод | Действие |
|---|---|---|
| `/user` → 401 | токен протух или скопирован с обрезанием | перевыпустить PAT |
| скоупы без `repo` | токен не даёт доступа к приватным репозиториям | перевыпустить со `repo`, `read:org` |
| в `/user/orgs` нет `iiko-product-process`, приглашений 0 | приглашение не выдано | просить админа организации: роль `read` |
| приглашение есть в `memberships/orgs?state=pending` | не принято | принять в GitHub → Settings → Organizations |
| канон → 200 | доступ есть | переходить к форку и клону |

Организация может существовать публично (`/orgs/<org>` → 200) при нуле публичных репозиториев:
это ничего не говорит о доступе — решает только проверка под токеном.

# Типовые проблемы git

| Симптом | Причина | Что делать |
|---|---|---|
| `401 Bad credentials` | токен неверный, протух или не экспортирован | `export GITHUB_TOKEN=…`, проверить `x-oauth-scopes` |
| `403 Write access to repository not granted` | push в канон (роль read) или токен без `repo` | пушить в свой форк, проверить скоупы |
| `Permission denied (publickey)` | SSH-ключ не добавлен в GitHub | `ssh -T git@github.com`, добавить `id_ed25519.pub` |
| `Push rejected (fetch first)` | в каноне появились новые коммиты | `git fetch upstream && git rebase upstream/main` |
| `Need to specify how to reconcile divergent branches` | ветка разошлась с форком | `git pull --rebase` или явный merge |
| форк не создаётся | уже есть репозиторий с таким именем | переименовать свой старый, затем форкнуть |
| `Cannot assign … permission of read` | попытка выдать read в репозитории личного аккаунта | read возможен только в организации |
| `.hermes.md` создан, но правила не работают | файл не в корне git-репозитория | положить в корень клона, проверить `pwd` |
| правила `AGENTS.md` перестали действовать | рядом появился `.hermes.md`: первый источник выигрывает | удалить `.hermes.md`, нужное перенести в `AGENTS.md` |
| «в `personal` видны все папки» | в форке `personal` — это канон + артефакты, а не только `tasks/` | это норма: шаблон задачи в `tasks/`, скиллы в `main` |

# Итоговое сообщение сотруднику

> Подключение готово: доступ к организации есть, форк `<логин>/iiko-product-process` создан,
> клон настроен (`origin` — форк, `upstream` — канон), identity задан, ветка `personal` на месте.
> Правила для Гермеса — канонный `.hermes.md`.
> MCP: `<что подключено / что отложено>`.
> В репозитории 7 шагов процесса и 22 скилла — от валидации проблемы до сопровождения разработки.
> Дальше: `<подключить Matomo / завести папку задачи по вашей теме>`. Что выбираем?
