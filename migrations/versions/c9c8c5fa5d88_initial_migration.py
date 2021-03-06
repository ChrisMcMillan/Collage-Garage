"""Initial Migration

Revision ID: c9c8c5fa5d88
Revises: 
Create Date: 2021-09-09 14:35:52.770982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9c8c5fa5d88'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users_data', sa.Column('favorite_color', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users_data', 'favorite_color')
    # ### end Alembic commands ###
