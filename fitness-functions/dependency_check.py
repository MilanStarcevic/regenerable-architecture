"""
Dependency Check Fitness Function

Measures dependency health of Python source files.
Dependency accumulation in AI-generated code is a slop signal:
the model imports libraries freely, often for single-use convenience.

Metrics:
  - Total import count
  - External (non-standard-library) import count
  - Presence of forbidden/unexpected dependencies
  - Dependency growth risk (imports per file)

Returns a score from 0 (healthy) to 100 (high dependency risk).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

# Python standard library top-level module names (curated subset, not exhaustive)
STDLIB_MODULES = {
    "abc", "ast", "asyncio", "base64", "collections", "contextlib", "copy",
    "csv", "dataclasses", "datetime", "decimal", "enum", "functools", "hashlib",
    "heapq", "http", "inspect", "io", "itertools", "json", "logging", "math",
    "operator", "os", "pathlib", "pickle", "platform", "pprint", "queue",
    "random", "re", "shutil", "signal", "socket", "sqlite3", "string",
    "struct", "subprocess", "sys", "tempfile", "threading", "time", "typing",
    "unittest", "urllib", "uuid", "warnings", "weakref", "xml", "zipfile",
}

# Thresholds
MAX_IMPORTS_PER_FILE = 10
MAX_EXTERNAL_IMPORTS_PER_FILE = 5

# Dependencies that should not appear in a capsule without explicit justification
DISCOURAGED_DEPENDENCIES = {
    "requests",    # heavyweight HTTP; prefer httpx or stdlib urllib
    "pandas",      # rarely needed in a capsule implementation
    "numpy",       # same
    "sqlalchemy",  # capsules should call domain APIs, not own databases
    "django",      # framework; should not appear in capsule logic
    "flask",       # same
    "fastapi",     # same
}


def _get_imports(tree: ast.AST) -> list[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return imports


def _is_external(module: str) -> bool:
    return module not in STDLIB_MODULES and not module.startswith("_")


def check_directory(directory: str | Path, forbidden: set[str] | None = None) -> dict:
    directory = Path(directory)
    if forbidden is None:
        forbidden = DISCOURAGED_DEPENDENCIES

    py_files = [
        f for f in directory.rglob("*.py")
        if not any(part.startswith(".") for part in f.parts)
    ]

    all_imports: list[str] = []
    external_imports: list[str] = []
    forbidden_found: list[str] = []
    file_details: list[dict] = []

    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(f))
        except (OSError, SyntaxError):
            continue

        imports = _get_imports(tree)
        external = [i for i in imports if _is_external(i)]
        bad = [i for i in external if i in forbidden]

        all_imports.extend(imports)
        external_imports.extend(external)
        forbidden_found.extend(bad)

        file_details.append({
            "file": str(f),
            "total_imports": len(imports),
            "external_imports": len(external),
            "forbidden": bad,
        })

    if not file_details:
        return {"files_checked": 0, "total_imports": 0, "external_imports": 0, "forbidden": [], "score": 0}

    avg_imports = len(all_imports) / len(file_details)
    avg_external = len(external_imports) / len(file_details)

    score = 0.0
    score += min(30, (avg_imports / MAX_IMPORTS_PER_FILE) * 30)
    score += min(40, (avg_external / max(MAX_EXTERNAL_IMPORTS_PER_FILE, 1)) * 40)
    score += min(30, len(set(forbidden_found)) * 10)

    return {
        "files_checked": len(file_details),
        "total_imports": len(all_imports),
        "external_imports": len(set(external_imports)),
        "forbidden_found": list(set(forbidden_found)),
        "avg_imports_per_file": round(avg_imports, 1),
        "score": round(min(100.0, score), 1),
        "details": file_details,
    }


if __name__ == "__main__":
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
