# routers/user.py
from ec_helpers.handlers import CustomHTTPException
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_user_service, get_db_session
from services.chat.user_service import UserService
from ..schemas.base_schemas import CreateEntityErrorResponseExample
from ..schemas.user import SignUpRequest, SignUpResponse, SignInRequest, SignInResponse
from typing import Annotated

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SignUpResponse,
    responses=CreateEntityErrorResponseExample.responses(),
)
async def signup(
    request_body: SignUpRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SignUpResponse:
    try:
        user = await user_service.signup(
            session=session,
            username=request_body.username,
            password=request_body.password,
        )
        tokens = await user_service.login(
            session=session,
            username=request_body.username,
            password=request_body.password,
        )
        return SignUpResponse(username=user.username, **tokens)
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            type="/signup_error/username_taken",
            title="Username already taken",
            details=str(e),
        )


@router.post(
    "/signin",
    status_code=status.HTTP_200_OK,
    response_model=SignInResponse,
    responses=CreateEntityErrorResponseExample.responses(),
)
async def signin(
    request_body: SignInRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> SignInResponse:
    try:
        tokens = await user_service.login(
            session=session,
            username=request_body.username,
            password=request_body.password,
        )
        return SignInResponse(**tokens)
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            type="/signin_error/invalid_credentials",
            title="Invalid credentials",
            details=str(e),
        )

