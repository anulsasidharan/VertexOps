"""Create a local development admin user (refuses non-development APP_ENV).

Usage (from repository root, with ``.env`` / env vars set like the API):

    python -m scripts.bootstrap_dev_user
    python -m scripts.bootstrap_dev_user --email you@example.com --password 'your-secret'

Defaults: email ``admin@localhost``, password ``changeme``, workspace name ``Default``.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from backend.core.config import get_settings
from backend.core.db import check_db_connectivity, db_session, dispose_engine
from backend.core.security import hash_password
from backend.models.user import User
from backend.models.workspace import Workspace
from backend.repositories.user_repository import UserRepository
from backend.repositories.workspace_repository import WorkspaceRepository


async def _run(*, email: str, password: str, workspace_name: str) -> int:
    settings = get_settings()
    if not settings.is_development:
        print("Refusing: APP_ENV must be 'development'.", file=sys.stderr)
        return 1

    if not await check_db_connectivity():
        print("Cannot connect to PostgreSQL (DATABASE_URL).", file=sys.stderr)
        print("  1) Start the database, e.g. from the repo root: docker compose up -d postgres", file=sys.stderr)
        print("  2) Match .env to your server: compose Postgres uses", file=sys.stderr)
        print("     postgresql+asyncpg://vertexops:vertexops@localhost:5432/vertexops (host).", file=sys.stderr)
        print("  3) Then: alembic upgrade head", file=sys.stderr)
        return 1

    async with db_session() as session:
        urepo = UserRepository(session)
        existing = await urepo.get_by_email(email)
        if existing is not None:
            print(f"User already exists: {email!r} — nothing to do.")
            return 0

        ws_repo = WorkspaceRepository(session)
        ws = await ws_repo.get_by_name(workspace_name)
        if ws is None:
            ws = Workspace(name=workspace_name)
            await ws_repo.add(ws)

        user = User(
            email=email,
            password_hash=hash_password(password),
            role="admin",
            workspace_id=ws.id,
        )
        await urepo.add(user)

    print(
        f"Created dev user {email!r} (role=admin) in workspace {workspace_name!r}. "
        "Use these credentials on the frontend JWT form."
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap a dev-only admin user (requires APP_ENV=development).",
    )
    parser.add_argument(
        "--email",
        default="admin@localhost",
        help="Login email (default: admin@localhost)",
    )
    parser.add_argument(
        "--password",
        default="changeme",
        help="Login password (default: changeme; change after first login)",
    )
    parser.add_argument(
        "--workspace-name",
        default="Default",
        help="Workspace display name to create or reuse (default: Default)",
    )
    args = parser.parse_args()

    if args.password == "changeme":
        print(
            "Warning: using default password 'changeme'. "
            "Pass --password for something stronger.",
            file=sys.stderr,
        )

    async def _amain() -> int:
        try:
            return await _run(
                email=args.email,
                password=args.password,
                workspace_name=args.workspace_name,
            )
        finally:
            await dispose_engine()

    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
