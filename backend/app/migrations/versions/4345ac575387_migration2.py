"""migration2

Revision ID: 4345ac575387
Revises: 3e56fd78fcaf
Create Date: 2025-05-06 12:17:24.909741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4345ac575387'
down_revision: Union[str, None] = '3e56fd78fcaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
