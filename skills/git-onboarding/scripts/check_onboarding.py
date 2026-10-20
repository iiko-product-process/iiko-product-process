#!/usr/bin/env python3
"""Замер готовности к онбордингу в git-репозиторий процесса.

Проверяет окружение и, если передан клон, состояние самого репозитория.
Ничего не меняет, токены не печатает. Возвращает 1, если есть блокеры.

    python3 check_onboarding.py
    python3 check_onboarding.py --repo .
    python3 check_onboarding.py --repo ~/iiko-product-process
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

OK, WARN, BLOCK = "ok", "warn", "БЛОКЕР"
RULE_FILES = (".hermes.md", "AGENTS.md", "CLAUDE.md", ".cursorrules")
TOKEN_VARS = ("GITHUB_TOKEN", "GH_TOKEN")
results: list[tuple[str, str, str]] = []


def add(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=25)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


def git(args: list[str], cwd: Path) -> tuple[int, str]:
    return run(["git", *args], cwd=cwd)


def api_status(url: str, token: str | None) -> int:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def check_env() -> str | None:
    if shutil.which("git"):
        add(OK, "git", run(["git", "--version"])[1].splitlines()[0])
    else:
        add(BLOCK, "git", "не найден в PATH")

    add(OK if sys.version_info >= (3, 8) else BLOCK, "python",
        f"{sys.version.split()[0]} (нужно 3.8+)")

    candidates = [Path.home() / ".ssh" / name for name in ("id_ed25519", "id_rsa")]
    if os.environ.get("HERMES_HOME"):
        candidates.insert(0, Path(os.environ["HERMES_HOME"]) / ".ssh" / "id_ed25519")
    key = next((p for p in candidates if p.exists()), None)
    add(OK if key else WARN, "ssh-ключ",
        str(key) if key else "нет ключа в ~/.ssh — клон по SSH не пройдёт, останется HTTPS")

    token = next((os.environ[v] for v in TOKEN_VARS if os.environ.get(v)), None)
    add(OK if token else WARN, "GITHUB_TOKEN",
        "есть" if token else "нет: проверка канона через API недоступна")
    return token


def check_identity(repo: Path | None) -> None:
    cwd = repo if repo else None
    name = run(["git", "config", "--get", "user.name"], cwd)[1]
    email = run(["git", "config", "--get", "user.email"], cwd)[1]
    if not (name and email):
        add(BLOCK, "git identity", "user.name/user.email не заданы — первый коммит упадёт")
        return
    local = run(["git", "config", "--local", "--get", "user.name"], cwd)[1] if repo else ""
    add(OK, "git identity", f"{name} <{email}> ({'local' if local else 'global'})")


def check_api(token: str | None, org: str, slug: str) -> None:
    status = api_status(f"https://api.github.com/repos/{org}/{slug}", token)
    if status == 200:
        add(OK, "доступ к канону", f"{org}/{slug} → 200")
    elif status in (401, 403):
        add(BLOCK, "доступ к канону", f"{org}/{slug} → {status}: токен неверный или без repo/read:org")
    elif status == 404 and not token:
        add(WARN, "доступ к канону", f"{org}/{slug} → 404 без токена: репозиторий приватный")
    elif status == 404:
        add(BLOCK, "доступ к канону", f"{org}/{slug} → 404 с токеном: приглашение не принято")
    else:
        add(WARN, "доступ к канону", f"{org}/{slug} → сеть недоступна или ответ {status}")


def check_repo(repo: Path) -> None:
    code, _ = git(["rev-parse", "--git-dir"], repo)
    if code != 0:
        add(BLOCK, "клон", f"{repo} не git-репозиторий")
        return

    remotes = git(["remote", "-v"], repo)[1]
    add(OK if "origin" in remotes else BLOCK, "remote origin",
        "есть" if "origin" in remotes else "нет — клон не из форка")
    add(OK if "upstream" in remotes else WARN, "remote upstream",
        "есть" if "upstream" in remotes else "нет: git remote add upstream <url канона>")

    if "upstream" in remotes:
        code, out = git(["fetch", "upstream", "--dry-run"], repo)
        add(OK if code == 0 else WARN, "git fetch upstream",
            "проходит" if code == 0 else (out.splitlines()[-1] if out else "не проверено"))

    # База проверки — канон: на ветке personal нет ни INDEX.md, ни .hermes.md
    base = next((ref for ref in ("upstream/main", "origin/main", "HEAD")
                 if git(["rev-parse", "--verify", "-q", ref], repo)[0] == 0), "HEAD")
    files = set(git(["ls-tree", "-r", "--name-only", base], repo)[1].splitlines())

    is_process = "INDEX.md" in files or any(f.startswith("step-") for f in files)
    if not is_process:
        add(WARN, "тип репозитория",
            f"в {base} нет INDEX.md и step-*/ — проверки веток и артефактов пропущены")
    else:
        for name in ("README.md", "INDEX.md", "CONTRIBUTING.md"):
            add(OK if name in files else WARN, name, "есть" if name in files else f"не найден в {base}")
        branches = git(["branch", "-a"], repo)[1]
        add(OK if "personal" in branches else WARN, "ветка personal",
            "есть" if "personal" in branches else "нет: git checkout -b personal upstream/main")
        branch = git(["rev-parse", "--abbrev-ref", "HEAD"], repo)[1]
        add(OK if branch != "main" else WARN, "текущая ветка",
            branch + ("" if branch != "main" else " — артефакты должны быть на personal"))

    in_canon = [f for f in RULE_FILES if git(["cat-file", "-e", f"{base}:{f}"], repo)[0] == 0]
    in_tree = [f for f in RULE_FILES if (repo / f).exists()]
    if in_canon:
        add(OK if len(in_canon) == 1 else WARN, "правила для агента",
            f"из канона: {in_canon[0]}" if len(in_canon) == 1
            else f"в {base} два источника {in_canon}: загрузится только первый по приоритету")
    elif not in_tree:
        add(WARN, "правила для агента", "нет .hermes.md/AGENTS.md — создать по шаблону")
    elif len(in_tree) > 1:
        add(BLOCK, "правила для агента",
            f"в клоне {in_tree}: загрузится только первый по приоритету, остальные молча выключены")
    else:
        add(OK, "правила для агента", f"загрузится {in_tree[0]}")

    if (repo / ".hermes.md").exists() and ".hermes.md" not in in_canon:
        code_ignored = git(["check-ignore", "-q", ".hermes.md"], repo)[0]
        code_tracked = git(["ls-files", "--error-unmatch", ".hermes.md"], repo)[0]
        if code_tracked == 0:
            add(BLOCK, ".hermes.md в индексе", "личный файл закоммичен — убрать из индекса и добавить в .git/info/exclude")
        elif code_ignored == 0:
            add(OK, ".hermes.md вне коммита", "в .git/info/exclude или gitignore")
        else:
            add(WARN, ".hermes.md вне коммита", "не исключён: printf '.hermes.md\\n' >> .git/info/exclude")


def main() -> int:
    ap = argparse.ArgumentParser(description="Проверка готовности к онбордингу в репозиторий процесса")
    ap.add_argument("--repo", help="путь к клону (необязательно)")
    ap.add_argument("--org", default="iiko-product-process")
    ap.add_argument("--slug", default="iiko-product-process", help="имя канона в организации")
    ap.add_argument("--json", action="store_true", help="печатать результат в JSON")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve() if args.repo else None
    token = check_env()
    check_identity(repo)
    check_api(token, args.org, args.slug)
    if repo:
        check_repo(repo)

    if args.json:
        print(json.dumps([{"status": s, "check": n, "detail": d} for s, n, d in results],
                         ensure_ascii=False, indent=2))
    else:
        for status, name, detail in results:
            print(f"{status:<7} {name:<24} {detail}")
        blockers = sum(1 for s, _, _ in results if s == BLOCK)
        warns = sum(1 for s, _, _ in results if s == WARN)
        print(f"\nблокеров: {blockers}, предупреждений: {warns}")
    return 1 if any(s == BLOCK for s, _, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
