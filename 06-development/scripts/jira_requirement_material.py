#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Материал для актуализации требований: что зафиксировано в PB-задаче и что поменялось рядом.

Запуск:
    python3 jira_requirement_material.py PB-7938
    python3 jira_requirement_material.py PB-7938 --days 30 --comments 10 --out ../ARTIFACTS/<слаг>/06-реализация
    python3 jira_requirement_material.py PB-7938 --sources PB-7026,PB-7359

Что делает:
  1. Читает основную продуктовую задачу (PB Story): описание как есть + последние комментарии.
  2. Собирает кандидатов-источников правки: связанные задачи (issuelinks в обе стороны),
     подзадачи, родителя и задачи, которые упоминают ключ в тексте (`text ~ "KEY"`).
  3. По каждому источнику достаёт: историю правок описания (было → стало) и свежие комментарии.
  4. Печатает материал и сохраняет его в файл — дальше ИИ сопоставляет и предлагает правку
     в основную задачу (решение принимает человек).

Зависимостей нет. Нужны JIRA_URL (по умолчанию https://jira.iiko.ru) и JIRA_TOKEN.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

JIRA_URL = os.environ.get("JIRA_URL", "https://jira.iiko.ru").rstrip("/")
TOKEN = os.environ.get("JIRA_TOKEN", "")
MSK = timezone(timedelta(hours=3))

FIELDS = "summary,status,issuetype,assignee,reporter,updated,created,parent,subtasks,issuelinks,components,labels"


def api(path, params=None):
    url = JIRA_URL + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("Jira %s: HTTP %s %s" % (path, e.code, e.read().decode("utf-8", "replace")[:200])) from None
    except urllib.error.URLError as e:
        raise RuntimeError("Jira недоступна: %s" % e.reason) from None


def norm_key(raw):
    m = re.search(r"([A-Z][A-Z0-9_]+-\d+)", (raw or "").upper())
    if not m:
        raise SystemExit("Не понял задачу: %r" % raw)
    return m.group(1)


def browse(k):
    return "%s/browse/%s" % (JIRA_URL, k)


def parse_ts(v):
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None


def fmt(ts):
    return ts.astimezone(MSK).strftime("%d.%m.%Y %H:%M") if ts else "—"


def clip(text, limit, mark="…(сокращено)"):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n" + mark


def issue_pack(key, comment_limit):
    """Задача целиком: поля + описание + комментарии + история правок описания."""
    raw = api("/rest/api/2/issue/" + key, {"expand": "changelog", "fields": FIELDS + ",description,comment"})
    f = raw.get("fields", {})
    pack = {
        "key": key,
        "url": browse(key),
        "type": (f.get("issuetype") or {}).get("name", "—"),
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", "—"),
        "assignee": (f.get("assignee") or {}).get("displayName") or "—",
        "updated": f.get("updated"),
        "description": f.get("description") or "",
        "comments": [],
        "description_edits": [],
        "status_changes": [],
        "links": [],
    }
    cm = (f.get("comment") or {})
    comments = cm.get("comments") or []
    pack["comments_total"] = cm.get("total", len(comments))
    for c in comments[-comment_limit:]:
        pack["comments"].append({
            "when": c.get("created"),
            "author": (c.get("author") or {}).get("displayName", "—"),
            "body": c.get("body") or "",
        })
    for h in (raw.get("changelog") or {}).get("histories", []):
        for it in h.get("items", []):
            if it.get("field") == "description":
                pack["description_edits"].append({
                    "when": h.get("created"),
                    "author": (h.get("author") or {}).get("displayName", "—"),
                    "from": it.get("fromString") or "",
                    "to": it.get("toString") or "",
                })
            elif it.get("field") == "status":
                pack["status_changes"].append({
                    "when": h.get("created"),
                    "from": it.get("fromString") or "",
                    "to": it.get("toString") or "",
                })
    for l in f.get("issuelinks") or []:
        other = l.get("outwardIssue") or l.get("inwardIssue") or {}
        pack["links"].append({
            "type": l["type"]["name"],
            "direction": l["type"].get("outward") if l.get("outwardIssue") else l["type"].get("inward"),
            "key": other.get("key"),
        })
    pack["subtasks"] = [s["key"] for s in (f.get("subtasks") or [])]
    pack["parent"] = (f.get("parent") or {}).get("key")
    return pack


def candidates(main, extra, days):
    """Кандидаты-источники: связи, подзадачи, родитель, упоминающие задачи."""
    found, order, seen = {}, [], {main["key"]}
    for k, why in [(l["key"], "%s (%s)" % (l["direction"], l["type"])) for l in main["links"] if l["key"]] + \
                  [(s, "подзадача") for s in main["subtasks"]] + \
                  [((main["parent"] or ""), "родитель")] + \
                  [(k, "задан явно") for k in extra]:
        if k and k not in seen:
            seen.add(k)
            order.append(k)
            found[k] = why
    # задачи, которые ссылаются на ключ текстом («по задаче PB-…»)
    try:
        res = api("/rest/api/2/search", {
            "jql": 'text ~ "%s" ORDER BY updated DESC' % main["key"],
            "maxResults": 20,
            "fields": "summary,status,issuetype,updated",
        })
        for i in res.get("issues", []):
            k = i["key"]
            if k not in seen:
                seen.add(k)
                order.append(k)
                found[k] = "упоминает %s в тексте" % main["key"]
    except RuntimeError as e:
        print("(поиск упоминаний не сработал: %s)" % e, file=sys.stderr)
    return found, order


def main():
    ap = argparse.ArgumentParser(description="Материал для актуализации требований в PB-задаче")
    ap.add_argument("task", help="ключ или ссылка на основную продуктовую задачу (PB Story)")
    ap.add_argument("--days", type=int, default=30, help="окно для комментариев и правок, дней (по умолчанию 30)")
    ap.add_argument("--comments", type=int, default=5, help="сколько последних комментариев тянуть (по умолчанию 5)")
    ap.add_argument("--edits", type=int, default=3, help="сколько последних правок описания показывать по источнику")
    ap.add_argument("--sources", default="", help="дополнительные ключи-источники через запятую")
    ap.add_argument("--max-text", type=int, default=6000, help="лимит символов на один текст (по умолчанию 6000)")
    ap.add_argument("--out", help="папка для материала (обычно ARTIFACTS/<слаг>/06-реализация)")
    args = ap.parse_args()

    if not TOKEN:
        raise SystemExit("Не задан JIRA_TOKEN (source /opt/data/.env)")

    key = norm_key(args.task)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    extra = [norm_key(s) for s in args.sources.split(",") if s.strip()]

    main_pack = issue_pack(key, args.comments)
    found, order = candidates(main_pack, extra, args.days)
    sources = []
    for k in order:
        try:
            pack = issue_pack(k, args.comments)
        except RuntimeError as e:
            print("(источник %s не прочитан: %s)" % (k, e), file=sys.stderr)
            continue
        pack["why"] = found[k]
        pack["recent_edits"] = [e for e in pack["description_edits"] if (parse_ts(e["when"]) or cutoff) >= cutoff][-args.edits:]
        pack["recent_comments"] = [c for c in pack["comments"] if (parse_ts(c["when"]) or cutoff) >= cutoff]
        pack["recent_status"] = [s for s in pack["status_changes"] if (parse_ts(s["when"]) or cutoff) >= cutoff]
        sources.append(pack)

    now = datetime.now(MSK)
    out = []
    out.append("# Материал для актуализации требований: %s" % main_pack["key"])
    out.append("")
    out.append("**%s** — «%s» · Статус: %s · Ответственный: %s · Обновлена: %s" % (
        main_pack["type"], main_pack["summary"], main_pack["status"], main_pack["assignee"], fmt(parse_ts(main_pack["updated"]))))
    out.append("Ссылка: %s" % main_pack["url"])
    out.append("Собрано: %s МСК · окно: %d дн. · источников-кандидатов: %d" % (now.strftime("%d.%m.%Y %H:%M"), args.days, len(sources)))
    out.append("")
    out.append("## 1. Что зафиксировано в основной задаче (as is)")
    out.append("")
    out.append("### Описание")
    out.append("")
    out.append(clip(main_pack["description"], args.max_text) or "(описание пустое)")
    out.append("")
    if main_pack["comments"]:
        out.append("### Последние комментарии (%d из %d)" % (len(main_pack["comments"]), main_pack.get("comments_total", 0)))
        out.append("")
        for c in main_pack["comments"]:
            out.append("- **%s, %s:** %s" % (fmt(parse_ts(c["when"])), c["author"], clip(c["body"], 800).replace("\n", " ")))
        out.append("")
    if main_pack["description_edits"]:
        out.append("### Описание правили %d раз(а); последняя правка — %s" % (
            len(main_pack["description_edits"]), fmt(parse_ts(main_pack["description_edits"][-1]["when"]))))
        out.append("")

    out.append("## 2. Кандидаты-источники (где могла появиться новая редакция требования)")
    out.append("")
    if not sources:
        out.append("Связанных задач и упоминаний не нашлось — уточни ключ задачи-источника через `--sources`.")
        out.append("")
    for s in sources:
        out.append("### [%s](%s) — «%s»" % (s["key"], s["url"], s["summary"]))
        out.append("")
        out.append("%s · Статус: %s · Кто: %s · Обновлена: %s · связь: %s" % (
            s["type"], s["status"], s["assignee"], fmt(parse_ts(s["updated"])), s["why"]))
        out.append("")
        if s["recent_edits"]:
            out.append("**Правки описания за %d дн. (%d):**" % (args.days, len(s["recent_edits"])))
            out.append("")
            for e in s["recent_edits"]:
                out.append("- %s, %s" % (fmt(parse_ts(e["when"])), e["author"]))
                out.append("  - было: %s" % clip(e["from"], 1200).replace("\n", " "))
                out.append("  - стало: %s" % clip(e["to"], 1200).replace("\n", " "))
            out.append("")
        if s["recent_status"]:
            out.append("**Смена статусов за %d дн.:** %s" % (args.days, " → ".join(
                "%s (%s)" % (x["to"], fmt(parse_ts(x["when"]))) for x in s["recent_status"])))
            out.append("")
        if s["recent_comments"]:
            out.append("**Комментарии за %d дн. (%d):**" % (args.days, len(s["recent_comments"])))
            out.append("")
            for c in s["recent_comments"]:
                out.append("> **%s, %s:** %s" % (fmt(parse_ts(c["when"])), c["author"], clip(c["body"], 1500)))
                out.append("")
        if not (s["recent_edits"] or s["recent_comments"] or s["recent_status"]):
            out.append("Изменений за окно нет. Текущее описание источника (если правка была раньше):")
            out.append("")
            out.append(clip(s["description"], 1500) or "(пусто)")
            out.append("")
        out.append("Описание источника целиком: %s" % s["url"])
        out.append("")

    out.append("## 3. Что делать дальше (порядок для агента)")
    out.append("")
    out.append("1. Сопоставить разделы описания основной задачи с правками источников: что именно изменилось —")
    out.append("   правило, поведение, граница, текст интерфейса.")
    out.append("2. Показать предложение «было → стало» по разделам, с ссылками на источник и дату.")
    out.append("3. Ничего не записывать в Jira до явного подтверждения человеком.")
    out.append("")

    material = "\n".join(out)
    stamp = now.strftime("%Y-%m-%d")
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        md_path = os.path.join(args.out, "material-%s-%s.md" % (key, stamp))
        json_path = os.path.join(args.out, "material-%s-%s.json" % (key, stamp))
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(material + "\n")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump({"generated_at": now.isoformat(), "main": main_pack, "sources": sources},
                      fh, ensure_ascii=False, indent=2)
        print("материал: %s" % md_path)
        print("json:     %s" % json_path)
        print()
    print(material)

    if not args.out:
        print("Артефакты по задаче складываются в её папку — ARTIFACTS/<слаг>/06-реализация/ "
              "(укажи путь флагом --out).")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print("Ошибка: %s" % e, file=sys.stderr)
        sys.exit(2)
