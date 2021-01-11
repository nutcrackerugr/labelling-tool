"""Added creation and completion date to Tasks

Revision ID: f703c7265e90
Revises: ee7f9f1ad865
Create Date: 2021-01-11 17:58:00.037554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f703c7265e90'
down_revision = 'ee7f9f1ad865'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'created_at')
    op.drop_column('task', 'completed_at')
    # ### end Alembic commands ###