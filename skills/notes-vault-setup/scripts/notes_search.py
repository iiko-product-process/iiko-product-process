#!/usr/bin/env python3
"""
Поиск по заметкам (SQLite FTS5). Токен-дешёвый: возвращает только сниппеты.
Использование:  python3 notes_search.py "<запрос>" [лимит] [--paths]
Запрос FTS5: AND по умолчанию, можно OR, "фраза", поле: term (title:маркетплейс).
"""
import os, sqlite3, sys

DB = "/opt/data/notes/.index/notes.db"

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
