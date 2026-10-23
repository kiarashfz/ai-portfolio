from email.policy import default
from typing import List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, time
from sqlalchemy.sql import text
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from sqlalchemy import Column, UniqueConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB


# ---------- BASE ----------


class BaseEntity(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP")
        },
    )


class Message(BaseEntity, table=True):
    __tablename__ = "message"

    portfolio_id: UUID = Field(foreign_key="portfolio.id", index=True)
    portfolio: "Portfolio" = Relationship(back_populates="messages")

    session_id: UUID = Field(index=True)
    role: str    # "user" | "assistant"
    content: str


class Portfolio(BaseEntity, table=True):
    __tablename__ = "portfolio"

    user_id: UUID = Field(foreign_key="user.id", unique=True, index=True)
    user: "User" = Relationship(back_populates="portfolio", passive_deletes=True)

    first_name: str
    last_name: str
    title: str
    summary: str

    profile_data: Dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )

    messages: List["Message"] = Relationship(
        back_populates="portfolio",
        passive_deletes=True,
    )


class User(BaseEntity, table=True):
    __tablename__ = "user"

    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
    )

    username: str = Field(index=True)
    password_hash: str

    portfolio: Portfolio | None = Relationship(
        back_populates="user",
        passive_deletes=True,
    )