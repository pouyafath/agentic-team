#!/usr/bin/env bash
# Install the agentic team into an existing git repository without overwriting anything.
#   scripts/install.sh /path/to/project
# For a brand-new project, prefer GitHub's "Use this template" on this repository.
set -euo pipefail

kit="$(cd "$(dirname "$0")/.." && pwd)"
dst="${1:?usage: scripts/install.sh <target-repo>}"
[ -e "$dst/.git" ] || { echo "error: $dst is not a git repository" >&2; exit 1; }

items=(
  CLAUDE.md
  .claude/settings.json .claude/hooks .claude/agents .claude/skills
  .github/ISSUE_TEMPLATE .github/pull_request_template.md .github/CODEOWNERS
  .github/workflows/ci.yml .github/workflows/deploy.yml
  docs/adr/0000-template.md docs/runbooks/rollback.md
  scripts/metrics.py scripts/setup-github.sh
)

copied=0; skipped=0
for item in "${items[@]}"; do
  while IFS= read -r -d '' src; do
    rel="${src#"$kit"/}"
    if [ -e "$dst/$rel" ]; then
      echo "skip (exists): $rel"; skipped=$((skipped + 1))
    else
      mkdir -p "$dst/$(dirname "$rel")" && cp "$src" "$dst/$rel" && copied=$((copied + 1))
    fi
  done < <(find "$kit/$item" -type f -not -name '*.pyc' -print0)
done

grep -qs '^\.claude/worktrees/' "$dst/.gitignore" || printf '\n# agentic team\n.claude/worktrees/\n.claude/settings.local.json\n' >> "$dst/.gitignore"

echo "Installed $copied files ($skipped skipped) into $dst"
echo "Next: merge any skipped files by hand, add 'make lint/test/acceptance/ci' targets,"
echo "commit on a branch, open a PR, then run scripts/setup-github.sh --protect."
