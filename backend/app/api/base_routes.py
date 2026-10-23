from fastapi import APIRouter

from core.settings import settings
from utils.schemas import AuthErrorResponseExample
from .v1.routes import v1_router

api_router = APIRouter(
    prefix=settings.API_SERVICE_PREFIX,
    responses=AuthErrorResponseExample.responses()
)

api_router.include_router(
    v1_router,
    prefix="/v1",
)
