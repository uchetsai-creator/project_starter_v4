# Prompt Library

<!--
  For: AI / LLM Application
  Purpose: Index of all prompt templates. This file lists what exists and defines the rules.
           Actual prompt content lives in individual [prompt-id]-prompt.md files.
           Do not put prompt content in this file — keep it as index only.
  Update when: A prompt file is created, retired, or its current version changes.
-->

## Rules

* This file is the index only. Do not write prompt content here.
* Each prompt must have its own file: `docs/specs/prompts/[prompt-id]-prompt.md`
* After creating or updating a prompt file, verify the row in the Active Prompts table below.
* When retiring a prompt, move its row to the Retired Prompts table and update the file status.

## Naming Convention

```
[feature]-[purpose]
```

File: `docs/specs/prompts/[prompt-id]-prompt.md`

Examples:
```
docs/specs/prompts/financial-advice-prompt.md
docs/specs/prompts/rag-synthesis-prompt.md
docs/specs/prompts/intent-classifier-prompt.md
```

---

## Active Prompts

| Prompt ID | Current version | Purpose | File |
|---|---|---|---|
| [prompt-id] | v1 | [what it does] | `prompts/[prompt-id]-prompt.md` |

---

## Retired Prompts

| Prompt ID | Last version | Retired date | Replaced by | Reason |
|---|---|---|---|---|
| [prompt-id] | v2 | [YYYY-MM-DD] | [new-prompt-id] | [e.g., model change required rewrite] |
