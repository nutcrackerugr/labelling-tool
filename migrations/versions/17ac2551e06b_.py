"""empty message

Revision ID: 17ac2551e06b
Revises: 
Create Date: 2019-12-11 15:28:07.515138

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '17ac2551e06b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('revoked_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('id_str', table_name='user')
    op.drop_table('user')
    op.drop_index('id_str', table_name='tweet')
    op.drop_table('tweet')
    op.drop_index('name', table_name='label')
    op.drop_table('label')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('label',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'label', ['name'], unique=True)
    op.create_table('tweet',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('id_str', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=19), nullable=False),
    sa.Column('full_text', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=False),
    sa.Column('truncated', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('created_at', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=30), nullable=False),
    sa.Column('in_reply_to_status_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=19), nullable=True),
    sa.Column('in_reply_to_user_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=19), nullable=True),
    sa.Column('geo', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.Column('coordinates', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.Column('retweet_count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('favorite_count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('lang', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=30), nullable=True),
    sa.Column('retweeted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('favorited', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('labels', sa.BLOB(), nullable=True),
    sa.Column('highlights', sa.BLOB(), nullable=True),
    sa.Column('tags', sa.BLOB(), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.CheckConstraint('`favorited` in (0,1)', name='CONSTRAINT_3'),
    sa.CheckConstraint('`retweeted` in (0,1)', name='CONSTRAINT_2'),
    sa.CheckConstraint('`truncated` in (0,1)', name='CONSTRAINT_1'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='tweet_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('id_str', 'tweet', ['id_str'], unique=True)
    op.create_table('user',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('id_str', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=19), nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('screen_name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('location', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.Column('description', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.Column('protected', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('profile_image_url_https', mysql.TEXT(collation='utf8mb4_unicode_ci'), nullable=True),
    sa.CheckConstraint('`protected` in (0,1)', name='CONSTRAINT_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('id_str', 'user', ['id_str'], unique=True)
    op.drop_table('revoked_token')
    # ### end Alembic commands ###
