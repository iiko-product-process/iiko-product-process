---
name: notes-vault-setup
description: "Use to install the notes vault (Obsidian+GitHub+Hermes)."
version: 1.0.0
author: Hermes Agent (iiko)
license: MIT
metadata:
  hermes:
    tags: [notes, obsidian, github, setup, fts5, telegram]
---

# Установка системы заметок: Hermes ↔ GitHub ↔ Obsidian

Скилл-установщик. Загрузи его в Hermes и скажи агенту «установи по этому скиллу» — он развернёт всю систему: папку заметок, скрипты индекса/поиска/раскладки, три рабочих скилла, приватный репозиторий на GitHub и синк с Obsidian на Mac.

## Что получится в итоге

1. **Vault** `$HERMES_HOME/notes` (по умолчанию `$HERMES_HOME/notes`) — `.md`-заметки в Obsidian-совместимом формате, одновременно git-репозиторий.
2. **Скрипты** в `notes/.index/`:
   - `notes_classify.py` — раскладывает заметки по папкам `Категория/Тема/` на основе frontmatter;
   - `notes_index.py` — пересборка FTS5-индекса + `index.md` (оглавление) + авто-коммит и авто-push в GitHub;
   - `notes_search.py` — быстрый поиск по базе, отдаёт только сниппеты (экономия токенов).
3. **Три скилла Hermes** (тексты — Приложение A): `notes-inbox` (приём заметок из чата), `notes-search` (поиск по базе), `obsidian` (файловые операции с vault).
4. **Приватный репозиторий GitHub** — источник истины; сервер пушит, Mac тянет.
5. **Obsidian на Mac** — vault открыт локально, синхронизация через плагин Obsidian Git.

Поток данных: `Telegram-топик → Hermes (скилл notes-inbox) → .md в vault → classify → index+commit+push → GitHub → Mac (Obsidian)` и обратно: `правки в Obsidian → плагин Git → push → сервер делает pull перед поиском`.

---

## 0. Предпосылки (проверь перед началом)

- Hermes Agent в контейнере/на сервере, доступны инструменты `terminal`, `file`, `skills` (`HERMES_HOME` обычно `$HERMES_HOME`).
- `python3` ≥ 3.8 со **SQLite с FTS5** и `git`. Проверка:
  ```bash
  python3 -c "import sqlite3;print([r[0] for r in sqlite3.connect(':memory:').execute('pragma compile_options') if 'FTS5' in r[0]])"
  git --version
  ```
  Если FTS5 пусто — поставь sqlite3 с FTS5 (`apt-get install -y sqlite3 libsqlite3-dev` и/или Python из дистрибутива с libsqlite3, где FTS5 включён).
- Аккаунт GitHub (для приватного репозитория) + Mac с установленным Obsidian.
- Опционально: Telegram-топик «📝 Заметки» в рабочей группе, куда бот принимает заметки.

Дальше `$V` = `$HERMES_HOME/notes`.

## 1. Скелет vault

```bash
mkdir -p "$V"/{.index,raw}
cat > "$V/.gitignore" <<'EOF'
/raw/
/.index/
.DS_Store
EOF
```
`raw/` — оригиналы присланных файлов (docx/xlsx/pptx/скрины), `.index/` — SQLite-индекс и скрипты. **Обе папки в git не попадают** (не нужны на Mac, могут содержать тяжёлое/чувствительное).

## 2. Скрипты

Создай три файла (полный код — **Приложение B**), затем `chmod +x`:
```bash
chmod +x "$V/.index/"*.py
python3 "$V/.index/notes_index.py"      # smoke-test: должен создать .index/notes.db и index.md
```

## 3. Скиллы-компаньоны

Создай три скилла через `skill_manage(action='create')` (или положи SKILL.md руками в `$HERMES_HOME/skills/note-taking/<имя>/SKILL.md`). Тексты — **Приложение A**, дублировать/переписывать не нужно, копируй как есть:
- `notes-inbox` — триггер: пользователь кинул заметку/файл/расшифровку;
- `notes-search` — триггер: вопрос по прошлым заметкам («что решили по X?»);
- `obsidian` — файловые операции с vault.

## 4. GitHub (обязательный шаг для синка с Mac)

### 4.1 Токен
- **Fine-grained PAT**: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate.
  - Repository access: **Only select repositories** → репозиторий заметок (или создать его тут же).
  - Permissions: **Contents → Read and write** (Metadata: Read-only подставляется автоматически).
  - Expiration: по политике компании (ставь напоминание о продлении — иначе push молча отвалится).
- Либо **classic token** со scope `repo` (проще, но доступ шире).

### 4.2 Репозиторий
Создай **приватный** пустой репозиторий (без README/.gitignore), например `notes-obsidian`.

### 4.3 Секрет
```bash
grep -q '^GITHUB_TOKEN=' "$HERMES_HOME/.env" || echo 'GITHUB_TOKEN=<токен>' >> "$HERMES_HOME/.env"
chmod 600 "$HERMES_HOME/.env"
```
`.env` лежит **вне** vault — в git не попадёт.

### 4.4 Инициализация и первый push (в контейнере)
```bash
cd "$V"
git init -b main
git config user.name  "Hermes Notes"
git config user.email "hermes@<домен>"
git add -A && git commit -qm "notes: инициализация"
git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/<USER>/<REPO>.git"
git push -u origin main
git ls-remote origin >/dev/null && echo "GitHub OK"
```
**Про токен в URL:** в контейнере нет `gh` CLI и кред-хелпера, поэтому токен «зашит» в remote — так молчаливо работают cron-джобы. Токен |виден в `git remote -v` — не пересылай вывод и не коммить. Смена токена:
```bash
git remote set-url origin "https://x-access-token:<НОВЫЙ_ТОКЕН>@github.com/<USER>/<REPO>.git"
```
Проверь, что `.env` недоступен изнутри vault: `git -C "$V" check-ignore -v ../.env` не нужен — просто не копируй его в vault.

### 4.5 (альтернатива) gh CLI
Если `gh` доступен: `gh auth login` → `gh repo create notes-obsidian --private --source="$V" --push`. В большинстве контейнеров образов Hermes `gh` нет — тогда вариант из 4.4.

## 5. Obsidian на Mac

1. Склонируй репозиторий (без токена в URL — Git Credential Manager/логин GitHub сам подставит доступ):
   ```bash
   git clone https://github.com/<USER>/<REPO>.git ~/Documents/notes-obsidian
   ```
   (или GitHub Desktop → Clone repository)
2. Obsidian → **Open folder as vault** → выбрать `~/Documents/notes-obsidian`.
3. Settings → Community plugins → Browse → установить **Obsidian Git** (автор Vinzent) → включить.
4. В настройках приложения **Obsidian Git** («Obsidian Git» в разделе Community plugins → Options):
   - *Auto backup after stopping editing* — **ON**
   - *Auto backup interval* — 5–10 минут
   - *Pull on startup* — **ON**
   - *Push on backup* — **ON**
   - *Author name / Author email* — ваши (иначе плагин подставит дефолт)
5. Проверка: создать тестовую заметку в Obsidian → дождаться коммита (статус-бар плагина) → на сервере `git -C "$V" pull --ff-only` → файл появился. Обратно: заметка, созданная ботом → на Mac сделать Pull.

Правила совместной работы: **источник истины — сервер**; на Mac перед правками Pull on startup, после — push. Конфликты разруливаются обычным git (на Mac `git pull --rebase`).

## 6. Проверка установки (чек-лист)

- [ ] `python3 "$V/.index/notes_index.py"` → «индекс обновлён: N заметок» и первая запись в `git log`
- [ ] `python3 "$V/.index/notes_classify.py"` → «перемещено заметок: 0» (на пустой базе)
- [ ] `python3 "$V/.index/notes_search.py" "тест"` → находит созданную вручную заметку
- [ ] `git -C "$V" ls-remote origin` → OK
- [ ] Заметка, положенная ботом через топик, появилась в vault, ответ бота — `✅ Заметка: «…» · Категория/Тема · путь`
- [ ] На Mac `git pull` видит эту заметку; правка в Obsidian уезжает в GitHub (и подтягивается на сервере)

## 7. Правила ведения базы (то, на что опираются скиллы)

- Frontmatter каждой заметки:
  ```yaml
  ---
  title: Краткое название
  date: ГГГГ-ММ-ДД
  kind: заметка          # заметка | договорённость | транскрибация | встреча | идея | файл
  category: Заметки      # папка (см. таблицу)
  topic: маркетплейс     # опционально: тема/проект/человек → подпапка
  tags: [тег1, тег2]
  source: telegram
  ---
  ```
- Раскладка по `kind` (таблица в скилле `notes-inbox`): договорённость → `Договорённости`, транскрибация → `Транскрибации`, встреча → `Встречи`, идея → `Идеи`, заметка → `Заметки`, файл/неясно → `Прочее`. Папки создаёт `notes_classify.py`, **вручную их не строят**.
- **Договорённости** обязаны иметь секцию `## Решения` со строками
  `- [ ] Ответственный: … · Срок: ГГГГ-ММ-ДД · Суть: …` — по ним ищется «что на ком висит».
- **Транскрибации** — структура по темам + таймкоды + финальная секция «Суть и решения».
- Связи между заметками — Obsidian-вики-ссылки `[[Транскрибации/2026-09-07_…]]`.
- Порядок после сохранения заметки: `notes_classify.py` → `notes_index.py` (он же коммитит и пушит) → короткий ответ пользователю строкой.

## Pitfalls

- **NFD-имена (macOS).** Файлы из desktop-вложений приходят в Unicode-нормализации NFD: поиск по NFC-имени не находит файл. Ищи через `unicodedata.normalize('NFC', name)`.
- **`read_file` может счесть валидный UTF-8 файл «бинарным»** (плотный не-ASCII текст, длинные расшифровки). Читай через `terminal` python-ом кусками: `print(open(path, encoding='utf-8').read()[21000:42000])`.
- **DOCX без текста через `read_file`**: извлекай `zipfile.ZipFile(f).read('word/document.xml')` → параграфы `<w:p …>` → склейка `<w:t>` (проверь ещё `word/footnotes.xml`, `header*/footer*`).
- **`notes_index.py` делает commit+push сам.** Не запускай его, если в vault лежат секреты; ошибки push (нет сети) не фатальны — повторятся при следующем запуске.
- **Не читай всю базу.** Сначала `index.md`, потом FTS-поиск, только затем 1–3 файла.
- **Токен в remote URL** — виден в `git remote -v`; при утечке отозвать в GitHub и заменить `git remote set-url`. Имя репозитория/токен не светить в чатах.
- **Часовые пояса:** `date` в заметках — локальная дата пользователя (МСК), cron живёт в UTC.
- **`.index/` и `raw/` не синкаются на Mac** (в `.gitignore`) — это норма: поиск работает на сервере, оригиналы остаются на сервере.
- **Тема (`topic`) не угадывается скриптом** — её ставит агент из смысла заметки, иначе заметка ляжет в корень категории.

---

## Приложение A — тексты скиллов-компаньонов

### A1. `notes-inbox`

```markdown
---
name: notes-inbox
description: "Use when user drops a note or file into the notes topic."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [notes, inbox, telegram, obsidian, markdown]
---

# Входящие заметки → Markdown-база

Пользователь кидает в топик «Заметки» (или просит сохранить заметку/договорённость/транскрибацию) текст или файл.
Задача: конвертировать в аккуратный .md и сохранить в базу **$V** (Obsidian-совместимая, корень = vault).

## Формат файла

```markdown
---
title: Краткое название
date: ГГГГ-ММ-ДД
kind: заметка            # заметка | договорённость | транскрибация | встреча | идея | файл
category: Категория      # см. таблицу раскладки
topic: Тема              # опционально: короткая тема/проект/человек → подпапка
tags: [тег1, тег2]
source: telegram
---
```

## Раскладка по смыслу (категоризация)

Структура должна РАЗВИВАТЬСЯ САМА. Каждая заметка раскладывается по категории и теме:

| kind | category (папка) |
|---|---|
| транскрибация | `Транскрибации` |
| договорённость | `Договорённости` |
| встреча | `Встречи` |
| идея | `Идеи` |
| заметка | `Заметки` |
| файл / неясно | `Прочее` |

- `topic` — определяешь из содержания: имя/проект/направление (например `Руслан`, `маркетплейс`). Файл ложится в `Категория/Тема/`. Если темы нет — в корень категории.
- Папку создаёт скрипт `notes_classify.py` — **не строй папки вручную**.

Правила:
- slug — транслит или короткое осмысленное имя (латиница/дефисы).
- Для **договорённостей** обязательна секция `## Решения` с буллетами
  `- [ ] Ответственный: … · Срок: ГГГГ-ММ-ДД · Суть: …` — по ней ищут «что на ком висит».
- Для **транскрибаций** — таймкоды и реплики спикеров, если различимы; в конце секция «Суть и решения».
- Связывай с похожими заметками вики-ссылками `[[…]]` (Obsidian).
- Русский текст сохраняется как есть (UTF-8).

## Конвертация файлов

| Вход | Действие |
|---|---|
| текст в сообщении | тело заметки (выдели главное, структурируй заголовками) |
| .md / .txt | нормализовать + frontmatter |
| PDF / docx / xlsx / pptx | извлечь текст (навыки pdf/docx/xlsx/powerpoint/ocr-and-documents), переложить в md; при сложной вёрстке — сохранить и оригинал |
| фото (скрин/доска) | распознать текст vision-моделью; если нечитаемо — сохранить файл в raw/ и честно сказать |
| голосовые | транскрибация пока НЕ настроена: сообщи, предложи записать текстом |
| ссылка на видео встречи | youtube-content, если доступно |

Оригиналы файлов (не-md) сохраняй в `raw/` (`raw/{ГГГГ-ММ-ДД}_{имя}`) — для сверки.

## После сохранения

1. `python3 $V/.index/notes_classify.py` — раскладка по kind/category/topic.
2. `python3 $V/.index/notes_index.py` — FTS5 + index.md, он же коммитит и пушит.
3. Ответь КОРОТКО, одной строкой: `✅ Заметка: «{title}» · {category}/{topic?} · {путь}`.

## Pitfalls

- Приём вложений ботом проверен — если файл не пришёл/битый, попроси переслать.
- **NFD-имена (macOS):** поиск по NFC-имени не находит файл — ищи через `unicodedata.normalize('NFC', n)`.
- **`read_file` пишет «Binary file»** — читай текст через `terminal` python-ом.
- Не сохраняй служебный текст переписки — только саму заметку/договорённость.
- Не придумывай содержание; неоднозначности уточняй одним вопросом.
- Если контента мало (пустое сообщение/непонятный файл) — переспроси, что сохранить.
```

### A2. `notes-search`

```markdown
---
name: notes-search
description: "Use to search the user notes vault fast and token-cheap."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [notes, search, fts5, obsidian]
---

# Поиск по базе заметок (дешёвый по токенам)

Пользователь спрашивает то, что может лежать в его заметках («что решили по X?», «когда встреча?»).
База: **$V**. Поиск — индексами, БЕЗ чтения всех файлов.

## Порядок (от дешёвого к дорогому)

0. **Синк с Mac**: `git -C $V pull --ff-only` (тихо; ошибки игнорируй — например, нет сети).
1. **Оглавление**: `$HERMES_HOME/notes/index.md` — одна строка на заметку (дата, название, kind, теги).
2. **FTS5-поиск**: `python3 $V/.index/notes_search.py "<запрос>" [лимит]`
   - слова (AND по умолчанию), `OR`, `"фраза"`, поля `title:слово`, `kind:договорённость`, `tags:…`;
   - если «индекс не найден» — сначала `python3 $V/.index/notes_index.py`.
3. **Точечное чтение**: 1–3 подходящих файла, если сниппетов мало.
4. Ответ — кратко, со ссылкой: `(заметка: Договорённости/Руслан/…md)`.

## Правила экономии токенов

- Никогда не читай всю папку заметок «на всякий случай».
- Не пересказывай заметку целиком — отвечай на вопрос.
- Нет совпадений — так и скажи, предложи уточнить запрос.

## Pitfalls

- index.md/notes.db устаревают, если заметка сохранена без пересборки — запусти notes_index.py.
- Пути файлов — как вернул поиск (относительно $V).
```

### A3. `obsidian`

```markdown
---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Файловые операции с vault: чтение, список заметок, поиск, создание, дополнение, вики-ссылки.

## Vault path

Путь — `OBSIDIAN_VAULT_PATH` из `${HERMES_HOME}/.env` (по умолчанию — рабочая база заметок). Файловые инструменты НЕ раскрывают переменные окружения — сначала определи конкретный абсолютный путь (через `terminal`), дальше работай файловыми инструментами. В путях могут быть пробелы — поэтому файловые инструменты предпочтительнее shell.

## Операции

- **Чтение заметки** — `read_file` с абсолютным путём.
- **Список заметок** — `search_files(target="files", pattern="*.md", path=<vault>)`.
- **Поиск** — `search_files(target="content", pattern=<regex>, path=<vault>, file_glob="*.md")`.
- **Создание** — `write_file` с полным markdown (frontmatter обязателен).
- **Дополнение/правки** — `patch` по устойчивому якорю; `write_file` — если переписываешь целиком.
- **Wikilinks** — `[[Имя заметки]]` для связей между заметками.
```

---

## Приложение B — код скриптов

### B1. `notes_classify.py`

```python
#!/usr/bin/env python3
"""
Детерминированный раскладчик заметок по смысловым категориям.
Страховка поверх агента: читает frontmatter (kind, category, topic) и кладёт
файл в notes/<Категория>/<Тема>/<имя>. Если агент не указал category —
выводит из kind. Тему (topic) берёт только из frontmatter (агент задаёт её из смысла).
Запуск: python3 notes_classify.py   (после — обязательно notes_index.py для индекса/пуша)
"""
import json, os, re, shutil, subprocess
from datetime import datetime

ROOT = "$HERMES_HOME/notes"
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

# категория по kind (если category не задан явно)
KIND_CAT = {
    "договорённость": "Договорённости",
    "транскрибация": "Транскрибации",
    "встреча": "Встречи",
    "идея": "Идеи",
    "заметка": "Заметки",
    "файл": "Прочее",
}
DEFAULT_CAT = "Прочее"

def safe_name(s, fallback="без-темы"):
    s = str(s or "").strip()
    s = re.sub(r"[\\/:*?\"<>|]", "-", s).strip(" .-_")
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:48] or fallback

def get_fm(text):
    m = FM_RE.match(text)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip().strip('"[]').strip()
    return fm

def walk_md():
    for dirpath, dirs, files in os.walk(ROOT):
        parts = dirpath.split(os.sep)
        if ".index" in parts or "raw" in parts or ".git" in parts:
            continue
        for fn in files:
            if fn.endswith(".md") and fn != "index.md" and not fn.startswith("."):
                yield os.path.join(dirpath, fn)

def main():
    moved = 0
    for path in walk_md():
        text = open(path, encoding="utf-8").read()
        fm = get_fm(text)
        cat = fm.get("category") or KIND_CAT.get(fm.get("kind", "").lower(), DEFAULT_CAT)
        topic = safe_name(fm.get("topic")) if fm.get("topic") else None
        # категорию тоже санитизируем на одиночный сегмент
        cat = safe_name(cat, "Прочее")
        target_dir = os.path.join(ROOT, cat, topic) if topic else os.path.join(ROOT, cat)
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, os.path.basename(path))
        if os.path.abspath(path) != os.path.abspath(target):
            rel_old = os.path.relpath(path, ROOT)
            # git mv для отслеживаемых — чтобы история сохранилась
            tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--error-unmatch", rel_old],
                                     capture_output=True).returncode == 0
            if tracked:
                subprocess.run(["git", "-C", ROOT, "mv", "-k", rel_old,
                                os.path.relpath(target, ROOT)])
            else:
                shutil.move(path, target)
            moved += 1
    print(f"перемещено заметок: {moved}; категории:",
          sorted({os.path.relpath(d, ROOT).split(os.sep)[0] for d, _, _ in os.walk(ROOT)
                  if ".index" not in d and "raw" not in d and os.path.relpath(d, ROOT) != "."}))

if __name__ == "__main__":
    main()
```

### B2. `notes_index.py`

```python
#!/usr/bin/env python3
"""
Пересборка индекса заметок Obsidian-совместимой базы:
  notes/**/*.md  ->  .index/notes.db (SQLite FTS5)  +  index.md (оглавление)
Идемпотентно: полный rebuild при каждом запуске.
Заметка = md-файл с YAML-frontmatter: title, date, kind, tags.
В конце — автоматический git commit + push (ошибки сети не фатальны).
"""
import json, os, re, sqlite3, subprocess, sys
from datetime import datetime

ROOT = "$HERMES_HOME/notes"
DB = os.path.join(ROOT, ".index", "notes.db")
INDEX_MD = os.path.join(ROOT, "index.md")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})", re.M)

def parse_fm(text):
    m = FM_RE.match(text)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip().strip('"[]').strip()
    body = text[m.end():] if m else text
    return fm, body

def first_heading(body):
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
    return ""

def walk():
    for dirpath, _, files in os.walk(ROOT):
        if ".index" in dirpath or "raw" in dirpath:
            continue
        for fn in sorted(files):
            if fn.endswith(".md") and fn != "index.md" and not fn.startswith("."):
                yield os.path.join(dirpath, fn)

def main():
    notes = []
    for path in walk():
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        fm, body = parse_fm(text)
        title = fm.get("title") or first_heading(body) or os.path.splitext(os.path.basename(path))[0]
        date = fm.get("date") or ""
        if not date:
            m = DATE_RE.search(os.path.basename(path))
            date = m.group(1) if m else ""
        kind = fm.get("kind", "заметка")
        tags = fm.get("tags", "")
        notes.append({"path": rel, "title": title, "date": date, "kind": kind,
                      "tags": tags, "body": body.strip()})

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS notes_fts")
    cur.execute("""CREATE VIRTUAL TABLE notes_fts USING fts5(
        path, title, kind, tags, date, body, tokenize='unicode61')""")
    for n in notes:
        cur.execute("INSERT INTO notes_fts VALUES (?,?,?,?,?,?)",
                    (n["path"], n["title"], n["kind"], n["tags"], n["date"], n["body"]))
    conn.commit()
    conn.close()

    # оглавление
    def wikilink(rel):
        return "[[" + rel[:-3].replace("\\", "/") + "]]"
    lines = ["# Оглавление заметок", "",
             f"Заметок: {len(notes)} · обновлено {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ""]
    for n in sorted(notes, key=lambda x: (x["date"], x["title"])):
        tags = (" · " + n["tags"]) if n["tags"] else ""
        cat = os.path.dirname(n["path"]).replace("\\", "/").split("/", 1)[0]
        lines.append(f"- **{n['date'] or '????-??-??'}** [{n['title']}]({n['path']}) · _{n['kind']}_ · {cat}{tags}")
    open(INDEX_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"индекс обновлён: {len(notes)} заметок -> {DB}, {INDEX_MD}")

    # Авто-push в GitHub (источник истины — сервер). Ошибки (нет сети) не фатальны.
    try:
        r = subprocess.run(["git", "-C", ROOT, "add", "-A"], capture_output=True, text=True)
        if r.returncode != 0:
            print("git add:", r.stderr.strip()[:200])
            return
        diff = subprocess.run(["git", "-C", ROOT, "diff", "--cached", "--quiet"],
                              capture_output=True, text=True).returncode
        if diff == 0:
            print("изменений для коммита нет")
            return
        subprocess.run(["git", "-C", ROOT, "commit", "-q", "-m", "notes: авто-индекс"], check=False)
        p = subprocess.run(["git", "-C", ROOT, "push"], capture_output=True, text=True)
        if p.returncode != 0:
            print("push:", p.stderr.strip()[:200])
    except Exception as e:
        print("авто-push пропущен:", e)

if __name__ == "__main__":
    main()
```

### B3. `notes_search.py`

```python
#!/usr/bin/env python3
"""
Поиск по заметкам (SQLite FTS5). Токен-дешёвый: возвращает только сниппеты.
Использование:  python3 notes_search.py "<запрос>" [лимит] [--paths]
Запрос FTS5: AND по умолчанию, можно OR, "фраза", поле:term (title:маркетплейс).
"""
import os, sqlite3, sys

DB = "$HERMES_HOME/notes/.index/notes.db"

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    q = sys.argv[1]
    limit = 8
    only_paths = False
    for a in sys.argv[2:]:
        if a == "--paths":
            only_paths = True
        elif a.isdigit():
            limit = int(a)
    if not os.path.exists(DB):
        print("индекс не найден — запусти notes_index.py", file=sys.stderr)
        sys.exit(2)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        rows = cur.execute(
            """SELECT path, title, kind, date, snippet(notes_fts, 5, '«', '»', '…', 24)
               FROM notes_fts WHERE notes_fts MATCH ? ORDER BY rank LIMIT ?""",
            (q, limit)).fetchall()
    except sqlite3.OperationalError as e:
        print("ошибка запроса:", e, file=sys.stderr)
        sys.exit(1)
    if not rows:
        print("совпадений нет")
        return
    for path, title, kind, date, sn in rows:
        if only_paths:
            print(path)
            continue
        print(f"[{date or '????-??-??'}] {title} · {kind}\n  файл: {path}\n  …{sn}…\n")

if __name__ == "__main__":
    main()
```
