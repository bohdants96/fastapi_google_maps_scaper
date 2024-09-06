"""people-lead, work, house

Revision ID: 690311c1c05d
Revises: 9a3dea6af407
Create Date: 2024-08-30 11:44:38.049369

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "690311c1c05d"
down_revision: Union[str, None] = "9a3dea6af407"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "house",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "address", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("price", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "peoplelead",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("phones", sa.JSON(), nullable=True),
        sa.Column("emails", sa.JSON(), nullable=True),
        sa.Column("works_id", sa.JSON(), nullable=True),
        sa.Column("house_id", sa.Integer(), nullable=True),
        sa.Column("scraped_date", sa.DateTime(), nullable=False),
        sa.Column("received_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["house_id"],
            ["house.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "work",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "company_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "position", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("work_from", sa.DateTime(), nullable=True),
        sa.Column("work_to", sa.DateTime(), nullable=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["person_id"],
            ["peoplelead.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("work")
    op.drop_table("peoplelead")
    op.drop_table("house")
    # ### end Alembic commands ###
