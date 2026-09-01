# Content Factory

The **Content Factory** is a web application built with **Next.js** (TypeScript) that enables content creators to:

- Author and organize educational content
- Create lessons and learning paths
- Manage media assets and resources

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS

## Setup

### 1. Install Node.js

Requires Node.js 18+. Download from [https://nodejs.org](https://nodejs.org).

### 2. Install dependencies

```bash
cd content-factory
npm install
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the development server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### 5. Build for production

```bash
npm run build
npm start
```

## Project Structure

```
content-factory/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout with sidebar
│   │   ├── page.tsx         # Dashboard (placeholder)
│   │   ├── courses/
│   │   │   ├── page.tsx     # Courses list (clickable links to detail)
│   │   │   └── [id]/
│   │   │       └── page.tsx # Course detail: units + lessons management
│   │   ├── lessons/
│   │   │   └── [id]/
│   │   │           └── page.tsx # Lesson detail: curriculum upload + listing
│   │   ├── assets/          # Assets (placeholder)
│   │   └── settings/        # Settings (placeholder)
│   ├── components/
│   │   ├── Sidebar.tsx       # Admin sidebar navigation
│   │   └── NewCourseForm.tsx # Create course form
│   └── lib/
│       └── api.ts            # Reusable API client (courses, units, lessons, curriculum)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── .env.example
└── README.md
```

## Content Hierarchy

The Content Factory follows a **Course → Unit → Lesson** hierarchy:

1. **Courses** — list at `/courses`, detail at `/courses/{id}`
2. **Units** — created and managed on the Course detail page
3. **Lessons** — created inside units (expand a unit to see lessons)
4. **Curriculum** — uploaded on the Lesson detail page at `/lessons/{id}`

### Supported Curriculum File Types

- `.pptx` — PowerPoint presentations
- `.pdf` — PDF documents
- `.docx` — Word documents
- `.xlsx` — Excel spreadsheets

## Running Backend + Frontend Together

1. Start the backend (from the `backend/` directory):

```bash
uvicorn app.main:app --reload
```

2. Start the frontend (from the `content-factory/` directory):

```bash
npm run dev
```

3. Open `http://localhost:3000` in your browser.
4. Navigate to **Courses** to create and view courses.

## License

All rights reserved.
