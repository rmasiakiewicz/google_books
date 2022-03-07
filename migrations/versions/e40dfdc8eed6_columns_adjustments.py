"""Columns adjustments

Revision ID: e40dfdc8eed6
Revises: 747cc0f3e312
Create Date: 2022-03-07 01:15:27.418203

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e40dfdc8eed6'
down_revision = '747cc0f3e312'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('book', 'publication_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('book', 'number_of_pages',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('book', 'title', existing_type=sa.String(length=300), nullable=False)
    op.alter_column('book', 'preview_link', existing_type=sa.String(length=200), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('book', 'number_of_pages',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('book', 'publication_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('book', 'title', existing_type=sa.String(length=100), nullable=False)
    op.alter_column('book', 'preview_link', existing_type=sa.String(length=100), nullable=False)
    # ### end Alembic commands ###
