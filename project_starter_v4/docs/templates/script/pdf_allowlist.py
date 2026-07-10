"""pdf_allowlist.py — Single source of truth for the PDF file list.

Imported by both build_pdf.py and translate_docs.py.
Edit only this file when adding or removing documents from the PDF.

Chapter structure:
  1. Introduction   — system overview, stakeholders, glossary
  2. Plan           — project plan, changelog
  3. Design         — architecture, data model, interface design
  4. Build          — module flows, codebase map, dependencies
  5. Test           — test plan and report
  6. Deployment     — deployment topology, environment, logging

Rules:
  - Each entry is (section_key, relative_path_from_docs_dir).
  - section_key must match a key in STRINGS["en"]["sections"] in build_pdf.py.
  - Order determines the order documents appear in the PDF.
  - Files under business/*-process.md, business/*-object.md, and
    modules/*/*-module-data-flow.md are auto-scanned and do NOT need to be listed here.
  - log-*.md files are intentionally excluded — dev reference only, not PDF audience.
"""

PDF_ALLOWLIST = [
    # ── Chapter 1: Introduction ──────────────────────────────────────────────
    ("introduction",   "project-requirements.md"),
    ("introduction",   "business/business-rules.md"),
    ("introduction",   "business/business-objects.md"),   # index
    ("introduction",   "business/business-process.md"),   # index
    # *-object.md and *-process.md auto-scanned
    ("introduction",   "specs/glossary.md"),

    # ── Chapter 2: Plan ──────────────────────────────────────────────────────
    ("plan",           "project-plan.md"),
    ("plan",           "changelog.md"),
    ("plan",           "task-log.md"),
    ("plan",           "sprint-change-log.md"),

    # ── Chapter 3: Design ────────────────────────────────────────────────────
    ("design",         "architecture/architecture.md"),
    ("design",         "architecture/backend.md"),
    ("design",         "architecture/frontend.md"),
    ("design",         "architecture/database.md"),
    ("design",         "specs/data-model.md"),
    ("design",         "specs/api-contract.md"),
    ("design",         "specs/permissions.md"),
    # specs/research.md is excluded until filled with real content.
    # Uncomment the line below once it has actual technology decisions (not just placeholders):
    # ("design",         "specs/research.md"),
    # *-module-data-flow.md auto-scanned (class diagrams)
    # module-flow files auto-scanned (sequence diagrams)

    # ── Chapter 4: Build ─────────────────────────────────────────────────────
    ("build",          "modules/module-data-flow.md"),    # index (section-filtered)
    ("build",          "modules/module-flow.md"),         # index (section-filtered)
    ("build",          "codebase-map.md"),
    ("build",          "specs/dependencies.md"),
    ("build",          "architecture/deployment.md"),     # build steps + startup

    # ── Chapter 5: Test ──────────────────────────────────────────────────────
    ("test",           "specs/test-plan.md"),
    ("test",           "specs/test-report.md"),

    # ── Chapter 6: Deployment ────────────────────────────────────────────────
    ("deployment",     "specs/logging-spec.md"),
    ("deployment",     "specs/quickstart.md"),
]


# Per-file section filter: only the listed ## headings (and their content) are kept.
# Everything else in the file is stripped before rendering.
PDF_SECTION_FILTER = {
    "modules/module-data-flow.md":    ["## Module Flow Files"],
    "modules/module-flow.md":         ["## Flow Files"],
    "business/business-objects.md":   ["## Object Files", "## Relationships"],
    "business/business-process.md":   ["## Process Files"],
    # business-rules.md: keep real rule sections, strip placeholder BR-001/BR-002 blocks
    "business/business-rules.md":     ["## Approval Rules", "## Validation Rules",
                                       "## Notification Rules", "## Audit Rules"],
}
