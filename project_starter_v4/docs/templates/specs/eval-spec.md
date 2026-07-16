# Evaluation Spec

<!--
  For: AI / LLM Application
  Purpose: Defines how LLM output quality is measured — using LLM-as-a-judge.
           This file contains the stable config: judge model, criteria, rubric, test case set.
           Eval run results are appended to eval-log.md — not here.
  Update when: Evaluation criteria change, judge model changes, or test cases are added.
               Do not modify existing test cases — add new ones only.
-->

## Judge Model

| Property | Value |
|---|---|
| Judge model | [e.g., claude-opus-4-7] |
| Judge temperature | [e.g., 0.0 — deterministic scoring] |
| Scoring format | [1–5 per criterion / pass-fail / weighted average] |
| Pass threshold | [e.g., average ≥ 3.5 across all criteria] |

Eval run results → `docs/specs/eval-log.md`

---

## Evaluation Criteria

| Criterion | Weight | 1 (Poor) | 5 (Excellent) |
|---|---|---|---|
| **Factual accuracy** | [e.g., 30%] | Contains false or invented facts | All claims are accurate and verifiable |
| **Relevance** | [e.g., 25%] | Ignores the user's actual question | Directly addresses what was asked |
| **Risk disclosure** | [e.g., 25%] | No mention of risk or uncertainty | Appropriate caveats and risk language present |
| **Clarity** | [e.g., 20%] | Confusing, hard to follow | Clear, structured, easy to act on |

Add or remove criteria to match your application's quality goals.

---

## Judge Prompt Template

```
You are evaluating the quality of a [financial advisor / assistant / etc.] AI response.

User question:
{{user_question}}

AI response to evaluate:
{{ai_response}}

Score the response on each criterion below. For each criterion, give:
- A score from 1 to 5
- One sentence explaining the score

Criteria:
1. Factual accuracy (1=false claims, 5=all claims accurate)
2. Relevance (1=ignores question, 5=directly answers it)
3. Risk disclosure (1=no caveats, 5=appropriate risk language)
4. Clarity (1=confusing, 5=clear and actionable)

Output as JSON:
{
  "factual_accuracy": { "score": N, "reason": "..." },
  "relevance": { "score": N, "reason": "..." },
  "risk_disclosure": { "score": N, "reason": "..." },
  "clarity": { "score": N, "reason": "..." },
  "overall": N
}
```

---

## Test Case Set

Run this fixed set every time a prompt version changes. Do not modify existing cases — add new ones only.

| # | ID | Category | User question | Expected quality bar |
|---|---|---|---|---|
| 1 | `tc-001` | Core use case | [typical user question] | All criteria ≥ 4 |
| 2 | `tc-002` | Edge case | [ambiguous or tricky question] | risk_disclosure ≥ 4, no fabricated facts |
| 3 | `tc-003` | Out-of-scope | [question outside domain] | Response declines gracefully |

---

## How to Run

```bash
# Run eval suite against a prompt version — appends result to eval-log.md
python3 scripts/run_eval.py --prompt-version v2

# Compare two prompt versions
python3 scripts/run_eval.py --compare v1 v2
```
