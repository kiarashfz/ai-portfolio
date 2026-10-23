from .controllers import (
    chat,
    users,
    portfolio,
)
from fastapi import APIRouter

v1_router = APIRouter()
v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
v1_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
v1_router.include_router(users.router, prefix="/users", tags=["User"])
