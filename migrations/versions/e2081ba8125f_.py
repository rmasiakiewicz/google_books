"""empty message

Revision ID: e2081ba8125f
Revises: e40dfdc8eed6
Create Date: 2022-03-07 01:30:01.715320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e2081ba8125f"
down_revision = "e40dfdc8eed6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "book",
        "title",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=300),
        existing_nullable=False,
    )
    op.alter_column(
        "book",
        "preview_link",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=200),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "book",
        "preview_link",
        existing_type=sa.String(length=200),
        type_=sa.VARCHAR(length=100),
        nullable=False,
    )
    op.alter_column(
        "book",
        "title",
        existing_type=sa.String(length=300),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )
    # ### end Alembic commands ###