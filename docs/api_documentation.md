# API Documentation

Base URL: `http://localhost:8001`. Interactive OpenAPI docs: `http://localhost:8001/docs`.

## `GET /api/health`

Returns service status, Python version, platform, and configured model directory.

## `GET /api/datasets/`

Returns normalized example totals and counts grouped by source.

## `GET /api/datasets/sample?n=5`

Returns up to 100 normalized records. `n` must be between 1 and 100. A record has `question`, `answer`, `evidence`, `label` (`0` or `1`), and `source`.

## `POST /api/experiments/train`

Trains and evaluates all three models. It saves model files, a report CSV, and confusion-matrix images to `outputs/`.

Successful response:

```json
{
  "status": "complete",
  "comparison": {
    "adaptive_okf": {
      "accuracy": 0.8,
      "precision": 0.8,
      "recall": 0.8,
      "f1": 0.8,
      "roc_auc": 0.8
    }
  }
}
```

The metric values above are illustrative. Training returns all three model entries.

## `GET /api/experiments/comparison`

Returns the saved comparison metrics, or an empty object before the first training run.

## `POST /api/analysis/`

Request:

```json
{
  "model": "adaptive_okf",
  "question": "What is the capital of France?",
  "answer": "Paris is the capital of France.",
  "evidence": "Paris is the capital and largest city of France."
}
```

The `model` must be `baseline_rag`, `self_correction`, or `adaptive_okf`. `answer` and `evidence` must be non-empty. The response includes the risk score, thresholded label, measured feature values, and a short message. A `400` response indicates the model has not yet been trained; request validation errors return `422`.