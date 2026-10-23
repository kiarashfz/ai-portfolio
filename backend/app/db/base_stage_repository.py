from __future__ import annotations

from typing import Any, Dict, Generic, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from .utils import transactional, TModel
from sqlalchemy import select



class BaseSingleStageRepository(Generic[TModel]):
    def __init__(
            self,
            model: Type[TModel],
            id_attribute: str = "id",
    ) -> None:
        self.model = model
        self.id_attribute = id_attribute

    def _entity_type(self) -> str:
        return getattr(self.model, "__tablename__", self.model.__name__)

    def _get_pk(self, instance: TModel) -> Any:
        return getattr(instance, self.id_attribute)

    def _exception_handler(self, e):
        error_message = str(e)
        if "foreign key constraint" in error_message.lower():
            raise ValueError(
                "Invalid foreign key reference. Please check the related record."
            )
        elif "unique constraint" in error_message.lower():
            raise ValueError("Duplicate entry detected. The record already exists.")
        elif "null value in column" in error_message.lower():
            raise ValueError(
                "A required field is missing. Please provide all necessary data."
            )
        else:
            raise ValueError("A database integrity error occurred. Please try again.")

    async def create(
            self,
            session: AsyncSession,
            **data: Any,
    ) -> TModel:
        payload: Dict[str, Any] = dict(data)
        instance = self.model(**payload)
        async with transactional(session):
            session.add(instance)
            try:
                await session.flush()
            except IntegrityError as e:
                self._exception_handler(e)
        return instance

    async def bulk_create(
            self,
            session: AsyncSession,
            data_list: list[Dict[str, Any]],
    ) -> list[TModel]:
        if not data_list:
            return []

        instances = [self.model(**data) for data in data_list]

        async with transactional(session):
            session.add_all(instances)
            try:
                await session.flush()
            except IntegrityError as e:
                self._exception_handler(e)

        return instances

    async def get(
            self,
            session: AsyncSession,
            entity_id: Any,
            select_relateds: list[str] = None,
            prefetch_relateds: list[str] = None
    ) -> Optional[TModel]:

        query = select(self.model).where(self.model.id == entity_id)

        if select_relateds:
            for relation in select_relateds:
                query = query.options(joinedload(getattr(self.model, relation)))

        if prefetch_relateds:
            for relation in prefetch_relateds:
                query = query.options(selectinload(getattr(self.model, relation)))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, entity_id: Any, **updates: Any) -> Optional[TModel]:
        async with transactional(session):
            instance = await session.get(self.model, entity_id)
            if not instance:
                return None

            for k, v in updates.items():
                setattr(instance, k, v)

            try:
                await session.flush()
            except IntegrityError as e:
                self._exception_handler(e)

        return instance

    async def delete(self, session: AsyncSession, entity_id: Any) -> bool:
        async with transactional(session):
            instance = await session.get(self.model, entity_id)
            if instance:
                await session.delete(instance)
                return True
            return False
