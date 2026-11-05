Система заметок Hermes <-> GitHub <-> Obsidian
================================================

Что в архиве
------------
notes-vault-setup/SKILL.md        — скилл-установщик (пошаговая инструкция + код скриптов)
notes-vault-setup/scripts/*.py    — те же скрипты файлами (notes_classify, notes_index, notes_search)

Как поставить (2 шага)
----------------------
1) Скилл в Hermes:
   положите папку notes-vault-setup в <HERMES_HOME>/skills/note-taking/
   (например /opt/data/skills/note-taking/notes-vault-setup/)
   либо просто попросите агента: «установи скилл из этого файла» и передайте SKILL.md.

2) Попросите агента выполнить шаги 0-6 из SKILL.md. Он развернёт:
   - папку заметок (vault) с .gitignore, raw/ и .index/;
   - скрипты раскладки, индексации (FTS5) и поиска;
   - скиллы-компаньоны notes-inbox / notes-search / obsidian;
   - приватный репозиторий на GitHub (нужен PAT с Contents: Read and write);
   - синк с Obsidian на Mac через плагин Obsidian Git.

Что понадобится
---------------
- Hermes Agent (контейнер), python3 c SQLite FTS5, git;
- аккаунт GitHub + приватный репозиторий;
- Mac с Obsidian.

Проверка: чек-лист в разделе 6 файла SKILL.md.
