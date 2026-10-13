#!/bin/bash
# scripts/git_hook.sh — pre-push git hook for prscore risk scoring
#
# Install:
#   cp scripts/git_hook.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push
#
# This hook runs `prscore review` on each commit being pushed.
# If any commit scores >= 60, the push is blocked and a decision is required.

set -euo pipefail

PRSCORE_CMD="${PRSCORE_CMD:-prscore}"
RISK_THRESHOLD="${RISK_THRESHOLD:-60}"
REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "[prscore] Pre-push hook running..."

# Read the list of refs being pushed (stdin format: <local_ref> <local_sha> <remote_ref> <remote_sha>)
while IFS=' ' read -r local_ref local_sha remote_ref remote_sha; do
    # Skip deletions
    if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # Determine range to check
    if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
        # New branch — check last 5 commits
        RANGE="${local_sha}~5..${local_sha}"
    else
        RANGE="${remote_sha}..${local_sha}"
    fi

    COMMIT_LIST=$(git log --format="%H" "$RANGE" 2>/dev/null || true)

    if [ -z "$COMMIT_LIST" ]; then
        echo "[prscore] No new commits in range $RANGE."
        continue
    fi

    HIGH_RISK=0
    for commit in $COMMIT_LIST; do
        echo "[prscore] Scoring commit $commit..."
        # Run prscore; capture score from JSON output
        SCORE_JSON=$("$PRSCORE_CMD" review "$commit" --repo "$REPO_ROOT" --no-explain --json 2>/dev/null || echo '{"score":0}')
        SCORE=$(echo "$SCORE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('score',0))")
        echo "[prscore] Commit $commit scored: $SCORE/100"
        if [ "$SCORE" -ge "$RISK_THRESHOLD" ]; then
            echo "[prscore] ⚠ HIGH RISK: $commit scored $SCORE (threshold: $RISK_THRESHOLD)"
            HIGH_RISK=1
        fi
    done

    if [ "$HIGH_RISK" -eq 1 ]; then
        echo ""
        echo "[prscore] ❌ Push blocked: one or more commits exceeded the risk threshold ($RISK_THRESHOLD)."
        echo "   Run 'prscore review <commit>' for details."
        echo "   Run 'prscore decide <commit> <score> escalate' to log and force-push."
        echo "   To bypass: git push --no-verify"
        exit 1
    fi
done

echo "[prscore] ✓ All commits passed risk check. Proceeding with push."
exit 0
