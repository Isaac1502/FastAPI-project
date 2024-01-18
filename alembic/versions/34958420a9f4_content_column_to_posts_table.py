"""content column to posts table

Revision ID: 34958420a9f4
Revises: f4369c9bd755
Create Date: 2024-01-18 17:54:05.073348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "34958420a9f4"
down_revision: Union[str, None] = "f4369c9bd755"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
