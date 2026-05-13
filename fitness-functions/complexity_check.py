"""
Complexity Check Fitness Function

Measures structural complexity of Python source files.
High complexity in AI-generated code is a slop signal.

Metrics:
  - Functions longer than N lines
  - Files longer than N lines
  - Estimated branch count (if/elif/else/for/while/try/except)
  - Maximum nesting depth

Returns a score from 0 (healthy) to 100 (high complexity).
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field


MAX_FUNCTION_LINES = 30
MAX_FILE_LINES = 200
BRANCH_PENALTY = 2
NESTING_PENALTY = 5


@dataclass
class FileComplexity:
    path: str
    total_lines: int
    function_count: int
    long_functions: list[tuple[str, int]] = field(default_factory=list)
    branch_count: int = 0
    max_nesting: int = 0

    @property
    def score(self) -> float:
        s = 0.0
        if self.total_lines > MAX_FILE_LINES:
            s += min(30, (self.total_lines - MAX_FILE_LINES) / 10)
        for _, length in self.long_functions:
            s += min(20, (length - MAX_FUNCTION_LINES) / 3)
        s += min(25, self.branch_count * BRANCH_PENALTY)
        s += min(15, self.max_nesting * NESTING_PENALTY)
        return min(100.0, s)


class NestingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self._depth = 0
        self.branches = 0

    def _enter(self, node):
        self._depth += 1
        self.max_depth = max(self.max_depth, self._depth)
        self.generic_visit(node)
        self._depth -= 1

    def visit_If(self, node): self.branches += 1; self._enter(node)
    def visit_For(self, node): self.branches += 1; self._enter(node)
    def visit_While(self, node): self.branches += 1; self._enter(node)
    def visit_Try(self, node): self.branches += 1; self._enter(node)
    def visit_ExceptHandler(self, node): self.branches += 1; self._enter(node)
    def visit_With(self, node): self._enter(node)


def _function_line_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    if not node.body:
        return 0
    end = getattr(node, "end_lineno", None)
    if end is None:
        return 0
    return end - node.lineno


def check_file(path: Path) -> FileComplexity | None:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return None

    lines = source.splitlines()
    long_fns = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = _function_line_length(node)
            if length > MAX_FUNCTION_LINES:
                long_fns.append((node.name, length))

    fn_count = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )

    visitor = NestingVisitor()
    visitor.visit(tree)

    return FileComplexity(
        path=str(path),
        total_lines=len(lines),
        function_count=fn_count,
        long_functions=long_fns,
        branch_count=visitor.branches,
        max_nesting=visitor.max_depth,
    )


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    py_files = list(directory.rglob("*.py"))

    results = []
    for f in py_files:
        if any(part.startswith(".") for part in f.parts):
            continue
        fc = check_file(f)
        if fc is not None:
            results.append(fc)

    if not results:
        return {
            "files_checked": 0,
            "total_lines": 0,
            "long_functions": [],
            "total_branches": 0,
            "max_nesting": 0,
            "score": 0,
            "details": [],
        }

    total_lines = sum(r.total_lines for r in results)
    all_long = [(r.path, fn, ln) for r in results for fn, ln in r.long_functions]
    total_branches = sum(r.branch_count for r in results)
    max_nesting = max(r.max_nesting for r in results)
    aggregate_score = min(100, sum(r.score for r in results) / len(results))

    return {
        "files_checked": len(results),
        "total_lines": total_lines,
        "long_functions": all_long,
        "total_branches": total_branches,
        "max_nesting": max_nesting,
        "score": round(aggregate_score, 1),
        "details": [
            {
                "file": r.path,
                "lines": r.total_lines,
                "branches": r.branch_count,
                "max_nesting": r.max_nesting,
                "long_functions": r.long_functions,
                "score": round(r.score, 1),
            }
            for r in results
        ],
    }


if __name__ == "__main__":
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
