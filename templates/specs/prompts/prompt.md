# [Prompt ID] Prompt

<!--
  For: AI / LLM Application
  One file per prompt. Stored under docs/specs/prompts/[prompt-id]-prompt.md
  After creating or updating this file, verify the row exists in prompt-library.md.
-->

**Prompt ID:** [prompt-id]
**Purpose:** [One line — what this prompt makes the model do]
**Used by:** [which module or feature invokes this prompt]
**Current version:** v[N]

---

## Input Variables

| Variable | Type | Description |
|---|---|---|
| `{{variable_name}}` | string | [what to inject here] |
| `{{variable_name}}` | list | [what to inject here] |

---

## Current Template (v[N])

```
[Full prompt text with {{variable}} placeholders.
Keep the template exactly as sent to the model — do not paraphrase.]
```

---

## Example

**Input:**

```json
{
  "variable_name": "example value"
}
```

**Expected output:**

```
[Paste a representative model response for the example input above.]
```

---

## Test Cases

| # | Input | Expected behaviour |
|---|---|---|
| 1 | [typical input] | [what a good response looks like] |
| 2 | [edge case] | [expected handling] |
| 3 | [out-of-scope] | [should decline gracefully] |

---

## Version History

| Version | Date | Change | Reason |
|---|---|---|---|
| v1 | [YYYY-MM-DD] | Initial | |
| v[N] | [YYYY-MM-DD] | [what changed] | [why — e.g., eval score improved / added guardrail] |
