"""initiated database

Revision ID: 4cfefcc5aaef
Revises: 
Create Date: 2023-11-01 23:33:01.637983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cfefcc5aaef'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('auth_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('auth_id')
    )
    op.create_table('games',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('config', sa.JSON(), nullable=True),
    sa.Column('game_started_time', sa.DateTime(), nullable=False),
    sa.Column('game_ended_time', sa.DateTime(), nullable=True),
    sa.Column('winner_id', sa.Integer(), nullable=True),
    sa.Column('history', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wallets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('address', sa.String(length=64), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_to_games',
    sa.Column('users', sa.Integer(), nullable=True),
    sa.Column('games', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['games'], ['games.id'], ),
    sa.ForeignKeyConstraint(['users'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_to_games')
    op.drop_table('wallets')
    op.drop_table('games')
    op.drop_table('users')
    # ### end Alembic commands ###
