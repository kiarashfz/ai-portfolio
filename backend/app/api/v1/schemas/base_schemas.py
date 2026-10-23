from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Any
from utils import BaseExample


class BaseEntitySchema(BaseModel):
    id: UUID
    created_at: datetime


class AssignRequest(BaseModel):
    index: int | None = Field(
        default=None, ge=1, description="Position of product in zone"
    )


class EntityActionErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                400: [
                    {
                        "type": "/{action}_error/{entity_name}",
                        "title": "{Action} Error",
                        "details": "Error details",
                    }
                ]
            }
        ]


class EntityNotFoundErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                404: [
                    {
                        "type": "/not_found/{entity_name}",
                        "title": "Not Found",
                        "details": "{EntityName} has not found",
                    }
                ]
            }
        ]


class EntityLockErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                400: [
                    {
                        "type": "/update_error/{entity_name}",
                        "title": "Update Error",
                        "details": "Entity is locked for changes and is ready to publish.",
                    }
                ]
            }
        ]


class EntityUniqueErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                400: [
                    {
                        "type": "/{action}_error/{entity_name}",
                        "title": "{action} Error",
                        "details": "Duplicate entry detected. The record already exists.",
                    }
                ]
            }
        ]


class EntityFindErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                400: [
                    {
                        "type": "/find_error/{entity_name}",
                        "title": "Find Error",
                        "details": "Error details",
                    }
                ]
            }
        ]


class GetEntityErrorResponseExample(
    EntityActionErrorResponseExample,
    EntityNotFoundErrorResponseExample
):
    pass


class CreateEntityErrorResponseExample(
    EntityActionErrorResponseExample,
    EntityUniqueErrorResponseExample
):
    pass


class UpdateEntityErrorResponseExample(
    EntityActionErrorResponseExample,
    EntityNotFoundErrorResponseExample,
    EntityLockErrorResponseExample,
    EntityUniqueErrorResponseExample,
):
    pass


class FindEntityErrorResponseExample(
    EntityNotFoundErrorResponseExample,
    EntityFindErrorResponseExample,
):
    pass
