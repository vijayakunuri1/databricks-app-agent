#!/usr/bin/env bash
# Applies branch protection rules to the master branch via the GitHub REST API.
#
# Usage:
#   export GITHUB_TOKEN=<your-personal-access-token>
#   bash scripts/setup_branch_protection.sh
#
# Required token scopes: repo (for private repos) or public_repo (for public repos)

set -euo pipefail

OWNER="Lockton-Companies"
REPO="databricks-app-agent"
BRANCH="master"
API="https://api.github.com/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection"

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "Error: GITHUB_TOKEN is not set."
  echo "Export a GitHub PAT with 'repo' scope and re-run."
  exit 1
fi

echo "Applying branch protection rules to '${BRANCH}'..."

curl -s -X PUT "${API}" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["Lint & Format", "Type Check", "Tests"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false,
      "required_approving_review_count": 1
    },
    "restrictions": null,
    "required_linear_history": true,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "block_creations": false,
    "required_conversation_resolution": true
  }' | python3 -m json.tool

echo ""
echo "Branch protection applied. Verify at:"
echo "  https://github.com/${OWNER}/${REPO}/settings/branches"
