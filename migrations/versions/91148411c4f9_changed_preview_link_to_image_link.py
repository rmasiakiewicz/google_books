"""changed preview link to image link

Revision ID: 91148411c4f9
Revises: 0b00a2afdddd
Create Date: 2022-03-08 20:53:21.408482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "91148411c4f9"
down_revision = "0b00a2afdddd"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("book", sa.Column("image_link", sa.String(length=200), nullable=True))
    op.drop_column("book", "preview_link")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "book",
        sa.Column(
            "preview_link", sa.VARCHAR(length=200), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("book", "image_link")
    # ### end Alembic commands ###