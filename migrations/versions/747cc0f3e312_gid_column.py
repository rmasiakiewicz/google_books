"""gid column

Revision ID: 747cc0f3e312
Revises: 3a0ccc24a873
Create Date: 2022-03-06 21:52:17.355706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "747cc0f3e312"
down_revision = "3a0ccc24a873"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "author", ["name"])
    op.add_column("book", sa.Column("gid", sa.String(length=50), nullable=False))
    op.create_unique_constraint(None, "book", ["isbn_13"])
    op.create_unique_constraint(None, "book", ["gid"])
    op.create_unique_constraint(None, "book", ["isbn_10"])
    op.create_unique_constraint(None, "language", ["name"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "language", type_="unique")
    op.drop_constraint(None, "book", type_="unique")
    op.drop_constraint(None, "book", type_="unique")
    op.drop_constraint(None, "book", type_="unique")
    op.drop_column("book", "gid")
    op.drop_constraint(None, "author", type_="unique")
    # ### end Alembic commands ###
