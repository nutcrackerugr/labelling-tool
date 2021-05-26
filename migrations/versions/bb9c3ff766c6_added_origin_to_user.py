"""Added origin to User

Revision ID: bb9c3ff766c6
Revises: e15849bb1dff
Create Date: 2021-05-03 19:41:38.207349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb9c3ff766c6'
down_revision = 'e15849bb1dff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('origin', sa.PickleType(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'origin')
    # ### end Alembic commands ###