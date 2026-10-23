import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, text
from typing import Optional
from uuid import UUID
from .models import (
    ProductStage,
    ProductLive,
    ZoneStage,
    ZoneLive,
    ZoneProductLinkStage,
    ZoneProductLinkLive,
    ChangeMerge,
    ZoneStyleEnum,
    ZoneDataTypeEnum,
)
from .base_stage_repository import BaseStageRepository
from .publish_engine import PublishEngine
from .base_stage_services import LinkEngine


class ZoneStageService:
    def __init__(self, zone_repo: BaseStageRepository, link_repo: BaseStageRepository):
        self.zone_repo = zone_repo
        self.link_engine = LinkEngine(link_repo, ZoneProductLinkStage)

    # Zone CRUD
    async def create_zone(self, session: AsyncSession, created_by: str, **data):
        return await self.zone_repo.create(session, created_by=created_by, **data)

    async def update_zone(
        self, session: AsyncSession, zone_id: UUID, created_by: str, **updates
    ):
        return await self.zone_repo.update(
            session, entity_id=zone_id, created_by=created_by, **updates
        )

    async def delete_zone(self, session: AsyncSession, zone_id: UUID, created_by: str):
        return await self.zone_repo.delete(
            session, entity_id=zone_id, created_by=created_by
        )

    # Link ops
    async def assign_product(
        self,
        session: AsyncSession,
        zone_id: UUID,
        product_id: UUID,
        created_by: str,
        index: Optional[int] = None,
    ):
        return await self.link_engine.assign(
            session, "zone_id", zone_id, "product_id", product_id, created_by, index
        )

    async def move_product(
        self,
        session: AsyncSession,
        zone_id: UUID,
        product_id: UUID,
        new_index: int,
        created_by: str,
    ):
        await self.link_engine.move(
            session, "zone_id", zone_id, "product_id", product_id, new_index, created_by
        )

    async def remove_product(
        self, session: AsyncSession, zone_id: UUID, product_id: UUID, created_by: str
    ):
        await self.link_engine.remove(
            session, "zone_id", zone_id, "product_id", product_id, created_by
        )


# ---------- Database setup ----------
def make_engine():
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", "5433"))
    pg_user = os.getenv("POSTGRES_USER", "user")
    pg_password = os.getenv("POSTGRES_PASSWORD", "password")
    pg_db = os.getenv("POSTGRES_DB", "mydb")
    async_url = (
        f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    )
    return create_async_engine(async_url, echo=False, pool_pre_ping=True)


async def truncate_all(session: AsyncSession):
    tables = [
        "change_log",
        "change_merge",
        "zoneproductlink_stage",
        "zone_stage",
        "product_stage",
        "zoneproductlink_live",
        "zone_live",
        "product_live",
    ]
    for table in tables:
        await session.execute(
            text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
        )
    await session.commit()


# ---------- Tests ----------
async def test_create_zone_and_products(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )
    p2 = await product_repo.create(
        session, created_by="t", title="P2", description="D2"
    )

    zones = (await session.scalars(select(ZoneStage))).all()
    products = (await session.scalars(select(ProductStage))).all()

    assert len(zones) == 1
    assert len(products) == 2
    print("[OK] test_create_zone_and_products")


async def test_assign_and_reorder_links(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )
    p2 = await product_repo.create(
        session, created_by="t", title="P2", description="D2"
    )
    p3 = await product_repo.create(
        session, created_by="t", title="P3", description="D3"
    )

    await zone_service.assign_product(session, zone.id, p1.id, created_by="t")
    await zone_service.assign_product(session, zone.id, p2.id, created_by="t", index=1)
    await zone_service.assign_product(session, zone.id, p3.id, created_by="t")

    await zone_service.move_product(
        session, zone.id, p3.id, new_index=2, created_by="t"
    )
    await zone_service.remove_product(session, zone.id, p1.id, created_by="t")

    links = (
        await session.scalars(
            select(ZoneProductLinkStage)
            .where(ZoneProductLinkStage.zone_id == zone.id)
            .order_by(ZoneProductLinkStage.seq_num)
        )
    ).all()

    assert [l.product_id for l in links] == [p2.id, p3.id]
    print("[OK] test_assign_and_reorder_links")


async def test_partial_publish(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)
    publish_engine = PublishEngine(
        {
            "product_stage": ProductLive,
            "zone_stage": ZoneLive,
            "zoneproductlink_stage": ZoneProductLinkLive,
        },
    )

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )
    await zone_service.assign_product(session, zone.id, p1.id, created_by="t")

    # only ready/publish products + zones (not links)
    merges = (
        await session.scalars(
            select(ChangeMerge).where(
                ChangeMerge.status == "draft",
                ChangeMerge.entity_type.in_(["product_stage", "zone_stage"]),
            )
        )
    ).all()
    for m in merges:
        await publish_engine.ready_by_merge_id(session, m.id)
    await publish_engine.publish_all(session)

    zones_live = (await session.scalars(select(ZoneLive))).all()
    prods_live = (await session.scalars(select(ProductLive))).all()
    links_live = (await session.scalars(select(ZoneProductLinkLive))).all()

    assert len(zones_live) == 1
    assert len(prods_live) == 1
    assert len(links_live) == 0  # links not published
    print("[OK] test_partial_publish")


async def test_full_publish(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)
    publish_engine = PublishEngine(
        {
            "product_stage": ProductLive,
            "zone_stage": ZoneLive,
            "zoneproductlink_stage": ZoneProductLinkLive,
        },
    )

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )
    p2 = await product_repo.create(
        session, created_by="t", title="P2", description="D2"
    )

    await zone_service.assign_product(session, zone.id, p1.id, created_by="t")
    await zone_service.assign_product(session, zone.id, p2.id, created_by="t")

    merges = (
        await session.scalars(select(ChangeMerge).where(ChangeMerge.status == "draft"))
    ).all()
    for m in merges:
        await publish_engine.ready_by_merge_id(session, m.id)
    await publish_engine.publish_all(
        session,
        publish_order={"product_stage": 1, "zone_stage": 1, "zoneproductlink_stage": 2},
    )

    zones_live = (await session.scalars(select(ZoneLive))).all()
    prods_live = (await session.scalars(select(ProductLive))).all()
    links_live = (await session.scalars(select(ZoneProductLinkLive))).all()

    assert len(zones_live) == 1
    assert len(prods_live) == 2
    assert len(links_live) == 2
    assert sorted(l.seq_num for l in links_live) == [1, 2]
    print("[OK] test_full_publish")


# ---------- Extended Tests ----------
async def test_reindexing(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)

    # Create zone and products
    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone R",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    products = [
        await product_repo.create(
            session, created_by="t", title=f"P{i}", description=f"D{i}"
        )
        for i in range(1, 6)
    ]

    # Assign products with intentional gaps in seq_num
    await zone_service.assign_product(
        session, zone.id, products[0].id, created_by="t", index=1
    )
    await zone_service.assign_product(
        session, zone.id, products[1].id, created_by="t", index=10
    )
    await zone_service.assign_product(
        session, zone.id, products[2].id, created_by="t", index=5
    )
    await zone_service.assign_product(session, zone.id, products[3].id, created_by="t")
    await zone_service.assign_product(session, zone.id, products[4].id, created_by="t")

    # Move product 2 to position 2 → triggers reindex
    await zone_service.move_product(
        session, zone.id, products[1].id, new_index=2, created_by="t"
    )

    # Fetch current seq_nums
    links = (
        await session.scalars(
            select(ZoneProductLinkStage)
            .where(ZoneProductLinkStage.zone_id == zone.id)
            .order_by(ZoneProductLinkStage.seq_num)
        )
    ).all()

    seqs = [l.seq_num for l in links]
    expected_order = [
        products[0].id,
        products[1].id,
        products[2].id,
        products[3].id,
        products[4].id,
    ]

    assert [l.product_id for l in links] == expected_order, "Reindex ordering failed"
    assert seqs == list(range(1, 6)), "Reindex seq_nums should be compact from 1"
    print("[OK] test_reindexing")


async def test_changemerge_entries(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)

    # Create zone and a product
    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone C",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    product = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )

    # Assign product to zone
    await zone_service.assign_product(session, zone.id, product.id, created_by="t")

    # Fetch ChangeMerge rows
    merges = (
        await session.scalars(select(ChangeMerge).order_by(ChangeMerge.created_at))
    ).all()

    # Expected: CREATE product, CREATE zone, CREATE link
    assert len(merges) == 3, "Should create 3 ChangeMerge rows"
    actions = [m.action for m in merges]
    entities = [m.entity_type for m in merges]

    assert "CREATE" in actions
    assert "product_stage" in entities
    assert "zone_stage" in entities
    assert "zoneproductlink_stage" in entities
    print("[OK] test_changemerge_entries")


from sqlalchemy import select


async def test_link_ordering_reindex(session: AsyncSession):
    await truncate_all(session)
    # ---------- Initialize repositories and services ----------
    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)

    publish_engine = PublishEngine(
        {
            "product_stage": ProductLive,
            "zone_stage": ZoneLive,
            "zoneproductlink_stage": ZoneProductLinkLive,
        },
    )

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="tester", title="P1", description="D1"
    )
    p2 = await product_repo.create(
        session, created_by="tester", title="P2", description="D2"
    )
    p3 = await product_repo.create(
        session, created_by="tester", title="P3", description="D3"
    )

    # ---------- Assign products ----------
    await zone_service.assign_product(
        session, zone.id, p1.id, created_by="tester"
    )  # seq 1
    await zone_service.assign_product(
        session, zone.id, p2.id, created_by="tester"
    )  # seq 2
    await zone_service.assign_product(
        session, zone.id, p3.id, created_by="tester", index=2
    )  # seq 2, p2 -> 3

    stmt = (
        select(ZoneProductLinkStage)
        .where(ZoneProductLinkStage.zone_id == zone.id)
        .order_by(ZoneProductLinkStage.seq_num)
    )
    links = (await session.scalars(stmt)).all()
    assert [l.seq_num for l in links] == [1, 2, 3], "Initial stage seq_nums incorrect"

    await zone_service.move_product(
        session, zone.id, p1.id, new_index=3, created_by="tester"
    )
    links = (await session.scalars(stmt)).all()
    assert [l.seq_num for l in links] == [1, 2, 3], "Seq_nums after move incorrect"
    assert [l.product_id for l in links] == [
        p3.id,
        p2.id,
        p1.id,
    ], "Product order after move incorrect"

    # ---------- Publish all staged changes ----------
    await publish_engine.publish_all(
        session,
        include_drafts=True,
        publish_order={"product_stage": 1, "zone_stage": 1, "zoneproductlink_stage": 2},
    )

    # ---------- Check live table ----------
    live_stmt = (
        select(ZoneProductLinkLive)
        .where(ZoneProductLinkLive.zone_id == zone.id)
        .order_by(ZoneProductLinkLive.seq_num)
    )
    live_links = (await session.scalars(live_stmt)).all()
    assert [l.seq_num for l in live_links] == [
        1,
        2,
        3,
    ], "Live seq_nums incorrect after first publish"

    # ---------- Force reindex by inserting a new product at index 2 ----------
    p4 = await product_repo.create(
        session, created_by="tester", title="P4", description="D4"
    )
    await zone_service.assign_product(
        session, zone.id, p4.id, created_by="tester", index=2
    )

    links = (await session.scalars(stmt)).all()
    assert [l.seq_num for l in links] == [
        1,
        2,
        3,
        4,
    ], "Stage seq_nums incorrect after reindex"
    assert [l.product_id for l in links] == [
        p3.id,
        p4.id,
        p2.id,
        p1.id,
    ], "Product order incorrect after reindex"

    # ---------- Verify ChangeMerge entries for link changes ----------
    cm_stmt = (
        select(ChangeMerge)
        .where(ChangeMerge.entity_type == "zoneproductlink_stage")
        .order_by(ChangeMerge.created_at)
    )
    cm_rows = (await session.scalars(cm_stmt)).all()

    # ---------- Publish all staged changes again ----------
    await publish_engine.publish_all(
        session,
        include_drafts=True,
        publish_order={"product_stage": 1, "zone_stage": 1, "zoneproductlink_stage": 2},
    )

    # ---------- Verify live table and ChangeMerge consistency ----------
    live_links = (await session.scalars(live_stmt)).all()
    assert [l.seq_num for l in live_links] == [
        1,
        2,
        3,
        4,
    ], "Live seq_nums incorrect after reindex publish"
    assert [l.product_id for l in live_links] == [
        p3.id,
        p4.id,
        p2.id,
        p1.id,
    ], "Live product order incorrect"

    cm_rows = (await session.scalars(cm_stmt)).all()
    assert all(
        cm.status == "published" for cm in cm_rows
    ), "All ChangeMerge entries should be published after publish_all"

    print(
        "[OK] Test passed: assign, move, reindex, and publish verified in stage, live, and ChangeMerge."
    )


async def test_relation(session: AsyncSession):
    await truncate_all(session)

    product_repo = BaseStageRepository(ProductStage)
    zone_repo = BaseStageRepository(ZoneStage)
    link_repo = BaseStageRepository(ZoneProductLinkStage)
    zone_service = ZoneStageService(zone_repo, link_repo)
    publish_engine = PublishEngine(
        {
            "product_stage": ProductLive,
            "zone_stage": ZoneLive,
            "zoneproductlink_stage": ZoneProductLinkLive,
        },
    )

    zone = await zone_service.create_zone(
        session,
        created_by="t",
        title="Zone A",
        style=ZoneStyleEnum.STYLE_A,
        data_type=ZoneDataTypeEnum.PRODUCT,
    )
    p1 = await product_repo.create(
        session, created_by="t", title="P1", description="D1"
    )
    p2 = await product_repo.create(
        session, created_by="t", title="P2", description="D2"
    )
    await zone_service.assign_product(session, zone.id, p1.id, created_by="t")
    await zone_service.assign_product(session, zone.id, p2.id, created_by="t")

    await zone_service.move_product(session, zone.id, p1.id, 2, created_by="t")

    await zone_service.remove_product(session, zone.id, p2.id, created_by="t")

    # await publish_engine.publish_all(
    #     session,
    #     include_drafts=True,
    #     publish_order={"product_stage": 1, "zone_stage": 1, "zoneproductlink_stage": 2},
    # )

    # zones_live = (await session.scalars(select(ZoneLive))).all()
    # prods_live = (await session.scalars(select(ProductLive))).all()
    # links_live = (await session.scalars(select(ZoneProductLinkLive))).all()

    # assert len(zones_live) == 1
    # assert len(prods_live) == 1
    # assert len(links_live) == 0  # links not published
    print("[OK] test_partial_publish")


# ---------- Runner ----------
async def main():
    engine = make_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:

        await test_create_zone_and_products(session)
        await test_assign_and_reorder_links(session)
        await test_partial_publish(session)
        await test_full_publish(session)
        await test_reindexing(session)
        await test_changemerge_entries(session)
        await test_link_ordering_reindex(session)
        await test_relation(session)
        # await truncate_all(session)


if __name__ == "__main__":
    asyncio.run(main())
