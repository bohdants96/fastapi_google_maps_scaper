"""transactions

Revision ID: 335e8ae42212
Revises: d69b660f58b1
Create Date: 2024-05-29 15:32:55.083363

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "335e8ae42212"
down_revision: Union[str, None] = "d69b660f58b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "stripe_payment_id",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "currency", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "status", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transactions_stripe_payment_id"),
        "transactions",
        ["stripe_payment_id"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_transactions_stripe_payment_id"), table_name="transactions"
    )
    op.drop_table("transactions")
    # ### end Alembic commands ###
