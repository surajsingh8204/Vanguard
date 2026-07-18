from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.services.temporal_service import temporal_service
from backend.src.api.utils import api_success, api_error

router = APIRouter(
    prefix="/temporal",
    tags=["Temporal Intelligence"],
)


@router.get("/timeline")
def timeline(
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(temporal_service.timeline()))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)