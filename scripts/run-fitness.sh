#!/usr/bin/env bash
# Run fitness functions against a capsule directory.
# Usage: ./scripts/run-fitness.sh [capsule-directory]
# Default: examples/pricing-discount-capsule

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET="${1:-$REPO_ROOT/examples/pricing-discount-capsule}"

echo "Running fitness functions against: $TARGET"
echo "---"

python3 "$TARGET/fitness/entropy_score.py"
