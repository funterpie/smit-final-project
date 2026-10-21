#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_ROOT="$ROOT/demo"
DEMO_DB="${PRSCORER_DEMO_DB:-$DEMO_ROOT/demo.db}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/prscore-demo.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

export AUDIT_DB_PATH="$DEMO_DB"
export GROQ_API_KEY=""
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
mkdir -p "$DEMO_ROOT/outputs" "$(dirname "$DEMO_DB")"

make_case() {
  local name="$1"
  local source_case="${2:-$name}"
  local repo="$WORK_DIR/$name"
  mkdir -p "$repo"
  cp -R "$DEMO_ROOT/cases/$source_case/." "$repo/"
  git -C "$repo" init -q
  git -C "$repo" config user.name "PR Risk Scorer Demo"
  git -C "$repo" config user.email "demo@example.invalid"
  git -C "$repo" add .
  git -C "$repo" commit -qm "demo: $name risk case"
  printf '%s\n' "$repo"
}

for name in low medium high; do
  repo="$(make_case "$name")"
  commit="$(git -C "$repo" rev-parse HEAD)"
  (
    cd "$ROOT"
    ./.venv/bin/prscore review "$commit" --repo "$repo"
  ) > "$DEMO_ROOT/outputs/$name.txt" 2>&1
  printf 'Saved real %s-case CLI output to demo/outputs/%s.txt\n' "$name" "$name"
done

low_repo="$(make_case no-close-match low)"
low_commit="$(git -C "$low_repo" rev-parse HEAD)"
(
  cd "$ROOT"
  SIMILARITY_THRESHOLD=0.9999 ./.venv/bin/prscore review "$low_commit" --repo "$low_repo"
) > "$DEMO_ROOT/outputs/no-close-match.txt" 2>&1
printf 'Saved the thresholded no-close-match output to demo/outputs/no-close-match.txt\n'
