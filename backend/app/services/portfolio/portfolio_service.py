from uuid import UUID
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from db.base_stage_repository import BaseSingleStageRepository
from db.base_stage_services import BaseSingleStageService
from db.models import Portfolio


class PortfolioService(BaseSingleStageService[Portfolio]):
    def __init__(self, repo: BaseSingleStageRepository = None):
        self.repo = repo or BaseSingleStageRepository(Portfolio)
        super().__init__(self.repo, Portfolio)

    async def get_by_username(self, session: AsyncSession, username: str) -> Portfolio | None:
        portfolios, _ = await self.find(
            session=session,
            select_relateds=['user'],
            filters={"user.username": {"match_mode": "equals", "value": username}},
        )
        return portfolios[0] if portfolios else None

    async def get_by_user_id(self, session: AsyncSession, user_id: UUID) -> Portfolio | None:
        portfolios, _ = await self.find(
            session=session,
            filters={"user_id": {"match_mode": "equals", "value": user_id}},
        )
        return portfolios[0] if portfolios else None

    async def create_portfolio(
        self,
        session: AsyncSession,
        user_id: UUID,
        first_name: str,
        last_name: str,
        title: str,
        summary: str,
        profile_data: dict[str, Any] | None = None,
    ) -> Portfolio:
        return await self.repo.create(
            session=session,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            summary=summary,
            profile_data=profile_data,
        )

    async def update_portfolio(
        self,
        session: AsyncSession,
        portfolio: Portfolio,
        first_name: str,
        last_name: str,
        title: str,
        summary: str,
        profile_data: dict[str, Any] | None = None,
    ) -> Portfolio:
        portfolio.first_name = first_name
        portfolio.last_name = last_name
        portfolio.title = title
        portfolio.summary = summary
        portfolio.profile_data = profile_data
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)
        return portfolio