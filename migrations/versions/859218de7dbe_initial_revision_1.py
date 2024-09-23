"""Initial revision 1

Revision ID: 859218de7dbe
Revises: 
Create Date: 2024-09-23 20:23:29.074176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '859218de7dbe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='zoom_bot'
    )
    op.create_table('temporary_conference_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tg', sa.BigInteger(), nullable=False),
    sa.Column('date', sa.String(length=320), nullable=True),
    sa.Column('choosen_zoom', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.String(length=320), nullable=True),
    sa.Column('duration_meeting', sa.Float(), nullable=True),
    sa.Column('autorecord_flag', sa.String(length=320), nullable=True),
    sa.Column('illegal_intervals', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='zoom_bot'
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tg', sa.BigInteger(), nullable=False),
    sa.Column('nickname', sa.String(length=320), nullable=False),
    sa.Column('fullname', sa.String(length=320), nullable=False),
    sa.Column('fio', sa.String(length=320), nullable=False),
    sa.Column('date_reg', sa.DateTime(), nullable=False),
    sa.Column('number_created_conferences', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='zoom_bot'
    )
    op.create_table('created_conferences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('date_creation', sa.TIMESTAMP(), nullable=False),
    sa.Column('name', sa.String(length=320), nullable=False),
    sa.Column('account', sa.String(length=320), nullable=False),
    sa.Column('start_time', sa.TIMESTAMP(), nullable=False),
    sa.Column('duration', sa.String(length=320), nullable=False),
    sa.Column('autorecord', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['zoom_bot.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='zoom_bot'
    )
    op.create_table('user_chats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('id_topic_chat', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['zoom_bot.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='zoom_bot'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_chats', schema='zoom_bot')
    op.drop_table('created_conferences', schema='zoom_bot')
    op.drop_table('users', schema='zoom_bot')
    op.drop_table('temporary_conference_data', schema='zoom_bot')
    op.drop_table('admin_group', schema='zoom_bot')
    # ### end Alembic commands ###