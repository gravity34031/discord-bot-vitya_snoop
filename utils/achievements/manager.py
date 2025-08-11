import discord

from collections import defaultdict
from datetime import datetime

from models.models import Session, Achievement, UserAchievement, UserStats, UserSeasonStats, Season


class AchievementManager:
    """
    USE trigger_achievement in COGS
    ex.: await self.achievement_manager.trigger_achievement('snoop_count', member, member.guild)
    """
    def __init__(self, bot, model_view):
        self.model_view = model_view
        self.bot_channel = bot.bot_channel
        self.special_achievement_handlers = defaultdict(list) # all handlers - events-decorators
        
    # the OPENED function that will be called from cogs
    async def trigger_achievement(self, event_name: str, user, guild, extra_data=None):
        # handle standart achievements
        await self.__handle_standart_achievements(event_name, user, guild)
        
        # handle special achievenemts
        handlers = self.special_achievement_handlers.get(event_name, [])
        for handler in handlers:
            await handler(user, guild, extra_data or {})
        

    # decorator for adding events in special_achievement_handlers
    # ONLY FOR SPECIAL ACHIVEMENTS
    def achievement_trigger(self, event_name: str):
        def decorator(func):
            self.special_achievement_handlers[event_name].append(func)
            return func
        return decorator
    
    
    async def __handle_standart_achievements(self, event_name: str, user, guild):
        session = Session()
        try:
            # get achievements by event_name(same with table column names)
            # There could be a list of the same achievements different only in level (Наставник I, Наставник II...)
            stat_name = event_name
            
            achievements = session.query(Achievement).filter_by(event=event_name, type="standart").all()
            achievements_season = None
            season_stats = None
            season_id = self.model_view.get_current_season_id()
            if season_id:
                season_stats = session.query(UserSeasonStats).filter_by(user_id=user.id, guild_id=guild.id, season_id=season_id).first()
                achievements_season = session.query(Achievement).filter_by(event=event_name+'_season', type="standart").all()
            if not achievements and not achievements_season: return

            stats = session.query(UserStats).filter_by(user_id=user.id, guild_id=guild.id).first()

            
            if not stats and not season_stats: return
            
            # hancle season achievements
            value_season = getattr(season_stats, stat_name, None)
            for ach in achievements_season:
                if value_season is None: break
                if value_season >= ach.level:
                    await self.give_achievement(user, guild, ach.name)
            
            # handle standart achievements
            value = getattr(stats, stat_name, None)
            for ach in achievements:
                if value is None: break
                if value >= ach.level:
                    await self.give_achievement(user, guild, ach.name)  
        except Exception as e:
            print(f"error while handling standart achievements: {e}, user={user}, guild_id={guild.id}, event_name={event_name}")
        finally:
            session.commit()
            session.close()            
    
    
    async def give_achievement(self, user, guild, achievement_name: str):
        try:
            session = Session()
            ach = session.query(Achievement).filter_by(name=achievement_name).first()
            if not ach: print("achievement not found"); return
            
            user_ach = session.query(UserAchievement).filter_by(user_id=user.id, guild_id=guild.id, achievement_id=ach.id).first()
            if not user_ach: # if user has not this achievement
                user_ach = UserAchievement(user_id=user.id, guild_id=guild.id, achievement_id=ach.id, date_awarded=datetime.now())
                session.add(user_ach)
                print(f"achievement {achievement_name} given to user {user}")
                
                # find channel by its name
                announce_channel = discord.utils.get(guild.text_channels, name=self.bot_channel)
                # send message if channel is found
                if announce_channel and user:
                    await announce_channel.send(
                        f"🎉 {user.mention} ({user}) получил ачивку **{achievement_name}**\nУсловие получения: {ach.condition_description}**!"
                    )
                    
        except Exception as e:
            print(f"error while giving achievement: {e}")
        finally:
            session.commit()
            session.close()
        
        


# if type == "standart":
#     achievements = Achievement where event==event_name. There could be a list of the same achievements different only in level (Наставник I, Наставник II...)
#     if event_name not contains _season: coins_earned
#         stats = UserStat where userid=userid, guildid=guildid.
#         stat = stats['event_name']
#     if event_name contains _season: # coins_earned_season
#         stats = UserSeason where userid=userid, guildid=guildid.
#         stat = stats['event_name'(without _season)]
#     for ach in achievements:
#         if stat >= ach.level:
#             await give_achievement(user_id, guild_id, ach.name)
            
# if type == "special":
    


        
        
        
        
        
# async def on_nickname_change(user_id, guild_id):
#     await trigger_achievement("nickname_change", user_id, guild_id, extra_data={})



# @achievement_trigger("nickname_change")
# async def handle_nickname_change(user_id, guild_id, extra):
#     # Получаем текущий сезон
#     season = get_current_season()
#     stats = get_or_create_user_season_stats(user_id, guild_id, season.id)
#     stats.nickname_changes += 1
#     session.commit()

#     # Стандартные достижения
#     for level, threshold in enumerate([10, 25, 50, 100, 200], start=1):
#         if stats.nickname_changes >= threshold:
#             await give_achievement(user_id, f"Неудержимый {level}")

#     # Специальные — например, 500 за день
#     if extra.get("changes_today", 0) >= 500:
#         await give_achievement(user_id, "Безумие")