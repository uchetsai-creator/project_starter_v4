# Refactoring Plan — project_starter_v4

Derived from `docs/architecture-analysis.md`. Addresses Problems 1–5 in three sequential phases.

---

## Phase 1 — Document Registry + Context Builder + AGENTS.md Reduction

**Goal:** Eliminate duplicated project-type knowledge (Problems 1–4) and deterministic task startup context (Problem 5).

**Risk:** Low — scripts are refactored to load from the registry; behaviour is unchanged. AGENTS.md shrinks but all rules remain enforced by the hook.

### Files affected

| File | Change | Type |
|---|---|---|
| `document-registry.yaml` (new) | Single source of truth for all document metadata | New |
| `verify_docs.py` | Remove `MATRIX`, `FILE_LOCATIONS`, `VALID_TYPES`; load from registry | Refactor |
| `verify_content.py` | Remove `TYPE_DOCS`, `DOC_PATHS`, `VALID_TYPES`, `UNIVERSAL_DOCS`; load from registry | Refactor |
| `verify_logs.py` | Remove `VALID_TYPES`, `LOGGING_REQUIRED`, `TRACE_ID_TYPES`; load from registry | Refactor |
| `verify_tests.py` | Remove `VALID_TYPES`, `PIPELINE_TYPES`; load from registry | Refactor |
| `build_pdf.py` | Remove `VALID_PROJECT_TYPES`, `AUTO_SCAN_TYPES`; load from registry | Refactor |
| `templates/init/document-matrix.md` | Replace static table with "generated from document-registry.yaml" note | Update |
| `build-context.py` (new, repo root) | Reads `.project-starter.yml` + `current-state.md`; writes `.ai/AI_CONTEXT.md` | New |
| `.project-starter.yml` | Add optional `task_type` field | Update |
| `templates/current-state.md` | Add `Task Type:` field; add "run build-context.py" note | Update |
| `AGENTS.md` | Remove startup discovery logic and Quick filter guide; add pointer to `build-context.py` | Simplify |
| `.gitignore` | Add `.ai/` | Update |
| `README.md` | Add Context Builder section | Update |
| `guidance/document-purposes-common.md` | Add `build-context.py` and `.ai/AI_CONTEXT.md` entries | Update |

### Migration strategy

1. Create `document-registry.yaml` with the full schema (see `docs/context-builder-design.md`)
2. Add a thin registry loader (`_registry.py`) in `templates/script/`
3. Refactor each script: replace hardcoded dicts with `load_registry()` calls
4. Verify: run `verify_framework.py --strict` — all checks must pass
5. Implement `build-context.py`
6. Simplify `AGENTS.md`

**No folder restructuring in this phase** — every script path reference stays the same. The value is gained from the registry and context builder alone, without rename churn.

---

## Phase 2 — Workflow State Extraction

**Goal:** Extract the task-state machine (current-state.md, sprint-change-log.md, task-log.md update rules) from AGENTS.md prose into a structured `workflow-state.yaml`. AI agents read the YAML instead of parsing natural-language rules.

**Risk:** Medium — changes AGENTS.md structure agents rely on. Requires testing with Claude Code before merging.

### Files affected

| File | Change | Type |
|---|---|---|
| `workflow-state.yaml` (new) | Structured task lifecycle: transitions, required fields, doc-checklist trigger rules | New |
| `AGENTS.md` | Remove task lifecycle prose; replace with pointer to `workflow-state.yaml` | Simplify |
| `build-context.py` | Read `workflow-state.yaml` to augment `.ai/AI_CONTEXT.md` with lifecycle rules | Update |
| `verify_framework.py` | Add check: `workflow-state.yaml` must exist and be valid YAML | Update |

### Migration strategy

1. Extract closeout rules, Doc Checklist trigger table, and sprint-sync procedure from AGENTS.md
2. Encode them in `workflow-state.yaml`
3. Update `build-context.py` to include relevant workflow rules in `.ai/AI_CONTEXT.md`
4. Manually test one full task cycle (start → closeout) with the new files before removing AGENTS.md prose

---

## Phase 3 — Full Orchestrator + Agent Adapters

**Goal:** Replace direct script calls with an orchestrator (`run.py` or `project-starter` CLI) that reads from the registry and workflow state. Add thin adapters for Claude Code MCP, Cursor, and Codex.

**Risk:** High — user-facing interface change. Requires deprecation path for direct script calls.

### Files affected

| File | Change | Type |
|---|---|---|
| `run.py` (new, repo root) | CLI orchestrator: `run verify`, `run context`, `run pdf`, `run scan` | New |
| `adapters/claude-mcp-server.py` (new) | MCP tool wrappers for Claude Code | New |
| `adapters/cursor-rules.md` (new) | Cursor-compatible rules file generated from registry | New |
| `README.md` | Add "Using the orchestrator" section; deprecate direct script calls | Update |
| `AGENTS.md` | Replace all `python3 docs/script/X.py` calls with `run X` | Update |

### Migration strategy

1. Implement `run.py` as a thin dispatcher that calls existing scripts unchanged
2. Publish adapters as optional add-ons; direct script calls continue to work
3. Deprecate direct calls in README with a 2-phase notice (warn → remove)

---

## Risk Register

| Risk | Phase | Likelihood | Mitigation |
|---|---|---|---|
| Registry schema breaks a script silently | 1 | Low | `verify_framework.py` validates registry on every commit |
| AI agent does not read `.ai/AI_CONTEXT.md` | 1 | Medium | AGENTS.md explicitly instructs agents to read it first |
| Workflow YAML is harder to update than prose | 2 | Medium | Keep YAML flat; one field per rule; AGENTS.md prose remains as comments |
| Orchestrator adds install friction | 3 | Low | `run.py` is zero-dependency stdlib; no pip install required |
| Adapter diverges from registry | 3 | Medium | Adapters generated from registry at build time, not hand-written |
