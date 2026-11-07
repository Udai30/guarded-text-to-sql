# UI/UX Design: Guarded Text-to-SQL Agent (Gradio)

## Tab 1: Ask
- Top bar: **Act as** (Manager, Rep 275, Rep 276, Rep 277; final IDs from M1), **Mode** (Pipeline: variant dropdown / Agent).
- Question box with 6 example chips spanning sales, purchasing, production and HR.
- Result: answer sentence, sortable table, auto chart for 2–20 rows.
- Clarification: when the agent asks, an inline prompt appears above the result; answering continues the run.
- Accordion **SQL**: final SQL with copy button, attempts (error, cost rejection, repaired SQL), scoping badge ("code + RLS").
- Accordion **Agent trace** (agent mode): numbered tool calls with arguments, short result and time.
- Accordion **Why this SQL** (pipeline): linked tables by schema, join path, grounded values, examples used.
- Blocked request: red banner with the reason and the layer that stopped it.

## Tab 2: Analyst
- Question box with 3 example "why" questions; Act-as applies.
- Live plan list (sub-questions tick off as they run).
- Report: findings with clickable citations [Q1]…[Qn] that open the sub-query's SQL and rows; up to 3 charts; "N claims dropped by the number check" note.
- Download report as markdown.

## Tab 3: Evaluation
- Pipeline variants vs agent: accuracy with CIs, LLM calls, latency.
- Error-category bar chart; failure gallery.
- Analyst metrics (automatic + hand-graded, labelled).
- Phase 2: BIRD Mini-Dev EX / Soft F1 / R-VES.

## Tab 4: Safety
- Attack suite by entry point (CLI, agent, MCP): expected vs actual outcome, layer that stopped it.

## Tab 5: About
Architecture diagram, MCP setup snippet for Claude Desktop, schema map, dataset notes, limitations. In the live demo: model used and rate limits.
