"""
Capsule-local slop score runner.

Runs the main fitness functions against this capsule directory.
"""

import sys
from pathlib import Path

# Point at the repo-level fitness-functions directory
REPO_ROOT = Path(__file__).parent.parent.parent.parent
CAPSULE_DIR = Path(__file__).parent.parent

sys.path.insert(0, str(REPO_ROOT / "fitness-functions"))

from slop_score import compute_slop_score
import json

if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = compute_slop_score(CAPSULE_DIR, verbose=verbose)
    print(json.dumps(result, indent=2))
    if result["slop_score"] >= 71:
        sys.exit(1)
