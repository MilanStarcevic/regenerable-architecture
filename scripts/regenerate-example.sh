#!/usr/bin/env bash
# Demonstrates the regeneration lifecycle for the pricing-discount-capsule.
#
# This script simulates regeneration by:
# 1. Checking that durable artifacts are in place
# 2. Removing the implementation file
# 3. Regenerating from a reference copy (in a real workflow, an AI tool would do this)
# 4. Running tests to verify correctness
# 5. Running fitness functions to verify health
#
# In a real workflow, step 3 would call an AI coding tool with the regeneration recipe.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CAPSULE="$REPO_ROOT/examples/pricing-discount-capsule"
IMPL="$CAPSULE/src/pricing_discount_service.py"

echo "=== Regeneration Demo: pricing-discount-capsule ==="
echo ""

echo "Step 1: Verify durable artifacts are in place"
for f in "intent.md" "regeneration-recipe.md" "contracts/openapi.yaml" \
          "tests/test_acceptance.py" "tests/test_invariants.py" "tests/test_contract.py"; do
    if [ -f "$CAPSULE/$f" ]; then
        echo "  [ok] $f"
    else
        echo "  [MISSING] $f — cannot regenerate safely"
        exit 1
    fi
done

echo ""
echo "Step 2: Back up and remove current implementation"
BACKUP=$(mktemp)
cp "$IMPL" "$BACKUP"
rm "$IMPL"
echo "  Implementation removed (backup at $BACKUP)"

echo ""
echo "Step 3: Regenerate implementation from durable artifacts"
echo "  (In a real workflow, an AI tool would read intent.md + tests + contract)"
echo "  (and generate the implementation. Here we restore from the reference copy.)"
cp "$BACKUP" "$IMPL"
echo "  Implementation regenerated."

echo ""
echo "Step 4: Run tests to verify correctness"
python3 -m pytest "$CAPSULE/tests/" -q --tb=short
echo "  All tests passed."

echo ""
echo "Step 5: Run fitness functions to verify health"
python3 "$CAPSULE/fitness/slop_score.py"

echo ""
echo "=== Regeneration complete ==="
