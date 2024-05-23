"""empty message

Revision ID: 637217d3d77b
Revises: 5ad88f51406c
Create Date: 2024-05-23 20:16:24.802927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '637217d3d77b'
down_revision: Union[str, None] = '5ad88f51406c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scrapeddata', 'company_phone',
               existing_type=sa.INTEGER(),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               existing_nullable=True)
    op.alter_column('scrapeddata', 'zip_code',
               existing_type=sa.INTEGER(),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scrapeddata', 'zip_code',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('scrapeddata', 'company_phone',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
