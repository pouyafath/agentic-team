#!/usr/bin/env bash
# One-time GitHub setup for a project run by the agentic team.
# Run it yourself (human, repo admin) from the project root, not through an agent:
#   scripts/setup-github.sh [owner/repo] [--protect]
set -euo pipefail

repo="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
[[ "$repo" == --* ]] && repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
protect=false
for arg in "$@"; do [[ "$arg" == "--protect" ]] && protect=true; done

echo "Configuring $repo"

labels=(
  "type:brief|5319e7|Product brief"
  "type:epic|3e4b9e|Epic grouping several stories"
  "type:story|1d76db|User story: one branch, one PR"
  "type:bug|d73a4a|Defect"
  "type:chore|c5def5|Maintenance or ops work"
  "type:spike|fbca04|Time-boxed research"
  "status:backlog|ededed|Not yet ready"
  "status:ready|0e8a16|Spec complete, can start"
  "status:in-progress|1d76db|Being implemented"
  "status:in-review|5319e7|QA verification and code review"
  "status:ready-for-release|0e8a16|Gates passed, awaiting merge/release"
  "status:blocked|b60205|Waiting on the Product Owner"
  "risk:0|c2e0c6|Low risk"
  "risk:1|fef2c0|Standard risk"
  "risk:2|f9d0c4|Sensitive: auth, money, PII, migrations, infra"
  "po:approved|0e8a16|Product Owner approved (required for risk:2)"
  "defect:escaped|b60205|Bug found after merge"
)
for spec in "${labels[@]}"; do
  IFS='|' read -r name color desc <<< "$spec"
  gh label create "$name" --repo "$repo" --color "$color" --description "$desc" --force >/dev/null
done
echo "✓ labels"

login="$(gh api user -q .login)"
if grep -q '@PRODUCT_OWNER' .github/CODEOWNERS 2>/dev/null; then
  sed -i.bak "s/@PRODUCT_OWNER/@${login}/g" .github/CODEOWNERS && rm -f .github/CODEOWNERS.bak
  echo "✓ CODEOWNERS now names @${login}: commit and push this change"
fi

if $protect; then
  # Required checks match the job names in .github/workflows/ci.yml.
  # Approving reviews stay at 0 while agents push with your identity (you cannot approve your own PR).
  # Once agents use a separate bot account, raise it to 1 and require code-owner review.
  gh api -X PUT "repos/$repo/branches/main/protection" --input - <<'JSON' >/dev/null
{
  "required_status_checks": {"strict": true, "contexts": ["make ci", "secret scan", "static analysis"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"required_approving_review_count": 0, "dismiss_stale_reviews": true},
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
  echo "✓ branch protection on main"
fi

cat <<EOF

Remaining manual steps (GitHub UI):
  1. Settings > Environments: create 'staging' and 'production'; on 'production' add yourself
     as Required reviewer (human gate G4). Put deploy credentials in environment secrets.
  2. When staging exists: Settings > Variables > DEPLOY_ENABLED=true.
  3. Private repo with GitHub Code Security? Set variable GHAS_ENABLED=true for dependency review.
  4. Optional: a Projects board grouped by the status:* labels for a visual Kanban view.
EOF
