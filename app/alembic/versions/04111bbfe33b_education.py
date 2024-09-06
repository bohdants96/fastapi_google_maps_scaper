"""education

Revision ID: 04111bbfe33b
Revises: a40856c981f9
Create Date: 2024-09-06 10:46:00.331048

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "04111bbfe33b"
down_revision: Union[str, None] = "a40856c981f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "education",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "college", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("degree", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "from_date", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "to_date", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "peoplelead", sa.Column("education_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "peoplelead", "education", ["education_id"], ["id"]
    )
    op.alter_column(
        "work",
        "work_from",
        existing_type=postgresql.TIMESTAMP(),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=True,
    )
    op.alter_column(
        "work",
        "work_to",
        existing_type=postgresql.TIMESTAMP(),
        type_=sqlmodel.sql.sqltypes.AutoString(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "work",
        "work_to",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.alter_column(
        "work",
        "work_from",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.drop_constraint(None, "peoplelead", type_="foreignkey")
    op.drop_column("peoplelead", "education_id")
    op.drop_table("education")
    # ### end Alembic commands ###
