"""Added help text to labels

Revision ID: 4de5ff2b1f2e
Revises: a7e545b2a953
Create Date: 2020-07-01 17:27:15.612880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4de5ff2b1f2e'
down_revision = 'a7e545b2a953'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('label', sa.Column('help_text', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('label', 'help_text')
    # ### end Alembic commands ###
