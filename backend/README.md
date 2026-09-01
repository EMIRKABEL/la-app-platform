# LA App Backend

FastAPI backend for the LA App platform (Content Factory).

## Tech Stack

- **Python >=3.12,<3.13**
- **FastAPI** — Web framework
- **SQLAlchemy 2.0** — ORM
- **Pydantic v2** — Data validation
- **Alembic** — Database migrations
- **PostgreSQL** — Database (compatible with Supabase, AWS RDS, Docker, or self-hosted)
- **pytest** — Testing

## Setup

### 1. Create a Python virtual environment

```bash
cd backend
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and edit with your database URL:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://laapp:changeme@localhost:5432/laapp
```

> **Local development without PostgreSQL:**
> You can use SQLite temporarily by setting:
> ```
> DATABASE_URL=sqlite:///./laapp.db
> ```
> Then create tables with:
> ```bash
> python -c "from app.db.session import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
> ```

### 4. Run Alembic migrations (PostgreSQL)

```bash
alembic upgrade head
```

### 5. Run the FastAPI server locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Health check: `GET http://localhost:8000/health`

Interactive docs: `http://localhost:8000/docs`

### 6. Run tests

```bash
pytest
```

Tests use SQLite in-memory and do **not** require a running PostgreSQL instance.

## API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/health` | Health check |
| `GET` | `/api/courses` | List all courses (newest first) |
| `POST` | `/api/courses` | Create a new course |
| `GET` | `/api/courses/{course_id}` | Get a single course (404 if not found) |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route definitions
│   │   ├── __init__.py
│   │   └── courses.py       # Course CRUD endpoints
│   ├── core/                # Configuration and settings
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/                  # Database session and engine
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── types.py         # Portable JSONB type
│   ├── models/              # SQLAlchemy ORM models
│   │   └── ...
│   ├── repositories/        # Data-access layer
│   │   └── course_repository.py
│   ├── schemas/             # Pydantic schemas
│   │   └── course.py
│   └── services/            # Business logic layer
│       └── course_service.py
├── tests/                   # pytest test suite
├── alembic/                 # Migration scripts
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment file
├── .python-version          # Python 3.12
└── README.md
```

## Database Models

| Model            | Description                                        |
| ---------------- | -------------------------------------------------- |
| `Course`         | Top-level container for a course                    |
| `Unit`           | A unit within a course                             |
| `Lesson`         | A lesson within a unit, with lifecycle status     |
| `CurriculumSource` | Uploaded curriculum file linked to a lesson      |
| `LessonObjective`| Learning objectives associated with a lesson      |
| `Activity`       | Activities within a lesson, with JSON config       |
| `Asset`          | Media assets with approval workflow                |
| `LessonVersion`  | Versioned snapshots of lesson content (JSONB)       |

## License

All rights reserved.
