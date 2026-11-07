# Backend Schema: Guarded Text-to-SQL Agent

## Database
PostgreSQL 16 (Docker), database `adventureworks`, loaded from the AdventureWorks 2014 OLTP CSVs with the AdventureWorks-for-Postgres port. The agent sees **34 allow-listed tables** in 5 schemas. `db setup` records actual row counts per table in `data/manifest.json`; documents quote those numbers, never guesses.

| Schema | Allow-listed tables |
|---|---|
| sales (11) | salesorderheader, salesorderdetail, customer, salesperson, salesterritory, store, specialoffer, specialofferproduct, salesreason, salesorderheadersalesreason, salespersonquotahistory |
| production (10) | product, productcategory, productsubcategory, productmodel, productinventory, location, workorder, scrapreason, billofmaterials, productlistpricehistory |
| purchasing (5) | purchaseorderheader, purchaseorderdetail, vendor, productvendor, shipmethod |
| humanresources (5) | employee, department, employeedepartmenthistory, shift, employeepayhistory (manager only) |
| person (3) | person, stateprovince, countryregion |

Excluded on purpose: person.emailaddress, person.personphone, person.password, person.address, sales.creditcard, sales.personcreditcard, sales.shoppingcartitem.

## Knowledge files
| File | Content |
|---|---|
| knowledge/columns.yaml | One entry per allow-listed column: schema, table, column, type, description, sample values (non-personal) |
| knowledge/joins.yaml | Foreign-key graph for join paths |
| knowledge/glossary.yaml | Business terms → columns (e.g. "revenue" → `salesorderdetail.linetotal`; "online order" → `onlineorderflag`) |
| knowledge/examples.jsonl | 30–50 solved `{question, sql, tags}` pairs for few-shot (disjoint from golden) |
| eval/golden.jsonl | `{id, question, sql, as_rep, tags, order_matters}` |
| eval/smoke.txt | 20 golden IDs for the CI gate |
| eval/analyst.jsonl | `{id, question, as_rep, expected_drivers, notes}` |
| eval/attacks.jsonl | `{id, entry: cli|agent|mcp, question_or_sql, as_rep, expected: BLOCK|SCOPED|ANSWER}` |
| eval/bird/ | Phase 2 Mini-Dev data (not committed if licence terms require) |
| reports/baseline.json | Smoke-subset scores the CI gate compares against |
| index/ | Chroma collections: columns, values, examples |

## Pydantic models
```python
Variant = Literal["zero_shot","linked","grounded","self_correct","agent"]

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    as_rep: int | None = None          # salesperson businessentityid, e.g. 275
    variant: Variant = "self_correct"
    database: Literal["adventureworks","bird"] = "adventureworks"
    evidence: str | None = None        # BIRD external knowledge (phase 2)

class Attempt(BaseModel):
    sql: str; ok: bool; error: str | None; rows: int | None
    est_cost: float | None; rejected_by: str | None   # validator|cost|timeout|db

class ToolCall(BaseModel):
    tool: str; args: dict[str, Any]; ok: bool; summary: str; ms: int

class AskResponse(BaseModel):
    answer: str; columns: list[str]; rows: list[list[Any]]
    sql: str | None; attempts: list[Attempt]; tool_calls: list[ToolCall]
    scoped_to: int | None; blocked: bool; block_reason: str | None
    clarification: str | None
    linked_columns: list[str]; grounded_values: list[str]; example_ids: list[str]
    latency_ms: int; llm_calls: int; run_id: str

class SubQuery(BaseModel):
    id: str; sub_question: str; sql: str | None
    columns: list[str]; rows: list[list[Any]]; ok: bool

class Finding(BaseModel):
    text: str; citations: list[str]     # SubQuery ids; numbers in text must appear in them

class AnalystReport(BaseModel):
    question: str; scoped_to: int | None; plan: list[str]
    subqueries: list[SubQuery]; findings: list[Finding]
    charts: list[dict[str, Any]]; dropped_claims: int
    latency_ms: int; llm_calls: int; run_id: str
```

## Agent state
- Pipeline: `question, as_rep, database, evidence, linked, join_path, values, examples, sql, attempts[], result, blocked, llm_calls, budget`.
- Tool agent: `messages[], tool_calls[], failed_runs, steps, best_result, pending_clarification`.
- Analyst: `question, plan[], subqueries[], findings[], charts[]`.

## Roles and scoping
- `sqlagent_owner`: loads data, creates roles and policies. Never used at runtime.
- `sqlagent_app` (LOGIN): `SET LOCAL ROLE` to one of the two below per request.
- `sqlagent_manager`: SELECT on all 34 tables.
- `sqlagent_rep`: SELECT on all except `humanresources.employeepayhistory`; RLS on salesorderheader, salesorderdetail, store, customer, salespersonquotahistory keyed on `sqlagent.rep_id`.
- Act-as reps: three salesperson IDs with many orders (e.g. 275, 276, 277; confirm in M1).
- Online orders have no salesperson, so reps see only reseller orders; needs a golden case.

## Allow-lists
- Tables: the 34 above, schema-qualified.
- Functions: COUNT, SUM, AVG, MIN, MAX, ROUND, DATE_TRUNC, EXTRACT, DATE_PART, TO_CHAR, COALESCE, NULLIF, LOWER, UPPER, LENGTH, SUBSTRING, CAST, RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD.
- Denied: set_config, current_setting, pg_*, dblink*, lo_*, pg_catalog, information_schema.

## Config
`model, agent_model, temperature 0, max_repairs 3, agent_max_steps 10, agent_max_failed_runs 3, analyst_max_subqueries 6, row_limit 1000, statement_timeout 5s, explain_max_cost, explain_max_rows, top_k_columns 25, top_k_values 8, top_k_examples 4, gate_max_drop 5, dsn from .env`.

## Run artefacts
`runs/<run_id>/predictions.jsonl, traces.jsonl, summary.json`; `reports/results.md`, `reports/analyst.md`, `reports/bird.md`, `reports/baseline.json`.
