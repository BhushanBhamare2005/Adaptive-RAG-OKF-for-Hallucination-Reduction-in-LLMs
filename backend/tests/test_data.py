import json

from app.data.loader import load_all_datasets
from app.data.preprocessor import clean
from app.data.validator import validate


def test_load_returns_records():
    recs = load_all_datasets()
    assert len(recs) > 0


def test_each_record_has_fields():
    for r in load_all_datasets():
        assert {"answer", "evidence", "label", "source"} <= r.keys()


def test_validator_accepts_valid():
    assert validate({"question": "q", "answer": "a", "evidence": "e", "label": 0})


def test_validator_rejects_invalid():
    assert not validate({"answer": "a"})


def test_clean_normalizes_whitespace():
    assert clean("  Hello   World  ") == "hello world"


def test_loader_normalizes_all_source_schemas(tmp_path):
    examples = {
        "qa_data.json": {
            "question": "q",
            "knowledge": "facts",
            "right_answer": "supported",
            "hallucinated_answer": "unsupported",
        },
        "dialogue_data.json": {
            "dialogue_history": "history",
            "knowledge": "facts",
            "right_response": "supported",
            "hallucinated_response": "unsupported",
        },
        "general_data.json": {
            "user_query": "q",
            "chatgpt_response": "response",
            "hallucination": "yes",
        },
        "summarization_data.json": {
            "document": "source document",
            "right_summary": "supported summary",
            "hallucinated_summary": "unsupported summary",
        },
    }
    for filename, row in examples.items():
        (tmp_path / filename).write_text(json.dumps(row) + "\n", encoding="utf-8")

    records = load_all_datasets(tmp_path)

    assert len(records) == 7
    assert {record["source"] for record in records} == {
        "qa",
        "dialogue",
        "general",
        "summarization",
    }
    assert [record["label"] for record in records if record["source"] == "qa"] == [0, 1]
    general = next(record for record in records if record["source"] == "general")
    assert general["label"] == 1
    assert general["evidence"] == ""


def test_loader_reports_invalid_jsonl_line(tmp_path):
    (tmp_path / "qa_data.json").write_text("{invalid}\n", encoding="utf-8")

    try:
        load_all_datasets(tmp_path)
    except ValueError as error:
        assert "qa_data.json:1" in str(error)
    else:
        raise AssertionError("Invalid JSONL should raise an error.")
