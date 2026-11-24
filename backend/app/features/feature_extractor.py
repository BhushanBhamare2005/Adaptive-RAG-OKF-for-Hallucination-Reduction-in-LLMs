import pandas as pd

from app.features.evidence_features import (
    answer_length,
    evidence_overlap,
    has_numeric_claim,
    sequence_similarity,
)

FEATURE_NAMES = [
    "evidence_overlap",
    "sequence_similarity",
    "answer_length",
    "has_numeric_claim",
    "evidence_length",
]


def _row_features(answer: str, evidence: str) -> list:
    answer = answer or ""
    evidence = evidence or ""
    return [
        evidence_overlap(answer, evidence),
        sequence_similarity(answer, evidence),
        float(answer_length(answer)),
        float(has_numeric_claim(answer)),
        float(len(evidence.split())),
    ]


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    rows = [_row_features(r["answer"], r["evidence"]) for _, r in df.iterrows()]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)


def extract_single(answer: str, evidence: str) -> pd.DataFrame:
    return pd.DataFrame([_row_features(answer, evidence)], columns=FEATURE_NAMES)
