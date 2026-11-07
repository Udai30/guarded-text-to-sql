# TRD: Guarded Text-to-SQL Agent

## 1. Architecture
```
            UI (Gradio) · CLI (Typer) · MCP server (stdio)
                              │
        ┌─────────────────────┼──────────────────────┐
   Pipeline (LangGraph)   Tool-using agent      Analyst agent
   link → ground →        LLM picks tools:      plan → sub-questions
   examples → generate    search_schema         → each via pipeline/agent
   → validate → scope     get_column_values     → findings + charts
   → execute → repair≤3   explain_sql, run_sql  → citation + number check
   → answer               ask_user (≤ 10 steps)
        └─────────────────────┼──────────────────────┘
                      guarded_execute()
   validate (sqlglot) → scope rewrite → EXPLAIN cost guard
   → read-only role + RLS → statement_timeout → row limit
```

## 2. Stack
| Layer | Choice |
|---|---|
| Language | Python 3.12, uv |
| Agents | LangGraph (pipeline graph, tool-calling agent, analyst graph; `interrupt` for ask_user) |
| LLM (dev/eval) | Ollama `qwen2.5-coder:7b` (fallback 3B), with tool calling; confirm tool-call support at build time, else use `qwen2.5:7b-instruct` for the agent |
| LLM (live demo only) | One free-tier hosted LLM API, chosen in phase 3 |
| Embeddings | Ollama `nomic-embed-text` |
| Vector store | Chroma (local) |
| SQL parsing | sqlglot (dialect `postgres`) |
| DB | PostgreSQL 16 in Docker, AdventureWorks 2014 OLTP via AdventureWorks-for-Postgres |
| Driver | psycopg 3 with a small pool |
| MCP | Official Python MCP SDK (FastMCP), stdio transport |
| Charts | Plotly (UI and analyst report) |
| UI | Gradio; CLI with Typer |
| Tests/CI | pytest, ruff, mypy, GitHub Actions (Postgres service container) |
Check current versions at build time.

## 3. Safety layers (defence in depth), all inside `guarded_execute()`
1. **Roles:** `sqlagent_manager` and `sqlagent_rep`, both NOLOGIN, SELECT on allow-listed tables only, `default_transaction_read_only = on`, no CREATE anywhere. The app logs in as `sqlagent_app` (NOINHERIT) and runs `SET LOCAL ROLE` per request inside a read-only transaction. The owner role is used only by `db setup`.
2. **AST validation:** exactly one statement; root is Select/Union/With; no Insert/Update/Delete/Merge/Drop/Create/Alter/Copy/Set/Call/Do; tables ⊆ schema-qualified allow-list; functions ⊆ allow-list; deny `set_config`, `current_setting`, `pg_*`, `dblink*`, `lo_*`, `pg_catalog`, `information_schema`.
3. **Scoping in code:** sqlglot rewrites scoped tables to CTEs (salesorderheader by `salespersonid`, salesorderdetail via scoped headers, store by `salespersonid`, customer via scoped stores, salespersonquotahistory by `businessentityid`). `humanresources.employeepayhistory` is refused for reps.
4. **Scoping in the database (RLS):** policies for `sqlagent_rep` on the same tables keyed on `current_setting('sqlagent.rep_id')::int`, set by the app with `SET LOCAL`. Each layer is tested alone.
5. **EXPLAIN cost guard:** `EXPLAIN (FORMAT JSON)` on the final scoped SQL; reject if estimated total cost or estimated rows exceed config thresholds. The rejection reason goes to repair, or back to the agent as a tool result.
6. **Limits:** `SELECT * FROM (...) AS q LIMIT 1000`; `SET LOCAL statement_timeout = '5s'`.
7. **Prompt hygiene:** question JSON-encoded; schema, values and tool results in delimited blocks; tool results treated as data.
8. **Answer check:** every number in LLM-written text must appear in a cited result; otherwise the sentence is dropped and replaced by the template answer.

## 4. Agents
### 4.1 Pipeline (baseline)
Fixed graph per APPFLOW; variants zero_shot, linked, grounded, self_correct.

### 4.2 Tool-using agent (variant `agent`)
- Tools: `search_schema(query)` → columns + join paths; `get_column_values(table, column, query)` → matching distinct values (non-personal columns only); `explain_sql(sql)` → validation result + cost estimate, no execution; `run_sql(sql)` → rows via `guarded_execute()`; `ask_user(question)` → LangGraph interrupt (in eval: auto-answered "use your best judgement" and counted).
- Budget: ≤ 10 tool calls, ≤ 3 failed `run_sql`, ≤ 60 s wall time; then return the best result so far or a clear failure.
- Scope is bound to the session, not a tool argument.

### 4.3 Analyst agent (`sqlagent analyze`)
- Planner: question → 3–6 sub-questions with intent (compare periods, break down by dimension, check drivers). Each sub-question runs through the best variant (pipeline or agent, chosen from M6/M7 results).
- Writer: findings in short bullets plus up to 3 charts. Each number carries a citation `[Q2]` to a sub-query; the number check removes any number not found in the cited result.
- Output: markdown report + JSON trace (sub-questions, SQL, rows, citations).

### 4.4 MCP server
- Tools: `ask(question)`, `run_sql(sql)`, `list_tables()`, `describe_table(table)`, `analyze(question)` (optional flag).
- Scope and role come from server config (`--as-rep 275` or manager), never from tool arguments. All calls go through `guarded_execute()`.
- Tested with the MCP Python client and by hand in Claude Desktop.

## 5. Decisions
| # | Decision | Alternative | Reason |
|---|---|---|---|
| D1 | sqlglot AST over regex | Regex deny-list | Regex is easy to bypass; AST knows statement types |
| D2 | Scoping by query rewrite in code **and** RLS | Tell the LLM to filter | Model instructions are not a security boundary |
| D3 | Pipeline baseline + agent as a measured variant | Agent only | Shows when agency pays off and what it costs |
| D4 | Golden set disjoint from few-shot store, enforced by test | Shared | Prevents flattering scores |
| D5 | AdventureWorks subset of 34 tables | All ~68 tables / Chinook | Needs real schema linking; drops personal data |
| D6 | Postgres in Docker | Native install on Windows | Same setup on laptop and CI |
| D7 | BIRD Mini-Dev PostgreSQL for phase 2 | Full BIRD dev (SQLite) / Spider 2.0 | Native Postgres, official scripts |
| D8 | One `guarded_execute()` for every entry point | Per-feature checks | One place to test; MCP and agent can't bypass guards |
| D9 | EXPLAIN before execute | Timeout only | Rejects runaway queries cheaply and gives the repair loop a useful signal |
| D10 | Analyst numbers must cite a query result | Free-form LLM summary | No made-up numbers |

## 6. Evaluation
### 6.1 AdventureWorks golden set
- 60–80 questions tagged simple, join, multi-schema join, aggregate, time, nested, recursive, with `as_rep` cases.
- Execution accuracy: compare normalised results of reference and predicted SQL (same scope): sorted rows unless order matters; numerics rounded to 2 dp; ignore column names.
- Error categories: wrong table/column, wrong join path, wrong filter value, wrong aggregation, wrong time logic, scope error, invalid SQL, cost-rejected, timeout, agent step budget exceeded.
- Per variant (4 pipeline + agent): N, bootstrap CIs, LLM calls, tool calls, p50/p95 latency. Paired comparison between best pipeline and agent on the same questions.

### 6.2 Analyst set
- 10–15 "why/what changed" questions written by hand with notes on the expected drivers.
- Automatic: % numbers traceable, % sub-queries valid, sub-queries per question, latency.
- Hand-graded usefulness 1–5 against a written rubric (found the main driver? misleading claims?). Labelled as hand-graded in every report.

### 6.3 Attacks
Attacks run through CLI, agent tools and MCP. Report which layer stopped each one.

### 6.4 CI regression gate
`sqlagent eval --gate` runs a 20-question smoke subset and fails if EX drops more than 5 points below `reports/baseline.json` or any attack succeeds. Runs in a manual/nightly GitHub workflow with Ollama `qwen2.5-coder:3b`; unit and safety tests run on every push.

### 6.5 Phase 2: BIRD Mini-Dev (PostgreSQL)
- 500 pairs over 11 databases in Postgres database `bird`; evidence used, reported with and without it.
- Scoping off; validation, read-only role, EXPLAIN guard and timeouts on.
- Official Mini-Dev scripts (EX, Soft F1, R-VES) for best pipeline and agent. Few-shot only from BIRD train.

## 7. Phase 3: live demo
- Hugging Face Spaces (Gradio) + free-tier hosted Postgres (Neon or Supabase) loaded with the same 34 tables, roles and RLS.
- One free-tier LLM API; key in Space secrets. Check terms and limits at build time.
- Per-session rate limit (e.g. 20 questions/hour), analyst capped at 3 runs/hour, MCP not exposed publicly.
- Banner: model used, data is a public sample, numbers in README come from local runs.
