# Architecture

```text
React + Vite dashboard
        │ HTTP / JSON (/api)
        ▼
FastAPI routes
   ├── datasets ── JSONL normalization
   ├── analysis ── feature extraction ── trained classifier
   └── experiments ── train / evaluate ── artifacts
                                         ├── outputs/models/
                                         ├── outputs/reports/
                                         └── outputs/confusion_matrices/
```

## Layers

1. **Frontend** — React pages for dashboard, answer analysis, experiments, dataset exploration, and project information.
2. **API** — FastAPI routes validate requests and expose health, data, training, comparison, and prediction operations.
3. **Data** — the loader reads newline-delimited JSON and normalizes each dataset into `{question, answer, evidence, label, source}` records.
4. **Features and models** — five deterministic answer/evidence features are passed to scikit-learn classifiers.
5. **Artifacts** — the training service saves fitted models, a metrics CSV, and confusion-matrix images beneath `outputs/`.

## Training and prediction flow

1. `POST /api/experiments/train` loads and normalizes all available source datasets.
2. A deterministic, stratified 80/20 split is created; all three models are trained and evaluated on the same held-out split.
3. Models, evaluation metrics, and confusion matrices are written to `outputs/`.
4. `POST /api/analysis/` uses the selected saved model to calculate a hallucination probability from the submitted answer and evidence.

The general-domain dataset contains no retrieved evidence. Its normalized examples keep the evidence empty rather than treating a prompt or hallucination span as evidence.