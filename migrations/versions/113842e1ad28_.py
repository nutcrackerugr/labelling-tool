"""empty message

Revision ID: 113842e1ad28
Revises: 
Create Date: 2020-01-22 12:23:04.171524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '113842e1ad28'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('label',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('values', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('revoked_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_str', sa.String(length=19), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('screen_name', sa.String(length=100), nullable=False),
    sa.Column('location', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('protected', sa.Boolean(), nullable=False),
    sa.Column('profile_image_url_https', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_str')
    )
    op.create_table('tweet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_str', sa.String(length=19), nullable=False),
    sa.Column('full_text', sa.Text(), nullable=False),
    sa.Column('truncated', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.String(length=30), nullable=False),
    sa.Column('in_reply_to_status_id', sa.String(length=19), nullable=True),
    sa.Column('in_reply_to_user_id', sa.String(length=19), nullable=True),
    sa.Column('geo', sa.Text(), nullable=True),
    sa.Column('coordinates', sa.Text(), nullable=True),
    sa.Column('retweet_count', sa.Integer(), nullable=True),
    sa.Column('favorite_count', sa.Integer(), nullable=True),
    sa.Column('lang', sa.String(length=30), nullable=True),
    sa.Column('retweeted', sa.Boolean(), nullable=True),
    sa.Column('favorited', sa.Boolean(), nullable=True),
    sa.Column('labels', sa.PickleType(), nullable=True),
    sa.Column('highlights', sa.PickleType(), nullable=True),
    sa.Column('tags', sa.PickleType(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_str')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tweet')
    op.drop_table('user')
    op.drop_table('revoked_token')
    op.drop_table('label')
    op.drop_table('app_user')
    # ### end Alembic commands ###
