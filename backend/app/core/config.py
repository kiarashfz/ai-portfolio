from ec_logging import AsyncLogger
from ec_searchia.client import SearchiaClient

from services.chat.message_service import MessageService
from services.chat.rag_service import RAGService
from services.chat.user_service import UserService
from services.external.ai.client import AIClient
from services.external.vector_db import MilvusVectorStore
from services.external.embeddings.embeddings_client import EmbeddingsClient
from services.portfolio.portfolio_service import PortfolioService
from .settings import settings
from ec_postgres import PostgresClient
from ec_redis import RedisClient
from services import (
    MinioService,
    FileService,
)
from services.chat import (
    AIChatService,
)

logger = AsyncLogger(
    service=settings.SERVICE_NAME,
    environment=settings.ENVIRONMENT,
    container_name=settings.CONTAINER_ID,
    worker_id=settings.WORKER_ID,
    http=settings.LOGGER_HTTP_ENABLED,
    console=settings.LOGGER_CONSOLE_ENABLED,
    http_endpoint=settings.FLUENTBIT_ENDPOINT,
)


redis = RedisClient(
    nodes=(
        settings.REDIS_URL
        if settings.ENVIRONMENT == "local"
        else settings.redis_startup_nodes
    ),
    username=settings.REDIS_USER,
    password=settings.REDIS_PASSWORD,
    prefix=settings.REDIS_PREFIX,
    logger=logger,
)

db_client = PostgresClient(
    url=settings.postgres_url,
    echo=False,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=30.0,
    pool_pre_ping=True,
)

portfolio_db_client = PostgresClient(
    url=settings.postgres_db_url,
    echo=True,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=30.0,
    pool_pre_ping=True,
)


minio_service = MinioService(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    bucket_name=settings.MINIO_BUCKET,
    region=settings.MINIO_REGION,
)

file_service = FileService(
    minio_service=minio_service,
    base_upload_path=settings.UPLOAD_BASE_PATH,
    cdn_base_path=settings.CDN_BASE_PATH,
    custom_http_proxy=settings.CUSTOM_HTTP_PROXY,
)

searchia_client = SearchiaClient(
    endpoint=settings.SEARCHIA_BASE_ENDPOINT,
    api_key=settings.SEARCHIA_API_KEY,
    index_name=settings.SEARCHIA_INDEX_NAME,
    logger=logger,
    custom_http_proxy=settings.CUSTOM_HTTP_PROXY
)



message_service = MessageService()
portfolio_service = PortfolioService()
ai_client = AIClient(base_url=settings.AI_BASE_URL, api_key=settings.AI_API_KEY, model=settings.AI_MODEL_NAME)

# RAG Services - Milvus Vector Store
vector_store = MilvusVectorStore(
    host=settings.MILVUS_HOST,
    port=settings.MILVUS_PORT,
    collection_name=f"{settings.MILVUS_COLLECTION}_v3",
)

embeddings_client = EmbeddingsClient(
    base_url=settings.AI_EMBEDDING_BASE_URL,
    api_key=settings.AI_EMBEDDING_API_KEY,
    model=settings.AI_EMBEDDING_MODEL_NAME,
)

rag_service = RAGService(
    vector_store=vector_store,
    embeddings_client=embeddings_client,
)

user_service = UserService(jwt_public_key=settings.JWT_PUBLIC_KEY, jwt_private_key=settings.JWT_PRIVATE_KEY)

ai_chat_service = AIChatService(
    message_service=message_service,
    ai_client=ai_client,
    rag_service=rag_service,
)
