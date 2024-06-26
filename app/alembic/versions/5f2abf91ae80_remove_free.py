"""remove_free

Revision ID: 5f2abf91ae80
Revises: 636fc5d3fa36
Create Date: 2024-06-07 10:52:45.591289

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5f2abf91ae80"
down_revision: Union[str, None] = "636fc5d3fa36"
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
