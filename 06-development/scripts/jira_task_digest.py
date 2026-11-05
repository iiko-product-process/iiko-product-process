#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Выгрузка семьи задач Jira по эпику/стори: статусы, ответственные, изменения.

Запуск:
    python3 jira_task_digest.py PB-7986
    python3 jira_task_digest.py https://jira.iiko.ru/browse/PB-7986 --days 14 --out ../tasks/<слаг>/06-реализация
    python3 jira_task_digest.py PB-8063 --no-changelog

Что делает:
  1. Находит всю семью задач вокруг указанной: эпик → дочерние (Epic Link) → их подзадачи;
     стори → подзадачи, родитель, связанные задачи (issuelinks в обе стороны).
  2. Тянет по каждой: тип, статус, ответственного, даты, прогресс по подзадачам.
  3. Читает историю изменений (changelog) и отбирает изменения за окно `--days`.
  4. Печатает markdown-дайджест и сохраняет JSON-снапшот (для сравнения с прошлой выгрузкой).

Зависимостей нет (только стандартная библиотека). Нужны переменные окружения:
    JIRA_URL    — по умолчанию https://jira.iiko.ru
    JIRA_TOKEN  — персональный токен Jira (как в /opt/data/.env)
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

JIRA_URL = os.environ.get("JIRA_URL", "https://jira.iiko.ru").rstrip("/")
TOKEN = os.environ.get("JIRA_TOKEN", "")
MSK = timezone(timedelta(hours=3))  # Jira iiko живёт в МСК

FIELDS = ",".join([
    "summary", "status", "issuetype", "assignee", "reporter", "created", "updated",
    "resolutiondate", "duedate", "priority", "subtasks", "issuelinks", "parent",
    "labels", "components", "fixVersions", "aggregatetimespent", "customfield_11441",
])

# Поля changelog, которые реально интересны продукту (остальное — шум)
INTERESTING = {
    "status": "статус",
    "assignee": "ответственный",
    "summary": "заголовок",
    "description": "описание",
    "priority": "приоритет",
    "duedate": "срок",
    "Sprint": "спринт",
    "Epic Link": "эпик",
    "labels": "метки",
    "components": "компоненты",
    "Fix Version": "версия",
    "Story Points": "оценка",
    "timeoriginalestimate": "оценка (время)",
    "timeestimate": "осталось",
    "resolution": "резолюция",
    "Attachment": "вложение",
}


def api(path, params=None, method="GET"):
    """Запрос к Jira REST API v2. Возвращает распарсенный JSON."""
    url = JIRA_URL + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError("Jira %s: HTTP %s %s" % (path, e.code, body)) from None
    except urllib.error.URLError as e:
        raise RuntimeError("Jira недоступна (%s): %s" % (url, e.reason)) from None


def norm_key(raw):
    """'https://jira.iiko.ru/browse/PB-7986?x=1' → 'PB-7986'."""
    m = re.search(r"([A-Z][A-Z0-9_]+-\d+)", (raw or "").upper())
    if not m:
        raise SystemExit("Не понял задачу: %r. Нужен ключ (PB-7986) или ссылка." % raw)
    return m.group(1)


def browse(key):
    return "%s/browse/%s" % (JIRA_URL, key)


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def fmt(ts):
    return ts.astimezone(MSK).strftime("%d.%m.%Y %H:%M") if ts else "—"


def brief(issue):
    """Компактное представление задачи из ответа поиска/issue."""
    f = issue.get("fields", {})
    sub = f.get("subtasks") or []
    return {
        "key": issue["key"],
        "url": browse(issue["key"]),
        "type": (f.get("issuetype") or {}).get("name", "—"),
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", "—"),
        "status_category": ((f.get("status") or {}).get("statusCategory") or {}).get("name", "—"),
        "assignee": (f.get("assignee") or {}).get("displayName") or "—",
        "updated": f.get("updated"),
        "created": f.get("created"),
        "resolutiondate": f.get("resolutiondate"),
        "duedate": f.get("duedate"),
        "parent": (f.get("parent") or {}).get("key"),
        "epic": f.get("customfield_11441"),
        "components": [c.get("name") for c in (f.get("components") or [])],
        "labels": f.get("labels") or [],
        "subtasks": [{"key": s["key"], "status": (s.get("fields", {}).get("status") or {}).get("name", "—")} for s in sub],
        "links": [link_pair(l) for l in (f.get("issuelinks") or [])],
    }


def link_pair(link):
    other = link.get("outwardIssue") or link.get("inwardIssue") or {}
    direction = link["type"].get("outward") if link.get("outwardIssue") else link["type"].get("inward")
    of = other.get("fields", {}) or {}
    return {
        "type": link["type"]["name"],
        "direction": direction,
        "key": other.get("key"),
        "url": browse(other["key"]) if other.get("key") else None,
        "status": (of.get("status") or {}).get("name", "—"),
        "summary": of.get("summary", ""),
        "project": (other.get("key") or "").split("-")[0],
    }


def family(root_key, max_children):
    """Собирает семью задач: корень, дети по Epic Link, подзадачи, родитель, связи."""
    root_raw = api("/rest/api/2/issue/" + root_key, {"fields": FIELDS})
    root = brief(root_raw)
    members = [root]
    notes = []

    # эпик → дочерние задачи (+ их подзадачи, они приходят тем же запросом)
    if root["type"].lower() == "epic":
        found = api("/rest/api/2/search", {
            "jql": '"Epic Link" = %s ORDER BY key ASC' % root_key,
            "maxResults": max_children,
            "fields": FIELDS,
        })
        kids = [brief(i) for i in found.get("issues", [])]
        if found.get("total", 0) > len(kids):
            notes.append("дочерних задач больше лимита: показано %d из %d (--max-children)" % (len(kids), found["total"]))
        members += kids
        for k in kids:
            for s in k["subtasks"]:
                if s["key"] not in {m["key"] for m in members}:
                    members.append({"key": s["key"], "url": browse(s["key"]), "type": "Sub-task",
                                    "status": s["status"], "summary": "(подзадача %s)" % k["key"],
                                    "assignee": "—", "children_of": k["key"]})
    # подзадачи самого корня
    for s in root["subtasks"]:
        if s["key"] not in {m["key"] for m in members}:
            members.append({"key": s["key"], "url": browse(s["key"]), "type": "Sub-task",
                            "status": s["status"], "summary": "(подзадача %s)" % root_key,
                            "assignee": "—", "children_of": root_key})
    # родитель
    if root["parent"] and root["parent"] not in {m["key"] for m in members}:
        parent = brief(api("/rest/api/2/issue/" + root["parent"], {"fields": FIELDS}))
        parent["relation"] = "родитель"
        members.append(parent)
    # связанные задачи (обе стороны)
    for l in root["links"]:
        if l["key"] and l["key"] not in {m["key"] for m in members}:
            members.append({
                "key": l["key"], "url": l["url"], "relation": "%s (%s)" % (l["direction"], l["type"]),
                "type": "—", "status": l["status"], "summary": l["summary"], "assignee": "—",
            })
    # всем, кроме корня, подтягиваем тип/ответственного, если их нет
    need = [m["key"] for m in members if m.get("assignee") == "—" or m.get("type") == "—"]
    if need:
        for m in enrich(need):
            for f in members:
                if f["key"] == m["key"]:
                    f.update({k: v for k, v in m.items() if k not in ("subtasks", "links", "epic", "components")})
    return root, members, notes


def resolve_board(ref):
    """Доска по id или по части названия (Agile API)."""
    if str(ref).isdigit():
        return api("/rest/agile/1.0/board/%s" % ref)
    got = api("/rest/agile/1.0/board", {"name": ref, "maxResults": 50}).get("values", [])
    exact = [b for b in got if b["name"].strip().lower() == str(ref).strip().lower()]
    if exact:
        return exact[0]
    if len(got) == 1:
        return got[0]
    if not got:
        raise SystemExit("Доска «%s» не найдена (проверь название или укажи id)" % ref)
    raise SystemExit("Под «%s» подходит несколько досок: %s — укажи id" % (
        ref, ", ".join("%s (%s)" % (b["name"], b["id"]) for b in got[:6])))


def sprint_family(board_ref, max_issues, project=None, component=None, assignee=None, sprint_ref=None):
    """Активный спринт доски: задачи спринта как «семья» для того же отчёта.

    Нужен для дейли: берём только то, что команда взяла в текущий спринт.
    """
    board = resolve_board(board_ref)
    sprints = api("/rest/agile/1.0/board/%s/sprint" % board["id"], {"state": "active"}).get("values", [])
    if not sprints:
        sprints = api("/rest/agile/1.0/board/%s/sprint" % board["id"], {"maxResults": 50}).get("values", [])
        if not sprints:
            raise SystemExit("У доски «%s» нет спринтов" % board["name"])
    variants = []
    for s in sprints:
        n = api("/rest/agile/1.0/sprint/%s/issue" % s["id"], {"maxResults": 1, "fields": "key"}).get("total", 0)
        variants.append((s, n))
    if sprint_ref:
        want = str(sprint_ref).strip().lower()
        hit = [v for v in variants if str(v[0]["id"]) == want or want in v[0]["name"].lower()]
        if not hit:
            raise SystemExit("В спринтах доски «%s» нет «%s»: %s" % (
                board["name"], sprint_ref, ", ".join("%s «%s»" % (v[0]["id"], v[0]["name"]) for v in variants)))
        sprint, total_hint = hit[0]
    else:
        # у доски может быть несколько активных спринтов: берём самый узкий (командный),
        # общий релизный спринт компании отдаём в подсказке
        variants.sort(key=lambda v: v[1])
        sprint, total_hint = variants[0]
    issues, start, sprint_total = [], 0, 0
    while len(issues) < max_issues:
        page = api("/rest/agile/1.0/sprint/%s/issue" % sprint["id"],
                   {"startAt": start, "maxResults": 50, "fields": FIELDS})
        sprint_total = page.get("total", sprint_total)
        batch = page.get("issues", [])
        issues += batch
        if len(batch) < 50:
            break
        start += 50
    fetched = len(issues)
    total = fetched
    if project:
        issues = [i for i in issues if i["key"].split("-")[0].upper() == project.upper()]
    if component:
        issues = [i for i in issues if component.lower() in
                  [c.get("name", "").lower() for c in (i["fields"].get("components") or [])]]
    if assignee:
        issues = [i for i in issues if assignee.lower() in
                  ((i["fields"].get("assignee") or {}).get("displayName") or "").lower()]
    members = [brief(i) for i in issues]
    root = {
        "key": board["name"],
        "url": "%s/secure/RapidBoard.jspa?rapidView=%s" % (JIRA_URL, board["id"]),
        "type": "Спринт",
        "summary": "Активный спринт «%s»" % sprint["name"],
        "status": "активен",
        "status_category": "In Progress",
        "assignee": board["name"],
        "created": sprint.get("startDate"),
        "updated": sprint.get("endDate"),
        "links": [],
    }
    notes = ["спринт %s — %s" % ((sprint.get("startDate") or "")[:10], (sprint.get("endDate") or "")[:10]),
             "задач в спринте: %d, после фильтров: %d" % (sprint_total or fetched, len(members))]
    if len(variants) > 1:
        notes.append("у доски несколько спринтов: %s — взят самый узкий, другой можно взять через --sprint" % (
            ", ".join("%s «%s» (%d)" % (v[0]["id"], v[0]["name"], v[1]) for v in sorted(variants, key=lambda v: v[1]))))
    if sprint_total > fetched:
        notes.append("задач больше лимита: собрано %d из %d — поднять --max-children" % (fetched, sprint_total))
    return root, members, notes


def enrich(keys):
    """Дотягивает поля по списку ключей (пачками по 50)."""
    out = []
    for i in range(0, len(keys), 50):
        chunk = keys[i:i + 50]
        found = api("/rest/api/2/search", {
            "jql": "key in (%s)" % ",".join(chunk),
            "maxResults": 100,
            "fields": FIELDS,
        })
        out += [brief(x) for x in found.get("issues", [])]
    return out


def changelog(key, cutoff):
    """Изменения задачи за окно: [{when, author, field, from, to}] (свежие в конце)."""
    raw = api("/rest/api/2/issue/" + key, {"expand": "changelog", "fields": "summary"})
    changes = []
    for h in (raw.get("changelog") or {}).get("histories", []):
        ts = parse_ts(h.get("created"))
        if not ts or ts < cutoff:
            continue
        for it in h.get("items", []):
            field = it.get("field") or ""
            changes.append({
                "key": key,
                "when": h.get("created"),
                "author": (h.get("author") or {}).get("displayName", "—"),
                "field": field,
                "label": INTERESTING.get(field, field),
                "interesting": field in INTERESTING,
                "from": (it.get("fromString") or "")[:160],
                "to": (it.get("toString") or "")[:160],
            })
    return key, changes


def collect_changes(keys, cutoff, workers):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda k: changelog(k, cutoff), keys))
    out = []
    for _, ch in results:
        out += ch
    out.sort(key=lambda c: c["when"] or "")
    return out


def find_previous(out_dir, key):
    """Прошлый JSON-снапшот этой же задачи — чтобы показать, что изменилось с прошлой выгрузки."""
    if not out_dir or not os.path.isdir(out_dir):
        return None
    files = sorted([f for f in os.listdir(out_dir) if f.startswith("snapshot-%s-" % key) and f.endswith(".json")])
    if not files:
        return None
    try:
        with open(os.path.join(out_dir, files[-1]), encoding="utf-8") as fh:
            return {"file": files[-1], "data": json.load(fh)}
    except Exception:
        return None


def top_list(pairs, limit, unit=""):
    """«имя — N; имя — N; ещё K» — чтобы сводка влезала в строку дейли."""
    pairs = sorted(pairs, key=lambda x: -x[1])
    head = "; ".join("%s — %d" % (name, n) for name, n in pairs[:limit])
    return head + ("; ещё %d%s" % (len(pairs) - limit, unit) if len(pairs) > limit else "")


def render(root, members, changes, cutoff, days, stuck_days, notes, previous, all_changes=False, tasks_table=True, changes_computed=True):
    now = datetime.now(MSK)
    changes_full = changes
    noisy = [c for c in changes if not c["interesting"]]
    if not all_changes:
        changes = [c for c in changes if c["interesting"]]
    by_status = {}
    by_assignee = {}
    for m in members:
        by_status.setdefault(m.get("status", "—"), []).append(m["key"])
        by_assignee.setdefault(m.get("assignee", "—"), []).append(m["key"])
    children = [m for m in members if m["key"] != root["key"]]
    per_key = {}
    for c in changes:
        per_key[c["key"]] = per_key.get(c["key"], 0) + 1

    stuck = []
    for m in members:
        stamps = [t for t in (parse_ts(c["when"]) for c in changes_full if c["key"] == m["key"]) if t]
        last_change = max(stamps) if stamps else None
        base = last_change or parse_ts(m.get("updated")) or parse_ts(m.get("created"))
        if base and (now - base) > timedelta(days=stuck_days) and m.get("status_category") != "Done":
            stuck.append((m, (now - base).days))
    stuck.sort(key=lambda x: -x[1])

    lines = []
    lines.append("# %s — «%s»" % (root["key"], root["summary"]))
    lines.append("")
    lines.append("%s · Статус: **%s** · Ответственный: %s · Обновлена: %s" % (
        root["type"], root["status"], root["assignee"], fmt(parse_ts(root.get("updated")))))
    lines.append("Ссылка: %s" % root["url"])
    if root.get("type") == "Спринт":
        lines.append("Выгружено: %s МСК · окно изменений: %d дн. · задач в спринте: %d" % (
            now.strftime("%d.%m.%Y %H:%M"), days, len(members)))
    else:
        lines.append("Выгружено: %s МСК · окно изменений: %d дн. · всего задач в семье: %d (дочерних: %d)" % (
            now.strftime("%d.%m.%Y %H:%M"), days, len(members), len(children)))
    lines.append("")
    lines.append("## Коротко")
    lines.append("")
    lines.append("- **Статусы:** " + top_list([(s, len(k)) for s, k in by_status.items()], 8, " статусов"))
    lines.append("- **Кто ведёт:** " + top_list(
        [("без ответственного" if a == "—" else a, len(k)) for a, k in by_assignee.items()], 6, " человек"))
    if not changes_computed:
        lines.append("- **Изменений за %d дн.:** не считались (`--no-changelog`)" % days)
    else:
        lines.append("- **Изменений за %d дн.:** %d (последнее: %s)" % (
            days, len(changes), fmt(parse_ts(changes[-1]["when"])) if changes else "нет"))
    if noisy:
        lines.append("- Служебных изменений (связи, вложения-служебка и пр.) скрыто: %d — показать: `--all-changes`" % len(noisy))
    lines.append("- **Без движения больше %d дн.:** %d" % (stuck_days, len(stuck)))
    if previous:
        prev_keys = {m["key"] for m in previous["data"].get("members", [])}
        new_keys = [m["key"] for m in members if m["key"] not in prev_keys]
        lines.append("- **С прошлой выгрузки (%s):** %s" % (previous["file"], (
            "новых задач: " + ", ".join(new_keys)) if new_keys else "новых задач нет"))
    for n in notes:
        lines.append("- ⚠️ " + n)
    lines.append("")

    lines.append("## Задачи семьи")
    lines.append("")
    if not tasks_table:
        lines.append("Таблица задач не выводится (`--brief`): статусы и изменения — в блоках выше, полный список смотрится в Jira.")
    else:
        lines.append("| Ключ | Тип | Заголовок | Статус | Кто | Обновлена | Изменений за %d дн. |" % days)
        lines.append("|---|---|---|---|---|---|---|")
        ordered = [m for m in members if m["key"] == root["key"]] + sorted(
            children, key=lambda m: (m["status_category"] or "", -(parse_ts(m.get("updated")) or datetime(1970, 1, 1, tzinfo=MSK)).timestamp()))
        for m in ordered:
            lines.append("| [%s](%s) | %s | %s | %s | %s | %s | %d |" % (
                m["key"], m["url"], m.get("type", "—"), (m.get("summary") or "")[:70],
                m.get("status", "—"), m.get("assignee", "—"),
                fmt(parse_ts(m.get("updated"))), per_key.get(m["key"], 0)))
    lines.append("")

    if changes:
        lines.append("## Что изменилось за %d дн." % days)
        lines.append("")
        lines.append("| Когда | Кто | Задача | Что | Было → Стало |")
        lines.append("|---|---|---|---|---|")
        for c in changes[-60:]:
            mark = "" if c["interesting"] else "·"
            lines.append("| %s | %s | %s | %s%s | %s → %s |" % (
                fmt(parse_ts(c["when"])), c["author"], c["key"], mark, c["label"],
                (c["from"] or "—").replace("|", "/").replace("\n", " ")[:60],
                (c["to"] or "—").replace("|", "/").replace("\n", " ")[:60]))
        lines.append("")

    if stuck:
        lines.append("## Без движения больше %d дн." % stuck_days)
        lines.append("")
        for m, d in stuck[:20]:
            lines.append("- [%s](%s) — %s · %s · %d дн. без изменений" % (
                m["key"], m["url"], (m.get("summary") or "")[:60], m.get("status", "—"), d))
        lines.append("")

    links = [l for l in root.get("links", []) if l.get("key")]
    if links:
        lines.append("## Связи корневой задачи")
        lines.append("")
        for l in links:
            lines.append("- [%s](%s) — %s (%s, %s) %s" % (
                l["key"], l["url"], l["status"], l["type"], l["direction"], (l["summary"] or "")[:60]))
        lines.append("")

    lines.append("---")
    lines.append("Данные — из Jira (REST API v2), без правок. Вопросы к данным («почему застряло», "
                 "«что уточнить у команды») задаются по этому дайджесту.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Выгрузка семьи задач Jira: статусы и изменения")
    ap.add_argument("task", nargs="?", help="ключ (PB-7986) или ссылка на задачу Jira")
    ap.add_argument("--board", help="режим спринта: доска команды (id или часть названия) — берутся задачи активного спринта")
    ap.add_argument("--sprint", dest="sprint_ref", help="уточнить спринт доски: id или часть названия (если активных несколько)")
    ap.add_argument("--project", help="фильтр спринта по проекту, например PB")
    ap.add_argument("--component", help="фильтр спринта по компоненте команды")
    ap.add_argument("--assignee", help="фильтр спринта по исполнителю (часть имени)")
    ap.add_argument("--days", type=int, default=7, help="окно изменений, дней (по умолчанию 7)")
    ap.add_argument("--stuck-days", type=int, default=14, help="порог «нет движения», дней (по умолчанию 14)")
    ap.add_argument("--max-children", type=int, default=500, help="лимит задач (по умолчанию 500)")
    ap.add_argument("--workers", type=int, default=8, help="параллельных запросов changelog (по умолчанию 8)")
    ap.add_argument("--out", help="папка для снапшота и markdown (обычно tasks/<слаг>/06-реализация)")
    ap.add_argument("--no-changelog", action="store_true", help="без истории изменений (быстро)")
    ap.add_argument("--json-only", action="store_true", help="только JSON, без markdown")
    ap.add_argument("--all-changes", action="store_true", help="показывать и служебные изменения (связи и пр.)")
    ap.add_argument("--brief", action="store_true", help="без таблицы задач: только сводка по статусам, изменения и застой")
    args = ap.parse_args()

    if not TOKEN:
        raise SystemExit("Не задан JIRA_TOKEN (возьми из /opt/data/.env): source /opt/data/.env")

    key = norm_key(args.task) if args.task else ""
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    if args.board:
        root, members, notes = sprint_family(args.board, args.max_children, args.project, args.component, args.assignee, args.sprint_ref)
        key = "sprint-%s" % re.sub(r"[^0-9A-Za-z]+", "-", root["key"]).strip("-")
    else:
        if not args.task:
            raise SystemExit("Укажи задачу (ключ или ссылку) или доску через --board")
        root, members, notes = family(key, args.max_children)

    changes = []
    if not args.no_changelog:
        changes = collect_changes([m["key"] for m in members], cutoff, args.workers)

    previous = find_previous(args.out, key)
    digest = render(root, members, changes, cutoff, args.days, args.stuck_days, notes, previous, args.all_changes, not args.brief, not args.no_changelog)

    snapshot = {
        "generated_at": datetime.now(MSK).isoformat(),
        "days": args.days,
        "root": root,
        "members": members,
        "changes": changes,
    }

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        stamp = datetime.now(MSK).strftime("%Y-%m-%d")
        json_path = os.path.join(args.out, "snapshot-%s-%s.json" % (key, stamp))
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, ensure_ascii=False, indent=2)
        if not args.json_only:
            md_path = os.path.join(args.out, "digest-%s-%s.md" % (key, stamp))
            with open(md_path, "w", encoding="utf-8") as fh:
                fh.write(digest + "\n")
            print("markdown: %s" % md_path)
        print("снапшот:  %s" % json_path)

    if args.json_only:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print()
        print(digest)
        if not args.out:
            print("\nАртефакты по задаче складываются в её папку — tasks/<слаг>/06-реализация/ "
                  "(укажи путь флагом --out).")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print("Ошибка: %s" % e, file=sys.stderr)
        sys.exit(2)
