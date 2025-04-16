from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, SmallInteger
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
    snoop_counter = Column(Integer, default=0)
    
class Initials(Base):
    __tablename__ = "initials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    type = Column(SmallInteger) # 0 - first name, 1 - last name, 2 - legendary full name
    gender = Column(SmallInteger) # 0 - male, 1 - female, 2 - other
    

# Подключение к SQLite
engine = create_engine("sqlite:///models/database.db")
Base.metadata.create_all(engine)  # Создает таблицу, если её нет
Session = sessionmaker(bind=engine)