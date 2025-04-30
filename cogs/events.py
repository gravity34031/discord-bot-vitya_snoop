import discord
import asyncio
from discord.ext import commands
import datetime

from models.models import Session, VoiceTime
from utils.decorators import in_allowed_channels


class EventCog(commands.Cog):
    def __init__(self, bot, cache_manager, nickname_manager, model_view):
        self.bot = bot
        self.cache_manager = cache_manager
        self.nickname_manager = nickname_manager
        self.model_view = model_view
        
        self.change_nickname = nickname_manager.change_nickname
        
        self.suggestion_channels = {'firstname': 1355601355644866721, 'secondname': 1355601431700443467, 'legendary': 1356006322356752568}
        
        
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

        # play mitin welcome
        if member.name == 'gravity9525' and after.channel and before.channel == None:
            voice_channel = after.channel
            if not member.guild.voice_client:  # если бот не подключён
                vc = await voice_channel.connect()
            else:
                vc = member.guild.voice_client
            await vc.move_to(voice_channel)

            if vc.is_connected():
                audio_source = discord.FFmpegPCMAudio("media/mitin.mp3")
                if not vc.is_playing():
                    vc.play(audio_source)
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    await vc.disconnect()
                else:
                    print("Уже играет звук.")
            else:
                print("Ошибка: бот не подключён к голосовому каналу.")

            
        # if before.channel is None and after.channel is not None:
        channel_id = 1354805999277445291
        if after.channel is not None and after.channel.id==channel_id and before.channel!=channel_id:
            await self.change_nickname(member)
            await member.move_to(before.channel)
            self.model_view.increase_counter(member)



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == 'mollenq':
            await message.add_reaction('🍑')
            
        await self.bot.process_commands(message)
      
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        valid_channels = [self.suggestion_channels['firstname'], self.suggestion_channels['secondname'], self.suggestion_channels['legendary']]

        # ignore not valid channels
        if payload.channel_id not in valid_channels:
            return

        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
        if user.bot:
            return  # ignore bots reactions

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if user.name in ['gravity9525', 'mollenq', 'executus'] :
            if payload.emoji.name == '❤️':
                try:
                    await message.add_reaction('✅')
                except discord.Forbidden:
                    print(f"[WARNING] Бот не может добавить реакцию ✅ на сообщение пользователя {user.name}")
                allowed_emojis = {'✅', '❤️'}
                await self._add_initials(message.content, payload.channel_id)
            else:
                try:
                    await message.add_reaction('❌')
                except discord.Forbidden:
                    print(f"[WARNING] Бот не может добавить реакцию ❌ на сообщение пользователя {user.name}")
                allowed_emojis = {'❌'}     

            # remove other reactions
            for reaction in message.reactions:
                if str(reaction.emoji) not in allowed_emojis:
                    await message.clear_reaction(reaction.emoji)
    
    
    async def _add_initials(self, message, channel_id):
        type_id = -1
        if channel_id == self.suggestion_channels['firstname']:
            type_id = 0
        elif channel_id == self.suggestion_channels['secondname']:
            type_id = 1
        elif channel_id == self.suggestion_channels['legendary']:
            type_id = 2
        if type_id == -1: return
        
        if type_id in (0, 1):
            message_prettyfied = message.replace("'", "").replace("[", "").replace("]", "").replace("\n", " ").replace("\t", " ").replace(",", "")
            for word in message_prettyfied.split(' '):
                await self.cache_manager.add_name(word.capitalize().strip(), type_id)
        else:
            message_prettyfied = message.replace("'", "").replace("[", "").replace("]", "").replace("\n", " ").replace("\t", " ")
            for words in message_prettyfied.split(','):
                legend = ' '.join(words.split()[:2]).title().strip()
                if len(legend)<2: continue
                
                await self.cache_manager.add_name(legend, type_id) # add legend
                await self.cache_manager.add_name(legend.split()[0].capitalize(), 0) # add firstname
                await self.cache_manager.add_name(legend.split()[1].capitalize(), 1) # add lastname
        
    

        
        
async def setup(bot):
    await bot.add_cog(EventCog(bot, bot.cache_manager, bot.nickname_manager, bot.model_view))