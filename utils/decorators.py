import discord
from discord import app_commands

def in_allowed_channels(allowed_channels_ids):
    async def predicate(interaction: discord.Interaction) -> bool:
        ids = allowed_channels_ids
        if isinstance(allowed_channels_ids, int): ids = [allowed_channels_ids]
        return interaction.channel.id in ids
    return app_commands.check(predicate)