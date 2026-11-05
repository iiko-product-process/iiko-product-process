#!/usr/bin/env bash
# skills-digest.sh — собрать присланные сотрудниками архивы в один markdown-отчёт.
#
# Дедуплицирует одинаковые скиллы (совпадение sha1), сравнивает с каноном, считает объём правок
# и раскладывает по разделам: новое / изменённое / идентично канону (свёрнуто) / требует внимания.
#
# usage:
#   skills-digest.sh [--inbox DIR] [--out FILE.md] [--canon-repo PATH] [--workdir DIR] [--top N]
#
# По умолчанию: --inbox ~/skill-reports, --out ~/skill-reports/digest-<дата>.md,
#               --canon-repo /opt/data/iiko-product-office-skills, --workdir ~/skill-reports/_work
set -uo pipefail

INBOX="$HOME/skill-reports"
OUT=""
CANON="/opt/data/iiko-product-office-skills"
WORK=""
TOP=50

while [ $# -gt 0 ]; do
  case "$1" in
    --inbox) INBOX="${2:?}"; shift ;;
    --out) OUT="${2:?}"; shift ;;
    --canon-repo) CANON="${2:?}"; shift ;;
    --workdir) WORK="${2:?}"; shift ;;
    --top) TOP="${2:?}"; shift ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$INBOX" ] || { echo "skills-digest: нет каталога $INBOX"; exit 1; }
DATE="$(date +%Y-%m-%d)"
[ -n "$OUT" ] || OUT="$INBOX/digest-$DATE.md"
[ -n "$WORK" ] || WORK="$INBOX/_work"
mkdir -p "$WORK"

shopt -s nullglob
archives=("$INBOX"/*.tar.gz)
if [ ${#archives[@]} -eq 0 ]; then
  echo "skills-digest: в $INBOX нет архивов *.tar.gz"; exit 0
fi

# распаковка
for a in "${archives[@]}"; do
  stem="$(basename "$a" .tar.gz)"
  [ -d "$WORK/$stem" ] || tar -xzf "$a" -C "$WORK" 2>/dev/null
done

DIGEST_ARGS=("$WORK" "$CANON" "$OUT" "$TOP" "$DATE" "${#archives[@]}")
python3 - "${DIGEST_ARGS[@]}" <<'PY'
import json, os, sys, difflib, glob, collections, hashlib

work, canon, out, top, date, n_arch = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], int(sys.argv[6])

# --- канон: name -> (sha1, path) ---
canon_map = {}
for f in glob.glob(os.path.join(canon, "**", "SKILL.md"), recursive=True):
    if "/.git/" in f:
        continue
    rel = os.path.relpath(f, canon)
    if not (rel.startswith("skills/") or rel.startswith("step-")):
        continue
    name = None
    for line in open(f, encoding='utf-8', errors='ignore'):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"'); break
    if not name:
        continue
    canon_map[name] = (hashlib.sha1(open(f, 'rb').read()).hexdigest(), f)

# --- сбор из манифестов ---
entries = {}   # (name, sha1) -> dict
stats = collections.Counter()
bad = []
for mf in glob.glob(os.path.join(work, "*", "manifest.json")):
    try:
        m = json.load(open(mf, encoding='utf-8'))
    except Exception as e:
        bad.append(f"{mf}: {e}"); continue
    author = m.get("author") or "?"
    root = os.path.dirname(mf)
    for it in m.get("items", []):
        stats[it.get("status", "?")] += 1
        if it.get("status") == "identical":
            continue
        key = (it.get("name"), it.get("sha1"))
        e = entries.setdefault(key, {
            "name": it.get("name"), "sha1": it.get("sha1"), "version": it.get("version") or "—",
            "authors": set(), "size_kb": 0, "secrets": set(), "statuses": set(),
            "paths": [], "mtime": it.get("mtime") or "—",
        })
        e["authors"].add(author)
        e["size_kb"] = max(e["size_kb"], it.get("size_kb") or 0)
        e["statuses"].add(it.get("status"))
        if it.get("secrets"):
            e["secrets"].update(s for s in it["secrets"].split(";") if s)
        p = os.path.join(root, "skills", it.get("name") or "")
        if os.path.isdir(p):
            e["paths"].append(p)

def canon_lines(name):
    v = canon_map.get(name)
    if not v: return None
    return open(v[1], encoding='utf-8', errors='ignore').read().splitlines()

def lines_of(path):
    f = os.path.join(path, "SKILL.md")
    if not os.path.isfile(f): return []
    return open(f, encoding='utf-8', errors='ignore').read().splitlines()

rows = []
for (name, sha), e in entries.items():
    in_canon = name in canon_map
    status = "новое" if not in_canon else "изменено"
    if e["secrets"] or "attention" in e["statuses"]:
        status = "требует внимания"
    added = removed = 0
    if in_canon:
        base = canon_lines(name) or []
        cur = lines_of(e["paths"][0]) if e["paths"] else []
        sm = difflib.SequenceMatcher(None, base, cur)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("replace", "delete"): removed += i2 - i1
            if tag in ("replace", "insert"): added += j2 - j1
    rows.append({**e, "status": status, "in_canon": in_canon, "added": added, "removed": removed,
                 "authors_str": ", ".join(sorted(e["authors"])), "paths": e["paths"]})

order = {"требует внимания": 0, "новое": 1, "изменено": 2}
rows.sort(key=lambda r: (order.get(r["status"], 9), -(r["added"] + r["removed"]), r["name"] or ""))

def table(rs):
    out = ["| # | Статус | Скилл | Версия | Автор(ы) | ±строк | Размер | Файлы |",
           "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rs[:top], 1):
        delta = f"+{r['added']}/−{r['removed']}" if r["in_canon"] else "—"
        files = "<br>".join(f"`{p}`" for p in r["paths"][:2]) or "—"
        out.append(f"| {i} | {r['status']} | `{r['name']}` | {r['version']} | {r['authors_str']} | {delta} | {r['size_kb']} КБ | {files} |")
    if len(rs) > top:
        out.append(f"| … | | ещё {len(rs)-top} | | | | | |")
    return "\n".join(out)

new_rows = [r for r in rows if r["status"] == "новое"]
chg_rows = [r for r in rows if r["status"] == "изменено"]
att_rows = [r for r in rows if r["status"] == "требует внимания"]

md = [f"# Дайджест скиллов сотрудников — {date}", ""]
md.append(f"Архивов: **{n_arch}** · уникальных скиллов к разбору: **{len(rows)}** "
          f"(новых {len(new_rows)}, изменённых {len(chg_rows)}, требуют внимания {len(att_rows)}) · "
          f"идентичных канону пропущено: {stats.get('identical', 0)}")
md += ["", f"Канон для сравнения: `{canon}`", ""]

if att_rows:
    md += ["## Требует внимания", "", "В файлах найдены строки, похожие на секреты — смотреть до переноса в канон.", "", table(att_rows), ""]
if new_rows:
    md += ["## Новые скиллы", "", table(new_rows), ""]
if chg_rows:
    md += ["## Изменённые скиллы", "", "±строк считается от версии в каноне (если скилла там нет — прочерк).", "", table(chg_rows), ""]
if not rows:
    md += ["Новых и изменённых скиллов нет — все присланные совпали с каноном.", ""]
if bad:
    md += ["## Ошибки разбора", ""] + [f"- {b}" for b in bad] + [""]

md += ["## Что дальше", "",
       "1. Открыть файлы из колонки «Файлы» — это распакованные копии из архивов.",
       "2. Решить по каждому: в канон (через PR), автору на доработку или в архив.",
       "3. В канон переносить только после проверки на секреты и совместимость с текущей версией.",
       ""]

open(out, "w", encoding='utf-8').write("\n".join(md))
print(f"дайджест: {out}")
print(f"архивов {n_arch}, уникальных {len(rows)}: новых {len(new_rows)}, изменённых {len(chg_rows)}, внимание {len(att_rows)}, идентичных {stats.get('identical', 0)}")
PY
