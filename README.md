# Guarded Text-to-SQL Agent

Ask business questions in plain English over an ERP-style sales, purchasing, production and HR database, and get a correct, safe answer with the SQL shown. Ask "why" questions and an analyst agent plans several queries and writes a short findings report in which every number links to the query that produced it. Every query is validated, cost-checked with EXPLAIN, run through a read-only Postgres role, and scoped so a salesperson sees only their own orders, both in code and through Postgres row-level security. The same guarded engine is exposed as an MCP server.

> Status: planning. Results are placeholders until evaluation runs.
>
> **Live demo:** [link after phase 3] · **Demo GIF:** [after MF]

## Highlights
- **Workflow vs agent, measured:** a fixed LangGraph pipeline against a tool-using agent on the same golden set and on BIRD, comparing accuracy, LLM calls and latency.
- **Analyst agent:** multi-step "why did X change?" questions → plan → 3–6 guarded queries → findings with charts and per-number citations.
- **MCP server:** any MCP client (e.g. Claude Desktop) can query the database through the same guards; scope is fixed by server config.
- **Defence in depth:** sqlglot AST allow-lists, EXPLAIN cost guard, read-only roles, code scoping + RLS, timeouts, number check on generated text.
- **Evaluation discipline:** held-out golden set, ablations with CIs, attack suite, CI regression gate, public benchmark (BIRD Mini-Dev).

## Why this project
A public, inspectable version of the text-to-SQL skills from my work products, written fresh with no work code or data.

## Datasets
**Phase 1: AdventureWorks 2014 OLTP on PostgreSQL.** Microsoft's sample database for a fictional bicycle maker, loaded with the [AdventureWorks-for-Postgres](https://github.com/lorint/AdventureWorks-for-Postgres) port. Five schemas (sales, production, purchasing, humanresources, person); the agent uses a curated subset of 34 tables. The data is realistic but synthetic. Confirm the licence of both the Microsoft release and the port before publishing.

**Phase 2: BIRD Mini-Dev (PostgreSQL).** 500 question/SQL pairs over 11 real-world databases, CC BY-SA 4.0, metrics EX, Soft F1 and R-VES.

## Results: AdventureWorks golden set (fill in from `reports/results.md`)
| Variant | Execution accuracy | Valid SQL | Avg LLM calls | p50 latency | Attacks blocked |
|---|---|---|---|---|---|
| Pipeline: zero-shot | [ ] | [ ] | [ ] | [ ] | [ ] |
| Pipeline: + schema linking | [ ] | [ ] | [ ] | [ ] | [ ] |
| Pipeline: + few-shot + value grounding | [ ] | [ ] | [ ] | [ ] | [ ] |
| Pipeline: + self-correction (≤3) | [ ] | [ ] | [ ] | [ ] | [ ] |
| Tool-using agent | [ ] | [ ] | [ ] | [ ] | [ ] |

## Results: analyst agent (fill in from `reports/analyst.md`)
| Metric | Value |
|---|---|
| Questions | [ ] |
| Numbers traceable to a cited query (automatic) | [ ] |
| Queries valid and executed | [ ] |
| Usefulness, hand-graded 1–5 (by me, rubric in report) | [ ] |

## Results: BIRD Mini-Dev PostgreSQL (fill in from `reports/bird.md`)
| Variant | EX | Soft F1 | R-VES | N |
|---|---|---|---|---|
| Pipeline: zero-shot | [ ] | [ ] | [ ] | [ ] |
| Pipeline: best | [ ] | [ ] | [ ] | [ ] |
| Tool-using agent | [ ] | [ ] | [ ] | [ ] |

## Quick start (after build)
```bash
cp .env.example .env            # then set the passwords
uv sync
ollama pull qwen2.5-coder:7b
docker compose up -d              # Postgres 16 with AdventureWorks loaded
uv run sqlagent db setup          # read-only roles, RLS policies, row counts
uv run sqlagent index build       # schema, values, examples
uv run sqlagent ask "Top 5 territories by sales in 2013" --as-rep 275
uv run sqlagent ask "..." --variant agent
uv run sqlagent analyze "Why did reseller sales in Canada drop in Q3 2013?"
uv run sqlagent eval --variant all
uv run sqlagent mcp serve         # MCP server over stdio
uv run sqlagent ui
```

## Files
README, PRD, TRD, APPFLOW, UI_UX_DESIGN, BACKEND_SCHEMA, IMPLEMENTATION_PLAN, WORKLOG, BUILD_PROMPTS, CLAUDE.md.

## Limitations
AdventureWorks data is synthetic. The golden set is [N] hand-written questions. Analyst usefulness is graded by me. PostgreSQL dialect only. The live demo uses a hosted free-tier model, which differs from the local model used for reported numbers.
