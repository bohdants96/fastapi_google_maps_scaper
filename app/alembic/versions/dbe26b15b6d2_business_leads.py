"""business_leads

Revision ID: dbe26b15b6d2
Revises: fce3c1a5ac73
Create Date: 2024-06-03 10:26:41.242816

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "dbe26b15b6d2"
down_revision: Union[str, None] = "fce3c1a5ac73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "businesslead",
        sa.Column(
            "company_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "company_address",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "company_phone", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "website", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "business_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "country", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("county", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "zip_code", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("scraped_date", sa.DateTime(), nullable=False),
        sa.Column("received_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_businesslead_business_type"),
        "businesslead",
        ["business_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_businesslead_city"), "businesslead", ["city"], unique=False
    )
    op.create_index(
        op.f("ix_businesslead_country"),
        "businesslead",
        ["country"],
        unique=False,
    )
    op.create_index(
        op.f("ix_businesslead_state"), "businesslead", ["state"], unique=False
    )
    op.drop_index("ix_scrapeddata_business_type", table_name="scrapeddata")
    op.drop_index("ix_scrapeddata_city", table_name="scrapeddata")
    op.drop_index("ix_scrapeddata_country", table_name="scrapeddata")
    op.drop_index("ix_scrapeddata_state", table_name="scrapeddata")
    op.drop_table("scrapeddata")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "scrapeddata",
        sa.Column(
            "company_name", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "business_type", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "company_address",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "company_phone", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "zip_code", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("website", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "country", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column("city", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("county", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "scraped_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "received_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="scrapeddata_pkey"),
    )
    op.create_index(
        "ix_scrapeddata_state", "scrapeddata", ["state"], unique=False
    )
    op.create_index(
        "ix_scrapeddata_country", "scrapeddata", ["country"], unique=False
    )
    op.create_index(
        "ix_scrapeddata_city", "scrapeddata", ["city"], unique=False
    )
    op.create_index(
        "ix_scrapeddata_business_type",
        "scrapeddata",
        ["business_type"],
        unique=False,
    )
    op.drop_index(op.f("ix_businesslead_state"), table_name="businesslead")
    op.drop_index(op.f("ix_businesslead_country"), table_name="businesslead")
    op.drop_index(op.f("ix_businesslead_city"), table_name="businesslead")
    op.drop_index(
        op.f("ix_businesslead_business_type"), table_name="businesslead"
    )
    op.drop_table("businesslead")
    # ### end Alembic commands ###