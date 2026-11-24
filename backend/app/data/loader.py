import json
import logging
from pathlib import Path

from app.core.config import settings

log = logging.getLogger(__name__)

_FILES = ("qa_data.json", "dialogue_data.json", "general_data.json", "summarization_data.json")


def _read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as dataset_file:
        for line_number, line in enumerate(dataset_file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON in dataset: {path}:{line_number}") from error
            if not isinstance(row, dict):
                raise ValueError(f"Dataset row must be a JSON object: {path}:{line_number}")
            records.append(row)
    return records


def _record(question: str, answer: str, evidence: str, label: int, source: str) -> dict:
    return {
        "question": question.strip(),
        "answer": answer.strip(),
        "evidence": evidence.strip(),
        "label": label,
        "source": source,
    }


def _normalize(row: dict, source: str) -> list[dict]:
    if source == "qa":
        question = row["question"]
        evidence = row["knowledge"]
        return [
            _record(question, row["right_answer"], evidence, 0, source),
            _record(question, row["hallucinated_answer"], evidence, 1, source),
        ]
    if source == "dialogue":
        question = row["dialogue_history"]
        evidence = row["knowledge"]
        return [
            _record(question, row["right_response"], evidence, 0, source),
            _record(question, row["hallucinated_response"], evidence, 1, source),
        ]
    if source == "summarization":
        document = row["document"]
        return [
            _record(document, row["right_summary"], document, 0, source),
            _record(document, row["hallucinated_summary"], document, 1, source),
        ]
    if source == "general":
        label_value = str(row["hallucination"]).strip().lower()
        if label_value not in {"yes", "no"}:
            raise ValueError(f"Unexpected general-data label: {label_value!r}")
        return [
            _record(
                row["user_query"],
                row["chatgpt_response"],
                "",
                int(label_value == "yes"),
                source,
            )
        ]

    question = row["question"]
    answer = row["answer"]
    evidence = row["evidence"]
    label = row["label"]
    if label not in (0, 1, False, True):
        raise ValueError(f"Unexpected hallucination label: {label!r}")
    return [_record(question, answer, evidence, int(label), source)]


def load_all_datasets(raw_dir: Path | str | None = None) -> list[dict]:
    raw_dir = Path(raw_dir) if raw_dir else settings.data_dir / "raw"
    records = []

    for filename in _FILES:
        path = raw_dir / filename
        if not path.exists():
            log.warning("Missing dataset: %s", path)
            continue
        source = filename.removesuffix("_data.json")
        for row in _read_jsonl(path):
            records.extend(_normalize(row, source))

    return records
