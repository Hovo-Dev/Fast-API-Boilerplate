# FastAPI Boilerplate

Async FastAPI starter with PostgreSQL, Alembic migrations, user and project management, and Docker Compose.

## Stack

- **FastAPI** + **SQLAlchemy 2.0** (fully async)
- **Pydantic v2** validation
- **FastCRUD** for CRUD + pagination
- **Alembic** — separate migrations for users and projects
- **PostgreSQL** via asyncpg
- **structlog** for structured logging
- **Docker Compose** (one command)

## Quickstart

```bash
git clone https://github.com/<you>/FastAPI-boilerplate
cd FastAPI-boilerplate
docker compose up --build
```

The app waits for Postgres, runs `alembic upgrade head`, then starts Uvicorn.

- API docs: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Local dev without Docker

```bash
uv sync
cp scripts/local_with_uvicorn/.env.example src/.env
# edit src/.env with your local Postgres details
cd src && uv run alembic upgrade head
cd .. && uv run uvicorn src.app.main:app --reload
```

## Configuration

Copy `.env.example` to `src/.env` and set:

```env
APP_NAME="My Project"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
ENVIRONMENT=local   # local | staging | production
```

`ENVIRONMENT` controls API docs exposure — docs are hidden in `production`.

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users` | List users (paginated) |
| GET | `/api/v1/users/{id}` | Get user by id |
| DELETE | `/api/v1/users/{id}` | Delete user (blocked if owns active projects) |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project by id |
| GET | `/api/v1/users/{id}/projects` | List projects by user |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/ready` | Readiness check (includes DB) |

## Migrations

Migrations are split — users first, projects depend on users:

```
migrations/versions/
  20260518_0714_create_users_table.py
  20260518_0715_create_projects_table.py
```

Add a new migration:

```bash
cd src && uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

## Deployment scripts

`setup.py` copies the right files for your deployment target:

```bash
./setup.py local       # Uvicorn with auto-reload
./setup.py staging     # Gunicorn + Uvicorn workers
./setup.py production  # NGINX + Gunicorn + Uvicorn workers
```

Each option copies a `Dockerfile`, `docker-compose.yml`, and `.env.example` from `scripts/`.

## Project structure

```
src/
  app/
    api/v1/          # Route handlers
    core/
      config.py      # Settings (pydantic-settings)
      db/            # SQLAlchemy engine + session + Base
      exceptions/    # HTTP exception re-exports
    crud/            # FastCRUD instances
    middleware/      # Logger middleware
    models/          # SQLAlchemy ORM models
    schemas/         # Pydantic schemas
    services/        # Business logic
  migrations/        # Alembic env + versions
```

## License

[MIT](LICENSE.md)
