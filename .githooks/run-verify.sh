#!/usr/bin/env bash
# Optional Claude Code fast-feedback script (Phase 20).
# Called by .claude/settings.json Stop hook after every Claude session.
# Writes verify output to logs/ — non-blocking (always exits 0).

mkdir -p logs
if [ ! -f .project-starter.yml ] || [ ! -f docs/script/verify_docs.py ]; then
    exit 0
fi
TYPE=$(grep '^project_type:' .project-starter.yml | sed 's/project_type:[[:space:]]*//' | tr -d ""' ")
[ -z "$TYPE" ] && exit 0
python3 docs/script/verify_docs.py \
    --project-type "$TYPE" --content --json \
    > "logs/verify-$(date +%Y%m%d-%H%M%S).json" 2>&1 || true
