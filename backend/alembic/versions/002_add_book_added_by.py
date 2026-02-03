"""add book added_by_user_id

Revision ID: 002
Revises: 001
Create Date: 2025-02-02

"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "books",
        sa.Column("added_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade():
    op.drop_column("books", "added_by_user_id")
