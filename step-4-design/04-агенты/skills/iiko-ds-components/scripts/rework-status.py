"""Where did the _audit/rec rework stop? Reads files only, prints a table.

Usage:
    python rework-status.py [repo_root]        # default: C:\\Users\\asukharev\\GitHub\\DS

Answers the question asked after every interruption: which components still have no
patterns_ru, which out/<kind>/ patches exist but were never merged into data/, and how
many phone screens each page's preview has. Run it before promising anything.

Then:  python ../apply_out.py --build   and   python ../checks/check-patch.py
"""
import glob
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\asukharev\GitHub\DS"
REC = os.path.join(ROOT, "_audit", "rec")
DATA = os.path.join(REC, "data")
OUT = os.path.join(REC, "out")
KINDS = ("edits", "previews", "platforms", "patterns")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # a half-written patch must not kill the report
        return {"__error__": str(exc)}


def main():
    rows, no_pat, unsynced, errors = [], [], [], []
    for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        slug = os.path.basename(path)[:-5]
        data = load(path)
        if "__error__" in data:
            errors.append("data/%s.json: %s" % (slug, data["__error__"]))
            continue
        have = [k for k in KINDS if os.path.exists(os.path.join(OUT, k, slug + ".json"))]
        pats = data.get("patterns_ru") or []
        if not pats:
            no_pat.append(slug)
        preview = data.get("preview_html") or ""
        patch_path = os.path.join(OUT, "previews", slug + ".json")
        if os.path.exists(patch_path):
            patch = load(patch_path)
            if "__error__" in patch:
                errors.append("out/previews/%s.json: %s" % (slug, patch["__error__"]))
            elif (patch.get("preview_html") or "").strip() != preview.strip():
                unsynced.append(slug)
        rows.append((slug, len(pats), preview.count("phones__item"), ",".join(have) or "-"))

    print("%-16s %-9s %-8s %s" % ("slug", "patterns", "screens", "out/ patches"))
    for slug, n_pat, screens, have in rows:
        print("%-16s %-9d %-8d %s" % (slug, n_pat, screens, have))
    print("\nстраниц: %d" % len(rows))
    print("без паттернов (checker скажет PAT-MISSING): %d %s" % (len(no_pat), no_pat))
    print("превью в out/ не совпадает с data/ (не влито): %d %s" % (len(unsynced), unsynced))
    for err in errors:
        print("ошибка чтения:", err)
    print("\nдальше: python apply_out.py --build && python checks/check-patch.py")


main()
