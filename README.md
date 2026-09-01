# LA App Platform

A portable, cloud-agnostic monorepo for **LA App** — a learning and content platform consisting of two main products:

## Products

### 1. Content Factory

A web application (Next.js) that allows content creators to design, author, and manage educational content, lessons, and learning paths for the platform.

- **Tech stack:** Next.js (TypeScript)
- **Location:** [`content-factory/`](./content-factory)

### 2. Learning Platform (Student App)

A mobile application used by students to consume content, follow lessons, track progress, and interact with learning material.

- **Tech stack:** Mobile app (framework TBD)
- **Location:** [`student-app/`](./student-app)

## Repository Structure

| Folder            | Purpose                                                      |
| ----------------- | ------------------------------------------------------------ |
| `content-factory/` | Next.js web app for content creation and management         |
| `backend/`         | FastAPI (Python) backend with PostgreSQL database           |
| `student-app/`     | Mobile application for students                              |
| `shared/`          | Shared schemas, types, and contracts across services         |
| `infrastructure/`  | Docker and deployment configuration                          |
| `docs/`            | Architecture and project documentation                       |

## Getting Started

This repository is in its initial scaffold stage. Each folder contains a placeholder README describing its future purpose.

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Development

Each service will have its own setup instructions. For now, the project can be bootstrapped using Docker Compose:

```bash
docker-compose up
```

## License

All rights reserved.
