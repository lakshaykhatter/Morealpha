"""add exchange to ticker

Revision ID: 02300d49db40
Revises: db1176d8ca88
Create Date: 2019-04-05 16:02:59.737495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02300d49db40'
down_revision = 'db1176d8ca88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticker', sa.Column('exchange', sa.String(length=200), nullable=True))
    op.create_index(op.f('ix_ticker_exchange'), 'ticker', ['exchange'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ticker_exchange'), table_name='ticker')
    op.drop_column('ticker', 'exchange')
    # ### end Alembic commands ###
