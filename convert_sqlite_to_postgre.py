from sqlalchemy import create_engine, Column, BigInteger, Integer, String, Float, DateTime, SmallInteger
from sqlalchemy.orm import sessionmaker
from models.models import Base  # Предполагаем, что эти классы в models.py
import datetime 




class VoiceTime(Base):
    __tablename__ = "voice_time"

    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    total_time = Column(Float, default=0)  # Общее время в минутах
    last_join = Column(DateTime, nullable=True)  # Последний вход в голосовой
    snoop_counter = Column(Integer, default=0)
    last_played_day = Column(Integer, default=datetime.datetime.now().day)
    
class Initials(Base):
    __tablename__ = "initials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    type = Column(SmallInteger) # 0 - first name, 1 - last name, 2 - legendary full name
    gender = Column(SmallInteger) # 0 - male, 1 - female, 2 - other





# 1. Подключение к SQLite (источник)
sqlite_engine = create_engine("sqlite:///models/database.db")
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

# 2. Подключение к PostgreSQL (приёмник)
pg_engine = create_engine("postgresql+psycopg://postgres:46864238@localhost/discord_bot")
PGSession = sessionmaker(bind=pg_engine)
pg_session = PGSession()

# 3. Убедись, что таблицы в PostgreSQL созданы (можно один раз выполнить)
Base.metadata.create_all(pg_engine)

# 4. Копируем VoiceTime
voice_times = sqlite_session.query(VoiceTime).all()
for record in voice_times:
    # Убедись, что last_played_day — точно int
    if isinstance(record.last_played_day, datetime.datetime):
        fixed_day = record.last_played_day.day
    elif isinstance(record.last_played_day, str):
        try:
            fixed_day = datetime.datetime.fromisoformat(record.last_played_day).day
        except Exception:
            print("⚠ Не удалось разобрать дату:", record.last_played_day)
            continue
    else:
        fixed_day = record.last_played_day

    pg_session.add(VoiceTime(
        user_id=record.user_id,
        guild_id=record.guild_id,
        total_time=record.total_time,
        last_join=record.last_join,
        snoop_counter=record.snoop_counter,
        last_played_day=fixed_day  # тут уже точно int
    ))

# 5. Копируем Initials
initials = sqlite_session.query(Initials).all()
for record in initials:
    pg_session.merge(Initials(
        id=record.id,
        value=record.value,
        type=record.type,
        gender=record.gender
    ))

# 6. Сохраняем и закрываем
pg_session.commit()
pg_session.close()
sqlite_session.close()

print("✅ Данные успешно перенесены из SQLite в PostgreSQL.")