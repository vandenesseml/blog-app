"""add name attribute to user

Revision ID: 2080bd9b600d
Revises: 11c41accc66b
Create Date: 2018-11-01 11:49:21.472566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2080bd9b600d'
down_revision = '11c41accc66b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('full_name', sa.String(length=240), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=True)
    op.create_index(op.f('ix_user_full_name'), 'user', ['full_name'], unique=True)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_full_name'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'full_name')
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###