#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Самопроверка движков шага 6 — не тест-сьют, а быстрый прогон изменённого поведения.

    python3 selfcheck.py            # всё, включая живые запросы к Jira
    python3 selfcheck.py --offline  # только чистые функции и сборка отчёта, без сети

Проверяет: разбор ключа, вывод в МСК, фильтр служебных изменений, дифф с прошлым
снапшотом, сбор кандидатов-источников, коды выхода и форматы файлов выгрузки.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DIGEST = os.path.join(HERE, "jira_task_digest.py")
MATERIAL = os.path.join(HERE, "jira_requirement_material.py")
RESTORE = os.path.join(HERE, "jira_restore_description.py")
MSK = timezone(timedelta(hours=3))
OK, FAIL = [], []


def check(name, cond, extra=None):
    (OK if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + ("" if cond else " :: " + str(extra)[:300]))


def section(title):
    print("\n" + title)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, path
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def env():
    for line in open("/opt/data/.env", encoding="utf-8", errors="replace"):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k, v)


def run(script, *args, env_extra=None, timeout=180):
    e = dict(os.environ)
    e.update(env_extra or {})
    p = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, env=e, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def stub_jira():
    """Локальная заглушка Jira: GET отдаёт описание, PUT его меняет (умеет портить текст)."""
    store, log = {"desc": "", "mangle": False}, []

    class H(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # noqa: A002 — сигнатура как у базового класса
            pass

        def do_GET(self):
            log.append("GET")
            body = json.dumps({"fields": {"description": store["desc"], "summary": "Заглушка"}}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_PUT(self):
            n = int(self.headers.get("Content-Length") or 0)
            desc = json.loads(self.rfile.read(n) or b"{}").get("fields", {}).get("description", "")
            log.append("PUT")
            store["desc"] = desc + "\n(искажено сервером)" if store["mangle"] else desc
            self.send_response(204)
            self.end_headers()

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, store, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="без запросов к Jira")
    args = ap.parse_args()
    env()

    d, m = load(DIGEST, "jtd"), load(MATERIAL, "jrm")

    section("1) разбор ключа и даты")
    check("ключ из ссылки с параметрами", d.norm_key("https://jira.iiko.ru/browse/PB-7986?focusedId=1") == "PB-7986")
    check("ключ из нижнего регистра", d.norm_key("pb-8063") == "PB-8063")
    try:
        d.norm_key("нет ключа"); check("мусор → выход с ошибкой", False, "SystemExit не брошен")
    except SystemExit:
        check("мусор → выход с ошибкой", True)
    check("время печатается в МСК", d.fmt(d.parse_ts("2026-10-09T11:54:00.000+0300")) == "09.10.2026 11:54")
    check("пустая дата не падает", d.parse_ts(None) is None)

    section("2) отчёт: фильтр служебных изменений, застой, дифф со снапшотом")
    now, iso = datetime.now(MSK), lambda dt: dt.isoformat()
    root = {"key": "PB-1", "url": "u", "type": "Epic", "summary": "Эпик", "status": "Open", "status_category": "To Do",
            "assignee": "Иван", "created": iso(now - timedelta(days=60)), "updated": iso(now), "links": []}
    child = {"key": "PB-2", "url": "u2", "type": "Story", "summary": "Ребёнок", "status": "In dev",
             "status_category": "In Progress", "assignee": "Пётр", "created": iso(now - timedelta(days=50)),
             "updated": iso(now - timedelta(days=40))}
    changes = [{"key": "PB-2", "when": iso(now - timedelta(days=1)), "author": "Пётр", "field": "status",
                "label": "статус", "interesting": True, "from": "Open", "to": "In dev"},
               {"key": "PB-1", "when": iso(now - timedelta(days=2)), "author": "Пётр", "field": "Epic Child",
                "label": "Epic Child", "interesting": False, "from": "", "to": "PB-2"}]
    snap = lambda keys: {"file": "snapshot-PB-1-2026-10-08.json", "data": {"members": [{"key": k} for k in keys]}}
    md = d.render(root, [root, child], changes, now - timedelta(days=7), 7, 14, [], snap(["PB-1", "PB-2"]))
    check("служебное изменение не попадает в таблицу", "Epic Child" not in md.split("## Что изменилось")[-1])
    check("но сказано, сколько служебных скрыто", "скрыто: 1" in md)
    check("значимое изменение показано", "Open → In dev" in md)
    check("застой без движения найден", "PB-2" in md.split("Без движения")[-1])
    check("новых задач нет — так и написано", "новых задач нет" in md)
    check("новая задача против снапшота названа",
          "новых задач: PB-2" in d.render(root, [root, child], changes, now - timedelta(days=7), 7, 14, [], snap(["PB-1"])))
    md_all = d.render(root, [root, child], changes, now - timedelta(days=7), 7, 14, [], None, True)
    check("--all-changes отдаёт служебные", "Epic Child" in md_all)
    brief = d.render(root, [root, child], changes, now - timedelta(days=7), 7, 14, [], None, False, False)
    check("режим --brief: сводка есть, таблицы задач нет",
          "## Коротко" in brief and "| Ключ | Тип |" not in brief and "не выводится" in brief)
    check("сводка обрезается по лимиту с остатком",
          d.top_list([("a", 3), ("b", 1), ("c", 2)], 2) == "a — 3; c — 2; ещё 1")
    check("--no-changelog честно говорит, что история не считалась",
          "не считались" in d.render(root, [root, child], changes, now - timedelta(days=7), 7, 14, [], None, False, True, False))
    check("без снапшота строки диффа нет", "С прошлой выгрузки" not in md_all)

    section("3) материал для актуализации: срез текста и каналы поиска источника")
    check("длинный текст режется", m.clip("x" * 100, 10).endswith("(сокращено)"))
    check("короткий текст не трогается", m.clip("коротко", 10) == "коротко")
    orig = m.api
    setattr(m, "api", lambda path, params=None: {"issues": [{"key": "PB-13", "fields": {}}]})  # сеть не трогаем
    found, order = m.candidates({"key": "PB-10", "links": [{"key": "WEB-1", "type": "Relates", "direction": "relates to"}],
                                 "subtasks": ["PB-11"], "parent": "PB-12"}, ["WEB-2"], 30)
    setattr(m, "api", orig)
    check("найдены связь, подзадача, родитель, явный ключ, упоминание",
          set(order) == {"WEB-1", "PB-11", "PB-12", "WEB-2", "PB-13"}, order)
    check("дублей нет", len(order) == len(set(order)))
    check("причина связи сохранена", found["WEB-1"].startswith("relates to") and found["PB-11"] == "подзадача")

    section("3b) откат описания из бэкапа: чтение файла")
    r = load(RESTORE, "jrd")
    box_holder = tempfile.TemporaryDirectory(prefix="hermes-verify-selfcheck-")
    path = os.path.join(box_holder.name, "backup.txt")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("h2. Текст\r\n\r\n|a|b|")
    check("бэкап читается без перевода переводов строк", r.read_backup(path) == "h2. Текст\r\n\r\n|a|b|", repr(r.read_backup(path)[:20]))
    try:
        r.read_backup(path + ".нет"); check("нет файла → понятная ошибка вместо трейсбека", False, "SystemExit не брошен")
    except SystemExit as e:
        check("нет файла → понятная ошибка вместо трейсбека", "Не читается файл-бэкап" in str(e), str(e)[:80])

    section("4) откат описания: запись против локальной заглушки Jira (прод не трогаем)")
    srv, store, log = stub_jira()
    url = "http://127.0.0.1:%d" % srv.server_port
    box_holder = tempfile.TemporaryDirectory(prefix="hermes-verify-selfcheck-")
    box = box_holder.name
    old = os.path.join(box, "old.txt")
    new = os.path.join(box, "new.txt")
    for path, text in ((old, "h2. Старое\n|a|b|"), (new, "h2. Новое\n{{userId}} остаётся")):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    def restore(*args, token="test-token"):
        return run(RESTORE, *args, env_extra={"JIRA_URL": url, "JIRA_TOKEN": token}, timeout=60)

    store["desc"], log[:] = "что-то в Jira", []
    rc, out, _ = restore("PB-1", new)
    check("без --apply не пишет", rc == 0 and "это проверка" in out and "PUT" not in log, log)
    store["desc"] = "старое"
    log.clear()
    rc, out, _ = restore("PB-1", new, "--apply")
    check("--apply пишет файл и сверяет чтением обратно",
          rc == 0 and store["desc"] == open(new, encoding="utf-8", newline="").read() and "совпадает с бэкапом: True" in out, log)
    store["mangle"] = True
    rc, out, err = restore("PB-1", old, "--apply")
    check("искажение при записи ловится: код 2 без ложного успеха", rc == 2 and "ПРОВЕРКА НЕ ПРОШЛА" in err and "True" not in out, (rc, err[:120]))
    store["mangle"], store["desc"], log[:] = False, open(old, encoding="utf-8", newline="").read(), []
    rc, out, _ = restore("PB-1", old, "--apply")
    check("описания совпадают — записи нет", rc == 0 and "менять нечего" in out and "PUT" not in log, log)
    rc, out, err = restore("PB-1", os.path.join(box, "нет.txt"))
    check("нет файла бэкапа → понятная ошибка без трейсбека",
          rc != 0 and "Не читается файл-бэкап" in err + out and "Traceback" not in err, (rc, err[:120]))
    srv.shutdown()

    if args.offline:
        section("5) живые прогоны пропущены (--offline)")
    elif not os.environ.get("JIRA_TOKEN"):
        section("5) живые прогоны пропущены: нет JIRA_TOKEN (source /opt/data/.env)")
    else:
        section("5) живые прогоны по Jira")
        tmp_holder = tempfile.TemporaryDirectory(prefix="hermes-verify-step6-")
        tmp = tmp_holder.name
        rc, out, err = run(DIGEST, "PB-8063", "--days", "30", "--out", tmp)
        check("выгрузка отработала", rc == 0, err)
        check("корень и подзадача в таблице", "PB-8063" in out and "PB-8064" in out)
        check("файлы выгрузки созданы", {f.split("-")[0] for f in os.listdir(tmp)} == {"digest", "snapshot"}, str(os.listdir(tmp)))
        rc2, out2, err2 = run(DIGEST, "PB-8063", "--days", "1", "--no-changelog", "--out", tmp)
        check("повторный прогон видит прошлый снапшот", rc2 == 0 and "С прошлой выгрузки" in out2, err2)
        snap_file = sorted(f for f in os.listdir(tmp) if f.startswith("snapshot-PB-8063"))[-1]
        check("снапшот — валидный JSON нужной формы",
              set(json.load(open(os.path.join(tmp, snap_file)))) >= {"generated_at", "root", "members", "changes"})
        rc3, out3, err3 = run(MATERIAL, "PB-8063", "--days", "30", "--comments", "3", "--out", tmp)
        check("материал отработал", rc3 == 0, err3)
        check("секции материала на месте", all(s in out3 for s in ("## 1. Что зафиксировано", "## 2. Кандидаты-источники", "## 3. Что делать дальше")))
        check("файлы материала созданы", any(f.startswith("material-PB-8063") for f in os.listdir(tmp)))
        rc4, out4, _ = run(DIGEST, "PB-8063", "--json-only", "--no-changelog")
        check("--json-only парсится", rc4 == 0 and json.loads(out4)["root"]["key"] == "PB-8063")
        rc5, out5, err5 = run(MATERIAL, "мусор-без-ключа")
        check("мусорный ключ → ненулевой код", rc5 != 0 and "Не понял задачу" in err5 + out5)
        rc6, out6, err6 = run(DIGEST, "PB-8063", env_extra={"JIRA_TOKEN": ""})
        check("без токена — понятная ошибка", rc6 != 0 and "JIRA_TOKEN" in out6 + err6)
        rc7, out7, err7 = run(DIGEST, "--board", "iiko Web Features", "--days", "1", "--no-changelog", "--brief")
        check("режим спринта: активный спринт доски собран",
              rc7 == 0 and "Спринт" in out7 and "задач в спринте:" in out7, (rc7, err7[:150]))
        rc8, out8, err8 = run(DIGEST, "--board", "нет-такой-доски-в-jira")
        check("несуществующая доска → понятная ошибка", rc8 != 0 and "не найдена" in out8 + err8)
        rc9, out9, err9 = run(DIGEST)
        check("без задачи и без доски → подсказка", rc9 != 0 and "Укажи задачу" in out9 + err9)
        rc10, out10, err10 = run(DIGEST, "--board", "322", "--sprint", "9.9.1", "--no-changelog", "--brief")
        check("явный выбор спринта (--sprint) работает",
              rc10 == 0 and "9.9.1" in out10 and "несколько спринтов" in out10, (rc10, err10[:150]))
        cut = re.search(r"больше лимита: собрано (\d+) из (\d+)", out10)
        check("обрезание по лимиту помечено, а не молчит",
              bool(cut) and cut.group(1) == "500" and int(cut.group(2)) > 500 and "--max-children" in out10,
              out10[-300:])
        rc11, out11, err11 = run(DIGEST, "--board", "322", "--sprint", "нет-такого-спринта")
        check("несуществующий спринт → понятная ошибка", rc11 != 0 and "нет «" in out11 + err11)

    section("6) правила хранения: артефакты — в папке задачи, а не в шаге")
    step6 = os.path.dirname(HERE)
    check("папки examples в шаге 6 нет", not os.path.isdir(os.path.join(step6, "examples")),
          os.path.join(step6, "examples"))
    for sk in ("jira-task-digest", "requirement-actualization"):
        path = os.path.join(step6, "skills", sk, "SKILL.md")
        text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        check("скилл %s: правило раскладки в папку задачи" % sk, "tasks/<слаг>/06-реализация/" in text)
    readme = open(os.path.join(step6, "README.md"), encoding="utf-8").read()
    check("README шага: раздел про раскладку артефактов", "Куда складываются артефакты шага" in readme)
    check("скрипты напоминают, куда складывать артефакты",
          "tasks/<слаг>/06-реализация/" in open(DIGEST, encoding="utf-8").read()
          and "tasks/<слаг>/06-реализация/" in open(MATERIAL, encoding="utf-8").read())

    print("\nИТОГ: %d PASS, %d FAIL" % (len(OK), len(FAIL)))
    if FAIL:
        print("провалилось: " + ", ".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
