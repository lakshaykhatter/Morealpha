"""added title to Post

Revision ID: cf2b45a6e851
Revises: be48e2ebd998
Create Date: 2019-04-01 17:58:43.774138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf2b45a6e851'
down_revision = 'be48e2ebd998'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('title', sa.String(length=200), nullable=True))
    op.create_index(op.f('ix_post_title'), 'post', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_title'), table_name='post')
    op.drop_column('post', 'title')
    # ### end Alembic commands ###
