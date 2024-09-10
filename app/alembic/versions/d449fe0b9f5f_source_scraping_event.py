"""source_scraping_event

Revision ID: d449fe0b9f5f
Revises: 04111bbfe33b
Create Date: 2024-09-10 12:22:16.101163

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d449fe0b9f5f"
down_revision: Union[str, None] = "04111bbfe33b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "scrapereventdata",
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("scrapereventdata", "source")
    # ### end Alembic commands ###
