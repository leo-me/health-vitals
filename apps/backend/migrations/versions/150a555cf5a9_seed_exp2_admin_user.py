"""seed exp2 admin user

Revision ID: 150a555cf5a9
Revises: a1b2c3d4e5f6
Create Date: 2026-05-25 00:00:00.000000

Seeds a fixed admin user that `experiments/exp2_mlflow_pipeline` uses to
authenticate against /api/v1/train. Email and password come from
app.core.config.settings.EXP2_ADMIN_* so they can be overridden by env vars
in CI / production, but ship with sensible dev defaults.

Idempotent: ON CONFLICT (email) DO NOTHING — re-running upgrade head will not
fail, and will not clobber a password the operator has changed since.
"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import settings
from app.core.security import hash_password


revision: str = '150a555cf5a9'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # UUID generated in Python so we don't depend on the pgcrypto extension,
    # which has not been enabled in earlier migrations.
    user_id = str(uuid.uuid4())
    hashed  = hash_password(settings.EXP2_ADMIN_PASSWORD)

    # user_type is a PG ENUM whose stored labels are the uppercase Python
    # member names ('PATIENT', 'CAREGIVER', 'ADMIN') — see migration
    # f7886d5ffef0_create_core_tables. The ::usertypeenum cast is required
    # because the bind param is a plain string.
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, email, password, user_type, created_at)
            VALUES (:id, :email, :pwd, 'ADMIN'::usertypeenum, NOW())
            ON CONFLICT (email) DO NOTHING
            """
        ).bindparams(
            id    = user_id,
            email = settings.EXP2_ADMIN_EMAIL,
            pwd   = hashed,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email")
          .bindparams(email=settings.EXP2_ADMIN_EMAIL)
    )
