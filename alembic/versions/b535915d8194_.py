"""

Revision ID: b535915d8194
Revises: 504fc01e4d11
Create Date: 2024-01-05 00:42:07.369985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b535915d8194'
down_revision: Union[str, None] = '504fc01e4d11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ipfs_cid', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ipfs_cid')
    )
    op.create_table('users_assets',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('asset_id', sa.Integer(), nullable=False),
    sa.Column('nft_id', sa.BigInteger(), nullable=False),
    sa.Column('is_locked', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.auth_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('nft_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_assets')
    op.drop_table('assets')
    # ### end Alembic commands ###
