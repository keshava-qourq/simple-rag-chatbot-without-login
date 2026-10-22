# Developer Guide

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start status -->
_Up to date._
<!-- sdlc:auto:end status -->

<!-- sdlc:auto:start source -->
Generated from commit `d2d4c0a` · model `claude-sonnet-5`
<!-- sdlc:auto:end source -->

<!-- sdlc:auto:start overview -->
A simple RAG chatbot application with a FastAPI backend (Python) and a Vite + React 19 SPA frontend. The backend currently ships only a health check endpoint with SQLAlchemy models and database setup ready for expansion; the frontend renders seeded sample data with an API client seam prepared for real backend wiring. A docker-compose file provisions PostgreSQL 16 and MinIO for local infrastructure.
<!-- sdlc:auto:end overview -->

<!-- sdlc:auto:start prerequisites -->
- Node.js 20+
- Python 3.12+
- Docker and Docker Compose (for PostgreSQL/MinIO)
<!-- sdlc:auto:end prerequisites -->

<!-- sdlc:auto:start setup -->
1. cd frontend && npm install
2. cd ../backend && pip install -r requirements.txt
3. (optional) docker compose up -d to start PostgreSQL and MinIO
4. cd backend && uvicorn app.main:app --reload
5. cd frontend && npm run dev
<!-- sdlc:auto:end setup -->

<!-- sdlc:auto:start run -->
| Name | Command | Description |
|---|---|---|
| frontend dev | `cd frontend && npm run dev` | Starts the Vite dev server for the React SPA |
| backend dev | `cd backend && uvicorn app.main:app --reload` | Starts the FastAPI service with auto-reload on port 8000 |
| frontend build | `cd frontend && npm run build` | Bundles the frontend for production (does not typecheck) |
| frontend preview | `cd frontend && npm run preview` | Serves the production build locally |
| frontend lint | `cd frontend && npm run lint` | Runs ESLint over the frontend |
| frontend format | `cd frontend && npm run format` | Formats frontend code with Prettier |
| frontend typecheck | `cd frontend && npm run typecheck` | Runs tsc --noEmit for type checking |
| backend lint | `cd backend && ruff check .` | Lints the backend with ruff |
| backend format | `cd backend && ruff format .` | Formats backend code with ruff |
<!-- sdlc:auto:end run -->

<!-- sdlc:auto:start structure -->
| Path | Purpose |
|---|---|
| `backend/` | FastAPI service with app entrypoint, database setup, models, schemas, services, routers, tests, and config files |
| `backend/app/` | Application package containing main.py, database.py, models.py, schemas.py, services.py, and routers/ |
| `backend/tests/` | Backend test suite (pytest) including health check test |
| `frontend/` | Vite + React 19 SPA with screens, lib utilities, tests, and config |
| `frontend/src/` | Frontend source: main.tsx entry, lib/ with api client and UI vocabulary, and CSS |
| `frontend/e2e/` | Playwright end-to-end acceptance tests |
| `docker-compose.yml` | Provisions PostgreSQL 16 and MinIO containers with persistent volumes |
<!-- sdlc:auto:end structure -->

<!-- sdlc:auto:start conventions -->
- Backend uses FastAPI 0.115 with SQLAlchemy 2.0 and Pydantic 2; one router per architecture component
- Stub routes return a typed StubResponse so the OpenAPI document stays complete before handlers are implemented
- Backend defaults to SQLite via DATABASE_URL env var, swappable to PostgreSQL without code changes
- CORS allows Vite dev origins by default; override with ALLOWED_ORIGINS env var
- Frontend uses React 19 with react-router-dom 7 and Tailwind CSS 4
- Frontend imports use the @ alias mapped to ./src
- Generated screens render seeded sample data; src/lib/api.ts provides the seam for real API calls
- Test files live beside the code they cover (frontend src/**/*.{test,spec}.{ts,tsx}; backend tests/)
<!-- sdlc:auto:end conventions -->

<!-- sdlc:auto:start testing -->
| Name | Command | Description |
|---|---|---|
| frontend unit tests | `cd frontend && npm run test` | Runs Vitest component tests scoped to src/ |
| frontend e2e tests | `cd frontend && npm run test:e2e` | Runs Playwright acceptance tests; boots backend and preview server automatically when E2E_BASE_URL is not set |
| install e2e browser | `cd frontend && npm run test:e2e:install` | Installs Chromium for Playwright |
| backend tests | `cd backend && pytest` | Runs pytest with coverage from the backend directory |
<!-- sdlc:auto:end testing -->

<!-- sdlc:auto:start troubleshooting -->
| Problem | Solution |
|---|---|
| Frontend API calls fail with CORS errors in dev | Ensure the backend is running on port 8000; default CORS allows localhost:5173. Set ALLOWED_ORIGINS if using a different dev port. |
| Backend pytest cannot import app | Run pytest from the backend/ directory; pytest.ini sets pythonpath=. so the app package is importable. |
| Playwright e2e tests fail because backend is not running | Playwright config auto-starts the backend, but if it is already running on port 8000 set E2E_BASE_URL or let it reuse the existing server outside CI. |
| npm run build succeeds but npm run typecheck fails | Build does not typecheck by design; run npm run typecheck and fix untyped state issues before maintaining the codebase. |
<!-- sdlc:auto:end troubleshooting -->
