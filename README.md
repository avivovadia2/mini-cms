# Mini CMS

Onboarding project: a small claims app (policies → FNOL → claims → exposures) built on the same stack and
versions as the Five Sigma CMS. Spec: Notion → Engineering Onboarding → Aviv Onboarding →
"Onboarding project: Mini Claims app".

```
backend/    Flask API (Python 3.11)
frontend/   React + TypeScript (Vite 4)
```

## Run locally from a clean machine (macOS)

### 1. Prerequisites

```bash
brew install pyenv nvm postgresql@17
pyenv install 3.11        # any 3.11.x
nvm install 20            # version pinned in .nvmrc
brew services start postgresql@17
```

### 2. Database

```bash
createdb mini_cms        # development
createdb mini_cms_test   # tests: rebuilt from the migrations on every pytest run
```

### 3. Backend — http://localhost:5001

```bash
cd backend
$(pyenv prefix 3.11)/bin/python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env          # adjust DATABASE_URL if your Postgres needs a user/password
.venv/bin/flask db upgrade    # apply the migrations
.venv/bin/flask run --debug
```

- Health check: http://localhost:5001/api/health → `{"status": "ok", "database": "ok"}`
- OpenAPI docs (spectree): http://localhost:5001/api/docs/swagger/

### 4. Frontend — http://localhost:5173

In a second terminal:

```bash
cd frontend
nvm use
npm install
npm run dev
```

Open the URL Vite prints (5173, or the next free port) and register an organization. API calls go through the Vite
proxy to the backend on 5001.

### Tests, lint, typecheck

```bash
cd backend  && .venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/ruff format --check .
cd frontend && npm test && npm run lint && npm run typecheck
```

Backend tests run against the real `mini_cms_test` Postgres database (override with `TEST_DATABASE_URL`). Frontend
tests (Vitest + Testing Library) render the whole app in jsdom and mock only the network.

## Choices and why

**Local environment: Homebrew Postgres + a Python venv + nvm, no Docker.**
Docker Compose would bring the database up with one command, but it adds a moving part for something only the
database needs, and a native Postgres is quicker to inspect with `psql`. The only external service is Postgres, and
its connection string lives in `backend/.env` (`DATABASE_URL`). To use Docker for the database instead, run
`docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_DB=mini_cms postgres:17` and nothing else
changes.

**Ports: backend on 5001, not Flask's default 5000.** On macOS, port 5000 is often taken (the AirPlay Receiver or
other local servers). The port is set in `backend/.env` (`FLASK_RUN_PORT`).

**Dev proxy instead of CORS.** Vite forwards `/api/*` to Flask, so the browser sees a single origin. No CORS
configuration is needed, and the frontend uses relative URLs (`/api/...`), the same as when both are served together.

**Backend structure: the CMS's third-generation service modules, one per domain.**

```
backend/app/
  __init__.py     create_app(): config → extensions → error handlers → modules → spectree
  registry.py     ModuleRegistration + get_service(Interface): lazy singletons, constructor injection
  errors.py       domain exceptions and the one place they become HTTP status codes
  schemas.py      Pydantic types shared by all modules (pagination, required text)
  modules/<name>/ organizations, users, auth
    interface.py  the module's public API (ABC)
    schemas/      Pydantic shapes in and out: data (`*Info`), requests, responses
    api/          spectree routes; the only layer that commits
    internal/     private: service (implements the interface), managers, models, exceptions
backend/migrations/   Alembic (Flask-Migrate). Schema changes only through migrations, never db.create_all()
```

Modules talk to each other only through `get_service(OtherInterface)` and schemas, never through each other's
`internal/` or ORM models. See `backend/app/modules/__init__.py`.

**Frontend structure.** `src/api/` (typed axios calls mirroring the backend schemas), `src/auth/` (the current user,
loaded once and shared through React context; `RequireAuth` guards every route except Login and Register),
`src/components/` (Base UI + Tailwind building blocks), `src/pages/`, and `src/validation.ts` (Yup rules that mirror
the server's).

**Health check also pings the database** (`SELECT 1`), and returns 503 if it can't reach it. A health check that only
proves Flask is up would hide the most likely local problem, a database that isn't running.

**Versions are pinned to the CMS** (Flask 2.3, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, Flask-Migrate 4.0, Flask-Login 0.6,
spectree 2.0, React 18.3, TypeScript 5.8, Vite 4, axios 0.21, Base UI 1.8, Tailwind 3, Formik 2.4, Yup 0.32,
react-router-dom 5.3, Vitest 2.1). Werkzeug is held on 2.3.x, the line released alongside Flask 2.3, rather than
jumping to 3.x. ESLint stays on 8 (what the Vite 4 template uses), with typescript-eslint 8 so it understands TypeScript 5.8.
