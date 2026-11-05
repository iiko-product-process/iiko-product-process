---
name: matomo-daily-report
description: "Use for daily iiko Matomo report (yesterday, per-page)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [matomo, daily, report, iiko, analytics]
---

# Ежедневный Matomo-отчёт iiko (каждый день, 09:00 МСК)

Данные за **вчера** (полный календарный день), по ВСЕМ разделам приложения (страница = модуль: navigator, purchase, till-shifts…; ~59 шт/день; кросс-доменная агрегация по всем ресторанам).
Рабочая папка: **$HERMES_HOME/matomo_weekly/**.

## Шаги

1. **Выгрузка**: `cd $HERMES_HOME/matomo_weekly && python3 fetch_matomo_daily.py`
   (токен сам читает из $HERMES_HOME/.env; пишет daily.json со всеми разделами и устройствами по каждому разделу).
2. **Сборка прототипа**: `python3 build_daily_dashboard.py` → `daily_dashboard.html`
   (KPI, почасовая активность, устройства дня, топ-12, полная таблица всех страниц).
3. **Датированная копия для отправки** — имя файла = дата ДАННЫХ (вчера), ISO ГГГГ-ММ-ДД:
   `cp daily_dashboard.html reports/matomo_daily_$(date -d yesterday +%F).html`
   В сообщение прикрепляй эту копию, НЕ daily_dashboard.html.
4. **Прочитай** `$HERMES_HOME/matomo_weekly/daily.json` (дата, weekday, totals, devices_total, hourly, pages[]).
5. **Финальное сообщение** (RU, компактное; полные данные — в файле-прототипе):
   - Шапка: «📊 Matomo iiko · вчера, {ДД.ММ} ({день недели})».
   - Блок «Резюме»: уники · визиты · действия · устройства дня.
   - Блок «Топ разделов»: 5–8 строк `• {module} — {уники} уник., {визиты} виз. · D {pct}% / M {pct}%`
     (из p.module/p.uniq/p.visits/p.devices; кратко: Smartphone→M, Desktop→D, Tablet→T, Phablet→P).
     Дополнительно — сравнение с предыдущим днём (взять «Уники/Визиты» из последнего файла $HERMES_HOME/cron/output/d1d15d50171d/*.md) и 3–5 фраз инсайтов (соотношение визит/уника, мобильные vs десктопные разделы).
   - Строка: «Все N страниц — в прототипе» + `MEDIA:$HERMES_HOME/matomo_weekly/reports/matomo_daily_<ГГГГ-ММ-ДД>.html` (файл уйдёт вложением; <ГГГГ-ММ-ДД> = дата данных из шага 3).
   - Примечание, если день неполный/пустой.
   - **Форматирование: смысловые блоки разделяй ПУСТОЙ СТРОКОЙ (`\n\n`).**
6. Не выдумывай цифры; при пустом/битом daily.json — честно скажи и приложи вывод скрипта.

## Pitfalls

- «Вчера» считается по UTC (06:00 UTC = 09:00 МСК — корректно).
- Уники по страницам в дневном архиве есть (nb_uniq_visitors). В daily.json поля host/path/url НЕТ: fetch-скрипт агрегирует по p.module (сегмент по разделу, кросс-доменно), поэтому Σ uniq/visits по pages больше итогов дня (один пользователь = несколько разделов).
- Пик/минимум часа считать по daily.json.hourly (visits); сумма 24 часов сходится с totals.visits — это и есть проверка полноты дня.
- В данных попадаются dev-строки (localhost, «/» без хоста) — в выводах можно отмечать, из таблицы не удалять.
- **Dev-строки не подставлять в сегмент.** Проверено 12.10.26: строка `auth` в Actions.getPageUrls — это localhost `/auth/login` (2 виз.), а сегмент `pageUrl=@/auth` собирает реальный `/navigator/auth/login` (2 664 уник. / 5 296 виз.) → в daily.json строка `auth` показывала чужие цифры и вставала №2 по уникам. С 13.10.26 fetch-скрипт такие строки помечает `dev=true` и оставляет их собственные цифры (0–2). Так же выглядят `order`, `payment-gateways`, `loans`. Похожие dev-адреса видны в flat-выгрузке: `/auth/login`, `/order-list-v2`, `/order/edit/:id`, `/orders/new` — host localhost.
- «Дверь» приложения — `/navigator/auth/login` (в flat-выгрузке ~2,7 тыс. уник./день, ~95% уников модуля navigator), затем `/navigator/home`. Полезно для инсайтов; при путанице модулей смотреть flat `Actions.getPageUrls` (`flat=1`, `filter_limit`).
