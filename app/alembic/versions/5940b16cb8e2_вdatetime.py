"""вdatetime

Revision ID: 5940b16cb8e2
Revises: be0971ab9fe0
Create Date: 2024-06-12 21:08:03.450523

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5940b16cb8e2"
down_revision: Union[str, None] = "be0971ab9fe0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "businesslead",
        "received_date",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "businesslead",
        "received_date",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    # ### end Alembic commands ###
