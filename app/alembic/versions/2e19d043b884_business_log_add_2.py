"""business_log_add_2

Revision ID: 2e19d043b884
Revises: f79929f5f2c9
Create Date: 2024-06-24 15:52:03.711952

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e19d043b884"
down_revision: Union[str, None] = "f79929f5f2c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("businessleadaccesslog", "free_access")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "businessleadaccesslog",
        sa.Column(
            "free_access", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
    )
    # ### end Alembic commands ###
