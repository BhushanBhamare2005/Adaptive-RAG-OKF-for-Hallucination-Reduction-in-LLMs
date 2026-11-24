from fastapi import APIRouter, HTTPException

from app.api.schemas.request import AnalyzeRequest
from app.api.schemas.response import AnalyzeResponse
from app.services.prediction_service import predict

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse, include_in_schema=False)
@router.post("", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        return predict(req.model, req.answer, req.evidence, req.question or "")
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Model not trained. Train models from the Experiments page. ({e})",
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
