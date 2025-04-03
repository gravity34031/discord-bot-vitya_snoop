from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class VoiceTime(Base):
    __tablename__ = "voice_time"

    user_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, primary_key=True)
    total_time = Column(Float, default=0)  # Общее время в минутах
    last_join = Column(DateTime, nullable=True)  # Последний вход в голосовой
    money = Column(Integer, default=0)

# Подключение к SQLite
engine = create_engine("sqlite:///models/database.db")
Base.metadata.create_all(engine)  # Создает таблицу, если её нет
Session = sessionmaker(bind=engine)