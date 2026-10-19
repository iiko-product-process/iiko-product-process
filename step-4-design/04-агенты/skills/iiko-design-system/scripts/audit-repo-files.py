#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит файлов рабочего дерева DS: что никем не упомянуто, что дублируется, что весит.

Запуск из корня DS:
    python scripts/audit-repo-files.py
    python scripts/audit-repo-files.py --root C:/Users/asukharev/GitHub/DS --top 40

Печатает три отчёта: ссылочный анализ (кто упомянут, кто нет), группы дублей по содержимому,
вес по папкам (через `git ls-files`, а не `git cat-file` — на 1000+ файлах тот уходит в таймаут).

НИЧЕГО не удаляет и не меняет: это отчёт для владельца, работы — после его слова.
Помнить: «нигде не упомянут» != «не нужен» — PNG и сырьё читаются скриптами через glob по каталогу.
"""
import argparse
import collections
import hashlib
import os
import subprocess
import sys

SKIP_DIRS = {".git", "__pycache__", "node_modules"}
TEXT_EXT = {".html", ".css", ".js", ".mjs", ".py", ".md", ".json", ".txt", ".ps1", ".svg",
            ".yml", ".yaml", ".xml"}


def collect(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            try:
                files.append((rel, path, os.path.getsize(path)))
            except OSError:
                continue
    return files


def mention_report(files, top):
    texts = {}
    for rel, path, size in files:
        if os.path.splitext(rel)[1].lower() in TEXT_EXT and size < 3_000_000:
            try:
                texts[rel] = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
    mentions = collections.defaultdict(list)
    for rel, body in texts.items():
        for other, _, _ in files:
            if other != rel and other.split("/")[-1] in body:
                mentions[other].append(rel)
    orphans = [(rel, size) for rel, _, size in files if not mentions[rel]]
    print(f"== ссылочный анализ: файлов {len(files)}, текстовых {len(texts)}, "
          f"нигде не упомянуто {len(orphans)}")
    by_dir = collections.Counter("/".join(rel.split("/")[:2]) for rel, _ in orphans)
    for key, count in by_dir.most_common(top):
        print(f"   {count:5d}  {key}")
    print("   примеры (крупнейшие):")
    for rel, size in sorted(orphans, key=lambda x: -x[1])[:top]:
        print(f"   {size:8d}  {rel}")
    print("   ВНИМАНИЕ: упоминание ищется по имени; PNG и сырьё читаются glob-ом по каталогу —"
          " перед вердиктом искать потребителя по каталогу, `open(`/`glob`/`import`.\n")


def dup_report(files, top):
    groups = collections.defaultdict(list)
    for rel, path, size in files:
        if size < 1024:
            continue
        try:
            groups[hashlib.md5(open(path, "rb").read()).hexdigest()].append((rel, size))
        except OSError:
            continue
    dups = [v for v in groups.values() if len(v) > 1]
    wasted = sum(size * (len(v) - 1) for v in dups for _, size in v[:1])
    print(f"== дубли по содержимому: групп {len(dups)}, лишнего ~{wasted // 1024} КБ")
    for group in sorted(dups, key=lambda g: -g[0][1])[:top]:
        rel, size = group[0]
        print(f"   {len(group)}x {size // 1024:5d} КБ: {rel}")
        for other, _ in group[1:]:
            print(f"            = {other}")
    print()


def weight_report(root, top):
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"== вес в git: не удалось выполнить git ls-files ({exc})")
        return
    agg = collections.Counter()
    cnt = collections.Counter()
    total = 0
    for rel in out.splitlines():
        path = os.path.join(root, rel.replace("/", os.sep))
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        key = "/".join(rel.split("/")[:2])
        agg[key] += size
        cnt[key] += 1
        total += size
    print(f"== вес в git: трекается {len(out.splitlines())} файлов, {total / 1048576:.1f} МБ")
    for key, size in agg.most_common(top):
        print(f"   {size / 1048576:7.2f} МБ  {cnt[key]:5d} файлов  {key}")
    png = [r for r in out.splitlines() if r.lower().endswith(".png")]
    print(f"   PNG в гите: {len(png)}\n")


def junk_report(files, top):
    tiny = sorted((size, rel) for rel, _, size in files if size < 20)
    print(f"== мелочь (<20 Б): {len(tiny)}")
    for size, rel in tiny[:top]:
        print(f"   {size:5d}  {rel}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=os.getcwd(), help="корень дерева (по умолчанию текущий каталог)")
    parser.add_argument("--top", type=int, default=25, help="сколько строк показывать в списках")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    files = collect(root)
    print(f"дерево: {root}")
    print(f"файлов (без .git/__pycache__): {len(files)}, "
          f"объём {sum(s for _, _, s in files) / 1048576:.1f} МБ\n")
    mention_report(files, args.top)
    dup_report(files, args.top)
    weight_report(root, args.top)
    junk_report(files, args.top)
    print("\nНичего не удалялось и не менялось — это отчёт.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
