"""add BVP ACC IBI TEMP to sensortype enum

Revision ID: a1b2c3d4e5f6
Revises: efc683e4bc1f
Create Date: 2026-05-18 00:00:00.000000

PostgreSQL ENUM values can only be added, never removed.
Downgrade is intentionally a no-op.
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0cdee26f8097'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE sensortype ADD VALUE IF NOT EXISTS 'bvp'")
    op.execute("ALTER TYPE sensortype ADD VALUE IF NOT EXISTS 'acc'")
    op.execute("ALTER TYPE sensortype ADD VALUE IF NOT EXISTS 'ibi'")
    op.execute("ALTER TYPE sensortype ADD VALUE IF NOT EXISTS 'temp'")


def downgrade() -> None:
    # PostgreSQL does not support DROP VALUE on an enum type.
    pass
