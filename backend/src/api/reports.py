from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.services.report_service import report_service
from backend.src.api.utils import api_success, api_error

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/latest")
def latest_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=1000),
    report_type: str | None = None,
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(report_service.latest(page=page, limit=limit, report_type=report_type)))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)


@router.get("/history")
def report_history(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    report_type: str | None = None,
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(report_service.history(page=page, limit=limit, report_type=report_type)))
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)


@router.get("/content")
def report_content(
    filename: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    try:
        return JSONResponse(api_success(report_service.content(filename)))
    except ValueError as exc:
        return JSONResponse(api_error(str(exc)), status_code=404)
    except Exception as exc:
        return JSONResponse(api_error(str(exc)), status_code=500)