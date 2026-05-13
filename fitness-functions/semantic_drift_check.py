"""
Semantic Drift Check Fitness Function

Measures alignment between the implementation/tests and the business intent
declared in intent.md.

Semantic drift occurs when code still passes tests but no longer represents
the business intent it was created to fulfill. Domain terms have been renamed,
business rules have been reinterpreted, and the logic drifted from the spec.

Heuristic approach for this demo:
  - Extract key domain terms from intent.md
  - Check that those terms appear in implementation and test files
  - Check that critical invariants (max discount, non-negative) are tested
  - Check that explanation behavior is tested

IMPORTANT: This is a heuristic. Real semantic drift detection at scale requires:
  - Spec-to-test traceability matrices
  - Requirements coverage metrics
  - Formal invariant specifications
  - LLM-assisted review with human approval gates
  - Production behavior comparison against golden masters

Returns a score from 0 (no detected drift) to 100 (high detected drift).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

INTENT_FILENAME = "intent.md"

# Patterns indicating strong behavioral test coverage (good signal, reduces drift)
INVARIANT_PATTERNS = [
    r"max.*discount|discount.*max|cap|maximum",
    r"negative|non.negative|\bge\b|\bgt\b|>=\s*0",
    r"explanation|explain",
]

# If no intent.md is found, use these as fallback domain terms for the demo capsule
FALLBACK_DOMAIN_TERMS = [
    "discount",
    "customer",
    "tier",
    "basket",
    "campaign",
    "explanation",
    "maximum",
]


def _extract_domain_terms(intent_path: Path) -> list[str]:
    """Extract likely domain terms from an intent.md file."""
    try:
        content = intent_path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return FALLBACK_DOMAIN_TERMS

    # Extract words from bullet points and headers — likely to be domain terms
    terms = set()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "#")) or line.startswith(("reward", "encourage", "allow", "never", "always")):
            words = re.findall(r"\b[a-z]{4,}\b", line)
            terms.update(w for w in words if w not in {
                "that", "this", "with", "from", "have", "must", "will",
                "should", "when", "into", "over", "been", "than", "then",
                "they", "their", "more", "also", "each", "only", "just",
                "same", "some", "such", "very", "well", "even", "most",
                "about", "apply", "applied",
            })
    return list(terms) if terms else FALLBACK_DOMAIN_TERMS


def _read_python_sources(directory: Path) -> str:
    """Concatenate all Python source and test files for term searching."""
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

    # Find intent.md
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

    # Check domain term presence
    missing_terms = [t for t in domain_terms if t not in source_content]
    present_count = len(domain_terms) - len(missing_terms)
    term_coverage = present_count / max(len(domain_terms), 1)

    # Check invariant patterns
    invariants_covered = all(
        re.search(pattern, source_content, re.IGNORECASE)
        for pattern in INVARIANT_PATTERNS
    )

    # Score: 0 = no drift, 100 = high drift
    score = 0.0

    # Missing terms penalty (up to 60)
    missing_ratio = len(missing_terms) / max(len(domain_terms), 1)
    score += missing_ratio * 60

    # Missing invariant coverage (up to 40)
    if not invariants_covered:
        score += 40

    # Bonus: intent.md not found is a drift signal
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
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
