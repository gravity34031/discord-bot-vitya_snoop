import os
import asyncio
import traceback
from datetime import datetime
from dotenv import load_dotenv
from mpmath import mp

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Настройки
mp.dps = 61
deerday_chance = 12

class Schedule:
    def __init__(self, bot, debug, server_hour_offset=-5,  day="fri", hour=10, minute=0):
        self.bot = bot
        self.channel_id = 1349770231307960332
        self.media_path = 'media/'
        self.day = day
        time_offset = 0 if debug else server_hour_offset
        self.hour = (hour + time_offset) % 24
        self.minute = minute
        self.scheduler = AsyncIOScheduler()
        self._started = False  # <--- repeat control
        
    def start(self):
        if self._started:
            print("Планировщик уже запущен. Пропускаем повторный запуск.")
            return
        self._started = True
        print("\nЗапуск планировщика...")
        day, hour, minute = self.day, self.hour, self.minute
        self.scheduler.add_job(self._post_photo, CronTrigger(day_of_week=day, hour=hour, minute=minute))  # Локальное время
        self.scheduler.start()
        print(f"Планировщик запущен. на {day} в {hour}:{minute}\n")
        
        
    async def _post_photo(self):
        try:
            now = datetime.now()
            day, month, year = now.day, now.month, now.year
            pi_modifier = int(str(mp.pi)[14:][day])
            sum_ = day + month + year + pi_modifier
            rand_num = sum_ % deerday_chance

            if rand_num == min(5, deerday_chance - 1):
                print("Лосятница!")
                message = "лосятница!"
                photo_path = os.path.join(self.media_path, 'deerday.jpg')
            else:
                print("Свинятница!")
                message = "пятница!"
                photo_path = os.path.join(self.media_path, 'pigday.jpg')

            await self._send_photo(photo_path, message)

        except Exception as e:
            print(f"Ошибка в post_photo: {e}\n{traceback.format_exc()}")
        

    async def _send_photo(self, photo_path: str, message: str): 
        try:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                file = discord.File(photo_path)
                await channel.send(content=f"@everyone, сегодня {message}", file=file)
                print("Photo sent successfully.")
            else:
                print("Channel not found.")
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}\n{traceback.format_exc()}")