"""str

Revision ID: 2d8d5e4d01d7
Revises: f63713aad844
Create Date: 2024-06-10 17:06:17.100686

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2d8d5e4d01d7"
down_revision: Union[str, None] = "f63713aad844"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "reservedcredit",
        "task_id",
        existing_type=sa.INTEGER(),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "reservedcredit",
        "task_id",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
