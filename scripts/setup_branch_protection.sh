#!/usr/bin/env bash
# ==============================================================================
# Setup GitHub Branch Protection Rules via GitHub CLI (gh)
# ==============================================================================
set -euo pipefail

REPO="${1:-KrishnakantYadav00/cicdintegratedshortner}"
BRANCH="main"

echo "Setting up branch protection for repository: ${REPO} on branch: ${BRANCH}"

if ! command -v gh &> /dev/null; then
  echo "[!] GitHub CLI (gh) is not installed."
  echo "Please configure branch protection in GitHub Web UI:"
  echo "1. Go to https://github.com/${REPO}/settings/branches"
  echo "2. Click 'Add classic branch protection rule' or 'Add rule'"
  echo "3. Branch name pattern: ${BRANCH}"
  echo "4. Check 'Require a pull request before merging'"
  echo "5. Check 'Require status checks to pass before merging'"
  echo "   - Require branches to be up to date before merging"
  echo "   - Status checks required: 'Lint & Unit Tests', 'Docker Build & Vulnerability Scan'"
  echo "6. Check 'Do not allow bypassing the above settings'"
  echo "7. Save changes."
  exit 0
fi

echo "Submitting branch protection payload via GitHub API..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Lint & Unit Tests",
      "Docker Build & Vulnerability Scan"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "[✓] Branch protection successfully configured for ${REPO}:${BRANCH}!"
