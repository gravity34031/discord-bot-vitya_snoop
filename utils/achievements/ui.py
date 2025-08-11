import discord
from discord.ui import View, Button

from datetime import datetime

ACHIEVEMENTS_PER_PAGE = 5


def format_achievement_embed(ach, completed=False, date=None):
    status = "✅ Получено" if completed else "❌ Не получено"
    embed = discord.Embed(
        title=f"{ach.name}",
        description=ach.description,
        color=discord.Color.green() if completed else discord.Color.red()
    )
    embed.add_field(name="Условие", value=ach.condition_description, inline=False)
    embed.add_field(name="Тип", value=ach.type.capitalize(), inline=True)
    if ach.level:
        embed.add_field(name="Уровень", value=str(ach.level), inline=True)
    if completed and date:
        embed.set_footer(text=f"{status} • {date.strftime('%d.%m.%Y')}")
    else:
        embed.set_footer(text=status)
    return embed


class AchievementPaginator(View):
    def __init__(self, interaction: discord.Interaction, achievements: list[discord.Embed]):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.achievements = achievements
        self.page = 0

    async def update(self):
        embed = self.achievements[self.page]
        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Это меню не для тебя.", ephemeral=True)
            return
        self.page = (self.page - 1) % len(self.achievements)
        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Это меню не для тебя.", ephemeral=True)
            return
        self.page = (self.page + 1) % len(self.achievements)
        await self.update()
        await interaction.response.defer()