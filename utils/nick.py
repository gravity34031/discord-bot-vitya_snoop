import discord
from random import choice as random_choice
from random import uniform as random_uniform
from typing import Tuple

from utils.constants import RU_FIRST_NAMES, RU_LAST_NAMES, RU_LEGENDARY_NAMES, ROLES
from models.models import Session, VoiceTime


""" WEIGHTED NAME0 """
common_mult = 1.2
uncommon_mult = 7.6
rare_mult = 19.8
epic_mult = 917
legendary_mult = 3846
base_pool_size = 50


async def change_nickname(member):
    # get hours  
    hours_spent = await get_hours_spent(member)
    
    nickname, rarity, base_mult = get_weighted_name(base_pool_size, hours_spent)
    try:
        await member.edit(nick=nickname)
        print(f"Ник пользователя {member.name} изменен на {nickname}")
    except Exception as e:
        print(f"Ошибка при смене ника: {e}")
    try:
        await clear_roles(member)
        await add_role(member, rarity)      
        print(f"Роль пользователя {member.name} изменена на {rarity}")  
    except Exception as e:
        print(f"Ошибка при смене ника: {e}")
    
    return nickname, rarity, base_mult


def get_weighted_name(base_pool_size=50, hours_spent=0):
    """Генерирует пул ников, выбирает один с учётом редкости и веса."""
    base_mult = get_base_mult(hours_spent, base_pool_size)
    pool_size_increase = base_pool_size*(base_mult*500) # +50 for 20 hours
    pool_size = min(int(base_pool_size + pool_size_increase), 850) # stop on 160th hour
    
    RARITY_WEIGHTS = {
        'обычный': 1+(common_mult*0.1*base_mult),
        'необычный': 1+(uncommon_mult*0.2*base_mult),
        'редкий': 1+(rare_mult*0.4*base_mult),
        'эпический': 1+(epic_mult*1.2*base_mult),
        'легендарный': 1+(legendary_mult*1.8*base_mult),
    }
    name_pool = []

    for _ in range(pool_size):
        nickname = get_random_name()
        rarity = check_rarity(nickname)
        weight = RARITY_WEIGHTS.get(rarity, 1)
        name_pool.append((nickname, rarity, base_mult, weight))

    total_weight = sum(w for _, _, _, w in name_pool)
    rnd = random_uniform(0, total_weight)
    upto = 0
    for name, rarity, base_mult, weight in name_pool:
        if upto + weight >= rnd:
            return name, rarity, base_mult
        upto += weight

    return name_pool[-1][:3]  # fallback



def get_random_name():
    return random_choice(RU_FIRST_NAMES) + ' ' + random_choice(RU_LAST_NAMES)



async def get_hours_spent(member):
    try:
        session = Session()
        user_id, guild_id = member.id, member.guild.id
        voice_entry = session.query(VoiceTime).filter_by(user_id=user_id, guild_id=guild_id).first()
        if voice_entry is None:
            voice_entry = VoiceTime(user_id=user_id, guild_id=guild_id, total_time=0)
            session.add(voice_entry)
        hours_spent = round(voice_entry.total_time / 60, 2) if voice_entry.total_time else voice_entry.total_time
    except:
        print('error while getting spent hours in database.')
        hours_spent = 0
    finally:
        session.commit()
        session.close()
    return hours_spent


def get_base_mult(hours_spent=0, base_pool_size=50):
    # 0.1 1000 hours
    # 0.01 100 hours
    # 0.01 100 hours
    # 0.001 10 hours increasing ~x3 the chance
    # 0.0005 5 hours
    # 0.0001 1 hour
    base_mult = round(min(0.0001*hours_spent, 1), 4)
    return base_mult





""" ROLES """
async def clear_roles(member):
    for role in member.roles:
        if role.name in ROLES:
            await member.remove_roles(role)

async def add_role(member, role):
    role = discord.utils.get(member.guild.roles, name=role)
    await member.add_roles(role)




""" RARITY """
def check_rarity(full_name):
    if is_legendary(full_name):
        return ROLES[4]
    elif is_epic(full_name):
        return ROLES[3]
    elif is_rare(full_name):
        return ROLES[2]
    elif is_uncommon(full_name):
        return ROLES[1]
    return ROLES[0]

def split_name(full_name: str) -> Tuple[str, str]:
    """Разделяет полное имя на имя и фамилию."""
    parts = full_name.split()
    return (parts[0], parts[1]) if len(parts) == 2 else ("", "")

def is_legendary(full_name: str) -> bool:
    """Проверяет, является ли имя легендарным (в списке)."""
    return full_name in RU_LEGENDARY_NAMES

def is_epic(full_name: str) -> bool:
    """Проверяет, является ли имя эпическим (сравнение последних букв)."""
    """Эпическое, если последние 3 буквы имени и фамилии совпадают."""
    first_name, second_name = split_name(full_name)

    if not first_name or not second_name:
        return False

    # Проверяем условия
    if len(first_name) < 3 or len(second_name) < 3 or abs(len(first_name) - len(second_name)) > 3:
        return False
    first_sub = first_name[-3:]
    second_sub = second_name[-3:]
    return first_sub == second_sub

def is_rare(full_name: str) -> bool:
    """Проверяет, является ли имя редким (первая буква совпадает)."""
    first_name, second_name = split_name(full_name)
    return first_name and second_name and first_name[0].lower() == second_name[0].lower()

def is_uncommon(full_name: str) -> bool:
    """Проверяет, является ли имя необычным (длина имени = длине фамилии)."""
    first_name, second_name = split_name(full_name)
    return first_name and second_name and len(first_name) == len(second_name)




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