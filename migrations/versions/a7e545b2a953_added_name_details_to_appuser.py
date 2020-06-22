"""Added name details to AppUser

Revision ID: a7e545b2a953
Revises: c174a09daa49
Create Date: 2020-06-22 13:44:19.424961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7e545b2a953'
down_revision = 'c174a09daa49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('app_user', sa.Column('name', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_user', 'name')
    # ### end Alembic commands ###
