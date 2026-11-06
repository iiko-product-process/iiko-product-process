#!/usr/bin/env python3
"""Прототип Шага 2 как веб-сервис: раздаёт калькулятор гипотез и хранит списки в репозитории.

Запуск (из любой папки):
    python3 serve.py --port 8788 [--host 0.0.0.0] [--auth пользователь:пароль] [--repo /opt/data/iiko-product-process]

Что делает:
  GET  /                        — прототип; при ?list=<id> данные списка встраиваются в страницу
  GET  /api/lists               — оглавление списков: id, название, тип, проблема, число гипотез
  GET  /api/lists/<id>          — список целиком
  PUT  /api/lists/<id>          — сохранить список (тело: {list, goals, items}) → файл в репозитории + коммит и пуш
  POST /api/lists               — создать список: {"title": "...", "problem": "..."} → id генерируется
  GET  /healthz                 — проверка живости

Скрипт использует только стандартную библиотеку. Авторизация — HTTP Basic (по умолчанию выключена).
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]          # 02-hypotheses/
PROTO = ROOT / "prototype" / "ocenka-gipotez_kalkulyator.html"
REPO = ROOT.parent                                          # iiko-product-process/
LISTS = ROOT / "data" / "lists"
AGGREGATE = ROOT / "scripts" / "aggregate.py"

DEFAULT_GOALS = [
    {"id": "ns", "name": "North Star 2027", "g": 2.0, "kind": "north"},
    {"id": "g32", "name": "Годовая: цифровизация процессов, +20% критичных", "g": 1.7, "kind": "year"},
    {"id": "q", "name": "Квартальная: OKR продукта", "g": 1.4, "kind": "quarter"},
    {"id": "sup", "name": "Поддерживающие задачи", "g": 1.0, "kind": "support"},
    {"id": "bg", "name": "Эксперименты и фон", "g": 0.8, "kind": "bg"},
    {"id": "must", "name": "Обязательное: закон, безопасность", "g": 0, "kind": "must"},
]

AUTH: str | None = None          # "user:pass" или None
GIT_LOCK = threading.Lock()

# --- канал «сайт → Hermes»: страница просит агента добавить гипотезы в список ---
HERMES_BIN = os.environ.get("HERMES_BIN", "/opt/hermes/.venv/bin/hermes")
ASK_TASKS: dict[str, dict] = {}          # task_id -> {status, list, started, output, seconds}
ASK_LOCK = threading.Lock()
ASK_RUNNING: str | None = None           # id задачи, которая сейчас выполняется
ASK_TIMEOUT = 900                        # 15 минут на прогон агента

# Все запросы с сайта идут в ОДИН чат десктоп-клиента: id сессии хранится в файле,
# при первом запросе он определяется сам, сессия переименовывается в понятное название.
ASK_SESSION_FILE = pathlib.Path(os.environ.get("HERMES_ASK_SESSION_FILE", "/opt/data/hypoproto-ask-session.txt"))
ASK_SESSION_TITLE = os.environ.get("HERMES_ASK_SESSION_TITLE", "🤖 Сайт → Hermes (гипотезы)")

ASK_PROMPT = """Запрос с сайта прототипа «Списки гипотез» (кнопка «Спросить Hermes»). Отвечай в этом же чате одной короткой строкой-итогом.

Работай по скиллу iiko-hypotheses. Репозиторий: /opt/data/iiko-product-process, папка шага: 02-hypotheses.

Продакт просит через сайт прототипа дополнить список гипотез.
Список: «{title}» (id: {lid}, файл data/lists/{lid}.json).
Запрос продакта: "{text}"

Что сделать:
1) добавь 1–3 гипотезы строго в формате «Если …, тогда …, так как …»; у каждой метрика baseline → target (нет данных — пиши «baseline уточнить»), источник данных, оценки I/C/E по анкерам скилла, цели с α (не больше двух, Σα = 1);
2) впиши их в data/lists/{lid}.json, существующие гипотезы и массив goals не меняй; id новых — h<номер>-<смысл>; у каждой новой гипотезы обязательно поле "by":"hermes" (интерфейс покажет бейдж «🤖 Hermes» — так видно, что её предложил агент, а не человек);
3) прогони python3 scripts/aggregate.py (он синхронизирует общий список);
4) закоммить локально, без пуша: git add -A && git commit -m "Шаг 2: гипотезы из прототипа — <кратко>";
5) закончи ответ одной строкой: сколько гипотез добавлено и о чём (без markdown).
"""


ASK_PROMPT_TASK = """Запрос с сайта прототипа «Списки гипотез» (кнопка «Создать задачу»). Отвечай в этом же чате одной короткой строкой-итогом.

Работай по скиллу iiko-hypotheses. Репозиторий: /opt/data/iiko-product-process, папка шага: 02-hypotheses.

Продакт отобрал галочками гипотезы в списке «{title}» (id: {lid}, файл data/lists/{lid}.json) и просит оформить их в Jira.

Что сделать:
1) создай ОДНУ задачу в Jira на весь отобранный набор: проект PB, тип Story; гипотезы не разбивать на разные задачи; обязательно добавь label `Hermes` — по нему отслеживаем задачи, заведённые с Hermes, и он не заменяется другими метками;
2) Summary — по общему смыслу набора (если длиннее ~120 символов — сжать); Description — требования: как реализовать отобранные гипотезы в рамках этой задачи (что должно появиться в продукте и из чего состоят механизмы). Данные гипотез в описание НЕ дублировать — формулировки, метрики, источники данных, оценки I/C/E, баллы и цели с α остаются только на странице списка гипотез. Оформляй по формату шага 3 (скилл pb-task-writer): цель, AS-IS/TO-BE, требования, критерии приёмки, зависимости, out of scope; в конце — ссылка на инструмент;
3) заполни `scoreWSJF` (`customfield_14743`) баллом ICEG = I × C × E × G по отобранным гипотезам — бери гипотезу с наибольшим баллом, число должно совпадать с баллом в списке шага 2; в конце описания добавь 2–3 строки обоснования («**Приоритет (ICEG): X** — I=…, C=…, E=…, G=…; почему так»). Если у гипотезы не проставлена цель — сначала уточни у продакта, на какую цель работает задача; если ответа нет, предположи цель по описанию, возьми её вес и пометь в обосновании «предположение, требует подтверждения PO»; `G = 1.0` — только если целей нет во всём списке. I/C/E/G уже есть в списке гипотез, в описание их не дублируй, только в обосновании;
4) после создания впиши ключ задачи в поле "jira" каждой отобранной гипотезы в data/lists/{lid}.json (остальные поля не менять), прогони python3 scripts/aggregate.py, закоммить и запушь;
5) закончи ответ одной строкой: ключ и ссылка задачи + одна фраза, о чём она (без markdown).

Запрос продакта: "{text}"
"""

_TRANSLIT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
})


def slug(text: str) -> str:
    """«Проверочная проблема» → «proverochnaya-problema» (латиница для имён файлов)."""
    latin = (text or "").lower().translate(_TRANSLIT)
    return re.sub(r"[^a-z0-9]+", "-", latin).strip("-") or "spisok"


def list_files() -> dict[str, pathlib.Path]:
    return {p.stem: p for p in sorted(LISTS.glob("*.json"))}


def read_list(lid: str) -> dict | None:
    f = list_files().get(lid)
    if not f:
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def index() -> list[dict]:
    out = []
    for lid, f in list_files().items():
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        m = d.get("list") or {}
        out.append({"id": lid, "title": m.get("title") or lid, "type": m.get("type") or "general",
                    "problem": m.get("problem"), "count": len(d.get("items") or []),
                    "updated": m.get("updated")})
    return out


def git_commit(message: str) -> str:
    """Коммит изменений списков локально (без пуша). Возвращает короткий отчёт.

    Пуш отключён: по процессу сотрудник не публикует в репозиторий — изменения
    вносит администратор. Локальный коммит нужен только как точка истории.
    """
    if not (REPO / ".git").exists():
        return "репозиторий не найден рядом со скриптом — коммит пропущен"
    with GIT_LOCK:
        try:
            # коммитим только данные списков: прочие правки репозитория — дело рук человека
            subprocess.run(["git", "-C", str(REPO), "add", "02-hypotheses/data"], check=True, capture_output=True, timeout=60)
            diff = subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--quiet"], capture_output=True)
            if diff.returncode == 0:
                return "изменений нет"
            subprocess.run(["git", "-C", str(REPO), "commit", "-m", message], check=True, capture_output=True, timeout=60)
            return "сохранено в локальный клон (публикует администратор)"
        except Exception as exc:  # noqa: BLE001
            return f"ошибка git: {exc}"


def run_aggregate() -> str:
    try:
        r = subprocess.run([sys.executable, str(AGGREGATE)], capture_output=True, timeout=120)
        return (r.stdout or b"").decode("utf-8", "replace").strip()
    except Exception as exc:  # noqa: BLE001
        return f"ошибка aggregate: {exc}"


class Handler(BaseHTTPRequestHandler):
    server_version = "hypoproto/1.0"

    # ---------- утилиты ----------
    def log_message(self, format, *args):  # тише в логах  # noqa: A002
        sys.stderr.write("[hypoproto] " + (format % args) + "\n")

    def _auth_ok(self) -> bool:
        if not AUTH:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            given = base64.b64decode(header[6:]).decode("utf-8")
        except Exception:  # noqa: BLE001
            return False
        return given == AUTH

    def _need_auth(self) -> None:
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="hypotheses"')
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _send(self, code: int, body: bytes, ctype: str = "application/json; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    # ---------- маршруты ----------
    def do_GET(self) -> None:  # noqa: N802
        if not self._auth_ok():
            return self._need_auth()
        url = urllib.parse.urlparse(self.path)
        path, query = url.path, urllib.parse.parse_qs(url.query)

        if path == "/healthz":
            return self._json(200, {"status": "ok", "lists": len(list_files())})

        if path == "/api/lists":
            return self._json(200, {"lists": index()})

        m = re.fullmatch(r"/api/lists/([A-Za-z0-9._-]+)", path)
        if m:
            d = read_list(m.group(1))
            return self._json(200, d) if d else self._json(404, {"error": "список не найден"})

        m = re.fullmatch(r"/api/ask/([0-9a-f]{6,32})", path)
        if m:
            task = ASK_TASKS.get(m.group(1))
            if not task:
                return self._json(404, {"error": "задача не найдена"})
            out = dict(task)
            out["seconds"] = round(time.time() - task["started"], 1)
            return self._json(200, {"task": m.group(1), **out})

        if path in ("/", "/index.html"):
            return self._page(query.get("list", [None])[0])

        return self._json(404, {"error": "не найдено"})

    def do_PUT(self) -> None:  # noqa: N802
        if not self._auth_ok():
            return self._need_auth()
        m = re.fullmatch(r"/api/lists/([A-Za-z0-9._-]+)", urllib.parse.urlparse(self.path).path)
        if not m:
            return self._json(404, {"error": "не найдено"})
        lid = m.group(1)
        try:
            data = self._body()
        except Exception as exc:  # noqa: BLE001
            return self._json(400, {"error": f"некорректный JSON: {exc}"})
        items = data.get("items")
        if not isinstance(items, list):
            return self._json(400, {"error": "в теле нет массива items"})
        meta = data.get("list") or {}
        meta["id"] = lid
        meta["title"] = meta.get("title") or lid
        meta["updated"] = time.strftime("%Y-%m-%d")
        data["list"] = meta
        data.setdefault("goals", DEFAULT_GOALS)
        LISTS.mkdir(parents=True, exist_ok=True)
        (LISTS / f"{lid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        agg = run_aggregate()
        report = git_commit(f"Списки гипотез: {meta['title']} ({len(items)} шт.)")
        return self._json(200, {"ok": True, "id": lid, "items": len(items), "aggregate": agg, "git": report})

    def do_POST(self) -> None:  # noqa: N802
        if not self._auth_ok():
            return self._need_auth()
        route = urllib.parse.urlparse(self.path).path
        if route == "/api/ask":
            return self._ask_start()
        if route != "/api/lists":
            return self._json(404, {"error": "не найдено"})
        try:
            body = self._body()
        except Exception as exc:  # noqa: BLE001
            return self._json(400, {"error": f"некорректный JSON: {exc}"})
        title = (body.get("title") or "").strip()
        problem = (body.get("problem") or "").strip()
        if not title:
            return self._json(400, {"error": "нужно поле title"})
        # id — из названия (коротко и предсказуемо), а не из текста проблемы
        lid = ("problema-" if (problem or body.get("type") == "problem") else "") + slug(title)[:48].rstrip("-")
        if (LISTS / f"{lid}.json").exists():
            return self._json(409, {"error": f"список {lid} уже есть — поменяйте название"})
        data = {"list": {"id": lid, "title": title, "type": "problem" if problem else "general",
                         "problem": problem or None, "created": time.strftime("%Y-%m-%d"),
                         "updated": time.strftime("%Y-%m-%d")},
                "goals": DEFAULT_GOALS, "items": []}
        (LISTS / f"{lid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        agg = run_aggregate()
        report = git_commit(f"Новый список гипотез: {title}")
        return self._json(201, {"ok": True, "id": lid, "aggregate": agg, "git": report})

    # ---------- канал «сайт → Hermes» ----------
    @staticmethod
    def _ask_session_id() -> str | None:
        """id чата, в который складываются все запросы с сайта."""
        try:
            return ASK_SESSION_FILE.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    @staticmethod
    def _ask_session_save(sid: str) -> None:
        try:
            ASK_SESSION_FILE.write_text(sid + "\n", encoding="utf-8")
        except OSError:
            pass

    @staticmethod
    def _ask_newest_session_since(ts: float) -> str | None:
        """id самой свежей сессии, созданной после ts (state.db доступен только на чтение)."""
        try:
            import sqlite3
            db = pathlib.Path(os.environ.get("HERMES_STATE_DB", "/opt/data/state.db"))
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            try:
                row = con.execute(
                    "SELECT id FROM sessions WHERE started_at >= ? AND source = 'desktop' "
                    "ORDER BY started_at DESC LIMIT 1", (ts - 5,)).fetchone()
                if row:
                    return row[0]
                row = con.execute(
                    "SELECT id FROM sessions WHERE last_activity_at >= ? "
                    "ORDER BY last_activity_at DESC LIMIT 1", (ts - 5,)).fetchone()
                return row[0] if row else None
            finally:
                con.close()
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _ask_session_forget() -> None:
        try:
            ASK_SESSION_FILE.unlink()
        except OSError:
            pass

    def _ask_run_agent(self, prompt: str, sid: str | None):
        """Один прогон агента. С sid — продолжаем тот же чат, без sid — создаём новый."""
        cmd = [HERMES_BIN, "chat", "-q", prompt, "-Q", "--yolo", "-s", "iiko-hypotheses", "--no-restore-cwd"]
        if sid:
            cmd += ["--resume", sid]
        env = dict(os.environ, HOME="/opt/data")
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=ASK_TIMEOUT)
        out = proc.stdout or ""
        m = re.search(r"^session_id:\s*(\S+)\s*$", out, re.M)
        new_sid = m.group(1) if m else None
        lines = [l.strip() for l in out.splitlines()
                 if l.strip() and not l.strip().startswith(("session_id:", "↻"))]
        message = lines[-1] if lines else "нет финального ответа агента"
        return proc.returncode, new_sid, message
    def _ask_start(self) -> None:
        global ASK_RUNNING
        try:
            body = self._body()
        except Exception as exc:  # noqa: BLE001
            return self._json(400, {"error": f"некорректный JSON: {exc}"})
        lid = (body.get("list") or "").strip()
        text = (body.get("text") or "").strip()
        mode = (body.get("mode") or "ask").strip()
        if mode not in ("ask", "task"):
            return self._json(400, {"error": "mode должен быть ask или task"})
        if not lid or not text:
            return self._json(400, {"error": "нужны поля list и text"})
        data = read_list(lid)
        if not data:
            return self._json(404, {"error": f"список {lid} не найден"})
        if len(text) > 2000:
            return self._json(400, {"error": "запрос слишком длинный (до 2000 знаков)"})
        if not pathlib.Path(HERMES_BIN).exists():
            return self._json(500, {"error": f"не найден агент {HERMES_BIN}"})
        with ASK_LOCK:
            if ASK_RUNNING:
                return self._json(409, {"error": "Hermes уже занят другим запросом — подождите"})
            task_id = uuid.uuid4().hex[:12]
            ASK_RUNNING = task_id
            ASK_TASKS[task_id] = {"status": "running", "list": lid, "started": time.time(), "output": ""}
        threading.Thread(target=self._ask_run, args=(task_id, lid, data.get("list", {}).get("title") or lid, text, mode),
                         daemon=True).start()
        return self._json(202, {"ok": True, "task": task_id, "list": lid})

    def _ask_run(self, task_id: str, lid: str, title: str, text: str, mode: str = "ask") -> None:
        global ASK_RUNNING
        template = ASK_PROMPT_TASK if mode == "task" else ASK_PROMPT
        prompt = template.format(title=title, lid=lid, text=text.replace('"', "'"))
        sid = self._ask_session_id()
        session_note = ""
        started = time.time()
        try:
            code, new_sid, message = self._ask_run_agent(prompt, sid)
            if new_sid is None and not sid:
                new_sid = self._ask_newest_session_since(started)
            # сессия-чат потерялась (удалена/архивирована) — один повтор с новой
            if sid and code != 0 and not new_sid:
                self._ask_session_forget()
                started = time.time()
                code, new_sid, message = self._ask_run_agent(prompt, None)
                new_sid = new_sid or self._ask_newest_session_since(started)
                sid = None
            if new_sid and not sid:
                self._ask_session_save(new_sid)
                try:
                    subprocess.run([HERMES_BIN, "sessions", "rename", new_sid, ASK_SESSION_TITLE],
                                   capture_output=True, text=True, timeout=60)
                except Exception:  # noqa: BLE001
                    pass
            session_note = f"чат «{ASK_SESSION_TITLE}»"
            status = "done" if code == 0 else "error"
        except subprocess.TimeoutExpired:
            message, status = f"Hermes не успел за {ASK_TIMEOUT // 60} мин", "timeout"
        except Exception as exc:  # noqa: BLE001
            message, status = f"сбой запуска агента: {exc}", "error"
        with ASK_LOCK:
            ASK_TASKS[task_id].update({"status": status, "message": message[:600],
                                       "session": self._ask_session_id(), "chat": session_note})
            ASK_RUNNING = None

    # ---------- страница ----------
    def _page(self, lid: str | None) -> None:
        html = PROTO.read_text(encoding="utf-8")
        data = read_list(lid) if lid else None
        if data is None:
            first = index()
            lid = first[0]["id"] if first else "obshiy-spisok"
            data = read_list(lid) or {"list": {"id": lid, "title": "Новый список", "type": "general"},
                                      "goals": DEFAULT_GOALS, "items": []}
        # данные и признак серверного режима должны попасть в страницу ДО скрипта приложения
        inject = ("<script>window.__HYPOTHESES__ = " + json.dumps(data, ensure_ascii=False) + ";\n"
                  "window.__SERVER__ = " + json.dumps({"api": "/api", "list": data["list"]["id"]}) + ";</script>\n")
        html = html.replace("<body>", "<body>\n" + inject, 1)
        self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")


def main() -> int:
    global AUTH
    host, port, auth = "0.0.0.0", 8788, None
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--port" and i + 1 < len(argv):
            port = int(argv[i + 1]); i += 2; continue
        if argv[i] == "--host" and i + 1 < len(argv):
            host = argv[i + 1]; i += 2; continue
        if argv[i] == "--auth" and i + 1 < len(argv):
            auth = argv[i + 1]; i += 2; continue
        print(f"неизвестный аргумент: {argv[i]}")
        return 2
    AUTH = auth
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"прототип гипотез: http://{host}:{port}/ · списков {len(list_files())} · "
          f"авторизация {'включена' if AUTH else 'выключена'}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("остановлено")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
