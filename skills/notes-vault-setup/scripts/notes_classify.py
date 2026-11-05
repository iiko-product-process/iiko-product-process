#!/usr/bin/env python3
"""
Детерминированный раскладчик заметок по смысловым категориям.
Страховка поверх агента: читает frontmatter (kind, category, topic) и кладёт
файл в /opt/data/notes/<Категория>/<Тема>/<имя>. Если агент не указал category —
выводит из kind. Тему (topic) берёт только из frontmatter (агент задаёт её из смысла).
Запуск: python3 notes_classify.py   (после — обязательно notes_index.py для индекса/пуша)
"""
import json, os, re, shutil, subprocess
from datetime import datetime

ROOT = "/opt/data/notes"
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
