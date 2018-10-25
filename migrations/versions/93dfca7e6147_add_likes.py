"""add likes

Revision ID: 93dfca7e6147
Revises: 7f705488d218
Create Date: 2018-10-25 13:18:18.749270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93dfca7e6147'
down_revision = '7f705488d218'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('likes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'likes')
    # ### end Alembic commands ###