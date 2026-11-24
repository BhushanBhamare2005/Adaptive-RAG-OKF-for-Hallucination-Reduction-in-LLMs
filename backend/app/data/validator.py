REQUIRED_FIELDS = ("question", "answer", "evidence", "label")


def validate(record: dict) -> bool:
    return (
        all(k in record for k in REQUIRED_FIELDS)
        and isinstance(record["question"], str)
        and isinstance(record["answer"], str)
        and isinstance(record["evidence"], str)
        and record["label"] in (0, 1, False, True)
    )
