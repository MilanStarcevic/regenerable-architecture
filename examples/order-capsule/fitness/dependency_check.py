"""
Dependency Check — reference implementation.
See fitness-functions/README.md for the interface contract and tool alternatives.

Measures dependency health of Python source files.
Returns a score from 0 (healthy) to 100 (high dependency risk).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

STDLIB_MODULES = {
    "abc", "ast", "asyncio", "base64", "collections", "contextlib", "copy",
    "csv", "dataclasses", "datetime", "decimal", "enum", "functools", "hashlib",
    "heapq", "http", "inspect", "io", "itertools", "json", "logging", "math",
    "operator", "os", "pathlib", "pickle", "platform", "pprint", "queue",
    "random", "re", "shutil", "signal", "socket", "sqlite3", "string",
    "struct", "subprocess", "sys", "tempfile", "threading", "time", "typing",
    "unittest", "urllib", "uuid", "warnings", "weakref", "xml", "zipfile",
}

KNOWN_TEST_DEPS = {"pytest", "pytest_cov", "coverage", "hypothesis", "factory_boy"}

KNOWN_FITNESS_MODULES = {
    "decay_dashboard", "complexity_check", "duplication_check", "dependency_check",
    "test_confidence_check", "semantic_drift_check", "changeability_check",
}

EXEMPT_SUBDIRS = {"fitness", "fitness-functions"}

MAX_IMPORTS_PER_FILE = 10
MAX_EXTERNAL_IMPORTS_PER_FILE = 5

DISCOURAGED_DEPENDENCIES = {
    "requests",
    "pandas",
    "numpy",
    "sqlalchemy",
    "django",
    "flask",
    "fastapi",
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
    if module in STDLIB_MODULES:
        return False
    if module in KNOWN_TEST_DEPS:
        return False
    if module in KNOWN_FITNESS_MODULES:
        return False
    if module.startswith("_"):
        return False
    return True


def _is_exempt_path(f: Path) -> bool:
    return any(part in EXEMPT_SUBDIRS for part in f.parts)


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
        if _is_exempt_path(f):
            file_details.append({
                "file": str(f),
                "total_imports": len(imports),
                "external_imports": 0,
                "forbidden": [],
                "exempt": True,
            })
            all_imports.extend(imports)
            continue

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
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
