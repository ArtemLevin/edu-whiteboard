# План разработки и обучения: Edu Whiteboard

## 1. Общая идея проекта

Мы разрабатываем образовательный сервис, в котором:

```text
Ученик видит задание
↓
открывает онлайн-доску
↓
пишет решение
↓
сохраняет черновик
↓
сдаёт решение
↓
учитель проверяет и оставляет комментарий
```

Проект используется не только как продуктовая заготовка, но и как учебный маршрут для повторения backend-разработки от основ до архитектурно осмысленного приложения.

Техническая цель:

```text
FastAPI async
Pydantic validation
PostgreSQL
Redis
структурное логирование
модульность
SOLID
DRY
луковичная архитектура
готовность к будущим микросервисам
```

Kafka на старте не подключаем как обязательную часть. Мы проектируем событийную модель и порт публикации событий, чтобы Kafka или Redpanda можно было добавить позже без переписывания бизнес-логики.

---

## 2. Архитектурное решение

Фиксируем подход:

```text
модульный монолит
+
луковичная архитектура внутри каждого модуля
+
готовность к будущему выделению микросервисов
```

Мы не начинаем с физических микросервисов, потому что они сразу добавляют сложность:

```text
межсервисное взаимодействие
сетевые ошибки
distributed transactions
eventual consistency
Kafka / broker
observability
trace_id
service discovery
CI/CD для каждого сервиса
версии API
контрактные тесты
```

Вместо этого мы строим один backend, но с чёткими границами модулей.

---

## 3. Главная архитектурная идея

Вместо одной общей луковицы:

```text
backend/app/
├─ domain/
├─ application/
├─ infrastructure/
└─ presentation/
```

используем модульный вариант:

```text
backend/app/
├─ modules/
│  ├─ users/
│  ├─ exercises/
│  ├─ attempts/
│  ├─ feedback/
│  ├─ boards/
│  ├─ notifications/
│  ├─ ai_review/
│  └─ shared/
│
├─ core/
└─ main.py
```

Каждый важный бизнес-модуль может иметь свою внутреннюю луковицу:

```text
module/
├─ domain/
├─ application/
├─ infrastructure/
└─ presentation/
```

---

## 4. Правило зависимостей

Внутри каждого модуля:

```text
domain
  ↑
application
  ↑
infrastructure / presentation
```

Практически это означает:

```text
presentation → application → domain
infrastructure → application/domain
domain → никуда наружу
```

Запрещено:

```text
domain импортирует FastAPI
domain импортирует SQLAlchemy
domain импортирует Redis
domain импортирует Pydantic-схемы API
application импортирует SQLAlchemy-модели
application импортирует FastAPI router
```

Разрешено:

```text
router вызывает use case
use case работает с domain entity
use case зависит от repository protocol
repository реализует protocol через SQLAlchemy
```

---

## 5. Границы модулей

### `users`

Отвечает за пользователей:

```text
ученики
учителя
админы
роли
позже — авторизация
```

### `exercises`

Отвечает за задания:

```text
условие
тема
сложность
ответ
архивация
список заданий
```

### `attempts`

Отвечает за попытки решения:

```text
начать попытку
сохранить черновик
сдать решение
статус попытки
история попыток
```

### `boards`

Отвечает за данные доски:

```text
board_state
версии доски
превью
экспорт
replay
```

На первом MVP можно хранить `board_state` внутри `attempts`, но модуль `boards` оставляем как будущую границу.

### `feedback`

Отвечает за проверку:

```text
комментарий учителя
оценка
возврат на доработку
статус проверки
```

### `notifications`

Будущий модуль:

```text
уведомления ученику
уведомления учителю
email
telegram
push
```

В MVP можно не реализовывать, только заложить событие.

### `ai_review`

Будущий модуль:

```text
AI-проверка решения
AI-подсказки
анализ ошибок
генерация рекомендаций
```

Это первый кандидат на будущий отдельный микросервис.

### `shared`

Общие вещи, которые не принадлежат одному модулю:

```text
общие value objects
общие base types
общие domain events
pagination
result types
id types
```

Важно: `shared` не должен становиться мусорной папкой.

---

## 6. Целевая структура проекта

```text
edu_whiteboard/
├─ backend/
│  ├─ app/
│  │  ├─ modules/
│  │  │  ├─ shared/
│  │  │  │  ├─ domain/
│  │  │  │  │  ├─ events.py
│  │  │  │  │  ├─ exceptions.py
│  │  │  │  │  └─ ids.py
│  │  │  │  ├─ application/
│  │  │  │  │  ├─ event_publisher.py
│  │  │  │  │  └─ pagination.py
│  │  │  │  └─ infrastructure/
│  │  │  │     └─ events/
│  │  │  │        ├─ logging_event_publisher.py
│  │  │  │        └─ kafka_event_publisher.py
│  │  │  │
│  │  │  ├─ users/
│  │  │  │  ├─ domain/
│  │  │  │  │  ├─ entities.py
│  │  │  │  │  ├─ enums.py
│  │  │  │  │  └─ exceptions.py
│  │  │  │  ├─ application/
│  │  │  │  │  ├─ dto.py
│  │  │  │  │  ├─ ports.py
│  │  │  │  │  └─ use_cases/
│  │  │  │  ├─ infrastructure/
│  │  │  │  │  ├─ models.py
│  │  │  │  │  ├─ mappers.py
│  │  │  │  │  └─ repositories.py
│  │  │  │  └─ presentation/
│  │  │  │     ├─ schemas.py
│  │  │  │     └─ router.py
│  │  │  │
│  │  │  ├─ exercises/
│  │  │  │  ├─ domain/
│  │  │  │  │  ├─ entities.py
│  │  │  │  │  ├─ enums.py
│  │  │  │  │  ├─ value_objects.py
│  │  │  │  │  └─ exceptions.py
│  │  │  │  ├─ application/
│  │  │  │  │  ├─ dto.py
│  │  │  │  │  ├─ ports.py
│  │  │  │  │  └─ use_cases/
│  │  │  │  ├─ infrastructure/
│  │  │  │  │  ├─ models.py
│  │  │  │  │  ├─ mappers.py
│  │  │  │  │  └─ repositories.py
│  │  │  │  └─ presentation/
│  │  │  │     ├─ schemas.py
│  │  │  │     └─ router.py
│  │  │  │
│  │  │  ├─ attempts/
│  │  │  │  ├─ domain/
│  │  │  │  │  ├─ entities.py
│  │  │  │  │  ├─ enums.py
│  │  │  │  │  ├─ value_objects.py
│  │  │  │  │  ├─ events.py
│  │  │  │  │  └─ exceptions.py
│  │  │  │  ├─ application/
│  │  │  │  │  ├─ dto.py
│  │  │  │  │  ├─ ports.py
│  │  │  │  │  └─ use_cases/
│  │  │  │  ├─ infrastructure/
│  │  │  │  │  ├─ models.py
│  │  │  │  │  ├─ mappers.py
│  │  │  │  │  └─ repositories.py
│  │  │  │  └─ presentation/
│  │  │  │     ├─ schemas.py
│  │  │  │     └─ router.py
│  │  │  │
│  │  │  ├─ feedback/
│  │  │  ├─ boards/
│  │  │  ├─ notifications/
│  │  │  └─ ai_review/
│  │  │
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  ├─ database.py
│  │  │  ├─ logging.py
│  │  │  ├─ middleware.py
│  │  │  └─ security.py
│  │  │
│  │  └─ main.py
│  │
│  ├─ tests/
│  │  ├─ unit/
│  │  ├─ integration/
│  │  └─ api/
│  │
│  ├─ alembic/
│  ├─ pyproject.toml
│  └─ Dockerfile
│
├─ frontend/
└─ docker-compose.yml
```

---

## 7. Формат работы

Правило разработки:

```text
одна итерация = один файл или один небольшой логический шаг
```

Для каждой итерации фиксируем:

1. Зачем нужен файл.
2. Где он лежит.
3. Полный код файла.
4. Разбор ключевых идей.
5. Как проверить.
6. Какие ошибки могут возникнуть.
7. Какой следующий файл.

Код пишем с простыми русскими комментариями внутри.

---

# Фаза 1. Каркас проекта

## 1.1. Скрипт создания структуры

Файл:

```text
create_project_structure.sh
```

Цель:

```text
создать папки модульного монолита
```

Изучаем:

```text
почему структура проекта — часть архитектуры
как папки помогают соблюдать границы
```

---

## 1.2. `pyproject.toml`

Файл:

```text
backend/pyproject.toml
```

Изучаем:

```text
зависимости
dev-зависимости
ruff
mypy
pytest
editable install
```

---

## 1.3. `.env.example`

Файл:

```text
backend/.env.example
```

Изучаем:

```text
конфигурация
секреты
переменные окружения
```

---

## 1.4. `README.md`

Файл:

```text
README.md
```

Изучаем:

```text
как документировать архитектуру и запуск
```

---

# Фаза 2. Shared module

Сначала делаем минимальный общий слой. Не большой, только то, что действительно общее.

## 2.1. Общие id-типы

Файл:

```text
backend/app/modules/shared/domain/ids.py
```

Что будет:

```python
UserId
ExerciseId
AttemptId
```

Изучаем:

```text
type aliases
NewType
почему id разных сущностей лучше не смешивать
```

---

## 2.2. Общие доменные исключения

Файл:

```text
backend/app/modules/shared/domain/exceptions.py
```

Что будет:

```text
DomainError
ValidationDomainError
PermissionDomainError
EntityNotFoundError
```

Изучаем:

```text
почему domain не должен выбрасывать HTTPException
```

---

## 2.3. Доменные события

Файл:

```text
backend/app/modules/shared/domain/events.py
```

Что будет:

```text
DomainEvent
```

Изучаем:

```text
события как способ подготовиться к микросервисам
```

---

## 2.4. Порт публикации событий

Файл:

```text
backend/app/modules/shared/application/event_publisher.py
```

Что будет:

```text
EventPublisherPort
```

Изучаем:

```text
инверсия зависимостей
Kafka-ready подход без Kafka
```

---

## 2.5. Пагинация

Файл:

```text
backend/app/modules/shared/application/pagination.py
```

Что будет:

```text
PaginationParams
Page
```

Изучаем:

```text
общие DTO
ограничения limit/offset
```

---

# Фаза 3. Users module

Минимальная модель пользователя.

## 3.1. UserRole enum

Файл:

```text
backend/app/modules/users/domain/enums.py
```

Что будет:

```text
UserRole.STUDENT
UserRole.TEACHER
UserRole.ADMIN
```

---

## 3.2. User exceptions

Файл:

```text
backend/app/modules/users/domain/exceptions.py
```

Что будет:

```text
UserAlreadyExistsError
InactiveUserError
```

---

## 3.3. User entity

Файл:

```text
backend/app/modules/users/domain/entities.py
```

Что будет:

```text
User
```

Методы:

```text
create_student()
create_teacher()
deactivate()
activate()
```

Изучаем:

```text
dataclass
entity
identity
role
```

---

## 3.4. User DTO

Файл:

```text
backend/app/modules/users/application/dto.py
```

---

## 3.5. UserRepositoryPort

Файл:

```text
backend/app/modules/users/application/ports.py
```

---

## 3.6. CreateUserUseCase

Файл:

```text
backend/app/modules/users/application/use_cases/create_user.py
```

---

# Фаза 4. Exercises module

## 4.1. ExerciseDifficulty enum

Файл:

```text
backend/app/modules/exercises/domain/enums.py
```

---

## 4.2. Exercise exceptions

Файл:

```text
backend/app/modules/exercises/domain/exceptions.py
```

---

## 4.3. ExerciseContent value object

Файл:

```text
backend/app/modules/exercises/domain/value_objects.py
```

Что будет:

```text
ExerciseContent
```

Изучаем:

```text
value object
frozen dataclass
валидация условия задания
```

---

## 4.4. Exercise entity

Файл:

```text
backend/app/modules/exercises/domain/entities.py
```

Методы:

```text
create()
archive()
restore()
rename()
change_content()
change_difficulty()
```

---

## 4.5. Exercise DTO

Файл:

```text
backend/app/modules/exercises/application/dto.py
```

---

## 4.6. ExerciseRepositoryPort

Файл:

```text
backend/app/modules/exercises/application/ports.py
```

---

## 4.7. CreateExerciseUseCase

Файл:

```text
backend/app/modules/exercises/application/use_cases/create_exercise.py
```

---

## 4.8. ListExercisesUseCase

Файл:

```text
backend/app/modules/exercises/application/use_cases/list_exercises.py
```

---

## 4.9. GetExerciseUseCase

Файл:

```text
backend/app/modules/exercises/application/use_cases/get_exercise.py
```

---

# Фаза 5. Attempts module

Это главный модуль продукта.

## 5.1. AttemptStatus enum

Файл:

```text
backend/app/modules/attempts/domain/enums.py
```

Статусы:

```text
DRAFT
SUBMITTED
CHECKED
RETURNED
```

---

## 5.2. Attempt exceptions

Файл:

```text
backend/app/modules/attempts/domain/exceptions.py
```

Ошибки:

```text
InvalidAttemptStatusTransition
EmptyBoardStateError
AttemptAlreadySubmittedError
AttemptCannotBeEditedError
```

---

## 5.3. BoardState value object

Файл:

```text
backend/app/modules/attempts/domain/value_objects.py
```

На первом этапе `BoardState` живёт в `attempts`, потому что это часть попытки. Позже можно вынести в `boards`.

Изучаем:

```text
JSON как value object
защита от пустого состояния
ограничение размера
```

---

## 5.4. Attempt domain events

Файл:

```text
backend/app/modules/attempts/domain/events.py
```

События:

```text
AttemptStarted
BoardSaved
AttemptSubmitted
AttemptReviewed
```

---

## 5.5. SolutionAttempt entity

Файл:

```text
backend/app/modules/attempts/domain/entities.py
```

Методы:

```text
start()
save_board()
submit()
mark_checked()
return_for_revision()
```

Изучаем:

```text
инварианты
жизненный цикл
переходы статусов
```

---

## 5.6. Attempt DTO

Файл:

```text
backend/app/modules/attempts/application/dto.py
```

---

## 5.7. AttemptRepositoryPort

Файл:

```text
backend/app/modules/attempts/application/ports.py
```

---

## 5.8. StartAttemptUseCase

Файл:

```text
backend/app/modules/attempts/application/use_cases/start_attempt.py
```

---

## 5.9. SaveBoardUseCase

Файл:

```text
backend/app/modules/attempts/application/use_cases/save_board.py
```

---

## 5.10. SubmitAttemptUseCase

Файл:

```text
backend/app/modules/attempts/application/use_cases/submit_attempt.py
```

Здесь впервые используем:

```text
EventPublisherPort
```

Но реализация пока будет просто логировать события.

---

## 5.11. ReviewAttemptUseCase

Файл:

```text
backend/app/modules/attempts/application/use_cases/review_attempt.py
```

Позже часть логики можно вынести в `feedback`.

---

# Фаза 6. Unit-тесты ядра

Сначала тестируем без базы и FastAPI.

## 6.1. Тест User entity

Файл:

```text
backend/tests/unit/users/domain/test_user.py
```

---

## 6.2. Тест Exercise entity

Файл:

```text
backend/tests/unit/exercises/domain/test_exercise.py
```

---

## 6.3. Тест BoardState

Файл:

```text
backend/tests/unit/attempts/domain/test_board_state.py
```

---

## 6.4. Тест SolutionAttempt lifecycle

Файл:

```text
backend/tests/unit/attempts/domain/test_solution_attempt.py
```

Проверяем:

```text
start → draft
draft → save_board
draft → submit
submitted нельзя редактировать
submitted → checked
submitted → returned
```

---

## 6.5. Тест SaveBoardUseCase

Файл:

```text
backend/tests/unit/attempts/application/test_save_board.py
```

Изучаем:

```text
fake repository
fake event publisher
тестирование use case без базы
```

---

# Фаза 7. Core

Добавляем техническое ядро приложения.

## 7.1. `config.py`

Файл:

```text
backend/app/core/config.py
```

Изучаем:

```text
pydantic-settings
BaseSettings
.env
```

---

## 7.2. `logging.py`

Файл:

```text
backend/app/core/logging.py
```

Изучаем:

```text
JSON logs
структурное логирование
request_id
```

---

## 7.3. `middleware.py`

Файл:

```text
backend/app/core/middleware.py
```

Изучаем:

```text
FastAPI middleware
request_id
latency_ms
```

---

## 7.4. `database.py`

Файл:

```text
backend/app/core/database.py
```

Изучаем:

```text
SQLAlchemy async engine
async_sessionmaker
```

---

# Фаза 8. Infrastructure: PostgreSQL

Теперь реализуем хранение.

## 8.1. Общий SQLAlchemy Base

Файл:

```text
backend/app/core/database.py
```

или отдельный:

```text
backend/app/core/sqlalchemy_base.py
```

---

## 8.2. User ORM model

Файл:

```text
backend/app/modules/users/infrastructure/models.py
```

---

## 8.3. Exercise ORM model

Файл:

```text
backend/app/modules/exercises/infrastructure/models.py
```

---

## 8.4. Attempt ORM model

Файл:

```text
backend/app/modules/attempts/infrastructure/models.py
```

Особенно изучаем:

```text
JSONB для board_state
индексы
foreign keys
timestamp fields
```

---

## 8.5. User mappers

Файл:

```text
backend/app/modules/users/infrastructure/mappers.py
```

---

## 8.6. Exercise mappers

Файл:

```text
backend/app/modules/exercises/infrastructure/mappers.py
```

---

## 8.7. Attempt mappers

Файл:

```text
backend/app/modules/attempts/infrastructure/mappers.py
```

---

## 8.8. User repository

Файл:

```text
backend/app/modules/users/infrastructure/repositories.py
```

---

## 8.9. Exercise repository

Файл:

```text
backend/app/modules/exercises/infrastructure/repositories.py
```

---

## 8.10. Attempt repository

Файл:

```text
backend/app/modules/attempts/infrastructure/repositories.py
```

---

## 8.11. Alembic setup

Файлы:

```text
backend/alembic.ini
backend/alembic/env.py
```

---

## 8.12. Первая миграция

Файл:

```text
backend/alembic/versions/0001_initial.py
```

---

# Фаза 9. Infrastructure: Redis и события

## 9.1. Redis cache port

Файл:

```text
backend/app/modules/shared/application/cache.py
```

---

## 9.2. Redis cache adapter

Файл:

```text
backend/app/modules/shared/infrastructure/cache/redis_cache.py
```

---

## 9.3. LoggingEventPublisher

Файл:

```text
backend/app/modules/shared/infrastructure/events/logging_event_publisher.py
```

---

## 9.4. KafkaEventPublisher skeleton

Файл:

```text
backend/app/modules/shared/infrastructure/events/kafka_event_publisher.py
```

Статус:

```text
не подключаем в MVP
оставляем как адаптер на будущее
```

---

## 9.5. Outbox model

Файл:

```text
backend/app/modules/shared/infrastructure/events/outbox_model.py
```

Это важный шаг на пути к микросервисам.

Изучаем:

```text
outbox pattern
надёжная публикация событий
почему нельзя просто “сохранить в БД и потом отправить в Kafka”
```

---

# Фаза 10. Presentation: API

## 10.1. User schemas

Файл:

```text
backend/app/modules/users/presentation/schemas.py
```

---

## 10.2. Exercise schemas

Файл:

```text
backend/app/modules/exercises/presentation/schemas.py
```

---

## 10.3. Attempt schemas

Файл:

```text
backend/app/modules/attempts/presentation/schemas.py
```

---

## 10.4. Dependencies

Файл:

```text
backend/app/core/dependencies.py
```

Выбор: зависимости разных модулей собираются в `core/dependencies.py`, потому что это внешний слой, который связывает приложение воедино.

---

## 10.5. User router

Файл:

```text
backend/app/modules/users/presentation/router.py
```

Endpoints:

```text
POST /api/v1/users
GET  /api/v1/users/{user_id}
```

---

## 10.6. Exercise router

Файл:

```text
backend/app/modules/exercises/presentation/router.py
```

Endpoints:

```text
POST /api/v1/exercises
GET  /api/v1/exercises
GET  /api/v1/exercises/{exercise_id}
```

---

## 10.7. Attempt router

Файл:

```text
backend/app/modules/attempts/presentation/router.py
```

Endpoints:

```text
POST  /api/v1/attempts
GET   /api/v1/attempts/{attempt_id}
PATCH /api/v1/attempts/{attempt_id}/board
POST  /api/v1/attempts/{attempt_id}/submit
POST  /api/v1/attempts/{attempt_id}/review
```

---

## 10.8. Exception handlers

Файл:

```text
backend/app/core/exception_handlers.py
```

Изучаем:

```text
DomainError → HTTP response
единый формат ошибок
```

---

## 10.9. `main.py`

Файл:

```text
backend/app/main.py
```

Изучаем:

```text
создание FastAPI app
подключение middleware
подключение exception handlers
подключение routers
```

---

# Фаза 11. Docker и запуск

## 11.1. Backend Dockerfile

Файл:

```text
backend/Dockerfile
```

---

## 11.2. docker-compose.yml

Файл:

```text
docker-compose.yml
```

Сервисы:

```text
backend
postgres
redis
```

Опционально позже:

```text
redpanda
redpanda-console
```

---

## 11.3. Makefile

Файл:

```text
Makefile
```

Команды:

```text
make dev
make test
make lint
make migrate
make seed
```

---

## 11.4. Seed script

Файл:

```text
backend/app/modules/exercises/infrastructure/seed.py
```

---

# Фаза 12. API-тесты и интеграционные тесты

## 12.1. Repository integration tests

Файлы:

```text
backend/tests/integration/users/test_user_repository.py
backend/tests/integration/exercises/test_exercise_repository.py
backend/tests/integration/attempts/test_attempt_repository.py
```

---

## 12.2. API tests

Файлы:

```text
backend/tests/api/test_exercises_api.py
backend/tests/api/test_attempts_api.py
```

---

## 12.3. Полный сценарий

Файл:

```text
backend/tests/api/test_attempt_flow.py
```

Сценарий:

```text
создать ученика
создать задание
начать попытку
сохранить доску
сдать решение
проверить решение
```

---

# Фаза 13. Frontend MVP

Frontend оставляем проще, потому что главный учебный фокус пока backend.

## 13.1. Vite + React setup

Файлы:

```text
frontend/package.json
frontend/vite.config.ts
```

---

## 13.2. API client

Файл:

```text
frontend/src/api/http.ts
```

---

## 13.3. Exercises API

Файл:

```text
frontend/src/api/exercises.ts
```

---

## 13.4. Attempts API

Файл:

```text
frontend/src/api/attempts.ts
```

---

## 13.5. ExerciseListPage

Файл:

```text
frontend/src/pages/ExerciseListPage.tsx
```

---

## 13.6. ExerciseCard

Файл:

```text
frontend/src/components/ExerciseCard.tsx
```

---

## 13.7. ExerciseSolvePage

Файл:

```text
frontend/src/pages/ExerciseSolvePage.tsx
```

---

## 13.8. BoardEditor with tldraw

Файл:

```text
frontend/src/components/BoardEditor.tsx
```

---

## 13.9. Autosave hook

Файл:

```text
frontend/src/hooks/useAutosaveBoard.ts
```

---

## 13.10. TeacherAttemptsPage

Файл:

```text
frontend/src/pages/TeacherAttemptsPage.tsx
```

---

# Фаза 14. Auth и роли

После MVP добавляем полноценную авторизацию.

## 14.1. Password hashing

Файл:

```text
backend/app/core/security.py
```

---

## 14.2. RegisterUserUseCase

Файл:

```text
backend/app/modules/users/application/use_cases/register_user.py
```

---

## 14.3. LoginUserUseCase

Файл:

```text
backend/app/modules/users/application/use_cases/login_user.py
```

---

## 14.4. Auth router

Файл:

```text
backend/app/modules/users/presentation/auth_router.py
```

---

## 14.5. Role-based dependencies

Файл:

```text
backend/app/core/auth_dependencies.py
```

---

# Фаза 15. Feedback module

Когда базовый review внутри `attempts` станет понятен, выделим отдельный модуль.

Файлы:

```text
backend/app/modules/feedback/domain/entities.py
backend/app/modules/feedback/domain/value_objects.py
backend/app/modules/feedback/application/use_cases/create_feedback.py
backend/app/modules/feedback/infrastructure/models.py
backend/app/modules/feedback/presentation/router.py
```

Изучаем:

```text
как выделять отдельный bounded context
как не ломать существующий код
```

---

# Фаза 16. Boards module

Когда `board_state` начнёт усложняться, выделим `boards`.

Будущий функционал:

```text
версии доски
история изменений
replay
превью
экспорт
```

Файлы:

```text
backend/app/modules/boards/domain/entities.py
backend/app/modules/boards/application/use_cases/save_board_version.py
backend/app/modules/boards/infrastructure/models.py
```

---

# Фаза 17. Events, outbox, workers

Это мост к микросервисам.

## 17.1. Outbox repository

Файл:

```text
backend/app/modules/shared/infrastructure/events/outbox_repository.py
```

---

## 17.2. Outbox worker

Файл:

```text
backend/app/modules/shared/infrastructure/events/outbox_worker.py
```

---

## 17.3. Background worker

Файл:

```text
backend/app/worker.py
```

---

## 17.4. Internal event handlers

Файл:

```text
backend/app/modules/attempts/application/event_handlers.py
```

Сценарий:

```text
attempt.submitted
→ запланировать AI review
→ уведомить учителя
```

---

# Фаза 18. AI review module

Сначала внутри монолита.

Файлы:

```text
backend/app/modules/ai_review/domain/entities.py
backend/app/modules/ai_review/application/use_cases/request_ai_review.py
backend/app/modules/ai_review/application/use_cases/complete_ai_review.py
backend/app/modules/ai_review/infrastructure/ai_client.py
backend/app/modules/ai_review/presentation/router.py
```

Потом его можно вынести первым микросервисом.

---

# Фаза 19. Notifications module

Файлы:

```text
backend/app/modules/notifications/domain/entities.py
backend/app/modules/notifications/application/use_cases/send_notification.py
backend/app/modules/notifications/infrastructure/email_sender.py
```

События:

```text
attempt.submitted
attempt.reviewed
ai_review.completed
```

---

# Фаза 20. Подготовка к реальным микросервисам

Только после рабочего монолита.

## Что нужно сделать перед выносом сервиса

```text
чёткий публичный API модуля
события входа/выхода
собственные таблицы или схема БД
никаких прямых импортов domain другого модуля
контрактные тесты
идемпотентность event handlers
корреляционные id в логах
```

## Первый кандидат на вынос

```text
ai_review
```

Почему:

```text
естественно асинхронный
может долго работать
может масштабироваться отдельно
не должен блокировать сдачу решения
```

---

# Новый порядок первых 15 итераций

Чтобы старт был понятным и не слишком тяжёлым, начинаем так:

```text
1. create_project_structure.sh
2. backend/pyproject.toml
3. backend/.env.example
4. backend/app/modules/shared/domain/ids.py
5. backend/app/modules/shared/domain/exceptions.py
6. backend/app/modules/shared/domain/events.py
7. backend/app/modules/users/domain/enums.py
8. backend/app/modules/users/domain/entities.py
9. backend/app/modules/exercises/domain/enums.py
10. backend/app/modules/exercises/domain/value_objects.py
11. backend/app/modules/exercises/domain/entities.py
12. backend/app/modules/attempts/domain/enums.py
13. backend/app/modules/attempts/domain/value_objects.py
14. backend/app/modules/attempts/domain/entities.py
15. backend/tests/unit/attempts/domain/test_solution_attempt.py
```

После этого уже будет:

```text
модульная структура
shared kernel
users domain
exercises domain
attempts domain
первый unit-тест
```

---

# Контрольные точки обучения

## Контрольная точка 1 — структура

Вы понимаете:

```text
почему модульный монолит лучше преждевременных микросервисов
почему каждый модуль похож на будущий сервис
как папки помогают соблюдать границы
```

## Контрольная точка 2 — domain

Вы понимаете:

```text
entity
value object
enum
domain error
domain event
инвариант
```

## Контрольная точка 3 — application

Вы понимаете:

```text
use case
DTO
port
dependency inversion
fake repository
```

## Контрольная точка 4 — infrastructure

Вы понимаете:

```text
ORM model
repository adapter
mapper
migration
JSONB
Redis
outbox
```

## Контрольная точка 5 — presentation

Вы понимаете:

```text
Pydantic schema
FastAPI router
Depends
exception handler
HTTP boundary
```

## Контрольная точка 6 — микросервисная готовность

Вы понимаете:

```text
когда Kafka нужна
что такое outbox pattern
какой модуль можно вынести первым
почему не надо выносить всё сразу
```

---

# Итоговое архитектурное решение

Фиксируем:

```text
1. Не делаем микросервисы сразу.
2. Делаем модульный монолит.
3. Внутри модулей используем луковичную архитектуру.
4. Между модулями держим строгие границы.
5. События проектируем сразу.
6. Kafka оставляем как optional adapter.
7. Outbox pattern изучим до физического выноса сервисов.
8. Первым кандидатом на будущий микросервис будет ai_review.
```

---

# Следующий практический шаг

Начинаем с файла:

```text
create_project_structure.sh
```

Он создаст каркас модульного монолита:

```text
backend/app/modules/shared
backend/app/modules/users
backend/app/modules/exercises
backend/app/modules/attempts
backend/app/core
backend/tests
frontend
```

После него переходим к:

```text
backend/pyproject.toml
```

Затем начинаем ядро:

```text
backend/app/modules/shared/domain/ids.py
```
