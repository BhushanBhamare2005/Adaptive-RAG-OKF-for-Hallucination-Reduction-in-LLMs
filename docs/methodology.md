# Methodology

## Task and labels

Binary classification estimates whether a generated answer is hallucinated (`1`) or grounded (`0`). The supplied QA, dialogue, and summarization sets include a correct and a hallucinated answer per source row; the loader emits both examples. The general set supplies a response and a `yes`/`no` hallucination label.

## Data normalization

The `.json` dataset files are newline-delimited JSON (JSONL), not JSON arrays.

| Dataset | Question/context | Evidence | Labels and answers |
|---|---|---|---|
| QA | `question` | `knowledge` | Emits `right_answer` as `0` and `hallucinated_answer` as `1` |
| Dialogue | `dialogue_history` | `knowledge` | Emits `right_response` as `0` and `hallucinated_response` as `1` |
| Summarization | `document` | `document` | Emits `right_summary` as `0` and `hallucinated_summary` as `1` |
| General | `user_query` | Not supplied | Emits `chatgpt_response` with the source-provided `yes`/`no` label |

For general examples, the evidence is intentionally empty; the source-provided response label is retained. The model's reported metrics therefore combine tasks with different evidence availability.

## Features

1. `evidence_overlap` — Jaccard similarity over non-stopword tokens.
2. `sequence_similarity` — character-level `SequenceMatcher` ratio.
3. `answer_length` — answer word count.
4. `has_numeric_claim` — whether the answer contains a digit.
5. `evidence_length` — evidence word count.

## Classifiers and evaluation

| Model | Classifier |
|---|---|
| `baseline_rag` | Logistic Regression |
| `self_correction` | Gradient Boosting (200 estimators) |
| `adaptive_okf` | Gradient Boosting (300 estimators, depth 4) |

The training service uses one 80/20 stratified split (`random_state=42`) for all models. It reports accuracy, precision, recall, F1, and ROC-AUC, and saves the models, a comparison CSV, and confusion matrices. Prediction uses the configurable `0.5` threshold.

This is a simple feature-based research baseline, not a generative RAG system, a fact verifier, or a calibrated confidence model. Feature importance is not represented as per-feature causal contribution in the API; the response lists the measured feature values.