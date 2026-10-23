# schemas/user.py
from pydantic import BaseModel


class SignUpRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "john_doe", "password": "secure_password"}
        }


class SignInRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "john_doe", "password": "secure_password"}
        }


class SignUpResponse(BaseModel):
    username: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SignInResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"