"""rename voice_time to user_stats

Revision ID: 2c761462d33e
Revises: 9c0b402da2f9
Create Date: 2025-06-02 04:19:15.493915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c761462d33e'
down_revision: Union[str, None] = '9c0b402da2f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('voice_time', 'user_stats')


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('user_stats', 'voice_time')
