#!/usr/bin/env bash
# Demonstrates the regeneration lifecycle for the pricing-discount-capsule.
#
# This script simulates regeneration by:
# 1. Checking that durable artifacts are in place
# 2. Removing the implementation file
# 3. Regenerating from durable artifacts using Claude
# 4. Running tests to verify correctness
# 5. Running fitness functions to verify health

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CAPSULE="$REPO_ROOT/examples/pricing-discount-capsule"
IMPL="$CAPSULE/src/pricing_discount_service.py"

echo "=== Regeneration Demo: pricing-discount-capsule ==="
echo ""

echo "Step 1: Verify durable artifacts are in place"
for f in "intent.md" "regeneration-recipe.md" "ports/inbound/openapi.yaml" \
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
echo "Step 3: Regenerate implementation using Claude"
claude -p "Regenerate $IMPL for the pricing-discount-capsule.

Read these files first:
  - $CAPSULE/intent.md
  - $CAPSULE/ports/inbound/openapi.yaml
  - $CAPSULE/ports/outbound/dependencies.yaml
  - $CAPSULE/tests/test_acceptance.py
  - $CAPSULE/tests/test_invariants.py

Requirements:
  - Function signature: calculate_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict
  - Return: {\"discount_percentage\": int, \"explanation\": list[str]}
  - Implement all business rules from intent.md
  - Keep the implementation simple and explicit — no rule engines or strategy patterns
  - No external runtime dependencies beyond the Python standard library
  - All tests in tests/ must pass

Write the implementation to $IMPL. Do not add features or behavior beyond what the tests and intent.md require." \
  --allowedTools "Read,Write" \
  --output-format text
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
