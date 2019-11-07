"""empty message

Revision ID: 6f4ed5c9157c
Revises: 8f446dbe2169
Create Date: 2019-11-01 22:53:08.148837

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6f4ed5c9157c'
down_revision = '8f446dbe2169'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('certs',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('resource_id', sa.Integer(), nullable=True),
                    sa.Column('consumer_id', sa.Integer(), nullable=True),
                    sa.Column('transfer_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['consumer_id'], ['user.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(
                        ['resource_id'], ['resource.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['transfer_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.drop_table('transfers')
    op.drop_table('buys')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('buys',
                    sa.Column('id', mysql.INTEGER(display_width=11),
                              autoincrement=True, nullable=False),
                    sa.Column('resource_id', mysql.INTEGER(
                        display_width=11), autoincrement=False, nullable=True),
                    sa.Column('consumer_id', mysql.INTEGER(display_width=11),
                              autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(
                        ['consumer_id'], ['user.id'], name='buys_ibfk_1'),
                    sa.ForeignKeyConstraint(
                        ['resource_id'], ['resource.id'], name='buys_ibfk_2'),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_default_charset='utf8',
                    mysql_engine='InnoDB'
                    )
    op.create_table('transfers',
                    sa.Column('transfer_id', mysql.INTEGER(
                        display_width=11), autoincrement=False, nullable=True),
                    sa.Column('transfee_id', mysql.INTEGER(
                        display_width=11), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(
                        ['transfee_id'], ['user.id'], name='transfers_ibfk_1'),
                    sa.ForeignKeyConstraint(
                        ['transfer_id'], ['buys.id'], name='transfers_ibfk_2'),
                    mysql_default_charset='utf8',
                    mysql_engine='InnoDB'
                    )
    op.drop_table('certs')
    # ### end Alembic commands ###
