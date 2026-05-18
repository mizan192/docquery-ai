"""add missing columns

Revision ID: 334c57a3bfea
Revises: 
Create Date: 2026-05-19 01:47:37.443991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '334c57a3bfea'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # add user_id column
    # step 1 - add as nullable first
    op.add_column('documents', sa.Column('user_id', sa.Integer(), nullable=True))
    # step 2 - fill existing rows with default user_id=1
    op.execute("UPDATE documents SET user_id = 1 WHERE user_id IS NULL")
    # step 3 - make not nullable
    op.alter_column('documents', 'user_id', nullable=False)
    # step 4 - add foreign key
    op.create_foreign_key(None, 'documents', 'users', ['user_id'], ['id'])

    # add status column
    # step 1 - add as nullable first
    op.add_column('documents', sa.Column('status', sa.String(), nullable=True))
    # step 2 - fill existing rows with default status
    op.execute("UPDATE documents SET status = 'completed' WHERE status IS NULL")
    # step 3 - make not nullable
    op.alter_column('documents', 'status', nullable=False)

    # add error_message column (nullable so no default needed)
    op.add_column('documents', sa.Column('error_message', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_constraint(None, 'documents', type_='foreignkey')
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'status')
    op.drop_column('documents', 'user_id')

