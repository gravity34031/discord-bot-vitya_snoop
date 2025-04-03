import discord
import os
from discord.ext import commands

from cogs.commands import update_voice_stats

# Замените на свой токен
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True
guild = discord.Object(id="1349770230674755684")

bot = commands.Bot(command_prefix='!', intents=intents)


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


@bot.event
async def on_ready():
    await load_cogs()
    print(f'Бот {bot.user.name} запущен!')
    try:
        await bot.tree.sync()
        print("Слаши-команды синхронизированы.")
        for command in bot.tree.get_commands():
            print(f"Зарегистрирована команда: {command.name}")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")

    update_voice_stats(bot)
    
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.CheckFailure):
        await interaction.response.send_message(
            "Вы не можете использовать эту команду в этом канале.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("Произошла ошибка.", ephemeral=True)
    

bot.run(TOKEN)

