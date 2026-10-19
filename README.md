# Продуктовый процесс iiko

Канон: **https://github.com/iiko-product-process/iiko-product-process** (private, организация `iiko-product-process`).

Репозиторий продуктового процесса iiko web: скиллы по шагам, реестр скиллов, шаблон задачи и правила работы.

## Что внутри

| Папка | К чему относится |
|---|---|
| `step-1-problem/` | Шаг 1 — проблема: формулировка, валидация, исследование, рынок, данные |
| `step-2-hypotheses/` | Шаг 2 — гипотезы, приоритизация, ICE |
| `step-3-pb-task-writer/` | Шаг 3 — задача в Jira PB |
| `step-4-design/` | Шаг 4 — дизайн, прототипы, гайды |
| `step-5-specification/` | Шаг 5 — спецификация (PRD) |
| `step-6-development/` | Шаг 6 — разработка: выгрузка задач Jira, актуализация требований |
| `tasks/` | `_шаблон` задачи и скилл `task-workspace` |
| `INDEX.md` | Реестр всех скиллов процесса: на каждый скилл обязательна строка |
| `CONTRIBUTING.md` | Процесс работы: форк → ветка → PR |

## Две ветки

| Ветка | Назначение | Что лежит |
|---|---|---|
| `main` | Общее, единственный источник для команды | Скиллы `step-N/…`, `INDEX.md`, `tasks/_шаблон`, `tasks/skill` |
| `personal` | Личное пространство сотрудника | Только скелет: `tasks/README.md` и `tasks/_шаблон`; в форке — артефакты задач |

## Как начать

1. **Fork** канона в свой аккаунт — доступ выдан только на чтение, форк разрешён.
2. Клонируй свой форк и подключи канон как `upstream`:

```bash
git clone https://github.com/<ты>/iiko-product-process.git
cd iiko-product-process
git remote add upstream https://github.com/iiko-product-process/iiko-product-process.git
```

3. Обновляй общее: `git checkout main && git pull upstream main`.
4. Личные задачи веди на ветке `personal` — она не PR-ится никогда.
5. Предложить общий скилл — ветка `feature/*` от чистого `main` → PR в `main` канона, мержит админ.

Полный процесс — [CONTRIBUTING.md](CONTRIBUTING.md). Реестр скиллов — [INDEX.md](INDEX.md).

## История

Снимок-объединение двух процессных репозиториев (`iiko-product-process-main` + `iiko-product-process`) от 19.10.2026: общее вынесено в `main`, личные папки задач — в `personal`. Тогда же репозиторий перенесён в организацию `iiko-product-process`: участники получают доступ только на чтение и работают через форки.
