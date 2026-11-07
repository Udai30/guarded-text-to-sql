# Implementation Plan: Guarded Text-to-SQL Agent

## Phase 1: AdventureWorks on PostgreSQL
Target: about 19–20 hours.

| # | Milestone | Deliverables | Acceptance check | Est. |
|---|---|---|---|---|
| M0 | Setup | uv project, Typer CLI, configs, docker-compose (Postgres 16), CI with Postgres service | CI green; DB reachable | 0.5 h |
| M1 | DB + safety core | Load AdventureWorks, `db setup` (roles, grants, read-only, manifest), sqlglot validator, EXPLAIN cost guard, limits, timeout, single `guarded_execute()` | Writes/DDL/SET/set_config/catalogue reads blocked; valid SELECTs pass; cross join rejected by EXPLAIN; slow query times out; app role cannot write with validator off | 1.8 h |
| M2 | Scoping | AST rewrite + RLS; refusal for restricted tables | Leak tests for 3 reps with code only, RLS only, both | 1 h |
| M3 | Knowledge + retrieval | columns.yaml, joins.yaml, glossary.yaml, values index, examples store | Linker table recall ≥ 85% on golden | 1.5 h |
| M4 | Golden, analyst set, attacks | ≥ 60 golden, 10–15 analyst questions, ≥ 30 attacks across CLI/agent/MCP, smoke subset | All reference SQL executes; disjointness test passes | 1.7 h |
| M5 | Pipeline agent | LangGraph pipeline, 4 variants, repair loop, answer + number check | 10 golden end-to-end with traces | 1 h |
| M6 | Eval + gate | Scorer, ablation, CIs, error categories, `--gate`, baseline.json, nightly workflow | `reports/results.md` with N; gate fails on a seeded regression | 1 h |
| M7 | Tool-using agent | 5 tools, LangGraph tool-calling agent, step budget, interrupt for ask_user, eval as variant `agent` | Agent row in results with paired comparison vs best pipeline | 3.5 h |
| M8 | Analyst agent | Planner, sub-query runner, writer with citations, number check, charts, report + trace | Analyst eval: 100% traceable numbers; `reports/analyst.md` | 4.5 h |
| M9 | MCP server | FastMCP server, 4–5 tools, scope from config, MCP attack tests | MCP client tests pass; works in Claude Desktop (screenshot) | 2 h |
| M10 | UI | Gradio tabs per UI_UX_DESIGN.md | Act-as switch changes results; agent trace and analyst tab work | 1.2 h |
| MF | Ship phase 1 | README results, demo GIF, architecture diagram, resume bullets | Every number traces to a run ID | 0.5 h |

### Cut list (in order)
1. Analyst charts (keep tables). 2. Merge "grounded" into self_correct. 3. glossary.yaml. 4. MCP `analyze` tool. 5. Clarification UI (keep the tool, auto-answer).

## Phase 2: BIRD Mini-Dev (PostgreSQL)
Target: about 6–8 hours. Start after phase 1 ships.

| # | Milestone | Deliverables | Acceptance check | Est. |
|---|---|---|---|---|
| B1 | Load BIRD | Mini-Dev PostgreSQL into database `bird`, read-only role, source + checksum | 11 databases queryable as read-only role | 1 h |
| B2 | Adapter | Schema docs from BIRD descriptions; evidence in prompts; few-shot from BIRD train only | No Mini-Dev question in few-shot (test) | 1.5 h |
| B3 | Run + score | Best pipeline and agent, with and without evidence; official scripts | Reproducible from saved predictions | 2.5 h |
| B4 | Report | `reports/bird.md`: N, scores, CIs, errors, cited published baselines | README table filled from run IDs | 1 h |

## Phase 3: Live demo (just before applying)
Target: about 2–3 hours.

| # | Milestone | Deliverables | Acceptance check | Est. |
|---|---|---|---|---|
| D1 | Hosted DB | Free-tier Postgres (Neon or Supabase) with the 34 tables, roles and RLS | Leak and attack tests pass against the hosted DB | 1 h |
| D2 | Hosted app | Hugging Face Space (Gradio), free-tier LLM API via secrets, rate limits, demo banner | Public link works; attacks blocked; limits enforced | 1.5 h |
| D3 | Polish | README link, GIF, short Loom/YouTube walkthrough | Link in README and resume | 0.5 h |

## Resume bullet templates
- "Built a guarded text-to-SQL system (LangGraph, sqlglot, PostgreSQL) over a 34-table ERP-style database with read-only roles, code + row-level-security scoping and an EXPLAIN cost guard; [B]% execution accuracy on [N] held-out questions (zero-shot [A]%), [C]% EX on BIRD Mini-Dev, 0 scope leaks across [Y] attacks."
- "Compared a fixed pipeline with a tool-using agent: agent [+/−D] points accuracy at [E]× LLM calls; built an analyst agent answering multi-step 'why' questions with 100% query-cited numbers, and exposed the guarded engine as an MCP server."
