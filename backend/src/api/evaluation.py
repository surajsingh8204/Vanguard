from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.services.evaluation_service import evaluation_service
from backend.src.api.utils import api_success, api_error

router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)


@router.get("/summary")
def evaluation_summary(
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(evaluation_service.summary()))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)