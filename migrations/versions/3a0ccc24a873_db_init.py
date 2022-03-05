"""db init

Revision ID: 3a0ccc24a873
Revises: 
Create Date: 2022-03-05 16:21:25.508576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a0ccc24a873"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "author",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "language",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "book",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("publication_date", sa.DateTime(), nullable=False),
        sa.Column("number_of_pages", sa.Integer(), nullable=False),
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.Column("preview_link", sa.String(length=100), nullable=True),
        sa.Column("isbn_10", sa.String(length=10), nullable=True),
        sa.Column("isbn_13", sa.String(length=13), nullable=True),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "book_author",
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["author.id"],
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["book.id"],
        ),
        sa.PrimaryKeyConstraint("author_id", "book_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("book_author")
    op.drop_table("book")
    op.drop_table("language")
    op.drop_table("author")
    # ### end Alembic commands ###