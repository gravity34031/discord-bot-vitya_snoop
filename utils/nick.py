import discord
from random import choice as random_choice
from typing import Tuple
from utils.constants import RU_FIRST_NAMES, RU_LAST_NAMES, RU_LEGENDARY_NAMES, ROLES



async def change_nickname(member):
    nickname = get_random_name()
    rarity = check_rarity(nickname)
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
    
    return nickname, rarity



async def clear_roles(member):
    for role in member.roles:
        if role.name in ROLES:
            await member.remove_roles(role)

async def add_role(member, role):
    role = discord.utils.get(member.guild.roles, name=role)
    await member.add_roles(role)


def get_random_name():
    return random_choice(RU_FIRST_NAMES) + ' ' + random_choice(RU_LAST_NAMES)





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