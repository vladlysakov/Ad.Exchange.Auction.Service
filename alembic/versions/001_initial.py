"""initial

Revision ID: 001
Revises: 
Create Date: 2025-01-10 12:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'supplies',
        sa.Column('id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supplies_id'), 'supplies', ['id'])
    
    op.create_table(
        'bidders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bidders_id'), 'bidders', ['id'])
    op.create_index(op.f('ix_bidders_country'), 'bidders', ['country'])
    
    op.create_table(
        'supply_bidder',
        sa.Column('supply_id', sa.String(), nullable=False),
        sa.Column('bidder_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['bidder_id'], ['bidders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['supply_id'], ['supplies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('supply_id', 'bidder_id')
    )


def downgrade() -> None:
    op.drop_table('supply_bidder')
    op.drop_index(op.f('ix_bidders_country'), table_name='bidders')
    op.drop_index(op.f('ix_bidders_id'), table_name='bidders')
    op.drop_table('bidders')
    op.drop_index(op.f('ix_supplies_id'), table_name='supplies')
    op.drop_table('supplies')
