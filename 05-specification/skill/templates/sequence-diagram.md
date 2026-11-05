<!-- Источник: скилл spec-writing v2.0 (Александра Коновалова), вложение к странице «Формат PRD» (wiki.iiko.ru, IIKOWEB, pageId 181776249). Файл выгружен в репозиторий 2026-10-01. -->

### Д.3 Sequence diagram (шаблон)

Используй для «Шага 4. Системное взаимодействие». Диаграмма обязана показывать **не только happy path** — добавляй ошибки, retry, timeout и альтернативные ветки, если они влияют на реализацию.

### Базовый каркас

```mermaid
sequenceDiagram
    autonumber
    actor User as Пользователь
    participant UI as Интерфейс
    participant iiko as iiko / backend
    participant API as Внешний API
    participant DB as База данных

    User->>UI: Действие
    UI->>iiko: Запрос
    iiko->>API: Внешний вызов
    API-->>iiko: Ответ
    iiko->>DB: Сохранение
    iiko-->>UI: Результат
    UI-->>User: Ответ пользователю
```

### Как покрывать не-happy path

#### Ошибка внешнего сервиса

```mermaid
sequenceDiagram
    participant iiko
    participant API as Внешний API

    iiko->>API: Запрос
    API-->>iiko: Ошибка (500 / отказ)
    iiko-->>User: Сообщение об ошибке
```

#### Timeout и retry

```mermaid
sequenceDiagram
    participant iiko
    participant API as Внешний API

    iiko->>API: Запрос
    Note over iiko,API: timeout 10s
    API--x iiko: Нет ответа
    iiko->>API: Повтор (retry 1/3)
    API-->>iiko: Ответ
```

#### Альтернативные ветки (alt / opt)

```mermaid
sequenceDiagram
    participant iiko
    participant API as Внешний API

    iiko->>API: Запрос
    alt Успех
        API-->>iiko: 200 OK
        iiko-->>User: Подтверждено
    else Отказ
        API-->>iiko: 4xx/5xx
        iiko-->>User: Ошибка + причина
    else Timeout
        API--x iiko: Нет ответа
        iiko-->>User: Ошибка «сервис недоступен»
    end
```

#### Webhook / асинхронное событие

```mermaid
sequenceDiagram
    participant iiko
    participant API as Внешний API
    participant Hook as Webhook endpoint

    iiko->>API: Запрос на создание
    API-->>iiko: Принято (202)
    API->>Hook: Событие (асинхронно)
    Hook-->>iiko: Подтверждение получения
```

### Правила

1. **Только реальные системы и события** — не добавляй блоки, которых нет в требованиях.
2. **Один участник = одна система/роль.** Не смешивай UI и backend в одном боксе.
3. **Ошибки и retry/timeout — обязательны**, если задача затрагивает внешние интеграции или асинхронные события.
4. **autonumber** включай, когда на диаграмму будут ссылаться из текста спецификации («см. шаг 3»).
5. Проверяй соответствие: диаграмма не должна противоречить текстовым сценариям (Шаг 5) и разделу To-be.

### Отрисовка

- Если среда поддерживает Mermaid — оставь код-блок, он отрисуется сам.
- Если нет — сгенерируй изображение доступным способом (например, `mmdc`/PlantUML-конвертер) и вставь ссылку на картинку рядом с кодом.
- Никогда не оставляй диаграмму «только текстом», если есть способ её отрисовать.



---
