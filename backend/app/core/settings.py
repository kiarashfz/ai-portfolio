from pydantic_settings import BaseSettings
from uuid import uuid4
from ec_helpers import get_etc_hostnames
from os import path
from typing import Optional
import json
from redis.asyncio.cluster import ClusterNode

parent_dir = path.abspath(path.abspath(path.dirname(__file__)) + "/../")


class Settings(BaseSettings):
    SERVICE_NAME: str
    TIMEZONE: str = "Asia/Tehran"
    ENVIRONMENT: str = "development"
    API_SERVICE_PREFIX: str = ""

    API_V1_STR: str = "/v1"

    WORKER_ID: str = uuid4().hex
    CONTAINER_ID: str = get_etc_hostnames()

    FLUENTBIT_ENDPOINT: str
    LOGGER_CONSOLE_ENABLED: Optional[bool] = False
    LOGGER_HTTP_ENABLED: Optional[bool] = True

    REDIS_NODES: Optional[str] = None
    REDIS_URL: Optional[str] = None
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_PREFIX: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_REGION: str

    UPLOAD_BASE_PATH: str
    CDN_BASE_PATH: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    POSTGRES_COMMERCE_DB: str
    POSTGRES_COMMERCE_USER: str
    POSTGRES_COMMERCE_PASSWORD: str
    POSTGRES_COMMERCE_HOST: str
    POSTGRES_COMMERCE_PORT: str

    LDAP_ENDPOINT: str

    ENM_ENDPOINT: str
    ENM_USERNAME: str
    ENM_PASSWORD: str
    ENM_NOTIFICATION_CODE: str

    SMSD_ENDPOINT: str = ""
    SMSC_USERNAME: str = ""
    SMSC_PASSWORD: str = ""
    SMSC_SENDER_NAME_ONNET: str = "My_Irancell"

    MAIL_SENDER: str = "yellomart@mtnirancell.ir"
    MAIL_SMTP_ADDRESS: str = "LBMAIL.mtnirancell.ir"
    MAIL_SMTP_PORT: int = 25

    LOGIN_OTP_EXPIRY: int = 120

    JWT_PUBLIC_KEY: str = open(f"{parent_dir}/rsa/public.pem", "r").read()
    JWT_PRIVATE_KEY: str = open(f"{parent_dir}/rsa/private.key", "r").read()

    CUSTOM_HTTP_PROXY: str | None = None

    # SEARCHIA
    SEARCHIA_BASE_ENDPOINT: str
    SEARCHIA_API_KEY: str
    SEARCHIA_INDEX_NAME: str

    RABBITMQ_URL: str

    AUTO_UPDATE_PRODUCTS_CRON_HOURS: int = 17
    AUTO_UPDATE_PRODUCTS_CRON_MINUTES: int = 0

    AI_BASE_URL: str
    AI_API_KEY: str
    AI_MODEL_NAME: str

    AI_EMBEDDING_MODEL_NAME: str
    AI_EMBEDDING_BASE_URL: str
    AI_EMBEDDING_API_KEY: str

    # RAG & Vector Database - Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "portfolio_embeddings"

    class Config:
        case_sensitive = True

    @property
    def postgres_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_db_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_COMMERCE_USER}:{self.POSTGRES_COMMERCE_PASSWORD}@{self.POSTGRES_COMMERCE_HOST}:{self.POSTGRES_COMMERCE_PORT}/{self.POSTGRES_COMMERCE_DB}"

    @property
    def redis_startup_nodes(self):
        redis_urls = json.loads(self.REDIS_NODES)
        return [
            ClusterNode(url.split("://")[1].split(":")[0], int(url.split(":")[-1]))
            for url in redis_urls
        ]


settings = Settings()
