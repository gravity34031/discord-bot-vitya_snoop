from discord import app_commands, Interaction, utils as discord_utils
from discord.ext import commands
from sqlalchemy import inspect, text
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
import json

from models.models import Session, Achievement, UserSeasonStats, Season

model_registry = {
    'achievement': Achievement,
    'user_season_stats': UserSeasonStats,
    'season': Season,
    # добавить остальные таблицы
}

class AdminCog(commands.Cog):
    def __init__(self, bot, cache_manager, nickname_manager, model_view, achievement_manager):
        """
        model_registry: dict[str, BaseModel] - словарь 'имя_таблицы' -> SQLAlchemy модель
        """
        self.bot = bot
        self.bot_channel_admin = bot.bot_channel + "-админ"
        self.cache_manager = cache_manager
        self.nickname_manager = nickname_manager
        self.model_view = model_view
        self.achievement_manager = achievement_manager
        self.model_registry = model_registry

    admin_group = app_commands.Group(name="admin", description="Admin DB operations")

    @admin_group.command(name="crud", description="CRUD operations on any table")
    @app_commands.describe(
        operation="Operation: get, add, update, delete",
        table=f"Table name: {', '.join([i for i in model_registry.keys()])}",
        id="Record ID for get/update/delete (optional for add)",
        data="Filters for get OR JSON data for add or update (key-value pairs)"
    )
    async def crud(self, interaction: Interaction, operation: str, table: str, id: int = None, data: str = None):
        """
        get, add, update, delete
        /admin crud operation:get table:achievement (id:1) (data:level>5 and type='standart')
        /admin crud operation:add table:achievement data:{"name":"Test1", "description":"-", "condition_description":"-", "type":"standart", "event":"snoop_counter", "level":100}
        /admin crud operation:update table:achievement id:1 data:{"level":50}
        /admin crud operation:delete table:achievement id:1
        """
        operation = operation.lower()
        table = table.lower()

        if table not in self.model_registry:
            await interaction.response.send_message(f"Unknown table: {table}")
            return
        model = self.model_registry[table]

        data_dict = None
        filter_str = None

        if data:
            try:
                # Пытаемся парсить как JSON
                data_dict = json.loads(data)
            except:
                # Если не JSON — значит фильтр для WHERE
                filter_str = data
                
        # find channel by its name
        channel = discord_utils.get(interaction.guild.text_channels, name=self.bot_channel_admin)
        if not channel:
            await interaction.response.send_message(f"Channel {self.bot_channel_admin} not found. Please create it first.")
            return

        session = Session()
        try:
            await channel.send(f"{interaction.user.mention} Operation: {operation}, Table: {table}, ID: {id}, Data: {data}")
            if operation == "get":
                if filter_str and not id:
                    try:
                        query = session.query(model).filter(text(filter_str))
                        records = query.all()
                        if not records:
                            # await interaction.response.send_message(f"No records found in {table} with filter: {filter_str}")
                            await channel.send(f"No records found in {table} with filter: {filter_str}")
                            return
                        output = self._format_records(records, model)
                        await self._send_long_message(interaction, output, channel)
                        return
                    except Exception as e:
                        # await interaction.response.send_message(f"Invalid filter: {e}")
                        await channel.send(f"Invalid filter: {e}")
                        return

                if id is not None:
                    record = session.query(model).get(id)
                    if not record:
                        # await interaction.response.send_message(f"No record with id={id} in {table}")
                        await channel.send(f"No record with id={id} in {table}")
                        return
                    text_out = "\n".join(f"{c.key}: {getattr(record, c.key)}" for c in inspect(model).c)
                    # await interaction.response.send_message(f"Record {id} in {table}:\n{text_out}")
                    await channel.send(f"Record {id} in {table}:\n{text_out}")
                    return

                records = session.query(model).all()
                if not records:
                    # await interaction.response.send_message(f"No records found in {table}")
                    await channel.send_message(f"No records found in {table}")
                    return
                output = self._format_records(records, model)
                await self._send_long_message(interaction, output, channel)

            elif operation == "add":
                if not data:
                    # await interaction.response.send_message("Data is required for 'add'")
                    await channel.send("Data is required for 'add'")
                    return
                if not data_dict:
                    await channel.send("Data is not correct JSON format")
                    return
                obj = model()
                for key, val in data_dict.items():
                    if hasattr(obj, key):
                        setattr(obj, key, val)
                session.add(obj)
                session.commit()
                # await interaction.response.send_message(f"Added record to {table} with id={obj.id}")
                await channel.send(f"Added record to {table} with id={obj.id}")

            elif operation == "update":
                if id is None:
                    # await interaction.response.send_message("ID is required for 'update'")
                    await channel.send("ID is required for 'update'")
                    return
                if not data:
                    # await interaction.response.send_message("Data is required for 'update'")
                    await channel.send("Data is required for 'update'")
                    return
                if not data_dict:
                    # await interaction.response.send_message("Data is required for 'update'")
                    await channel.send("Data is not correct JSON format")
                    return
                obj = session.query(model).get(id)
                if not obj:
                    # await interaction.response.send_message(f"No record with id={id} in {table}")
                    await channel.send(f"No record with id={id} in {table}")
                    return
                for key, val in data_dict.items():
                    if hasattr(obj, key):
                        setattr(obj, key, val)
                session.commit()
                # await interaction.response.send_message(f"Updated record {id} in {table}")
                await channel.send(f"Updated record {id} in {table}")

            elif operation == "delete":
                if id is None:
                    # await interaction.response.send_message("ID is required for 'delete'")
                    await channel.send("ID is required for 'delete'")
                    return
                obj = session.query(model).get(id)
                if not obj:
                    # await interaction.response.send_message(f"No record with id={id} in {table}")
                    await channel.send(f"No record with id={id} in {table}")
                    return
                session.delete(obj)
                session.commit()
                # await interaction.response.send_message(f"Deleted record {id} from {table}")
                await channel.send(f"Deleted record {id} from {table}")

            else:
                # await interaction.response.send_message(f"Unknown operation: {operation}")
                await channel.send(f"Unknown operation: {operation}")

        except Exception as e:
            # await interaction.response.send_message(f"Error during {operation}: {e}")
            await channel.send(f"Error during {operation}: {e}")

        finally:
            if channel != interaction.channel:
                await interaction.response.send_message(f"Operation {operation} completed. Result sent to {channel.mention}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Operation {operation} completed.", ephemeral=True)
            session.close()
            
         
            
    def _format_records(self, records, model):
        """Форматирует список записей в строку"""
        lines = []
        for r in records:
            lines.append("\n".join(f"{c.key}: {getattr(r, c.key)}" for c in inspect(model).c))
            if r != records[-1]:
                lines.append("-" * 20)
        return "\n".join(lines)


    async def _send_long_message(self, interaction, text, channel=None):
        """Отправляет текст в несколько сообщений, если он длиннее лимита"""
        chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]

        if channel:
            # Отправляем в заданный канал
            for chunk in chunks:
                await channel.send(chunk)
        else:
            # Отправляем в ответ на команду
            await interaction.response.send_message(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)




async def setup(bot):
    await bot.add_cog(AdminCog(bot, bot.cache_manager, bot.nickname_manager, bot.model_view, bot.achievement_manager))