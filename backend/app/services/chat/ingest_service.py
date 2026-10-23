"""Service for managing portfolio data ingestion workflow"""
from uuid import UUID
from typing import Any

from services.chat.rag_service import RAGService
from services.portfolio.portfolio_service import PortfolioService


class IngestService:
    """
    Service for managing portfolio data ingestion
    Coordinates between portfolio service and RAG service
    """

    def __init__(
        self,
        portfolio_service: PortfolioService,
        rag_service: RAGService,
    ):
        self.portfolio_service = portfolio_service
        self.rag_service = rag_service

    async def ingest_portfolio_by_username(
        self,
        session,
        portfolio_username: str,
        portfolio_data: dict[str, Any],
        chunk_size: int = 512,
    ) -> dict[str, Any]:
        """
        Ingest portfolio data by username

        Args:
            session: Database session
            portfolio_username: Portfolio username
            portfolio_data: Data to ingest
            chunk_size: Chunk size for embeddings

        Returns:
            Dict with ingestion results
        """
        # Get portfolio by username
        portfolio = await self.portfolio_service.get_by_username(session, portfolio_username)
        if not portfolio:
            raise ValueError(f"Portfolio with username '{portfolio_username}' not found")

        # Ingest data
        result = await self.rag_service.ingest_portfolio_data(
            portfolio_id=portfolio.id,
            portfolio_data=portfolio_data,
            chunk_size=chunk_size,
        )

        return {
            "portfolio_id": str(portfolio.id),
            "portfolio_username": portfolio_username,
            **result,
        }

