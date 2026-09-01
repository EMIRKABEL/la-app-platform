# LA App Platform

A portable, cloud-agnostic monorepo for **LA App** — a learning and content platform consisting of two main products:

## Products

### 1. Content Factory

A web application (Next.js) that allows content creators to design, author, and manage educational content, lessons, and learning paths for the platform.

- **Tech stack:** Next.js (TypeScript), Tailwind CSS
- **Location:** [`content-factory/`](./content-factory)

### 2. Learning Platform (Student App)

A mobile application used by students to consume content, follow lessons, track progress, and interact with learning material.

- **Tech stack:** Mobile app (framework TBD)
- **Location:** [`student-app/`](./student-app)

## Repository Structure

| Folder             | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| `content-factory/` | Next.js web app for content creation and management         |
| `backend/`         | FastAPI (Python) backend with PostgreSQL database           |
| `student-app/`     | Mobile application for students                              |
| `shared/`          | Shared schemas, types, and contracts across services        |
| `infrastructure/`  | Docker and deployment configuration                          |
| `docs/`            | Architecture and project documentation                      |

## Getting Started

### Prerequisites

- Python >=3.12,<3.13
- Node.js 18+
- PostgreSQL 16 (or use SQLite for local development)

### Running the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env — use SQLite for quick local dev:
#   DATABASE_URL=sqlite:///./laapp.db
# Or use PostgreSQL:
#   DATABASE_URL=postgresql://laapp:changeme@localhost:5432/laapp

# Create tables (SQLite)
python -c "from app.db.session import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"

# Run migrations (PostgreSQL)
# alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.
API docs at `http://localhost:8000/docs`.

### Running the Frontend

```bash
cd content-factory
npm install

cp .env.example .env
# Edit .env — ensure NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

Frontend runs at `http://localhost:3000`.

### Running Both Together

1. Start the backend in one terminal:
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```

2. Start the frontend in another terminal:
   ```bash
   cd content-factory && npm run dev
   ```

3. Open `http://localhost:3000` in your browser.

4. Navigate to **Courses** to create and view courses.
5. Click a course to open its detail page — create **Units** and **Lessons**.
6. Open a lesson to upload **curriculum files** (PPTX, PDF, DOCX, XLSX).

### Content Hierarchy

Content is organized as **Course → Unit → Lesson**:

- A **Course** is the top-level container (e.g. "English A1")
- A **Unit** belongs to a Course (e.g. "Unit 1: Greetings")
- A **Lesson** belongs to a Unit (e.g. "Lesson 1: Hello and Goodbye")
- Each Lesson can have **Curriculum Source** files uploaded

### Curriculum Upload Workflow

1. Create a Course
2. Create a Unit inside the Course
3. Create a Lesson inside the Unit
4. Open the Lesson and click **Upload Curriculum**
5. Select a `.pptx`, `.pdf`, `.docx`, or `.xlsx` file
6. The file is stored locally and a `CurriculumSource` record is created
7. The curriculum list on the Lesson page refreshes automatically

### Local Storage

Uploaded curriculum files are stored under `storage/curriculum/` during
development. The storage root is configured via `STORAGE_ROOT` in
`backend/.env`.

The backend uses a `StorageProvider` abstraction (`LocalStorageProvider`
for development) so storage can later move to S3, Cloudflare R2, Supabase
Storage, or MinIO without changing application logic.

### Docker

The project can also be bootstrapped using Docker Compose:

```bash
docker-compose up
```

## License

All rights reserved.
