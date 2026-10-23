from pydantic import BaseModel

class AIChatRequest(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, I have a question about my order."
            }
        }

class AIChatResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, Answer."
            }
        }