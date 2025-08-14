"""created user_stats_dev table and transfered few filelds from user_stats to it

Revision ID: 70256e971bdc
Revises: 1ad438a71e55
Create Date: 2025-08-13 17:19:05.725855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '70256e971bdc'
down_revision: Union[str, None] = '1ad438a71e55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем новую колонку для переименования total_time
    op.add_column('user_stats', sa.Column('time_in_voice', sa.Float(), nullable=True))

    # 2. Создаём новую таблицу user_stats_dev
    op.drop_table('user_stats_dev')
    op.create_table(
        'user_stats_dev',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('last_join', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_played_day', sa.Integer(), nullable=True),
        sa.Column('legendary_cooldown_left', sa.Integer(), nullable=True),
        sa.Column('legendary_cooldown_total', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id', 'guild_id'],
            ['user_stats.user_id', 'user_stats.guild_id']
        ),
        sa.UniqueConstraint('user_id', 'guild_id')  # чтобы связь была один-к-одному
    )

    # 3. Копируем данные total_time → time_in_voice
    op.execute("""
        UPDATE user_stats
        SET time_in_voice = total_time
    """)

    # 4. Копируем last_join и last_played_day в новую таблицу
    op.execute("""
        INSERT INTO user_stats_dev (user_id, guild_id, last_join, last_played_day)
        SELECT user_id, guild_id, last_join, last_played_day
        FROM user_stats
    """)

    # 5. После копирования удаляем старые колонки
    op.drop_column('user_stats', 'total_time')
    op.drop_column('user_stats', 'last_join')
    op.drop_column('user_stats', 'last_played_day')
    # ### end Alembic commands ###


def downgrade() -> None:
    # 1. Возвращаем старые колонки
    op.add_column('user_stats', sa.Column('total_time', sa.Float(), nullable=True))
    op.add_column('user_stats', sa.Column('last_join', sa.TIMESTAMP(), nullable=True))
    op.add_column('user_stats', sa.Column('last_played_day', sa.Integer(), nullable=True))

    # 2. Переносим данные обратно
    op.execute("""
        UPDATE user_stats
        SET total_time = time_in_voice
    """)

    op.execute("""
        UPDATE user_stats AS us
        SET last_join = usd.last_join,
            last_played_day = usd.last_played_day
        FROM user_stats_dev AS usd
        WHERE us.user_id = usd.user_id
    """)

    # 3. Удаляем новую колонку и новую таблицу
    op.drop_column('user_stats', 'time_in_voice')
    op.drop_table('user_stats_dev')
