# Mini CMS — onboarding project

A small claims app (policies → FNOL → claims → exposures) built on the same stack and versions as the Five Sigma CMS.
**The goal is learning, not a product:** the author must be able to explain every line in review.

- Spec: Notion → Dev → Engineering Onboarding → Aviv Onboarding → "Onboarding project: Mini Claims app"
- Jira: project NGTPA, epic NGTPA-31206. One Story per milestone (M0 = NGTPA-31483).
- Reviewer: Yaron Elhadad. One PR per milestone, reviewed before the next milestone starts.

## How Claude should help (important)

- **Mix mode:** Claude may scaffold boilerplate (configs, tooling, app wiring, build setup). The author writes the
  business logic, models, migrations' content decisions, API schemas, and tests. When a task touches those, explain the
  approach, point to CMS patterns, and review — don't just generate the solution unless explicitly asked.
- Whatever Claude writes must be small and explainable; walk through it after writing.
- Never copy CMS code. Reading it for patterns is fine.
- No over-engineering: no generic repositories, plugin systems, or abstract base classes nothing needs.
  Three similar lines beat a premature abstraction.

## Stack (pinned to CMS versions — do not upgrade)

Backend: Python 3.11, Flask 2.3, SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1, Flask-Migrate 4.0 (Alembic),
Flask-Login 0.6, spectree 2.0 + Pydantic 2, pytest 7.4, ruff 0.6, PostgreSQL 15+.

Frontend: React 18.3, TypeScript 5.8, Vite 4, BaseUI 5 + Tailwind 3, Formik 2.4 + Yup 0.32, axios 0.21,
react-router-dom 5.3, Vitest 2.1.

## Layout

```
backend/    Flask app (app factory in app/__init__.py), migrations/, tests/, requirements.txt, pyproject.toml (ruff)
frontend/   Vite + React + TS app; dev server proxies /api to the backend
```

Backend follows the CMS's **third-generation service modules** (see `backend/app/modules/__init__.py`):
- One module per domain under `app/modules/<name>/`: `interface.py` (ABC), `schemas/`, `api/`, and a private
  `internal/` (`service.py`, `managers/`, `models/`, `exceptions.py`).
- Outside a module, only its `interface` and `schemas` may be imported — never `internal/`. Services are fetched with
  `get_service(Interface)` from `app/registry.py` (deliberately no `@inject`/`Depends()`, permissions or events).
- Each module exposes a `ModuleRegistration` that is listed in `MODULE_REGISTRATIONS`.
- Managers never commit; the API layer commits. Current org comes from `current_user.organization_id`.
- Tests: `backend/tests/modules/<name>/test_*.py`, `class Test<Thing>:` / `def test_<behaviour>`. The test DB
  (`mini_cms_test`) is rebuilt from the migrations once per session and truncated after each test.

## Commands

Backend (from `backend/`, venv at `backend/.venv`):
- Run: `.venv/bin/flask run --debug` (port 5001, from `.env`; 5000 is often taken on macOS)
- Migrate: `.venv/bin/flask db migrate -m "..."` then `.venv/bin/flask db upgrade`
- Lint: `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
- Tests: `.venv/bin/pytest`

Frontend (from `frontend/`):
- Run: `npm run dev` (port 5173)
- Lint / typecheck: `npm run lint && npm run typecheck`
- Tests: `npm test`

## Rules the code must follow (from the spec)

- Schema changes only through Alembic migrations — never `db.create_all()`. One migration per milestone PR.
- All API routes live under `/api`, are declared with spectree, and use Pydantic request/response models.
- Multi-tenancy: every table except `organization` has `organization_id`; every query is scoped to the current
  user's org. Another org's resource → **404**, never 403. A cross-org data leak is a project failure.
- Business errors are domain exceptions mapped to HTTP in one place: not found → 404, invalid transition /
  duplicate conversion → 409, validation → 422. No session → 401.
- List endpoints paginate (max 100/page), return a total count, and must not N+1.
- Tests assert outcomes (DB state, response body), not that helpers were called. Backend tests use a real Postgres DB.
- Every form uses Formik + Yup; client rules mirror server rules; server errors show on the form.
