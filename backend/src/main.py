from fastapi import FastAPI

from backend.src.api.health import router as health_router

from backend.src.config.settings import settings
from backend.src.api.auth import router as auth_router
from backend.src.api.conversations import router as conversation_router
from backend.src.api.query import router as query_router
from backend.src.api.dashboard import router as dashboard_router


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(query_router)
app.include_router(dashboard_router)



@app.get("/")
async def root():
    return {
        "message": "Welcome to Vanguard Backend",
        "docs": "/docs"
    }
