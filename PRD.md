# PRD: Guarded Text-to-SQL Agent

## 1. Problem
Business users want answers from enterprise databases without writing SQL. LLM-written SQL can be wrong, slow or dangerous, and it can leak rows a user should not see. Real schemas are wide, real questions are often "why" questions needing several queries, and more and more the caller is another AI agent, not a person.

## 2. Goal
Answer English questions over an ERP-style PostgreSQL database (AdventureWorks, 34 curated tables) with high execution accuracy, while guaranteeing: no writes, bounded cost, and per-user row scoping applied by code and by the database, never by the model. Measure when a tool-using agent beats a fixed pipeline. Answer multi-step "why" questions with traceable findings. Expose the guarded engine over MCP. Benchmark on BIRD Mini-Dev (phase 2) and ship a live demo (phase 3).

## 3. Users
| User | Need |
|---|---|
| Sales/operations manager (admin) | Company-wide answers and "why" analyses with charts |
| Salesperson (rep) | Answers limited to their own orders, stores and quotas; no HR pay data |
| Another AI agent (MCP client) | Safe, scoped database access through standard tools |
| Recruiter / interviewer | Live demo, measured results, evidence of safety layering |

## 4. Requirements
| ID | Requirement | Priority |
|---|---|---|
| R1 | Natural-language question → single SELECT → result table + short answer | Must |
| R2 | Read-only access: dedicated Postgres roles with SELECT-only grants on allow-listed tables, `default_transaction_read_only = on` | Must |
| R3 | AST validation with sqlglot (dialect `postgres`): one statement, SELECT/WITH only, schema-qualified table allow-list, function allow-list | Must |
| R4 | Row scoping for reps: AST rewrite to scoped CTEs in code, plus Postgres RLS policies | Must |
| R5 | Row limit, `statement_timeout`, and EXPLAIN cost guard before execution | Must |
| R6 | Schema linking across 5 schemas / 34 tables with FK join paths | Must |
| R7 | Value grounding: retrieve real column values matching the question | Should |
| R8 | Dynamic few-shot from a solved-example store, disjoint from the golden set | Should |
| R9 | Self-correction: on DB error, cost rejection or empty result, retry with the signal (≤ 3) | Must |
| R10 | Golden set ≥ 60 questions with reference SQL; execution-accuracy scorer | Must |
| R11 | Attack suite (writes, DDL, `set_config`/`SET ROLE`, catalogue reads, scoping bypass, prompt injection, MCP-argument abuse) | Must |
| R12 | Ablation over pipeline variants **and** the tool-using agent; report N, CIs, LLM calls, latency, error categories | Must |
| R13 | Gradio UI with SQL view, "acting as" selector, agent trace and analyst tab | Should |
| R14 | Agent can ask a clarifying question when the question is ambiguous (`ask_user` tool) | Should |
| R15 | Tool-using agent: tools search_schema, get_column_values, explain_sql, run_sql, ask_user; bounded steps | Must |
| R16 | Analyst agent: plan → 3–6 guarded queries → findings + charts; every number cites a query | Must |
| R17 | MCP server exposing the guarded engine; scope from server config only | Must |
| R18 | CI eval regression gate on a smoke subset | Should |
| R19 | Phase 2: BIRD Mini-Dev PostgreSQL, official EX / Soft F1 / R-VES, pipeline and agent | Must (phase 2) |
| R20 | Phase 3: hosted live demo with rate limits, read-only DB, free-tier LLM API | Must (phase 3) |

## 5. Success metrics (targets)
| Metric | Target |
|---|---|
| Execution accuracy, best variant, AdventureWorks held-out | ≥ 75% |
| Attack suite: writes or scope bypass executed (all entry points incl. MCP) | 0 |
| Valid SQL rate | ≥ 95% |
| Scope leakage tests (code layer and RLS layer, each tested alone) | 0 leaks |
| Analyst: numbers traceable to a cited query | 100% (enforced; untraceable numbers are removed) |
| Agent vs pipeline | Report honestly, whichever wins |
| Phase 2: BIRD Mini-Dev EX | Report with N; no target before a baseline run |

## 6. Out of scope
Writes, cross-database joins, dialects other than PostgreSQL, real user accounts (the demo uses an "act as" selector), BIRD leaderboard submission, paid services.

## 7. Interview questions this prepares
- Why execution accuracy instead of comparing SQL strings?
- Why is a read-only DB role stronger than prompt rules? Why add RLS on top of the AST rewrite?
- When does a tool-using agent beat a fixed workflow, and what does it cost?
- How do you stop an analyst agent from making up numbers?
- How do you make an MCP tool safe when the caller is another LLM?
- How does schema linking scale from 34 tables to hundreds?
- How does your BIRD number compare with published systems, and why?
- What would change on SAP HANA or SQL Server?
