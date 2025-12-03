import datetime

from models.models import Session, UserStats, UserStatsDev, UserSeasonStats, Season, Achievement


class ModelView:
    def __init__(self, bot):
        self.bot = bot
        
    
    def increase_counter(self, member):
        try:
            session = Session()
            user_id, guild_id = member.id, member.guild.id
            stats_entry = session.query(UserStats).filter_by(user_id=user_id, guild_id=guild_id).first()
            season_id = self.get_current_season_id()
            stats_season_entry = session.query(UserSeasonStats).filter_by(user_id=user_id, guild_id=guild_id, season_id=season_id).first()
            
            if stats_entry is None:
                stats_entry = UserStats(user_id=user_id, guild_id=guild_id, time_in_voice=0)
                session.add(stats_entry)
            if stats_season_entry is None:
                stats_season_entry = UserSeasonStats(user_id=user_id, guild_id=guild_id, season_id=season_id)
                session.add(stats_season_entry)
                
            entries = [stats_entry, stats_season_entry]
            for entry in entries:
                session.add(stats_entry)
                if entry.snoop_counter is None:
                    entry.snoop_counter = 0
                entry.snoop_counter += 1
        except:
            print('error while increasing snoop_counter in database.')
        finally:
            session.commit()
            session.close()
            
            
    def handle_stats_after_snoop(self, member, rarity):
        try:
            session = Session()
            user_id, guild_id = member.id, member.guild.id
            stats_entry_dev = session.query(UserStatsDev).filter_by(user_id=user_id, guild_id=guild_id).first()
            if stats_entry_dev is None:
                stats_entry_dev = UserStatsDev(user_id=user_id, guild_id=guild_id)
                session.add(stats_entry_dev)
            
            if rarity in ('редкий', 'эпический', 'легендарный'):
                stats_entry_dev.rolls_since_rare = 0 
            else: 
                stats_entry_dev.rolls_since_rare += 1
            
            if rarity == 'легендарный':
                stats_entry_dev.legendary_cooldown_left = stats_entry_dev.legendary_cooldown_total
            else:
                stats_entry_dev.legendary_cooldown_left = max(0, stats_entry_dev.legendary_cooldown_left - 1)
            
        except Exception as e:
            print('error while handling stats after snoop in database.:', e)
        finally:
            session.commit()
            session.close()
            
            
    def update_voice_stats(self, bot):
        print("Обновление голосовых данных после перезапуска...")
        session = Session()
        try:
            now = datetime.datetime.now()

            # Проверяем всех пользователей в базе
            all_entries = session.query(UserStats).all()
            active_users = set()  # Список пользователей, кто СЕЙЧАС в голосе

            # Проверяем голосовые чаты
            for guild in bot.guilds:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        user_id = member.id
                        guild_id = guild.id
                        active_users.add((user_id, guild_id))  # Помечаем, что этот юзер сейчас в голосе

                        voice_entry = session.query(UserStats).filter_by(user_id=user_id, guild_id=guild_id).first()
                        voice_entry_devs = session.query(UserStatsDev).filter_by(user_id=user_id, guild_id=guild_id).first()
                        if voice_entry:
                            print(f"\t{member.display_name} уже в голосовом чате ({vc.name}).")
                        else:
                            # Если записи нет, создаем новую
                            voice_entry = UserStats(user_id=user_id, guild_id=guild_id)
                            voice_entry_devs = UserStatsDev(user_id=user_id, guild_id=guild_id, last_join=now)
                            voice_entry.dev_stats = voice_entry_devs
                            session.add(voice_entry)

            # Теперь проверяем, кто БЫЛ в голосе, но сейчас НЕ в голосе (значит, он вышел во время отключения бота)
            for entry in all_entries:
                user_id, guild_id = entry.user_id, entry.guild_id
                if (user_id, guild_id) not in active_users and entry.dev_stats.last_join:
                    # Пользователь вышел во время отключения бота -> фиксируем его время
                    time_spent = now - entry.dev_stats.last_join
                    minutes = round(time_spent.total_seconds() / 60, 2)
                    entry.time_in_voice += minutes
                    entry.time_in_voice = round(entry.time_in_voice, 2)
                    entry.dev_stats.last_join = None  # Обнуляем last_join, чтобы не учитывать ошибочное время
                elif (user_id, guild_id) in active_users and not entry.dev_stats.last_join:
                    entry.dev_stats.last_join = now

            print("Голосовая статистика обновлена после перезапуска.")

        except Exception as e:
            print(f"Ошибка при обновлении голосовых данных после перезапуска: {e}")
        finally:
            session.commit()
            session.close()
            
    
    def get_current_season_id(self):
        date = datetime.datetime.now()
        session = Session()
        try:
            season = session.query(Season).filter(Season.start_date <= date, Season.is_current == True).first()
            if season:
                return season.id
            return None
        except Exception as e:
            print(f"error while getting current season: {e}")
        finally:
            session.commit()
            session.close()
        
        
    def get_achievement_levels(self, achievement_name):
        ach_levels = {}  
        session = Session()
        try:
            achievements = session.query(Achievement).filter(
                Achievement.name.ilike(f'%{achievement_name}%')  # нечувствительно к регистру
            ).all()
            for ach in achievements:
                ach_levels[ach.level] = ach.name
        except Exception as e:
            print(f"error while handling special achievements: {e}")
        finally:
            session.commit()
            session.close()
            
        return ach_levels
    