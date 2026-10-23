from ec_helpers.handlers import CustomHTTPException
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from core.dependencies import (
    get_db_session,
    get_portfolio_service,
    get_rag_service,
    get_user_service,
)
from services.portfolio.portfolio_service import PortfolioService
from services.chat.rag_service import RAGService
from services.chat.user_service import UserService
from db.models import User
from ..schemas.portfolio import UpsertPortfolioRequest, UpsertPortfolioResponse, PortfolioResponse

router = APIRouter()
bearer = HTTPBearer()


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
        user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    try:
        payload = user_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject")
    except Exception:
        raise CustomHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            type="/auth_error/invalid_token",
            title="Invalid or expired token",
            details="Please sign in again.",
        )

    user = await user_service.get_by_id(session=session, user_id=user_id)
    if not user:
        raise CustomHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            type="/auth_error/user_not_found",
            title="User not found",
            details="Token is valid but user no longer exists.",
        )
    return user


@router.patch(
    "/me/portfolio",
    status_code=status.HTTP_200_OK,
    response_model=UpsertPortfolioResponse,
    summary="Create or update the authenticated user's portfolio",
)
async def upsert_portfolio(
        request_body: UpsertPortfolioRequest,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)],
        rag_service: Annotated[RAGService, Depends(get_rag_service)],
) -> UpsertPortfolioResponse:
    try:
        existing = await portfolio_service.get_by_user_id(
            session=session,
            user_id=current_user.id,
        )

        profile_data = {
            "skills": request_body.skills,
            "experiences": [e.model_dump() for e in request_body.experiences],
            "education": [e.model_dump() for e in request_body.education],
            "links": request_body.links.model_dump(),
        }

        if existing:
            portfolio = await portfolio_service.update_portfolio(
                session=session,
                portfolio=existing,
                first_name=request_body.first_name,
                last_name=request_body.last_name,
                title=request_body.title,
                summary=request_body.summary,
                profile_data=profile_data,
            )
            created = False
        else:
            portfolio = await portfolio_service.create_portfolio(
                session=session,
                user_id=current_user.id,
                first_name=request_body.first_name,
                last_name=request_body.last_name,
                title=request_body.title,
                summary=request_body.summary,
                profile_data=profile_data,
            )
            created = True

        rag_result = await rag_service.ingest_portfolio_data(
            portfolio_id=portfolio.id,
            portfolio_data=profile_data,
        )

        await session.commit()

        return UpsertPortfolioResponse(
            username=current_user.username,
            portfolio_url=f"portfoliogpt.com/{current_user.username}",
            chunks_ingested=rag_result["vectors_upserted"],
            created=created,
        )

    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            type="/portfolio_error/upsert_failed",
            title="Portfolio upsert failed",
            details=str(e),
        )


@router.get(
    "/me/portfolio",
    status_code=status.HTTP_200_OK,
    response_model=PortfolioResponse,
    summary="Get portfolio by me",
)
async def get_portfolio(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PortfolioResponse:
    try:
        portfolio = await portfolio_service.get_by_user_id(session, current_user.id)
        if not portfolio:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                type="/portfolio_error/not_found",
                title="Portfolio not found",
                details=f"No portfolio found for '{current_user.username}'.",
            )

        return PortfolioResponse(
            username=portfolio.user.username,
            first_name=portfolio.first_name,
            last_name=portfolio.last_name,
            title=portfolio.title,
            summary=portfolio.summary,
            profile_data=portfolio.profile_data,
        )
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            type="/portfolio_error/retrieval_failed",
            title="Portfolio retrieval failed",
            details=str(e),
        )


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=PortfolioResponse,
    summary="Get a public portfolio by username",
)
async def get_public_portfolio(
        username: str,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PortfolioResponse:
    try:
        portfolio = await portfolio_service.get_by_username(session, username.lower())
        if not portfolio:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                type="/portfolio_error/not_found",
                title="Portfolio not found",
                details=f"No portfolio found for '{username}'.",
            )

        return PortfolioResponse(
            username=portfolio.user.username,
            first_name=portfolio.first_name,
            last_name=portfolio.last_name,
            title=portfolio.title,
            summary=portfolio.summary,
            profile_data=portfolio.profile_data,
        )
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            type="/portfolio_error/retrieval_failed",
            title="Portfolio retrieval failed",
            details=str(e),
        )
