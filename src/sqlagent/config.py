"""Configuration: YAML defaults plus environment overrides.

Secrets (passwords, API keys) are read only from the environment / `.env`, never from YAML.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONFIG_PATH = Path("configs/default.yaml")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DatabaseConfig(_Strict):
    name: str = "adventureworks"
    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    app_user: str = "sqlagent_app"
    owner_user: str = "sqlagent_owner"


class GuardsConfig(_Strict):
    row_limit: int = Field(default=1000, gt=0)
    statement_timeout: str = "5s"
    max_estimated_cost: float = Field(default=1_000_000, gt=0)
    max_estimated_rows: float = Field(default=1_000_000, gt=0)


class ScopingConfig(_Strict):
    rep_scoped_tables: list[str] = Field(default_factory=list)
    manager_only_tables: list[str] = Field(default_factory=list)


class LLMConfig(_Strict):
    provider: str = "ollama"
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder:7b"
    fallback_model: str = "qwen2.5-coder:3b"
    embedding_model: str = "nomic-embed-text"
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class AgentConfig(_Strict):
    max_tool_calls: int = Field(default=10, gt=0)
    max_failed_runs: int = Field(default=3, ge=0)
    max_seconds: int = Field(default=60, gt=0)
    max_repairs: int = Field(default=3, ge=0)


class PathsConfig(_Strict):
    data_dir: Path = Path("data")
    index_dir: Path = Path("index")
    runs_dir: Path = Path("runs")
    knowledge_dir: Path = Path("knowledge")
    eval_dir: Path = Path("eval")
    reports_dir: Path = Path("reports")


class Settings(_Strict):
    database: DatabaseConfig = DatabaseConfig()
    guards: GuardsConfig = GuardsConfig()
    scoping: ScopingConfig = ScopingConfig()
    llm: LLMConfig = LLMConfig()
    agent: AgentConfig = AgentConfig()
    paths: PathsConfig = PathsConfig()


def _env_overrides(env: dict[str, str]) -> dict[str, Any]:
    db: dict[str, Any] = {}
    if host := env.get("SQLAGENT_DB_HOST"):
        db["host"] = host
    if port := env.get("SQLAGENT_DB_PORT") or env.get("PGPORT"):
        db["port"] = int(port)
    if name := env.get("POSTGRES_DB"):
        db["name"] = name
    if owner := env.get("POSTGRES_USER"):
        db["owner_user"] = owner
    return {"database": db} if db else {}


def _merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_settings(path: Path | None = None, env: dict[str, str] | None = None) -> Settings:
    """Load settings from YAML (default `configs/default.yaml`) and apply env overrides."""
    if env is None:
        load_dotenv(override=False)
        env = dict(os.environ)
    if path is None:
        path = Path(env.get("SQLAGENT_CONFIG", str(DEFAULT_CONFIG_PATH)))
    raw: dict[str, Any] = {}
    if path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if loaded is not None:
            if not isinstance(loaded, dict):
                raise ValueError(f"{path}: top level must be a mapping")
            raw = loaded
    return Settings.model_validate(_merge(raw, _env_overrides(env)))
