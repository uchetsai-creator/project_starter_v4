# AI / LLM Debug Guide

<!--
  Debug reference for AI / LLM Application projects.
  Load when an LLM response is wrong, unexpected, or missing.
  Not needed during normal task work — open only when debugging an active incident.
-->

## When to use this guide

- The LLM returned a wrong or hallucinated answer
- The LLM returned no answer, an error, or a malformed response
- Eval score dropped compared to a previous prompt version
- A tool call was not triggered, timed out, or returned wrong output
- RAG retrieved the wrong chunks (or nothing at all)

---

## Step 1 — Identify the failure type

| Symptom | Likely cause | Go to |
|---|---|---|
| Answer is factually wrong or hallucinated | LLM had no access to correct information | Step 2 (Retriever) or Step 3 (Prompt) |
| Answer ignores the question | System prompt overrides, or context too long | Step 3 (Prompt) |
| No tool was called when it should have been | Tool schema wrong, or prompt did not trigger it | Step 4 (Tool) |
| Tool was called with wrong arguments | LLM misread intent or schema is unclear | Step 4 (Tool) |
| Correct direction, wrong detail | Retriever pulled wrong or outdated chunk | Step 2 (Retriever) |
| Low eval score despite reasonable answer | Rubric mismatch or judge instability | Step 5 (Evaluation) |
| Error / exception (not a wrong answer) | API failure, rate limit, malformed response | Step 6 (API) |

---

## Step 2 — Retriever debug

Run the retrieval step in isolation, without the LLM.

| Question | How to check |
|---|---|
| How many chunks were retrieved? | Log `retrieved_chunks` count — 0 means retriever returned nothing |
| Are relevance scores above threshold? | Below threshold = nothing useful was found |
| Do retrieved chunks contain the correct answer? | Read the chunks manually |

| Finding | Diagnosis |
|---|---|
| 0 chunks retrieved | Query did not match — check embedding model, query rewriting, or threshold |
| Chunks retrieved but answer not in them | Wrong chunks — check similarity metric, top-K, or chunking strategy |
| Correct chunks retrieved but LLM ignored them | Problem is in prompt injection, not retrieval — go to Step 3 |
| Chunks contain the answer but it is outdated | Knowledge source not re-indexed after update |

Check `rag-contract.md` to confirm the correct knowledge source is being queried, and that threshold and top-K are set as intended.

---

## Step 3 — Prompt debug

Check the **rendered** prompt that was actually sent — not the template, but the filled-in version.

1. Log or print the full prompt (system message + user message after variable injection)
2. Does the system prompt include all required context?
3. Are all template variables filled in? (look for unfilled `{{variable}}` placeholders)
4. Is the total length within the context window limit?
5. Try a minimal version of the prompt — does the problem go away?

| Finding | Fix |
|---|---|
| Variable not filled in | Variable name mismatch in rendering code |
| System prompt missing critical instruction | Update the system prompt in `llm-contract.md` and bump version |
| Context too long / truncated | Reduce retrieved chunks, or summarize context before injection |
| Same prompt, different results each run | Non-determinism — lower temperature, or add explicit output format instruction |

Check `llm-contract.md` to confirm the system prompt version in use matches the logged version.

---

## Step 4 — Tool call debug

Check whether the tool was triggered and what happened to its output.

| Question | How to check |
|---|---|
| Was the tool triggered? | Look for `tool_use` block in LLM response |
| Were tool arguments correct? | Compare logged args to expected schema |
| Did the tool return a result, error, or timeout? | Check tool execution log |
| Did the LLM use the tool result? | Check if tool output appears in LLM's final answer |

| Finding | Diagnosis |
|---|---|
| No `tool_use` block in response | LLM decided tool was unnecessary — make tool use explicit in the prompt |
| Wrong tool selected | Multiple tools with overlapping descriptions — clarify each tool's purpose |
| Wrong arguments passed | Tool parameter schema unclear — update `llm-contract.md` tool schema |
| Tool errored | Bug in tool implementation — check tool code, not the LLM |
| Tool timed out | External dependency (API, DB) too slow — add timeout and fallback handling |
| Tool result ignored | Prompt does not instruct LLM to use tool results — update system prompt |

---

## Step 5 — Evaluation debug

If eval scores dropped or a specific test case is failing:

1. Open `eval-log.md` — compare the current run score to previous runs
2. Open `eval-spec.md` — find which criterion dropped
3. Look at the specific failing test case — what did the LLM output vs. what was expected?
4. Run the same case 3× — if judge scores vary by more than 1 point, the judge itself is unstable

| Finding | Action |
|---|---|
| One criterion dropped, others stable | Isolate which prompt change caused it — compare versions in `llm-contract.md` |
| Judge scores inconsistent across runs | Judge temperature too high — check eval-spec.md judge parameters |
| All criteria dropped | Major regression — likely a system prompt change; check version history |
| Score low but human review says answer is correct | Rubric mismatch — refine the criterion in `eval-spec.md` |

---

## Step 6 — API / Infrastructure debug

For errors and exceptions, not wrong answers:

| Error | First action |
|---|---|
| `rate_limit_exceeded` | Check token usage — prompts may be too long; add request throttling |
| `context_length_exceeded` | Prompt + retrieved context exceeds model limit — reduce context injection |
| `timeout` | Provider may be slow — check status page, add retry with exponential backoff |
| `invalid_api_key` | Check env vars — key may have been rotated |
| Malformed / non-JSON response | LLM not following schema — add explicit format instruction to system prompt |
| `tool_use_error` | Tool returned an error — check tool implementation and input validation |

---

## LLM call log format

Every LLM call must produce one structured log entry (follows `logging-spec.md` format).

```
[timestamp] [INFO] [LLM] llm call — end: success
  → {
      "trace_id": "a1b2c3d4-...",
      "prompt_version": "v2.1",
      "model": "claude-sonnet-4-6",
      "input_tokens": 1240,
      "output_tokens": 380,
      "latency_ms": 2100,
      "cost_usd": 0.004,
      "retrieved_chunks": 3,
      "tool_calls": ["search_db"],
      "judge_score": 4.2
    }
```

Omit fields that do not apply (e.g. `retrieved_chunks` when no RAG, `judge_score` when no eval was run).

---

## Quick checklist (copy into task notes)

```
[ ] Failure type identified (wrong answer / no answer / tool / eval / API error)?
[ ] Retriever checked — how many chunks, are they relevant?
[ ] Rendered prompt inspected — variables filled, context present, within limit?
[ ] Tool call traced — was it triggered, correct args, result used by LLM?
[ ] Eval log compared — which criterion and which test case failed?
[ ] LLM call log contains trace_id, tokens, latency, cost?
```
