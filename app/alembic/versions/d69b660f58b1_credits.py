"""credits

Revision ID: d69b660f58b1
Revises: 81b42b47d626
Create Date: 2024-05-29 15:23:28.569776

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d69b660f58b1"
down_revision: Union[str, None] = "81b42b47d626"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "credits",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("total_credit", sa.Integer(), nullable=False),
        sa.Column("used_credit", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("credits")
    # ### end Alembic commands ###
