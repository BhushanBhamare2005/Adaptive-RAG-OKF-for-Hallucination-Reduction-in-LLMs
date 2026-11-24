import pandas as pd

from app.core.config import settings


def get_comparison() -> dict:
    path = settings.outputs_dir / "reports" / "model_comparison.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path, index_col=0)
    return df.round(4).to_dict(orient="index")
