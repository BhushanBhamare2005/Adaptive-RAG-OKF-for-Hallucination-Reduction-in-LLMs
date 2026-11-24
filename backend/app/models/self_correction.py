from sklearn.ensemble import GradientBoostingClassifier


def build_model() -> GradientBoostingClassifier:
    return GradientBoostingClassifier(n_estimators=200, random_state=42)
