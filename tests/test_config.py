from pathlib import Path

import pytest
from pydantic import ValidationError

from sqlagent.config import DEFAULT_CONFIG_PATH, load_settings

ROOT = Path(__file__).resolve().parents[1]


def test_default_yaml_loads() -> None:
    s = load_settings(ROOT / DEFAULT_CONFIG_PATH, env={})
    assert s.database.name == "adventureworks"
    assert s.database.app_user == "sqlagent_app"
    assert s.guards.row_limit == 1000
    assert s.guards.statement_timeout == "5s"
    assert "humanresources.employeepayhistory" in s.scoping.manager_only_tables
    assert len(s.scoping.rep_scoped_tables) == 5
    assert s.agent.max_tool_calls == 10


def test_env_overrides_db_location() -> None:
    env = {"SQLAGENT_DB_HOST": "db.local", "SQLAGENT_DB_PORT": "6543"}
    s = load_settings(ROOT / DEFAULT_CONFIG_PATH, env=env)
    assert s.database.host == "db.local"
    assert s.database.port == 6543


def test_missing_file_gives_defaults(tmp_path: Path) -> None:
    s = load_settings(tmp_path / "nope.yaml", env={})
    assert s.database.port == 5432


def test_unknown_key_rejected(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("guards:\n  row_limit: 10\n  allow_writes: true\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_settings(p, env={})


def test_yaml_holds_no_secrets() -> None:
    text = (ROOT / DEFAULT_CONFIG_PATH).read_text(encoding="utf-8").lower()
    for word in ("password:", "api_key", "secret:"):
        assert word not in text
