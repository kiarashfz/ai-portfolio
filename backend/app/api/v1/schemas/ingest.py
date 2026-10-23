"""Schemas for portfolio data ingestion"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class IngestRequest(BaseModel):
    """Request body for ingesting portfolio data"""

    data: Dict[str, Any] = Field(
        ...,
        description="Portfolio data to ingest. Can contain any structured data about the portfolio.",
        example={
            "summary": "Experienced full-stack developer with 5 years of expertise",
            "skills": ["Python", "JavaScript", "FastAPI", "React"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "duration": "2021-2024",
                    "description": "Led development of microservices architecture"
                }
            ],
            "projects": [
                {
                    "name": "AI Portfolio System",
                    "description": "RAG-based portfolio assistant",
                    "technologies": ["FastAPI", "Pinecone", "OpenAI"]
                }
            ]
        }
    )

    chunk_size: Optional[int] = Field(
        default=512,
        ge=100,
        le=2000,
        description="Maximum characters per chunk for embedding"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "summary": "Experienced full-stack developer",
                    "skills": ["Python", "JavaScript"],
                    "experience": [
                        {
                            "company": "Tech Corp",
                            "position": "Senior Developer",
                        }
                    ]
                },
                "chunk_size": 512
            }
        }


class IngestResponse(BaseModel):
    """Response from portfolio data ingestion"""

    portfolio_username: str = Field(
        ...,
        description="Username of the portfolio"
    )
    chunks_created: int = Field(
        ...,
        description="Number of chunks created from the data"
    )
    vectors_upserted: int = Field(
        ...,
        description="Number of vectors upserted to Pinecone"
    )
    status: str = Field(
        default="success",
        description="Status of the ingestion"
    )
    message: str = Field(
        default="Data ingested successfully",
        description="Status message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "portfolio_username": "john_doe",
                "chunks_created": 12,
                "vectors_upserted": 12,
                "status": "success",
                "message": "Data ingested successfully"
            }
        }


class IngestErrorResponse(BaseModel):
    """Error response for ingestion"""

    status: str = "error"
    message: str
    details: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to ingest portfolio data",
                "details": "Portfolio not found"
            }
        }

