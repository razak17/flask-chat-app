"""empty message

Revision ID: 4f431dcd3c84
Revises: d5d66f442c91
Create Date: 2020-03-17 06:21:40.343991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f431dcd3c84'
down_revision = 'd5d66f442c91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('entry')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('room', sa.INTEGER(), nullable=False),
    sa.Column('date_joined', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###