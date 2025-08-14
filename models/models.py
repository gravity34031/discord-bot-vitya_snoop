from sqlalchemy import create_engine, Column, Integer, BigInteger, Float, Boolean, DateTime, String, SmallInteger, ForeignKey, JSON, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

from utils.constants import LEGENDARY_COOLDOWN_TOTAL

Base = declarative_base()

# class VoiceTime(Base):
#     __tablename__ = "voice_time"

#     user_id = Column(BigInteger, primary_key=True)
#     guild_id = Column(BigInteger, primary_key=True)
#     total_time = Column(Float, default=0)  # Общее время в минутах
#     last_join = Column(DateTime, nullable=True)  # Последний вход в голосовой
#     snoop_counter = Column(Integer, default=0)
#     last_played_day = Column(Integer, default=datetime.datetime.now().day)
    
# class Initials(Base):
#     __tablename__ = "initials"
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     value = Column(String)
#     type = Column(SmallInteger) # 0 - first name, 1 - last name, 2 - legendary full name
#     gender = Column(SmallInteger) # 0 - male, 1 - female, 2 - other
    
""" STATS """
class UserStats(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.dev_stats:
            self.dev_stats = UserStatsDev(user_id=self.user_id, guild_id=self.guild_id)

    __tablename__ = "user_stats"
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    saved_nicknames = Column(Integer, ForeignKey("saved_nicknames.id", ondelete="CASCADE"), nullable=True)
    
    snoop_counter = Column(Integer, default=0)
    time_in_voice = Column(Float, default=0)  # total time in voice in minutes
    coins = Column(Integer, default=0)
    coins_earned = Column(Integer, default=0)
    # expend more stats in model
    # top stats for STANDART achievements
    # UserStats.achievement_stats for special achivements
    achievement_stats = relationship("UserAchievementStats", back_populates="user_stats", uselist=False, cascade="all, delete-orphan")
    dev_stats = relationship("UserStatsDev", back_populates="user_stats", uselist=False, cascade="all, delete-orphan")


# expands UserStats adding additional fields needed for dev purposes
class UserStatsDev(Base):
    __tablename__ = "user_stats_dev"
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'guild_id'],
            ['user_stats.user_id', 'user_stats.guild_id'],
            ondelete="CASCADE"
        ),
    )

    last_join = Column(DateTime, nullable=True)  # last join in any voice channel
    rolls_since_rare = Column(Integer, default=0)
    legendary_cooldown_left = Column(Integer, default=0)
    legendary_cooldown_total = Column(Integer, default=20)
    roll_bonus_add = Column(Float, default=0.0) # [0, 1.0]
    roll_base_attempts = Column(Integer, default=0)     # base number of attempts to upgrade tier
    roll_attempts_factor = Column(Float, default=1.0)   # amount of attempts with high bust, max attempts~=attempts_factor+base_attempts
    roll_upgrade_chance = Column(Float, default=0.0)    # chance to upgrade tier by one attempt
    last_played_day = Column(Integer, default=lambda: datetime.datetime.now().day) # last day when welcome audio was played
    
    user_stats = relationship("UserStats", back_populates="dev_stats", uselist=False)


# expands UserStats for SPECIAL achievements
class UserAchievementStats(Base):
    __tablename__ = "user_achievement_stats"
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'guild_id'],
            ['user_stats.user_id', 'user_stats.guild_id'],
            ondelete="CASCADE"
        ),
    )
    
    afk_time = Column(Integer, default=0) # in minutes
    snoops_per_day = Column(Integer, default=0)
    last_snoop_time = Column(DateTime, nullable=True)
    nicks_added = Column(Integer, default=0)
    myths_collected = Column(Integer, default=0)
    legends_collected = Column(Integer, default=0)
    unluck_count = Column(Integer, default=0)
    snoops_after_legend = Column(Integer, default=0)
    # back relationship to stats of the user
    user_stats = relationship("UserStats", back_populates="achievement_stats", uselist=False)
    
    
class SavedNicknames(Base):
    __tablename__ = "saved_nicknames"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    
    
    
""" SEASON """
# class UserSeason(Base):
#     __tablename__ = "user_season"
    
#     user_id = Column(BigInteger, primary_key=True)
#     guild_id = Column(BigInteger, primary_key=True)
#     season_id = Column(Integer, ForeignKey("season.id"), primary_key=True)
#     # expand user stats in season
#     season_stats = relationship("UserSeasonStats", back_populates="user_season", uselist=False)
    
    
class UserSeasonStats(Base):
    __tablename__ = "user_season_stats"
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    season_id = Column(Integer, ForeignKey("season.id"), primary_key=True)
    
    time_in_voice = Column(Float, default=0) # in minutes
    snoop_counter = Column(Integer, default=0)
    coins_earned = Column(Integer, default=0)



class Season(Base):
    __tablename__ = "season"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    
    
    
""" USER ACHIEVEMENTS """
class UserAchievement(Base):
    __tablename__ = "user_achievement"
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    achievement_id = Column(Integer, ForeignKey("achievement.id", ondelete="CASCADE"), primary_key=True)
    date_awarded = Column(DateTime, nullable=False)
    
    achievement = relationship("Achievement", back_populates="user_achievements", passive_deletes=True)
    
    
class Achievement(Base):
    __tablename__ = "achievement"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    condition_description = Column(String, nullable=False, default="???") # way of getting achievement
    
    type = Column(String, nullable=False)   # standart/special
    event = Column(String, nullable=False)  # name of the statistic fields in UserStats or UserSeason
                                            # time_in_voice, snoop_counter, coins_earned, coins FOR UserStats
                                            # or time_in_voice_season, snoop_counter_season, coins_earned_season FOR UserSeason
    level = Column(Integer, nullable=False) # level describes not level of an achievement, but STATS needed to get it
    
    condition_data = Column(JSON, nullable=True) # condition data for special achievements
    
    user_achievements = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


 
class Initials(Base):
    __tablename__ = "initials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    type = Column(SmallInteger) # 0 - first name, 1 - last name, 2 - legendary full name
    gender = Column(SmallInteger) # 0 - male, 1 - female, 2 - other
    



# # Подключение к базе данных
postgre_url = os.environ.get("DATABASE_URL")
engine = create_engine(postgre_url)
Base.metadata.create_all(engine)  # create table if not exists
Session = sessionmaker(bind=engine) 



# alembic revision --autogenerate -m "test"
# alembic upgrade head

# заупстить конвертер, запустить upgrade head


# Создать новую миграцию (после изменений в моделях)
# alembic revision --autogenerate -m "описание изменений"

# Применить миграции
# alembic upgrade head

# Откатить на одну версию назад
# alembic downgrade -1

# Посмотреть историю миграций
# alembic history

# Проверить текущую версию
# alembic current