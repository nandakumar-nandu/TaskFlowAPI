"""create categories and tags tables and update tasks

Revision ID: 7ae8a893652f
Revises: 6001dfc821dc
Create Date: 2026-07-18 08:43:17.320815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ae8a893652f'
down_revision: Union[str, Sequence[str], None] = '6001dfc821dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ⚙️ 1. Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ⚙️ 2. Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'user_id', name='uq_tag_name_user_id')
    )

    # ⚙️ 3. Create task_tags association table (junction table)
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('tag_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # ⚙️ 4. Update tasks table
    # Add category_id nullable column
    op.add_column('tasks', sa.Column('category_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_tasks_category_id_categories',
        'tasks', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add database indexes on frequently filtered columns
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('ix_tasks_priority', 'tasks', ['priority'], unique=False)
    op.create_index('ix_tasks_category_id', 'tasks', ['category_id'], unique=False)
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # ❌ 1. Drop indexes on tasks table
    op.drop_index('ix_tasks_due_date', table_name='tasks')
    op.drop_index('ix_tasks_category_id', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')

    # ❌ 2. Drop category_id foreign key constraint and column from tasks table
    op.drop_constraint('fk_tasks_category_id_categories', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'category_id')

    # ❌ 3. Drop tables in reverse order
    op.drop_table('task_tags')
    op.drop_table('tags')
    op.drop_table('categories')

