"""create users and interviews

Revision ID: 29a7fbe1ba9b
Revises: 96c1dfd5aa71
Create Date: 2025-09-16 21:06:38.406979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29a7fbe1ba9b'
down_revision: Union[str, None] = '96c1dfd5aa71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
