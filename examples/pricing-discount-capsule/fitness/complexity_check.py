"""Capsule-local complexity check."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "fitness-functions"))

from complexity_check import check_directory
import json

if __name__ == "__main__":
    result = check_directory(Path(__file__).parent.parent)
    print(json.dumps(result, indent=2))
