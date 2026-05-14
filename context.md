# Team Nexus — Full Codebase Context

## Project Overview
Production-ready SaaS Team Task Manager backend built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**.  
Entry point: `uvicorn app.main:app --reload`  
API docs: `/docs`

---

## Tech Stack
- **FastAPI** — web framework
- **SQLAlchemy 2.0** — ORM (async-style `select()` queries)
- **PostgreSQL** — database (via `psycopg2-binary`)
- **Alembic** — migrations
- **Pydantic v2 + pydantic-settings** — validation & config
- **python-jose** — JWT tokens
- **passlib[bcrypt]** — password hashing

---

## Directory Structure
```
Team nexus/
├── app/
│   ├── main.py                  # FastAPI app, router registration
│   ├── api/
│   │   ├── dependencies.py      # Auth dependency injection
│   │   ├── auth.py              # /auth routes
│   │   ├── users.py             # /users routes
│   │   ├── teams.py             # /teams routes
│   │   ├── team_members.py      # /teams/{id}/members routes
│   │   ├── projects.py          # /teams/{id}/projects + /projects routes
│   │   ├── tasks.py             # /projects/{id}/tasks + /tasks routes
│   │   └── health.py            # /health/check
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings, .env)
│   │   ├── database.py          # SQLAlchemy engine, SessionLocal, Base, get_db
│   │   └── security.py          # JWT + bcrypt utilities
│   ├── models/
│   │   ├── base.py              # BaseModel (id, created_at, updated_at)
│   │   ├── user.py              # User
│   │   ├── team.py              # Team
│   │   ├── team_member.py       # TeamMember (association)
│   │   ├── project.py           # Project
│   │   └── task.py              # Task
│   ├── schemas/
│   │   ├── auth.py              # UserCreate, UserResponse, Token, UserLogin, PasswordChange, TokenRefresh
│   │   ├── team.py              # TeamCreate, TeamUpdate, TeamResponse
│   │   ├── team_member.py       # TeamMemberAdd, TeamMemberResponse
│   │   ├── project.py           # ProjectCreate, ProjectUpdate, ProjectResponse
│   │   ├── task.py              # TaskCreate, TaskUpdate, TaskResponse
│   │   └── health.py            # HealthResponse
│   ├── services/
│   │   ├── auth.py              # AuthService
│   │   ├── team.py              # TeamService
│   │   ├── team_member.py       # TeamMemberService
│   │   ├── project.py           # ProjectService
│   │   └── task.py              # TaskService
│   ├── repositories/            # (empty, reserved for data access layer)
│   ├── middleware/              # (empty, reserved)
│   └── utils/                   # (empty, reserved)
├── alembic/
│   ├── env.py                   # Alembic config, imports all models
│   └── versions/                # 5 migration files
├── .env / .env.example
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── alembic.ini
```

---

## Configuration (`app/core/config.py`)
`Settings` class via `pydantic-settings`, loaded from `.env`:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Team Task Manager` | App display name |
| `APP_VERSION` | `0.1.0` | Version |
| `ENVIRONMENT` | `development` | Enables SQL echo in dev |
| `DATABASE_URL` | *(required)* | PostgreSQL connection string |
| `SECRET_KEY` | *(change in prod)* | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `BCRYPT_ROUNDS` | `12` | bcrypt cost factor |

`.env.example` DATABASE_URL: `postgresql+psycopg2://postgres:postgres@localhost:5432/team_task_manage`

---

## Database (`app/core/database.py`)
- `engine` — SQLAlchemy engine with `pool_pre_ping=True`, SQL echo in dev
- `SessionLocal` — `sessionmaker(autoflush=False, autocommit=False)`
- `Base` — `declarative_base()` shared by all models
- `get_db()` — FastAPI dependency yielding a `Session`, closes on exit

---

## Models

### BaseModel (`app/models/base.py`)
Abstract base for all models:
- `id` — Integer PK
- `created_at` — DateTime with timezone, server default `now()`
- `updated_at` — DateTime with timezone, auto-updates on change

### User (`app/models/user.py`) — table: `users`
| Column | Type | Notes |
|---|---|---|
| `email` | String(255) | unique, indexed, not null |
| `hashed_password` | String(128) | bcrypt hash |
| `full_name` | String(100) | not null |
| `is_active` | Boolean | default True |
| `is_superuser` | Boolean | default False |

Relationships:
- `team_memberships` → `TeamMember` (cascade delete-orphan)
- `assigned_tasks` → `Task` (via `Task.assignee_id`)

### Team (`app/models/team.py`) — table: `teams`
| Column | Type | Notes |
|---|---|---|
| `name` | String(100) | not null |
| `description` | Text | nullable |
| `owner_id` | Integer FK → `users.id` | CASCADE delete, indexed |

Relationships:
- `owner` → `User` (lazy=joined)
- `members` → `TeamMember` (cascade delete-orphan)
- `projects` → `Project` (cascade delete-orphan)

### TeamMember (`app/models/team_member.py`) — table: `team_members`
| Column | Type | Notes |
|---|---|---|
| `team_id` | Integer FK → `teams.id` | CASCADE delete, indexed |
| `user_id` | Integer FK → `users.id` | CASCADE delete, indexed |
| `role` | String(50) | default `"member"` |

Unique constraint: `(team_id, user_id)`

### Project (`app/models/project.py`) — table: `projects`
| Column | Type | Notes |
|---|---|---|
| `team_id` | Integer FK → `teams.id` | CASCADE delete, indexed |
| `name` | String(100) | not null |
| `description` | Text | nullable |
| `status` | String(50) | default `"active"` |

Relationships:
- `team` → `Team`
- `tasks` → `Task` (cascade delete-orphan)

### Task (`app/models/task.py`) — table: `tasks`
| Column | Type | Notes |
|---|---|---|
| `project_id` | Integer FK → `projects.id` | CASCADE delete, indexed |
| `title` | String(200) | not null |
| `description` | Text | nullable |
| `status` | String(50) | `todo\|in_progress\|review\|done`, default `"todo"` |
| `priority` | String(50) | `low\|medium\|high`, default `"medium"` |
| `assignee_id` | Integer FK → `users.id` | SET NULL on delete, nullable |
| `due_date` | Date | nullable |

---

## Schemas (Pydantic v2)

### Auth (`app/schemas/auth.py`)
- `UserCreate` — `email`, `full_name`, `password` (min 8 chars)
- `UserResponse` — `id`, `email`, `full_name`, `is_active`, `is_superuser`
- `UserLogin` — `email`, `password`
- `Token` — `access_token`, `refresh_token`, `token_type="bearer"`
- `TokenRefresh` — `refresh_token`
- `PasswordChange` — `current_password`, `new_password`

### Team (`app/schemas/team.py`)
- `TeamCreate` — `name` (max 100), `description?`
- `TeamUpdate` — all optional
- `TeamResponse` — `id`, `name`, `description`, `owner_id`

### TeamMember (`app/schemas/team_member.py`)
- `TeamMemberAdd` — `user_id`, `role?` (default `"member"`)
- `TeamMemberResponse` — `id`, `team_id`, `user_id`, `role`

### Project (`app/schemas/project.py`)
- `ProjectCreate` — `name`, `description?`, `status?` (default `"active"`)
- `ProjectUpdate` — all optional
- `ProjectResponse` — `id`, `team_id`, `name`, `description`, `status`

### Task (`app/schemas/task.py`)
- `TaskStatus` = `Literal["todo", "in_progress", "review", "done"]`
- `TaskPriority` = `Literal["low", "medium", "high"]`
- `TaskCreate` — `title`, `description?`, `status?`, `priority?`, `assignee_id?`, `due_date?`
- `TaskUpdate` — all optional
- `TaskResponse` — `id`, `project_id`, `title`, `description`, `status`, `priority`, `assignee_id`, `due_date`

---

## Services (Business Logic)

### AuthService (`app/services/auth.py`)
- `register_user(db, user_create)` — checks email uniqueness, hashes password, creates User; raises `ValueError` if email taken
- `authenticate_user(db, email, password)` — verifies password + active status; returns `User` or `None`
- `get_user_by_id(db, user_id)` — lookup by PK
- `get_user_by_email(db, email)` — lookup by email
- `create_tokens(user_id)` — returns `Token` with access + refresh JWTs (`sub=str(user_id)`)
- `change_password(db, user, current_password, new_password)` — verifies current, hashes new; raises `ValueError` if wrong

### TeamService (`app/services/team.py`)
- `create_team(db, team_create, owner_id)` → `Team`
- `get_teams_for_user(db, owner_id)` → `List[Team]`
- `get_team_by_id(db, team_id)` → `Team | None`
- `update_team(db, team, team_update)` → `Team` (partial update via `model_dump(exclude_unset=True)`)
- `delete_team(db, team)` → `None`

### TeamMemberService (`app/services/team_member.py`)
- `add_member_to_team(db, team, member_add)` → `TeamMember`; raises `ValueError` if user not found or already member
- `get_team_members(db, team_id)` → `List[TeamMember]`
- `get_membership(db, team_id, user_id)` → `TeamMember | None`
- `remove_member_from_team(db, membership)` → `None`

### ProjectService (`app/services/project.py`)
- `create_project(db, project_create, team_id)` → `Project`
- `get_projects_for_team(db, team_id)` → `List[Project]`
- `get_project_by_id(db, project_id)` → `Project | None`
- `update_project(db, project, project_update)` → `Project`
- `delete_project(db, project)` → `None`

### TaskService (`app/services/task.py`)
- `create_task(db, task_create, project_id, team_id)` → `Task`; validates assignee is team member/owner
- `get_tasks_for_project(db, project_id)` → `List[Task]`
- `get_task_by_id(db, task_id)` → `Task | None`
- `update_task(db, task, task_update, team_id)` → `Task`; validates new assignee
- `delete_task(db, task)` → `None`
- `_validate_assignee(db, assignee_id, team_id)` — checks user exists and is team member OR team owner

---

## API Endpoints

### Auth (`/auth`) — `app/api/auth.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register user → returns `Token` |
| POST | `/auth/login` | No | Login with JSON → returns `Token` |
| POST | `/auth/login/oauth2` | No | OAuth2 form login (Swagger UI) |
| POST | `/auth/refresh` | No | Refresh access token |
| GET | `/auth/me` | Active user | Get current user profile |
| POST | `/auth/change-password` | Active user | Change password |
| POST | `/auth/logout` | Active user | Client-side logout placeholder |

### Users (`/users`) — `app/api/users.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | JWT | Get own profile |
| GET | `/users/` | Superuser | List all users (skip/limit) |
| GET | `/users/{user_id}` | Superuser | Get user by ID |
| POST | `/users/{user_id}/activate` | Superuser | Activate user |
| POST | `/users/{user_id}/deactivate` | Superuser | Deactivate user |

### Teams (`/teams`) — `app/api/teams.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/teams/` | Active user | Create team (owner = current user) |
| GET | `/teams/` | Active user | List own teams |
| GET | `/teams/{team_id}` | Owner | Get team by ID |
| PUT | `/teams/{team_id}` | Owner | Update team |
| DELETE | `/teams/{team_id}` | Owner | Delete team |

### Team Members (`/teams/{team_id}/members`) — `app/api/team_members.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/teams/{team_id}/members` | Owner | Add member |
| GET | `/teams/{team_id}/members` | Member or Owner | List members |
| DELETE | `/teams/{team_id}/members/{user_id}` | Owner | Remove member |

### Projects — `app/api/projects.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/teams/{team_id}/projects` | Owner | Create project |
| GET | `/teams/{team_id}/projects` | Member or Owner | List team projects |
| GET | `/projects/{project_id}` | Member or Owner | Get project |
| PUT | `/projects/{project_id}` | Owner | Update project |
| DELETE | `/projects/{project_id}` | Owner | Delete project |

### Tasks — `app/api/tasks.py`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/projects/{project_id}/tasks` | Member or Owner | Create task |
| GET | `/projects/{project_id}/tasks` | Member or Owner | List project tasks |
| GET | `/tasks/{task_id}` | Member or Owner | Get task |
| PUT | `/tasks/{task_id}` | Owner or Assignee | Update task |
| DELETE | `/tasks/{task_id}` | Owner | Delete task |

### Health
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health/check` | No | Returns `{"status": "ok"}` |
| GET | `/` | No | Welcome message |

---

## Auth Dependencies (`app/api/dependencies.py`)
- `get_current_user` — decodes JWT, fetches user from DB, raises 401/403
- `get_current_active_user` — wraps `get_current_user`, raises 400 if inactive
- `get_current_superuser` — wraps `get_current_user`, raises 403 if not superuser
- OAuth2 scheme: `tokenUrl="auth/login"`

---

## Security (`app/core/security.py`)
- `hash_password(password)` — bcrypt hash
- `verify_password(plain, hashed)` — bcrypt verify
- `create_access_token(data, expires_delta?)` — JWT with `type="access"`, default 30 min
- `create_refresh_token(data)` — JWT with `type="refresh"`, default 7 days
- `decode_token(token)` — returns payload dict or `None` on failure

JWT payload: `{"sub": "<user_id_str>", "exp": <timestamp>, "type": "access|refresh"}`

---

## Authorization Rules Summary
| Action | Who can do it |
|---|---|
| Create/update/delete team | Team owner |
| View team | Team owner |
| Add/remove team members | Team owner |
| View team members | Team owner or any member |
| Create/update/delete project | Team owner |
| View projects | Team owner or any member |
| Create task | Team owner or any member |
| View tasks | Team owner or any member |
| Update task | Team owner OR task assignee |
| Delete task | Team owner only |
| List/manage all users | Superuser only |

---

## Database Migrations (Alembic)
Migration order:
1. `6a34c8535bdf` — users table
2. `45486a0e7f3d` — teams table
3. `3db58f9ea050` — team_members table
4. `fcb490eed27f` — projects table
5. `b8a70b5a4e6f` — tasks table

Commands:
```bash
alembic upgrade head          # apply all migrations
alembic revision --autogenerate -m "message"  # create new migration
alembic downgrade -1          # rollback one step
```

---

## Docker
`docker-compose.yml` defines two services:
- `db` — `postgres:16-alpine`, port `5432`, healthcheck via `pg_isready`
- `backend` — built from `Dockerfile`, port `8000`, depends on `db` health

Both on `team_nexus_network` bridge network. Postgres data persisted in `postgres_data` volume.

---

## Future / Planned
- Multi-tenant architecture with organizations
- Token blacklist (Redis) for proper logout
- Role-based access control (RBAC) beyond owner/member
- `repositories/` layer for data access abstraction
- `middleware/` for request logging, rate limiting, etc.
