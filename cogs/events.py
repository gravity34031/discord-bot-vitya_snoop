import discord
from discord.ext import commands
import datetime

from models.models import Session, VoiceTime
from utils.nick import change_nickname


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after, *args):
        # if user entered or leaved voice channel
        if (before.channel is None and after.channel is not None) or (before.channel is not None and after.channel is None):
            try:
                session = Session()
                user_id, guild_id = member.id, member.guild.id
                voice_entry = session.query(VoiceTime).filter_by(user_id=user_id, guild_id=guild_id).first()
                # user entered voice channel
                if before.channel is None and after.channel is not None:
                    now = datetime.datetime.now()
                    if not voice_entry:
                        voice_entry = VoiceTime(user_id=user_id, guild_id=guild_id, last_join=now, total_time=0)
                        session.add(voice_entry)
                    else:
                        voice_entry.last_join = now
                # user leaved all voice channels
                elif before.channel is not None and after.channel is None:
                    if voice_entry and voice_entry.last_join:
                        join_time = voice_entry.last_join
                        time_spent = datetime.datetime.now() - join_time
                        minutes = round(time_spent.total_seconds() / 60, 2)
                        voice_entry.total_time += minutes
                        voice_entry.total_time = round(voice_entry.total_time, 2)
                        voice_entry.last_join = None
            except:
                print('error while updating database.')
            finally:
                session.commit()
                session.close()

            
        # if before.channel is None and after.channel is not None:
        channel_id = 1354805999277445291
        if after.channel is not None and after.channel.id==channel_id and before.channel!=channel_id:
            await change_nickname(member)
            await member.move_to(before.channel)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == 'mollenq':
            await message.add_reaction('💩')
            
        await self.bot.process_commands(message)
        
    

        
        
async def setup(bot):
    await bot.add_cog(EventCog(bot))