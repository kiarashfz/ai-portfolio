from fastapi import FastAPI, status, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from contextlib import asynccontextmanager
from ec_logging import AccessMiddleware
from ec_helpers.handlers import CustomHTTPException, custom_http_exception_handler
from api.base_routes import api_router
from api.health.health_route import health_router
from core.settings import settings
from core.config import (
    logger,
    db_client,
    portfolio_db_client,
    redis, vector_store,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.start()
        await logger.info("startup")
        vector_store.initialize()
        yield
        await db_client.close()
        await portfolio_db_client.close()
        await logger.info("shutdown")
    except Exception:
        import traceback
        traceback.print_exc()


app = FastAPI(
    title=settings.SERVICE_NAME,
    openapi_url=f"{settings.API_SERVICE_PREFIX}/openapi.json",
    docs_url=f"{settings.API_SERVICE_PREFIX}/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def global_execution_handler(request: Request, exc: Exception):
    if settings.ENVIRONMENT == "local":
        import traceback

        print(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.add_middleware(
    ServerErrorMiddleware,
    handler=global_execution_handler,
)
app.add_middleware(
    AccessMiddleware,
    logger=logger,
    forbidden_events=["", "docs", "openapi.json"],
)

app.include_router(api_router)
app.include_router(health_router, tags=["Health"])

app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)

