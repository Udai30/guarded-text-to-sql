"""M0 infra check: Postgres 16 is reachable. Test-only connection as the container owner;
runtime code never connects as the owner (CLAUDE.md)."""

import os

import psycopg
import pytest

from sqlagent.config import load_settings


@pytest.mark.db
def test_postgres16_reachable() -> None:
    s = load_settings()
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        pytest.skip("POSTGRES_PASSWORD not set")
    try:
        conn = psycopg.connect(
            host=s.database.host,
            port=s.database.port,
            dbname=s.database.name,
            user=s.database.owner_user,
            password=password,
            connect_timeout=3,
        )
    except psycopg.OperationalError as exc:
        if os.environ.get("CI"):
            raise
        pytest.skip(f"Postgres not reachable: {exc}")
    with conn:
        version = conn.execute("SHOW server_version_num").fetchone()
    assert version is not None
    assert int(version[0]) // 10000 == 16
