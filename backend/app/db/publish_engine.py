from __future__ import annotations
from functools import partial

from datetime import datetime
from typing import Any, Dict, Optional, Type, List, Tuple
from uuid import UUID

from db.base_stage_services import BaseStageService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy import select

from .models import ChangeMerge
from .utils import transactional, parse_fk_violation
from sqlalchemy.exc import IntegrityError


class PublishEngine:
    """Publishes merged changes from `ChangeMerge` into live tables."""

    def __init__(
            self,
            entity_type_to_live_model: Dict[str, Type[SQLModel]],
            entity_type_to_service: Dict[str, Type[BaseStageService]],
            id_attribute: str = "id",
    ) -> None:
        self.entity_type_to_live_model = entity_type_to_live_model
        self.entity_type_to_service = entity_type_to_service
        self.id_attribute = id_attribute
        self._link_config = {
            "categoryproductlink_stage": {
                "parent_attr": "category_id",
                "secondary_attr": "product_id",
            },
            "categorysupplierlink_stage": {
                "parent_attr": "category_id",
                "secondary_attr": "supplier_id",
            },
            "zoneproductlink_stage": {
                "parent_attr": "zone_id",
                "secondary_attr": "product_id",
            },
            "zonebannerlink_stage": {
                "parent_attr": "zone_id",
                "secondary_attr": "banner_id",
            },
            "zonecategorylink_stage": {
                "parent_attr": "zone_id",
                "secondary_attr": "category_id",
            },
            "pagezonelink_stage": {
                "parent_attr": "page_id",
                "secondary_attr": "zone_id",
            },
        }

        self._relations_key = {
            "categoryproductlink_stage": "products",
            "categorysupplierlink_stage": "suppliers",
            "zoneproductlink_stage": "products",
            "zonebannerlink_stage": "banners",
            "zonecategorylink_stage": "categories",
            "pagezonelink_stage": "zones",
        }

    def _is_relation(self, entity_type):
        if "link" in entity_type:
            return True
        return False

    async def publish_by_merge_id(self, session: AsyncSession, merge_id: UUID, published_by: str) -> bool:
        return await self._publish_in_session(session, merge_id, published_by)

    async def reject_by_merge_id(self, session: AsyncSession, merge_id: UUID, rejected_by: str) -> bool:
        return await self._reject_in_session(session, merge_id, rejected_by)

    async def ready_by_merge_id(self, session: AsyncSession, merge_id: UUID) -> bool:
        async with transactional(session):
            row = await session.get(ChangeMerge, merge_id)
            if not row or row.status != "draft":
                return False
            row.status = "ready"
            session.add(row)
            await session.flush()
            return True

    async def _publish_in_session(self, session: AsyncSession, merge_id: UUID, published_by: str) -> bool:
        try:
            async with session.begin_nested():
                merge_row: Optional[ChangeMerge] = await session.get(
                    ChangeMerge, merge_id
                )
                if merge_row is None or merge_row.status != "ready":
                    return False

                live_model = self.entity_type_to_live_model.get(merge_row.entity_type)
                if live_model is None:
                    return False

                entity_id = merge_row.entity_id
                action = merge_row.action
                data_after: Optional[Dict[str, Any]] = merge_row.data_after

                if action == "CREATE":
                    await self._apply_create(session, live_model, entity_id, data_after)
                elif action == "UPDATE":
                    await self._apply_update(session, live_model, entity_id, data_after)
                elif action == "DELETE":
                    await self._apply_delete(session, live_model, entity_id)
                else:
                    return False

                merge_row.status = "published"
                merge_row.has_error = False
                merge_row.message = None
                merge_row.published_by = published_by
                merge_row.published_at = datetime.utcnow()
                session.add(merge_row)

            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            merge_row = await session.get(ChangeMerge, merge_id)
            if merge_row:
                parsed = parse_fk_violation(e)
                if parsed:
                    merge_row.has_error = True
                    merge_row.message = f"Missing referenced entity: {parsed}"
                    session.add(merge_row)
                    await session.commit()
                    raise ValueError({"error": "Missing referenced entity", **parsed})
                else:
                    merge_row.has_error = True
                    merge_row.message = str(e.orig) if hasattr(e, "orig") else str(e)
                    merge_row.has_error = True
                    session.add(merge_row)
                    await session.commit()
                    raise e

            else:
                raise ValueError({"error": "row does not exists"})

        return True

    async def _reject_in_session(self, session: AsyncSession, merge_id: UUID, rejected_by: str) -> bool:
        try:
            async with session.begin_nested():
                merge_row: Optional[ChangeMerge] = await session.get(
                    ChangeMerge, merge_id
                )
                if merge_row is None or merge_row.status != "draft":
                    return False

                reject_function = await self._prepare_reject_function_with_arguments(
                    session, merge_row, rejected_by
                )
                if not reject_function:
                    return False

                await reject_function()

            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            parsed = parse_fk_violation(e)
            if parsed:
                raise ValueError({"error": "Missing referenced entity", **parsed})
            else:
                raise e

        return True

    async def _prepare_reject_function_with_arguments(
            self,
            session: AsyncSession,
            change_merge_obj: ChangeMerge,
            rejected_by: str
    ) -> function:

        stage_service: BaseStageService | None = self.entity_type_to_service.get(change_merge_obj.entity_type)
        if stage_service is None:
            return None

        model = self.entity_type_to_live_model.get(change_merge_obj.entity_type)
        if model is None:
            return None

        entity_type = change_merge_obj.entity_type
        entity_id = change_merge_obj.entity_id
        action = change_merge_obj.action
        data_before: dict[str, Any] = dict(change_merge_obj.data_before or {})

        if self._is_relation(entity_type):
            parent_attr = self._link_config[entity_type]["parent_attr"]
            secondary_attr = self._link_config[entity_type]["secondary_attr"]
            if action == "CREATE":
                parent_id = change_merge_obj.data_after[parent_attr]
                secondary_id = change_merge_obj.data_after[secondary_attr]
                return partial(
                    stage_service.relations.remove,
                    session, self._relations_key[entity_type], parent_id, secondary_id, rejected_by
                )
            elif action == "DELETE":
                parent_id = change_merge_obj.data_before[parent_attr]
                secondary_id = change_merge_obj.data_before[secondary_attr]
                return partial(
                    stage_service.relations.assign,
                    session, self._relations_key[entity_type], parent_id, secondary_id, rejected_by,
                    data_before["seq_num"],
                )
            elif action == "UPDATE":
                parent_id = change_merge_obj.data_after[parent_attr]
                secondary_id = change_merge_obj.data_after[secondary_attr]
                return partial(
                    stage_service.relations.move,
                    session, self._relations_key[entity_type], parent_id, secondary_id, data_before["seq_num"], rejected_by,
                )
            else:
                raise NotImplementedError(action)

        if action == "CREATE":
            return partial(
                stage_service.delete,
                session, entity_id, rejected_by
            )
        elif action == "UPDATE":
            data_before[self.id_attribute] = entity_id
            dto = model.model_validate(data_before)
            return partial(
                stage_service.update,
                session, entity_id, rejected_by, **dto.model_dump(exclude_unset=True)
            )
        elif action == "DELETE":
            dto = model.model_validate(data_before)
            return partial(
                stage_service.create,
                session, rejected_by, dto.model_dump()
            )
        else:
            return None

    async def publish(
            self,
            session: AsyncSession,
            item: ChangeMerge,
            published_by: str,
    ) -> int:
        """
        Publish given item.
        """
        return await self._publish_in_session(session, item.id, published_by)

    async def _apply_create(
            self,
            session: AsyncSession,
            live_model: Type[SQLModel],
            entity_id: Optional[UUID],
            data_after: Optional[Dict[str, Any]],
    ) -> None:
        if entity_id is None:
            return
        payload: Dict[str, Any] = dict(data_after or {})
        payload[self.id_attribute] = entity_id
        existing = await session.get(live_model, entity_id)
        if existing is None:
            dto = live_model.model_validate(payload)
            instance = live_model(**dto.model_dump())
            session.add(instance)
        else:
            dto = live_model.model_validate(payload)
            self._apply_payload(existing, dto.model_dump())
            session.add(existing)

    async def _apply_update(
            self,
            session: AsyncSession,
            live_model: Type[SQLModel],
            entity_id: Optional[UUID],
            data_after: Optional[Dict[str, Any]],
    ) -> None:
        if entity_id is None:
            return
        payload: Dict[str, Any] = dict(data_after or {})
        payload[self.id_attribute] = entity_id
        instance = await session.get(live_model, entity_id)
        if instance is None:
            dto = live_model.model_validate(payload)
            instance = live_model(**dto.model_dump())
            session.add(instance)
        else:
            dto = live_model.model_validate(payload)
            self._apply_payload(instance, dto.model_dump())
            session.add(instance)

    async def _apply_delete(
            self,
            session: AsyncSession,
            live_model: Type[SQLModel],
            entity_id: Optional[UUID],
    ) -> None:
        if entity_id is None:
            return
        instance = await session.get(live_model, entity_id)
        if instance is not None:
            await session.delete(instance)

    def _apply_payload(self, instance: SQLModel, payload: Dict[str, Any]) -> None:
        for key, value in payload.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

    async def publish_all(
            self,
            session: AsyncSession,
            published_by: str,
            limit: int = 1000,
            include_drafts: bool = False,
            publish_order: Dict[str, int] | None = None,
    ) -> int:
        """
        Publish all rows in dependency-safe order.
        - If include_drafts=True: first move all 'draft' merges to 'ready'.
        - Returns count published.
        """
        if include_drafts:
            # promote all drafts to ready
            draft_q = (
                select(ChangeMerge).where(ChangeMerge.status == "draft").limit(limit)
            )
            drafts: List[ChangeMerge] = (await session.execute(draft_q)).scalars().all()
            for draft in drafts:
                draft.status = "ready"
                session.add(draft)
            await session.flush()

        # now load ready rows
        q = select(ChangeMerge).where(ChangeMerge.status == "ready").limit(limit)
        rows: List[ChangeMerge] = (await session.execute(q)).scalars().all()
        if not rows:
            return 0

        def sort_key(row: ChangeMerge) -> Tuple[int, str]:
            return (
                publish_order.get(row.entity_type, 100),
                str(row.entity_type),
            )

        if publish_order:
            rows.sort(key=sort_key)

        published = 0
        for row in rows:
            if await self._publish_in_session(session, row.id, published_by):
                published += 1

        return published
