from fastapi import APIRouter, status
from fastapi.responses import JSONResponse


health_router = APIRouter()


@health_router.get("/live")
async def live():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "ok"})


@health_router.get("/ready")
async def ready():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "ok"})
