# Как работать с репозиторием iiko-product-process

Канон — [iiko-product-process/iiko-product-process](https://github.com/iiko-product-process/iiko-product-process). Два назначения — два места:

- **`main`** — общее: скиллы по шагам, реестр `INDEX.md`, сквозной скилл `skills/task-workspace`. Единственный источник для команды. Артефактов задач здесь нет.
- **`personal`** — личное: все артефакты задач. В общей репе это только скелет (`tasks/README.md` + `tasks/_шаблон`); у тебя в форке — твоё личное пространство.

## 1. Первый раз: форк и клон

1. На GitHub открой репу и нажми **Fork** — создастся копия в твоём аккаунте (с обеими ветками `main` и `personal`).
2. Клонируй СВОЙ форк:

```bash
git clone https://github.com/<ты>/iiko-product-process.git
cd iiko-product-process
```

3. Добавь общую репу как `upstream` (откуда качать обновления):

```bash
git remote add upstream https://github.com/iiko-product-process/iiko-product-process.git
```

Теперь у тебя два адреса: `origin` — твой форк, `upstream` — общая репа.

## 2. Как обновлять свой main (личное не трогается)

```bash
git checkout main
git pull upstream main
```

Обновит только `main` (скиллы). Ветка `personal` не задета — все твои артефакты на месте.

## 3. Как вести личные задачи (ветка personal)

```bash
git checkout personal
cp -r tasks/_шаблон tasks/моя-задача     # завести новую задачу из шаблона
# ... пишешь артефакты в tasks/моя-задача ...
git add tasks/моя-задача
git commit -m "Задача: ..."
git push origin personal                  # бэкап в свой форк
```

Структура задачи: `01-проблема` → `02-гипотезы` → `03-требования` → `04-дизайн` → `05-спека` → `06-реализация` → `07-пилот` + `материалы`, `встречи`, `журнал.md`. Правила ведения — скилл `task-workspace`.

Ветку `personal` **никогда** не PR-им в общую репу — это личное.

## 4. Как предложить общий скилл (PR)

```bash
git checkout main
git pull upstream main                    # свежий main
git checkout -b feature/мой-скилл         # ветка от чистого main
# добавить скилл в папку шага + строку в INDEX.md
git add -A
git commit -m "Скилл <имя> (шаг N)"
git push -u origin feature/мой-скилл
```

На GitHub: **Compare & pull request** из своего форка → base `main`, head `feature/мой-скилл`.

## Правила

- PR — только из ветки `feature/*` (от чистого `main`), только в `main`.
- Ветка `personal` в общую репу не PR-ится никогда.
- Каждый новый общий скилл — **обязательно** строка в `INDEX.md`, иначе PR не мёржится.
- Мержит PR только админ.
- В `main` личных артефактов нет — личное только на `personal`.

## Где что лежит

| Место | Что |
|---|---|
| `main` | скиллы `step-N/…`, `skills/task-workspace`, `INDEX.md` |
| `personal` (у тебя в форке) | `tasks/_шаблон` и твои `tasks/<задача>/…` |
| `feature/*` | предложения в общее (живут до мерджа, потом удаляются) |
