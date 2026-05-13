"""
Semantic Drift Check — reference implementation.
See fitness-functions/README.md for the interface contract and tool alternatives.

Measures alignment between implementation vocabulary and intent.md.
Returns a score from 0 (no detected drift) to 100 (high detected drift).

This is a heuristic. Real semantic drift detection at scale requires:
  - Spec-to-test traceability matrices
  - LLM-assisted review comparing intent.md to implementation behavior
  - Production behavior comparison against golden masters
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

INTENT_FILENAME = "intent.md"

INVARIANT_PATTERNS = [
    r"max.*discount|discount.*max|cap|maximum",
    r"negative|non.negative|\bge\b|\bgt\b|>=\s*0",
    r"explanation|explain",
]

FALLBACK_DOMAIN_TERMS = [
    "discount", "customer", "tier", "basket", "campaign", "explanation", "maximum",
]

_NARRATIVE_STOPWORDS = {
    "that", "this", "with", "from", "have", "must", "will", "should",
    "when", "into", "over", "been", "than", "then", "they", "their",
    "more", "also", "each", "only", "just", "same", "some", "such",
    "very", "well", "even", "most", "about", "apply", "applied",
    "allow", "reward", "never", "always", "encourage", "protect", "survive",
    "activate", "ensure", "require", "across",
    "boost", "boosts", "complete", "eligible", "readable", "higher", "larger",
    "ongoing", "facing", "display", "dispute", "resolution", "recognition",
    "purchases", "records", "catalog", "consumed", "domain", "trails", "writing",
    "temporary", "relationship", "incentive", "margin", "audit", "configuration",
    "does", "orders", "product", "products", "human",
}


def _extract_domain_terms(intent_path: Path) -> list[str]:
    """Extract code-relevant domain terms from intent.md.

    Only uses specification-style lines (table rows, lines with explicit values,
    headings) to avoid false positives from narrative motivational text.
    """
    try:
        content = intent_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return FALLBACK_DOMAIN_TERMS

    terms: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        is_table_row = "|" in stripped and not stripped.startswith("#")
        has_explicit_value = bool(re.search(r"\d+%|\btier\b|\bgold\b|\bsilver\b|`[^`]+`", stripped, re.IGNORECASE))
        is_heading = stripped.startswith("#") and len(stripped) < 60

        if not (is_table_row or has_explicit_value or is_heading):
            continue

        words = re.findall(r"\b[a-z][a-z0-9]{3,}\b", stripped.lower())
        for w in words:
            if w not in _NARRATIVE_STOPWORDS and not w.isdigit() and len(w) <= 14:
                terms.add(w)

    return list(terms) if len(terms) >= 3 else FALLBACK_DOMAIN_TERMS


def _read_python_sources(directory: Path) -> str:
    content_parts = []
    for f in directory.rglob("*.py"):
        if any(part.startswith(".") for part in f.parts):
            continue
        try:
            content_parts.append(f.read_text(encoding="utf-8").lower())
        except (OSError, UnicodeDecodeError):
            pass
    return "\n".join(content_parts)


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)

    intent_path = None
    for candidate in [directory / INTENT_FILENAME] + list(directory.rglob(INTENT_FILENAME)):
        if candidate.exists():
            intent_path = candidate
            break

    domain_terms = _extract_domain_terms(intent_path) if intent_path else FALLBACK_DOMAIN_TERMS
    source_content = _read_python_sources(directory)

    if not source_content:
        return {
            "intent_found": intent_path is not None,
            "domain_terms_checked": 0,
            "missing_terms": [],
            "invariants_covered": False,
            "score": 50,
            "note": "No Python source files found",
        }

    missing_terms = [t for t in domain_terms if t not in source_content]
    present_count = len(domain_terms) - len(missing_terms)
    term_coverage = present_count / max(len(domain_terms), 1)

    invariants_covered = all(
        re.search(pattern, source_content, re.IGNORECASE)
        for pattern in INVARIANT_PATTERNS
    )

    score = 0.0
    missing_ratio = len(missing_terms) / max(len(domain_terms), 1)
    score += missing_ratio * 60

    if not invariants_covered:
        score += 40

    if intent_path is None:
        score = min(100, score + 20)

    return {
        "intent_found": intent_path is not None,
        "intent_path": str(intent_path) if intent_path else None,
        "domain_terms_checked": len(domain_terms),
        "terms_present": present_count,
        "missing_terms": missing_terms,
        "term_coverage": round(term_coverage, 3),
        "invariants_covered": invariants_covered,
        "score": round(min(100.0, score), 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
