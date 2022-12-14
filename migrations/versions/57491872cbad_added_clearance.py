"""Added clearance

Revision ID: 57491872cbad
Revises: f38b55cd756c
Create Date: 2021-01-19 10:55:47.964162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57491872cbad'
down_revision = 'f38b55cd756c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('app_user', sa.Column('clearance', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_user', 'clearance')
    # ### end Alembic commands ###
