from fastapi import APIRouter, HTTPException

from app.services.evaluation_service import get_comparison
from app.services.prediction_service import clear_model_cache
from app.services.training_service import train_all

router = APIRouter()


@router.get("/comparison")
def comparison():
    return get_comparison()


@router.post("/train")
def train():
    try:
        comparison_result = train_all()
        clear_model_cache()
        return {"status": "complete", "comparison": comparison_result}
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
