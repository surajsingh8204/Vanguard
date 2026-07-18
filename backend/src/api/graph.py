from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.services.graph_service import graph_service
from backend.src.api.utils import api_success, api_error

router = APIRouter(
    prefix="/graphs",
    tags=["Graph Intelligence"],
)


@router.get("/summary")
def graph_summary(
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(graph_service.summary()))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)


@router.get("/network")
def graph_network(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    cluster: int | None = None,
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(graph_service.network(page=page, limit=limit, cluster=cluster)))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)