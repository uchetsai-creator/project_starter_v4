# Eval Log

<!--
  For: AI / LLM Application
  Purpose: Append-only log of every eval run result.
           One row per run. Agent only needs to read this when comparing prompt versions.
           Criteria and test cases live in eval-spec.md — not here.
  Update when: An eval run completes — append one row, never edit existing rows.
-->

| Date | Prompt ID | Prompt version | Judge model | Tests run | Avg score | Pass? | Notes |
|---|---|---|---|---|---|---|---|
| [YYYY-MM-DD] | [prompt-id] | v1 | claude-opus-4-7 | 3/3 | 3.8 | ✅ | Baseline |
