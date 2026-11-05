#!/usr/bin/env python3
"""
Пересборка индекса заметок Obsidian-совместимой базы:
  /opt/data/notes/**/*.md  →  .index/notes.db (SQLite FTS5)  +  index.md (оглавление)
Идемпотентно: полный rebuild при каждом запуске (на сотнях заметок — мгновенно).
Заметка = md-файл с YAML-frontmatter: title, date, kind, tags.
"""
import json, os, re, sqlite3, subprocess, sys
from datetime import datetime

ROOT = "/opt/data/notes"
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
