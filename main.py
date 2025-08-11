import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

from utils.nicknames.name_cache_manager import NameCacheManager
from utils.nicknames.nickname_manager import NicknameManager
from utils.achievements.manager import AchievementManager
from utils.achievements.special_achievements import SpecialAchievements
from utils.friday import Schedule
from models.model_view import ModelView

# Замените на свой токен
load_dotenv()
DEBUG = str(os.getenv('DEBUG')).capitalize() == "True"
if DEBUG:
    TOKEN = os.getenv('discord_token_dev')
else:
    TOKEN = os.getenv('discord_token')


intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True
guild = discord.Object(id="1349770230674755684")

bot = commands.Bot(command_prefix='!', intents=intents)





@bot.event
async def on_ready():
    bot.debug = DEBUG
    bot.bot_channel = 'анал-витька'
    
    # load managers
    bot.model_view = ModelView(bot)
    bot.cache_manager = NameCacheManager()
    bot.nickname_manager = NicknameManager(bot.cache_manager)
    bot.achievement_manager = AchievementManager(bot, bot.model_view)
    bot.special_achievements = SpecialAchievements(bot.achievement_manager, bot.model_view)
    
    await bot.cache_manager.load_caches()
    
    # load schedule for friday
    if not hasattr(bot, 'schedule'):
        bot.schedule = Schedule(bot, bot.debug, server_hour_offset=-5, day="fri", hour=10, minute=00)
        bot.schedule.start()
    
    # load cogs
    await load_cogs()
    
    print(f"Бот {bot.user.name} запущен! В {'тестовом' if DEBUG else 'боевом'} режиме")
    # sync slash commands
    try:
        await bot.tree.sync()
        print("\nСлаши-команды синхронизированы.")
        for command in bot.tree.get_commands():
            print(f"\tЗарегистрирована команда: {command.name}")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")
    print()

    # update voice stats
    bot.model_view.update_voice_stats(bot)
    print()
    
   
    
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Загружен модуль: {filename}")
            except discord.ClientException:
                await bot.reload_extension(f"cogs.{filename[:-3]}")
                print(f"♻️ Перезагружен модуль: {filename}")
            except Exception as e:
                print(f"❌ Ошибка при загрузке {filename}: {e}")
                

    
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        retry_after = round(error.retry_after)
        await interaction.response.send_message(
            f"⏳ Подожди {retry_after} сек. перед повторным использованием команды!",
            ephemeral=True
        )

    elif isinstance(error, discord.app_commands.CheckFailure):
        await interaction.response.send_message(
            "Вы не можете использовать эту команду в этом канале.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("Произошла ошибка.", ephemeral=True)

    



if __name__ == "__main__": 
    bot.run(TOKEN)