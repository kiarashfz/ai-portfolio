# PortfolioGPT

**A personal portfolio that visitors can talk to.**

PortfolioGPT turns a professional profile into a shareable website with an AI
assistant. Create an account, describe your skills and experience, and share your
username URL. Visitors can explore your profile and ask questions grounded in
its content through retrieval-augmented generation (RAG).

## Features

- Account signup and signin with bcrypt password hashing and RSA-signed JWTs.
- A dashboard to create and update your profile, skills, work experience,
  education, and website/GitHub/LinkedIn links.
- Public portfolio pages at `/<username>`.
- Portfolio-scoped chat with conversation history stored in PostgreSQL.
- Embedding ingestion and semantic retrieval through Milvus.
- OpenAI-compatible chat and embedding providers configured independently.
- Responsive interface with animated sections and Markdown chat responses.

## Stack and structure

| Layer | Technologies |
| --- | --- |
| Web | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Radix UI, Framer Motion |
| API | FastAPI, Pydantic, SQLModel / SQLAlchemy, Alembic |
| Storage | PostgreSQL, Milvus, MinIO, Redis |
| AI | OpenAI Python SDK with configurable compatible provider URLs |

```text
backend/
  app/
    api/                 # Health and versioned HTTP routes
    core/                # Settings and service wiring
    db/                  # Models, repositories, portfolio migration chain
    migrations/          # Older migration chain retained for reference
    rsa/                 # Generate your own signing keys locally
    services/            # Auth, portfolio, chat/RAG, provider and file services
  docker-compose.yml     # Milvus, etcd, MinIO and Attu
  .env.example
  requirements.txt
  requirements-private.txt
frontend/
  src/app/               # Landing, authentication, dashboard and public pages
  src/components/
  src/context/           # Authentication state
  src/lib/               # API client and shared utilities
  .env.example
```

## Run locally

### Prerequisites

- Python 3.12 and Node.js 20.9+ (the frontend `.nvmrc` selects Node.js 24).
- PostgreSQL and Redis running locally or on accessible hosts.
- Docker with Compose for the included Milvus stack.
- Chat and embedding provider credentials.
- Access to the original `ec_*` Python packages. These are external shared
  dependencies, **not included in this repository**. Their installed versions are
  listed in `backend/requirements-private.txt`. Configure your authorized package
  registry before installing them; public dependencies alone cannot start the API.

### 1. Configure the backend

From the repository root:

```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install -r backend/requirements.txt
# After configuring access to your original ec_* package registry:
python -m pip install -r backend/requirements-private.txt
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your database, Redis, storage and AI provider settings.
The secondary `POSTGRES_COMMERCE_*` client and the legacy integration variables
remain required by the existing service wiring. For local use, both PostgreSQL
clients can point to the same database.

Generate a new RSA key pair:

```bash
mkdir -p backend/app/rsa
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out backend/app/rsa/private.key
openssl rsa -pubout -in backend/app/rsa/private.key -out backend/app/rsa/public.pem
chmod 600 backend/app/rsa/private.key
```

The application reads these files when loading settings. Each installation must
supply its own keys. Environment files, keys, API request scratch files, editor
settings, dependency directories and generated files are excluded from Git.

### 2. Start supporting services

```bash
docker compose -f backend/docker-compose.yml up -d
```

The compose file starts Milvus (`19530`), etcd (`2379`), MinIO (`9000`, console
`9001`) and Attu (`8000`). PostgreSQL and Redis must be provisioned separately.
The compose credentials are local development defaults; change them before any
shared deployment. No application servers are started by this compose file.

### 3. Prepare the database

Create the database and user matching your `.env`. The historical Alembic files
are preserved, but the portfolio chain currently creates a `chat` table in one
revision and later expects a `portfolio` table. Review and repair this migration
chain before applying it to a database; a fresh `alembic upgrade head` is not a
verified setup path. The active portfolio models live in `backend/app/db/models.py`
and the corresponding migration directory is `backend/app/db/migrations`.

### 4. Start the API

In the activated virtual environment, export the settings and run from `backend/app`:

```bash
set -a
source backend/.env
set +a
cd backend/app
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

These commands assume you begin at the repository root. Settings read process
environment variables; the `.env` is explicitly loaded by the shell here.
API documentation is available at http://localhost:8080/docs with the default
empty `API_SERVICE_PREFIX`.

### 5. Start the frontend

In another terminal, from the repository root:

```bash
cd frontend
nvm use # Optional, if you use nvm
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. `NEXT_PUBLIC_API_BASE_URL` defaults to
`http://localhost:8080`; set it before building for another environment. It is
included in the browser bundle, so it must contain no secrets.

## API overview

Paths below use the default empty service prefix.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/v1/users/signup` | Create account and return tokens |
| POST | `/v1/users/signin` | Authenticate and return tokens |
| GET | `/v1/portfolio/me/portfolio` | Read your portfolio (Bearer token) |
| PATCH | `/v1/portfolio/me/portfolio` | Create/update and re-index your portfolio (Bearer token) |
| GET | `/v1/portfolio/{username}` | Read a public portfolio |
| POST | `/v1/chat/{portfolio_username}/chat` | Ask a question about a portfolio |

## Development checks

```bash
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

## Current limitations

This repository preserves an existing development project. Full backend startup
requires the external `ec_*` packages, configured infrastructure, valid model
credentials and a reviewed database migration path. The included compose stack
has no persistent volume configuration. The current API permits wildcard CORS
origins while enabling credentials; configure explicit origins for browser calls
that include credentials. Authentication and chat session behavior also need
review before production use. No live service is implied by the
`portfoliogpt.com` strings retained in UI metadata and response examples.
