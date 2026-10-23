from typing import Type, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from .base_stage_repository import BaseSingleStageRepository
from .find_engine import FindEngine
from .utils import TModel
from sqlalchemy.orm import joinedload, selectinload




from typing import Any, Dict, List, Optional, Tuple, Type, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc


class BaseSingleStageService(Generic[TModel]):
    """
    Simple service layer that uses BaseSingleStageRepository.
    Provides CRUD operations without change tracking, events, or created_by fields.
    """

    def __init__(self, repo: BaseSingleStageRepository, model: Type[TModel], find_engine: FindEngine = None):
        self.repo = repo
        self.model = model
        self.find_engine = find_engine or FindEngine()

    # ---- Standard CRUD ----
    async def get(
            self,
            session: AsyncSession,
            skip: int = 0,
            limit: int = 20,
            active: Optional[bool] = None,
            select_relateds: list[str] | None = None,
            prefetch_relateds: list[str] | None = None,
    ) -> Tuple[List[TModel], int]:
        """
        Get entities with pagination and optional active filter.
        Supports dynamic relation loading (joinedload/selectinload).
        Returns (items, total).
        """

        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if active is not None:
            query = query.where(self.model.is_active == active)
            count_query = count_query.where(self.model.is_active == active)

        # Order by created_at if available, otherwise by id
        if hasattr(self.model, 'created_at'):
            query = query.order_by(desc(self.model.created_at))
        else:
            query = query.order_by(desc(getattr(self.model, self.repo.id_attribute)))

        # Dynamic joinedload (like select_related)
        if select_relateds:
            for relation in select_relateds:
                query = query.options(joinedload(getattr(self.model, relation)))

        # Dynamic selectinload (like prefetch_related)
        if prefetch_relateds:
            for relation in prefetch_relateds:
                query = query.options(selectinload(getattr(self.model, relation)))

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        items = result.scalars().all()

        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        return items, total

    async def get_one(
            self,
            session: AsyncSession,
            entity_id: Any,
            select_relateds: list[str] = None,
            prefetch_relateds: list[str] = None
    ) -> Optional[TModel]:
        return await self.repo.get(session, entity_id, select_relateds, prefetch_relateds)

    async def create(self, session: AsyncSession, **data) -> TModel:
        """Create without created_by field since BaseSingleStageRepository doesn't track changes"""
        return await self.repo.create(session, **data)

    async def update(
            self, session: AsyncSession, entity_id: Any, **updates
    ) -> Optional[TModel]:
        """Update without created_by field since BaseSingleStageRepository doesn't track changes"""
        return await self.repo.update(session, entity_id=entity_id, **updates)

    async def delete(
            self, session: AsyncSession, entity_id: Any
    ) -> bool:
        """Delete without created_by field since BaseSingleStageRepository doesn't track changes"""
        return await self.repo.delete(session, entity_id=entity_id)

    async def activate(
            self, session: AsyncSession, entity_id: Any
    ) -> Optional[TModel]:
        """Activate entity by setting is_active=True"""
        return await self.update(session, entity_id, is_active=True)

    async def deactivate(
            self, session: AsyncSession, entity_id: Any
    ) -> Optional[TModel]:
        """Deactivate entity by setting is_active=False"""
        return await self.update(session, entity_id, is_active=False)

    async def find(
            self,
            session: AsyncSession,
            filters: Dict[str, Dict[str, Any]],
            skip: int = 0,
            limit: int = 100,
            select_relateds: list[str] | None = None,
    ) -> Tuple[List[TModel], int]:
        """Find entities using the find engine"""
        return await self.find_engine.find(
            session,
            self.model,
            filters,
            skip=skip,
            limit=limit,
            select_relateds=select_relateds,
        )