from enum import Enum

from ec_helpers.schema_examples import BaseExample
from pydantic import BaseModel
from typing import Any, Dict


class MatchMode(str, Enum):
    starts_with = "starts_with"
    contains = "contains"
    not_contains = "not_contains"
    ends_with = "ends_with"
    equals = "equals"
    not_equals = "not_equals"
    in_ = "in"
    not_in = "not_in"
    lt = "lt"
    lte = "lte"
    gt = "gt"
    gte = "gte"
    between = "between"
    date_is = "date_is"
    date_is_not = "date_is_not"
    date_before = "date_before"
    date_after = "date_after"
    custom = "custom"


class FilterCriteria(BaseModel):
    value: Any
    match_mode: MatchMode


class FindSchema(BaseModel):
    filters: Dict[str, FilterCriteria]
    skip: int = 0
    limit: int = 100


class SuccessResponse(BaseModel):
    message: str = "Done"

    class Config:
        json_schema_extra = {"example": {"message": "Done"}}


class ServiceResult(BaseModel):
    is_successful: bool
    code: int = 0
    message: str = ""


class AuthErrorResponseExample(BaseExample):
    class Config:
        examples: list[dict[int, list[dict[str, Any]]]] = [
            {
                401: [
                    {
                        "type": "/unauthorized",
                        "title": "Unauthorized",
                        "details": "Missing authorization header",
                    },
                    {
                        "type": "/unauthorized",
                        "title": "Unauthorized",
                        "details": "Invalid authorization header",
                    },
                    {
                        "type": "/unauthorized",
                        "title": "Unauthorized",
                        "details": "Expired token",
                    },
                    {
                        "type": "/unauthorized",
                        "title": "Unauthorized",
                        "details": "Expired token",
                    },
                    {
                        "type": "/unauthorized",
                        "title": "Unauthorized",
                        "details": "Invalid token",
                    },
                ],
                403: [
                    {
                        "type": "/forbidden",
                        "title": "Forbidden",
                        "details": "No permission",
                    }
                ]
            }
        ]
