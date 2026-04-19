# VertexOps dashboard (Vite + React)

## Run the UI

From this directory:

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dev server proxies `/api` to `http://localhost:8000`.

## Database and Python tools (run from repo root)

**Alembic** and **`python -m scripts.…`** must run from the **repository root** (the folder that contains `alembic.ini`, `backend/`, and `scripts/`), not from `frontend/`.

```bash
cd ..                    # Windows PowerShell: parent of frontend
uv run alembic upgrade head
uv run python -m scripts.bootstrap_dev_user --email you@example.com --password "your-secret"
```

Requires **[uv](https://docs.astral.sh/uv/)** and a synced venv at the repo root (`uv sync --all-groups` once). Or stay in `frontend/` and use the npm shortcuts (they call `uv run` in the parent directory):

```bash
npm run db:migrate
npm run db:bootstrap-user -- --email you@example.com --password "your-secret"
```

Ensure `.env` in the **repo root** has `DATABASE_URL`, `JWT_SECRET_KEY`, and `API_KEY_PEPPER` (see root `.env.example`).

If `alembic` or bootstrap fails with **connection refused**, start PostgreSQL first (e.g. `docker compose up -d postgres` from the repo root) and align `DATABASE_URL` with that server (for Compose: `vertexops:vertexops@localhost:5432/vertexops`).
