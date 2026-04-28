# Edu Whiteboard Python MVP

Асинхронный MVP образовательного сервиса:

- задания;
- онлайн-доска tldraw;
- сохранение состояния доски в Python backend;
- FastAPI async;
- Pydantic v2;
- SQLAlchemy 2 async;
- PostgreSQL;
- Redis;
- структурное JSON-логирование;
- модульная архитектура repositories/services/routers;
- подготовленная event-абстракция под Kafka.

## Kafka: нужна ли сейчас?

Для MVP — нет.

Kafka нужна позже, когда появятся независимые фоновые потребители:

- аналитика действий ученика;
- replay решения;
- уведомления учителю;
- AI-проверка в фоне;
- генерация отчётов;
- event sourcing;
- интеграции с внешними сервисами.

Сейчас достаточно синхронного API + PostgreSQL + Redis. В проекте есть `EventPublisher`, который пока работает как no-op. Его можно заменить Kafka-паблишером без изменения бизнес-сервисов.

## Структура

```text
backend/
  app/
    api/          # HTTP routers/dependencies
    core/         # config, logging, middleware
    db/           # SQLAlchemy engine/session/base
    models/       # ORM models
    schemas/      # Pydantic DTO
    repositories/ # доступ к данным
    services/     # бизнес-логика
    events/       # доменные события и publisher abstraction
    utils/        # seed/dev scripts
  alembic/        # миграции
frontend/
  src/
    api/          # API client
    components/   # tldraw-доска
    pages/        # основной UI
```

## Запуск backend

```bash
cd edu-whiteboard-python
cp backend/.env.example backend/.env
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/health
```

Swagger:

```text
http://localhost:8000/docs
```

## Наполнение тестовыми заданиями

В отдельном терминале:

```bash
docker compose exec backend python -m app.utils.seed
```

## Запуск frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Открыть:

```text
http://localhost:5173
```

## Основные API

```text
GET    /api/v1/exercises
POST   /api/v1/exercises
GET    /api/v1/exercises/{exercise_id}

POST   /api/v1/attempts
GET    /api/v1/attempts/{attempt_id}
PATCH  /api/v1/attempts/{attempt_id}/board
POST   /api/v1/attempts/{attempt_id}/submit
PATCH  /api/v1/attempts/{attempt_id}/teacher-comment
```

## Архитектурные решения

### Async Python

Используется FastAPI + SQLAlchemy async + asyncpg. Это нормально ложится на API, где много I/O: база, Redis, внешние сервисы, AI API.

### Pydantic-валидация

Все входные payload проходят через Pydantic-схемы:

- `ExerciseCreate`;
- `AttemptCreate`;
- `BoardStateUpdate`;
- `TeacherCommentUpdate`.

### DRY

Общие операции вынесены в `BaseRepository`. Бизнес-логика не дублируется в routers.

### SOLID

- Router отвечает только за HTTP.
- Service отвечает за бизнес-логику.
- Repository отвечает за работу с БД.
- EventPublisher абстрагирует механизм публикации событий.
- Config централизован.

### Redis

Сейчас Redis подключён в lifespan и готов для:

- rate limiting;
- кэша заданий;
- временных черновиков;
- distributed locks;
- idempotency keys.

### Kafka

Сейчас не включена. Добавлена точка расширения через `EventPublisher`.

## Что добавить следующим шагом

1. Таблицу `users` и нормальную авторизацию.
2. Роли: student / teacher / admin.
3. Teacher dashboard.
4. Автосохранение с debounce на frontend.
5. Восстановление tldraw snapshot из backend при открытии попытки.
6. Unit/integration tests.
7. OpenTelemetry tracing.
8. Background workers для AI-проверки.
