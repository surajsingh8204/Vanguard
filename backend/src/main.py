from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api.health import router as health_router

from backend.src.config.settings import settings
from backend.src.api.auth import router as auth_router
from backend.src.api.conversations import router as conversation_router
from backend.src.api.query import router as query_router
from backend.src.api.dashboard import router as dashboard_router
from backend.src.api.graph import router as graph_router
from backend.src.api.narrative import router as narrative_router
from backend.src.api.temporal import router as temporal_router
from backend.src.api.evaluation import router as evaluation_router
from backend.src.api.reports import router as reports_router


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(query_router)
app.include_router(dashboard_router)
app.include_router(graph_router)
app.include_router(narrative_router)
app.include_router(temporal_router)
app.include_router(evaluation_router)
app.include_router(reports_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Vanguard Backend",
        "docs": "/docs"
    }
