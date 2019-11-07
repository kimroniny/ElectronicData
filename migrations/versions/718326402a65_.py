"""empty message

Revision ID: 718326402a65
Revises: 
Create Date: 2019-11-01 17:55:27.050348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '718326402a65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=64), nullable=True),
                    sa.Column('email', sa.String(length=120), nullable=True),
                    sa.Column('password_hash', sa.String(
                        length=128), nullable=True),
                    sa.Column('balance', sa.Integer(), nullable=True),
                    sa.Column('about_me', sa.String(
                        length=140), nullable=True),
                    sa.Column('last_seen', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user',
                    ['username'], unique=True)
    op.create_table('resource',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('body', sa.String(length=140), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_resource_timestamp'),
                    'resource', ['timestamp'], unique=False)
    op.create_table('buys',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('resource_id', sa.Integer(), nullable=True),
                    sa.Column('consumer_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['consumer_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(
                        ['resource_id'], ['resource.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('transfers',
                    sa.Column('transfer_id', sa.Integer(), nullable=True),
                    sa.Column('transfee_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['transfee_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['transfer_id'], ['buys.id'], )
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transfers')
    op.drop_table('buys')
    op.drop_index(op.f('ix_resource_timestamp'), table_name='resource')
    op.drop_table('resource')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###