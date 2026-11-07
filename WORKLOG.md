# Worklog: Guarded Text-to-SQL Agent

## Template
### YYYY-MM-DD HH:MM — Milestone Mx
- Did:
- Tests: passed/total
- Results (run_id):
- Problems and fixes:
- Next:

## Log
### 2026-11-06 — Planning
- Did: planning docs written (Chinook, SQLite).
- Next: M0.

### 2026-11-07 — Re-plan: AdventureWorks on PostgreSQL + BIRD phase 2
- Did: switched dataset from Chinook/SQLite to AdventureWorks 2014 OLTP on PostgreSQL 16 (Docker), curated 34-table allow-list across 5 schemas; scoping now code rewrite + RLS; added phase 2 (BIRD Mini-Dev PostgreSQL). Updated all planning docs and CLAUDE.md.
- Decisions: personal tables (email, phone, password, address, credit card) excluded; rep IDs to be chosen from data in M1.
- Next: M0.

### 2026-11-07 — Re-plan: agentic features, phase 3 demo
- Did: added tool-using agent (measured against the pipeline), analyst agent with query-cited findings, MCP server, EXPLAIN cost guard and CI eval gate to phase 1; added phase 3 live demo (HF Spaces + free-tier hosted Postgres + free-tier LLM API). Single `guarded_execute()` for all entry points. Phase 1 estimate now ~19–20 h.
- Next: M0.

### 2026-11-07 — Repo setup
- Did: initialised git, added .gitignore (data/, index/, runs/, .env excluded), linked to github.com/Udai30/guarded-text-to-sql; created main, dev and test branches from the initial commit. Working branch: test.
- Next: M0.
