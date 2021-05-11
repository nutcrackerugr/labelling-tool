"""Added roles to AppUser

Revision ID: 49a1b2d356cf
Revises: bb9c3ff766c6
Create Date: 2021-05-11 10:03:57.620954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49a1b2d356cf'
down_revision = 'bb9c3ff766c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('app_user', sa.Column('roles', sa.String(256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_user', 'roles')
    # ### end Alembic commands ###
