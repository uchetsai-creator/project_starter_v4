# Pipeline Debug Guide

<!--
  Debug reference for Data Pipeline and ML Pipeline projects.
  Load this file when a pipeline stage fails or data quality is suspect.
  Not needed during normal task work — open only when debugging an active incident.
-->

## When to use this guide

- A pipeline stage fails (non-zero exit / orchestrator task marked failed)
- Data quality checks report unexpected failures
- Output data has wrong row count, wrong values, or wrong schema
- Pipeline ran successfully but downstream results look wrong

---

## Step 1 — Identify the failing stage

Open the orchestrator (Airflow / Prefect / etc.) and find the **first** failed task.

✅ Stages before the failed task — skip, their output is likely fine  
❌ The first failed stage — this is your starting point  
⏭ Stages after — they did not run (or ran on stale data)

Write it down:
```
Failed stage: _______________
```

---

## Step 2 — Check input data

Before reading the stage's code, check what it received.

| Question | How to check |
|---|---|
| Is the input file / table present? | `ls`, `SELECT COUNT(*) FROM ...` |
| Row count as expected? | Compare to source or previous run |
| Schema matches contract? | Check column names and types against `pipeline-contract.md` |
| Sample a few rows — any obvious bad values? | `SELECT * LIMIT 10` / `head -n 10 file.csv` |

If input is already bad → the bug is **upstream**. Go back to Step 1 with the upstream stage.

---

## Step 3 — Read the stage log

Look at the log for the failing stage only.

What to look for:
1. The **first** `ERROR` or `WARN` line — this is usually the root cause
2. Row count going in vs. row count coming out (look for "processed N rows", "rejected M rows")
3. Schema mismatch messages
4. External call failures (DB timeout, API error, file not found)

**The log format follows `logging-spec.md`:**
```
[timestamp] [ERROR] [STAGE_NAME] <operation> — failed: <reason>
  → {"trace_id": "...", key: value}
```

---

## Step 4 — Check data quality report

If the project uses a validation tool (Great Expectations, dbt tests, custom checks):

1. Open the validation report for this run
2. Find which expectation / test failed
3. Look at the failure details — sample failing rows are often included

| Failure type | Most likely cause |
|---|---|
| `not_null` | Source has NULLs that upstream did not filter |
| `value_in_set` / `accepted_values` | New category appeared in source data |
| `min_value` / `max_value` | Outlier or data entry error in source |
| `unique` | Duplicate rows — JOIN or UNION logic error |
| `row_count` | Upstream filtered too many rows, or source was truncated |
| `type` / `schema` | Source schema changed — column added, removed, or renamed |

---

## Step 5 — Trace lineage to find where data went bad

If Step 2 showed the failing stage's **input** was already wrong:

1. Open the lineage graph (DataHub / dbt lineage / your tool)
2. Find the current table / file in the graph
3. Walk upstream one hop at a time — check row count and sample at each hop
4. The first hop where bad data appears = the root cause stage

```
Source File
    ↓  ← clean?
Extract Stage    ← check here first
    ↓  ← clean?
Transform Stage  ← check here second
    ↓  ← bad!
Load Stage       ← symptom, not root cause
```

---

## Common failure patterns

| Symptom | First place to look |
|---|---|
| Row count drops unexpectedly | JOIN condition (inner join eliminating unmatched rows) |
| Row count increases unexpectedly | Duplicate key in JOIN, or missing DISTINCT |
| Type error / cast failure | Source schema changed, or new non-numeric value in numeric column |
| NULL constraint violation | New NULLs in source, or mapping skipped a required field |
| Stage timeout | Data volume spike, missing index, or slow external dependency |
| All rows fail quality check | Wrong file ingested (filename, date partition, or path mismatch) |
| Pipeline succeeds but dashboard wrong | Bug is in mart / aggregation layer — run the query manually |

---

## Quick checklist (copy into task notes)

```
[ ] Which stage failed? _______________
[ ] Input data present and correct row count?
[ ] First ERROR in stage log identified?
[ ] Data quality report checked — which expectation failed?
[ ] Root cause stage found via lineage?
[ ] Fix applied and failing stage re-run successfully?
[ ] Downstream stages re-run and output verified?
```
