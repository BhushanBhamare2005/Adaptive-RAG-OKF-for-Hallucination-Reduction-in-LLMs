import re
from difflib import SequenceMatcher

STOPWORDS = {
    "the", "is", "a", "an", "of", "in", "to", "and", "or", "was", "were",
    "by", "on", "at", "for", "with", "as", "be", "been", "being", "this",
    "that", "these", "those", "it", "its",
}


def _tokens(text: str) -> set:
    if not text:
        return set()
    return {w for w in re.findall(r"\b\w+\b", text.lower()) if w not in STOPWORDS}


def evidence_overlap(answer: str, evidence: str) -> float:
    """Jaccard overlap between answer and evidence content tokens."""
    a, e = _tokens(answer), _tokens(evidence)
    if not a or not e:
        return 0.0
    return len(a & e) / len(a | e)


def sequence_similarity(answer: str, evidence: str) -> float:
    """Character-level similarity between answer and evidence."""
    if not answer or not evidence:
        return 0.0
    return SequenceMatcher(None, answer.lower(), evidence.lower()).ratio()


def answer_length(answer: str) -> int:
    return len((answer or "").split())


def has_numeric_claim(answer: str) -> int:
    return int(bool(re.search(r"\d", answer or "")))
