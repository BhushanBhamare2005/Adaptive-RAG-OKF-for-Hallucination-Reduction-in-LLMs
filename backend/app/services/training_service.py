import logging
import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.data.loader import load_all_datasets
from app.features.feature_extractor import extract_features
from app.models import adaptive_okf, baseline_rag, self_correction
from app.utils.metrics import compute_metrics
from app.utils.visualization import save_confusion_matrix

log = logging.getLogger(__name__)

BUILDERS = {
    "baseline_rag": baseline_rag.build_model,
    "self_correction": self_correction.build_model,
    "adaptive_okf": adaptive_okf.build_model,
}


def train_all() -> dict:
    records = load_all_datasets()
    if not records:
        raise RuntimeError("No records found in data/raw/")

    frame = pd.DataFrame(records)
    features = extract_features(frame)
    labels = frame["label"].astype(int)
    if labels.nunique() != 2:
        raise ValueError("Training requires both grounded and hallucinated examples.")

    x_train, x_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, stratify=labels, random_state=42
    )
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    report_dir = settings.outputs_dir / "reports"
    matrix_dir = settings.outputs_dir / "confusion_matrices"
    report_dir.mkdir(parents=True, exist_ok=True)
    matrix_dir.mkdir(parents=True, exist_ok=True)

    comparison = {}
    for name, builder in BUILDERS.items():
        log.info("Training %s on %d records", name, len(x_train))
        classifier = builder()
        classifier.fit(x_train, y_train)
        predictions = classifier.predict(x_test)
        probabilities = classifier.predict_proba(x_test)[:, 1]
        comparison[name] = compute_metrics(y_test, predictions, probabilities)

        model_path = settings.model_dir / f"{name}.joblib"
        joblib.dump(classifier, model_path)
        save_confusion_matrix(
            confusion_matrix(y_test, predictions),
            name,
            matrix_dir,
        )
        log.info("Saved model %s", model_path)

    pd.DataFrame.from_dict(comparison, orient="index").to_csv(
        report_dir / "model_comparison.csv"
    )
    return comparison
