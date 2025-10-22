# DFD — Roommate Chores

Проект: Roommate Chores — трекер домашних дел между участниками
Сущности: `User; Chore(title, cadence); Assignment(user_id, due_at, status)`
API: CRUD `/chores`, CRUD `/assignments`, GET `/stats`
Стек: Python / FastAPI + SQLite/Postgres + Pytest

## Диаграмма DFD (Mermaid)

```mermaid
flowchart LR
  %% External actors
  User["User (Browser / Mobile)"]
  EmailSvc["External Email / SMS Service"]

  %% Trust boundaries
  subgraph Edge ["Trust Boundary: Edge (Client)"]
    User
  end

  subgraph EdgeAPI ["Trust Boundary: Edge (API / TLS)"]
    APIGW["API - FastAPI (TLS)"]
  end

  subgraph Core ["Trust Boundary: Core (Application)"]
    APIGW -->|F1: HTTPS auth| Auth["Auth Service (JWT / sessions)"]
    APIGW -->|F2: POST /chores| ChoreSvc["Chore Service"]
    APIGW -->|F3: POST /assignments| AssignSvc["Assignment Service"]
    APIGW -->|F4: GET /stats| StatsSvc["Stats Service"]
    ChoreSvc -->|F5: DB read/write| DB[(Database - Postgres)]
    AssignSvc -->|F6: DB read/write| DB
    StatsSvc -->|F7: DB read| DB
    ChoreSvc -->|F8: Enqueue notification| Queue["Internal Queue / Background job"]
    Queue -->|F9: Worker consumes| Worker["Worker - sends notifications (stub)"]
    Worker -->|F10: API / SMTP| EmailSvc
    Auth -->|F11: DB read| DB
  end

  style APIGW stroke-width:2px
%%  style DB stroke-dasharray: 5 5

  %% user interaction
  User --> APIGW
```

## Пояснения

* **Edge (Client):** браузер/мобильное приложение — недоверенный источник.
* **Edge (API / TLS):** публичный API (FastAPI) — проверяет TLS/аутентификацию.
* **Core (Application):** сервисы, воркеры, внутренняя очередь, БД — зона повышенного доверия.
* **Внешние участники:** Email/SMS провайдер для уведомлений.
* **Хранилища:** БД (Postgres/SQLite), внутренняя очередь (Redis / простая очередь).

## Потоки (идентификаторы)

* **F1** — Аутентификация / передача токена (Browser $\rightarrow$ API)
* **F2** — POST /chores (создание/изменение chore)
* **F3** — POST /assignments (создание/изменение assignment)
* **F4** — GET /stats (агрегаты/статистика)
* **F5** — Chore service $\leftrightarrow$ DB (CRUD)
* **F6** — Assignment service $\leftrightarrow$ DB (CRUD)
* **F7** — Stats service $\leftrightarrow$ DB (read/aggregate)
* **F8** — Chore service $\rightarrow$ Internal Queue (notify event)
* **F9** — Worker $\rightarrow$ Internal Queue (consume job)
* **F10** — Worker $\rightarrow$ External Email/SMS (HTTP/SMTP)
* **F11** — Auth service $\leftrightarrow$ DB (user lookup, password hash)
