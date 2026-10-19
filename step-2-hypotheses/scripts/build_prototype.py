#!/usr/bin/env python3
"""Собирает HTML-прототип со встроенным списком гипотез.

Использование:
    python3 build_prototype.py <list.json> [<out.html>]

Берёт prototype/ocenka-gipotez_kalkulyator.html, встраивает данные списка
(window.__HYPOTHESES__) и пишет готовый файл в build/<list-id>.html.
Такой файл открывается двойным щелчком и сразу показывает нужный список.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototype" / "ocenka-gipotez_kalkulyator.html"
OUT_DIR = ROOT / "build"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = pathlib.Path(sys.argv[1]).resolve()
    data = json.loads(src.read_text(encoding="utf-8"))
    html = PROTO.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    snippet = "<script>window.__HYPOTHESES__ = " + payload + ";</script>\n"
    # данные должны попасть в страницу ДО скрипта приложения — вставляем сразу после <body>
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + snippet, 1)
    elif "</head>" in html:
        html = html.replace("</head>", snippet + "</head>", 1)
    else:
        raise SystemExit("в прототипе нет ни <body>, ни </head> — файл повреждён")
    lid = (data.get("list") or {}).get("id") or src.stem
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DIR / f"{lid}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"собрано: {out} · гипотез {len(data.get('items') or [])} · {out.stat().st_size} байт")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
