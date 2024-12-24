"""Add nylas_session_id to User

Revision ID: 3be397649834
Revises: 
Create Date: 2024-12-22 10:21:34.749377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3be397649834'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nylas_grant_id', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('nylas_session_id', sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint(None, ['nylas_grant_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('nylas_session_id')
        batch_op.drop_column('nylas_grant_id')

    # ### end Alembic commands ###