from app.features.feature_extractor import FEATURE_NAMES, _row_features


def test_feature_count():
    f = _row_features("Paris is the capital of France.", "Paris is the capital of France.")
    assert len(f) == len(FEATURE_NAMES)


def test_identical_texts_high_overlap():
    f = _row_features("Paris is the capital of France.", "Paris is the capital of France.")
    assert f[0] > 0.9  # evidence_overlap
    assert f[1] > 0.9  # sequence_similarity


def test_numeric_detection():
    f = _row_features("The tower is 300 meters tall.", "The tower is 300 meters tall.")
    assert f[3] == 1.0


def test_empty_inputs_safe():
    f = _row_features("", "")
    assert len(f) == len(FEATURE_NAMES)
