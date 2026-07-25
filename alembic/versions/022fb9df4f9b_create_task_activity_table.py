"""create task activity table

Revision ID: 022fb9df4f9b
Revises: 7d5c9cfcd93c
Create Date: 2026-07-25 11:59:41.770174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '022fb9df4f9b'
down_revision: Union[str, Sequence[str], None] = '7d5c9cfcd93c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 📌 Step 1: Create the task_activity table with foreign key constraints
    op.create_table(
        'task_activity',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('diff', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 📌 Step 2: Create index on task_id to optimize activity trail queries
    op.create_index('ix_task_activity_task_id', 'task_activity', ['task_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 📌 Step 1: Drop index on task_id
    op.drop_index('ix_task_activity_task_id', table_name='task_activity')

    # 📌 Step 2: Drop the task_activity table
    op.drop_table('task_activity')
