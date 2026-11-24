import logging
from typing import Dict

import joblib

from app.api.schemas.response import AnalyzeResponse, FeatureContribution
from app.core.config import settings
from app.features.feature_extractor import FEATURE_NAMES, extract_single

log = logging.getLogger(__name__)

_MODEL_NAMES = {"baseline_rag", "self_correction", "adaptive_okf"}
_cache: Dict[str, object] = {}


def _load(model_name: str):
    if model_name not in _MODEL_NAMES:
        raise ValueError(f"Unknown model: {model_name}")
    if model_name in _cache:
        return _cache[model_name]
    path = settings.model_dir / f"{model_name}.joblib"
    if not path.exists():
        raise FileNotFoundError(str(path))
    clf = joblib.load(path)
    _cache[model_name] = clf
    log.info("Loaded model %s from %s", model_name, path)
    return clf


def clear_model_cache() -> None:
    _cache.clear()


def predict(
    model: str,
    answer: str,
    evidence: str,
    question: str = "",
) -> AnalyzeResponse:
    del question
    clf = _load(model)
    X = extract_single(answer, evidence)
    proba = float(clf.predict_proba(X)[0, 1])
    label = bool(proba >= settings.threshold)
    feats = [
        FeatureContribution(name=n, value=float(v))
        for n, v in zip(FEATURE_NAMES, X.iloc[0])
    ]
    msg = "Likely hallucinated" if label else "Likely grounded in evidence"
    return AnalyzeResponse(
        model=model,
        risk_score=round(proba, 4),
        hallucinated=label,
        features=feats,
        message=msg,
    )
