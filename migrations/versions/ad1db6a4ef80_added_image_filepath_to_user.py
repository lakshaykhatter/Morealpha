"""added image filepath to user

Revision ID: ad1db6a4ef80
Revises: fa71bf3a8fc7
Create Date: 2019-04-03 15:15:38.333090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad1db6a4ef80'
down_revision = 'fa71bf3a8fc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('image_file', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'image_file')
    # ### end Alembic commands ###
