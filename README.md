# Team Task Manager Backend

A production-ready SaaS Team Task Manager backend built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- Modular and scalable architecture
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations for database versioning
- Environment variable configuration
- Dependency injection for database sessions
- Prepared for multi-tenant SaaS architecture

## Setup

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the database URL and other settings as needed

5. **Set up the database**
   - Ensure PostgreSQL is running
   - Create a database for the application

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

- To create a new migration: `alembic revision --autogenerate -m "Migration message"`
- To apply migrations: `alembic upgrade head`
- To rollback: `alembic downgrade -1`

## Architecture

- `app/api/` - API routes and endpoints
- `app/core/` - Core functionality (config, database)
- `app/models/` - Database models
- `app/schemas/` - Pydantic schemas for validation
- `app/services/` - Business logic services
- `app/repositories/` - Data access layer
- `app/middleware/` - Custom middleware
- `app/utils/` - Utility functions

## Future Features

- Multi-tenant architecture with organizations
- User authentication and authorization
- Project and task management
- Role-based access control