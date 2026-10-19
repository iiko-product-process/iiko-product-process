#!/usr/bin/env python3
"""Обновление репозиториев DS одной командой.

Запуск из корня папки DS:

  python pull.py

Что делает: забирает свежий main из организации — в репозитории DS (эта папка) и в репозитории Prototypes (соседняя папка).
Если в репозитории лежат незакоммиченные правки или ты сидишь в своей ветке —
сообщает об этом и ничего не трогает, чтобы не потерять работу.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS = [
    ("DS (корень)", HERE),
    ("Prototypes (рядом)", os.path.normpath(os.path.join(HERE, "..", "Prototypes"))),
]


def git(path, *args):
    return subprocess.run(
        ["git", "-C", path] + list(args),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def first_line(text):
    text = (text or "").strip()
    return text.splitlines()[0] if text else ""


def main():
    print("Обновляю репозитории DS\n")
    problems = []

    for name, path in REPOS:
        if not os.path.isdir(os.path.join(path, ".git")):
            if path != HERE:
                print("· %-20s папки нет — репозиторий не склонирован" % name)
                problems.append("%s: нет папки" % name)
                continue
            print("· %-20s не git-репозиторий — запускать из корня папки DS" % name)
            problems.append("корень: не репозиторий")
            continue

        fetch = git(path, "fetch", "--quiet", "origin")
        if fetch.returncode != 0:
            print("· %-20s нет связи с гитом: %s" % (name, first_line(fetch.stderr)))
            problems.append("%s: ошибка связи" % name)
            continue

        branch = first_line(git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout)
        if branch != "main":
            print("· %-20s ты в ветке «%s» — main не трогаю" % (name, branch))
            continue

        dirty = [l for l in git(path, "status", "--porcelain", "--untracked-files=no").stdout.splitlines() if l.strip()]
        if dirty:
            print("· %-20s есть незакоммиченные правки (%d) — не трогаю" % (name, len(dirty)))
            problems.append("%s: незакоммиченные правки (перенеси их в свою ветку)" % name)
            continue

        behind = git(path, "rev-list", "--count", "HEAD..@{u}")
        if behind.returncode != 0:
            print("· %-20s ветка не отслеживает origin/main" % name)
            problems.append("%s: нет отслеживания origin/main" % name)
            continue

        count = int(behind.stdout.strip() or 0)
        if count == 0:
            print("· %-20s уже актуален" % name)
            continue

        merge = git(path, "merge", "--ff-only", "@{u}")
        if merge.returncode == 0:
            print("· %-20s обновлён на %d коммит(ов)" % (name, count))
        else:
            print("· %-20s не смог обновить: %s" % (name, first_line(merge.stderr)))
            problems.append("%s: обновление не прошло" % name)

    print()
    if problems:
        print("Нужно внимание:")
        for p in problems:
            print("  -", p)
        print("\nПодробнее — в readme.md")
    else:
        print("Оба репозитория на актуальном main.")


if __name__ == "__main__":
    main()
