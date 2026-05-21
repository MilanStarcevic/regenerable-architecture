"""
Semantic Drift Check — reference implementation.
See fitness-functions/README.md for the interface contract.
See fitness-functions/prompts/semantic-drift.md for the versioned evaluation prompt.

This check runs at the pre-regeneration gate, not on every commit. It determines whether
the implementation has behaviorally diverged from the declared intent in intent.md.

Two execution paths are provided:

  1. LLM-judged (primary): loads the versioned prompt from
     fitness-functions/prompts/semantic-drift.md, submits it to an LLM with intent.md
     and the implementation source as inputs, and parses the structured JSON response.

  2. Heuristic fallback (secondary): uses vocabulary matching and invariant pattern checks
     as a coarse proxy. This path is provided so make fitness runs in CI without LLM
     credentials. It is explicitly marked as a fallback in the output.

Configure the LLM path by implementing the call_llm function below. The default raises
NotImplementedError to make the absence of configuration visible rather than silent.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

INTENT_FILENAME = "intent.md"

# Path to the versioned prompt, resolved relative to this file's repo root.
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
PROMPT_PATH = _REPO_ROOT / "fitness-functions" / "prompts" / "semantic-drift.md"


# ---------------------------------------------------------------------------
# LLM abstraction layer
# ---------------------------------------------------------------------------

def call_llm(prompt_and_context: str) -> str:
    """Submit a prompt to an LLM and return the raw text response.

    Replace this function with a real implementation for your LLM provider.
    The function receives the complete prompt text (system instructions +
    delimited inputs) and must return a string containing only the JSON output
    described in fitness-functions/prompts/semantic-drift.md.

    Example implementations:
      - Anthropic: anthropic.Anthropic().messages.create(...)
      - OpenAI: openai.OpenAI().chat.completions.create(...)
      - Any provider that accepts a text prompt and returns text

    Raises:
        NotImplementedError: when no LLM provider has been configured.
    """
    raise NotImplementedError(
        "No LLM provider configured. Implement call_llm() in semantic_drift_check.py "
        "or set the USE_HEURISTIC_FALLBACK flag to run without an LLM."
    )


# Set to True to always use the heuristic fallback (for CI without LLM credentials).
USE_HEURISTIC_FALLBACK = True


# ---------------------------------------------------------------------------
# LLM-judged path
# ---------------------------------------------------------------------------

def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except OSError as e:
        raise FileNotFoundError(
            f"Semantic drift prompt not found at {PROMPT_PATH}. "
            "Ensure fitness-functions/prompts/semantic-drift.md exists."
        ) from e


def _build_context(directory: Path) -> tuple[str | None, str]:
    """Return (intent_text_or_None, implementation_source)."""
    intent_path = None
    for candidate in [directory / INTENT_FILENAME] + list(directory.rglob(INTENT_FILENAME)):
        if candidate.exists():
            intent_path = candidate
            break

    intent_text = intent_path.read_text(encoding="utf-8") if intent_path else None

    source_parts: list[str] = []
    for f in directory.rglob("*.py"):
        if any(part.startswith(".") for part in f.parts):
            continue
        if any(part in {"fitness", "tests"} for part in f.parts):
            continue
        try:
            source_parts.append(f"# --- {f.name} ---\n" + f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            pass

    return intent_text, "\n\n".join(source_parts)


def _status_from_llm_result(parsed: dict) -> str:
    if not parsed.get("drift_detected", False):
        return "healthy"
    rules = parsed.get("drifted_rules", [])
    severities = {r.get("severity", "minor") for r in rules}
    if "severe" in severities:
        return "critical"
    if "moderate" in severities:
        return "warning"
    return "watch"


def check_directory_llm(directory: str | Path) -> dict:
    """LLM-judged semantic drift check.

    Submits intent.md and the implementation source to an LLM using the
    versioned prompt in fitness-functions/prompts/semantic-drift.md. Parses
    the structured JSON response and converts it to a signal status.

    Fails loudly on malformed JSON — a malformed response is itself a signal.
    """
    directory = Path(directory)
    prompt_text = _load_prompt()
    intent_text, impl_source = _build_context(directory)

    if intent_text is None:
        return {
            "method": "llm",
            "error": "intent.md not found; cannot evaluate semantic drift",
            "score": 50.0,
            "status": "watch",
        }

    full_prompt = (
        prompt_text
        + "\n\n---\n\n"
        + "<intent>\n" + intent_text + "\n</intent>\n\n"
        + "<implementation>\n" + impl_source + "\n</implementation>"
    )

    raw_response = call_llm(full_prompt)

    # Parse response — fail loudly on malformed JSON.
    try:
        parsed = json.loads(raw_response.strip())
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM returned malformed JSON. This is itself a signal that something is wrong.\n"
            f"Raw response:\n{raw_response}\n\nJSON error: {e}"
        ) from e

    status = _status_from_llm_result(parsed)

    score_map = {"healthy": 0.0, "watch": 15.0, "warning": 45.0, "critical": 80.0}
    score = score_map.get(status, 50.0)

    return {
        "method": "llm",
        "prompt_version": "1.0",
        "drift_detected": parsed.get("drift_detected", False),
        "drifted_rules": parsed.get("drifted_rules", []),
        "overall_confidence": parsed.get("overall_confidence", ""),
        "rationale": parsed.get("rationale", ""),
        "status": status,
        "score": score,
    }


# ---------------------------------------------------------------------------
# Heuristic fallback (vocabulary and invariant matching)
# ---------------------------------------------------------------------------

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


def check_directory_heuristic(directory: str | Path) -> dict:
    """Heuristic vocabulary-based semantic drift check.

    This is a coarse proxy for semantic drift, provided so the check can run
    in CI without LLM credentials. It catches obvious vocabulary divergence but
    misses subtle behavioral reinterpretation of business rules.

    For pre-regeneration gate evaluation, use check_directory_llm instead.
    """
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
            "method": "heuristic",
            "intent_found": intent_path is not None,
            "domain_terms_checked": 0,
            "missing_terms": [],
            "invariants_covered": False,
            "score": 50.0,
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
        "method": "heuristic",
        "intent_found": intent_path is not None,
        "intent_path": str(intent_path) if intent_path else None,
        "domain_terms_checked": len(domain_terms),
        "terms_present": present_count,
        "missing_terms": missing_terms,
        "term_coverage": round(term_coverage, 3),
        "invariants_covered": invariants_covered,
        "score": round(min(100.0, score), 1),
    }


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def check_directory(directory: str | Path) -> dict:
    """Run semantic drift check.

    Uses the LLM-judged path when USE_HEURISTIC_FALLBACK is False and an LLM
    provider is configured. Falls back to heuristic vocabulary matching when
    USE_HEURISTIC_FALLBACK is True.

    At the pre-regeneration gate, use check_directory_llm directly to ensure
    the full LLM-judged evaluation runs.
    """
    if not USE_HEURISTIC_FALLBACK:
        return check_directory_llm(directory)
    return check_directory_heuristic(directory)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    use_llm = "--llm" in sys.argv
    if use_llm:
        result = check_directory_llm(target)
    else:
        result = check_directory_heuristic(target)
    print(json.dumps(result, indent=2))
    if result.get("score", 0) > 70:
        sys.exit(1)
