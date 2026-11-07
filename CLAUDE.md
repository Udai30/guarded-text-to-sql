# CLAUDE.md: rules for AI coding agents

## Project
Guarded Text-to-SQL Agent over **AdventureWorks on PostgreSQL** (phase 1), with a **BIRD Mini-Dev (PostgreSQL)** benchmark (phase 2) and a hosted **live demo** (phase 3). Phase 1 includes a fixed pipeline, a tool-using agent, an analyst agent and an MCP server. Read the planning docs first.

## Hard rules
- Free tools only for development and evaluation. Only the phase 3 live demo may use a free-tier hosted LLM API and free-tier hosting; keys live in `.env` or host secrets, never in the repo.
- Public sample data only: AdventureWorks 2014 OLTP (Microsoft sample) in phase 1, BIRD Mini-Dev in phase 2. No work code, schemas or data from any employer.
- The agent connects as a read-only Postgres role. Never add a write path, never connect as the owner or superuser at runtime.
- Every path to the database (pipeline, agent tools, analyst, MCP server, UI) goes through the same `guarded_execute()`. No second execution path.
- Scoping is enforced in code (AST rewrite) and in the database (row-level security), never by prompt. No tool or MCP argument may choose the scope; it comes from the session or server config.
- Golden questions must never appear in the few-shot store. In phase 2, BIRD dev/Mini-Dev questions never go into few-shot; few-shot for BIRD comes from BIRD train only.
- Never invent metrics; every number comes from a run ID. Every number in an analyst report must appear in the result of a cited query.
- Do not commit data/, index/, runs/ or .env. Commit only to the `test` branch unless told otherwise.

## Workflow
One milestone per session; tests with every change; run `ruff`, `mypy`, `pytest` before finishing; update WORKLOG.md; stop and ask on conflicts.
