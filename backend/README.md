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
| `GET` | `/api/courses/{course_id}/units` | List all units in a course |
| `POST` | `/api/courses/{course_id}/units` | Create a new unit in a course |
| `GET` | `/api/units/{unit_id}` | Get a single unit (404 if not found) |
| `GET` | `/api/units/{unit_id}/lessons` | List all lessons in a unit |
| `POST` | `/api/units/{unit_id}/lessons` | Create a new lesson (default status: draft) |
| `GET` | `/api/lessons/{lesson_id}` | Get a single lesson (404 if not found) |
| `POST` | `/api/lessons/{lesson_id}/curriculum` | Upload a curriculum file (multipart/form-data) |
| `GET` | `/api/lessons/{lesson_id}/curriculum` | List curriculum files for a lesson |

## Hierarchy

Content is organized as **Course → Unit → Lesson**:

1. A **Course** is the top-level container (e.g. "English A1")
2. A **Unit** belongs to a Course (e.g. "Unit 1: Greetings")
3. A **Lesson** belongs to a Unit (e.g. "Lesson 1: Hello and Goodbye")

Each Lesson can have one or more **Curriculum Source** files uploaded.

## Curriculum Upload

### Supported File Types

- `.pptx` — PowerPoint presentations
- `.pdf` — PDF documents
- `.docx` — Word documents
- `.xlsx` — Excel spreadsheets

Unsupported file types are rejected with HTTP 415.

### Upload Endpoint

```
POST /api/lessons/{lesson_id}/curriculum
Content-Type: multipart/form-data
```

The uploaded file is stored locally during development and a
`CurriculumSource` database record is created with:

| Field               | Description                                      |
| ------------------- | ------------------------------------------------ |
| `lesson_id`         | The lesson the file belongs to                   |
| `original_filename` | The filename as uploaded by the user             |
| `file_type`         | The file extension (e.g. `pptx`, `pdf`)          |
| `storage_path`      | Relative path within the storage root            |
| `uploaded_at`       | Timestamp of upload                              |
| `processing_status` | Always `pending` initially (AI analysis is Step 6) |

## Local File Storage

Uploaded curriculum files are stored on the local filesystem during
development under:

```
storage/curriculum/{course_id}/{unit_id}/{lesson_id}/{safe_filename}
```

### Configuration

The storage root is configured via the `STORAGE_ROOT` environment variable:

```
STORAGE_ROOT=../storage
```

Relative paths resolve from the `backend/` directory.

### Storage Abstraction

The backend uses a `StorageProvider` abstraction layer:

- `StorageProvider` — abstract base class (ABC)
- `LocalStorageProvider` — default implementation for development

To move to cloud storage later, implement a new class
(e.g. `S3StorageProvider`, `R2StorageProvider`, `MinIOStorageProvider`)
that inherits from `StorageProvider` and inject it into
`CurriculumService`. No lesson or curriculum logic needs to change.

### Security

- Filenames are sanitized to prevent path traversal attacks
- Original filenames are preserved in the database record
- The `storage_path` in the database is always relative to the storage root

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
