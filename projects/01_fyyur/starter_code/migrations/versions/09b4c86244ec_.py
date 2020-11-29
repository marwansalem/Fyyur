"""empty message

Revision ID: 09b4c86244ec
Revises: 327023e9cf01
Create Date: 2020-11-29 04:07:55.216014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b4c86244ec'
down_revision = '327023e9cf01'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('Show')
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist', sa.Integer(), nullable=False),
    sa.Column('venue', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['artist'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
