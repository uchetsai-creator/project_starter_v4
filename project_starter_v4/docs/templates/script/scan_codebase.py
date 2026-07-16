#!/usr/bin/env python3
"""scan_codebase.py — Module inventory and documentation coverage check

Scans a source directory and compares it against docs/modules/ to find:
  - Which folders are already documented
  - Which folders are not yet documented
  - Which folders are uncertain (shared utility? infrastructure?)

Outputs:
  --tree      Print a tree view of the source directory with coverage annotations
  --coverage  Print a coverage summary table
  --update    Update the Project Structure and Coverage Summary sections in codebase-map.md

Usage:
  python3 docs/script/scan_codebase.py <src_dir>
  python3 docs/script/scan_codebase.py <src_dir> --project-type <type>
  python3 docs/script/scan_codebase.py <src_dir> --tree
  python3 docs/script/scan_codebase.py <src_dir> --coverage
  python3 docs/script/scan_codebase.py <src_dir> --update docs/codebase-map.md

Project types (controls module boundary detection heuristic):
  web-app        Folders = Feature modules, Background Jobs, or Shared/Infrastructure (default)
  cli-tool       Folders = Commands or Shared/Infrastructure
  library        Folders = Namespaces or Shared/Infrastructure
  data-pipeline  Folders = Pipeline Stages or Shared/Infrastructure
  ml-pipeline    Folders = Pipeline Stages or Shared/Infrastructure
  microservices  Folders = Services or Shared/Infrastructure
  llm-app        Folders = Feature modules, Background Jobs, or Shared/Infrastructure

Examples:
  python3 docs/script/scan_codebase.py src
  python3 docs/script/scan_codebase.py src --project-type data-pipeline
  python3 docs/script/scan_codebase.py stages --project-type ml-pipeline --update docs/codebase-map.md
  python3 docs/script/scan_codebase.py src --project-type cli-tool --coverage
"""

import sys
import os
import argparse
import glob
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Folders that are almost never feature modules — skip or mark as "—"
# ---------------------------------------------------------------------------
SHARED_PATTERNS = {
    "lib", "libs", "utils", "util", "helpers", "helper",
    "common", "shared", "core", "types", "interfaces",
    "config", "configs", "constants", "constants",
    "middleware", "middlewares",
    "scripts", "script",
    "migrations", "migration", "seeds", "seed",
    "test", "tests", "__tests__", "spec", "specs",
    "dist", "build", "node_modules", ".git", "__pycache__",
    "docs", "docs-zh", "logs",
}

JOB_PATTERNS = {
    "jobs", "job", "workers", "worker",
    "consumers", "consumer", "subscribers", "subscriber",
    "cron", "crons", "tasks", "task", "queues", "queue",
    "handlers", "events",
}

# Pipeline stage name patterns — folder names commonly used in Data/ML pipelines.
# Numbers are stripped before matching (e.g. "01_extract" → "extract").
PIPELINE_STAGE_PATTERNS = {
    # Data pipeline stages
    "extract", "ingest", "intake", "fetch", "collect",
    "validate", "validation", "quality", "check",
    "transform", "transformation", "process", "processing", "enrich",
    "load", "export", "output", "sink",
    "stage", "staging",
    "raw", "curated", "clean", "cleaned",
    # ML pipeline stages
    "data", "dataset",
    "preprocess", "preprocessing",
    "features", "feature_engineering", "featurize",
    "train", "training",
    "evaluate", "evaluation", "eval",
    "predict", "prediction", "inference", "score", "scoring",
    "serve", "serving",
    "deploy", "deployment",
    "monitor", "monitoring",
    "register", "registry",
}

# ---------------------------------------------------------------------------
# Per-type vocabulary: what to call a non-shared folder
# ---------------------------------------------------------------------------

# Maps project-type → (singular label, plural label for summary line)
MODULE_VOCAB: dict[str, tuple[str, str]] = {
    "web-app":       ("Feature",        "feature modules"),
    "cli-tool":      ("Command",        "commands"),
    "library":       ("Namespace",      "namespaces"),
    "data-pipeline": ("Pipeline Stage", "pipeline stages"),
    "ml-pipeline":   ("Pipeline Stage", "pipeline stages"),
    "microservices": ("Service",        "services"),
    "llm-app":       ("Feature",        "feature modules"),
}

VALID_PROJECT_TYPES = list(MODULE_VOCAB.keys())


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def is_shared(name: str) -> bool:
    return name.lower() in SHARED_PATTERNS


def is_job_folder(name: str) -> bool:
    lower = name.lower()
    if lower in JOB_PATTERNS:
        return True
    # Match compound names like "order-consumer", "cron-inventory", "email-worker"
    parts = re.split(r"[-_]", lower)
    return any(p in JOB_PATTERNS for p in parts)


def is_pipeline_stage(name: str) -> bool:
    """Return True if the folder name matches a known pipeline stage pattern."""
    lower = name.lower()
    if lower in PIPELINE_STAGE_PATTERNS:
        return True
    # Strip leading numeric prefix: "01_extract" → "extract", "02-validate" → "validate"
    stripped = re.sub(r"^\d+[_\-]", "", lower)
    return stripped in PIPELINE_STAGE_PATTERNS


def guess_type(name: str, project_type: str | None = None) -> str:
    """Classify a source folder based on its name and the declared project type.

    Project type controls which module boundary heuristic applies:
    - data-pipeline / ml-pipeline: all non-shared folders are Pipeline Stages
    - cli-tool: all non-shared folders are Commands
    - library: all non-shared folders are Namespaces
    - microservices: all non-shared folders are Services
    - web-app / llm-app / None: Feature or Background Job (existing behaviour)
    """
    if is_shared(name):
        return "Shared / Infrastructure"

    if project_type in ("data-pipeline", "ml-pipeline"):
        # In a pipeline project all non-shared folders are stages.
        # is_pipeline_stage() provides extra confidence but does not gate the label —
        # an unknown folder name in a pipeline project is still a Pipeline Stage.
        return "Pipeline Stage"

    if project_type == "cli-tool":
        return "Command"

    if project_type == "library":
        return "Namespace"

    if project_type == "microservices":
        return "Service"

    # web-app, llm-app, and unspecified (default)
    if is_job_folder(name):
        return "Background Job"
    return "Feature"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_source_folders(src_dir: str, project_type: str | None = None) -> list[dict]:
    """Return all immediate subdirectories of src_dir (one level only)."""
    src_path = Path(src_dir)
    if not src_path.exists():
        print(f"Error: directory not found: {src_dir}")
        sys.exit(1)

    folders = []
    for entry in sorted(src_path.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            folders.append({
                "name": entry.name,
                "path": str(entry),
                "rel": str(entry.relative_to(src_path.parent)),
                "type": guess_type(entry.name, project_type),
            })
    return folders


def find_documented_modules(docs_dir: str = "docs") -> dict[str, str]:
    """Return {module_name: flow_file_path} for all existing module flow files."""
    pattern = os.path.join(docs_dir, "modules", "**", "*-module-data-flow.md")
    result = {}
    for path in glob.glob(pattern, recursive=True):
        # Derive module name from the parent folder name
        module_name = Path(path).parent.name
        result[module_name] = path
    return result


def match_folder_to_module(folder_name: str, documented: dict[str, str]) -> str | None:
    """Try to find a matching documented module for a source folder."""
    # Exact match
    if folder_name in documented:
        return documented[folder_name]
    # Prefix match (e.g. src folder "order" matches "order-consumer" module? no — only exact or suffix)
    for module_name, path in documented.items():
        if module_name == folder_name:
            return path
    return None


def annotate_folders(folders: list[dict], documented: dict[str, str]) -> list[dict]:
    for f in folders:
        match = match_folder_to_module(f["name"], documented)
        if f["type"] == "Shared / Infrastructure":
            f["status"] = "—"
            f["status_icon"] = "—"
            f["flow_file"] = "— Not required"
        elif match:
            f["status"] = "Documented"
            f["status_icon"] = "✅"
            f["flow_file"] = match
        else:
            f["status"] = "Not documented"
            f["status_icon"] = "❌"
            f["flow_file"] = "—"
    return folders


# ---------------------------------------------------------------------------
# Output: Tree view
# ---------------------------------------------------------------------------

def _arrow(label: str, width: int = 36) -> str:
    """Right-pad name to `width` chars then append ← label."""
    return f"{label:<{width}}← "


def print_tree(src_dir: str, folders: list[dict], docs_dir: str = "docs") -> str:
    """
    Build a full project-root tree starting one level above src_dir.
    Annotates every folder with ← description and module status icons.
    """
    src_path = Path(src_dir).resolve()
    project_root = src_path.parent
    folder_names = {f["name"] for f in folders}

    lines = []
    lines.append(f"{project_root.name}/")

    # Collect top-level entries of the project root
    try:
        root_entries = sorted(project_root.iterdir(), key=lambda x: (x.is_file(), x.name))
    except PermissionError:
        root_entries = []

    # Skip noisy folders at root level
    SKIP_ROOT = {".git", ".github", "node_modules", "__pycache__", ".venv", "venv",
                 "dist", "build", ".next", ".nuxt", "coverage", ".pdf_build_cache"}

    visible = [e for e in root_entries if e.name not in SKIP_ROOT]

    for i, entry in enumerate(visible):
        is_last = (i == len(visible) - 1)
        prefix = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if entry == src_path:
            # This is the source folder — expand its modules
            lines.append(f"{prefix}{_arrow(entry.name + '/', 28)}application source code")
            try:
                src_children = sorted(src_path.iterdir(), key=lambda x: (x.is_file(), x.name))
            except PermissionError:
                src_children = []
            src_visible = [e for e in src_children if e.name not in SKIP_ROOT]
            for j, sub in enumerate(src_visible):
                sub_last = (j == len(src_visible) - 1)
                sub_prefix = child_prefix + ("└── " if sub_last else "├── ")
                if sub.is_dir() and sub.name in folder_names:
                    folder = next(f for f in folders if f["name"] == sub.name)
                    icon = folder["status_icon"]
                    desc = folder.get("desc", folder["type"])
                    # Fixed-width columns: icon(2) + space(2) + name+slash padded to 24 + ← desc
                    name_col = f"{sub.name}/"
                    lines.append(f"{sub_prefix}{icon}  {name_col:<24}← {desc}")
                elif sub.is_dir():
                    lines.append(f"{sub_prefix}{sub.name}/")
                else:
                    lines.append(f"{sub_prefix}{sub.name}")

        elif entry.is_dir():
            # Annotate known top-level folders
            known = {
                "docs":        "planning, specs, architecture, module flow docs",
                "doc":         "planning, specs, architecture, module flow docs",
                "prisma":      "database schema and migrations",
                "migrations":  "database migrations",
                "migration":   "database migrations",
                "test":        "tests",
                "tests":       "tests",
                "__tests__":   "tests",
                "scripts":     "utility scripts",
                "script":      "utility scripts",
                "infra":       "infrastructure / IaC",
                "k8s":         "Kubernetes manifests",
                "deploy":      "deployment configs",
                "config":      "configuration files",
                "public":      "static assets",
                "assets":      "static assets",
            }
            desc = known.get(entry.name.lower(), "")
            if desc:
                lines.append(f"{prefix}{_arrow(entry.name + '/', 28)}{desc}")
            else:
                lines.append(f"{prefix}{entry.name}/")

        else:
            # Annotate known config files
            known_files = {
                "package.json":       "Node.js dependency manifest",
                "go.mod":             "Go module definition",
                "requirements.txt":   "Python dependencies",
                "pyproject.toml":     "Python project config",
                "Cargo.toml":         "Rust package manifest",
                "pom.xml":            "Maven project config",
                "build.gradle":       "Gradle build config",
                "docker-compose.yml": "local infrastructure services",
                "docker-compose.yaml":"local infrastructure services",
                "Dockerfile":         "container build definition",
                ".env.example":       "environment variable template",
                "Makefile":           "build / dev task runner",
                "README.md":          "project overview",
            }
            desc = known_files.get(entry.name, "")
            if desc:
                lines.append(f"{prefix}{_arrow(entry.name, 28)}{desc}")
            else:
                lines.append(f"{prefix}{entry.name}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output: Coverage table
# ---------------------------------------------------------------------------

def print_coverage(folders: list[dict], project_type: str | None = None) -> str:
    _, plural_label = MODULE_VOCAB.get(project_type, ("Feature", "feature modules"))

    lines = []
    lines.append(f"=== {plural_label.title()} Coverage Report ===\n")

    documented = [f for f in folders if f["status"] == "Documented"]
    undocumented = [f for f in folders if f["status"] == "Not documented"]
    shared = [f for f in folders if f["status"] == "—"]

    if documented:
        lines.append("✅  Documented:")
        for f in documented:
            lines.append(f"    {f['rel']:<40}  →  {f['flow_file']}")
        lines.append("")

    if undocumented:
        lines.append("❌  Not yet documented:")
        for f in undocumented:
            lines.append(f"    {f['rel']:<40}  →  needs module-data-flow.md  [{f['type']}]")
        lines.append("")

    if shared:
        lines.append("—   Shared / Infrastructure (no flow file needed):")
        for f in shared:
            lines.append(f"    {f['rel']}")
        lines.append("")

    total = len(documented) + len(undocumented)
    pct = int(len(documented) / total * 100) if total else 100
    lines.append(f"Coverage: {len(documented)}/{total} {plural_label} documented ({pct}%)")

    if undocumented:
        lines.append("")
        lines.append("Next steps:")
        for f in undocumented:
            slug = f["name"]
            lines.append(
                f"  - Create docs/modules/{slug}/{slug}-module-data-flow.md  [{f['type']}]"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output: Update codebase-map.md
# ---------------------------------------------------------------------------

def build_tree_block(src_dir: str, folders: list[dict], docs_dir: str = "docs") -> str:
    tree = print_tree(src_dir, folders, docs_dir)
    lines = ["```"]
    lines.append(tree)
    lines.append("```")
    return "\n".join(lines)


def build_coverage_table(folders: list[dict]) -> str:
    lines = []
    lines.append("| Module / Folder | Type | Status | Flow file |")
    lines.append("|---|---|---|---|")
    for f in folders:
        icon = f["status_icon"]
        status_text = f"{icon} {f['status']}" if f["status_icon"] != "—" else "— Not required"
        flow = f["flow_file"] if f["flow_file"] != "—" else "—"
        lines.append(f"| `{f['rel']}` | {f['type']} | {status_text} | {flow} |")
    return "\n".join(lines)


def update_codebase_map(map_path: str, src_dir: str, folders: list[dict], docs_dir: str = "docs"):
    if not os.path.exists(map_path):
        print(f"Error: codebase-map.md not found at {map_path}")
        sys.exit(1)

    with open(map_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree_block = build_tree_block(src_dir, folders, docs_dir)
    coverage_table = build_coverage_table(folders)

    # Replace Project Structure section
    content = re.sub(
        r"(## Project Structure\n<!--.*?-->\n\n)```[\s\S]*?```",
        r"\g<1>" + tree_block,
        content,
        flags=re.DOTALL,
    )

    # Replace Coverage Summary table
    content = re.sub(
        r"(## Coverage Summary\n<!--.*?-->\n\n)\|[\s\S]*?\n\n",
        r"\g<1>" + coverage_table + "\n\n",
        content,
        flags=re.DOTALL,
    )

    with open(map_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated: {map_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scan source directory and check documentation coverage."
    )
    parser.add_argument("src_dir", help="Source directory to scan (e.g. src, app, stages)")
    parser.add_argument(
        "--project-type",
        metavar="TYPE",
        choices=VALID_PROJECT_TYPES,
        help=(
            f"Project type — controls module boundary detection heuristic. "
            f"Valid values: {', '.join(VALID_PROJECT_TYPES)}"
        ),
    )
    parser.add_argument("--tree", action="store_true", help="Print tree view with coverage icons")
    parser.add_argument("--coverage", action="store_true", help="Print coverage summary")
    parser.add_argument("--update", metavar="CODEBASE_MAP", help="Update codebase-map.md in place")
    parser.add_argument("--docs", default="docs", help="Path to docs directory (default: docs)")
    args = parser.parse_args()

    project_type = args.project_type  # None if not supplied — falls back to web-app behaviour

    folders = find_source_folders(args.src_dir, project_type)
    documented = find_documented_modules(args.docs)
    folders = annotate_folders(folders, documented)

    # Default: show both tree and coverage if no flag given
    show_all = not args.tree and not args.coverage and not args.update

    if args.tree or show_all:
        print(print_tree(args.src_dir, folders, args.docs))
        print()

    if args.coverage or show_all:
        print(print_coverage(folders, project_type))

    if args.update:
        update_codebase_map(args.update, args.src_dir, folders, args.docs)


if __name__ == "__main__":
    main()
