from ec_helpers.handlers import CustomHTTPException
from fastapi import APIRouter, Depends, status
from services.chat import AIChatService
from core.dependencies import (
    get_ai_chat_service,
    get_db_session,
    get_portfolio_service,
)
from sqlalchemy.ext.asyncio import AsyncSession

from services.portfolio.portfolio_service import PortfolioService
from ..schemas.ai_chat import (
    AIChatResponse,
    AIChatRequest,
)
from ..schemas.base_schemas import (
    CreateEntityErrorResponseExample,
)
from typing import Annotated
from uuid import UUID

router = APIRouter()


import uuid
from fastapi import Request

async def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    return UUID(session_id)


@router.post(
    "/{portfolio_username}/chat",
    status_code=status.HTTP_201_CREATED,
    response_model=AIChatResponse,
    responses=CreateEntityErrorResponseExample.responses()
)
async def ai_chat(
        portfolio_username: str,
        request_body: AIChatRequest,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)],
        ai_chat_service: Annotated[AIChatService, Depends(get_ai_chat_service)],
        session_id: Annotated[
            UUID,
            Depends(get_session_id),
        ],
):
    try:
        portfolio_username = portfolio_username.lower()
        portfolio = await portfolio_service.get_by_username(session, portfolio_username)
        if portfolio is None:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )

        answer: str = await ai_chat_service.chat(
            session=session,
            session_id=session_id,
            user_message=request_body.message,
            portfolio=portfolio,
        )
        await session.commit()
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            type="/create_error/ai_chat",
            title="Error",
            details=str(e.args[0]),
        )

    return AIChatResponse(
        message=answer,
    )
