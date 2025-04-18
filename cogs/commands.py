import datetime
from collections import defaultdict
import discord
import asyncio

from discord import app_commands
from discord.ext import commands

from models.models import Session, VoiceTime, Initials
from utils.decorators import in_allowed_channels
from utils.constants import RARITY_STYLES


class CommandCog(commands.Cog):
    def __init__(self, bot, cache_manager, nickname_manager, model_view):
        self.bot = bot
        self.cache_manager = cache_manager
        self.nickname_manager = nickname_manager
        self.model_view = model_view
        
        self.change_nickname = nickname_manager.change_nickname
        self.get_base_mult = nickname_manager.get_base_mult


    # randomly change nickname
    @app_commands.command(name="snoop", description="Случайным образом меняет никнейм")
    @app_commands.describe(target="Имя пользователя(через @ или никнейм)")
    @app_commands.checks.cooldown(rate=1, per=2, key=lambda i: (i.user.id))
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
    @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.user.id))
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
            if voice_entry.snoop_counter is None:
                voice_entry.snoop_counter = 0
                session.add(voice_entry)
                session.commit()
            snoop_counter = voice_entry.snoop_counter
                
            hours_spent = round(voice_entry.total_time / 60, 2) if voice_entry.total_time else voice_entry.total_time
            base_mult = self.get_base_mult(hours_spent)

            await interaction.response.send_message(
                f'Время пользователя {member.display_name} ({member}) в голосовых каналах: {hours_spent} ч.\n'
                f'Попыток сменить ник: {snoop_counter}\n'
                f'Базовый коэффициент: {base_mult} (0.0001 за 1 час)'
                , ephemeral=True)
        except:
            print('error while checking database.')
        finally:
            session.close()
            


    @app_commands.command(name="top", description="Топ пользователей по времени в голосовых каналах")
    @app_commands.describe(field="Поле для сортировки (time, count)")
    @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.user.id))
    async def top(self, interaction: discord.Interaction, field: str|None=None) -> None:
        try:
            guild_id = interaction.guild.id
            session = Session()
            if field == 'count':
                voice_entry = session.query(VoiceTime).filter_by(guild_id=guild_id).order_by(VoiceTime.snoop_counter.desc()).limit(10).all()
                message = f"Топ {len(voice_entry)} пользователей по количеству смен ников:\n"
                is_counter = True
            else:
                voice_entry = session.query(VoiceTime).filter_by(guild_id=guild_id).order_by(VoiceTime.total_time.desc()).limit(10).all()
                message = f"Топ {len(voice_entry)} пользователей по времени в голосовых каналах:\n"
                is_counter = False
                
            if voice_entry is not None:
                guild = interaction.guild  # Получаем объект сервера
                members = {member.id: (member.mention, member) for member in guild.members}  # Создаем словарь {id: ник}
                
                indx=1
                for entry in voice_entry:
                    time_hours = round(entry.total_time / 60, 2) if entry.total_time else entry.total_time
                    if entry.snoop_counter is None:
                        entry.snoop_counter = 0
                        session.add(voice_entry)
                        session.commit()
                    snoop_counter = entry.snoop_counter
                    
                    display_name = members.get(entry.user_id, f"Неизвестный ({entry.user_id})")[0]
                    username = members.get(entry.user_id, f"Неизвестный ({entry.user_id})")[1]
                    if is_counter:
                        message += f'{indx}) {display_name} {f"({username})" if username else ""}: Смен ника: **{snoop_counter}** | **{time_hours} ч.**\n'
                    else:
                        message += f'{indx}) {display_name} {f"({username})" if username else ""}: **{time_hours} ч.** | Смен ника: **{snoop_counter}**\n'
                    indx += 1
                await interaction.response.send_message(message, ephemeral=True)
        except:
            print('error while checking database.')
        finally:
            session.close()


    # send a message
    @app_commands.command(name="say", description="Отправка сообщения")
    @app_commands.describe(message="Сообщение")
    @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.user.id))
    async def say(self, interaction: discord.Interaction, message: str) -> None:
        await interaction.response.send_message(message)


    # get channel id
    @app_commands.command(name="get_channel_id", description="Get channel id")
    @app_commands.describe(name="Channel name")
    @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.user.id))
    async def get_channel_id(self, interaction: discord.Interaction, name: str) -> None:
        for channel in interaction.guild.channels:
            if channel.name == name:
                wanted_channel_id = channel.id
        await interaction.response.send_message(f'ID канала {name}: {wanted_channel_id}', ephemeral=True) # this is just to check 
        
    

    @app_commands.command(name="get_initials", description="Get all initials from database")
    @app_commands.describe(type="0 - first name, 1 - last name, 2 - legendary name")
    @app_commands.checks.cooldown(rate=1, per=3, key=lambda i: (i.user.id))
    async def get_initials(self, interaction: discord.Interaction, type: int) -> None:
        try:
            session = Session()
            result = None
            if type in (0, 1, 2):
                result = session.query(Initials).filter_by(type=type).all()
            else:
                await interaction.response.send_message(f'Неверный тип.', ephemeral=True)
                return
        except Exception as e:
            print(f'Error while checking initials database: {e}')
            if not interaction.response.is_done():
                await interaction.response.send_message(f'Произошла ошибка.', ephemeral=True)
            else:
                await interaction.followup.send(f'Произошла ошибка.', ephemeral=True)
            return
        finally:
            session.close()
            
        initials_list = [i.value for i in result]
        if not initials_list:
            message = 'Список пуст.'
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True)
            else:
                await interaction.followup.send(message, ephemeral=True)
            return

        # Группировка по первой букве
        grouped = defaultdict(list)
        for word in initials_list:
            if not word:
                continue
            first_char = word[0].upper()
            if 'А' <= first_char <= 'Я':
                grouped[first_char].append(word)
            else:
                grouped['#'].append(word)  # для символов, цифр, латиницы и прочего

        # Сортировка по алфавиту: А–Я, потом #
        sorted_keys = sorted([k for k in grouped.keys() if k != '#']) + (['#'] if '#' in grouped else [])

        # Формируем текст
        chunks = []
        current_chunk = ''
        for letter in sorted_keys:
            block = f"**{letter})** {', '.join(sorted(grouped[letter], key=lambda x: x.lower()))}\n"
            if len(current_chunk) + len(block) > 2000:
                chunks.append(current_chunk)
                current_chunk = block
            else:
                current_chunk += block

        if current_chunk:
            chunks.append(current_chunk)

        # Отправляем по частям
        if not interaction.response.is_done():
            await interaction.response.send_message(chunks[0], ephemeral=True)
            chunks = chunks[1:]
        for chunk in chunks:
            await interaction.followup.send(chunk, ephemeral=True)
            
        
                
                
    @app_commands.command(name="delete_initial", description="Удаляет инициалы value из базы данных")
    @app_commands.describe(value="Инициал. Можно списком, разделенным пробелами. Легенды разделяются запятыми")
    @app_commands.describe(type="0 - first name, 1 - last name, 2 - legendary name")
    @app_commands.checks.cooldown(rate=1, per=1, key=lambda i: (i.user.id))
    async def delete_initial(self, interaction: discord.Interaction, value: str, type: int) -> None:
        try:
            if type in (0, 1):
                for item in value.split(' '):
                    self.cache_manager.delete_initial(item, type)
            if type == 2:
                for item in value.split(','):
                    self.cache_manager.delete_initial(value, type)
            await interaction.response.send_message(f'Инициалы {value} успешно удалены.', ephemeral=True)
        except:
            await interaction.response.send_message(f'Произошла ошибка.', ephemeral=True)


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
            nickname, rarity, base_mult = await self.change_nickname(member)
            self.model_view.increase_counter(member)

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
    await bot.add_cog(CommandCog(bot, bot.cache_manager, bot.nickname_manager, bot.model_view))