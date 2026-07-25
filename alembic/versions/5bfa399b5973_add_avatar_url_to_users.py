"""add avatar url to users

Revision ID: 5bfa399b5973
Revises: 7ae8a893652f
Create Date: 2026-07-25 11:48:09.065251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bfa399b5973'
down_revision: Union[str, Sequence[str], None] = '7ae8a893652f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 📌 Step 1: Add the avatar_url column to the users table
    op.add_column(
        'users',
        sa.Column('avatar_url', sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 📌 Step 1: Drop the avatar_url column from the users table
    op.drop_column('users', 'avatar_url')
