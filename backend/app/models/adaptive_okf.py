from sklearn.ensemble import GradientBoostingClassifier


def build_model() -> GradientBoostingClassifier:
    return GradientBoostingClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
