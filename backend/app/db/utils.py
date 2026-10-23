from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import TypeVar
from sqlmodel import SQLModel
import re
from sqlalchemy.exc import IntegrityError


TModel = TypeVar("TModel", bound=SQLModel)


@asynccontextmanager
async def transactional(session: AsyncSession):
    """Open a per-call transactional boundary.

    - If the `session` already has an active transaction (e.g., higher layer started one),
      use a SAVEPOINT via begin_nested() so this operation remains atomic without
      controlling the outer transaction.
    - If no transaction is active, start and commit/rollback a real transaction via begin().
    """
    # AsyncSession exposes get_transaction()/in_transaction() to detect active tx
    if session.in_transaction():  # type: ignore[attr-defined]
        async with session.begin_nested():
            yield
    else:
        async with session.begin():
            yield


def parse_fk_violation(error: IntegrityError) -> dict | None:
    err_msg = str(error.orig)

    if "ForeignKeyViolationError" not in err_msg:
        return None

    key_match = re.search(r"Key \((?P<col>\w+)\)=\((?P<id>[^)]+)\)", err_msg)

    table_match = re.search(
        r"(is not present in|is still referenced from) table \"(?P<table>\w+)\"",
        err_msg,
    )

    if not key_match or not table_match:
        return None

    violation_text = table_match.group(1)
    violation_type = (
        "missing_reference" if "not present" in violation_text else "existing_reference"
    )

    return {
        "column": key_match.group("col"),
        "id": key_match.group("id"),
        "related_table": table_match.group("table"),
        "violation_type": violation_type,
    }
