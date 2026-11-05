# Админ-операции Matomo: пользователи, инвайты, транзакционная почта, OAuth

Проверено 2026-09-10 на iiko-инстансе `https://analytics.iiko.services` (Matomo **5.11.0**, PHP 8.4.22,
Apache 2.4.67, idSite 1, токен из `$HERMES_HOME/.env` → `MATOMO_TOKEN_AUTH`) — по живым вызовам API
и по исходникам `5.x-dev`.

## Главное в одну строку

Админские **UI**-настройки (в первую очередь SMTP / Email settings и `[mail]` в `config.ini.php`)
токеном не читаются и не правятся — нужен логин в UI под паролем либо доступ к файлу на сервере.
Всё, что касается **отчётов и пользователей**, по API доступно.

## Границы возможностей токена (суперюзерский)

Токен обладает правами суперюзера: `UsersManager.getUsers` отдаёт всех 19 пользователей
(единственный суперюзер — `Admin_matomo` / apetrovskiy@iikosoftware.com, остальные приглашены им же;
у 17 из 19 заполнен `invite_accept_at`).

| Задача | Токеном | Как на самом деле |
|---|---|---|
| Список/детали пользователей, email, `invite_status`, `last_seen` | ✅ `UsersManager.getUsers` | — |
| Пригласить сотрудника | ✅ `UsersManager.inviteUser(login, email, initialIdSite, expiryInDays)` | `initialIdSite` обязателен; письмо уходит сразу, если жив SMTP |
| Переслать инвайт / получить ссылку | ✅ `resendInvite(login, expiryInDays=7)`; `generateInviteLink` — инвайт-ссылка **без отправки письма** (фолбэк при мёртвой почте) | — |
| **Выставить пароль пользователю** | ✅ `UsersManager.updateUser(login, password)` | письма не шлёт; `passwordConfirmation` требуется только при session-auth, для API-токена — нет |
| Self-service сброс пароля («Забыли пароль?») | ❌ API нет | UI `Login.resetPassword` |
| Email-отчёты по расписанию | ✅ `ScheduledReports.addReport / updateReport / deleteReport / getReports / generateReport / sendReport` | ЕДИНСТВЕННАЯ «отправка на почту», полностью автоматизируемая |
| Чтение/правка SMTP (host, port, type, username, password, encryption, from-адрес) | ❌ | UI `Administration → General Settings → Email settings` под паролем или `config.ini.php` |
| Диагностика почты, список активных плагинов | ❌ | только UI (Diagnostics / Plugins) |

## Ключевая заминка: суперюзерский токен не открывает UI

```
POST https://analytics.iiko.services/index.php
  module=CoreAdminHome&action=generalSettings&token_auth=<superuser>
→ HTTP 500 «This user has super-user access. Embedding widgets with super-user
  token authentication is not allowed.»
```

Причина в исходниках: `core/API/Request.php::checkTokenAuthIsNotLimited($module, $action)` —
для **любого** не-API запроса при `Access::hasSuperUserAccess()` сразу бросается
`Widgetize_TooHighAccessLevel`. GET это или POST — неважно; superuser-ветка срабатывает **до**
проверки флагов `enable_framed_allow_write_admin_token_auth` / `token_auth.write_admin_allowed_module_actions`,
так что обходного конфига нет. Следствие: `CoreAdminHome.setMailSettings` и любые UI-страницы
токеном не дёрнуть. Не обещать пользователю «настрою почту через API» — это физически не тот путь.

## Методы, которых НЕТ на этом инстансе (ответ «method … does not exist»)

`UsersManager.getUserByTokenAuth`, `CorePluginsAdmin.getPluginsInfo`,
`API.getAvailableMethodsInVersion`, `ScheduledReports.getReportTypes | getReportFormats | getReportMetadata`,
плагин `Mail` (его не существует), API у плагина `Diagnostics`. Список активных плагинов и
диагностику почты по API не вытащить. Типы и форматы отчётов (`'email'`, `'html'`/`'pdf'`) живут
в UI-метаданных, а не в API.

Полезно помнить: список доступных методов у инстанса спросить нечем, поэтому перед обещанием
фичи — пробовать конкретный метод и читать текст ошибки.

## Транзакционные письма: как устроена отправка

Встроенные письма `Login` / `UsersManager` (сброс пароля, приглашения); галочки «включить» у них нет —
работают ровно настолько, насколько настроен почтовый транспорт.

Транспорт в Matomo 5.x — **PHPMailer 7.1.1** (был Zend/Laminas), обёртка `core/Mail/Transport.php`:

- `[mail] transport` пусто → PHP `mail()`. Если `mail()` запрещён в `disable_functions` или MTA нет —
  падает **вся** транзакционная почта, ошибка в UI: «Невозможно запустить функцию mail()».
  (Реальный кейс iiko: `mail()` запрещён, поэтому сброс пароля падает, а инвайты раздавались ссылками.)
- `transport = "smtp"` → `isSMTP()`; `mail()` не нужен вообще (сокет к релею).
- `type` кладётся в `AuthType` как `strtoupper()`; штатные значения `Plain` / `Login` / `Cram-md5`.
- `encryption = "none"` → `SMTPAutoTLS = false`; иначе `SMTPSecure`.
- Ключи самоподписанных сертов: `[mail] ssl_verify_peer`, `ssl_verify_peer_name`, `ssl_disallow_self_signed`.

```ini
[mail]
transport = "smtp"
host = "smtp.example.com"
port = 587
type = "Login"
username = "matomo@example.com"
password = "..."
encryption = "tls"

[General]
noreply_email_address = "matomo@example.com"
noreply_email_name = "iiko Matomo"
```

UI (рестарт не нужен): POST в `module=CoreAdminHome&action=setMailSettings` с полями
`mailUseSmtp / mailHost / mailPort / mailType / mailUsername / mailPassword / mailEncryption`
+ `mailFromAddress / mailFromName` (`[General] noreply_email_address|noreply_email_name`).
Нужен суперюзер + подтверждение пароля; страница целиком отключена при
`isGeneralSettingsAdminEnabled() = false`.

**Чек-лист для IT:** исходящие **587 (TLS) / 465 (SSL)** разрешены с хоста Matomo; from-адрес на
домене с **SPF/DKIM** (иначе письма уходят и падают в спам — самая частая «почта настроена, но не
приходит»); для M365/Google — включён SMTP AUTH + app password.

## Питфол: «все приняли инвайт» ≠ почта работает

17/19 пользователей имеют заполненный `invite_accept_at` (09.07–08.09) при том, что письма не
уходили вообще — ссылки раздавали руками через `generateInviteLink`. Не делать вывода о живом
транспорте по факту принятых инвайтов; проверять реальной отправкой (тестовый `inviteUser` на
подконтрольный ящик или «Забыли пароль?» для своего аккаунта — тот же транспорт, нулевой мусор).

## OAuth / OAuth2 — где дружит, где нет

| Область | Статус |
|---|---|
| **SMTP (XOAUTH2)** | ❌ Из коробки нет. PHPMailer умеет, но `Transport.php` **никогда не вызывает `setOAuth()`**, полей client_id/secret/refresh_token в `[mail]` и UI нет, `league/oauth2-*` в composer.lock — только в `suggest`. Релей с OAuth2 = внутренний SMTP-шлюз с Login/app password, либо патч (DI-подмена `Piwik\Mail\Transport` + composer, дорого и ломает обновления) |
| **API-доступ** | ✅ Официальный плагин `OAuth2` (matomo-org, GPL-3, free): first-party authorization server — Authorization Code (PKCE), Client Credentials, Refresh Token; scopes `matomo:read/write/admin/superuser`; bearer вместо `token_auth`; RFC 8414 discovery `/.well-known/oauth-authorization-server`; UI `Administration → Platform → OAuth 2.0`; внутри `league/oauth2-server`. Ветка 5.x (5.3.3 в репо, 5.0.0 в маркетплейсе) требует matomo `>=5.0,<6` + PHP ≥8.1 → подходит для 5.11.0/PHP 8.4 |
| **Вход/SSO** | ⚠️ В ядре только `Login` + `LoginLdap` (LDAP лицензируемый). OIDC — community-плагины `LoginOIDC` (dominik-th, 374k загрузок), `PkceOIDC`, `RebelOIDC` |

## Приёмы разведки по Matomo (переиспользуемые)

- **GitHub code search с токеном** — быстрее, чем угадывать имя метода/файла:
  `GET https://api.github.com/search/code?q=<Symbol>+repo:matomo-org/matomo` (нужен `GITHUB_TOKEN`
  из `$HERMES_HOME/.env`). Так найдены `checkTokenAuthIsNotLimited` и `Widgetize_TooHighAccessLevel`.
- **Raw-исходники вместо доков**: `raw.githubusercontent.com/matomo-org/matomo/5.x-dev/...`
  (developer.matomo.org — JS-рендер). Поведение методов брать из `plugins/<Plugin>/API.php` + `Controller.php`.
- **Маркетплейс**: `https://plugins.matomo.org/api/2.0/plugins?query=oauth` — в payload бывают битые
  control-символы → `json.loads(raw, strict=False)`. Даёт owner/`require` (matomo+php)/версии/даты.
  Детальный эндпоинт `/api/2.0/plugins/<Name>` отдаёт не-JSON — брать данные из поиска.
- **Версия инстанса**: `API.getMatomoVersion`; PHP/веб-сервер — `curl -sI .../index.php | grep -i x-powered-by`.
- Токен инстанса iiko — **только POST-параметром формы** (query/header отклоняются), см.
  `iiko-instance-access.md`.

## Формулировка задачи

«Настроить отправку сообщений на почту в Matomo» звучит двусмысленно — уточнять первой же репликой:

- **транзакционные письма** (инвайты, сброс пароля) → внешний SMTP, правится только в UI;
- **email-отчёты** (`ScheduledReports.*`, Matomo 4+) → полностью автоматизируется по API.

Это разные работы; смешение приводит к тому, что рекогносцировка уходит не туда.
