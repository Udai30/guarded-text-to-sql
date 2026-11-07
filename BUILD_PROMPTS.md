# Build Prompts: Guarded Text-to-SQL Agent

## Common header
> You are working in `guarded-text-to-sql-agent`. Read CLAUDE.md, PRD.md, TRD.md, BACKEND_SCHEMA.md and IMPLEMENTATION_PLAN.md. Implement only the milestone below, with tests. Never invent results. Free tools only (phase 3 exceptions in CLAUDE.md). Ask if the docs conflict.

## M0: Setup
uv Python 3.12 package `sqlagent`, Typer CLI (db, index, ask, analyze, eval, bird, mcp, ui stubs), `configs/default.yaml`, `.env.example`, `docker-compose.yml` with Postgres 16, ruff/mypy/pytest, `.gitignore` (data/, index/, runs/, .env), GitHub Actions CI with a Postgres service container.
**Verify:** `uv run sqlagent --help`; `pg_isready`; CI green.

## M1: DB and safety core
Load AdventureWorks 2014 OLTP with the AdventureWorks-for-Postgres port (its docker-compose or install.sql; port `update_csvs.rb` to Python if Ruby is a problem on Windows). Record sources and checksums. `sqlagent db setup` creates roles per BACKEND_SCHEMA.md, grants SELECT on the 34 tables, sets read-only defaults, writes `data/manifest.json` with real row counts. Implement `guarded_execute(sql, scope)`: sqlglot validation per TRD §3, EXPLAIN (FORMAT JSON) cost guard, row limit, `statement_timeout`. This is the only function that touches the database at runtime.
**Verify:** INSERT/UPDATE/DELETE/MERGE/DROP/COPY/SET/SET ROLE/set_config/pg_catalog/information_schema/multi-statement blocked; 10 valid SELECTs pass; a cross join on order lines is rejected by EXPLAIN; a slow query times out; the app role cannot write with the validator bypassed.

## M2: Scoping
sqlglot rewrite to scoped CTEs (salesorderheader, salesorderdetail, store, customer, salespersonquotahistory); refuse `employeepayhistory` for reps; RLS policies for `sqlagent_rep`. Pick three rep IDs from data.
**Verify:** leak tests for three reps, run with code only, RLS only, both.

## M3: Knowledge and retrieval
`columns.yaml`, `joins.yaml` (from real FKs), `glossary.yaml`. Chroma collections for columns, distinct values (exclude personal fields), examples. Implement `link_schema` (retrieve + FK bridge tables), `ground_values`, `pick_examples`, reusable as agent tools.
**Verify:** linker table recall ≥ 85% on golden; print it.

## M4: Golden, analyst set, attacks
≥ 60 golden (all 5 schemas, ≥ 12 `as_rep`, ≥ 5 multi-schema, ≥ 2 recursive BOM); `eval/smoke.txt` with 20 IDs; 10–15 analyst questions with expected drivers written after exploring the data; ≥ 30 attacks tagged by entry point (cli, agent, mcp). Run every reference query.
**Verify:** all reference SQL executes; disjointness test passes.

## M5: Pipeline agent
LangGraph graph per APPFLOW with variants zero_shot, linked, grounded, self_correct; repair ≤ 3 on DB error, cost rejection or empty result; template answer + optional LLM sentence with number check.
**Verify:** 10 golden end-to-end with traces.

## M6: Evaluation and gate
Execution-accuracy scorer per TRD §6.1; all variants; bootstrap CIs; error categories; attack results with stopping layer; `reports/results.md`. `sqlagent eval --gate` on the smoke subset against `reports/baseline.json`; nightly/manual GitHub workflow with Ollama 3B.
**Verify:** report reproducible from saved predictions; gate fails on a deliberately broken prompt.

## M7: Tool-using agent
LangGraph tool-calling agent with search_schema, get_column_values, explain_sql, run_sql, ask_user (interrupt; auto-answered in eval and counted). Budget ≤ 10 tool calls, ≤ 3 failed runs, 60 s. Scope bound to session. Add as variant `agent` in eval with a paired comparison against the best pipeline variant. Check the local model's tool-calling support first.
**Verify:** agent row in `reports/results.md`; agent attack cases pass.

## M8: Analyst agent
Planner → 3–6 sub-questions → each via the best variant and `guarded_execute()` → writer with `[Qn]` citations → number check drops untraceable claims → up to 3 Plotly charts → markdown report + JSON trace. `sqlagent analyze` and `sqlagent eval --analyst` (automatic metrics; hand-grade usefulness with the rubric and store grades in `eval/analyst_grades.jsonl`).
**Verify:** 100% of numbers in reports traceable; `reports/analyst.md` written.

## M9: MCP server
FastMCP stdio server `sqlagent mcp serve [--as-rep ID]` with ask, run_sql, list_tables, describe_table (analyze optional). Scope from config only. Tests with the MCP Python client including attack cases. Add a Claude Desktop config snippet to README.
**Verify:** MCP tests pass; manual run in Claude Desktop recorded as a screenshot.

## M10: UI
Gradio per UI_UX_DESIGN.md.
**Verify:** Act-as switch changes scoped answers; agent trace and analyst tab work.

## MF: Ship phase 1
README results from run IDs, demo GIF, architecture diagram, resume bullets.

## B1–B4: Phase 2, BIRD Mini-Dev
Per IMPLEMENTATION_PLAN.md §Phase 2. PostgreSQL release, official scripts, few-shot from BIRD train only, best pipeline and agent, with and without evidence, cite every published baseline.

## D1–D3: Phase 3, live demo
Per IMPLEMENTATION_PLAN.md §Phase 3 and TRD §7. Re-run leak and attack tests against the hosted DB before making the link public. Never commit keys.
