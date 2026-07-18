from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.services.narrative_service import narrative_service
from backend.src.api.utils import api_success, api_error

router = APIRouter(
    prefix="/narrative",
    tags=["Narrative Intelligence"],
)


@router.get("/summary")
def narrative_summary(
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(narrative_service.summary()))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)


@router.get("/clusters")
def narrative_clusters(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=1000),
    cluster: str | None = None,
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(narrative_service.clusters(page=page, limit=limit, cluster=cluster)))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)