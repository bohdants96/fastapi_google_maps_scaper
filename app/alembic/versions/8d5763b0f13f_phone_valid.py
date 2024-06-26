"""phone valid

Revision ID: 8d5763b0f13f
Revises: faab929e9c8f
Create Date: 2024-06-18 10:28:30.535995

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8d5763b0f13f"
down_revision: Union[str, None] = "faab929e9c8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column(
            "mobile_phone", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "instagram", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "twitter", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "facebook", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "linkedin", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.alter_column(
        "user", "free_credit", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user", "free_credit", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("user", "linkedin")
    op.drop_column("user", "facebook")
    op.drop_column("user", "twitter")
    op.drop_column("user", "instagram")
    op.drop_column("user", "mobile_phone")
    # ### end Alembic commands ###