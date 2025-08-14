import discord
import math
from random import choice as random_choice
from random import uniform as random_uniform
from random import random as random_random
from random import shuffle as random_shuffle
from typing import Tuple, Dict, List

from utils.nicknames.constants import RU_FIRST_NAMES, RU_LAST_NAMES, RU_LEGENDARY_NAMES, ROLES
from models.models import Session, UserStats, UserStatsDev


class NicknameManager:
    # """ WEIGHTED NAME """
    # common_mult = 1.2
    # uncommon_mult = 7.6
    # rare_mult = 19.8
    # epic_mult = 917
    # legendary_mult = 3846
    # base_pool_size = 50  
        
    ### SETTINGS ###
        # b defines blending strength between BASE and TARGET
        # b[0, 1]
    # compute_b()
    b_max = 0.6             # 60% of way to target
    b_cap = 0.8             # upper bound, maximum possible bonus. Just in case
    mid = 300.0             # avg hours on server for few months
    k = 120.0               # how quickly b approaches b_max
    # apply_upgrade_rolls()
    # base_attempts = 0       # base number of attempts to upgrade tier
    # attempts_factor = 4.0   # amount of attempts with high bust, max attempts~=attempts_factor+base_attempts
    # upgrade_chance = 0.22   # chance to upgrade tier by one attempt
    # apply_pity_and_penalty()
    pity_add_max = 0.12     # cap; max value of pity_add - bonus for dry rolls since rare
    penalty_sub_max = 0.15  # cap; max value of penalty_sub
    # q = 0.22                # chance to upgrade tier by one attempt
    ### END SETTINGS ###
 
    TIERS = ["common", "uncommon", "rare", "epic", "legendary"]
    TIER_INDEX = {t: i for i, t in enumerate(TIERS)}

    BASE = [0.55, 0.28, 0.12, 0.045, 0.005] # base probabilities
    TARGET = [0.30, 0.25, 0.25, 0.15, 0.05] # maximum possible probabilities
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        

    async def change_nickname(self, member):
        # get hours  
        user_state = await self.get_user_state(member)
        nickname, rarity_eng, user_options = self.generate_nick(user_state)
        rarity = ROLES.get(rarity_eng, 'обычный')
        try:
            await member.edit(nick=nickname)
            print(f"Ник пользователя {member.name} изменен на {nickname}")
        except Exception as e:
            print(f"Ошибка при смене ника: {e}")
        try:
            await self.clear_roles(member)
            await self.add_role(member, rarity)      
            print(f"Роль пользователя {member.name} изменена на {rarity}")  
        except Exception as e:
            print(f"Ошибка при смене роли ника: {e}")
        return nickname, rarity, user_options
    
    
    def generate_nick(self, user_state):
        """ return nickname, 
        user_options: dict = {'blended_chances', 'bonus', 'upgrade_attempts', 'upgrade_chance'}
        """
        rarity, user_options = self.roll_rarity(user_state)
        if rarity == "legendary":
            nickname = self.generate_legendary()
        elif rarity == "epic":
            nickname = self.generate_epic()
        elif rarity == "rare":
            nickname = self.generate_rare()
        elif rarity == "uncommon":
            nickname = self.generate_uncommon()
        else:
            nickname = self.generate_common()
        return nickname, rarity, user_options
    
    def roll_rarity(self, user_state: dict) -> str:
        """
        Final rarity roll with blend + upgrades + pity/penalty.
        Return rarity name.
        - user_state {
            'hours': float, 'bonus_add': float,
            'rolls_since_rare': int, 'legendary_cooldown_left': int, 'legendary_cooldown_total': int,
            'base_attempts': int, 'attempts_factor': float
            }
        """
        hours = user_state.get("hours", 0.0)
        bonus_add = user_state.get("bonus_add", 0.0)
        base_attempts = user_state.get("base_attempts", 0)
        attempts_factor = user_state.get("attempts_factor", 4.0)
        upgrade_chance = user_state.get("upgrade_chance", 0.0)
        
        pity_add, penalty_sub = self._apply_pity_and_penalty(user_state,
                                                            pity_add_max=self.pity_add_max, penalty_sub_max=self.penalty_sub_max)
        b = self._compute_b(hours=hours, bonus_add=bonus_add, pity_add=pity_add, penalty_sub=penalty_sub,
                           b_max=self.b_max, b_cap=self.b_cap, mid=self.mid, k=self.k)
        
        probs = self.__blend(self.BASE, self.TARGET, b)
        base_idx = self._sample_by_probs(probs)

        # step-up upgrades
        final_idx, upgrade_attempts = self._apply_upgrade_rolls(base_idx, b,
                                            base_attempts=base_attempts,
                                            attempts_factor=attempts_factor,
                                            q=upgrade_chance)
        return self.TIERS[final_idx], {'blended_chances': probs, 'bonus': b, 'upgrade_attempts': upgrade_attempts, 'upgrade_chance': upgrade_chance}
    
    
    async def get_user_state(self, member):
        """
        - user_state {
            'hours': float, 'bonus_add': float,
            'rolls_since_rare': int, 'legendary_cooldown_left': int, 'legendary_cooldown_total': int,
            'base_attempts': int, 'attempts_factor': float
        }
        """
        user_state = {}
        session = Session()
        try:
            user_id, guild_id = member.id, member.guild.id
            
            user_stats_entry = session.query(UserStats).filter_by(user_id=user_id, guild_id=guild_id).first()
            if user_stats_entry is None:
                user_stats_entry = UserStats(user_id=user_id, guild_id=guild_id, time_in_voice=0)
                session.add(user_stats_entry)
            hours_spent = round(user_stats_entry.time_in_voice / 60, 2) if user_stats_entry.time_in_voice else 0.0
            
            user_devs_stats_entry = session.query(UserStatsDev).filter_by(user_id=user_id, guild_id=guild_id).first()
            if user_devs_stats_entry is None:
                user_devs_stats_entry = UserStatsDev(user_id=user_id, guild_id=guild_id)
                session.add(user_devs_stats_entry)
            user_state = {
                'hours': hours_spent or 0.0,
                'bonus_add': user_devs_stats_entry.roll_bonus_add or 0.0,
                'rolls_since_rare': user_devs_stats_entry.rolls_since_rare or 0,
                'legendary_cooldown_left': user_devs_stats_entry.legendary_cooldown_left or 0,
                'legendary_cooldown_total': user_devs_stats_entry.legendary_cooldown_total or 20,
                'base_attempts': user_devs_stats_entry.roll_base_attempts or 0,
                'attempts_factor': user_devs_stats_entry.roll_attempts_factor or 1.0,
                'upgrade_chance': user_devs_stats_entry.roll_upgrade_chance or 0.0
            }
        except:
            print('error while getting user statistics from database.')
        finally:
            session.commit()
            session.close()
        return user_state


    """ ROLES """
    async def clear_roles(self, member):
        for role in member.roles:
            if role.name in ROLES.values():
                await member.remove_roles(role)

    async def add_role(self, member, role):
        role = discord.utils.get(member.guild.roles, name=role)
        await member.add_roles(role)


    """ SUPPORTING FUNCTIONS """ 
    def __normalize(self, p: List[float]) -> List[float]:
        # keep numeric stability
        s = sum(p)
        return [x / s for x in p] if s > 0 else self.__normalize([1.0/len(p)] * len(p))

    def __blend(self, base: List[float], target: List[float], b: float) -> List[float]:
        # convex combination between base and target
        # blend BASE -> TARGET using blending strength b
        return self.__normalize([ (1-b)*a + b*t for a, t in zip(base, target) ])

    def __logistic(self, x: float) -> float:
        # standard logistic
        return 1.0 / (1.0 + math.exp(-x))

    def _compute_b(self, hours: float, bonus_add: float = 0.0, pity_add: float = 0.0, penalty_sub: float = 0.0,
                b_max: float = 0.6, b_cap: float = 0.8,
                mid: float = 300.0, k: float = 120.0) -> float:
        """
        Compute blending strength b in [0, 1].
        - hours: server hours for the user (200..600 typical)
        - bonus_add: event/booster additive bump
        - pity_add: pity bump
        - penalty_sub: negative bump after recent legendary
        - b_max: scales hours contribution
        - b_cap: upper bound
        - mid: hours at which b is half way between b_min and b_max. Average time spent on the server
        - k: controls how quickly b approaches b_max
        """
        # hours contribution (saturates)
        b_hours = self.__logistic((hours - mid) / k) * b_max
        b = b_hours + bonus_add + pity_add - penalty_sub
        return max(0.0, min(b, b_cap))
        
    def _sample_by_probs(self, ps: List[float]) -> int:
        """
        Sample an index from a list of probabilities.
        It's like upgrading rare from common to legendary
        """
        r = random_random()
        acc = 0.0
        for i, p in enumerate(ps):
            acc += p
            if r <= acc:
                return i
        return len(ps) - 1  # fallback due to fp errors
    
    def _apply_upgrade_rolls(self, tier_idx: int, b: float,
                            base_attempts: int = 0, attempts_factor: float = 4.0, q: float = 0.22) -> int:
        """
        Try to upgrade resulting tier by several one-step rolls.
        attempts = base_attempts + round(attempts_factor * b)  -> 1..5
        Each attempt succeeds with prob q -> move up by 1 tier (capped).
        """
        attempts = base_attempts + round(attempts_factor * b)
        for _ in range(attempts):
            if random_random() < q and tier_idx < len(self.TIERS) - 1:
                tier_idx += 1
        return tier_idx, attempts
        
    def _apply_pity_and_penalty(self, state: dict, pity_add_max: float = 0.12, penalty_sub_max: float = 0.15) -> Tuple[float, float]:
        """
        Gives bonuses and debuffs based on previous rolls.
        Read user's state and return (pity_add, penalty_sub).
        state example fields:
        - "rolls_since_rare": int
        - "legendary_cooldown_left": int
        - "legendary_cooldown_total": int
        """
        pity_add = 0.0
        penalty_sub = 0.0

        # pity: +0.04 every 10 dry rolls since rare (cap +0.12)
        rsr = state.get("rolls_since_rare", 0)
        pity_add = min(pity_add_max, 0.04 * (rsr // 10))

        # anti-streak: after legendary, for N next rolls apply a penalty
        cooldown = state.get("legendary_cooldown_left", 0)
        if cooldown > 0:
            # linear decay from (penalty_sub_max) 0.15 to 0
            penalty_sub = penalty_sub_max * (cooldown / state.get("legendary_cooldown_total", max(1, cooldown)))

        return pity_add, penalty_sub
        

        

    """ Generators of different rarities """
    def generate_legendary(self):
        legendary_names = self.cache_manager.legendary_name_cache
        if len(legendary_names) == 0:
            print("Using old legendary names list")
            legendary_names = RU_LEGENDARY_NAMES
        return random_choice(legendary_names)
    
    def generate_epic(self):
        # Epic name is a name with the same last 3 letters.
        for i in range(100):
            firstname = random_choice(self.cache_manager.first_name_cache or RU_FIRST_NAMES)
            last_names = self.cache_manager.last_name_cache or RU_LAST_NAMES

            filtered_last_names = []
            # last_names = [i for i in last_names if i[-3:] == firstname[-3:]] but including case when name length < 3
            for lastname in last_names:
                # Сколько букв сравнивать
                suffix_len = min(len(firstname), len(lastname), 3)
                if firstname[-suffix_len:] == lastname[-suffix_len:]:
                    filtered_last_names.append(lastname)

            if filtered_last_names:
                return f"{firstname} {random_choice(filtered_last_names)}"
            
        return random_choice(RU_FIRST_NAMES) + " " + random_choice(RU_LAST_NAMES)
    
    def generate_rare(self):
        # Rare name is a name with the same first letter.
        for i in range(10):
            firstname = random_choice(self.cache_manager.first_name_cache or RU_FIRST_NAMES)
            
            last_names = self.cache_manager.last_name_cache or RU_LAST_NAMES
            same_letter_last_names = [
                ln for ln in last_names
                if ln and ln[0].lower() == firstname[0].lower()
            ]
            
            if same_letter_last_names:
                return f"{firstname} {random_choice(same_letter_last_names)}"

        return random_choice(RU_FIRST_NAMES) + " " + random_choice(RU_LAST_NAMES)
    
    def generate_uncommon(self):
        # Uncommon name is a name with the same length.
        for i in range(10):
            first_names = self.cache_manager.first_name_cache or RU_FIRST_NAMES
            firstname = random_choice(first_names)

            last_names = self.cache_manager.last_name_cache or RU_LAST_NAMES
            filtered_last_names = [ln for ln in last_names if len(ln) == len(firstname)]

            if filtered_last_names:
                return firstname + ' ' + random_choice(filtered_last_names)
        return random_choice(RU_FIRST_NAMES) + " " + random_choice(RU_LAST_NAMES)
    
    def generate_common(self):
        firstnames = self.cache_manager.first_name_cache
        if len(firstnames) == 0:
            firstnames = RU_FIRST_NAMES
        lastnames = self.cache_manager.last_name_cache
        if len(lastnames) == 0:
            lastnames = RU_LAST_NAMES
        return random_choice(firstnames) + " " + random_choice(lastnames)



    # async def change_nickname(self, member):
    #     # get hours  
    #     hours_spent = await self.get_hours_spent(member)
        
    #     nickname, rarity, base_mult = self.get_weighted_name(self.base_pool_size, hours_spent)
    #     try:
    #         await member.edit(nick=nickname)
    #         print(f"Ник пользователя {member.name} изменен на {nickname}")
    #     except Exception as e:
    #         print(f"Ошибка при смене ника: {e}")
    #     try:
    #         await self.clear_roles(member)
    #         await self.add_role(member, rarity)      
    #         print(f"Роль пользователя {member.name} изменена на {rarity}")  
    #     except Exception as e:
    #         print(f"Ошибка при смене ника: {e}")
        
    #     return nickname, rarity, base_mult

    # def get_weighted_name(self, base_pool_size=50, hours_spent=0):
    #     """Генерирует пул ников, выбирает один с учётом редкости и веса."""
    #     base_mult = self.get_base_mult(hours_spent)
    #     pool_size_increase = base_pool_size*(base_mult*500) # +50 for 20 hours
    #     pool_size = min(int(base_pool_size + pool_size_increase), 850) # stop on 160th hour
        
    #     RARITY_WEIGHTS = {
    #         'обычный': 1+(self.common_mult*0.1*base_mult),
    #         'необычный': 1+(self.uncommon_mult*0.2*base_mult),
    #         'редкий': 1+(self.rare_mult*0.4*base_mult),
    #         'эпический': 1+(self.epic_mult*1.2*base_mult),
    #         'легендарный': 1+(self.legendary_mult*1.8*base_mult),
    #     }
    #     name_pool = []

    #     for _ in range(pool_size):
    #         nickname = self.get_random_name()
    #         rarity = self.check_rarity(nickname)
    #         weight = RARITY_WEIGHTS.get(rarity, 1)
    #         name_pool.append((nickname, rarity, base_mult, weight))

    #     total_weight = sum(w for _, _, _, w in name_pool)
    #     rnd = random_uniform(0, total_weight)
    #     upto = 0
    #     for name, rarity, base_mult, weight in name_pool:
    #         if upto + weight >= rnd:
    #             return name, rarity, base_mult
    #         upto += weight

    #     return name_pool[-1][:3]  # fallback



    # def get_random_name(self):
    #     first_name = self.cache_manager.first_name_cache
    #     last_name = self.cache_manager.last_name_cache
    #     # use old name list
    #     if len(first_name) == 0 or len(last_name) == 0:
    #         print('using old name list')
    #         return random_choice(RU_FIRST_NAMES) + ' ' + random_choice(RU_LAST_NAMES)
    #     # use db
    #     return random_choice(first_name) + " " + random_choice(last_name)


    # def get_base_mult(self, hours_spent=0):
    #     # 0.1 1000 hours
    #     # 0.01 100 hours
    #     # 0.01 100 hours
    #     # 0.001 10 hours increasing ~x3 the chance
    #     # 0.0005 5 hours
    #     # 0.0001 1 hour
    #     base_mult = round(min(0.0001*hours_spent, 1), 4)
    #     return base_mult









    # """ RARITY """
    # def check_rarity(self, full_name):
    #     if self.is_legendary(full_name):
    #         return ROLES[4]
    #     elif self.is_epic(full_name):
    #         return ROLES[3]
    #     elif self.is_rare(full_name):
    #         return ROLES[2]
    #     elif self.is_uncommon(full_name):
    #         return ROLES[1]
    #     return ROLES[0]

    # def split_name(self, full_name: str) -> Tuple[str, str]:
    #     """Разделяет полное имя на имя и фамилию."""
    #     parts = full_name.split()
    #     return (parts[0], parts[1]) if len(parts) == 2 else ("", "")

    # def is_legendary(self, full_name: str) -> bool:
    #     """Проверяет, является ли имя легендарным (в списке)."""
    #     legendary_names = self.cache_manager.legendary_name_cache
    #     # use old name list
    #     if len(legendary_names) == 0:
    #         print("Using old legendary names list")
    #         return full_name in RU_LEGENDARY_NAMES
    #     # use db
    #     return full_name in legendary_names

    # def is_epic(self, full_name: str) -> bool:
    #     """Проверяет, является ли имя эпическим (сравнение последних букв)."""
    #     """Эпическое, если последние 3 буквы имени и фамилии совпадают."""
    #     first_name, second_name = self.split_name(full_name)

    #     if not first_name or not second_name:
    #         return False

    #     # Проверяем условия
    #     if len(first_name) < 3 or len(second_name) < 3 or abs(len(first_name) - len(second_name)) > 3:
    #         return False
    #     first_sub = first_name[-3:]
    #     second_sub = second_name[-3:]
    #     return first_sub == second_sub

    # def is_rare(self, full_name: str) -> bool:
    #     """Проверяет, является ли имя редким (первая буква совпадает)."""
    #     first_name, second_name = self.split_name(full_name)
    #     return first_name and second_name and first_name[0].lower() == second_name[0].lower()

    # def is_uncommon(self, full_name: str) -> bool:
    #     """Проверяет, является ли имя необычным (длина имени = длине фамилии)."""
    #     first_name, second_name = self.split_name(full_name)
    #     return first_name and second_name and len(first_name) == len(second_name)
    









# async def change_nickname(member):
#     try:
#         scavgen_data = requests.get('https://scavgen.com/api/single')
#         name_json = scavgen_data.json().get('scavenger')
#         new_nickname = f"{name_json['firstName']} {name_json['lastName']}"
#         print(name_json)
#         try:
#             await member.edit(nick=new_nickname)
#             print(f"Ник пользователя {member.name} изменен на {new_nickname}")
#         except Exception as e:
#             print(f"Ошибка при смене ника: {e}")
#     except Exception as e:
#         print(f"Ошибка при запросе на api scavgen.com: {e}")