"""search_history_2

Revision ID: e1505ad33dd7
Revises: 8c8c8022ac05
Create Date: 2024-06-24 16:09:58.486033

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1505ad33dd7"
down_revision: Union[str, None] = "8c8c8022ac05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "searchhistory",
        sa.Column(
            "source", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("searchhistory", "source")
    # ### end Alembic commands ###
