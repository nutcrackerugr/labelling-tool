"""empty message

Revision ID: 9cf172078b82
Revises: c768b780ba75
Create Date: 2020-06-10 11:47:17.388668

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9cf172078b82'
down_revision = 'c768b780ba75'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE label SET bgcolorhex = 'f8f9fa' WHERE bgcolorhex IS NULL")
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('label', 'bgcolorhex',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=6),
               nullable=False)
    op.add_column('tweet', sa.Column('rank', sa.Float(), nullable=False))
    op.create_index(op.f('ix_tweet_rank'), 'tweet', ['rank'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tweet_rank'), table_name='tweet')
    op.drop_column('tweet', 'rank')
    op.alter_column('label', 'bgcolorhex',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=6),
               nullable=True)
    # ### end Alembic commands ###
