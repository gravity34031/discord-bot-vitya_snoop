import datetime

from models.models import VoiceTime, Session


class ModelView:
    def __init__(self, bot):
        self.bot = bot
        
    
    def increase_counter(self, member):
        try:
            session = Session()
            user_id, guild_id = member.id, member.guild.id
            voice_entry = session.query(VoiceTime).filter_by(user_id=user_id, guild_id=guild_id).first()
            if voice_entry is None:
                voice_entry = VoiceTime(user_id=user_id, guild_id=guild_id, total_time=0)
                session.add(voice_entry)
            if voice_entry.snoop_counter is None:
                voice_entry.snoop_counter = 0
            voice_entry.snoop_counter += 1
        except:
            print('error while increasing snoop_counter in database.')
        finally:
            session.commit()
            session.close()
            
            
    def update_voice_stats(self, bot):
        print("Обновление голосовых данных после перезапуска...")
        session = Session()
        try:
            now = datetime.datetime.now()

            # Проверяем всех пользователей в базе
            all_entries = session.query(VoiceTime).all()
            active_users = set()  # Список пользователей, кто СЕЙЧАС в голосе

            # Проверяем голосовые чаты
            for guild in bot.guilds:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        user_id = member.id
                        guild_id = guild.id
                        active_users.add((user_id, guild_id))  # Помечаем, что этот юзер сейчас в голосе

                        voice_entry = session.query(VoiceTime).filter_by(user_id=user_id, guild_id=guild_id).first()
                        if voice_entry:
                            print(f"\t{member.display_name} уже в голосовом чате ({vc.name}).")
                        else:
                            # Если записи нет, создаем новую
                            voice_entry = VoiceTime(user_id=user_id, guild_id=guild_id, last_join=now, total_time=0)
                            session.add(voice_entry)

            # Теперь проверяем, кто БЫЛ в голосе, но сейчас НЕ в голосе (значит, он вышел во время отключения бота)
            for entry in all_entries:
                user_id, guild_id = entry.user_id, entry.guild_id
                if (user_id, guild_id) not in active_users and entry.last_join:
                    # Пользователь вышел во время отключения бота -> фиксируем его время
                    time_spent = now - entry.last_join
                    minutes = round(time_spent.total_seconds() / 60, 2)
                    entry.total_time += minutes
                    entry.total_time = round(entry.total_time, 2)
                    entry.last_join = None  # Обнуляем last_join, чтобы не учитывать ошибочное время
                elif (user_id, guild_id) in active_users and not entry.last_join:
                    entry.last_join = now

            print("Голосовая статистика обновлена после перезапуска.")

        except Exception as e:
            print(f"Ошибка при обновлении голосовых данных после перезапуска: {e}")
        finally:
            session.commit()
            session.close()