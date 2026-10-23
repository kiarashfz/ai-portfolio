from .config import (
    logger,
    db_client,
    portfolio_db_client,
    redis,
    minio_service,
    file_service,
    message_service,
    ai_chat_service,
    portfolio_service,
    rag_service,
    user_service,
)


async def get_logger():
    return logger


async def get_db_session():
    async with portfolio_db_client.async_session_maker() as session:
        yield session


async def get_redis():
    return redis


async def get_minio_service():
    return minio_service


async def get_file_service():
    return file_service


async def get_message_service():
    return message_service

async def get_ai_chat_service():
    return ai_chat_service

async def get_portfolio_service():
    return portfolio_service

async def get_rag_service():
    return rag_service


async def get_user_service():
    return user_service