from models.models import Session, UserAchievementStats, Achievement



class SpecialAchievements:
    """
    SpecialAchievements - list of handlers for special achievements
    standart snoop achievements handle automaticly in .handle_standard_achievements()
    """
    def __init__(self, achievement_manager, model_view):
        self.achievement_manager = achievement_manager
        self.give_achievement = achievement_manager.give_achievement
        self.model_view = model_view
        
        # automaticly register all methods that starts with dec_
        for attr_name in dir(self):
            if attr_name.startswith("dec_"):
                method = getattr(self, attr_name)
                if callable(method):
                    # extract event name from method name
                    # dec__snoop__midnight → snoop
                    parts = attr_name.split("__")
                    if len(parts) >= 2:
                        event_name = parts[1]  # "snoop"
                        self.achievement_manager.achievement_trigger(event_name)(method) # add method to manager(special_achievement_handlers dict of lists)
     
    
    
    """ SpecialAchievements handlers """               
    # snoop_counter_event
    async def dec__snoop_counter__no_rare_nicks_strike(self, user, guild, extra: dict):
        achivement_name = 'Неудачник'
        session = Session()
        try:
            user_stats = session.query(UserAchievementStats).filter_by(user_id=user.id, guild_id=guild.id).first()
            if user_stats is None:
                user_stats = UserAchievementStats(user_id=user.id, guild_id=guild.id)
                session.add(user_stats)
            if user_stats.unluck_count is None:
                user_stats.unluck_count = 0
            
            rarity = extra.get("rarity", None)
            if rarity is None: return
            
            if str(rarity).lower() in ('обычный', 'необычный', 'редкий'):
                user_stats.unluck_count += 1
               
            ach_levels = self.model_view.get_achievement_levels(achivement_name)

            if ach_levels in (None, {}): return
            
            for ach_level, ach_name in sorted(ach_levels.items()):
                if user_stats.unluck_count >= ach_level:
                    await self.give_achievement(user, guild, ach_name)
        except Exception as e:
            print(f"error while handling special achievements: {e}, user={user}, guild_id={guild.id}")
        finally:
            session.commit()
            session.close()
        
    # snoop_counter event
    async def dec__snoop_counter__collected_all_myths(self, user, guild, extra: dict):
        # custom logic
        session = Session()
        session.close()
        # try:
        #     count = session.query(...).filter(...).count()
        #     if count >= 10:
        #         await self.give_achievement(user, guild, "Охотник на мифов")
        # finally:
        #     session.close()

    # snoop_counter event
    async def dec__snoop_counter__snoop_midnight(self, user, guild, extra: dict):
        from datetime import datetime
        if datetime.now().hour == 0:
            await self.give_achievement(user, guild, "Ночной следопыт")