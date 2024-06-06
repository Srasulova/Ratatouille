"""Add photos column to Restaurant

Revision ID: 0545605dc7cf
Revises: 
Create Date: 2024-06-05 16:35:34.495270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0545605dc7cf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('restaurants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photos', sa.Text(), nullable=True))

    with op.batch_alter_table('user_restaurants', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('restaurant_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_restaurants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), nullable=False))
        batch_op.alter_column('restaurant_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('restaurants', schema=None) as batch_op:
        batch_op.drop_column('photos')

    # ### end Alembic commands ###
