import datetime
import discord
import asyncio

from discord import app_commands
from discord.ext import commands

from models.models import Session, VoiceTime
from utils.nick import change_nickname, get_base_mult
from utils.decorators import in_allowed_channels
from utils.constants import RARITY_STYLES


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # randomly change nickname
    @app_commands.command(name="snoop", description="Случайным образом меняет никнейм")
    @app_commands.describe(target="Имя пользователя(через @ или никнейм)")
    @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.user.id))
    # @in_allowed_channels(1354784115613761606)
    async def snoop(self, interaction: discord.Interaction, target: str|None=None) -> None:
        await interaction.response.defer(ephemeral=True)
        
        member = await self._get_user_from_mention(interaction, target)
        if member is None:
            await interaction.followup.send("Пользователь не найден или указан неверно.", ephemeral=True)
            return
        
        asyncio.create_task(self._run_snoop_logic(interaction, member))
        

    @app_commands.command(name="stats", description="Просмотр статистики")
    @app_commands.describe(target="Имя пользователя(через @ или никнейм)")
    async def stats(self, interaction: discord.Interaction, target: str|None=None) -> None:
        member = await self._get_user_from_mention(interaction, target)
        if member is None: return
        
        try:
            session = Session()
            user_id, guild_id = member.id, member.guild.id
            voice_entry = session.query(VoiceTime).filter_by(user_id=user_id, guild_id=guild_id).first()
            if voice_entry is None:
                voice_entry = VoiceTime(user_id=user_id, guild_id=guild_id, total_time=0)
                session.add(voice_entry)
                session.commit()
                
            hours_spent = round(voice_entry.total_time / 60, 2) if voice_entry.total_time else voice_entry.total_time
            base_mult = get_base_mult(hours_spent)
            
            await interaction.response.send_message(
                f'Время пользователя {member.display_name} ({member}) в голосовых каналах: {hours_spent} ч.\n'
                f'Базовый коэффициент: {base_mult} (0.0001 за 1 час)'
                , ephemeral=True)
        except:
            print('error while checking database.')
        finally:
            session.close()
            


    @app_commands.command(name="top", description="Топ пользователей по времени в голосовых каналах")
    async def top(self, interaction: discord.Interaction) -> None:
        try:
            guild_id = interaction.guild.id
            session = Session()
            voice_entry = session.query(VoiceTime).filter_by(guild_id=guild_id).order_by(VoiceTime.total_time.desc()).limit(10).all()
            if voice_entry is not None:
                guild = interaction.guild  # Получаем объект сервера
                members = {member.id: (member.display_name, member) for member in guild.members}  # Создаем словарь {id: ник}
                
                message = "Топ пользователей по времени в голосовых каналах:\n"
                for entry in voice_entry:
                    time_hours = round(entry.total_time / 60, 2) if entry.total_time else entry.total_time
                    display_name = members.get(entry.user_id, f"Неизвестный ({entry.user_id})")[0]
                    username = members.get(entry.user_id, f"Неизвестный ({entry.user_id})")[1]
                    message += f'{display_name} {f"({username})" if username else ""}: {time_hours} ч.\n'
                await interaction.response.send_message(message, ephemeral=True)
        except:
            print('error while checking database.')
        finally:
            session.close()


    # send a message
    @app_commands.command(name="say", description="Отправка сообщения")
    @app_commands.describe(message="Сообщение")
    async def say(self, interaction: discord.Interaction, message: str) -> None:
        await interaction.response.send_message(message)


    # get channel id
    @app_commands.command(name="get_channel_id", description="Get channel id")
    @app_commands.describe(name="Channel name")
    async def get_channel_id(self, interaction: discord.Interaction, name: str) -> None:
        for channel in interaction.guild.channels:
            if channel.name == name:
                wanted_channel_id = channel.id
        await interaction.response.send_message(f'ID канала {name}: {wanted_channel_id}', ephemeral=True) # this is just to check 


    # clear commands cache and sync
    @commands.command()
    async def clear_commands(self, ctx):
        if ctx.guild is None:
            await ctx.send("Эта команда не доступна в личных сообщениях.")
            return

        guild = discord.Object(id=ctx.guild.id)  # Получаем текущий сервер
        
        try:
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)  # Синхронизируем
            await ctx.send("Все слеш-команды на этом сервере очищены!")
        except Exception as e:
            await ctx.send(f"Произошла ошибка: {e}")
            print(f"Ошибка при очистке команд: {e}")


    async def _run_snoop_logic(self, interaction, member):
        try:
            nickname, rarity, base_mult = await change_nickname(member)

            await interaction.followup.send(
                f"🕵️ Ник пользователя {member} ({member.mention}) изменён на **{nickname}**\n"
                f"🎖️ Роль изменена на {RARITY_STYLES.get(rarity, f'**{rarity}**')}\n"
                f"🌟 Базовый коэффициент: **{base_mult}** (0.0001 за 1 час)",
                ephemeral=True
            )
        except Exception as e:
            print(f"[SNOOP ERROR] {e}")
            await interaction.followup.send("Произошла ошибка при смене ника или роли.", ephemeral=True)


    async def _get_user_from_mention(self, interaction: discord.Interaction, mention: str) -> discord.User:
        member = interaction.user
        if mention:
            try:
                if mention=='@everyone' or mention=='@here':
                    return None
                elif mention.startswith('<') and mention.endswith('>'):
                    target_id = int(mention[2:-1])
                    member = discord.utils.get(interaction.guild.members, id=target_id)
                else:
                    member = discord.utils.get(interaction.guild.members, name=mention)
            except:
                return None
        return member


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
    
    

def update_voice_stats(bot):
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
                        print(f"{member.display_name} уже в голосовом чате ({vc.name}).")
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