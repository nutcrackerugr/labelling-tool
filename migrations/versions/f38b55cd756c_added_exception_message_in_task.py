"""Added exception message in task

Revision ID: f38b55cd756c
Revises: 2a340de12c23
Create Date: 2021-01-12 16:46:40.992871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f38b55cd756c'
down_revision = '2a340de12c23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('exception_str', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'exception_str')
    # ### end Alembic commands ###