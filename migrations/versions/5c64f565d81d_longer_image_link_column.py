"""longer image link column

Revision ID: 5c64f565d81d
Revises: 91148411c4f9
Create Date: 2022-03-08 20:55:09.958514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c64f565d81d"
down_revision = "91148411c4f9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "book",
        "image_link",
        existing_type=sa.VARCHAR(length=200),
        type_=sa.String(length=400),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "book",
        "image_link",
        existing_type=sa.String(length=400),
        type_=sa.VARCHAR(length=200),
        existing_nullable=True,
    )
    # ### end Alembic commands ###
