# project_starter_v4 — Roadmap

## Vision

project_starter_v4 started as a Web App framework. This roadmap tracks the expansion to support all major software project types so the same AI-agent workflow can be applied to any project without producing empty or irrelevant documents.

---

## Phase 1 — Multi-Type Foundation (this release)

**Goal:** Add Project Type declaration to AGENTS.md so AI agents know which documents are required vs N/A. Introduce Pipeline Stage module type. Create templates for all new project types.

### Framework changes

| File | Change |
|---|---|
| `AGENTS.md` | Add `## Project Type` section — type declaration, document matrix, per-type initialization sequences |
| `docs/templates/flows/module-data-flow-v2.md` | Add **Pipeline Stage** as 4th module type (Format D) |
| `document-purposes.md` | Add entries for all new template documents |

### New templates

| Template | For project type | Replaces / supplements |
|---|---|---|
| `specs/pipeline-contract.md` | Data Pipeline, ML Pipeline | `api-contract.md` |
| `specs/cli-contract.md` | CLI Tool | `api-contract.md` |
| `specs/public-api.md` | Library / SDK | `api-contract.md` |
| `specs/model-contract.md` | ML Pipeline | — |
| `specs/experiment-log.md` | ML Pipeline | `sprint-change-log.md` (per experiment) |
| `specs/service-catalog.md` | Microservices | — |
| `specs/service-contract.md` | Microservices | `api-contract.md` (inter-service) |
| `specs/release-guide.md` | Library / SDK, CLI Tool | `deployment.md` |
| `specs/compatibility-matrix.md` | Library / SDK, CLI Tool | — |
| `architecture/distribution.md` | Library / SDK, CLI Tool | `deployment.md` |

---

## Phase 2 — Per-Type Document Update Checklist (future)

The Document Update Checklist in AGENTS.md currently lists all documents. When a project declares itself as CLI or Library, many checklist items are not applicable, but the agent still has to read and skip them.

**Goal:** Gate checklist items by project type so agents only evaluate relevant items.

Approach options:
- Tag each checklist item with applicable project types (e.g., `[Web App, Microservices]`)
- Split into per-type checklists (higher maintenance cost)

---

## Phase 3 — Per-Type Code Quality Check (future)

`code-quality-check.md` currently assumes a layered application architecture (Controller/Service/Repository). It needs project-type variants:

| Type | Key areas to add |
|---|---|
| CLI | Flag parsing isolation, command responsibility separation, exit code consistency |
| Library | No side effects at import, public API stability, test coverage of public surface |
| Data Pipeline | Inter-stage contract verification, idempotency, archive/replay guarantees |
| ML Pipeline | Data leakage checks, train/test split integrity, metric reproducibility |
| Microservices | Service contract conformance, circuit breaker coverage, distributed tracing |

---

## Phase 4 — scan_codebase.py per-type awareness (future)

`scan_codebase.py` currently identifies modules by folder structure. For pipeline and ML projects, "modules" are stages, not folders. For libraries, they are namespaces.

**Goal:** Accept a `--project-type` flag so the scanner applies the right module boundary detection heuristic per type.

---

## Known gaps (not yet scheduled)

- Mobile App: `frontend.md` does not cover native mobile structure (no web page, different deployment model)
- IaC / DevOps: Nearly all documents are inapplicable; dedicated IaC template set needed
- Event-Driven / Messaging: `api-contract.md` cannot express event schemas; a separate `event-catalog.md` template is needed (related to Microservices type but distinct)
