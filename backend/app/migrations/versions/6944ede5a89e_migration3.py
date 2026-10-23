"""migration3

Revision ID: 6944ede5a89e
Revises: 4345ac575387
Create Date: 2025-05-06 13:30:05.264796

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "6944ede5a89e"
down_revision: Union[str, None] = "4345ac575387"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "role",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "permission",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    )
    op.drop_column("permission", "description")
    op.alter_column("user", "is_active", server_default=None)
    op.alter_column("role", "is_active", server_default=None)
    op.alter_column("permission", "title", server_default=None)


def downgrade() -> None:
    op.add_column("permission", sa.Column("description", sa.String(), nullable=True))
    op.drop_column("permission", "title")
    op.drop_column("role", "is_active")
    op.drop_column("user", "is_active")
