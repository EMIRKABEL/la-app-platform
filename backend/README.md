# LA App Backend

FastAPI backend for the LA App platform (Content Factory).

## Tech Stack

- **Python 3.11+**
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

### 4. Run Alembic migrations

```bash
alembic upgrade head
```

### 5. Run the FastAPI server locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Health check: `GET http://localhost:8000/health`

### 6. Run tests

```bash
pytest
```

Tests use SQLite in-memory and do **not** require a running PostgreSQL instance.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route definitions (future)
│   │   └── __init__.py
│   ├── core/                # Configuration and settings
│   │   └── config.py
│   ├── db/                  # Database session and engine
│   │   └── session.py
│   ├── models/              # SQLAlchemy ORM models
│   │   └── ...
│   ├── schemas/             # Pydantic schemas (future)
│   │   └── __init__.py
│   └── services/            # Business logic (future)
│       └── __init__.py
├── tests/                   # pytest test suite
├── alembic/                 # Migration scripts
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment file
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
