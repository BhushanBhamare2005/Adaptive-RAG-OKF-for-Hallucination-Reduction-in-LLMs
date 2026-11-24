from fastapi import APIRouter, HTTPException
import joblib
import numpy as np

from app.core.config import settings
from app.features.feature_extractor import FEATURE_NAMES, extract_single

router = APIRouter()


@router.get("/models")
def models():
    return {"models": [
        {"name": "baseline_rag", "explainer": "model_native"},
        {"name": "self_correction", "explainer": "model_native"},
        {"name": "adaptive_okf", "explainer": "model_native"},
    ]}


@router.post("/models/{model_name}/prediction")
def explain_prediction(model_name: str, answer: str, evidence: str):
    path = settings.model_dir / f"{model_name}.joblib"
    if not path.exists():
        raise HTTPException(status_code=400, detail="Model has not been trained.")
    classifier = joblib.load(path)
    frame = extract_single(answer, evidence)
    try:
        import shap
        explainer = shap.Explainer(classifier)
        shap_values = explainer(frame)
        values = np.asarray(shap_values.values[0])
        if values.ndim > 1:
            values = values[:, 1] if values.shape[1] > 1 else values[:, 0]
        explanations = [{
            "feature": name,
            "value": float(frame.iloc[0][name]),
            "contribution": float(value),
        } for name, value in zip(FEATURE_NAMES, values)]
        explanations.sort(key=lambda item: abs(item["contribution"]), reverse=True)
        return {
            "available": True,
            "method": "shap",
            "probability": float(classifier.predict_proba(frame)[0, 1]),
            "explanations": explanations,
        }
    except Exception:
        pass
    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_
        method = "feature_importances"
    elif hasattr(classifier, "coef_"):
        importances = np.asarray(classifier.coef_[0])
        method = "linear_coefficients"
    else:
        return {"available": False, "reason": "The loaded model does not expose a supported native explainer."}
    explanations = [{
        "feature": name,
        "value": float(frame.iloc[0][name]),
        "contribution": float(value * frame.iloc[0][name]),
    } for name, value in zip(FEATURE_NAMES, importances)]
    explanations.sort(key=lambda item: abs(item["contribution"]), reverse=True)
    return {
        "available": True,
        "method": method,
        "probability": float(classifier.predict_proba(frame)[0, 1]),
        "explanations": explanations,
    }
